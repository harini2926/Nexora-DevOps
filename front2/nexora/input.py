"""Keyboard and mouse input, polled from the engine each frame."""

# The C++ side fills these sets each frame before calling update().
_pressed_keys  = set()
_down_keys     = set()
_axes          = {"Horizontal": 0.0, "Vertical": 0.0}


def _set_state(down, pressed, axes):
    """Called by the engine, not by user code."""
    global _down_keys, _pressed_keys, _axes
    _down_keys    = set(down)
    _pressed_keys = set(pressed)
    _axes         = dict(axes)


def is_down(key):
    """True while the key is held."""
    return key in _down_keys


def pressed(key):
    """True only on the frame the key was first pressed."""
    return key in _pressed_keys


def axis(name):
    """Returns -1.0, 0.0 or 1.0 for 'Horizontal' or 'Vertical'."""
    return _axes.get(name, 0.0)