import pathlib
import argparse
from PIL import Image
import re

parser = argparse.ArgumentParser(description = 'Convert covers to webp format')
parser.add_argument(
  '-c', '--cover-dir',
  metavar = 'PATH',
  help = 'Path to the cover HTML directory',
  action = 'store',
  default = './covers/'
)
parser.add_argument(
  '-i', '--image-dir',
  metavar = 'PATH',
  help = 'Path to the cover image directory',
  action = 'store',
  default = './src/'
)
parser.add_argument(
  '--original-ext',
  metavar = '.ext',
  help = 'The original image file extension',
  action = 'store',
  default = '.png'
)
parser.add_argument(
  '-d', '--del-original',
  help = 'Remove the original image',
  action = 'store_true',
  default = False
)
parser.add_argument(
  '--modify-readme',
  help = 'Also modify sources inside readme',
  action = 'store_true',
  default = False
)
parser.add_argument(
  '--quality',
  metavar = 'Q%',
  help = 'The quality of the saving file, defaults to 80%',
  action = 'store',
  default = '80%'
)

args = parser.parse_args()

def find_git_root(path = '.'):
  cur = pathlib.Path(path).resolve()
  while cur != cur.parent:
    for diritem in cur.iterdir():
      if diritem.name == '.git' and diritem.is_dir():
        return str(cur)
    cur = cur.parent


coverdir = pathlib.Path(args.cover_dir)
imagedir = pathlib.Path(args.image_dir)
gitroot  = pathlib.Path(find_git_root())

if args.modify_readme:
  readmepath = pathlib.Path(* gitroot.parts, 'README.md')
  with open(str(readmepath), encoding = 'utf-8') as readmefile:
    readmecontent = readmefile.read()

for item in coverdir.iterdir():
  targetpath = pathlib.Path(* imagedir.parts, item.with_suffix('.webp').name)
  originalpath = pathlib.Path(* imagedir.parts, item.with_suffix(args.original_ext).name)
  if targetpath.exists() or not originalpath.exists():
    continue
  print('Convert share cover {} => {}'.format(str(originalpath), str(targetpath)))
  cur = Image.open(str(originalpath))
  cur.save(str(targetpath), quality = int(args.quality[ : -1]))
  if args.del_original:
    originalpath.unlink()
  if args.modify_readme:
    pattern = re.compile(
      r'(?<=\s)src="src/{}"(?=(\s|>))'.format(
        originalpath.name
        .replace('.', '\\.')
        .replace('(', '\\(')
        .replace(')', '\\)')
        .replace('[', '\\[')
        .replace(']', '\\]'))
    )
    readmecontent, _ = pattern.subn('src="src/{}"'.format(targetpath.name), readmecontent)

if args.modify_readme:
  with open(str(readmepath), 'w', encoding = 'utf-8') as readmefile:
    readmefile.write(readmecontent)
