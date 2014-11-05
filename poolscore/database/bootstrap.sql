insert into accounts
	(username, email, firstname, lastname, language, active, player_ids)
	values ("admin", "", "admin", "user", "", 1, 1);

insert into password
	(password, account_id)
	select "pass", id from accounts where username="admin";

insert into league
	(name, shortname)
	values ("American Pool Players Association", "APA");

insert into division
	(name, league_id)
	values ("East Village", 1);

insert into team
	(name, league_num, locations, account_id, league_id, division_id)
	values ("Pool of Blood", "Josies's", 101, 1, 1, 1);
insert into team
	(name, league_num, account_id, league_id, division_id)
	values ("Mona's Athletic Club", "Mona's", 1105, 1, 1, 1);

insert into player
	(league_num, name, handicap)
	values (1, "Dagwood Bumstead", 6);
insert into player
	(league_num, name, handicap)
	values (1, "Andy Cap", 4);

insert into team_player
	(team_id, player_id)
	values (1,1);
insert into team_player
	(team_id, player_id)
	values (2,2);