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
    # if ENV != 'production':
    #     with open('fixtures/events.json', 'r') as json_file:
    #         json = json_file.read()
    #     return json

    events_table = Airtable(AIRTABLE_APP, EVENTS_TABLE, api_key=AIRTABLE_API_KEY)

    fields = [
        'Status', 'Assignment', 'Name', 'Agency', 'Type', 'Address',
        'Description', 'Start Date and Time', 'URL', 'Phone',
    ]

    try:
        event_rows = events_table.search('Status', 'Open',
                                        fields=fields, sort="Start Date and Time")

        events = [convert_fields(row) for row in event_rows]
        return jsonify(events)
    except HTTPError as error:
        print(error)
        return error.response.text


def convert_fields(row):
    print(row)
    fields = row['fields']
    return {
        'id': row['id'],
        'fields': {
            'name': fields.get('Name', ''),
            'agency_name': fields.get('Agency', ''),
            'assignment': fields.get('Assignment', []),
            'description': fields.get('Description', ''),
            'location_address': fields.get('Address', ''),
            'start_time': fields.get('Start Date and Time', ''),
            'url': fields.get('URL', ''),
            # end_time, community_area
        },
    }

@app.route('/api/applications', methods=['POST'])
def applications():
    applications_table = Airtable(AIRTABLE_APP, APPLICATIONS_TABLE, api_key=AIRTABLE_API_KEY)

    j = request.json
    for event in j['event']:
        fields = {
            'Name': j['applied_name'],
            'Email': j['email'],
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
