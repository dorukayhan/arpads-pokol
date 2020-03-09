# Arpad's Pokol

One of the unspoken rules of esports and other competitive games (e or not) is that if you attempt to rank every player by skill with an algorithm that spits out a single number, someone will complain of an "Elo hell" where they're hardstuck at their current rank because of bad teammates or a sudden skill spike in their opponents. Never mind that [the ranking algorithm may look nothing like Elo](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/) and it takes some truly awful matchmaking to get hardstuck at a rank that one doesn't belong to.

Now you too can create your own Elo hells with fire stolen from the very first hell, set alight by Elo himself for USCF. Whether you use this power for a chess tournament like USCF or 2am Super Smash Bros. scrims like me is up to you.

## Installation and usage

1. Get Python 3.8. """"""In return"""""" for having no dependencies, I shall ask you to get on with the times and install the latest Python
2. `git clone https://github.com/dorukayhan/arpads-pokol`
3. `cd arpads-pokol`
4. `./elo.py a-name-for-your-hell` (or `py -3 elo.py a-name-for-your-hell` if you're a Windows peasant like me)
5. Follow the instructions

Once you get a hell (or, more mildly, a pool) going under the name of, say, `example`, it'll be saved in `./example.elog`. Use `example` as the hell/pool name again in later executions to keep using it.