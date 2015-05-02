insert into accounts
	(username, email, firstname, lastname, language, active)
	values ("admin", "", "admin", "user", "", 1);
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


--Team 1 - Mona's
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Mona's Athletic Club", "Mona's", 1105, 1, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 1, 1);

insert into player
	(league_num, firstname, lastname, handicap)
	values (06954, "Ray", "De Jesus", 5);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 1, 1);
insert into team_player
	(team_id, player_id)
	values (1,1);
insert into player
	(league_num, firstname, lastname, handicap)
	values (08754, "Jason", "Tenzer", 5);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 2, 1);
insert into team_player
	(team_id, player_id)
	values (1,2);
insert into player
	(league_num, firstname, lastname, handicap)
	values (11480, "Julie", "Sisson", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 3, 1);
insert into team_player
	(team_id, player_id)
	values (1,3);
insert into player
	(league_num, firstname, lastname, handicap)
	values (12292, "Leslie", "Chung", 2);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 4, 1);
insert into team_player
	(team_id, player_id)
	values (1,4);
insert into player
	(league_num, firstname, lastname, handicap)
	values (07648, "Nick", "Herman", 6);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 5, 1);
insert into team_player
	(team_id, player_id)
	values (1,5);
insert into player
	(league_num, firstname, lastname, handicap)
	values (09454, "Genever", "McBain", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 6, 1);
insert into team_player
	(team_id, player_id)
	values (1,6);
insert into player
	(league_num, firstname, lastname, handicap)
	values (11102, "Haydee", "Jimenez", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 7, 1);
insert into team_player
	(team_id, player_id)
	values (1,7);
insert into player
	(league_num, firstname, lastname, handicap)
	values (13026, "Brian", "Daly", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 8, 1);
insert into team_player
	(team_id, player_id)
	values (1,8);


--Team 2 - Double Down
insert into team
	(name, location, league_num, account_id, league_id, division_id)
	values ("Double Down", "Double Down Saloon", 00806, 1, 1, 1);
insert into permissions
	(entity, row_id, account_id)
	values ("Team", 2, 1);

insert into player
	(league_num, firstname, lastname, handicap)
	values (10573, "Jona", "Herbert", 5);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 9, 1);
insert into team_player
	(team_id, player_id)
	values (2,9);
insert into player
	(league_num, firstname, lastname, handicap)
	values (10717, "Patrick", "Dopke", 5);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 10, 1);
insert into team_player
	(team_id, player_id)
	values (2,10);
insert into player
	(league_num, firstname, lastname, handicap)
	values (11757, "Eric", "Kalison", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 11, 1);
insert into team_player
	(team_id, player_id)
	values (2,11);
insert into player
	(league_num, firstname, lastname, handicap)
	values (12255, "Nick", "Mullendore", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 12, 1);
insert into team_player
	(team_id, player_id)
	values (2,12);
insert into player
	(league_num, firstname, lastname, handicap)
	values (12739, "John", "Bahal", 4);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 13, 1);
insert into team_player
	(team_id, player_id)
	values (2,13);
insert into player
	(league_num, firstname, lastname, handicap)
	values (12155, "Mookie", "Rosa", 5);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 14, 1);
insert into team_player
	(team_id, player_id)
	values (2,14);
insert into player
	(league_num, firstname, lastname, handicap)
	values (09907, "Ed", "Reinhardt", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 15, 1);
insert into team_player
	(team_id, player_id)
	values (2,15);
insert into player
	(league_num, firstname, lastname, handicap)
	values (12376, "Andrew", "Whitney", 3);
insert into permissions
	(entity, row_id, account_id)
	values ("Player", 16, 1);
insert into team_player
	(team_id, player_id)
	values (2,16);

