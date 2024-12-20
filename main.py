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

FRAMERATE = 90 # Set maximum FPS (frames per second)
POINTSIGN = "0"

class TerminalSpace(Terminal):
    """A TerminalSpace is the context object for manipulating the terminal's cells and cursor.
    It extends the blessed.Terminal class with PyWaveCLI specific properties and functions.
    """
    buffer: list[list[str]] = []
    graphspaces: list[Graphspace] = []

    def __init__(self, kind = None, stream = None, force_styling = False):
        """Create a new TerminalSpace object.

        Args:
            kind (_type_, optional): Defaults to None.
            stream (_type_, optional): Defaults to None.
            force_styling (bool, optional): Defaults to False.
        """
        super().__init__(kind, stream, force_styling)
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height-1)]
    
    # TODO: Handle resizing
    def handleResize(self, sig, action):
        """Handler for when the window is resized

        Args:
            sig (Signal): 
            action (ActionType):
        """
        #self.graphspaces[0].xCellCount = self.width
        #self.graphspaces[0].yCellCount = self.height
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
        menubuffer = [self.underline + x + self.normal for x in list("[Menu: M] | [Quit: Q] | [Zoom-X: (+/-)] | [Zoom-Y: (?/_)] | [Adjust PPC: (K|k / L|l)]")]
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
    """GraphSpace is an object class that contains and manupulates a coordinate system.
    It handles rendering of functions to a coordinate system.

    Returns:
        _type_: _description_
    """
    waves: list[Wave] = []
    buffer: list[list[str]] = []
    showMenu: bool = False
    menu: menu.Menu = None

    def __init__(self, parent: TerminalSpace, xCellCount: int, yCellCount: int, xRange:float, yRange: float, ppcMag: int):
        self.parentTerminal = parent
        self.xCellCount = xCellCount
        self.yCellCount = yCellCount if (yCellCount % 2 != 0) else yCellCount - 1
        self.ppcMagnitude = 0 if ppcMag < 0 else ppcMag
        self.xRange = xRange
        self.yRange = yRange
        self.stepSize = 1/math.pow(2, ppcMag)
        self.clearBuffer()
        self.menu = menu.SelectionMenu(self)
        self.menu.addInfoEntry("   General   | Option:  (Up/Down) | Edit:        (E) |", parent.cadetblue1)
        self.menu.addInfoEntry("   Controls: | Back:  (Backspace) | Submenu: (Enter) |", parent.cadetblue1)
        self.menu.addInfoEntry("   Wave Menu | Toggle Wave: (Tab) | Reset Wave:  (R) | Duplicate Wave: (D) |", parent.steelblue1)
        self.menu.addInfoEntry("   Controls: | Create Wave:   (N) | Set Color:   (C) | Delete Wave:  (Del) |", parent.steelblue1)
        self.menu.addInfoEntry("", parent.normal)

    def cartesianToGraphspace(self, x: float, y: float) -> tuple[int, int]:
        """Convert cartesian coordinates (x, y) to a column and row cell coordinate."""
        cellPointWidth = (self.xRange * 2) / self.xCellCount
        xInCells = round(x / cellPointWidth)
        xAdjusted = int(round(self.xCellCount / 2) + xInCells)

        cellPointHeight = (self.yRange * 2)/(self.yCellCount)
        yInCells = round(y / cellPointHeight)
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
    
    def addWaveFromEntry(self, waveEntry: menu.WaveEntry):
        self.waves.append(waveEntry.wave)
    
    def removeWave(self, wave: Wave):
        self.waves.pop(self.waves.index(wave))

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

    def renderMenuToFrame(self, curMenu: menu.Menu):
        if(curMenu.activeSubmenu):
            self.renderMenuToFrame(curMenu.activeSubmenu)
        for rowIdx, rowVal in enumerate(curMenu.buffer):
            for colIdx, colVal in enumerate(rowVal):
                self.buffer[curMenu.yRenderOffset + rowIdx+1][curMenu.xRenderOffset + colIdx] = colVal
        if(curMenu.inputWindowOverride):
            men: menu.SelectionMenu = curMenu
            self.renderMenuToFrame(men.getSelectedEntry().inputWindow)

    
    def printWaves(self):
        """Print all waves to the buffer for all values of x from -xRange to +xRange with a fixed stepSize."""
        x = -self.xRange
        while (x < self.xRange):
            for wave in self.waves:
                if not wave.visible: continue
                cellPos = self.cartesianToGraphspace(x, wave.getY(x))
                if cellPos != None: self.buffer[cellPos[1]][cellPos[0]] = f"{wave.termColor}{POINTSIGN}{self.parentTerminal.normal}"
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
        
    def alterScale(self, xy: str, delta: int):
        if(xy == "x"):
            self.xRange += delta
        elif(xy == "y"):
            self.yRange += delta
    
    def alterPPC(self, delta: int):
        self.ppcMagnitude += delta if self.ppcMagnitude + delta >= 0 else 0
        self.stepSize = 1/math.pow(2, self.ppcMagnitude)

class Wave():
    """ Wave Class : Contains a function f(x) and methods to evaluate it."""
    def __init__(self, func: str, termColor: str, customVars: dict[dict[str, "value": float, "incr": float]], visible: bool = True):
        self.func = func
        self.termColor = termColor
        self.customVars: dict = customVars
        self.originalVars: dict = copy.deepcopy(customVars)
        self.originalFunc = str(func)
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

    def resetWave(self):
        self.func = str(self.originalFunc)
        for var in self.originalVars.keys():
            for key in self.originalVars[var]:
                self.customVars[var][key] = self.originalVars[var][key]
        self.refreshWaveFunction()
    
    def refreshWaveFunction(self):
        lambdafied = "lambda x, "
        for av in self.customVars.keys():
            lambdafied += f"{av},"
        lambdafied = lambdafied[:-1] + ":"
        self.lambdafied = lambdafied + self.func
        self.asFunction = eval(self.lambdafied)
    
    def getCopy(self):
        return copy.deepcopy(self)

    def getFunc(self):
        return self.func()
    
    def tryUpdateWaveFunction(self, newFunc: str, newVars: dict[str:dict[str:float]]) -> bool:
        """Try to set a new wave function.

        Args:
            newFunc (str): The new function represented by a string
            newVars (dict): The new (if any) variables supplied

        Returns:
            bool: If the new wave function is evaluatable by eval, returns True. Else False.
        """
        lambdafied = "lambda x "
        for av in self.customVars.keys():
            lambdafied += f",{av} "
        lambdafied = lambdafied[:-1] + ":"
        lambdafied = lambdafied + newFunc
        try: 
            asFunction = eval(lambdafied)
            vars = [0] + [l[1]["value"] for l in self.customVars.items()]
            tryCalling = asFunction(*vars)
            tryCalling / 10
            pass

        except Exception as e:
            return False
        self.lambdafied = lambdafied
        self.func = newFunc
        self.asFunction = asFunction
        return True


def main():
    term = TerminalSpace()
    with term.hidden_cursor():
        
        if(os.name != "nt"): # Resize event handler only available on Linux / MacOS
            signal.signal(signal.SIGWINCH, term.handleResize)
        # Set cursor to 0,0, set theme, clear terminal
        print(f"{term.home}{term.gray100_on_gray1}{term.clear}")
        
        # Print example waves from a separate module (To avoid cluttering the code... even more than it already is...)
        from examples import addWaves
        addWaves(term)

        with term.cbreak():
            val = keyboard.Keystroke("")
            mainGS = term.graphspaces[0]
            while True:
                deepestMenu = mainGS.menu.recursiveSubMenuFetch()
                # Root (no menu) functionality keybinds
                if(not val.name and not deepestMenu.inputWindowOverride): # If no InputWindow is currently active
                    if(val.lower() == "q"): break
                    elif(val.lower() == "m"):
                        mainGS.showMenu = not mainGS.showMenu
                    elif(val.lower() == "-"):
                        mainGS.alterScale("x", 1)
                    elif(val.lower() == "+"):
                        mainGS.alterScale("x", -1 if mainGS.xRange > 1 else 0)
                    elif(val.lower() == "_"):
                        mainGS.alterScale("y", 1)
                    elif(val.lower() == "?"):
                        mainGS.alterScale("y", -1 if mainGS.yRange > 1 else 0)
                    elif(val == "K"):
                        mainGS.alterPPC(-0.1)
                    elif(val.lower() == "k"):
                        mainGS.alterPPC(-0.5)
                    elif(val == "L"):
                        mainGS.alterPPC(0.1)
                    elif(val.lower() == "l"):
                        mainGS.alterPPC(0.5)
                if(mainGS.showMenu and val != ""):
                    mainGS.menu.handleInput(val)
                if(mainGS.showMenu and val == "" and type(deepestMenu.getSelectedEntry()) is menu.ArgValEntry):
                    deepestMenu.generateMenu()

                term.render()
                val = term.inkey(timeout=(1/FRAMERATE))
            os.system("cls||clear")
if __name__ == "__main__":
    main()