import os
import requests
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
app=Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

#basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db' #+ os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#Migrate(app,db)

class location(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.Text)

    def __init__(self,name):
        self.name=name

def get_weather_data(city):
    url="https://api.openweathermap.org/data/2.5/weather?q={}&appid=a23e55afd350bf3c31d2b9a47cde885f"
    r=requests.get(url.format(city)).json()
    return r


@app.route("/",methods=['GET'])
def index_get():
    cities=location.query.all()

    weather_data=[]

    for city in reversed(cities):
        r=get_weather_data(city.name)

        weather={
        "city":city.name,
        "temperatue":str(round(int(r['main']['temp'])-273.1,2))+"º Celsius",
        "description":r['weather'][0]['description'],
        "icon":r['weather'][0]['icon']
        }


        weather_data.append(weather)

    return render_template("weather.html",weather_data=weather_data)

@app.route("/",methods=['POST'])
def index_post():
    err_msg=''
    new_city=request.form.get("city")
    new_city=new_city.capitalize()
        #print(new_city)
    if new_city:
            existing_city=location.query.filter_by(name=new_city).first()

            if not existing_city:
                new_city_data=get_weather_data(new_city)
                if new_city_data["cod"]==200:
                    new_city_obj=location(name=new_city)
                    #print(new_city_obj)
                    db.session.add(new_city_obj)
                    db.session.commit()
                else:
                    err_msg="City does not exist in the world!!"
            else:
                err_msg="city already exist in our database!!"
    if err_msg:
            flash(err_msg,'error')

    else:
            flash("City added successfully")
    return redirect(url_for("index_get"))

@app.route("/delete/<name>")
def delete_city(name):
    city=location.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f"successfully deleted {city.name}","success")
    return redirect(url_for("index_get"))

if __name__ == '__main__':
    app.run(debug=True)
