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

if ENV == 'production':
    from raven.contrib.flask import Sentry
    Sentry(app, dsn=environ['SENTRY_DSN'])

@app.route('/api/events', methods=['GET'])
def events():
    if ENV != 'production':
        with open('fixtures/events.json', 'r') as json_file:
            json = json_file.read()
        return json

    events_table = Airtable(AIRTABLE_APP, EVENTS_TABLE, api_key=AIRTABLE_API_KEY)

    fields = [
        'id', 'assignment_status', 'assignment', 'name', 'agency_name', 'classification',
        'description', 'start_time', 'end_time', 'location_address', 'status', 'community_area',
        'Custom Start Time', 'Custom End Time'
    ]
    event_rows = events_table.search('assignment_status', 'Open Assignment',
                                     fields=fields, sort="start_time")

    # handle custom start and end times :/
    for row in event_rows:
        fields = row['fields']
        if 'Custom Start Time' in fields:
            fields['start_time'] = fields['Custom Start Time']
            del fields['Custom Start Time']
        if 'Custom End Time' in fields:
            fields['end_time'] = fields['Custom End Time']
            del fields['Custom End Time']

    return jsonify(event_rows)

@app.route('/api/applications', methods=['POST'])
def applications():
    applications_table = Airtable(AIRTABLE_APP, APPLICATIONS_TABLE, api_key=AIRTABLE_API_KEY)

    j = request.json
    for event in j['event']:
        fields = {
            'applied_name': j['applied_name'],
            'email': j['email'],
            'Event': [event['id']],
            'Agree to Attend': j['agree_to_attend'],
            'Agree to Rate': j['agree_to_rate'],
            'Agree to Pay Taxes': j['agree_to_pay_taxes'],
            'Agree to Follow Instructions': j['agree_to_follow_instructions'],
            'Assignment Type': event['assignment_type']
        }

        app.logger.debug('creating assignment application on Airtable: %s' % str(fields))
        try:
            applications_table.insert(fields)
        except HTTPError as error:
            app.logger.error(error)
            app.logger.error(error.response.text)
            return jsonify({'message': 'error'}), 500

    return jsonify({'message': 'ok'}), 201

if __name__ == "__main__":
    app.run()
