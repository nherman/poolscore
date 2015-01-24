#!/bin/bash

sqlite3 /tmp/poolscore.db < poolscore/database/schema.sql
sqlite3 /tmp/poolscore.db < poolscore/database/bootstrap.sql
