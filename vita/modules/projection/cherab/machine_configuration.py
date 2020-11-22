
import os
import json
from raysect.core import rotate_z
from raysect.primitive import import_obj, import_ply, import_stl, import_vtk
from raysect.optical.material import AbsorbingSurface

from vita.utility.resource_manager import get_resource


def load_wall_configuration(config_file, parent):

    with open(config_file, 'r') as fh:
        vita_input = json.load(fh)

    machine_id = vita_input["machine-settings"]["machine-id"]

    try:
        wall_components = vita_input["machine-settings"]["wall-components"]
    except KeyError:
        raise IOError("Invalid vita config JSON - no 'wall-components' specification.")

    if not isinstance(wall_components, list):
        raise IOError("Invalid vita config JSON - expected a list of wall component specifications.")

    for component in wall_components:

        if not isinstance(component, dict):
            raise IOError("Invalid vita config JSON - expected a dictionary specifying the component.")

        resource_id = component["mesh-resource-id"]

        try:
            scaling = component["scaling"]
        except KeyError:
            scaling = None

        try:
            period = component["period"]
            if 360 % period:
                raise IOError("Invalid vita config JSON - the angle period must be divisible into 360 "
                              "degrees an integer number of times.")
        except KeyError:
            period = 360

        try:
            rotation_offset = component["rotation_offset"]
        except KeyError:
            rotation_offset = 0

        # TODO - add proper material handling
        material = AbsorbingSurface()

        mesh_instances = int(360 / period)

        mesh_file = get_resource(machine_id, 'mesh', resource_id)
        path, filename = os.path.split(mesh_file)
        name, ext = os.path.splitext(filename)

        importer = _import_functions[ext]

        mesh = importer(mesh_file, scaling=scaling, name=name, transform=rotate_z(rotation_offset))
        for i in range(mesh_instances):
            mesh.instance(material=material, parent=parent, transform=rotate_z(i * period), name=name)


_import_functions = {
    '.obj': import_obj,
    '.ply': import_ply,
    '.stl': import_stl,
    '.vtk': import_vtk
}
