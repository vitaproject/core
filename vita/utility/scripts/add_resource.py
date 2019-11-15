
import argparse

from vita.utility.resource_manager import add_resource


def main():

    parser = argparse.ArgumentParser(prog='vita_add_resource',
                                     description='Adds a resource file to the VITA hidden directory.')

    parser.add_argument("-l", "--symlink", default=False, action="store_true",
                        help="Instead of copying the resource file, create a symbolic link.")
    parser.add_argument('machine', type=str, help="A coded string identifying the fusion machine to which "
                                                  "this resource belongs, e.g. 'ST40', 'JET'.")
    parser.add_argument('type', type=str, help="A string identifying the resource type. Must be one of "
                                               "['equilibrium', 'mesh'].")
    parser.add_argument('id', type=str, help="A unique code to identify this resource, e.g. 'eq002'.")
    parser.add_argument('path', type=str, help="The file path to the selected resource.")

    args = parser.parse_args()

    add_resource(args.machine, args.type, args.id, args.path, symlink=args.symlink)
