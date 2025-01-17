import math
import csv
import sys
import os
import pprint

def getGlobalFilepath(filename):
  dirname = os.path.dirname(__file__)
  filepath = os.path.join(dirname, filename)
  return filepath

def readPrefCSV(filepath):
  prefCols = {
      "first": 0,
      "last": 1,
      "email": 2,
      "preferences": 3
  }
  prefs = {}
  # first = 0, last = 1, email = 2, emails of preferences = 3

  with open(filepath, newline='') as csvfile:
    matchReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in matchReader:
        prefs[row[prefCols["email"]]] = {
            "first": row[prefCols["first"]],
            "last": row[prefCols["last"]],
            "email": row[prefCols["email"]],
            "preferences": list() if row[prefCols["preferences"]] == "" else row[prefCols["preferences"]].split(",")
        }

  pprint.pprint(prefs)

  return prefs


def writeMatchCSV(matches, prefs, outfilepath):
  with open(outfilepath, "w",newline='') as csvfile:
    matchWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for email in matches:
      matchList = [f'{prefs[matchEmail]["first"]} {prefs[matchEmail]["last"]} ({matchEmail})' for matchEmail in matches[email]]
      matchStr = ""
      print(matchList, len(matchList))
      if len(matchList) == 0:
        continue
      elif len(matchList) == 1:
        matchStr = matchList[0]
      else:
        matchStr = ", ".join(matchList[:-1]) + f' and {matchList[-1]}'
      
      matchWriter.writerow([
          prefs[email]["first"],
          prefs[email]["last"],
          prefs[email]["email"],
          matchStr,
      ])
  print(f'People with matches written to {outfilepath}')

def writeNoMatchCSV(matches, prefs, outfilepath):
  with open(outfilepath, "w",newline='') as csvfile:
    matchWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for email in matches:
      if len(matches[email]) != 0:
        continue
      
      matchWriter.writerow([
          prefs[email]["first"],
          prefs[email]["last"],
          prefs[email]["email"],
      ])
  print(f'People with no matches written to {outfilepath}')

def getMatches(prefs):
  matches = {}
  for email in prefs:
    matches[email] = list(filter(lambda prefEmail: email in prefs[prefEmail]["preferences"], prefs[email]["preferences"]))
  return matches

def main(filepath):
  prefs = readPrefCSV(filepath)
  matches = getMatches(prefs)
  pprint.pprint(matches)
  writeMatchCSV(matches, prefs, getGlobalFilepath("final_matches.csv"))
  writeNoMatchCSV(matches, prefs, getGlobalFilepath("final_no_matches.csv"))


if (__name__ == "__main__"):  
  filename = sys.argv[1]
  filepath = getGlobalFilepath(filename)
  for index, arg in enumerate(sys.argv):
    print(index, arg)
  main(filepath)
