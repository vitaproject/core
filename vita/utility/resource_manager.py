
import re
import os
from shutil import copy

_RESOURCE_ROOT = os.path.expanduser("~/.vita")
if not os.path.isdir(_RESOURCE_ROOT) :
    _RESOURCE_ROOT = os.environ['VITADATA']

    if not os.path.isdir(_RESOURCE_ROOT) :
        raise ValueError("Set environment variable VITADATA to the location of the vita data folder containing machine configurations")


def _test_allowed_characters(string):

    match = re.match("^[a-zA-Z0-9_\-]*$", string)

    if not match:
        raise ValueError("Allowed characters are letters, numbers, underscore and hyphen.")


def add_resource(machine, type, id, path, symlink=False):
    """
    Add a resource file to the VITA hidden resource directory.

    :param str machine: A string identifying the fusion machine (e.g. "ST40").
    :param str type: The type of resource file. Must be one of ["equilibrium", "mesh"]
    :param str id: A unique string identifier for the resource.
    :param str path: The file path to the selected resource.
    :param bool symlink: Flag to specify whether a symlink should be created instead of
      copying the file. Useful for large simulation files.
    """

    path = os.path.abspath(path)

    if not os.path.exists(path):
        raise ValueError("The path to the specified resource cannot be found.")

    _test_allowed_characters(machine)
    _test_allowed_characters(id)

    if type not in ["configuration", "equilibrium", "geometry", "mesh"]:
        raise ValueError("Resources must be of type ['configuration', 'equilibrium', 'geometry', 'mesh'].")

    directory = os.path.join(_RESOURCE_ROOT, machine, type)
    # create directory structure if missing
    if not os.path.isdir(directory):
        os.makedirs(directory)

    ext = os.path.splitext(path)[1]
    new_path = os.path.join(directory, id + ext)

    if os.path.exists(new_path):
        raise ValueError("This resource already exists, you must change the ID or update the existing resource.")

    if symlink:
        os.symlink(path, new_path)
    else:
        copy(path, new_path)


def update_resource(machine, type, id, path, symlink=False):
    """
    Over write an existing resource file in the VITA hidden resource directory.

    :param str machine: A string identifying the fusion machine (e.g. "ST40").
    :param str type: The type of resource file. Must be one of ["equilibrium", "mesh"]
    :param str id: A unique string identifier for the resource.
    :param str path: The file path to the selected resource.
    :param bool symlink: Flag to specify whether a symlink should be created instead of
      copying the file. Useful for large simulation files.
    """

    path = os.path.abspath(path)

    if not os.path.exists(path):
        raise ValueError("The path to the specified new resource cannot be found.")

    _test_allowed_characters(machine)
    _test_allowed_characters(id)

    if type not in ["configuration", "equilibrium", "geometry", "mesh"]:
        raise ValueError("Resources must be of type ['configuration', 'equilibrium', 'geometry', 'mesh'].")

    directory = os.path.join(_RESOURCE_ROOT, machine, type)
    if not os.path.isdir(directory):
        raise ValueError("The specified resource was not found.")

    candidates = os.listdir(directory)
    for candidate in candidates:
        if os.path.splitext(candidate)[0] == id:
            old_file = os.path.join(directory, candidate)
            break
    else:
        raise ValueError("Existing resource not found, you must add this as a new resource.")

    if symlink:
        os.symlink(path, old_file)
    else:
        copy(path, old_file)


def list_resources():
    dict_list = {}
    dict_list['path'] = _RESOURCE_ROOT
    dict_list['machines'] = next(os.walk(dict_list['path']))[1]
    dict_list['equilibrium'] = {}
    dict_list['geometry'] = {}
    for machine in dict_list['machines']:
        for resource in ['equilibrium', 'geometry']:
            localpath = _RESOURCE_ROOT + '/' + machine + '/' + resource
            if not os.path.isdir(localpath): # resource type not found
                dict_list[resource][machine] = []
            else:
                dict_list[resource][machine] = os.listdir(localpath)
    return dict_list


def get_resource(machine, type, id):
    """
    Get the path to a VITA resource.

    :param str machine: A string identifying the fusion machine (e.g. "ST40").
    :param str type: The type of resource file. Must be one of ["equilibrium", "mesh"]
    :param str id: A unique string identifier for the resource.
    :return: The path to the selected resource.
    """

    _test_allowed_characters(machine)
    _test_allowed_characters(id)

    if type not in ["configuration", "equilibrium", "geometry", "mesh"]:
        raise ValueError("Resources must be of type ['configuration', 'equilibrium', 'geometry', 'mesh'].")

    directory = os.path.join(_RESOURCE_ROOT, machine, type)
    if not os.path.isdir(directory):
        raise ValueError("The specified resource was not found."
                         "{} - {} - {}".format(machine, type, id))

    candidates = os.listdir(directory)
    for candidate in candidates:
        if os.path.splitext(candidate)[0] == id:
            resource_path = os.path.join(directory, candidate)
            break
    else:
        raise ValueError("Existing resource not found, you must add this as a new resource.")

    return resource_path


def remove_resource(machine, type, id, prompt_user=False):
    """
    Remove a resource from the VITA resource file catalog.

    :param str machine: A string identifying the fusion machine (e.g. "ST40").
    :param str type: The type of resource file. Must be one of ["equilibrium", "mesh"]
    :param str id: A unique string identifier for the resource.
    :param bool prompt_user: Ask the user to confirm before deleting the file.
    """

    _test_allowed_characters(machine)
    _test_allowed_characters(id)

    if type not in ["configuration", "equilibrium", "mesh"]:
        raise ValueError("Resources must be of type ['configuration', 'equilibrium', 'mesh'].")

    directory = os.path.join(_RESOURCE_ROOT, machine, type)
    if not os.path.isdir(directory):
        raise ValueError("The specified resource was not found.")

    candidates = os.listdir(directory)

    for file in candidates:

        if os.path.splitext(file)[0] == id:
            file = os.path.join(directory, file)
            break

    else:
        raise ValueError("The specified resource was not found.")

    if prompt_user:
        print()
        print("Are you sure you wish to remove this resource file?")
        print("{}".format(file))
        confirmation = input("Confirm by typing 'yes': ")

        if not confirmation == "yes":
            print("Remove operation aborted.")
            return

    os.remove(file)

    if prompt_user:
        print("The resource file was deleted.")
