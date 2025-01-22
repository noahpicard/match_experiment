import math
import csv
import sys
import os
import pprint
import random
import typing
from typing import TypedDict

class Pairing(TypedDict):
    email1: str
    email2: str
    comb_score: float

def getGlobalFilepath(filename):
  dirname = os.path.dirname(__file__)
  filepath = os.path.join(dirname, filename)
  return filepath

def readHeadingCSV(filepath):
  dictRows = {}
  with open(filepath, newline='') as csvfile:
    matchReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    index_to_heading = {}
    heading_to_index = {}
    
    for rowindex, row in enumerate(matchReader):
        if (rowindex == 0):
          for index, heading in enumerate(row):
            index_to_heading[index] = heading
            heading_to_index[heading] = index
          continue
        dictRows[row[heading_to_index["email"]]] = {
            heading: float(row[index]) if not heading in ['first', 'last', 'email'] else row[index] for index, heading in index_to_heading.items()
        }
  return dictRows

def getDisplayName(email, prefs):
  return f'{prefs[email]["first"]} {prefs[email]["last"][0]}'

def check_valid_pair(email, pairing):
  return email in [pairing["email1"], pairing["email2"]]

def get_other_email(email, pairing):
  return pairing["email2"] if email == pairing["email1"] else pairing["email1"]

def get_other_pairing_email(email, round):
  search = [get_other_email(email, pairing) for pairing in round if check_valid_pair(email, pairing)]
  print("\n\nsearch", search, email, round)
  return search[0]

def writePairingsCSV(top_pairings, prefs, outfilepath):
  with open(outfilepath, "w",newline='') as csvfile:
    matchWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    matchWriter.writerow([
          "first",
          "last",
          "email",
      ] + [
        "round " + str(i) for i in range(len(top_pairings))
      ] + [
        "round " + str(i) + " score" for i in range(len(top_pairings))
      ])
    for email in prefs:

      print(top_pairings)
      print(top_pairings)
      pairing_res = [get_other_pairing_email(email, round) for round in top_pairings]
      pairing_res_names = [getDisplayName(pairing_email, prefs) for pairing_email in pairing_res]
      pairing_res_score = [["{:.2f}".format(pairing["comb_score"]) for pairing in round if email in [pairing["email1"], pairing["email2"]]][0] for round in top_pairings]
      print("pairing_res", pairing_res, len(pairing_res))
      matchWriter.writerow([
          prefs[email]["first"],
          prefs[email]["last"],
          prefs[email]["email"],
      ] + pairing_res_names + pairing_res_score)
  print(f'Round pairings written to {outfilepath}')

def getPairings(prefs, round_count):
  pairings = []
  all_pairing_scores: list[Pairing] = []
  for index, email1 in enumerate(prefs):
    for email2 in list(prefs.keys())[index:]:
      if (email1 == email2):
        continue
      score1 = prefs[email1][email2]
      score2 = prefs[email2][email1]
      comb_score = get_combined_score(score1, score2)
      all_pairing_scores.append({"email1": email1, "email2": email2, "comb_score": comb_score})

  prev_used_pairings: list[Pairing] = []
  for round in range(round_count):
    round_pairings, _ = getHighestScoredRound(prev_used_pairings, [], prefs, all_pairing_scores)
    pairings.append(round_pairings)
    prev_used_pairings = prev_used_pairings + round_pairings

  print("\n\npairings:")
  pprint.pprint(pairings)
  return pairings


def check_pairing_prev_used(pairing, used_pairings):
  return any([p["email1"] == pairing["email1"] and p["email2"] == pairing["email2"] for p in used_pairings])

def check_pairing_reuses_email(pairing, emails_used):
  return pairing["email1"] in emails_used or pairing["email2"] in emails_used


def getHighestScoredRound(prev_used_pairings: list[Pairing], used_pairings_for_round: list[Pairing], prefs, all_pairing_scores) -> tuple[list[Pairing], float]:
  emails_used = [email for pairing in used_pairings_for_round for email in [pairing["email1"], pairing["email2"]]]

  if len(used_pairings_for_round) * 2 == len(prefs):
    print("all emails used")
    return used_pairings_for_round, 0
  
  print("\n\nemails_used")
  pprint.pprint(emails_used)
  print("prev_used_pairings")
  pprint.pprint(prev_used_pairings)
  
  possible_pairings: list[Pairing] = [pairing for pairing in all_pairing_scores if not check_pairing_reuses_email(pairing, emails_used) and not check_pairing_prev_used(pairing, prev_used_pairings)]
  print("possible_pairings")
  pprint.pprint(possible_pairings)
  if len(possible_pairings) == 0:
    print("no possible pairings")
    return [], float('-inf')
  
  final_score = 0
  final_round_used: list[Pairing] = []
  for pairing in possible_pairings:
    print("trying pairing", pairing)
    best_round_used, best_score = getHighestScoredRound(prev_used_pairings, used_pairings_for_round + [pairing], prefs, all_pairing_scores)
    best_score = best_score + pairing["comb_score"]
    if best_score > final_score:
      final_score = best_score
      final_round_used = best_round_used

  return final_round_used, final_score

min_float = sys.float_info.min
def get_combined_score(score1, score2):
  return 2 / (1/(score1+min_float) + 1/(score2+min_float))

def main(filepath, round_count):
  prefs = readHeadingCSV(filepath)
  pairings = getPairings(prefs, round_count)
  print("pairings", len(pairings))
  pprint.pprint(pairings)

  top_pairings = pairings[:round_count]
  random.shuffle(top_pairings)
  print("top pairings", len(top_pairings))
  pprint.pprint(top_pairings)

  writePairingsCSV(top_pairings, prefs, getGlobalFilepath("final_group_pairings.csv"))
  

if (__name__ == "__main__"):  
  filename = sys.argv[1]
  filepath = getGlobalFilepath(filename)
  round_count = int(sys.argv[2])
  # for index, arg in enumerate(sys.argv):
  #   print(index, arg)
  main(filepath, round_count)
