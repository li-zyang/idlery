import pathlib
import argparse
from PIL import Image
import re

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
  default = '133x133'
)
parser.add_argument(
  '-l', '--large-box',
  metavar = 'WxH',
  action = 'store',
  default = '200x200'
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

_size__small = args.fill_size.split('x')
destsize__small = int(_size__small[0]), int(_size__small[1])

_size__large = args.large_box.split('x')
boxsize__large  = int(_size__large[0]), int(_size__large[1])

def genthumbnail(item):
  thumbnailpath__small = str(destpath) + '/' + item.with_suffix('.webp').name
  thumbnailpath__large = str(destpath) + '/' + re.sub(r'\.webp$', '_large.webp', item.with_suffix('.webp').name)
  smallthumbnail_exists = pathlib.Path(thumbnailpath__small).exists()
  largethumbnail_exists = pathlib.Path(thumbnailpath__large).exists()
  if not smallthumbnail_exists or not largethumbnail_exists:
    print('Generating thumbnail for {}'.format(str(item)))
    ori = Image.open(str(item))
    orisize = ori.size

  if not smallthumbnail_exists:
    scale = max(destsize__small[0] / orisize[0], destsize__small[1] / orisize[1])
    smallimg = ori.resize((round(orisize[0] * scale), round(orisize[1] * scale)), resample = Image.LANCZOS)
    newsize = smallimg.size
    trimpixels = (newsize[0] - destsize__small[0]) // 2, (newsize[1] - destsize__small[1]) // 2
    smallimg = smallimg.crop((trimpixels[0], trimpixels[1], newsize[0] - trimpixels[0], newsize[1] - trimpixels[1]))
    smallimg.save(thumbnailpath__small)
    smallimg.close()

  if not largethumbnail_exists:
    scale = min(boxsize__large[0] / orisize[0], boxsize__large[1] / orisize[1])
    largeimg = ori.resize((round(orisize[0] * scale), round(orisize[1] * scale)), resample = Image.LANCZOS)
    largeimg.save(thumbnailpath__large)
    largeimg.close()


if sourcepath.is_dir():
  itemiter = sourcepath.iterdir()
else:
  itemiter = [sourcepath]

for item in itemiter:
  if item.suffix.lower() in imageexts:
    genthumbnail(item)