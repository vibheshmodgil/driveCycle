import numpy as np 
import pandas as pd



def dataForce(data,df):
  mass = data['mass'] 
  rho = data['rho'] 
  Cd = data['Cd']
  Af = data['Af'] 
  g = data['g'] 
  alpha = data['alpha'] 
  r = data['r'] 
  df['speed'] = df['Speed [km/h]']*(5/18)
  df['distance'] = (df['speed'] * df['Time [s]'].diff()).cumsum().fillna(0)
  df['Acceleration'] = df['speed'].diff() / df['Time [s]'].diff()
  df['positiveAcceleration'] = df['Acceleration'].where(df['Acceleration'] >= 0, 0)

  # Force due to acceleration 
  df['Force_Acceleration'] = mass*df['positiveAcceleration']

  # Force due to drag 
  df['Force_Drag'] = 0.5*rho*Af*Cd*(df['speed']**2)

  # Force due to friction 
  # Since friction cofficient itself is speed dependent so first we have to calculate the friction cofficient 
  df['Friction_Cofficient'] = np.where(df['Speed [km/h]'] <= 0, 0, 0.01*(1+df['Speed [km/h]']/160))
  df['Force_Rolling_Resistance'] = df['Friction_Cofficient']*mass*g*np.cos(alpha)

  # Force due to its own weight travelling on a gradient 
  df['Force_Weight'] = mass*np.sin(alpha)

  # Total Force at all the instant points

  # Doubt for calculating the all forces We should only consider5 the forces where the acceleration is positive
  # As the vehicle is in braking mode when the acceleration is negative and battery is not providing any energy
  # Total Force at all the instant points

  df['Force_Total'] = df['Force_Weight'] + df['Force_Rolling_Resistance'] + df['Force_Drag'] + df['Force_Acceleration']

  # Force vise power analysdf_force_analysis
  df['Power_Drag'] = df['Force_Drag']*df['speed']
  df['Power_Rolling_Resistance'] = df['Force_Rolling_Resistance']*df['speed']
  df['Power_Weight'] = df['Force_Weight']*df['speed']
  df['Power_Acceleration'] = df['Force_Acceleration']*df['speed']
  df['Power_Total'] = df['Force_Total']*df['speed']


  df['omega'] = df['speed']/r
  df['omega_rpm'] = df['omega']*(60/(2*np.pi))
  df['Torque_Wheel'] = df['Force_Total']*r

  df['Power_Wheels'] = df['Torque_Wheel']*df['omega']
  df.fillna(0, inplace=True)
  return df 



def dataMotor(data,df):
    gear_ratio = data['gear_ratio'] 
    gear_efficiency = data['gear_efficiency'] 
    Motor_overload_factor_power = data['motor_overload_factor_for_power']
    Motor_overload_factor_for_torque = data['motor_overload_factor_for_torque']
    Motor_max_to_base_speed_ratio = data["motor_max_to_base_speed_ratio"] 
    # Speed and the Torque on the motor side 
    df['Motor_Torque'] = np.where(df['Torque_Wheel'] >= 0, 
                                        df['Torque_Wheel']/(gear_ratio*gear_efficiency), 
                                        0)
    df['Motor_Speed'] = (df['omega']*gear_ratio) 
    df['Motor_Speed_rpm'] = (df['omega_rpm']*gear_ratio) 

    # Get the maximum value of Motor_Speed
    max_speed_Rpm = df['Motor_Speed_rpm'].max()
    # Get the number of values in the Motor_Speed column
    num_values = df.shape[0]
    # Generate a new series with the same number of values as the Motor_Speed column
    plottingSpeedRpm = np.linspace(0, max_speed_Rpm, num_values)
    # Add the new series to the df_motor dataframe
    df['plotting_Speed_Rpm'] = plottingSpeedRpm

    # Get the maximum value of Motor_Speed
    max_speed = df['Motor_Speed'].max()
    # Get the number of values in the Motor_Speed column
    num_values = df.shape[0]
    # Generate a new series with the same number of values as the Motor_Speed column
    plottingSpeed = np.linspace(0, max_speed, num_values)
    # Add the new series to the df_motor dataframe
    df['plotting_Speed'] = plottingSpeed

    # Maximum Torque and speed at maximum torque 
    max_index = df['Motor_Torque'].idxmax()
    speed_at_peak_torque = df.loc[max_index, 'Motor_Speed_rpm']
    max_torque = df.loc[max_index, 'Motor_Torque']

    # Finding the motor output power
    df['power_motor_output'] = df['Motor_Torque']*df['Motor_Speed']

    # Formulas For the further analysis 
    base_speed_for_motor = max_speed/Motor_max_to_base_speed_ratio # Base Speed of the motor in radian per second 
    rated_torque_for_motor = max_torque/Motor_overload_factor_for_torque # Max Torque in Nm 
    rated_power_of_motor = rated_torque_for_motor*base_speed_for_motor/(1000) # Rated Power of in KW 
    peak_power_of_motor = rated_power_of_motor*Motor_overload_factor_power # Peak Power of the motor in KW 

    # For plotiing motor Rated Torque-Speed Chracterstics 
    df['plotting_rated_motor_torque'] = np.where(df['plotting_Speed'] <= base_speed_for_motor, 
                                           rated_torque_for_motor, 
                                           rated_power_of_motor*1000/df['plotting_Speed'])

    # For plotiing motor Peak Torque-Speed Chracterstics 
    df['plotting_peak_motor_torque'] = np.where(df['plotting_Speed'] <= base_speed_for_motor, 
                                           max_torque, 
                                           peak_power_of_motor*1000/df['plotting_Speed'])
    df.fillna(0, inplace=True)
    return df 

def motorParameters(data, df):
    Motor_overload_factor_power = data['motor_overload_factor_for_power']
    Motor_overload_factor_for_torque = data['motor_overload_factor_for_torque']
    Motor_max_to_base_speed_ratio = data["motor_max_to_base_speed_ratio"] 
  
    motorpara = {}
    max_speed = df['Motor_Speed'].max()
    motorpara['max_speed'] = max_speed

    # Maximum Torque and speed at maximum torque 
    max_index = df['Motor_Torque'].idxmax()
    speed_at_peak_torque = df.loc[max_index, 'Motor_Speed_rpm']
    motorpara['speed_at_peak_torque'] = speed_at_peak_torque
    max_torque = df.loc[max_index, 'Motor_Torque']

    # Formulas For the further analysis 
    base_speed_for_motor = max_speed/Motor_max_to_base_speed_ratio # Base Speed of the motor in radian per second 
    rated_torque_for_motor = max_torque/Motor_overload_factor_for_torque # Max Torque in Nm 
    rated_power_of_motor = rated_torque_for_motor*base_speed_for_motor/(1000) # Rated Power of in KW 
    peak_power_of_motor = rated_power_of_motor*Motor_overload_factor_power # Peak Power of the motor in KW 
    
    # Motor parameters after the calculations   
    motorpara['max_torque'] = max_torque
    motorpara['Motor_overload_factor_for_torque'] = Motor_overload_factor_for_torque
    motorpara['rated_torque_for_motor'] = rated_torque_for_motor
    motorpara['base_speed_for_motor'] = base_speed_for_motor
    motorpara['Motor_max_to_base_speed_ratio'] = Motor_max_to_base_speed_ratio
    motorpara['rated_power_of_motor'] = rated_power_of_motor
    motorpara['peak_power_of_motor'] = peak_power_of_motor
    
    
    return motorpara
  
