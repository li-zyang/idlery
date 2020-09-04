import inspect
import pathlib
import re
import sys
from datetime import datetime
from subprocess import run

import argparse

sys.path.insert(0, str(pathlib.Path(inspect.getsourcefile(lambda:0)).resolve().parent.parent))
# import from parent directory
import config

parser = argparse.ArgumentParser(description = 'Create a new idlery')
parser.add_argument(
  'type',
  metavar = 'TYPE',
  help = 'The idlery type. Corresponding template should be set in config.py.',
  action = 'store'
)
parser.add_argument(
  '--file', 
  metavar = 'PATH', 
  help = 'The file containing your idlery',
  action = 'store',
  default = './README.md'
)

args = parser.parse_args()

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

gitroot = find_git_root()

with open(args.file, encoding = 'utf-8') as readmefile:
  readmecontent = readmefile.read()

lines = readmecontent.split('\n')

beginlno = -1

for i, line in enumerate(lines):
  if line == config.idlerybegin:
    beginlno = i

if beginlno == -1:
  print('Cannot find begin line', file = sys.stderr)
  exit(1)

if not args.type in config.templates:
  print('Undefined idlery type: {}'.format(args.type))
  exit(1)

templatepath = pathlib.Path(resolve_root(config.templates[args.type], gitroot))

if not templatepath.exists():
  print('Template does not exists: {}'.format(str(templatepath)))

with open(str(templatepath), encoding = 'utf-8') as templatefile:
  template = templatefile.read()

templatelines = template.split('\n')

result = lines[ : beginlno + 1] 
result += [''] * config.empty_line_before
result += templatelines
result += [''] * config.empty_line_after
result += lines[beginlno + 1 : ]

with open(args.file, 'w', encoding = 'utf-8') as readmefile:
  readmefile.write('\n'.join(result))

if 'editor_command' in dir(config):
  run(config.editor_command.replace('%s', args.file), shell = True, check = True)
else:
  print('Done. Open your text editor to edit the top-most item.')
