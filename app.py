#Dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt


#establish database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
inspector = inspect(engine)
Base = automap_base()
Base.prepare(autoload_with=engine)
# Base.classes.keys()

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#create app
app = Flask(__name__)


#define all routes
@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/  <start> as ISO date"
        f"/api/v1.0/<start>/<end>   <start> and <end> as ISO dates"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #start session
    session = Session(engine)
    #get date data
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.date.fromisoformat(recent_date[0])
    year_ago = recent_date - dt.timedelta(days = 365)
    #build precip query
    prcp = session.query(Measurement.date, func.sum(Measurement.prcp)).filter(Measurement.date > (year_ago)).order_by(Measurement.date.desc()).group_by(Measurement.date).all()
    #get dictionary results
    all_precip = []
    for date, precip in prcp:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = precip
        all_precip.append(precip_dict)

    session.close()
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    #start session
    session = Session(engine)
    #get station list
    all_stations = session.query(Station.station).all()
    station_list = []
    for x in all_stations:
        station_list.append(x)
    session.close()


    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #get most active station
    most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    active_summary = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs), 2)).filter(Measurement.station == most_active[0]).all()
    last_year_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active[0]).filter(Measurement.date > year_ago).order_by(Measurement.date.desc()).all()
    past_year_tobs = []
    for date, tobs in last_year_tobs:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        past_year_tobs.append(last_year_tobs)
    
    session.close()
    return jsonify(past_year_tobs)

@app.route("/api/v1.0/<start>")
def temp_summary():

    return

@app.route("/api/v1.0/<start>/<end>")
def time_temp_summary():

    return

if __name__ == "__main__":
    app.run(debug=True)