import numpy as np

import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station



# Flask Setup

app = Flask(__name__)



# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all dates and precipitation data"""
    # Query all dates and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_date_prcp
    all_date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        all_date_prcp.append(date_prcp_dict)

    return jsonify(all_date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations names"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        all_stations_dict = {}
        all_stations_dict["station"] = station
        all_stations_dict["name"] = name
        all_stations.append(all_stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #find last date in database from Measurements
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = (dt.datetime.strptime(last_day[0], "%Y-%m-%d") - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    #find the most active station in database from Measurements
    active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    """Return a list of dates and temperature of the most active station for the last year"""
    # Query the dates and temperature observations of the most active station for the last year of data 
    results = session.query(Measurement.tobs).filter(Measurement.date >= query_date).\
filter(Measurement.station == active_station[0]).all()

    session.close()

    # Convert list of tuples into normal list
    info_active_station = list(np.ravel(results))

    return jsonify(info_active_station)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum, average and max temperature for a given date"""
    # Query of min, max and avg temperature for all dates greater than and equal to the given date.
    results = session.query(Measurement.date,func.min(Measurement.tobs),\
         func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).all()
             
    session.close()
    
# Create a dictionary from the row data and append to a list of info
    info = []
    for date, min, avg, max in results:
        info_dict = {}
        info_dict["DATE"] = date
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX"] = max
        info.append(info_dict)

    return jsonify(info)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of minimum, average and max temperature for a given start date and end date"""
    # Query of min, max and avg temperature for dates between given start and end date.
    results = session.query(func.min(Measurement.tobs),\
         func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()        
    
# Create a dictionary from the row data and append to a list of info
    info = []

    for min, avg, max in results:
        info_dict = {}
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX "] = max
        info.append(info_dict)



    return jsonify(info)



if __name__ == "__main__":
    app.run(debug=True)
