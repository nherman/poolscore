/* default password is "password" */
insert into user (date_created, date_modified, active, username, email, first_name, last_name, password, timezone) values (
    datetime('now'), datetime('now'), 1,
    "admin",
    "",
    "admin",
    "user",
    "pbkdf2:sha1:1000$PaFHk5oX$68e9a3824bf30ab93db4af52bb285831424965e0",
    "US/Eastern");
insert into entityuser (entity, row_id, user_id) values ("User",1,1);

insert into user (date_created, date_modified, active, username, email, first_name, last_name, password, timezone) values (
    datetime('now'), datetime('now'), 1,
    "nick",
    "nherman@gmail.com",
    "nick",
    "herman",
    "pbkdf2:sha1:1000$PaFHk5oX$68e9a3824bf30ab93db4af52bb285831424965e0",
    "US/Eastern");
insert into entityuser (entity, row_id, user_id) values ("User",2,1);
insert into entityuser (entity, row_id, user_id) values ("User",2,2);

INSERT INTO "player" VALUES(1,'2015-09-30 20:35:15','2015-09-30 20:35:15',1,'Nick','Herman','001',6);
INSERT INTO "player" VALUES(2,'2015-09-30 20:35:28','2015-09-30 20:37:09',1,'Ray','De Jesus','002',5);
INSERT INTO "player" VALUES(3,'2015-09-30 20:35:46','2015-09-30 20:35:46',1,'Chowder','Head','003',3);
INSERT INTO "player" VALUES(4,'2015-09-30 20:36:01','2015-09-30 20:36:01',1,'Jack','Herman','004',2);
INSERT INTO "player" VALUES(5,'2015-09-30 20:36:13','2015-09-30 20:36:13',1,'Sandy','Cofax','005',4);
INSERT INTO "player" VALUES(6,'2015-09-30 20:36:36','2015-09-30 20:36:36',1,'Silent','Killer','006',4);
INSERT INTO "player" VALUES(7,'2015-09-30 20:36:47','2015-09-30 20:36:47',1,'Vicious','Cycle','007',6);
INSERT INTO "player" VALUES(8,'2015-09-30 20:37:04','2015-09-30 20:37:04',1,'Prime','Meat','008',2);
INSERT INTO "player" VALUES(9,'2015-09-30 20:37:26','2015-09-30 20:37:26',1,'Minced','Bread','009',6);
INSERT INTO "player" VALUES(10,'2015-09-30 20:37:45','2015-09-30 20:37:45',1,'Three','Breasted Woman','010',7);
INSERT INTO "player" VALUES(11,'2015-09-30 20:38:00','2015-09-30 20:38:00',1,'Say','Your Prayers','011',4);
INSERT INTO "player" VALUES(12,'2015-09-30 20:38:24','2015-09-30 20:38:24',1,'San','Griah','012',3);
INSERT INTO "player" VALUES(13,'2015-09-30 20:38:42','2015-09-30 20:38:42',1,'Thousand','Island','013',5);
INSERT INTO "player" VALUES(14,'2015-09-30 20:38:57','2015-09-30 20:38:57',1,'Wife','Bonus','014',3);
INSERT INTO "player" VALUES(15,'2015-09-30 20:39:12','2015-09-30 20:39:12',1,'Bradley','Whitford','015',2);

INSERT INTO "team" VALUES(1,'2015-09-30 20:34:27','2015-09-30 20:34:27',1,'nick''s Team','100','Nick''s Bar',2);
INSERT INTO "team" VALUES(2,'2015-09-30 20:34:58','2015-09-30 20:34:58',1,'Eight Ball Team','200','Eight Ball Lounge',2);

INSERT INTO "entityuser" VALUES('Team',1,2);
INSERT INTO "entityuser" VALUES('Team',2,2);
INSERT INTO "entityuser" VALUES('Player',1,2);
INSERT INTO "entityuser" VALUES('Player',2,2);
INSERT INTO "entityuser" VALUES('Player',3,2);
INSERT INTO "entityuser" VALUES('Player',4,2);
INSERT INTO "entityuser" VALUES('Player',5,2);
INSERT INTO "entityuser" VALUES('Player',6,2);
INSERT INTO "entityuser" VALUES('Player',7,2);
INSERT INTO "entityuser" VALUES('Player',8,2);
INSERT INTO "entityuser" VALUES('Player',9,2);
INSERT INTO "entityuser" VALUES('Player',10,2);
INSERT INTO "entityuser" VALUES('Player',11,2);
INSERT INTO "entityuser" VALUES('Player',12,2);
INSERT INTO "entityuser" VALUES('Player',13,2);
INSERT INTO "entityuser" VALUES('Player',14,2);
INSERT INTO "entityuser" VALUES('Player',15,2);

INSERT INTO "team_player" VALUES(1,1);
INSERT INTO "team_player" VALUES(2,1);
INSERT INTO "team_player" VALUES(1,3);
INSERT INTO "team_player" VALUES(1,4);
INSERT INTO "team_player" VALUES(1,5);
INSERT INTO "team_player" VALUES(1,6);
INSERT INTO "team_player" VALUES(1,7);
INSERT INTO "team_player" VALUES(1,8);
INSERT INTO "team_player" VALUES(1,2);
INSERT INTO "team_player" VALUES(2,9);
INSERT INTO "team_player" VALUES(2,10);
INSERT INTO "team_player" VALUES(2,11);
INSERT INTO "team_player" VALUES(2,12);
INSERT INTO "team_player" VALUES(2,13);
INSERT INTO "team_player" VALUES(2,14);
INSERT INTO "team_player" VALUES(2,15);
