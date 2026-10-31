"""Messages that appear in the editor's AI / log panel."""

# The engine replaces this function at startup.
_sink = lambda level, msg: print(f"[{level}] {msg}")


def _set_sink(fn):
    """Called by the engine, not by user code."""
    global _sink
    _sink = fn


def info(msg):
    _sink("INFO", str(msg))


def warn(msg):
    _sink("WARN", str(msg))


def error(msg):
    _sink("ERROR", str(msg))