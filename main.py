from __future__ import annotations
from blessed import Terminal
import menu
import math

class TerminalSpace(Terminal):
    buffer: list[list[str]] = []
    graphspaces: list[Graphspace] = []

    def __init__(self, kind = None, stream = None, force_styling = False):
        super().__init__(kind, stream, force_styling)
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height-1)]
    
    def render(self):
        """
        Render a full frame to the TerminalSpace's buffer by rendering each graphspace and mapping them
        """
        for graphspace in self.graphspaces:
            graphspace.renderFrame()
            for idx, id in enumerate(graphspace.buffer):
                self.buffer[idx] = id
            graphspace.clearBuffer()

        # Render menu info in top left corner last
        menubuffer = [self.underline + x + self.normal for x in list("[Menu: M]")]
        for idx, id in enumerate(menubuffer):
            self.buffer[0][idx] = id
        
        self.printBuffer()

    def addGraphspace(self, graphspace: Graphspace):
        """
        Helper method for adding a Graphspace to the terminal context
        Arguments:
            graphspace: The Graphspace to add
        """
        self.graphspaces.append(graphspace)
    
    def printBuffer(self):
        """
        Render the TerminalSpace's buffer to the terminal. To be called only when the frame has been fully rendered to the buffer.
        """
        with self.location(0, 0):
            for y in range(len(self.buffer)):
                for x in range(len(self.buffer[y])):
                    print(self.buffer[y][x], end="")
                self.move_left(-self.width)
                print(self.move_down, end="")        

    def printGraphSpace(self, xPos: int, yPos: int, graphspace: Graphspace | menu.Menu):
        """
        Unused method for overriding the full frame render and printing a graph space directly to the terminal.
        Arguments:
            xPos: the x position of the cell from which to start the rendering
            yPos: the y position of the cell from which to start the rendering
            graphspace: the graphspace to print
        """
        with self.location(xPos, yPos):
            for y in range(len(graphspace.buffer)):
                for x in range(len(graphspace.buffer[y])):
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
        self.yCellCount = yCellCount
        self.xRange = xRange
        self.yRange = yRange
        self.stepSize = stepSize
        self.clearBuffer()
        self.menu = menu.Menu(self)

    def cartesianToGraphspace(self, x: float, y: float) -> tuple[int, int]:
        """Convert cartesian coordinates (x, y) to a column and row cell coordinate."""
        xStepSize = (self.xRange * 2) / self.xCellCount
        xInCells = round(x / xStepSize)
        xAdjusted = int((self.xCellCount / 2) + xInCells)

        yStepSize = (self.yRange * 2)/(self.yCellCount)
        yInCells = round(y / yStepSize)
        yAdjusted = int((self.yCellCount / 2) - yInCells)

        if (yAdjusted < 0 or yAdjusted >= self.yCellCount or xAdjusted < 0 or xAdjusted >= self.xCellCount):
            return None
        return(xAdjusted, yAdjusted)
    
    def addWave(self, wave: Wave):
        """ Helper function for adding a wave function to the GraphSpace
        Arguments:
            wave: The wave to add
        """
        self.waves.append(wave)
        self.menu.addEntry(wave)
        self.menu.generateMenu()

    def clearBuffer(self):
        # Reset the graphics buffer
        self.buffer = [[" " for _ in range(self.xCellCount)] for _ in range(self.yCellCount)]
    
    def renderFrame(self):
        self.printUIToBuffer()
        self.printWaves()
        if(self.showMenu):
            for rowIdx, rowVal in enumerate(self.menu.buffer):
                for colIdx, colVal in enumerate(rowVal):
                    self.buffer[rowIdx+1][colIdx] = colVal
        for wave in self.waves:
            wave.updateVariables()
    
    def printWaves(self):
        """Print all waves to the buffer for all values of x from -xRange to +xRange with a fixed stepSize."""
        x = -self.xRange
        while (x < self.xRange):
            for wave in self.waves:
                cellPos = self.cartesianToGraphspace(x, wave.getY(x))
                if cellPos != None: self.buffer[cellPos[1]][cellPos[0]] = f"{wave.termColor}0{self.parent.normal}"
            x += self.stepSize
    
    def printUIToBuffer(self):
        """Print the x and y axis, as well as other GUI elements.
        keyword arguments:
        width -- the terminal width (in cells)
        height -- the terminal height (in cells)
        """
        width = len(self.buffer[0])
        height = len(self.buffer)
        # Print the name of the current wave
        mockstring = "[Wave 1: f(x) = 0]"
        #buffer[0][round(width/2) - int(len(mockstring)/2)] = term.underline + mockstring # Ensure it's centered by shifting left by half the length of the string

        # Print the y-axis
        for y in range(1,height):
            self.buffer[y][round(width/2)] = "|"

        # Print the x-axis
        for x in range(0, width):
            self.buffer[round(height/2)][x] = "—"

        # Print the origin
        self.buffer[round((height)/2)][round(width/2)] = "+"

        # Print the legend
        #buffer[1][round(width/2) - len(str(yScale))] = str(yScale)
        #buffer[len(buffer)-2][round(width/2) - len(str(-yScale))] = str(-yScale)
        #buffer[round(height/2)][0] = str(xScale)
        #buffer[round(height/2)][width-len(str(-xScale))] = str(-xScale)
        

class Wave():
    def __init__(self, func: str, termColor: str, additionalVars: dict[dict[str, "value": float, "incr": float]]):
        self.func = func
        self.termColor = termColor
        self.av = additionalVars
        lambdafied = "lambda x, "
        for av in additionalVars.keys():
            lambdafied += f"{av},"
        lambdafied = lambdafied[:-1] + ":"
        self.lambdafied = lambdafied + func
        self.asFunction = eval(self.lambdafied)
    
    def getY(self, x):
        vars = [x] + [l[1]["value"] for l in self.av.items()]
        return self.asFunction(*vars)
        
    
    def updateVariables(self):
        for key in self.av.keys():
            self.av[key].update({"value": self.av[key]["value"] + self.av[key]["incr"]})

    def getFunc(self):
        return self.func()


def main():
    term = TerminalSpace()
 
    # Set cursor to 0,0, set theme, clear terminal
    print(f"{term.home}{term.gray100_on_gray1}{term.clear}")
    
    term.addGraphspace(Graphspace(term, term.width, term.height-1, 10, 10, 1/16))

    term.graphspaces[0].addWave(Wave("math.sin(x - shift) * (amp * math.sin(shift))", term.aqua, {"shift": {"value": 1, "incr": 1/10}, "amp": {"value": 5, "incr": 0}}))
    term.graphspaces[0].addWave(Wave("math.sin(x + shift) * (amp * math.sin(shift))", term.bright_yellow, {"shift": {"value": 10, "incr": 1/10}, "amp": {"value": 7, "incr": 0}}))
    term.graphspaces[0].addWave(Wave("math.sin(2 * x + shift) * (amp * math.sin(shift))", term.bright_red, {"shift": {"value": 10, "incr": 1/3}, "amp": {"value": 2, "incr": 0}}))
    with term.cbreak():
        val = ""
        while val.lower() != "q":
            if(val.lower() == "m"):
                term.graphspaces[0].showMenu = not term.graphspaces[0].showMenu
            term.render()
            val = term.inkey(timeout=0.02)

if __name__ == "__main__":
    main()