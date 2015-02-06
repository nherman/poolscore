insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("admin", "", "admin", "user", "", 101);
insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("player1", "", "player", "one", "", 1);
insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("player2", "", "player", "two", "", 1);
insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("empty", "", "empty", "account", "", 1);

insert into password
	(password, account_id)
	values ("pass", 1);
insert into password
	(password, account_id)
	values ("pass", 2);
insert into password
	(password, account_id)
	values ("pass", 3);
insert into password
	(password, account_id)
	values ("pass", 4);

insert into league
	(name, shortname)
	values ("American Pool Players Association", "APA");

insert into region
	(name, shortname, league_id)
	values ("New York - Manhattan", "NYC", 1);

insert into division
	(name, league_id, region_id, ruleset)
	values ("East Village", 1, 1, "APA8BALL");

insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Pool of Blood", "Josies's", 101, 1, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 1, 1);
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Mona's Athletic Club", "Mona's", 1105, 1, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 2, 1);
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Player1 Team", "P1's", 1111, 2, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 3, 2);
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Player2 Team", "P2's", 2222, 3, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 4, 3);
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Parkside", "Parkside", 666, 1, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 5, 1);

insert into player
	(league_num, firstname, lastname, handicap)
	values (1, "Dagwood", "Bumstead", 6);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 1, 1);
insert into player
	(league_num, firstname, lastname, handicap)
	values (2, "Andy", "Cap", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 2, 1);
insert into player
	(league_num, firstname, lastname, handicap)
	values (111, "Player", "One", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 3, 2);
insert into player
	(league_num, firstname, lastname, handicap)
	values (222, "Player", "Two", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 4, 3);
insert into player
	(league_num, firstname, lastname, handicap)
	values (666, "Guy", "Fiere", 2);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 5, 1);
insert into player
	(league_num, firstname, lastname, handicap)
	values (666, "Super", "Man", 2);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 6, 1);

insert into team_player
	(team_id, player_id)
	values (1,1);
insert into team_player
	(team_id, player_id)
	values (2,2);
insert into team_player
	(team_id, player_id)
	values (3,3);
insert into team_player
	(team_id, player_id)
	values (4,4);
insert into team_player
	(team_id, player_id)
	values (5,5);
insert into team_player
	(team_id, player_id)
	values (1,6);
