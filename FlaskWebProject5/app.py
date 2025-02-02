

from urllib import response
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import null
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from geopy.geocoders import Nominatim 
from datetime import datetime
import json
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config['SECRET_KEY'] = 'secret string'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    searches = db.relationship("SearchHistory", backref="user", lazy=True)

class WeatherForm(FlaskForm):
    city = StringField("City", validators=[DataRequired()])
    submit = SubmitField("Get Weather")
 
@app.route("/", methods=["GET", "POST"])
def index():
    form = WeatherForm()
    if form.is_submitted():
        city_name = form.city.data
        city = City.query.filter_by(name=city_name).first()
        if city is None:
            city = City(name=city_name)
            db.session.add(city)
            db.session.commit()
        user_id = get_user_id()
        search_history = SearchHistory(user_id=user_id, city_id=city.id)
        db.session.add(search_history)
        db.session.commit()
        weather_data = get_weather_data(city_name)
        if weather_data!= null:
            now = datetime.now()
            return render_template("weather.html", city=city_name, temperature=weather_data['hourly']['temperature_2m'][now.hour], current_time=weather_data['hourly']['time'][now.hour] )
    return render_template("index.html", form=form)

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    city_name = request.args.get("city")
    cities = City.query.filter(City.name.like(f"%{city_name}%")).all()
    return jsonify([city.name for city in cities])

@app.route("/search_history", methods=["GET"])
def search_history():
    user_id = get_user_id()
    searches = SearchHistory.query.filter_by(user_id=user_id).all()
    return jsonify([{"city": city.city.name, "count": len(searches)} for city in searches])

def get_user_id():
    # implement user authentication and return user ID
    return 1

def get_weather_data(city_name):
    
    api_url = "https://api.open-meteo.com/v1/forecast"
    gn = Nominatim(user_agent="tutorial")
    location = gn.geocode(city_name)
    if location == None:
        return null
    params = {
	"latitude": location.latitude,
	"longitude": location.longitude,
	"hourly": "temperature_2m"
    } 
    response = requests.get(api_url, params=params)
    data = response.json()
        
    #now = datetime.now()
    #print(data['hourly']['time'][now.hour], data['hourly']['temperature_2m'][now.hour])
 
    return data

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)