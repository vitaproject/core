
import argparse

from vita.utility.resource_manager import update_resource


def main():

    parser = argparse.ArgumentParser(prog='vita_update_resource',
                                     description='Updates an existing resource file in the VITA hidden directory.')

    parser.add_argument('machine', type=str, help="A coded string identifying the fusion machine to which "
                                                  "this resource belongs, e.g. 'ST40', 'JET'.")
    parser.add_argument('type', type=str, help="A string identifying the resource type. Must be one of "
                                               "['equilibrium', 'mesh'].")
    parser.add_argument('id', type=str, help="A unique code to identify this resource, e.g. 'eq002'.")
    parser.add_argument('path', type=str, help="The file path to the selected resource.")

    args = parser.parse_args()

    update_resource(args.machine, args.type, args.id, args.path)
