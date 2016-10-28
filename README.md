app for scoring pool tounaments

# To run dev server:
./start_poolscore.sh

# Dev environment will automatically generate sqlite db in the application root
app.db

# Populate DB with test data:
sqlite3 app.db < bootstrap-data/bootstrap-sqlite.sql