# Import dependencies
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# Create app
app = Flask(__name__)

# Define homepage
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )

# Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)


    """Return a JSON representation of precipitation data for the last year."""
    
    # Calculate the date 1 year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - relativedelta(years=1)
    
    # Query the database to get precipitation data for the last year
    precip_data = session.query(Measurement.date, Measurement.prcp).\
                  filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary from the query results and append to a list of all precipitation data
    precipitation = []
    for date, prcp in precip_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    # Return the JSON representation of the list of precipitation data
    return jsonify(precipitation)

# Define stations route
@app.route("/api/v1.0/stations")
def stations():
# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    
    # Query the database to get the stations
    stations = session.query(Station.station, Station.name).all()
    
    # Create a dictionary from the query results and append to a list of all stations
    station_list = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)
    
    # Return the JSON representation of the list of stations
    return jsonify(station_list)


# Define tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)


    """Return the temperature observations for the most active station in the last year"""
    # Calculate the date one year ago from the last date in database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the temperature observations for the most active station in the last year
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()[0]

    temp_data = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary from the query results and append to a list of all temperatures
    temperatures = []
    for date, temp in temp_data:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = temp
        temperatures.append(temperature_dict)

    # Return the JSON representation of the list of temperatures
    return jsonify(temperatures)

# Define start route
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start date until the end of the dataset"""

    # Query the database to get the min, avg, and max temperatures for the given start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Create a dictionary from the query results and append to a list of all temperature data
    temperature_data = []
    for min_temp, avg_temp, max_temp in results:
        temperature_dict = {}
        temperature_dict["TMIN"] = min_temp
        temperature_dict["TAVG"] = avg_temp
        temperature_dict["TMAX"] = max_temp
        temperature_data.append(temperature_dict)

    # Return the JSON representation of the list of temperature data
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min, max, and avg temperature for a given start-end range."""
    # Query the min, max, and avg temperatures for the given date range
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary from the query results and append to a list of all temperatures
    temperature_list = []
    for min_temp, max_temp, avg_temp in results:
        temperature_dict = {}
        temperature_dict["TMIN"] = min_temp
        temperature_dict["TMAX"] = max_temp
        temperature_dict["TAVG"] = avg_temp
        temperature_list.append(temperature_dict)

    # Return the JSON representation of the list of temperatures
    return jsonify(temperature_list)

if __name__ == "__main__":
    app.run(debug=True)
