from driveCycleData import driveCycleOne, standardDriveCycle, labDriveCycle
import pandas as pd
import numpy as np 
from flask import Flask, render_template, request, session,current_app

# create Flask application
app = Flask(__name__)
# set a secret key to use sessions
app.secret_key = 'some_secret_key'

# define the route for the home page
@app.route("/")
def home():
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
    current_app.df = df
    # get the dataframe from the session and convert it to JSON
    # pass the JSON data to the first drive cycle detail page template
    return render_template("first_drive_cycle_detail.html", df=df)

# define the route for the data required page
@app.route("/data_required",methods=["POST"])
def data_required():
    # get the dataframe from the session and convert it back to a Pandas dataframe
    return render_template('second_input.html')

# define the route for the analysis page
@app.route('/analysis', methods=['POST'])
def analysis():
    data = {}
    mass = float(request.form['mass'])
    data['mass'] = mass
    rho = float(request.form['rho'])
    data['rho'] = rho
    Cd = float(request.form['Cd'])
    data['Cd'] = Cd
    Af = float(request.form['Af'])
    data['Af'] = Af
    g = float(request.form['Af'])
    data['g'] = g
    alpha = float(request.form['alpha'])
    data['alpha'] = alpha
    r = float(request.form['r'])
    data['r'] = r 
    # get the dataframe from the session and convert it back to a Pandas dataframe
    df = current_app.df
    # perform calculations using the form data and the dataframe
    df_force_analysis = current_app.df # Raeading the data of drivecycle
    df_force_analysis['speed'] = df_force_analysis['Speed [km/h]']*(5/18)
    df_force_analysis['distance'] = (df_force_analysis['speed'] * df_force_analysis['Time [s]'].diff()).cumsum().fillna(0)
    df_force_analysis['Acceleration'] = df_force_analysis['speed'].diff() / df_force_analysis['Time [s]'].diff()
    df_force_analysis['positiveAcceleration'] = df_force_analysis['Acceleration'].where(df_force_analysis['Acceleration'] >= 0, 0)
    
    # Force due to acceleration 
    df_force_analysis['Force_Acceleration'] = mass*df_force_analysis['Acceleration']
    
    # Force due to drag 
    df_force_analysis['Force_Drag'] = 0.5*rho*Af*Cd*(df_force_analysis['speed']**2)
    
    # Force due to friction 
    # Since friction cofficient itself is speed dependent so first we have to calculate the friction cofficient 
    df_force_analysis['Friction_Cofficient'] = np.where(df_force_analysis['Speed [km/h]'] <= 0, 0, 0.01*(1+df_force_analysis['Speed [km/h]']/160))
    df_force_analysis['Force_Rolling_Resistance'] = df_force_analysis['Friction_Cofficient']*mass*g*np.cos(alpha)
    
    # Force due to its own weight travelling on a gradient 
    df_force_analysis['Force_Weight'] = mass*np.sin(alpha)
    
    # Total Force at all the instant points
    
    # Doubt for calculating the all forces We should only consider5 the forces where the acceleration is positive
    # As the vehicle is in braking mode when the acceleration is negative and battery is not providing any energy
    # Total Force at all the instant points
    
    df_force_analysis['Force_Total'] = df_force_analysis['Force_Weight'] + df_force_analysis['Force_Rolling_Resistance'] + df_force_analysis['Force_Drag'] + df_force_analysis['Force_Acceleration']
    df.fillna(0, inplace=True)
    df_force_analysis.fillna(0, inplace=True)
    return render_template('three_analysis.html',data=data,df=df,df_force_analysis = df_force_analysis)

# run the application
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
