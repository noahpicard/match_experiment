import math
import csv
import sys
import os
import pprint
import random
import typing
from typing import TypedDict
import round_matching as round_matching


def getStraightPrefs(men_prefs, women_prefs):
  prefs = {}
  for men_email in men_prefs:
    prefs[men_email] = {**men_prefs[men_email], **{men_email2: -1 for men_email2 in men_prefs}}

  for women_email in women_prefs:
    prefs[women_email] = {**women_prefs[women_email], **{women_email2: -1 for women_email2 in women_prefs}}

  print("rel lens",len(men_prefs), len(women_prefs))

  if (len(men_prefs) > len(women_prefs)):
    ## Add no ones as needed
    fake_woman_count = len(men_prefs) - len(women_prefs)
    for i in range(fake_woman_count):
      women_email = "fake_woman_" + str(i)
      prefs[women_email] = {"first": "No one", "last": "!", "email": women_email, **{other_email: 0 for other_email in prefs}}
      for pref in prefs:
        prefs[pref][women_email] = 0
  
  if (len(women_prefs) > len(men_prefs)):
    ## Add no ones as needed
    fake_man_count = len(women_prefs) - len(men_prefs)
    for i in range(fake_man_count):
      men_email = "fake_man_" + str(i)
      prefs[men_email] = {"first": "No one", "last": "!", "email": men_email, **{other_email: 0 for other_email in prefs}}
      for pref in prefs:
        prefs[pref][men_email] = 0
  
  return prefs


def main(men_filepath, women_filepath, round_count):
  import time
  # record start time
  start = time.time()
  men_prefs = round_matching.readHeadingCSV(men_filepath)
  women_prefs = round_matching.readHeadingCSV(women_filepath)
  prefs = getStraightPrefs(men_prefs, women_prefs)

  print("\n\nmen prefs")
  pprint.pprint(men_prefs)

  print("\n\nwomen prefs")
  pprint.pprint(women_prefs)

  print("\n\nprefs")
  pprint.pprint(prefs)

  pairings = round_matching.getMIPPairings(prefs, round_count)

  #pairings = round_matching.getPairings(prefs, round_count)
  # print("pairings", len(pairings))
  # pprint.pprint(pairings)

  # pairings = round_matching.getGSPairings(men_prefs, women_prefs, round_count)
  # print("GS pairings", len(pairings))
  # pprint.pprint(pairings)

  top_pairings = pairings[:round_count]
  random.shuffle(top_pairings)
  print("top pairings", len(top_pairings), [len(round) for round in top_pairings])
  pprint.pprint(top_pairings)

  round_matching.writePairingsCSV(top_pairings, prefs, round_matching.getGlobalFilepath("final_group_pairings.csv"))

  # record end time
  end = time.time()
  
  # print the difference between start 
  # and end time in milli. secs
  print("The time of execution of above program is :",
        (end-start) * 10**3, "ms")

if (__name__ == "__main__"):  
  men_filename = sys.argv[1]
  men_filepath = round_matching.getGlobalFilepath(men_filename)
  women_filename = sys.argv[2]
  women_filepath = round_matching.getGlobalFilepath(women_filename)
  round_count = int(sys.argv[3])
  for index, arg in enumerate(sys.argv):
    print(index, arg)
  main(men_filepath, women_filepath, round_count)
