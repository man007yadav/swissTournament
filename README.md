# udacity_swissTournament

This project provides a way to keep track of players, matches, and tournaments played in a variation of the [Swiss tournament format](https://en.wikipedia.org/wiki/Swiss-system_tournament). Here, any given match can result in a win, loss, or tie, worth 3, 0, or 1 points for the players, respectively. Since the number of rounds conventionally played in a Swiss tournament to determine the winner is not necessarily the same as the minimum number of rounds to find a "winner", the pairings function does not return information about tournament winners. Players can be tracked across distinct tournaments, all stored in a single Postgres database. Since there are several opportunities for user inputs to make their way directly into SQL statements, all inputs are checked for "cleanliness" before usage.

### Requirements

Python 2.7:
 -`bleach`
 -`psycopg2`

Postgres CLI >= 9.2 (to use parameter names in SQL functions)

### Installation

You will get the best compatibility using the Udacity-provided VM with Virtualbox/Vagrant. You can fork/clone this from [this GitHub repo](https://github.com/udacity/fullstack-nanodegree-vm). Alternatively, ensure your system has the above listed requirements.

If using the Udacity VM, replace the provided /tournament/ directory when you clone this repository: `git clone git@github.com:prlakhani/udacity_swissTournament.git tournament` (if you are already in the vagrant directory from cloning the Udacity repo). Otherwise, clone this repository normally.

### Database Setup

Navigate to the cloned tournament repository in a shell. Make sure you have a psql user with database creation permissions set up. Make sure you don't have any important database named "tournament" set up, and then run the following command in the psql CLI: `psql -f tournament.sql`. This sets up and connects to a fresh "tournament" database with the schema laid out in the file tournament.sql. 

### Usage

You will first need to add a tournament using `addTournament()`. Keep track of the printed or returned tournament_id number.

You can then register players into the database with `registerPlayer(name)`, providing the name of player. Again, the database IDs of the players are both printed and returned from this function, and should be kept track of for the next step: registering players in a tournament. This is done using the `registerPlayerInTournament` function, which takes the registered player_id and tournament_id as arguments.

From this point, you can run your tournament as expected. At any point, you can check the standings with `playerStandings(tournament_id)` and get a list of tuples consisting of the player_id, player's name, current tournament score, and number of matches played. You can report matches played using `reportMatch`. This function takes the tournament_id, winner_id as either the player_id of the winner or 0 if the match resulted in a tie, and then additional arguments which are the full set of all players participating in the match. This is designed to make changing the setup for matches with a different number of players easier (the only function that would need updating would be `swissPairings`, as well as to facilitate updating the scores of all players in case of a tie. Note that all players, including the winner if there was one, should be listed here. The `swissPairings(tournament_id)` function should be run at the start of a new round to determine which players should play one another to get closer to the goal of determining clear rankings in the tournament. The returned list consists of tuples with the IDs and names of players matched up for the next round. 

### Testing

A testing suite is provided (slightly modified and expanded on from the default Udacity set) in tournament_test.py. These can be run using `python tournament_test.py`