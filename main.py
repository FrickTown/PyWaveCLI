"""
[PyWaveCLI Core]
main.py -- The core for terminal interfacing, graphing logic and rendering logic.
Author: FrickTown (https://github.com/FrickTown/)
"""
from __future__ import annotations
from blessed import Terminal, keyboard
import os
import menu
import copy
import math
import signal

class TerminalSpace(Terminal):
    buffer: list[list[str]] = []
    graphspaces: list[Graphspace] = []

    def __init__(self, kind = None, stream = None, force_styling = False):
        super().__init__(kind, stream, force_styling)
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height-1)]
    
    def handleResize(sig, action, info):
        pass

    def render(self):
        """
        Render a full frame to the TerminalSpace's buffer by rendering each graphspace and mapping them
        """
        for gSpaceID, graphspace in enumerate(self.graphspaces, 1):
            graphspace.renderFrame()
            for idx, id in enumerate(graphspace.buffer):
                self.buffer[idx] = id
            graphspace.clearBuffer()

        # Render menu info in top left corner last
        menubuffer = [self.underline + x + self.normal for x in list("[Menu: M] | [Quit: Q]")]
        for idx, id in enumerate(menubuffer):
            self.buffer[0][idx] = id
        
        self.printBufferToTerminal()

    def addGraphspace(self, graphspace: Graphspace):
        """
        Helper method for adding a Graphspace to the terminal context
        keyword arguments:
            graphspace: The Graphspace to add
        """
        self.graphspaces.append(graphspace)
    
    def printBufferToTerminal(self):
        """Render the TerminalSpace's buffer to the terminal. To be called only when the frame has been fully rendered to the buffer."""
        with self.location(0, 0):
            for y in range(len(self.buffer)):
                for x in range(len(self.buffer[y])):
                    print(self.buffer[y][x], end="")
                print("", end="\n")
     
    def printGraphSpace(self, xPos: int, yPos: int, graphspace: Graphspace | menu.Menu):
        """
        Unused method for overriding the full frame render and printing a graph space directly to the terminal.
        arguments:
            xPos: the x position of the cell from which to start the rendering
            yPos: the y position of the cell from which to start the rendering
            graphspace: the graphspace to print
        """
        with self.location(xPos, yPos):
            for y in range(len(graphspace.buffer)):
                for x in range(len(graphspace.buffer[y])-1):
                    print(graphspace.buffer[y][x], end="")
                self.move_left(-self.width)
                print(self.move_down, end="")
    

class Graphspace():
    waves: list[Wave] = []
    buffer: list[list[str]] = []
    showMenu: bool = False
    menu: menu.Menu = None

    def __init__(self, parent: TerminalSpace, xCellCount: int, yCellCount: int, xRange:float, yRange: float, stepSize: float):
        self.parent = parent
        self.xCellCount = xCellCount
        self.yCellCount = yCellCount if (yCellCount % 2 != 0) else yCellCount - 1
        self.xRange = xRange
        self.yRange = yRange
        self.stepSize = stepSize
        self.clearBuffer()
        self.menu = menu.SelectionMenu(self)
        self.menu.addInfoEntry("Navigation: [Option: (Up/Down), Select: (Enter), Back: (Backspace)]", parent.cadetblue1)
        self.menu.addInfoEntry("Root Menu Controls: [Toggle Wave: (Tab), Reset Wave: (R)]", parent.plum)

    def cartesianToGraphspace(self, x: float, y: float) -> tuple[int, int]:
        """Convert cartesian coordinates (x, y) to a column and row cell coordinate."""
        xStepSize = (self.xRange * 2) / self.xCellCount
        xInCells = round(x / xStepSize)
        xAdjusted = int(round(self.xCellCount / 2) + xInCells)

        yStepSize = (self.yRange * 2)/(self.yCellCount)
        yInCells = round(y / yStepSize)
        yAdjusted = int(round((self.yCellCount / 2)) - yInCells)

        if (yAdjusted < 0 or yAdjusted >= self.yCellCount or xAdjusted < 0 or xAdjusted >= self.xCellCount):
            return None
        return(xAdjusted, yAdjusted)
    
    def addWave(self, wave: Wave):
        """ Helper function for adding a wave function to the GraphSpace
        keyword arguments:
            wave: The wave to add
        """
        self.waves.append(wave)
        self.menu.addWaveEntry(wave)
        self.menu.generateMenu()

    def clearBuffer(self):
        # Reset the graphics buffer
        self.buffer = [[" " for _ in range(self.xCellCount)] for _ in range(self.yCellCount)]
    
    def renderFrame(self):
        self.printUIToBuffer()
        self.printWaves()
        if(self.showMenu):
            self.renderMenuToFrame(self.menu)
        for wave in self.waves:
            wave.updateVariables()

    def renderMenuToFrame(self, menu: menu.Menu):
        if(menu.activeSubmenu):
            self.renderMenuToFrame(menu.activeSubmenu)
        for rowIdx, rowVal in enumerate(menu.buffer):
            for colIdx, colVal in enumerate(rowVal):
                self.buffer[menu.yRenderOffset + rowIdx+1][menu.xRenderOffset + colIdx] = colVal
    
    def printWaves(self):
        """Print all waves to the buffer for all values of x from -xRange to +xRange with a fixed stepSize."""
        x = -self.xRange
        while (x < self.xRange):
            for wave in self.waves:
                if not wave.visible: continue
                cellPos = self.cartesianToGraphspace(x, wave.getY(x))
                if cellPos != None: self.buffer[cellPos[1]][cellPos[0]] = f"{wave.termColor}0{self.parent.normal}"
            x += self.stepSize
    
    def printUIToBuffer(self):
        """Print the x and y axis, as well as other GUI elements."""
        width = len(self.buffer[0])
        height = len(self.buffer)
        
        # Print the y-axis
        for y in range(0,height):
            self.buffer[y][round(width/2)] = "|"

        # Print the x-axis
        for x in range(0, width):
            self.buffer[round(height/2)][x] = "—"

        # Print the origin
        self.buffer[round((height)/2)][round(width/2)] = "+"

        # Print the legend
        rangeS = str(self.yRange)                                       # Get yRange as a string
        rangeChars = list(rangeS)                                       # Turn the string into a list of chars
        legendPadding = 0                                               # Allow for padding (So that the value is not directly on the edge of the screen)
        xStart = round(width/2) - round(len(rangeS) / 2) - 1            # Find out where we're going to start mapping
        for idx, x in enumerate(range(xStart, xStart + len(rangeS))):   # Map the values of rangeChars onto the GraphSpace buffer
            self.buffer[0 + legendPadding][x] = rangeChars[idx]
            self.buffer[-(1 + legendPadding)][x] = rangeChars[idx]
        self.buffer[-(1 + legendPadding)][xStart-1] = '-'               # Remember negative sign

        rangeS = str(self.xRange)                                       # Get xRange as a string
        rangeChars = list(rangeS)                                       # Turn the string into a list of chars
        xStart1 = 1                                                     # Decide the x coordinate for the negative xRange string
        xStart2 = width - len(rangeChars)                               # Decide the x coordinate for the positive xRange string
        yVal = round(height/2) + 1                                      # (Change to - 1 to place text above the x-axis) (or 0 to place *on* the x-axis)
        for idx, x in enumerate(range(0, len(rangeS))):                 # Map the values of rangeChars onto the GraphSpace buffer
            self.buffer[yVal][xStart1 + x] = rangeChars[idx]
            self.buffer[yVal][xStart2 + x] = rangeChars[idx]
        self.buffer[yVal][xStart1-1] = '-'                              # Remember negative sign
        

class Wave():
    def __init__(self, func: str, termColor: str, customVars: dict[dict[str, "value": float, "incr": float]], visible: bool = True):
        self.func = func
        self.termColor = termColor
        self.customVars: dict = customVars
        self.originalVars: dict = copy.deepcopy(customVars)
        lambdafied = "lambda x, "
        for av in customVars.keys():
            lambdafied += f"{av},"
        lambdafied = lambdafied[:-1] + ":"
        self.lambdafied = lambdafied + func
        self.asFunction = eval(self.lambdafied)
        self.visible = visible
    
    def getY(self, x):
        vars = [x] + [l[1]["value"] for l in self.customVars.items()] # Fetch the current value of x and each custom variable into a list of strings 
        return self.asFunction(*vars) # Unpack the list into the lambda function to get the current value of the function
        
    
    def updateVariables(self):
        for key in self.customVars.keys():
            self.customVars[key].update({"value": self.customVars[key]["value"] + self.customVars[key]["incr"]})

    def getFunc(self):
        return self.func()


def main():
    term = TerminalSpace()
    if(os.name != "nt"): # Resize event handler only available on Linux / MacOS
        signal.signal(signal.SIGWINCH, term.handleResize)
    # Set cursor to 0,0, set theme, clear terminal
    print(f"{term.home}{term.gray100_on_gray1}{term.clear}")
    
    # Print example waves from a separate module (To avoid cluttering the code... even more than it already is...)
    from examples import addWaves
    addWaves(term)

    with term.cbreak():
        val = keyboard.Keystroke("")
        while True:
            if(val.lower() == "q" and type(term.graphspaces[0].menu.recursiveSubMenuFetch()) is not menu.InputMenu): break
            if(val.lower() == "m" and type(term.graphspaces[0].menu.recursiveSubMenuFetch()) is not menu.InputMenu):
                term.graphspaces[0].showMenu = not term.graphspaces[0].showMenu
            if(term.graphspaces[0].showMenu and val != ""):
                term.graphspaces[0].menu.handleInput(val)

            term.render()
            val = term.inkey(timeout=0.005)

if __name__ == "__main__":
    main()