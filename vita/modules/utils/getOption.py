
import sys, getopt


def getOption(option):
    '''Get the named long option from the command line without modifying the command line arguments array.'''

    try:
        opts, args = getopt.gnu_getopt(sys.argv.copy(), "", [option + "="])
    except getopt.GetoptError:
        return None

    value = ''
    for opt, arg in opts:
        if opt == '--' + option:
            value = arg

    return value
