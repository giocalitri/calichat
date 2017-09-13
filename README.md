# CALICHAT

Personal exercise to create a chat appication that uses sockets.

## How to run
This project has beed developed using Python 3.6 and Flask.

I have not had the possibility to move it to a docker environment yet, so to run this code you need to have Python 3.6 (but it should work on 3.5 as well). I also suggest to create a virtual environment.

I am pretty sure it will not run on Python 2.7, but [this is irrelevant](https://twitter.com/giocalitri/status/865640292279500801).

When your python environment is ready you will need to install the dependencies
```
pip install -U -r requirements.txt
```
And simply start the test web server
```
export FLASK_APP=calichat/calichat.py
flask run --host=0.0.0.0
```

## Missing features and TODOs

* Move all the JS and CSS outside the templates.
* Unit tests: I did not write any, but this should be priority #1 in a future iteration of the project
* Docker environment so the code can run with (almost) production like settings

