"""Base class for every game object script."""


class Component:
    """
    Attach to a game object by subclassing it.

    The engine calls:
        start()             once, when Play begins
        update(dt)          every frame, dt is seconds since last frame
        on_collision(other) whenever this object collides with another

    Attributes filled in by the engine before start() is called:
        transform   -- position, rotation, scale
        rigidbody   -- velocity, mass, gravity
        game_object -- the object this component is attached to
    """

    def __init__(self):
        self.transform = None
        self.rigidbody = None
        self.game_object = None

    # ----- lifecycle hooks: override in your subclass -----

    def start(self):
        pass

    def update(self, dt):
        pass

    def on_collision(self, other):
        pass