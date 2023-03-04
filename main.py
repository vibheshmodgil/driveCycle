from driveCycleData import driveCycleOne , standardDriveCycle, labDriveCycle
import pandas as pd
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'some_secret_key'
@app.route("/")
def home():
  return render_template('home.html',standardDriveCycle=standardDriveCycle,labDriveCycle=labDriveCycle)

@app.route("/check",methods=["POST"])
def check():
  
  value = request.form.get('submit_button')
  print(value)
  # set column names
 
  return render_template('check.html',df=df)

@app.route("/drive", methods=["POST"])
def drive():
  value = request.form.get('submit_button')
  column_names = ['Time [s]', 'Speed [km/h]']
  df = pd.DataFrame(driveCycleOne, columns=column_names)
  df['Acceleration'] = df['Speed [km/h]'].diff()/df['Time [s]'].diff()
  df.fillna(0, inplace=True)
  session['df'] = df 
  print(value)
  return render_template("first_drive_cycle_detail.html",df=df )

@app.route("/data_required",methods=["POST"])
def data_required():
  return render_template('second_input.html', x=session['df']['Acceleration'] )

@app.route("/analysis",methods=["POST"])
def analysis():
  return render_template('three_analysis.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)