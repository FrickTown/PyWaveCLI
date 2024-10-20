from __future__ import annotations
import main

class Menu():
    buffer: list[list[str]] = []
    
    # Style values
    minWidth = 15
    minHeight = 30
    hPadding = 2
    vPadding = 1
    idxPadding = 3

    activeIndex = 0

    menuEntries: list[MenuEntry] = []

    def __init__(self, graphSpace: main.Graphspace):
        self.graphSpace = graphSpace
        for wave in graphSpace.waves:
            self.menuEntries.append(MenuEntry(self, wave))
    
    def addEntry(self, entry: MenuEntry):
        self.menuEntries.append(MenuEntry(self, entry))

    def generateMenu(self):
        self.buffer = []
        # Determine the width and height of the menu
        if(len(self.menuEntries) > self.minHeight): self.minHeight = len(self.menuEntries)
        self.minWidth = len(self.menuEntries[0].getFunction())
        for menuEntry in self.menuEntries:
            func = menuEntry.getFunction()
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
    
    def select(self, change: int):
        self.activeIndex = (self.activeIndex + change) % (len(self.menuEntries - 1))

class MenuEntry():
    def __init__(self, menu: Menu, wave: main.Wave):
        self.parent = menu
        self.wave = wave
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
        self.active = True
        self.selected = False
    
    def getFunction(self):
        return self.wave.func

    def getMenuRow(self):
        bg = ""
        fg = ""
        if(self.selected and not self.active):
            bg = self.colors["selectedBg"]
            fg = self.colors["selectedFg"]
        elif(not self.selected and not self.active):
            bg = self.colors["unselectedBg"]
            fg = self.colors["unselectedFg"]
        elif(self.active):
            bg = self.colors["highlitBg"]
            fg = self.colors["highlitFg"]

        padOut = [" " for _ in range((self.parent.minWidth) - len(self.getFunction()))]
        idx = list(f"{self.parent.menuEntries.index(self) + 1}. ")
        idx = list(map(lambda x: self.wave.termColor + x, idx))
        func = list((self.getFunction()))
        func[0] = (self.colors["underline"] if self.active else "") + func[0]
        func[-1] = func[-1] + self.colors["normal"]
        out = [self.parent.decorations.get("row")[0]] + [" " for _ in range(self.parent.hPadding)] + idx + func + padOut + [" " for _ in range(self.parent.hPadding)] + [self.colors["normal"] + self.parent.decorations.get("row")[-1]]
        return out