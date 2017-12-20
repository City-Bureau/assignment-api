from sys import stdout
from os import environ, path

from flask import Flask, jsonify, request
from flask_cors import CORS
from airtable import Airtable
from requests import HTTPError

ENV = environ.get('ENV')
if ENV != 'production':
    from dotenv import load_dotenv
    dotenv_path = path.join(path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

AIRTABLE_APP = environ['AIRTABLE_APP']
AIRTABLE_API_KEY = environ['AIRTABLE_API_KEY']
EVENTS_TABLE = environ['EVENTS_TABLE']
APPLICATIONS_TABLE = environ['APPLICATIONS_TABLE']

app = Flask(__name__)
CORS(app)

@app.route('/api/events', methods=['GET'])
def events():
    if ENV != 'production':
        with open('fixtures/events.json', 'r') as json_file:
            json = json_file.read()
        return json

    events_table = Airtable(AIRTABLE_APP, EVENTS_TABLE, api_key=AIRTABLE_API_KEY)

    fields = [
      'id', 'assignment_status', 'assignment', 'name', 'agency_name', 'classification',
      'description', 'start_time', 'end_time', 'location_name', 'status', 'community_area'
    ]
    events = events_table.search('assignment_status', 'Open Assignment',
             fields=fields, sort="start_time")

    return jsonify(events)

@app.route('/api/applications', methods=['POST'])
def applications():
    applications_table = Airtable(AIRTABLE_APP, APPLICATIONS_TABLE, api_key=AIRTABLE_API_KEY)

    j = request.json
    fields = {
        'applied_name': j['applied_name'],
        'email': j['email'],
        'Event': j['event'],
        'Agree to Terms': j['agree_to_terms'],
        'Agree to Rate': j['agree_to_rate'],
    }

    app.logger.debug('creating assignment application on Airtable: %s' % str(fields))
    try:
        applications_table.insert(fields)
        return jsonify({'message': 'ok'}), 201
    except HTTPError as error:
        app.logger.error(error)
        app.logger.error(error.response.text)
        return jsonify({'message': 'error'}), 500

if __name__ == "__main__":
    app.run()
