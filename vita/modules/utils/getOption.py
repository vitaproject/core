import sys, getopt

def getOption(option) :
  '''Get the named long option from the command line without modifying the command line arguments array.'''
  try:
    opts, args = getopt.gnu_getopt(sys.argv.copy(), "", [option+"="])
  except getopt.GetoptError:
    return None

  value = ''
  for opt, arg in opts:
    if opt == '--'+option:
      value = arg

  return value

if __name__ == "__main__":                                                      # Unit tests
  if 1 :
    '''test: getOption'''
    options  = sys.argv = ['--input', 'inputFile']
    assert(    getOption('input') == 'inputFile')
    assert(not getOption('input') == 'outputFile')
    assert(    sys.argv == options)
    print("inputFile ==", getOption('input'))
