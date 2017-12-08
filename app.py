import os
from os import environ, path

from flask import Flask, jsonify
from flask_cors import CORS
from airtable import Airtable

if environ.get('ENV') != 'production':
    from dotenv import load_dotenv
    dotenv_path = path.join(path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

AIRTABLE_APP = environ['AIRTABLE_APP']
AIRTABLE_API_KEY = environ['AIRTABLE_API_KEY']

app = Flask(__name__)
CORS(app)

@app.route('/api/events')
def events():
    events_table = Airtable(AIRTABLE_APP, 'Meetings', api_key=AIRTABLE_API_KEY)

    events = events_table.search('assignment_status', 'Open Assignment', fields=['id', 'assignment_status', 'name', 'agency_name', 'classification', 'description', 'start_time', 'end_time', 'location_name', 'status'], sort="start_time")

    resp = jsonify(events)
    return resp

if __name__ == "__main__":
	app.run()
