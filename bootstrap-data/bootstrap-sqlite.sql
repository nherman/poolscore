/* default password is "password" */
insert into user (date_created, date_modified, active, username, email, first_name, last_name, password, timezone) values (
    datetime('now'), datetime('now'), 1,
    "admin",
    "",
    "admin",
    "user",
    "pbkdf2:sha1:1000$PaFHk5oX$68e9a3824bf30ab93db4af52bb285831424965e0",
    "US/Eastern");
