# Third party
import hou
from pxr import Plug, Tf

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("houdini.start")
_logger.setLevel(fxlog.DEBUG)


def set_node_primitive_default_path(
    node: hou.Node, nodes_to_ignore: list[str] = None, override_custom: bool = False
) -> None:
    """Sets default path for certain Houdini LOP nodes based on their USD
    plugin and schema types.

    Args:
        node (hou.Node): The node to set the primitive path on.
        nodes_to_ignore (list[str]): Add a list of node type names to ignore.
        override_custom (bool): Allow to override the node primpath even if a
            custom primitive path has already been defined. Defaults to `False`.
    """

    _logger.debug(f"Setting default primitive path for node: '{node.path()}'")

    # Combine nodes_to_ignore with defaults and create a set for O(1) lookups
    ignore_list = {"rendersettings", "renderproduct"}
    if nodes_to_ignore:
        ignore_list.update(nodes_to_ignore)

    # Early return conditions
    if (
        node.type().name() in ignore_list
        or node.type().category() != hou.lopNodeTypeCategory()
        or not (node.parm("primpath"))
    ):
        return

    # Determine the parameter to check
    parm_prim_name = "primpath"

    stage = node.stage()
    prim_path = node.evalParm(parm_prim_name)
    prim_path = hou.lop.makeValidPrimPath(prim_path)  # Fix wrong prim paths
    prim = stage.GetPrimAtPath(prim_path)
    prim_type_info = prim.GetPrimTypeInfo()
    prim_schema_type = prim_type_info.GetSchemaType()
    prim_parent_plugin = Plug.Registry().GetPluginForType(prim_schema_type)
    prim_parent_plugin_name = prim_parent_plugin.name
    prim_schema_type_name = prim_type_info.GetSchemaTypeName()

    if prim_parent_plugin_name == "UsdGeom":
        default_new_primitive_path = hou.lop.defaultNewPrimPath()
    elif prim_parent_plugin_name == "UsdLux":
        default_new_primitive_path = hou.lop.defaultLightsPrimPath()
    elif prim_schema_type_name == "Camera":
        default_new_primitive_path = hou.lop.defaultCamerasPrimPath()
    else:
        default_new_primitive_path = hou.lop.defaultNewPrimPath()

    # Early return if a custom value is set, and override is not on
    if node.parm(parm_prim_name).unexpandedString() != default_new_primitive_path and not override_custom:
        return

    # Early return if the schema type is unknown
    if prim_schema_type == Tf.Type.Unknown:
        return

    # Define the mapping of plugin and schema type names to default paths
    default_paths = {
        # Plugin name
        "usdGeom": "/world/geo/$OS",
        "usdVol": "/world/fx/$OS",
        "usdLux": "/world/lgt/$OS",
        # Schema type name
        "Camera": "/world/cam/$OS",
    }

    # Determine the default new primitive path based on the mapping
    default_new_primitive_path = default_paths.get(prim_parent_plugin_name, default_new_primitive_path)
    # Run over the plugin name (previous line) as schema type is more precise
    default_new_primitive_path = default_paths.get(prim_schema_type_name, default_new_primitive_path)

    _logger.debug(
        f"Plugin name: '{prim_parent_plugin_name}', Schema type name: '{prim_schema_type_name}', path: '{default_new_primitive_path}'"
    )
    node.parm(parm_prim_name).set(default_new_primitive_path)
