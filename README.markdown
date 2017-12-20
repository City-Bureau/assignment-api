# Assignment API

This is a small Flask app that is used to proxy requests to the Airtable API.

It provides two routes:

`/api/events`, which returns all meetings that a documenter can apply to cover.

`/api/assignments`, where the UI POSTs data to create an assignment.

# Requirements

- Python 3.6
- Airtable API key

To install the project's dependencies, use `pip install -r requirements.txt`.

# Running

To run in debug mode, which reloads the code on each request and is
ideal for local development:

```
$ FLASK_APP=app.py FLASK_DEBUG=1 flask run
```

You can also just run the app directly if you don't want the reloading
behavior:

```
$ python app.py
```

# Deployment

We deploy to a 12-factor PaaS, so any buildpack-based host (Heroku, Dokku,
etc.) ought to work.
