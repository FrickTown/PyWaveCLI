import main

class Menu():
    buffer: list[list[str]] = []
    minWidth = 10
    minHeight = 15

    decorations: dict = {
        "top": ["┏"] + ["━" for _ in range(minWidth)] + ["┓"],
        "row": ["┃"] + [" " for _ in range(minWidth)] + ["┃"],
        "bot": ["┗"] + ["━" for _ in range(minWidth)] + ["┛"],
    }

    def __init__(self, termSpace: main.TerminalSpace):
        self.termSpace = termSpace
    
    def generateMenu(self):
        self.buffer.append(self.decorations.get("top")[::])
        self.buffer.append(self.decorations.get("row")[::])
        self.buffer.append(self.decorations.get("bot")[::])
    