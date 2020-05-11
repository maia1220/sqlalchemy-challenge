
# import
from flask import Flask, jsonify
# %matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base= automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Station=Base.classes.station
Measure=Base.classes.measurement

# start app design
app = Flask(__name__)

@app.route("/")
def index():
    return (
        f"Welcome to your personal climate API!<br/>"
        f"Available Routes:<br/>"
        f"1: /api/v1.0/precipitation<br/>"
        f"2: /api/v1.0/stations<br/>"
        f"3: /api/v1.0/tobs<br/>"
        f"For #4 & #5: from '2010-01-01' to '2017-08-23':</br>"
        f"please first delete the 'startdate' and 'enddate' in the route names,</br>"
        f"then enter the dates that you choose as YYYYMMDD (numbers only, no hyphen nor space).</br>"
        f"4: /api/v1.0/startdate<br/>"
        f"5: /api/v1.0/startdate/enddate"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    session=Session(engine)
    results=session.query(Measure.date, Measure.prcp).all()
    session.close()

    all_prcp_dict = []

    for date, prcp in results:
        p_dict = {}
        p_dict["Date"] = date
        p_dict["Precipitation"] = prcp
        all_prcp_dict.append(p_dict)

    return jsonify(all_prcp_dict)

@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    results=session.query(Station.station, Station.name).\
            filter(Measure.station == Station.station).\
            group_by(Station.station).all()
    session.close()

    all_names=list(np.ravel(results))
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    results=session.query(Measure.date, Measure.tobs).all()
    session.close()

    lastdate=session.query(Measure.date).order_by(Measure.date.desc()).first()
    unano = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    mostactives=session.query(Measure.station, func.count(Measure.station)).\
            group_by(Measure.station).\
            order_by(func.count(Measure.station).desc()).first()
    most_active_station=mostactives.station

    year_tobs=session.query(Measure.date, Measure.tobs).\
        filter(Measure.date >= unano).\
        filter(Measure.station == most_active_station).\
        order_by(Measure.date).all()
    return jsonify(year_tobs)

@app.route("/api/v1.0/<start>")
def start_only_data(start):
    session=Session(engine)
    results=session.query(Measure.date, Measure.tobs).all()
    session.close()

    temp=[func.min(Measure.tobs), func.max(Measure.tobs),func.avg(Measure.tobs)]

     
    if len(str(start))==8:
        
        st=str(start)
        start_date=st[:4]+ "-"+st[4:6]+"-"+st[6:]
        syear=st[:4]
        smonth=st[4:6]
        sday=st[6:]

        start_temp_data=session.query(*temp).\
        filter(Measure.date >= dt.datetime(int(syear), int(smonth), int(sday))).\
        all()

        stmin=start_temp_data[0][0]
        stmax=start_temp_data[0][1]
        stavg=round(start_temp_data[0][2],2)

        return f"After {start_date}, the Min temperature: {stmin}, Max temperature: {stmax}, Average temperature: {stavg}."
    else:
        return "Please enter the start date as YYYYMMDD."

    
@app.route("/api/v1.0/<start>/<end>")
def start_end_data(start, end):
    session=Session(engine)
    results=session.query(Measure.date, Measure.tobs).all()
    session.close()

    temp=[func.min(Measure.tobs), func.max(Measure.tobs),func.avg(Measure.tobs)]


    if len(str(start))==8:
        if len(str(end))==8:
            st=str(start)
            start_date=st[:4]+ "-"+st[4:6]+"-"+st[6:]

            et=str(end)
            end_date=et[:4]+ "-"+et[4:6]+"-"+et[6:]

            temp_data=session.query(*temp).\
            filter(Measure.date >= start_date).\
            filter(Measure.date <= end_date).\
            all()

            tmin=temp_data[0][0]
            tmax=temp_data[0][1]
            tavg=round(temp_data[0][2],2)

            return f"The Min temperature: {tmin}, Max temperature: {tmax}, Average temperature: {tavg} between {start_date} and {end_date}."
    else:
        return "Please enter the start and end date as YYYYMMDD."



if __name__ == '__main__':
    app.run(debug=True)


