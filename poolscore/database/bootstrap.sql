insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("admin", "", "admin", "user", "", 101);
insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("player1", "", "player", "one", "", 1);
insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("player2", "", "player", "two", "", 1);

insert into password
	(password, account_id)
	select "pass", id from accounts where username="admin";

insert into league
	(name, shortname)
	values ("American Pool Players Association", "APA");

insert into region
	(name, shortname, league_id)
	values ("New York - Manhattan", "NYC", 1);

insert into division
	(name, league_id, region_id, ruleset)
	values ("East Village", 1, 1, "8ball_classic");

insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Pool of Blood", "Josies's", 101, 1, 1, 1);
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Mona's Athletic Club", "Mona's", 1105, 1, 1, 1);

insert into player
	(league_num, firstname, lastname, handicap)
	values (1, "Dagwood", "Bumstead", 6);
insert into player
	(league_num, firstname, lastname, handicap)
	values (2, "Andy", "Cap", 4);

insert into team_player
	(team_id, player_id)
	values (1,1);
insert into team_player
	(team_id, player_id)
	values (2,2);