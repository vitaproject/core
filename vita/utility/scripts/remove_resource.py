
import argparse

from vita.utility.resource_manager import remove_resource


def main():

    parser = argparse.ArgumentParser(prog='vita_remove_resource',
                                     description='Removes a resource file from the VITA resource directory.')

    parser.add_argument('machine', type=str, help="A coded string identifying the fusion machine to which "
                                                  "this resource belongs, e.g. 'ST40', 'JET'.")
    parser.add_argument('type', type=str, help="A string identifying the resource type. Must be one of "
                                               "['equilibrium', 'mesh'].")
    parser.add_argument('id', type=str, help="A unique code to identify this resource, e.g. 'eq002'.")

    args = parser.parse_args()

    remove_resource(args.machine, args.type, args.id, prompt_user=True)
