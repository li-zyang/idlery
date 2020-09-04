import inspect
import math
import os
import pathlib
import re
import sys
from datetime import datetime
from random import random

import argparse

sys.path.insert(0, str(pathlib.Path(inspect.getsourcefile(lambda:0)).resolve().parent.parent))
# import from parent directory
import config

parser = argparse.ArgumentParser(description = 'Fill out upload infomation automatically')
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

textfillpattern = re.compile(config.textfillpattern)
tf_yearpattern  = re.compile(config.tf_yearpattern)
tf_monthpattern = re.compile(config.tf_monthpattern)
tf_datepattern  = re.compile(config.tf_datepattern)
tf_hourpattern  = re.compile(config.tf_hourpattern)
tf_minpattern   = re.compile(config.tf_minpattern)
tf_idpattern    = re.compile(config.tf_idpattern)

datafillpattern = re.compile(config.datafillpattern)
df_tstmppattern = re.compile(config.df_tstmppattern)
df_idpattern    = re.compile(config.df_idpattern)


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

curid = None

for i, line in enumerate(lines):
  textfillmatch = textfillpattern.fullmatch(line)
  datafillmatch = datafillpattern.fullmatch(line)
  if not textfillmatch and not datafillmatch:
    continue
  if textfillmatch:
    yearmatch  = tf_yearpattern.search(line)
    monthmatch = tf_monthpattern.search(line)
    datematch  = tf_datepattern.search(line)
    hourmatch  = tf_hourpattern.search(line)
    minmatch   = tf_minpattern.search(line)
    idmatch    = tf_idpattern.search(line)
    if not (yearmatch and monthmatch and datematch and hourmatch and minmatch and idmatch):
      continue
    print('> {}: {}'.format(str(i).rjust(4), line[0 : 73]))
    curtime = datetime.now()
    lines[i] = tf_yearpattern.sub(str(curtime.year).rjust(4, '0'), lines[i])
    lines[i] = tf_monthpattern.sub(str(curtime.month).rjust(2, '0'), lines[i])
    lines[i] = tf_datepattern.sub(str(curtime.day).rjust(2, '0'), lines[i])
    lines[i] = tf_hourpattern.sub(str(curtime.hour).rjust(2, '0'), lines[i])
    lines[i] = tf_minpattern.sub(str(curtime.minute).rjust(2, '0'), lines[i])
    if curid:
      lines[i] = tf_idpattern.sub(curid, lines[i])
      curid = None
    else:
      lines[i] = tf_idpattern.sub(genid(), lines[i])
  else:
    tstmpmatch = df_tstmppattern.search(line)
    idmatch    = df_idpattern.search(line)
    if not (tstmpmatch and idmatch):
      continue
    print('> {}: {}'.format(str(i).rjust(4), line[0 : 73]))
    curtime = datetime.now()
    lines[i] = df_tstmppattern.sub(str(curtime.timestamp()), lines[i])
    curid = genid()
    lines[i] = df_idpattern.sub(curid, lines[i])

outputpath = args.alt if args.alt else args.input
with open(outputpath, 'w', encoding = 'utf-8') as outputfile:
  outputfile.write('\n'.join(lines))