from driveCycleData import driveCycleOne, standardDriveCycle, labDriveCycle
import pandas as pd
import numpy as np 
from flask import Flask, render_template, request, session,current_app, send_from_directory
from utilities import dataForce , dataMotor, motorParameters

data = {}

# create Flask application
app = Flask(__name__)
# set a secret key to use sessions
app.secret_key = 'some_secret_key'

# define the route for the home page
@app.route("/")
def home():
  print("Home : ",data)
    # pass drive cycle data to the home page template
  return render_template('home.html', standardDriveCycle=standardDriveCycle, labDriveCycle=labDriveCycle)

# define the route for the drive page
@app.route("/drive", methods=["POST"])
def drive():
    # get the value of the submit button from the form
    value = request.form.get('submit_button')
    # set column names
    column_names = ['Time [s]', 'Speed [km/h]']
    # create a dataframe from the drive cycle data and column names
    df = pd.DataFrame(driveCycleOne, columns=column_names)
    # calculate acceleration and add it as a new column to the dataframe
    df['Acceleration'] = df['Speed [km/h]'].diff() / df['Time [s]'].diff()
    df.fillna(0, inplace=True)
    # store the dataframe in the session
    data["df"] = df
    # get the dataframe from the session and convert it to JSON
    # pass the JSON data to the first drive cycle detail page template
    print("drive : ",data)
    return render_template("first_drive_cycle_detail.html", df=df)

# define the route for the data required page
@app.route("/data_required",methods=["POST"])
def data_required():
    # get the dataframe from the session and convert it back to a Pandas dataframe
    return render_template('second_input.html',background=send_from_directory('static/images', 'image.webp'))

# define the route for the analysis page
@app.route('/analysis', methods=['POST'])
def analysis(): 
    data['mass'] = float(request.form['mass'])
    data['rho'] = float(request.form['rho'])
    data['Cd']= float(request.form['Cd'])
    data['Af'] = float(request.form['Af'])
    data['g'] = float(request.form['Af'])
    data['alpha'] = float(request.form['alpha'])
    data['r'] = float(request.form['r'])
  
    # get the dataframe from the session and convert it back to a Pandas dataframe
    df = data["df"]
    # perform calculations using the form data and the dataframe
    data["df"] = dataForce(data,df)
    print("analysis : ",data)
    return render_template('three_analysis.html',data=data,df=df,df_force_analysis = data["df"])

@app.route('/power_analysis',methods=["POST"])
def power_analysis():
  df = data["df"]
  df_force_analysis = (data["df"])
  print("Power Analysis : ",data)
  return render_template("four_power_analysis.html", df=df, df_force_analysis = df_force_analysis)

@app.route("/datadrivetriansizing",methods=["POST"])
def datadrivetrainsizing():
  print("datadrivetrain sizing : ",data)
  return render_template("five_drive_train_sizing.html")

@app.route("/drivetrainsizing", methods=["POST"])
def drivetrainsizing():
  data['gear_ratio'] = float(request.form['gear_ratio'])
  data['gear_efficiency'] = float(request.form['gear_efficiency'])
  data['motor_overload_factor_for_power']= float(request.form['motor_overload_factor_for_power'])
  data['motor_overload_factor_for_torque']= float(request.form['motor_overload_factor_for_torque'])
  data["motor_max_to_base_speed_ratio"] = float(request.form['motor_overload_factor_for_torque'])
  data['df'] = dataMotor(data,data['df'])
  motorpara = motorParameters(data,data['df'])
  
  return render_template("six_drivetrainsizing.html",motorpara=motorpara)



# run the application
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
