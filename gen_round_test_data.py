import math
import csv
import sys
import os
import pprint
import random
import typing
from typing import TypedDict
import random

class Pairing(TypedDict):
    email1: str
    email2: str
    comb_score: float

def getGlobalFilepath(filename):
  dirname = os.path.dirname(__file__)
  filepath = os.path.join(dirname, filename)
  return filepath

def writeCSV(man_filepath, woman_filepath, man_size, woman_size):

  man_data = [
    ["first", "last", "email", *["woman" + str(i) + "@gmail.com" for i in range(woman_size)]],
    *[["man" + str(j), "last", "man" + str(j) + "@gmail.com", *[random.randint(1, 5) for i in range(woman_size)]] for j in range(man_size)]
  ]
  woman_data = [
    ["first", "last", "email", *["man" + str(i) + "@gmail.com" for i in range(man_size)]],
    *[["woman" + str(j), "last", "woman" + str(j) + "@gmail.com", *[random.randint(1, 5) for i in range(man_size)]] for j in range(woman_size)]
  ]

  with open(man_filepath, "w",newline='') as csvfile:
    matchWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in man_data:
      matchWriter.writerow(row)

  with open(woman_filepath, "w",newline='') as csvfile:
    matchWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in woman_data:
      matchWriter.writerow(row)
  print(f'Preferences written to {man_filepath} and {woman_filepath}')

def main(man_filepath, woman_filepath, man_size, woman_size):
  writeCSV(man_filepath, woman_filepath, man_size, woman_size)
  

if (__name__ == "__main__"):  
  man_filename = sys.argv[1]
  man_filepath = getGlobalFilepath(man_filename)
  woman_filename = sys.argv[2]
  woman_filepath = getGlobalFilepath(woman_filename)
  man_size = int(sys.argv[3])
  woman_size = int(sys.argv[4])
  # for index, arg in enumerate(sys.argv):
  #   print(index, arg)
  main(man_filepath, woman_filepath, man_size, woman_size)
