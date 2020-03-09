#!/usr/bin/env python3

import sys
import os
import re
from pathlib import Path
from datetime import datetime # datetime.utcnow().isoformat() returns something resembling an ISO 8601 timestamp
from statistics import fmean, pstdev

# This app is a dirty hack meant for late-night Smash scrims
# It doesn't need best-practice coding
__pool = {}
__scaling = 50
__distribution_height = 9
__distribution_width = 400
__initial_rating = 1500
__first_match = None

def main():
	if len(sys.argv) == 1: # No pool name provided
		if os.name == "nt": # Running on Windows
			print(f"Usage: py -3 {sys.argv[0]} [pool name]") # When will Windows support shebang lines?
		else: # Assume *nix
			print(f"Usage: ./{sys.argv[0]} [pool name]") # Also what if the script isn't named elo.py for some reason?
		print("If [pool name].elog exists in the current directory, match history will be read from it")
		print("Otherwise it'll be created")
		sys.exit(1)

	pool_name = sys.argv[1]
	match_history = Path(f"{pool_name}.elog")
	top_x_filter = re.compile(r"top \d+")
	if match_history.is_dir():
		print(f"./{pool_name}.elog is a folder, so {pool_name} can't be used as a pool name")
		sys.exit(2)
	elif match_history.is_file():
		read_match_history(match_history)
	else:
		new_pool(match_history)

	with match_history.open("a", encoding="utf-8", newline="\n") as match_log:
		try:
			while True:
				command_id = input("Enter a command (\"commands\" lists available commands): ")
				if command_id == "commands":
					display_commands()
				elif command_id == "new match":
					enter_match(match_log)
				elif command_id == "stats":
					display_pool_stats()
				elif top_x_filter.fullmatch(command_id): # command_id == "top X" where X is an integer
					display_leaderboard(int(command_id.split()[1]))
				else:
					print("Unknown or mistyped command. ", end='')
		except KeyboardInterrupt:
			sys.exit()

def read_match_history(filename):
	global __scaling
	global __distribution_height
	global __distribution_width
	global __initial_rating
	global __first_match

	print(f"./{filename.name} found, reading match history...", end='')
	# Format:
	# scaling {__scaling}
	# distheight {__distribution_height}
	# distwidth {__distribution_width}
	# beginning {__initial_rating}
	# zero or more of:
	# {UTC timestamp} {player A} {player B} {player A's score}
	with filename.open(mode="r", encoding="utf-8", newline="\n") as match_history:
		__scaling = int(match_history.readline().split()[1])
		__distribution_height = int(match_history.readline().split()[1])
		__distribution_width = int(match_history.readline().split()[1])
		__initial_rating = int(match_history.readline().split()[1])
		# Now the match history begins
		# The UTC timestamp contains no spaces, so A is .split()[1] and B is .split()[2]
		for match in match_history: # Hopefully this won't rewind the file
			tokens = match.split()
			if __first_match is None: # Save the first match's time for display_pool_stats
				__first_match = datetime.strptime(tokens[0], "%Y-%m-%dT%H:%M:%S.%f")
			rate(tokens[1], tokens[2], float(tokens[3]))
	print("done")
	print() # Separate boot-time blurb from actual use

def new_pool(filename):
	global __scaling
	global __distribution_height
	global __distribution_width
	global __initial_rating

	print(f"./{filename.name} not found. A wizard will now activate for creating a new pool.")
	print()
	__initial_rating = int(input("What should be the initial rating of new players? (1500 recommended just because) "))
	__scaling = int(input("What should be the maximum rating gain possible from a single win? (50 recommended just because) "))
	print("The next two parameters require some explanation.")
	print("Consider two hardstuck players, A and B, with ratings rA and rB such that rA > rB (i.e. A is better than B).")
	print("B's expected \"score\" against A on a scale of 0 to 1 is given by eB=1/(1+H^((rA-rB)/W)), where H and W are our tunable parameters.")
	print("If rA-rB=W, then eB=1/(1+H).")
	print("H=9 has the nice property that if rA-rB=W/2, eB=1/4.")
	__distribution_height = int(input("With all that in mind, H=? (9 strongly recommended) "))
	__distribution_width = int(input("And W=? (FIDE and USCF seem to use 400) "))
	with filename.open(mode="w", encoding="utf-8", newline="\n") as match_history:
		match_history.write(f"scaling {__scaling}\n")
		match_history.write(f"distheight {__distribution_height}\n")
		match_history.write(f"distwidth {__distribution_width}\n")
		match_history.write(f"beginning {__initial_rating}\n")
	print(f"Pool initialized in ./{filename.name}")
	print() # Separate boot-time blurb from actual use

def rate(player_a, player_b, a_score):
	global __scaling
	global __distribution_height
	global __distribution_width
	global __initial_rating
	global __pool

	# B "loses" as much rating as A "gains".
	# This means we can calculate A's rating change and negate it to get B's rating change
	rating_a = __pool.setdefault(player_a, __initial_rating) # Also initializes new player_a
	rating_b = __pool.setdefault(player_b, __initial_rating)
	a_expectation = 1/(1+(__distribution_height**((rating_b-rating_a)/__distribution_width)))
	a_change = int(__scaling * (a_score - a_expectation))
	__pool[player_a] += a_change
	__pool[player_b] -= a_change
	return a_change

def display_commands():
	print('"commands" displays this list')
	print('"new match" enters a new 1v1 to the match history and updates ratings accordingly')
	print('"stats" displays this pool\'s statistics and properties (number of players, scaling factor etc.)')
	print('"top X" displays the X highest-rated players (X=0 displays everyone)')
	print('Ctrl-C exits the program')

def enter_match(match_log):
	global __pool
	global __first_match

	player_a = input("Who is player A? ")
	player_b = input("Who is player B? ")
	old_rating_a = __pool.setdefault(player_a, __initial_rating)
	old_rating_b = __pool.setdefault(player_b, __initial_rating)
	a_score = float(input("On a scale from 0 to 1, what is A's score?\nUsually a win is 1, a loss is 0, and a draw is 0.5. "))
	match_time = datetime.utcnow()
	if __first_match is None:
		__first_match = match_time
	match_log.write(f"{match_time.isoformat()} {player_a} {player_b} {a_score}\n")
	match_log.flush() # To hell with buffering, no sane person will pipe batches of matches into enter_match
	a_change = rate(player_a, player_b, a_score)
	print(f"{player_a} is now rated {__pool[player_a]} ({a_change:{'+' if a_change else ''}} from {old_rating_a})")
	print(f"{player_b} is now rated {__pool[player_b]} ({-a_change:{'+' if -a_change else ''}} from {old_rating_b})")

def display_pool_stats():
	global __scaling
	global __distribution_height
	global __distribution_width
	global __initial_rating
	global __pool
	global __first_match

	print(f"Player count: {len(__pool)}")
	if __first_match is None:
		print("Player/rating statistics unavailable due to lack of players and matches")
	else:
		best_player = max(__pool, key=__pool.get)
		worst_player = min(__pool, key=__pool.get)
		now = datetime.utcnow()
		print(f"First match was done {'today' if (now-__first_match).days == 0 else f'{(now-__first_match).days} day(s) ago'}")
		print(f"Best player: {best_player} (rated {__pool[best_player]})")
		print(f"\"Worst\" player: {worst_player} (rated {__pool[worst_player]})")
		print(f"Average rating: {fmean(__pool.values()):.2f} (σ={pstdev(__pool.values()):.4f})")
	print(f"Initial rating: {__initial_rating}")
	print(f"Max rating change per match: {__scaling}")
	print(f"H: {__distribution_height}")
	print(f"W: {__distribution_width}")

def display_leaderboard(length):
	global __pool

	position = 1
	for player in sorted(__pool, key=__pool.get, reverse=True)[:length]:
		print(f"{position}. {player} (rated {__pool[player]})")
		position += 1

if __name__ == "__main__":
	print(os.getpid())
	main()