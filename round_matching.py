import math
import csv
import sys
import os
import pprint
import random
import typing
from typing import TypedDict

import mip

import gurobipy as gp

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
  return f'{prefs[email]["first"]} {prefs[email]["last"][0] if len(prefs[email]["last"]) > 0 else ""}'

def check_valid_pair(email, pairing):
  return email in [pairing["email1"], pairing["email2"]]

def get_other_email(email, pairing):
  return pairing["email2"] if email == pairing["email1"] else pairing["email1"]

def get_other_pairing_email(email, round):
  search = [get_other_email(email, pairing) for pairing in round if check_valid_pair(email, pairing)]
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
      pairing_res = [get_other_pairing_email(email, round) for round in top_pairings]
      pairing_res_names = [getDisplayName(pairing_email, prefs) for pairing_email in pairing_res]
      pairing_res_score = [["{:.2f}".format(pairing["comb_score"]) for pairing in round if email in [pairing["email1"], pairing["email2"]]][0] for round in top_pairings]
      matchWriter.writerow([
          prefs[email]["first"],
          prefs[email]["last"],
          prefs[email]["email"],
      ] + pairing_res_names + pairing_res_score)
  print(f'Round pairings written to {outfilepath}')


def get_gale_shapley_pairings(prev_used_pairings, men_pref, women_pref):
    """
    Implementation of the Gale-Shapley algorithm.

    Args:
        men_pref: A dictionary where keys are men and values are their preference lists of women.
        women_pref: A dictionary where keys are women and values are their preference lists of men.

    Returns:
        A dictionary of stable matches where keys are men and values are their matched women.
    """

    unmatched_men = set(men_pref.keys())
    matches = {}

    while unmatched_men:
        man = unmatched_men.pop()
        for woman in men_pref[man]:
            if (man, woman) in prev_used_pairings:
                continue
            if woman not in matches:
                matches[woman] = man
                break
            else:
                current_match = matches[woman]
                if women_pref[woman].index(man) < women_pref[woman].index(current_match):
                    matches[woman] = man
                    unmatched_men.add(current_match)
                    break
    return matches

# Example usage:
men_pref = {
    'm1': ['w1', 'w2', 'w3'],
    'm2': ['w2', 'w3', 'w1'],
    'm3': ['w3', 'w1', 'w2']
}

women_pref = {
    'w1': ['m1', 'm2', 'm3'],
    'w2': ['m2', 'm3', 'm1'],
    'w3': ['m3', 'm1', 'm2']
}

matches = get_gale_shapley_pairings([], men_pref, women_pref)
print(matches)


def getGSPairings(man_prefs, woman_prefs, round_count):
  pairings: list[list[Pairing]] = []
  all_pairing_scores: list[Pairing] = []
  for man_email in man_prefs:
    for woman_email in woman_prefs:
      man_score = man_prefs[man_email][woman_email]
      woman_score = woman_prefs[woman_email][man_email]
      comb_score = get_combined_score(man_score, woman_score)
      all_pairing_scores.append({"email1": man_email, "email2": woman_email, "comb_score": comb_score})

  man_order_pref = {
    man_email: sorted([woman_email for woman_email in woman_prefs], key=lambda woman_email: -man_prefs[man_email][woman_email]) for man_email in man_prefs
  }

  woman_order_pref = {
    woman_email: sorted([man_email for man_email in man_prefs], key=lambda man_email: -woman_prefs[woman_email][man_email]) for woman_email in woman_prefs
  }

  print("all_pairing_scores length -------", len(all_pairing_scores), all_pairing_scores[0], all_pairing_scores[-1])
  print("man_order_pref length -------", len(man_order_pref))
  pprint.pprint(man_order_pref)
  print("woman_order_pref length -------", len(woman_order_pref))
  pprint.pprint(woman_order_pref)

  prev_used_pairings: set[tuple[str, str]] = set()
  for round in range(round_count):
    round_gs_pairings = get_gale_shapley_pairings(prev_used_pairings, man_order_pref, woman_order_pref)

    round_pairings: list[Pairing] = []

    for woman_email, man_email in round_gs_pairings.items():
      man_score = man_prefs[man_email][woman_email]
      woman_score = woman_prefs[woman_email][man_email]
      comb_score = get_combined_score(man_score, woman_score)
      round_pairings.append({"email1": man_email, "email2": woman_email, "comb_score": comb_score})
      prev_used_pairings.add((man_email, woman_email))
    pairings.append(round_pairings)
  return pairings

def getMIPPairingsSingleRound(prefs, all_pairing_scores):

  m = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.GRB)
  prefContstraints = {
     email: [] for email in prefs
  }

  pairing_vars = []
  pairing_scores = []

  for pairing in all_pairing_scores:
    
    email1 = pairing["email1"]
    email2 = pairing["email2"]
    pairing_var = m.add_var(name=f'{email1}___{email2}', var_type=mip.BINARY)

    prefContstraints[email1].append(pairing_var)
    prefContstraints[email2].append(pairing_var)
    pairing_vars.append(pairing_var)
    pairing_scores.append(pairing["comb_score"])

  for email in prefContstraints:
    if prefContstraints[email] == []:
       return []
    # Each attendee is matched exactly once
    m += mip.xsum(prefContstraints[email]) == 1

  # All attendees are matched
  m += mip.xsum(pairing_vars) == len(prefContstraints) // 2

  # Objective is maximise the sum of all pairings
  m.objective = mip.maximize(mip.xsum(pairing_vars[i]*pairing_scores[i] for i in range(len(pairing_vars))))


  m.max_gap = 0.05
  status = m.optimize(max_seconds=300)
  if status == mip.OptimizationStatus.OPTIMAL:
      print('optimal solution cost {} found'.format(m.objective_value))
  elif status == mip.OptimizationStatus.FEASIBLE:
      print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
  elif status == mip.OptimizationStatus.NO_SOLUTION_FOUND:
      print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
  if status == mip.OptimizationStatus.OPTIMAL or status == mip.OptimizationStatus.FEASIBLE:
      print('solution:')
      for v in m.vars:
        if abs(v.x) > 1e-6: # only printing non-zeros
            print('{} : {}'.format(v.name, v.x))
  print("model.num_solutions: ", m.num_solutions)


def getGurobiPairingsSingleRound(prefs, all_pairing_scores):

  m = gp.Model()
  prefContstraints = {
     email: [] for email in prefs
  }

  pairing_vars = []
  pairing_scores = []

  for pairing in all_pairing_scores:
    
    email1 = pairing["email1"]
    email2 = pairing["email2"]
    pairing_var = m.addVar(vtype='B', name=f'{email1}___{email2}')
   

    prefContstraints[email1].append(pairing_var)
    prefContstraints[email2].append(pairing_var)
    pairing_vars.append(pairing_var)
    pairing_scores.append(pairing["comb_score"])

  pprint.pprint(prefContstraints)

  for email in prefContstraints:
    if prefContstraints[email] == []:
       return []
    # Each attendee is matched exactly once
    m.addConstr(gp.quicksum(prefContstraints[email]) == 1)
  # All attendees are matched
  m.addConstr(gp.quicksum(pairing_vars) == len(prefContstraints) // 2)

  # Objective is maximise the sum of all pairings
  m.setObjective(gp.quicksum([pairing_scores[i] * pairing_vars[i] for i in range(len(pairing_vars))]), gp.GRB.MAXIMIZE)

  # Solve it!
  m.optimize()

  print(f"Optimal objective value: {m.objVal}")
  pprint.pprint(m.getVars())

  final_pairings = [all_pairing_scores[index] for index, val in enumerate(pairing_vars) if val.x > 1e-6]

  return final_pairings

def getMIPPairings(prefs, round_count):
  pairings = []
  all_pairing_scores: list[Pairing] = []
  for index, email1 in enumerate(prefs):
    for email2 in list(prefs.keys())[index:]:
      if (email1 == email2):
        continue
      score1 = prefs[email1][email2]
      score2 = prefs[email2][email1]
      if (score1 == -1 or score2 == -1):
        continue
      comb_score = get_combined_score(score1, score2)
      all_pairing_scores.append({"email1": email1, "email2": email2, "comb_score": comb_score})

  #all_pairing_scores.sort(key=lambda pairing: pairing["comb_score"], reverse=True)

  print("all_pairing_scores length -------", len(all_pairing_scores), all_pairing_scores[0], all_pairing_scores[-1])

  for round in range(round_count):

    for threshold in range(1, len(prefs)):

      pref_mins: dict[str, float] = {email: min([val for key, val in prefs[email].items() if key not in ["first", "last", "email"]][:threshold]) for email in prefs}
      likely_pairing_scores = list(filter(lambda pairing: pairing["comb_score"] > pref_mins[pairing["email1"]] and pairing["comb_score"] > pref_mins[pairing["email2"]], all_pairing_scores))

      print("likely_pairing_scores length -------", len(likely_pairing_scores), "for threshold", threshold)

      
      
      round_pairings = getGurobiPairingsSingleRound(prefs, all_pairing_scores)
      print("DONE","round", round, "threshold", threshold)
      if len(round_pairings) != 0:
        pairings.append(round_pairings)
        all_pairing_scores = list(filter(lambda p: not any([pairing["email1"] == p["email1"] and pairing["email2"] == p["email2"] for pairing in round_pairings]), all_pairing_scores))
        print(" temp all_pairing_scores length -------", len(all_pairing_scores), all_pairing_scores[0], all_pairing_scores[-1])
        break
  return pairings
  



def getPairings(prefs, round_count):
  pairings = []
  all_pairing_scores: list[Pairing] = []
  for index, email1 in enumerate(prefs):
    for email2 in list(prefs.keys())[index:]:
      if (email1 == email2):
        continue
      score1 = prefs[email1][email2]
      score2 = prefs[email2][email1]
      if (score1 == -1 or score2 == -1):
        continue
      comb_score = get_combined_score(score1, score2)
      all_pairing_scores.append({"email1": email1, "email2": email2, "comb_score": comb_score})

  #all_pairing_scores.sort(key=lambda pairing: pairing["comb_score"], reverse=True)

  print("all_pairing_scores length -------", len(all_pairing_scores), all_pairing_scores[0], all_pairing_scores[-1])

  for round in range(round_count):

    for threshold in range(1, len(prefs)):

      pref_mins: dict[str, float] = {email: min([val for key, val in prefs[email].items() if key not in ["first", "last", "email"]][:threshold]) for email in prefs}
      likely_pairing_scores = list(filter(lambda pairing: pairing["comb_score"] > pref_mins[pairing["email1"]] and pairing["comb_score"] > pref_mins[pairing["email2"]], all_pairing_scores))

      print("likely_pairing_scores length -------", len(likely_pairing_scores), "for threshold", threshold)

      round_pairings, _ = getHighestScoredRound([], [], prefs, likely_pairing_scores)
      if len(round_pairings) != 0:
        pairings.append(round_pairings)
        all_pairing_scores = list(filter(lambda p: not any([pairing["email1"] == p["email1"] and pairing["email2"] == p["email2"] for pairing in round_pairings]), all_pairing_scores))
        print(" temp all_pairing_scores length -------", len(all_pairing_scores), all_pairing_scores[0], all_pairing_scores[-1])
        break
  return pairings

def check_pairing_reuses_email(pairing, emails_used):
  return pairing["email1"] in emails_used or pairing["email2"] in emails_used


def getHighestScoredRound(used_emails: list[str], pairings: list[Pairing], prefs, all_pairing_scores) -> tuple[list[Pairing], float]:

  # base case
  if len(used_emails) == len(prefs):
    return pairings, 0
  
  possible_pairings: list[Pairing] = [pairing for pairing in all_pairing_scores if not check_pairing_reuses_email(pairing, used_emails)]
  if len(possible_pairings) == 0:
    return [], float('-inf')
  
  final_score = 0
  update_count = 0
  final_round_used: list[Pairing] = []
  for pairing in possible_pairings:
    best_round_used, best_score = getHighestScoredRound(used_emails + [pairing["email1"], pairing["email2"]], pairings + [pairing], prefs, all_pairing_scores)
    best_score = best_score + pairing["comb_score"]
    if best_score > final_score:
      final_score = best_score
      final_round_used = best_round_used
      update_count += 1
      print("updated count", update_count, final_score, final_round_used)

  return final_round_used, final_score

min_float = sys.float_info.min
def get_combined_score(score1, score2):
  return 2 / (1/(score1+min_float) + 1/(score2+min_float))

def main(filepath, round_count):

  import time
  # record start time
  start = time.time()
  
  
  prefs = readHeadingCSV(filepath)
  pairings = getPairings(prefs, round_count)

  top_pairings = pairings[:round_count]
  random.shuffle(top_pairings)
  # print("top pairings", len(top_pairings))
  # pprint.pprint(top_pairings)

  writePairingsCSV(top_pairings, prefs, getGlobalFilepath("final_group_pairings.csv"))

  # record end time
  end = time.time()
  
  # print the difference between start 
  # and end time in milli. secs
  print("The time of execution of above program is :",
        (end-start) * 10**3, "ms")
  

if (__name__ == "__main__"):  
  filename = sys.argv[1]
  filepath = getGlobalFilepath(filename)
  round_count = int(sys.argv[2])
  main(filepath, round_count)
