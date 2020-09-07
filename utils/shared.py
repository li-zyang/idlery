import pathlib
import re

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


def find_git_root(path = '.'):
  cur = pathlib.Path(path).resolve()
  while cur != cur.parent:
    for diritem in cur.iterdir():
      if diritem.name == '.git' and diritem.is_dir():
        return str(cur)
    cur = cur.parent


def resolve_root(path, mountpoint):
  return str(pathlib.Path(* (pathlib.Path(mountpoint).parts + pathlib.Path(path).parts[1 : ])).as_posix())


def root_to(path, root):
  if pathlib.Path(path).resolve().joinpath(pathlib.Path(root).resolve()) != pathlib.Path(root).resolve():
    raise TypeError('Cannot root to a path in a different directory tree')
  return str(
    pathlib.Path('/', * pathlib.Path(path).resolve().parts[len(pathlib.Path(root).resolve().parts) : ]).as_posix()
  )

