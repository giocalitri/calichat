# CALICHAT

Personal exercise to create a chat application that uses websockets.

This project has beed developed using Python 3.6, Flask, Socket-IO, Postgres (but it should work fine with SQLite) and Redis.

I am pretty sure it will not run on Python 2, but [this is irrelevant](https://twitter.com/giocalitri/status/865640292279500801).

## How to run

### With docker (recommended)

Create a `.env` file:
```
cp .env.example .env
```
Then edit the .env file and set `SERVER_BASE_NAME` to your own local url (by default it is `calichat.local`).

Build the containers and run the app
```
docker-compose build
docker-compose up
```

Skip the next section and go to [Use the chat](#use-the-chat)

### Without docker

I am tempted to say "you are on your own".... but let's see if I can help.

To run this code on your local machine you need to have Python 3.6 (but it should work on 3.5 as well). I also suggest to create a virtual environment.

You will also need to run Redis and (optionally) Postgres if you do not want to use SQLite: it might work just fine on MySQL, but I have not tested it.

When your python environment is ready you will need to install the dependencies
```
pip install -U -r requirements.txt
```

Note: if you are running this on a mac, you need to uninstall `uwsgi` and reinstall it with SSL support.
```
brew install openssl
pip uninstall uwsgi
CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv --no-use-wheel
```

Then you need to export few environment variables (change redis and database url to your own).
```
export DEBUG=True
export DATABASE_URL=postgres://postgres@db:5432/postgres
export REDIS_URL=redis://redis:6379/0
export FLASK_APP=calichat/calichat.py
export FLASK_DEBUG=1
export PORT=5000
export SERVER_BASE_NAME=calichat.local
```

Then you should be able to start the service with either
```
flask run --host=0.0.0.0
```
if you want the dev server or
```
uwsgi uwsgi.ini
```
if you want a produnction like server.


### Use the chat
Add an entry to your `/etc/hosts` to resolve `calichat.local` (or your local name) to the IP where the app is running.
Note: if you run docker-machine, the IP is NOT `127.0.0.1`

The chat should then be available at http://calichat.local:5000/

Note: if you are using Docker, http://calichat.local:5001/ should also be available to simulate an environment
with multiple workers using a message queue.


## Missing features and TODOs
* Handle deletion of chat rooms and notify other users of the creations of new rooms
* Put nginx in fron of the uwsgi processes with a load balancer configuration
* Move all the JS and CSS outside the templates.
* Unit tests and linting
* Front end in REACT
