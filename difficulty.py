class Difficulty:
    def __init__(self, height: int, width: int, bombs: int):
        self.height = height
        self.width = width
        self.bombs = bombs

    def __str__(self) -> str:
        return f'{self.height}x{self.width} - {self.bombs} bombs'
