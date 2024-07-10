# Third-party
import hou

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("houdini.OnCreated")
_logger.setLevel(fxlog.DEBUG)

# Runtime
if hou.isUIAvailable():
    node: hou.Node = kwargs["node"]  # type: ignore
    _logger.debug(f"Node created: {node.path()}")
