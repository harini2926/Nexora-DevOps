"""
Nexora Game Engine — Python scripting API.

Scripts written inside the Nexora editor import this package to
control characters, scenes and game logic.

Example
-------
    import nexora

    class PlayerController(nexora.Component):
        def start(self):
            self.speed = 250

        def update(self, dt):
            axis = nexora.input.axis("Horizontal")
            self.transform.position.x += axis * self.speed * dt
"""

from .component import Component
from . import input
from . import log

__all__ = ["Component", "input", "log"]
__version__ = "0.1.0"