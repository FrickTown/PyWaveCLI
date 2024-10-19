import M6_Projekt.rewrite

class Menu():
    buffer: list[list[str]] = [[]]
    minWidth = 10
    minHeight = 15

    decorations: dict = {
        "top": ["┏"] + ["━" for _ in range(minWidth)] + ["┓"],
        "row": ["┃"] + [" " for _ in range(minWidth)] + ["┃"],
        "bot": ["┗"] + ["━" for _ in range(minWidth)] + ["┛"],
    }

    def __init__(self, termSpace: TerminalSpace):
        self.termSpace = termSpace
    
    def generateMenu(self):
        self.buffer[0] = self.decorations.get("top")[::]
        self.buffer[1] = self.decorations.get("row")[::]
        self.buffer[2] = self.decorations.get("bot")[::]
    