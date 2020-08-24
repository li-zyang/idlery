import pathlib
import argparse
from PIL import Image

parser = argparse.ArgumentParser(description = 'Convert an image to webp format')
parser.add_argument(
  '-i', '--input', 
  metavar = 'PATH', 
  help = 'The path to a specific image file',
  action = 'store',
  required = True
)
parser.add_argument(
  '-o', '--output', 
  metavar = 'PATH', 
  help = 'The path of the output file, defaults to the same path with "webp" extension',
  action = 'store'
)
parser.add_argument(
  '-f', '--force-override',
  help = "Don't raise an exception if the output path exists and override it",
  action = 'store_true'
)
parser.add_argument(
  '-q', '--quiet',
  help = "Don't raise an exception if the output path exists or the input path does not exists and just ignore it",
  action = 'store_true'
)
qualityargs = parser.add_mutually_exclusive_group()
qualityargs.add_argument(
  '--quality',
  metavar = 'Q%',
  help = 'The quality of the saving file, defaults to 80%',
  action = 'store',
  default = '80%'
)
qualityargs.add_argument(
  '--lossless',
  help = 'Save the file with lossless quality',
  action = 'store_true'
)

args = parser.parse_args()

inputpath  = pathlib.Path(args.input)
if args.output != None:
  outputpath = pathlib.Path(args.output)
else:
  outputpath = inputpath.with_suffix('.webp')

if not inputpath.exists():
  if not args.quiet:
    print('Cannot find {}')
  exit(2)

if outputpath.exists():
  if not (args.quiet or args.force_override):
    print('File {} already exists. Use --force-override to override it.')
  if args.quiet:
    exit(2)

with Image.open(args.input) as inputimg:
  if args.lossless:
    inputimg.save(outputpath, 'webp', lossless = True)
  else:
    inputimg.save(outputpath, 'webp', quality = ''.join(args.quality.rsplit('%')))