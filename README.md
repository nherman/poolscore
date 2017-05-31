app for scoring pool tounaments

#### To run dev server:
./run.py

Dev environment will automatically generate sqlite db in the application root (app.db)

#### Populate DB with test data:
sqlite3 app.db < bootstrap-data/bootstrap-sqlite.sql


#### Install Python packages using `virtualenv` tool

In the step 1 we create a new virtual environment.
```
virtualenv --verbose --python python2.7 ./poolscore-virtenv
```

In the step 2 we activate newly created environment and install python packages using pip tool.
```
cd ./poolscore-virtenv

source ./bin/activate

sudo pip install -r requirements.txt # Requirements file is located in the root of the web project.

deactivate
```

