"""
[PyWaveCLI Module]
menu.py -- A circular dependency for main.py describing and implementing the logic for the menu system.
Author: FrickTown (https://github.com/FrickTown/)
"""
from __future__ import annotations
from blessed import keyboard
import math
import copy
import main
from abc import ABC, abstractmethod

class Menu(ABC):
    # Frame buffer
    buffer: list[list[str]] = []
    
    # Style values
    minWidth: int = 15
    minHeight: int = 30
    hPadding: int = 2
    vPadding: int = 1
    idxPadding: int = 3
    decorations: dict = {}
    xRenderOffset = 0
    yRenderOffset = 0

    # Submenu logic // Root menu will have None values for name and parent
    parentMenu: Menu = None
    uniqueName: str = None
    activeSubmenu: Menu = None

    # InputWindow logic
    inputWindowOverride: bool = False

    def __init__(self, graphSpace: main.Graphspace, name: str = None, parentMenu: Menu = None):
        self.graphSpace = graphSpace
        self.uniqueName = name
        self.parentMenu = parentMenu
    
    def createRowFromString(self, rowText: str, color: str):
        """ Create a properly formatted row that fits into the menu, from a supplied string and color.
        keyword arguments:
        rowText -- String to write to menu row
        color -- The ANSI code to color the menu row
        """
        padOut = []
        if len(rowText) > self.minWidth: rowText = rowText[0:(self.minWidth - len(rowText))] # Cut off if too long
        else: padOut = [" " for _ in range((self.minWidth + 3) - len(rowText))] # How many additional whitespaces to we need to print from the end of the function string to the end of the menu?
        rowList = list(rowText)
        rowList = list(map(lambda x: color + x, rowList))
        out = [self.decorations.get("row")[0]] + [" " for _ in range(self.hPadding)] + rowList + padOut + [" " for _ in range(self.hPadding)] + [self.graphSpace.parent.normal + self.decorations.get("row")[-1]]
        return out
    
    def recursiveSubMenuFetch(self):
        if(self.activeSubmenu):
            return self.activeSubmenu.recursiveSubMenuFetch()
        else:
            return self

    @abstractmethod
    def generateMenu(self):
        pass

    @abstractmethod
    def handleInput(self, keyval: keyboard.Keystroke):
        pass
    

class SelectionMenu(Menu):

    # Menu entry logic
    activeIndex: int = None
    menuEntries: list[MenuEntry] = []

    def __init__(self, graphSpace, name = None, parentMenu = None):
        super().__init__(graphSpace, name, parentMenu)
        self.menuEntries = []
        if(parentMenu):
            self.xRenderOffset = parentMenu.xRenderOffset + len(parentMenu.buffer[0])

    def generateMenu(self):
        """ Uses all current menu data to generate a frame buffer. Should only be called when menu's data has changed in any way."""
        if(self.parentMenu):
            self.xRenderOffset = self.parentMenu.xRenderOffset + len(self.parentMenu.buffer[0])
        self.buffer = []
        # Determine the width and height of the menu
        if(len(self.menuEntries) > 0):
            if(len(self.menuEntries) > self.minHeight): self.minHeight = len(self.menuEntries)
            self.minWidth = len(self.menuEntries[0].getEntryText())
            for menuEntry in self.menuEntries:
                func = menuEntry.getEntryText()
                if(len(func) > self.minWidth):
                    self.minWidth = len(func)

        # Generate the non-menu entry rows
        self.decorations: dict = {
            "top": ["┏"] + ["━" for _ in range(self.minWidth + self.hPadding*2 + self.idxPadding)] + ["┓"],
            "row": ["┃"] + [" " for _ in range(self.minWidth + self.hPadding*2 + self.idxPadding)] + ["┃"],
            "bot": ["┗"] + ["━" for _ in range(self.minWidth + self.hPadding*2 + self.idxPadding)] + ["┛"],
        }

        # Print the rows
        
        self.buffer.append(self.decorations.get("top")[::])     # Print the top

        for _ in range(self.vPadding):                          # Top padding
            self.buffer.append(self.decorations.get("row")[::])
        
        for menuEntry in self.menuEntries:                      # Get the unique rows by generating a row for each menu entry
            self.buffer.append(menuEntry.getMenuRow())

        for _ in range(self.vPadding):                          # Bottom padding
            self.buffer.append(self.decorations.get("row")[::])

        self.buffer.append(self.decorations.get("bot")[::])     # Print bottom

        if(self.getSelectedEntry().inputWindow is not None):
            self.getSelectedEntry().inputWindow.generateMenu()

    def getSelectableEntries(self):
        """Return a subset of the menu's entries containing all elements that can be selected"""
        return list(filter(lambda x: x.selectable, self.menuEntries))
    
    def getSelectedEntry(self) -> SelectableEntry:
        """Return the MenuEntry subclass object that is currently selected in the menu"""
        return self.menuEntries[self.activeIndex]
    
    def addEntries(self, entries: list[MenuEntry]):
        """ Add multiple entries in a list. Currently unused.
        keyword arguments:
            entries -- The list of objects of MenuEntry subclasses to be added to the menu
        """
        for entry in entries:
            if len(self.getSelectableEntries()) == 0 and entry.selectable:
                entry.active = True
                self.activeIndex = len(self.menuEntries)
            self.menuEntries.append(entry)

    def addInfoEntry(self, info: str, color: str):
        """ Create and add a text entry.
        keyword arguments:
            info -- The string to be represented in the menu
            color -- The ANSI color for the string
        """
        newEntry = InfoEntry(self, info, color)
        self.menuEntries.append(newEntry)
    
    def addWaveEntry(self, wave: main.Wave):
        """ Create and add a wave entry.
        keyword arguments:
            wave -- The wave which will be represented by its function in the menu
        """
        newEntry = WaveEntry(self, wave)
        if(len(self.getSelectableEntries()) == 0):
            newEntry.active = True
            self.activeIndex = len(self.menuEntries)
        self.menuEntries.append(newEntry)
        self.generateMenu()
        newEntry.createSubMenu()

    def addArgEntry(self, wave: main.Wave, argName: str):
        """ Create and add an arg entry.
        keyword arguments:
            wave -- The wave which will be represented by its function in the menu
            argName -- The name of the custom variable
        """
        newEntry = ArgEntry(self, wave, argName)
        if(len(self.getSelectableEntries()) == 0):
            newEntry.active = True
            self.activeIndex = len(self.menuEntries)
        self.menuEntries.append(newEntry)
        self.generateMenu()
        newEntry.createSubMenu()
    
    def handleInput(self, keyval: keyboard.Keystroke):
        # If an input window is open, pass the input along to it
        if(self.inputWindowOverride):
            self.getSelectedEntry().inputWindow.handleInput(keyval)
            return

        # If this menu is displaying a submenu, pass the input along 'til it reaches its maximum depth
        if(self.activeSubmenu):
            self.activeSubmenu.handleInput(keyval)
            return # Ensure no double actions
        
        if keyval.name:   
            keyname = keyval.name

            if(keyname == "KEY_UP"):
                self.select(-1)
            elif(keyname == "KEY_DOWN"):
                self.select(1)
            elif(keyname == "KEY_ENTER"):
                self.toggleSubMenu()
            elif(keyname == "KEY_BACKSPACE"):
                if(not self.parentMenu):
                    self.graphSpace.showMenu = False
                    return
                self.parentMenu.toggleSubMenu()
            elif(keyname == "KEY_TAB"):
                if(type(self.getSelectedEntry()) is WaveEntry):
                    sel: WaveEntry = self.getSelectedEntry()
                    sel.wave.visible = not sel.wave.visible
                return
        
        if(keyval.lower() == "r"):
            if(type(self.getSelectedEntry()) is WaveEntry):
                wav: WaveEntry = self.getSelectedEntry()
                wav.wave.resetWave()
                self.generateMenu()
        elif(keyval.lower() == " "):
            self.getSelectedEntry().openInputWindow()
            return

    def select(self, change: int):
        """Select a neighboring entry in the active menu
        keyword arguments:
            change -- Integer of value (-1) or 1, for ascending / descending along the list entries.
        """
        selectableEntries = self.getSelectableEntries()
        if(len(selectableEntries) == 0):
            return
        selectableIndex = selectableEntries.index(self.menuEntries[self.activeIndex])
        newIndex = (selectableIndex + change)

        if(newIndex < 0):
            newIndex = len(selectableEntries) - 1
        newIndex %= len(selectableEntries)
        newSelection = selectableEntries[newIndex]
        newActualIndex = self.menuEntries.index(newSelection)

        self.menuEntries[self.activeIndex].active = False
        newSelection.active = True
        self.activeIndex = newActualIndex
        self.generateMenu()

    def toggleSubMenu(self):
        """If the currently selected SelectableMenuEntry subclass has a submenu with a non-None value, set it as this Menu's active SubMenu. If a SubMenu is already active, deactivate it.
        """
        if(self.activeIndex is None):
            return
        selectedEntry: SelectableEntry = self.getSelectedEntry()
        if self.activeSubmenu is None and selectedEntry.subMenu:
            selectedEntry.subMenu.generateMenu()
            self.activeSubmenu = selectedEntry.subMenu
        elif self.activeSubmenu:
            self.activeSubmenu = None


class MenuEntry(ABC):
    def __init__(self, menu: Menu):
        self.parent = menu
        self.styles = {
            "underline": self.parent.graphSpace.parent.underline,
            "normal": self.parent.graphSpace.parent.normal
        }
        self.selectable = False
        self.active = False
        self.selected = False

    @abstractmethod
    def getEntryText(self):
        pass

    @abstractmethod
    def getMenuRow(self):
        pass



class InfoEntry(MenuEntry):
    def __init__(self, menu: Menu, info: str, color: str):
        super().__init__(menu)
        self.info = info
        self.color = color
    
    def getEntryText(self):
        return self.info
    
    def getMenuRow(self):
        return self.parent.createRowFromString(self.getEntryText(), self.color)


class SelectableEntry(MenuEntry):
    subMenu: Menu = None
    inputWindow: InputWindow = None

    def __init__(self, menu: Menu):
        super().__init__(menu)
        self.selectable = True


    def onInputWindowCancel(self):
        self.inputWindow = None
        self.parent.inputWindowOverride = False

    @abstractmethod
    def openInputWindow(self, title: str = ""):
        self.parent.inputWindowOverride = True

    @abstractmethod
    def createSubMenu(self):
        pass

    @abstractmethod
    def onInputWindowConfirm(self, input: str, args: tuple) -> bool:
        pass
    


class WaveEntry(SelectableEntry):

    def __init__(self, menu: Menu, wave: main.Wave):
        super().__init__(menu)
        self.wave = wave
        self.color = wave.termColor
    
    def getEntryText(self):
        return self.wave.func

    def getMenuRow(self):
        padOut = [" " for _ in range((self.parent.minWidth) - len(self.getEntryText()))] # How many additional whitespaces to we need to print from the end of the function string to the end of the menu?
        idx = list(f"{self.parent.getSelectableEntries().index(self) + 1}. ")
        idx = list(map(lambda x: self.wave.termColor + x, idx))
        func = list((self.getEntryText()))
        func[0] = (self.styles["underline"] if self.active else "") + func[0]
        func[-1] = func[-1] + self.styles["normal"]
        out = [self.parent.decorations.get("row")[0]] + [" " for _ in range(self.parent.hPadding)] + idx + func + padOut + [" " for _ in range(self.parent.hPadding)] + [self.styles["normal"] + self.parent.decorations.get("row")[-1]]
        return out

    def createSubMenu(self):
        self.subMenu = SelectionMenu(self.parent.graphSpace, f"waveArgs{self.parent.getSelectableEntries().index(self)}", self.parent)
        for var in self.wave.customVars.keys():
            self.subMenu.addArgEntry(self.wave, var)
        self.subMenu.generateMenu()

    def onInputWindowConfirm(self, input: str, args: tuple) -> bool:
            if(not self.wave.tryUpdateWaveFunction(input, {})):
                return False

            self.parent.inputWindowOverride = False
            self.inputWindow = None
            self.parent.generateMenu()
            return True
    
    def openInputWindow(self, title: str = ""):
        super().openInputWindow(title)
        self.inputWindow = InputWindow(self, "Enter a new function:")
        self.inputWindow.setValueBuffer(list(self.wave.func))


class ArgEntry(SelectableEntry):
    def __init__(self, menu: Menu, wave: main.Wave, argName: str):
        super().__init__(menu)
        self.wave = wave
        self.argName = argName
        self.argRow = wave.customVars[argName]
    
    def getEntryText(self):
        return f"{self.argName}: {self.argRow['incr']}"

    def getMenuRow(self):
        padOut = [" " for _ in range((self.parent.minWidth) - len(self.getEntryText()))] # How many additional whitespaces to we need to print from the end of the function string to the end of the menu?
        idx = list(f"{self.parent.getSelectableEntries().index(self) + 1}. ")
        idx = list(map(lambda x: self.wave.termColor + x, idx))
        func = list(self.getEntryText())
        func[0] = (self.styles["underline"] if self.active else "") + func[0]
        func[-1] = func[-1] + self.styles["normal"]
        out = [self.parent.decorations.get("row")[0]] + [" " for _ in range(self.parent.hPadding)] + idx + func + padOut + [" " for _ in range(self.parent.hPadding)] + [self.styles["normal"] + self.parent.decorations.get("row")[-1]]
        return out
    
    def createSubMenu(self):
        pass

    def onInputWindowConfirm(self, input: str, args: tuple) -> bool:
        try:
            tryParse = eval("lambda: "+ input)
            newValue = tryParse()
        except Exception:
            return False
        self.wave.customVars[self.argName][args[0]] = newValue
        self.parent.inputWindowOverride = False
        self.inputWindow = None
        self.parent.generateMenu()
        return True

    def openInputWindow(self, title: str = ""):
        super().openInputWindow(title)
        self.inputWindow = InputWindow(self, "Enter increment value for " + self.argName + ":", "incr".center(4))
        self.inputWindow.setValueBuffer(list(str(self.wave.customVars[self.argName]["incr"])))

class InputWindow(Menu):
    # Frame buffer
    buffer: list[list[str]] = [[]]
    
    # Style values
    minWidth: int = 20
    minHeight: int = 30
    hPadding: int = 2
    vPadding: int = 1
    decorations: dict = {}
    xRenderOffset: int = 0

    # Text value logic
    valueBuffer: list[str] = []
    cursorPos: int = 0

    title: str = ""
    titleAsBuffer: list[str] = []

    def __init__(self, parentEntry: SelectableEntry, textPrompt: str, *args):
        self.args = args
        self.title = textPrompt
        self.valueBuffer: list[str] = []
        self.minWidth = len("| Confirm: (Enter) | Cancel: (Escape) |") + self.hPadding
        self.generateDecorations()
        self.parentMenu: SelectionMenu = parentEntry.parent
        self.graphSpace: main.Graphspace = self.parentMenu.graphSpace
        self.parentEntry: SelectableEntry = parentEntry
        self.titleAsBuffer = self.createRowFromString(textPrompt, self.graphSpace.parent.bright_magenta)
        self.xRenderOffset = round(self.graphSpace.xCellCount / 2) - round(self.minWidth/2) - self.hPadding
        self.yRenderOffset = round(self.graphSpace.yCellCount / 2) - round(self.minHeight/2) + self.vPadding
        self.invalid = False
    
    def generateDecorations(self):
        self.decorations = {
            "top": ["┏"] + ["━" for _ in range(self.minWidth + self.hPadding*2)] + ["┓"],
            "row": ["┃"] + [" " for _ in range(self.minWidth + self.hPadding*2)] + ["┃"],
            "bot": ["┗"] + ["━" for _ in range(self.minWidth + self.hPadding*2)] + ["┛"],
        }

    def setValueBuffer(self, buffer: list[str]):
        self.valueBuffer = buffer
        self.generateMenu()

    def createRowFromString(self, rowText: str, color: str):
        """ Create a properly formatted row that fits into the window, from a supplied string and color.
        keyword arguments:
        rowText -- String to write to menu row
        color -- The ANSI code to color the menu row
        """
        rowList = list(rowText)
        return self.generateMenuRowFromList(rowList, color)

    def generateMenuRowFromList(self, rowList: list[str], color: str):
        padOut = []
        padOut = [" " for _ in range((self.minWidth) - len(rowList))] # How many additional whitespaces to we need to print from the end of the function string to the end of the menu?
        rowList = list(map(lambda x: color + x, rowList))
        out = [self.decorations.get("row")[0]] + [" " for _ in range(self.hPadding)] + rowList + padOut + [" " for _ in range(self.hPadding)] + [self.graphSpace.parent.normal + self.decorations.get("row")[-1]]
        return out
    
    def addToVal(self, char):
        self.valueBuffer.append(char)
    
    def remFromVal(self):
        if len(self.valueBuffer):
            self.valueBuffer.pop()

    def generateMenu(self):
        """ Uses all current menu data to generate a frame buffer. Should only be called when menu's data has changed in any way."""
        self.buffer = []

        if(len(self.valueBuffer) > self.minWidth):
            self.minWidth = len(self.valueBuffer) + self.hPadding
            self.generateDecorations()
            self.titleAsBuffer = self.createRowFromString(self.title, self.graphSpace.parent.bright_magenta)

        # Print the rows
        self.buffer.append(self.decorations.get("top")[::])     # Print the top

        for _ in range(self.vPadding):                          # Top padding
            self.buffer.append(self.decorations.get("row")[::])

        self.buffer.append(self.titleAsBuffer)
        self.buffer.append(self.decorations.get("row")[::])
        # Print the cursor
        displayBuffer = self.valueBuffer[::]
        if(self.cursorPos == 0):
            displayBuffer.append(self.graphSpace.parent.gray100 + "_")
        else:
            displayBuffer.insert(self.cursorPos, self.graphSpace.parent.gray100 + "_")
        self.buffer.append(self.generateMenuRowFromList(displayBuffer, self.graphSpace.parent.bright_green if not self.invalid else self.graphSpace.parent.brown1))
        for _ in range(self.vPadding):                          # Bottom padding
            self.buffer.append(self.decorations.get("row")[::])

        self.buffer.append(self.createRowFromString("Confirm: (Enter) | Cancel: (Escape)".center(4, "-"), self.graphSpace.parent.steelblue1))
        self.buffer.append(self.decorations.get("bot")[::])     # Print bottom

        self.xRenderOffset = round(self.graphSpace.xCellCount / 2) - round(len(self.buffer[0])/2)
        self.yRenderOffset = round(self.graphSpace.yCellCount / 2) - round(len(self.buffer)/2)

    def handleInput(self, keyval: keyboard.Keystroke):
        """Input handler for InputMenu. Checks for special keys, otherwise, passes it on to the value buffer. 
        keyword arguments:
            keyval -- The keystroke read from stdin
        """
        if(keyval.name):
            keyname = keyval.name
            if(keyname == "KEY_ENTER"):
                    if(self.parentEntry.onInputWindowConfirm("".join(self.valueBuffer), self.args)):self.invalid = False
                    else:self.invalid = True
            elif(keyname == "KEY_BACKSPACE"):
                self.remFromVal()
                self.invalid = False
            elif(keyname == "KEY_ESCAPE"):
                self.valueBuffer = []
                self.invalid = False
                self.parentEntry.onInputWindowCancel()
            elif(keyname == "KEY_RIGHT"):
                self.cursorPos += 1 if self.cursorPos < 0 else 0
            elif(keyname == "KEY_LEFT"):
                self.cursorPos -= 1 if abs(self.cursorPos) < len(self.valueBuffer) else 0
        elif(keyval.isprintable()):
            self.invalid = False
            self.addToVal(keyval.lower())
        self.generateMenu()