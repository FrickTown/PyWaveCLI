from __future__ import annotations
import main

class Menu():
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

    # Submenu logic // Root menu will have None values for name and parent
    uniqueName: str = None
    parentMenu: Menu = None
    activeSubmenu: Menu = None

    # Menu entry logic
    activeIndex: int = None
    menuEntries: list[MenuEntry] = []

    def __init__(self, graphSpace: main.Graphspace, name: str = None, parentMenu: Menu = None):
        self.graphSpace = graphSpace
        self.uniqueName = name
        self.parentMenu = parentMenu
        self.menuEntries = []
        if(parentMenu):
            self.xRenderOffset = parentMenu.xRenderOffset + len(parentMenu.buffer[0]) + 1

    def getSelectableEntries(self):
        """Return a subset of the menu's entries containing all elements that can be selected"""
        return list(filter(lambda x: x.selectable, self.menuEntries))
    
    def getSelectedEntry(self):
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
        """ Create a text entry.
        keyword arguments:
            info -- The string to be represented in the menu
            color -- The ANSI color for the string
        """
        newEntry = InfoEntry(self, info, color)
        self.menuEntries.append(newEntry)
    
    def addWaveEntry(self, wave: main.Wave):
        """ Create a wave entry.
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

    def generateMenu(self):
        """ Uses all current menu data to generate a frame buffer. Should only be called when menu's data has changed in any way."""
        self.buffer = []
        # Determine the width and height of the menu
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

    def handleInput(self, keyname: str):
        if(self.activeSubmenu):
            self.activeSubmenu.handleInput(keyname)
            return
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
        if(not self.activeIndex):
            return
        selectedEntry: SelectableEntry = self.getSelectedEntry()
        if self.activeSubmenu is None and selectedEntry.subMenu:
            self.activeSubmenu = selectedEntry.subMenu
        elif self.activeSubmenu:
            self.activeSubmenu = None

class MenuEntry():
    def __init__(self, menu: Menu):
        self.parent = menu
        self.colors = {
            "selectedBg": self.parent.graphSpace.parent.on_bright_orange,
            "selectedFg": self.parent.graphSpace.parent.white,
            "unselectedBg": self.parent.graphSpace.parent.on_black,
            "unselectedFg": self.parent.graphSpace.parent.white,
            "highlitBg": self.parent.graphSpace.parent.on_white,
            "highlitFg": self.parent.graphSpace.parent.black,
            "underline": self.parent.graphSpace.parent.underline,
            "normal": self.parent.graphSpace.parent.normal
        }
        self.selectable = False
        self.active = False
        self.selected = False

    def getEntryText(self):
        return ""

    def getMenuRow(self):
        return [" "]

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
    subMenu = None
    def __init__(self, menu: Menu):
        super().__init__(menu)
        self.selectable = True

    def createSubMenu(self):
        pass

class WaveEntry(SelectableEntry):

    def __init__(self, menu: Menu, wave: main.Wave):
        super().__init__(menu)
        self.wave = wave
    
    def getEntryText(self):
        return self.wave.func

    def getMenuRow(self):
        padOut = [" " for _ in range((self.parent.minWidth) - len(self.getEntryText()))] # How many additional whitespaces to we need to print from the end of the function string to the end of the menu?
        idx = list(f"{self.parent.getSelectableEntries().index(self) + 1}. ")
        idx = list(map(lambda x: self.wave.termColor + x, idx))
        func = list((self.getEntryText()))
        func[0] = (self.colors["underline"] if self.active else "") + func[0]
        func[-1] = func[-1] + self.colors["normal"]
        out = [self.parent.decorations.get("row")[0]] + [" " for _ in range(self.parent.hPadding)] + idx + func + padOut + [" " for _ in range(self.parent.hPadding)] + [self.colors["normal"] + self.parent.decorations.get("row")[-1]]
        return out

    def createSubMenu(self):
        self.subMenu = Menu(self.parent.graphSpace, f"waveArgs{self.parent.getSelectableEntries().index(self)}", self.parent)
        for var in self.wave.customVars.keys():
            self.subMenu.addInfoEntry(f"{var}: {self.wave.customVars[var]["incr"]}", self.wave.termColor)
        self.subMenu.generateMenu()