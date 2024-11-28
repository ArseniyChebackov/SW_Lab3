import requests
from flask import Flask, abort, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sparql import get_universities_in_ukraine
import click
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'universities.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# University model
class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200), nullable=True)

# Routes
@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query')
    type_filter = request.args.get('type')
    location_filter = request.args.get('location')

    universities = University.query

    if query:
        universities = universities.filter(University.name.ilike(f'%{query}%'))
    if type_filter:
        universities = universities.filter(University.type.ilike(f'%{type_filter}%'))
    if location_filter:
        universities = universities.filter(University.location.ilike(f'%{location_filter}%'))

    universities = universities.all()

    return render_template('index.html', universities=universities)

@app.route('/university/<int:id>')
def university(id):
    university = db.session.get(University, id)
    if university is None:
        abort(404)
    return render_template('university.html', university=university)

@app.route('/about')
def about():
    return render_template('about.html')

# CLI command to initialize the database
@app.cli.command('init-db')
def initialize_data():
    db.create_all()  # Create tables

    # Fetch universities from DBpedia and add to the database
    data = get_universities_in_ukraine()
    if data:
        for item in data:
            name = item.get('name', '')
            university_type = item.get('type', '')
            location = item.get('location', 'Unknown')
            website = item.get('website', '')

            # Fetch location using geocoding API
            if not location or location == 'Unknown':
                location = fetch_location(name)
                print(f"Fetched location for {name}: {location}")

            if name:
                new_university = University(
                    name=name,
                    type=university_type,
                    location=location,
                    website=website,
                )
                db.session.add(new_university)
        db.session.commit()
    print("Database initialized with universities data.")

def fetch_location(name):
    api_key = '2f5740e410e24646a4859a5a7fc0c19d'
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': name,
        'key': api_key,
        'countrycode': 'ua',
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data['results']:
        return data['results'][0]['formatted']
    return 'Unknown'

if __name__ == '__main__':
    app.run(debug=True)