drop table if exists accounts;
create table accounts (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	username text not null,
	email text,
	firstname text,
	lastname text,
	language text,
	active numeric not null
);

drop table if exists password;
create table password (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	password text,
	account_id integer,
	foreign key(account_id) references accounts(id)
);

drop table if exists permissions;
create table permissions (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	entity text not null,
	row_id integer not null,
	account_id integer not null,
	foreign key(account_id) references accounts(id)
);
CREATE INDEX row_id_index ON permissions (row_id);

drop table if exists league;
create table league (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	name text not null,
	shortname text,
	ruleset text
);

drop table if exists region;
create table region (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	name text not null,
	ruleset text,
	shortname text,
	league_id integer not null,
	foreign key(league_id) references league(id)
);

drop table if exists division;
create table division (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	name text not null,
	ruleset text,
	league_id integer not null,
	region_id integer,
	foreign key(league_id) references league(id),
	foreign key(region_id) references region(id)
);

drop table if exists schedule;
create table schedule (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	name text,
	division_id integer,
	date datetime not null,
	home_team_id integer not null,
	away_team_id integer not null,
	foreign key(division_id) references division(id)
);

drop table if exists team;
create table team (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	name text not null,
	location text,
	account_id integer not null,
	league_num integer,
	league_id integer,
	division_id integer,
	foreign key(account_id) references accounts(id),
	foreign key(league_id) references league(id),
	foreign key(division_id) references division(id)
);

drop table if exists player;
create table player (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	league_num integer not null,
	firstname text,
	lastname text,
	handicap integer not null	
);

drop table if exists team_player;
create table team_player (
	id integer primary key autoincrement,
	team_id integer not null,
	player_id integer not null,
	foreign key(team_id) references team(id),
	foreign key(player_id) references player(id)
);

drop table if exists tourney;
create table tourney (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	date datetime not null,
	home_team_id integer not null,
	away_team_id integer not null,
	ruleset text not null,
	scoring_method text not null,
	winner integer,
	home_matches integer,
	away_matches integer,
	in_progress boolean,
	locked boolean,
	data text,
	foreign key(home_team_id) references team(id),
	foreign key(away_team_id) references team(id)
);

drop table if exists match;
create table match (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	tourney_id integer not null,
	home_player_ids text not null,
	away_player_ids text not null,
	home_games integer,
	away_games integer,
	winner integer,
	in_progress boolean,
	locked boolean,
	data text,
	foreign key(tourney_id) references tourney(id)
);

drop table if exists game;
create table game (
	id integer primary key autoincrement,
	date_created datetime default current_timestamp not null,
	date_modified datetime default current_timestamp not null,
	match_id integer not null,
	breaker integer,
	innings integer,
	win_type text,
	loss_type text,
	winner integer,
	in_progress boolean,
	locked boolean,
	data text,
	foreign key(match_id) references match(id)
);

