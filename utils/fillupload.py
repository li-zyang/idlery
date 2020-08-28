import pathlib
import argparse
from datetime import datetime
import re
from random import random
import math
import sys

parser = argparse.ArgumentParser(description = 'Fill up upload dates automatically')
parser.add_argument(
  'input', 
  metavar = 'PATH', 
  help = 'The file to process',
  action = 'store'
)
parser.add_argument(
  '-a', '--alt',
  metavar = 'PATH',
  help = 'Use an alternative path as destination',
  action = 'store'
)
parser.add_argument(
  '-f', '--force-override',
  help = 'Override the existing file. Only required if --alt is specified',
  action = 'store_true'
)

args = parser.parse_args()

tofind = re.compile(r'<td width="\d+" align="right">.*</td>')
yearpattern  = re.compile(r'(?<!(\w|-|:))yyyy(?=-)')
monthpattern = re.compile(r'(?<=-)MM(?=-)')
datepattern  = re.compile(r'(?<=-)DD(?!(\w|-|:))')
hourpattern  = re.compile(r'(?<!(\w|-|:))hh(?=:)')
minpattern   = re.compile(r'(?<=:)mm(?!\w)')
idpattern    = re.compile(r'(?<=#)__id(?!\w)')

def genid():
  charmap = '0123456789abcdefghijklmnopqretuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
  # datetime timestamp -> javascript timestamp: 1598590254.59908 -> 1598590254599
  # floor(t * 100)
  rawid = int(str(math.floor(random() * math.pow(2, 16))) + str(math.floor(datetime.now().timestamp() * 1000)))
  finalid = ''
  while rawid > 1:
    rawid, rem = divmod(rawid, len(charmap))
    finalid += charmap[rem]
  return finalid

if args.alt and pathlib.Path(args.alt).exists() and not args.force_override:
  print('Output path {} has already exists. Please use -f to override it.', file = sys.stderr)
  exit(2)

with open(args.input, 'r', encoding = 'utf-8') as inputfile:
  original = inputfile.read()

lines = original.split('\n')

for i, line in enumerate(lines):
  if not tofind.fullmatch(line):
    continue
  yearmatch  = yearpattern.search(line)
  monthmatch = monthpattern.search(line)
  datematch  = datepattern.search(line)
  hourmatch  = hourpattern.search(line)
  minmatch   = minpattern.search(line)
  idmatch    = idpattern.search(line)
  if not (yearmatch and monthmatch and datematch and hourmatch and minmatch and idmatch):
    continue
  print('> {}: {}'.format(str(i).rjust(4), line[0 : 73]))
  curtime = datetime.now()
  lines[i] = yearpattern.sub(str(curtime.year).rjust(4, '0'), lines[i])
  lines[i] = monthpattern.sub(str(curtime.month).rjust(2, '0'), lines[i])
  lines[i] = datepattern.sub(str(curtime.day).rjust(2, '0'), lines[i])
  lines[i] = hourpattern.sub(str(curtime.hour).rjust(2, '0'), lines[i])
  lines[i] = minpattern.sub(str(curtime.minute).rjust(2, '0'), lines[i])
  lines[i] = idpattern.sub(genid(), lines[i])

outputpath = args.alt if args.alt else args.input
with open(outputpath, 'w', encoding = 'utf-8') as outputfile:
  outputfile.write('\n'.join(lines))