import pathlib
import argparse
from tqdm import tqdm
from PIL import Image

parser = argparse.ArgumentParser(description = 'Generate thumbnails')
parser.add_argument(
  '-s', '--source', 
  metavar = 'PATH', 
  help = 'the source directory of images or a specific image file',
  action = 'store',
  default = './src'
)
parser.add_argument(
  '-d', '--dest', 
  metavar = 'PATH', 
  help = 'the destination directory of thumbnails',
  action = 'store',
  default = './thumbnail'
)
parser.add_argument(
  '-f', '--fill-size',
  metavar = 'WxH',
  help = 'the size of container rectangle',
  action = 'store',
  default = '100x100'
)
parser.add_argument(
  '--debug', 
  metavar = 'FUNCTION', 
  help = 'run specific debug program',
  action = 'store'
)

args = parser.parse_args()

sourcepath = pathlib.Path(args.source)
destpath = pathlib.Path(args.dest)

imageexts = ['.jpeg', '.jpg', '.png', '.gif', '.webp', '.tiff', '.bmp']

if not sourcepath.exists():
  print('Source path {} does not exists.'.fromat(str(sourcepath.resolve())))
  exit()

if not destpath.exists():
  destpath.mkdir()

_size = args.fill_size.split('x')
destsize = int(_size[0]), int(_size[1])

def genthumbnail(item):
  # thumbnailpath = str(item).rreplace(item.suffix, '.webp')
  thumbnailpath = str(destpath) + '/' + item.with_suffix('.webp').name
  if pathlib.Path(thumbnailpath).exists():
    return
  cur = Image.open(str(item))
  orisize = cur.size
  if orisize[0] <= orisize[1]:
    scale = destsize[0] / orisize[0]
  else:
    scale = destsize[1] / orisize[1]
  cur = cur.resize((int(orisize[0] * scale), int(orisize[1] * scale)), resample = Image.LANCZOS)
  newsize = cur.size
  trimpixels = (newsize[0] - destsize[0]) // 2, (newsize[1] - destsize[1]) // 2
  cur = cur.crop((trimpixels[0], trimpixels[1], newsize[0] - trimpixels[0], newsize[1] - trimpixels[1]))
  cur.save(thumbnailpath)
  cur.close()

if sourcepath.is_dir():
  for item in tqdm(sourcepath.iterdir()):
    if item.suffix.lower() in imageexts:
      genthumbnail(item)
else:
  for item in tqdm([sourcepath]):
    if item.suffix.lower() in imageexts:
      genthumbnail(item)