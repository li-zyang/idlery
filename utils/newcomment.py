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
from shared import *

parser = argparse.ArgumentParser(description = 'Comment on a spcific idlery')
parser.add_argument(
  'id',
  metavar = 'ID',
  help = 'The ID of a spcific idlery, starts with a \'#\'',
  action = 'store'
)
parser.add_argument(
  '--user',
  metavar = 'USER',
  help = 'The user who made this comment (the last component of "https://github.com/<user>")',
  action = 'store'
)
parser.add_argument(
  '--file', 
  metavar = 'PATH', 
  help = 'The file containing your idlery',
  action = 'store',
  default = './README.md'
)
parser.add_argument(
  '--self', 
  help = 'Indicate that this comment is made by your self. [user_name] should be set in config.py',
  action = 'store_true'
)
parser.add_argument(
  '-c', '--content', 
  metavar = 'CONTENT', 
  help = 'The comment content, in HTML. Do not open the text editor if this argument is provided.',
  action = 'store'
)

args = parser.parse_args()

gitroot = find_git_root()

if not args.self and not args.user:
  print('error: Reauire user name or --self', file = sys.stderr)
elif args.self:
  args.user = config.user_name

with open(args.file, encoding = 'utf-8') as readmefile:
  readmecontent = readmefile.read()

with open(resolve_root(config.templates["comment"], gitroot), encoding = 'utf-8') as templatefile:
  template = templatefile.read()

itembegin = re.compile(config.itembegin)
itemend   = re.compile(config.itemend)
item_idpattern = re.compile(config.item_idpattern)
commentfillpat = re.compile(config.comment_fillpattern)
commentuserpat = re.compile(config.comment_userpattern)

lines = readmecontent.split('\n')

findingend = False

for i, line in enumerate(lines):
  if not findingend:
    matchedbegin = itembegin.fullmatch(line)
    if not matchedbegin:
      continue
    idleryid = item_idpattern.search(line).group(0)
    if not idleryid == args.id[1 : ]:
      continue
    findingend = True

  else:
    matchedend = itemend.fullmatch(line)
    if not matchedend:
      continue
    findingend = False
    templatelines = template.split('\n')
    for j, tline in enumerate(templatelines):
      matcheduser = commentuserpat.search(tline)
      if not matcheduser:
        continue
      templatelines[j] = commentuserpat.subn(args.user, templatelines[j])[0]
    before = lines[ : i]
    after  = lines[i : ]
    if before[-1].endswith('</blockquote>'):
      before[-1] += templatelines[0]
      templatelines = templatelines[1 : ]
    if args.content:
      for j, tline in enumerate(templatelines):
        if not commentfillpat.fullmatch(tline):
          continue
        templatelines[j] = commentfillpat.sub(args.content, templatelines[j])
        break

    result = before + templatelines + after
    break

with open(args.file, 'w', encoding = 'utf-8') as readmefile:
  readmefile.write('\n'.join(result))

if config.editor_command and not args.content:
  run(config.editor_command.replace('%s', args.file))
elif not config.editor_command:
  print('Done. Open your text editor to edit the comment.')

