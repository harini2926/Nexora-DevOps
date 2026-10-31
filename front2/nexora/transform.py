"""Position / rotation / scale for a game object."""


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"


class Transform:
    def __init__(self):
        self.position = Vector2()
        self.rotation = 0.0
        self.scale    = Vector2(1.0, 1.0)