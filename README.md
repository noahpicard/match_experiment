# matcher
Automatic Matcher for Speed Dating!


### How to run round pairings

Run
`python3 straight_round_matching.py [relative path of mens input preferences csv] [relative path of womens input preferences csv] [number of rounds]`

For example:
`python3 straight_round_matching.py straight_round_example/men_round_preferences.csv straight_round_example/women_round_preferences.csv 2`

This should output `final_group_pairings.csv` that match those found in the `straight_round_example` folder

Make sure you follow the same csv format for your men and women input preference csv as the `straight_round_example/men_round_preferences.csv` file.


### How to run final matches

Make sure you have python 3 installed. Then run

`python3 final_matching.py [relative path of input preferences csv] `

For example:

`python3 final_matching.py example/input_preferences.csv`

This should output `final_matches.csv` and `final_no_matches.csv` that match those found in the `example` folder

Make sure you follow the same csv format for your input preference csv as the `example/input_preferences.csv` file.




