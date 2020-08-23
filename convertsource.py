import pathlib
import argparse
import textwrap
import re

parser = argparse.ArgumentParser(description = 'Convert media sources and links to jsdelivr CDN URLs')
parser.add_argument(
  '-i', '--input', 
  metavar = 'PATH', 
  help = 'The file to process',
  action = 'store'
)
parser.add_argument(
  '-o', '--output', 
  metavar = 'PATH', 
  help = 'Provide an alternative output file. The default is to override the input file',
  action = 'store'
)
parser.add_argument(
  '-b', '--base', 
  metavar = 'URL', 
  help = 'Provide an URL as base',
  action = 'store'
)
parser.add_argument(
  '-d', '--dir', 
  metavar = 'DIRECTORY', 
  help = 'Convert only if the URL is the subresource of these directories. ' + 
    'Directories seperates by comma and should be URL-encoded. ' + 
    'The default is src/ and thumbnail/',
  action = 'store',
  default = 'src,thumbnail'
)
parser.add_argument(
  '-e', '--element', 
  metavar = 'ELEMENT', 
  help = 'Elements to be processed. Supports "a", "img", "source". The default is "a" and "img"',
  action = 'store',
  default = 'a,img'
)
parser.add_argument(
  '--debug', 
  metavar = 'ENTRY', 
  help = 'Run specific debug program',
  action = 'store'
)

args = parser.parse_args()

required_args = [('-i/--input', 'input'), ('-b/--base', 'base')]
if not hasattr(args, 'debug'):
  for arg in required_args:
    if not hasattr(args, arg[1]):
      print('error: argument {} required'.format(arg[0]))
      exit(2)

# https://cdn.jsdelivr.net/gh/user/repo@version/file


def pairpattern(source, leftIdx, pair, *, skipList = None, escapechar = '\\'):
  if skipList == None:
    skipList = [
      ("'", "'", False),     ('"', '"', False),  ('""""', '""""', False),
      ("'''", "'''", False), ('#', '\n', False)
    ]

  left, right, nesting = pair
  if source[leftIdx: leftIdx + len(left)] != left:
    raise TypeError('The index {} at the given string reads "{}" instead of "{}"'.format(leftIdx, source[leftIdx], left))

  pairs = skipList + [pair]
  symbols = []
  for cur in pairs:
    if not cur[0] in symbols:
      symbols.append(cur[0])
    if not cur[1] in symbols:
      symbols.append(cur[1])

  symbols.sort(key = lambda item: len(item), reverse = True)
  symbolStack = [pair]
  i = leftIdx + len(left)

  while i < len(source):
    curSymb = ''
    # view
    view = source[i : i + 1]
    if view == escapechar:
      i += 2
      continue

    for cur in symbols:
      view = source[i : i + len(cur)]
      if view == cur:
        curSymb = cur
        break

    if curSymb == '':
      i += 1
      continue

    lastItem = symbolStack[-1]
    if lastItem[1] == curSymb:
      symbolStack.pop()
      if not len(symbolStack):
        return i
      else:
        i += len(curSymb)
        continue

    if lastItem[2]:
      asLeftPair = None
      for cur in pairs:
        if cur[0] == curSymb:
          asLeftPair = cur
          break

      if asLeftPair:
        symbolStack.append(asLeftPair)

    i += len(curSymb)

  return -1


def remove_empty_lines(text, leading = True, trailing = True):
  splitted = text.split('\n');
  if leading:
    for i, line in enumerate(splitted):
      if re.fullmatch(r'^\s*$', line):
        del splitted[i]
      else:
        break
  if trailing:
    for i, line in enumerate(reversed(splitted)):
      if re.fullmatch(r'^\s*$', line):
        del splitted[len(splitted) - i - 1]
      else:
        break
  return '\n'.join(splitted)


def detect_targets(text):
  pass

if hasattr(args, 'debug') and args.debug == 'test_pairpattern':
  teststrs = [
    ("""def f(a, b, c = d.sort(key = lambda x: x[")"]))""", 22, 45, ('(', ')', True)), 
    (r'\s*((\(\w+)\s*\d+)\s*\)', 3, 17, ('(', ')', True)),
    (remove_empty_lines(textwrap.dedent('''
      y = """
      what's "this"
      """
    ''')), 4, 22, ('"""', '"""', False))
  ]
  for i, test in enumerate(teststrs):
    result = pairpattern(test[0], test[1], test[3])
    if (result == test[2]):
      print('test {}: success, result = {}  {}'.format(i, result, test[0][test[1] : result + len(test[3][1])]))
    else:
      print('test {}: failed, result = {}'.format(i, result))
  exit(0)

resulttext = ''

with open(args.file, encoding = 'utf-8') as inputfile:
  pass