import pathlib
import argparse
from PIL import Image
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser(description = 'Remove EXIF of images')
parser.add_argument(
  '-s', '--source',
  metavar = 'PATH',
  help = 'The source path to a directory a specific image file',
  action = 'store',
  required = True
)
parser.add_argument(
  '-d', '--data-file',
  metavar = 'PATH',
  help = 'The file which stores the record',
  default = './data/exif-removed.json'
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

datafile = pathlib.Path(args.data_file)
# { path (relative to repo root), lastmodified (timestamp) }
if not (datafile.exists()):
  datafile.parent.mkdir(parents = True, exist_ok = True)
  datafile.touch()
  recorddata = []
else:
  with open(str(datafile), encoding = 'utf-8') as df:
    recorddata = json.load(df)

if pathlib.Path(args.source).is_dir():
  items = pathlib.Path(args.source).iterdir()
else:
  items = [pathlib.Path(args.source)]

cares = {'.jpeg', '.jpg', '.png', '.gif'}

for item in items:
  if item.is_dir() or not item.suffix in cares:
    continue
  removed = False
  for rec in recorddata:
    samefile = pathlib.Path(resolve_root(rec['path'], gitroot)) == item.resolve()
    samedate = rec['lastmodified'] == os.path.getmtime(str(item))
    if samefile and samedate:
      removed = True
  if removed:
    continue
  cur = Image.open(str(item))
  if 'exif' in cur.info:
    print('Removing EXIF of {}'.format(root_to(str(item), gitroot)))
    if item.suffix == '.jpeg' or item.suffix == '.jpg':
      cur.save(str(item), quality = "keep")
    elif item.suffix == '.png' or item.suffix == '.gif':
      cur.save(str(item))
  cur.close()
  recorddata.append({
    'path': root_to(str(item), gitroot),
    'lastmodified': os.path.getmtime(str(item))
  })

with open(str(datafile), 'w', encoding = 'utf-8') as df:
  json.dump(recorddata, df)