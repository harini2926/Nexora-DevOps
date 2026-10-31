"""Simple 2D rigidbody placeholder — the C++ side drives the real physics."""


class Rigidbody2D:
    def __init__(self):
        self.velocity = (0.0, 0.0)
        self.mass     = 1.0
        self.gravity  = 400.0

    def add_force(self, fx, fy):
        """Add an impulse. Sign convention: +y is down."""
        vx, vy = self.velocity
        self.velocity = (vx + fx, vy + fy)