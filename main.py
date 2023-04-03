from driveCycleData import driveCycleOne, standardDriveCycle, labDriveCycle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, send_from_directory
from utilities import dataForce, dataMotor, motorParameters, efficiencyMap, cyclicMotorEfficiency, Batterydata, batteryPar
import json
data = {}


# Open the JSON file and read its contents
with open('data.json', 'r') as f:
    data1 = f.read()
# Parse the JSON data into a dictionary
driveCyclesData = json.loads(data1)

# create Flask application
app = Flask(__name__)
# set a secret key to use sessions
app.secret_key = 'some_secret_key'


# define the route for the home page
@app.route("/")
def home():
  
  # pass drive cycle data to the home page template
  return render_template('home.html',
                         standardDriveCycle=standardDriveCycle,
                         labDriveCycle=labDriveCycle)


# define the route for the drive page
@app.route("/drive", methods=["POST"])
def drive():
  # get the value of the submit button from the form
  key = request.form.get ('submit_button')
  print(key)
  df = pd.DataFrame()
  # set column names  df = pd.DataFrame()
  df['Speed [km/h]'] = driveCyclesData[key]
  
# create a new column called `time` in the DataFrame `df`
  df['Time [s]'] = pd.Series(list(range(len(driveCyclesData[key]))))
  # calculate acceleration and add it as a new column to the dataframe
  df['Acceleration'] = df['Speed [km/h]'].diff() / df['Time [s]'].diff()
  df.fillna(0, inplace=True)
  # store the dataframe in the session
  data["df"] = df
  # get the dataframe from the session and convert it to JSON
  # pass the JSON data to the first drive cycle detail page template
  
  return render_template("first_drive_cycle_detail.html", df=df)


# define the route for the data required page
@app.route("/data_required", methods=["POST"])
def data_required():
  # get the dataframe from the session and convert it back to a Pandas dataframe
  vehicle_data = [
    {'name': 'RE Classic 350', 'weight': 195, 'wheel_radius': 0.2413, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Hero Honda(Splender plus)', 'weight': 110, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'TVS star city', 'weight': 116, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Honda Activa 110', 'weight': 110, 'wheel_radius': 0.175, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Hero Honda CD Deluxe', 'weight': 112, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Hero Passion Pro', 'weight': 118, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Honda CB Shine 125cc', 'weight': 114, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'TVS Radeon', 'weight': 118, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68},
    {'name': 'Bajaj discover', 'weight': 120, 'wheel_radius': 0.2, 'drag_coefficient': 0.78, 'vehicle_area': 0.68}
]
  return render_template('second_input.html',
                         background=send_from_directory(
                           'static/images', 'image.webp'),vehicle_data=vehicle_data)


# define the route for the analysis page
@app.route('/analysis', methods=['POST'])
def analysis():
  data['mass'] = float(request.form['mass'])
  data['rho'] = float(request.form['rho'])
  data['Cd'] = float(request.form['Cd'])
  data['Af'] = float(request.form['Af'])
  data['g'] = float(request.form['Af'])
  data['alpha'] = float(request.form['alpha'])
  data['r'] = float(request.form['r'])

  # get the dataframe from the session and convert it back to a Pandas dataframe
  df = data["df"]
  # perform calculations using the form data and the dataframe
  data["df"] = dataForce(data, df)
  print("analysis : ", data)
  return render_template('three_analysis.html',
                         data=data,
                         df=df,
                         df_force_analysis=data["df"])


@app.route('/power_analysis', methods=["POST"])
def power_analysis():
  df = data["df"]
  df_force_analysis = (data["df"])
  print("Power Analysis : ", data)
  return render_template("four_power_analysis.html",
                         df=df,
                         df_force_analysis=df_force_analysis)


@app.route("/datadrivetriansizing", methods=["POST"])
def datadrivetrainsizing():
  print("datadrivetrain sizing : ", data)
  return render_template("five_drive_train_sizing.html")


@app.route("/speedTorueChracterstics", methods=["POST"])
def speedTorqueChracterstics():
  data['gear_ratio'] = float(request.form['gear_ratio'])
  data['gear_efficiency'] = float(request.form['gear_efficiency'])
  data['motor_overload_factor_for_power'] = float(
    request.form['motor_overload_factor_for_power'])
  data['motor_overload_factor_for_torque'] = float(
    request.form['motor_overload_factor_for_torque'])
  data["motor_max_to_base_speed_ratio"] = float(
    request.form['motor_overload_factor_for_torque'])
  data['df'] = dataMotor(data, data['df'])
  motorpara = motorParameters(data, data['df'])
  maximum_speed_rpm = max(data['df']['Motor_Speed_rpm'])
  max_torque = max(data['df']['Motor_Torque'])
  # Define the range of values for speed and torque
  speed = np.linspace(
    0, maximum_speed_rpm, num=10
  )  # This will reshape the motor speed in rpm [0,maximum_Motor_speed_in_Rpm]
  torque = np.linspace(
    -10, max_torque,
    num=8)  # This will reshape the motor torque in [-10,max_torque]

  # Generate a grid of X and Y values
  X, Y = np.meshgrid(speed, torque)

  # Define the operating efficiency values
  Z = efficiencyMap()
  X = speed.tolist()
  Y = torque.tolist()
  Z = Z.tolist()

  return render_template('seven_speedTorqueChracterstics.html',
                         df=data['df'],
                         motorpara=motorpara,
                         X=X,
                         Y=Y,
                         Z=Z)


@app.route("/batteryCalculations", methods=['POST'])
def batteryCalculations():
  return render_template('eight_battery_caluclations.html')


@app.route('/batteryParameters', methods=['POST'])
def batteryParameters():

  data['range_we_wanted'] = float(request.form['range_we_wanted'])
  data['optimal_c_rate'] = float(request.form['optimal_c_rate'])
  data['battery_voltage'] = float(request.form['battery_voltage'])
  data['battery_utilization'] = float(request.form['battery_utilization'])
  data['specific_energy_battery'] = float(
    request.form['specific_energy_battery'])

  data['df'] = cyclicMotorEfficiency(data['df'])
  data['df'] = Batterydata(data['df'])
  batteryPara = batteryPar(data, data['df'])
  label_map = {
      'Total_energy_consumed_in_drive_cycle': 'Total Energy Consumed in Drive Cycle',
      'Milage': 'Mileage',
      'battery_size': 'Battery Size',
      'optimal_battery_power': 'Optimal Battery Power',
      'weight_of_the_battery': 'Weight of the Battery',
      'battery_Ah': 'Battery Ampere-hour (Ah)',
      'usable_Ah': 'Usable Ampere-hour (Ah)'
  }
  labeled_params = {label_map[k]: v for k, v in batteryPara.items()}
  param_info = {
    'Total_energy_consumed_in_drive_cycle': {
      'description': 'Total energy consumed in the drive cycle in kWhr/km',
      'wiki_url': 'https://en.wikipedia.org/wiki/Kilowatt_hour'
    },
    'Milage': {
      'description': 'Mileage of the vehicle in km/kWhr',
      'wiki_url': 'https://en.wikipedia.org/wiki/Fuel_economy_in_automobiles'
    },
    'battery_size': {
      'description':
      'Size of the battery required to achieve the desired range in kWhr',
      'wiki_url': 'https://en.wikipedia.org/wiki/Battery_(electricity)'
    },
    'optimal_battery_power': {
      'description': 'Optimal power rating of the battery in kW',
      'wiki_url': 'https://en.wikipedia.org/wiki/Battery_(electricity)'
    },
    'weight_of_the_battery': {
      'description': 'Weight of the battery in kg',
      'wiki_url': 'https://en.wikipedia.org/wiki/Lithium-ion_battery'
    },
    'battery_Ah': {
      'description': 'Battery capacity in Ampere-hour (Ah)',
      'wiki_url': 'https://en.wikipedia.org/wiki/Ampere_hour'
    },
    'usable_Ah': {
      'description': 'Usable battery capacity in Ampere-hour (Ah)',
      'wiki_url': 'https://en.wikipedia.org/wiki/Ampere_hour'
    }
  }
  return render_template('nine_battery_parameters.html',
                         data=batteryPara,
                         param_info=param_info)


@app.route('/check')
def check():
  return render_template('check.html')

# run the application
if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
