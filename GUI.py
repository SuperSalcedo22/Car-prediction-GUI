
''' 
Importing the required libraries
'''
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ck
import pandas as pd
import numpy as np
import requests
import pickle

'''
Defining global variables to be used

Data was imported as csv filse directly from the autotrader website
'''
# importing the manufacturer csv
makenmod_df = pd.read_csv('updated.csv')

#initialising the empty dictionary to be filled
model_dict = {}

# filling the dictionary with the make as key and the models as the values
for i in range(len(makenmod_df)):
    model_dict[makenmod_df['make'][i]] = makenmod_df['model'][i].split('#')
    
######## creating the fuel type variable
fuel_list = ['Bi Fuel',
             'Diesel',
             'Diesel Hybrid',
             'Petrol',
             'Petrol Hybrid',
             'Petrol Plug-in Hybrid']

#creating the dictionary and filling with zero values
fuel_dict = {x: 0 for x in fuel_list}


######## creating the bodytype variable
# importing the csv
type_df = pd.read_csv('type.csv')

type_dict = {}
for i in range(len(type_df)):
    type_dict[type_df['type'][i]] = type_df['code'][i]
bt_list = list(type_dict.keys())

######## creating the transmission variable
trans_list= ['Automatic','Manual']

####### creating the car make
# importing the csv
make_df = pd.read_csv('make.csv')

make_dict = {}
for i in range(len(make_df)):
    make_dict[make_df['make'][i]] = make_df['code'][i]
# creating the make list from the keys
make_list = list(make_dict.keys())

###### MAE found from the model
mae_perc = 1247/6697

'''
Setting up the interface
'''

background='#323050'
background ='#000000'
ck.set_appearance_mode('Dark')
ck.set_default_color_theme('dark-blue')

button_colour = '#CFD52A'

welcome_message = "Welcome to the Autotrader car valuation tool, this was trained using listed data on our website"

explain = "Please fill in the boxes below for an estimation on the price of your car"

stuck = "If your units do not match, open the conversion tools for the appropiate units"

make_msg = 'Please select the car make/manufacturer:'

bt_msg = 'Please select the body type:'

trans_msg = 'Please select the transmission:'

fuel_msg = 'Please select the fuel type:'

age_msg = 'Please enter the age of the vehicle (in years):'
max_age = 100 

milea_msg = 'Please enter the mileage:'
max_milea = 1000000

power_msg = 'Please enter the power (in BHP)'
max_power = 1000

size_msg = 'Please enter the engine size (to nearest 0.1 litres):'
max_size = 10

based = 'Based on the following input variables:'

disclaimer = 'Please note: this is only an estimate, for a more accurate cost please contact Autotrader directly'

'''
Functions
'''

# the screen size is found to ensure the UI fills the screen whenever used
def get_display_size():
    '''Finding the ideal screenwidth for the current display'''
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    global desc_height, desc_width
    desc_height = root.winfo_screenheight()
    desc_width = root.winfo_screenwidth()
    root.destroy()

def clear_widgets(frame):
    '''Deleting the widgets in the current frame before the next frame'''
    # select all frame widgets and delete them
    for widget in frame.winfo_children():
        widget.destroy()

# function that edits the display for the conversion tool        
def convert_km_to_miles():
    '''km to miles for the milage of the vehicle'''
    km = float(km_entry.get())
    miles = round(km * 0.621371,1)
    miles_label.config(text=str(miles))
        
def convert_ps_to_bhp():
    '''converting ps to bhp for the engine power'''
    ps = float(ps_entry.get())
    bhp = round(ps * 0.98632,1)
    bhp_label.config(text=str(bhp))    

def convert_cc_to_litres():
    '''converting cc to litres for convenience'''
    cc = float(cc_entry.get())
    litres = round(cc * 0.001,1)
    litres_label.config(text=str(litres))
    
def convert_us():
    '''Function to convert pounds to dollars using an API'''
    # Get the amount in pounds from the user
    upper_pounds = float(upper_price)
    lower_pounds = float(lower_price)
    # Make a GET request to the API to convert pounds to dollars
    url = f'https://api.exchangerate-api.com/v4/latest/GBP'
    response = requests.get(url)
    data = response.json()
    # Get the exchange rate for USD
    rate = data['rates']['USD']
    # Calculate the amount in dolars
    upper_dollars = round(upper_pounds * rate)
    lower_dollars = round(lower_pounds * rate)
    # Display the amount in dollars in the label
    label.config(text=f'${lower_dollars}-${upper_dollars}')

def convert_eu():
    '''Function to convert pounds to dollars using an API'''    
    # Get the amount in pounds from the user
    upper_pounds = float(upper_price)
    lower_pounds = float(lower_price)
    # Make a GET request to the API to convert pounds to euros
    url = f'https://api.exchangerate-api.com/v4/latest/GBP'
    response = requests.get(url)
    data = response.json()
    # Get the exchange rate for EUR
    rate = data['rates']['EUR']
    # Calculate the amount in euros
    upper_eu = round(upper_pounds * rate)
    lower_eu = round(lower_pounds * rate)
    # Display the amount in euros in the label
    label.config(text=f'€{lower_eu}-€{upper_eu}') 
    
def predict():
    '''Importing the ML algorithm'''
    
    #using the dictionary of encoded values and the one hot encoded values 
    #the user input of categorical variables are converted and put into an array
    
    # one hot encoded transmission before inputting into the machine learning model
    if cb_values['Trans'] == 'Automatic':
        trans_auto = 1
        trans_man = 0
    else:
        trans_auto = 0
        trans_man = 1
        
    # one hot encoding the fuel type to 1 based on the user input
    fuel_dict[cb_values['Fuel']] = 1
    
    global user_input
    # putting the values into an array to feed into the machine learning algorithm
    user_input = [[
        trans_auto,
        trans_man,
        fuel_dict[fuel_list[0]],
        fuel_dict[fuel_list[1]],
        fuel_dict[fuel_list[2]],
        fuel_dict[fuel_list[3]],
        fuel_dict[fuel_list[4]],
        fuel_dict[fuel_list[5]],
        values['Mileage'],
        values['Size'],
        values['Power'],
        values['Age'],
        make_dict[cb_values['Make']],
        type_dict[cb_values['Bt']]
    ]]
    
    
    # loading the machine learning model from a saved file
    with open("randomforest_regressor2.pkl","rb") as file:
        loaded_model = pickle.load(file)
    
    # making the prediction using the model and array
    global prediction
    prediction = loaded_model.predict(user_input)  
    
def check_values():
    '''checks that the inputted values are numerical and within a reasonable range'''

    # creating the dictionaries that can be referred to in future
    global cb_values, values, status, cb_status, error_dict
    cb_values = {
        'Make': make_cb.get(),
        'Bt': bt_cb.get(),
        'Fuel': fuel_cb.get(),
        'Trans': trans_cb.get()
    }
    cb_status = {
        'Make': 3,
        'Bt': 3,
        'Fuel': 3,
        'Trans': 3
    }
    values = {
        'Age': age_entry.get(),
        'Mileage': milea_entry.get(),
        'Power': power_entry.get(),
        'Size': size_entry.get()
    }
    status = {
        'Age': 2,
        'Mileage': 2,
        'Power': 2,
        'Size': 2
    }
    error_dict = {
        0: 'Input is correct',
        1: 'Is not within a reasonable range',
        2: 'Is not a valid number',
        3: 'Is empty'
    }
    
    #checks that all the entry variables are valid
    
    # for the comboboxes, have they been filled in?
    for x in cb_status:
        if len(cb_values[x])==0:
            continue
        else:
            cb_status[x]=0
    
    # for the entry boxes, are they a number?
    
    # Age
    try:
        values['Age'] = round(float(values['Age']),1)
    except:
        status['Age'] = 2
    else:
        # age needs to be within 1-100
        if values['Age']<0 or values['Age']>max_age:
            status['Age']=1
        else:
            status['Age']=0
    
    # Mileage
    try:
        values['Mileage'] = round(float(values['Mileage']),1)
    except:
        status['Mileage'] = 2
    else:
        # Milage cannot be negative and more than 1 million
        if values['Mileage']<0 or values['Mileage']>max_milea:
            status['Mileage']=1
        else:
            status['Mileage']=0

    # Power
    try:
        values['Power'] = round(float(values['Power']),1)
    except:
        status['Power'] = 2
    else:
        # Power cant be negative and more than 1000
        if values['Power']<0 or values['Power']>max_power:
            status['Power']=1
        else:
            status['Power']=0

    # Engine size
    try:
        values['Size'] = round(float(values['Size']),1)
    except:
        status['Size'] = 2
    else:
        # Power cant be negative and more than 10
        if values['Size']<0 or values['Size']>max_size:
            status['Size']=1
        else:
            status['Size']=0
    
    # checks that all inputs are valid before moving onto the new frame
    if sum(status.values())==0:
        
        predict()
        
        global upper_price, lower_price
        upper_price = round(prediction[0]*(1+mae_perc))
        lower_price = round(prediction[0]*(1-mae_perc))
        
        load_frame2()
    else:
    # otherwise, run the error code to display whats wrong with the inputs
        error()    
      
def open_tool():
    '''Creates the conversion window with the tools inside'''
    conv_window = tk.Toplevel(frame1)
    conv_window.title("Conversion Tool")
    
    #creating the global variables so they can be used in the functions
    global km_entry, miles_label, ps_entry, bhp_label, cc_entry, litres_label
    
    # km to miles converter
    km_label = tk.Label(conv_window, text="Enter kilometres:")
    km_label.grid(row=0, column=0, padx=10, pady=10)
    
    km_entry = tk.Entry(conv_window,
                        width=15,
                       font=("Segoe UI", 14))
    km_entry.grid(row=0, column=1, padx=10, pady=10)
    
    miles_label = tk.Label(conv_window,width=15, text="")
    miles_label.grid(row=0, column=2, padx=10, pady=10)
    
    convert_button = tk.Button(conv_window, text="Convert to miles", command=convert_km_to_miles)
    convert_button.grid(row=1,column=1, padx=10, pady=10)
    
    # ps to bhp converter
    ps_label = tk.Label(conv_window, text="Enter PS:")
    ps_label.grid(row=2, column=0, padx=10, pady=10)
    
    ps_entry = tk.Entry(conv_window,
                        width=15,
                       font=("Segoe UI", 14))
    ps_entry.grid(row=2, column=1, padx=10, pady=10)
    
    bhp_label = tk.Label(conv_window,width=15, text="")
    bhp_label.grid(row=2, column=2, padx=10, pady=10)
    
    convert_button = tk.Button(conv_window, text="Convert to BHP", command=convert_ps_to_bhp)
    convert_button.grid(row=3,column=1, padx=10, pady=10)
    
    # cc to litres converter
    cc_label = tk.Label(conv_window, text="Enter cc:")
    cc_label.grid(row=4, column=0, padx=10, pady=10)
    
    cc_entry = tk.Entry(conv_window,
                        width=15,
                       font=("Segoe UI", 14))
    cc_entry.grid(row=4, column=1, padx=10, pady=10)
    
    litres_label = tk.Label(conv_window,width=15, text="")
    litres_label.grid(row=4, column=2, padx=10, pady=10)
    
    convert_button = tk.Button(conv_window, text="Convert to litres", command=convert_cc_to_litres)
    convert_button.grid(row=5,column=1, padx=10, pady=10)    
    
def error():
    '''Error message about invalid input variables and displays whats wrong'''
    er_win = tk.Toplevel(frame1)
    er_win.title('Error')
    
    # make status
    make_label = tk.Label(er_win, text='Make status:')
    make_label.grid(row=0, column=0, padx=10, pady=10)
    make_label2 = tk.Label(er_win, text=cb_values['Make'])
    make_label2.grid(row=0, column=1, padx=10, pady=10)
    make_status = tk.Label(er_win, text=error_dict[cb_status['Make']])
    make_status.grid(row=0, column=2, padx=10, pady=10)
    
    # bodytype status
    bt_label = tk.Label(er_win, text='Body type status:')
    bt_label.grid(row=1, column=0, padx=10, pady=10)
    bt_label2 = tk.Label(er_win, text=cb_values['Bt'])
    bt_label2.grid(row=1, column=1, padx=10, pady=10)
    bt_status = tk.Label(er_win, text=error_dict[cb_status['Bt']])
    bt_status.grid(row=1, column=2, padx=10, pady=10)
    
    # fuel status
    fuel_label = tk.Label(er_win, text='Fuel type status:')
    fuel_label.grid(row=2, column=0, padx=10, pady=10)
    fuel_label2 = tk.Label(er_win, text=cb_values['Fuel'])
    fuel_label2.grid(row=2, column=1, padx=10, pady=10)
    fuel_status = tk.Label(er_win, text=error_dict[cb_status['Fuel']])
    fuel_status.grid(row=2,column=2, padx=10, pady=10)
    
    # transmission status
    trans_label = tk.Label(er_win, text='Transmission status:')
    trans_label.grid(row=3, column=0, padx=10, pady=10)
    trans_label2 = tk.Label(er_win, text=cb_values['Bt'])
    trans_label2.grid(row=3, column=1, padx=10, pady=10)
    trans_status = tk.Label(er_win, text=error_dict[cb_status['Bt']])
    trans_status.grid(row=3, column=2, padx=10, pady=10)
    
    # age status
    age_label = tk.Label(er_win, text='Age status:')
    age_label.grid(row=4, column=0, padx=10, pady=10)
    age_label2 = tk.Label(er_win, text=values['Age'])
    age_label2.grid(row=4, column=1, padx=10, pady=10)
    age_status = tk.Label(er_win, text=error_dict[status['Age']])
    age_status.grid(row=4, column=2, padx=10, pady=10)
    
    # Mileage status
    milea_label = tk.Label(er_win, text='Mileage status:')
    milea_label.grid(row=5, column=0, padx=10, pady=10)
    milea_label2 = tk.Label(er_win, text=values['Mileage'])
    milea_label2.grid(row=5, column=1, padx=10, pady=10)
    milea_status = tk.Label(er_win, text=error_dict[status['Mileage']])
    milea_status.grid(row=5, column=2, padx=10, pady=10)
    
    # Power status
    power_label = tk.Label(er_win, text='Engine Power status:')
    power_label.grid(row=6, column=0, padx=10, pady=10)
    power_label2 = tk.Label(er_win, text=values['Power'])
    power_label2.grid(row=6, column=1, padx=10, pady=10)
    power_status = tk.Label(er_win, text=error_dict[status['Power']])
    power_status.grid(row=6, column=2, padx=10, pady=10)
    
    # Size status
    size_label = tk.Label(er_win, text='Engine Size status:')
    size_label.grid(row=7, column=0, padx=10, pady=10)
    size_label2 = tk.Label(er_win, text=values['Size'])
    size_label2.grid(row=7, column=1, padx=10, pady=10)
    size_status = tk.Label(er_win, text=error_dict[status['Size']])
    size_status.grid(row=7, column=2, padx=10, pady=10)
        
'''
The frames within the GUI that are displayed
'''
def load_frame1():
    '''function that loads the main interface'''
    clear_widgets(frame2)
    # stack frame 1 on top
    frame1.tkraise()
    # prevent widgets from modifying the frame
    frame1.pack_propagate(False)
    
    # title of the app
    title = tk.Label(frame1,
                     text="Car Valuation Tool",
                     bg=background,
                     fg="white",
                     font=("Rockwell", 50)
                    ).place(rely=0.05,relx=0.5,anchor=CENTER)


    # making the comboboxes and entries global so they can be referred to again in the future
    global make_cb, bt_cb, fuel_cb, trans_cb, age_entry, milea_entry, power_entry, size_entry
    
    # welcome message
    welcome = tk.Label(frame1, 
                          text=welcome_message,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.12,relx=0.5,anchor=CENTER)
    
    # Message that explains whats going on
    msg = tk.Label(frame1, 
                          text=explain,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.15,relx=0.5,anchor=CENTER)

    # Help tip about the conversion tool
    tip = tk.Label(frame1, 
                          text=stuck,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.18,relx=0.5,anchor=CENTER)
    
    
    # dropdown to choose car manufacturer
    choose_make = tk.Label(frame1, 
                          text=make_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.25,relx=0.2,anchor=CENTER)
    
    selected_make = tk.StringVar()
    make_cb = ttk.Combobox(frame1, 
                           textvariable=selected_make,
                           values=make_list,
                          state='readonly',
                          width=30)
    make_cb.place(rely=0.3,relx=0.2, anchor=CENTER)
    
    
    # dropdown to select the body type of the vehicle
    choose_bt = tk.Label(frame1, 
                          text=bt_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.4,relx=0.2,anchor=CENTER)
    
    selected_bt = tk.StringVar()
    bt_cb = ttk.Combobox(frame1, 
                           textvariable=selected_bt,
                           values=bt_list,
                          state='readonly',
                        width = 30)
    bt_cb.place(rely=0.45,relx=0.2, anchor=CENTER)
 
    
    # dropdown to choose fuel type of car
    choose_fuel = tk.Label(frame1, 
                          text=fuel_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.25,relx=0.5,anchor=CENTER)
    
    selected_fuel = tk.StringVar()
    fuel_cb = ttk.Combobox(frame1, 
                           textvariable=selected_fuel,
                           values=fuel_list,
                          state='readonly',
                          width=30)
    fuel_cb.place(rely=0.3,relx=0.5, anchor=CENTER)    
    
    
    # dropdown to select the transmission of the vehicle
    choose_trans = tk.Label(frame1, 
                          text=trans_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.4,relx=0.5,anchor=CENTER)
    
    selected_trans = tk.StringVar()
    trans_cb = ttk.Combobox(frame1, 
                           textvariable=selected_trans,
                           values=trans_list,
                          state='readonly',
                           width=30)

    trans_cb.place(rely=0.45,relx=0.5, anchor=CENTER)
    

    # Entering the age of the vehicle
    choose_year = tk.Label(frame1, 
                          text=age_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.25,relx=0.8,anchor=CENTER)
    
    age_entry = tk.Entry(frame1,
                         width=30,
                         font=("Segoe UI", 14)
                        )
    age_entry.place(rely=0.3,relx=0.8, anchor=CENTER)

    
    # Entering the mileage of the vehicle
    choose_milea = tk.Label(frame1, 
                          text=milea_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.4,relx=0.8,anchor=CENTER)
    
    milea_entry = tk.Entry(frame1,
                           width=30,
                           font=("Segoe UI", 14)
                          )
    milea_entry.place(rely=0.45,relx=0.8, anchor=CENTER)


    # Entering the power of the vehicle
    choose_power = tk.Label(frame1, 
                          text=power_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.55,relx=0.33,anchor=CENTER)
    
    power_entry = tk.Entry(frame1,
                           width=30,
                           font=("Segoe UI", 14)
                          )
    power_entry.place(rely=0.6,relx=0.33, anchor=CENTER)
    
    
    # Entering the engine size of the vehicle
    choose_size = tk.Label(frame1, 
                          text=size_msg,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 18)
                         ).place(rely=0.55,relx=0.66,anchor=CENTER)
    
    size_entry = tk.Entry(frame1,
                           width=30,
                           font=("Segoe UI", 14)
                          )
    size_entry.place(rely=0.6,relx=0.66, anchor=CENTER)
    
    
    # Button to open up converter tool
    conversion = ck.CTkButton(master=frame1,
                           width = 0.15*desc_width,
                           height = 0.15*desc_height,
                           text="Open conversion tools",
                           corner_radius = 0.01*desc_width,
                           fg_color = "#F18A00",
                           font = ("Rockwell",24),
                              command = open_tool
                          ).place(rely=0.75,relx=0.33, anchor=CENTER)
    
    # Button to continue onto next page
    next_page = ck.CTkButton(master=frame1,
                           width = 0.2*desc_width,
                           height = 0.15*desc_height,
                           text="Submit variables",
                           corner_radius = 0.01*desc_width,
                           fg_color = "#F18A00",
                           font = ("Rockwell",24),
                             command = check_values
                          ).place(rely=0.75,relx=0.66, anchor=CENTER)

def load_frame2():
    '''2nd page that displays results'''
    clear_widgets(frame1)
    # stack frame 2 
    frame2.tkraise()
    # prevent widgets from modifying the frame
    frame1.pack_propagate(False)
    
    # title of the app
    title = tk.Label(frame2,
                     text="Car Valuation Tool",
                     bg=background,
                     fg="white",
                     font=("Rockwell", 50)
                    ).place(rely=0.05,relx=0.5,anchor=CENTER)
    
    # displays the output from the machine learning algorithm
    
    # based on the inputted values of:
    # explanation message
    welcome = tk.Label(frame2, 
                          text=based,
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 30)
                         ).place(rely=0.15,relx=0.5,anchor=CENTER)
    
    # car make
    chosen_make = tk.Label(frame2, 
                          text=f'Car Make: {cb_values["Make"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.25,relx=0.2,anchor=CENTER)

    # body type
    chosen_bt = tk.Label(frame2, 
                          text=f'Body Type: {cb_values["Bt"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.25,relx=0.4,anchor=CENTER)
    
    # fuel type
    chosen_fuel = tk.Label(frame2, 
                          text=f'Fuel Type: {cb_values["Fuel"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.25,relx=0.6,anchor=CENTER)
    
    # transmission
    chosen_trans = tk.Label(frame2, 
                          text=f'Transmission: {cb_values["Trans"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.25,relx=0.8,anchor=CENTER)
    
    # Age
    chosen_age = tk.Label(frame2, 
                          text=f'Age (years): {values["Age"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.35,relx=0.2,anchor=CENTER)
    
    # milage
    chosen_milea = tk.Label(frame2, 
                          text=f'Mileage: {values["Age"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.35,relx=0.4,anchor=CENTER)
    
    # Engine Power
    chosen_power = tk.Label(frame2, 
                          text=f'Engine Power (BHP): {values["Age"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.35,relx=0.6,anchor=CENTER)
    
    # Engine Size
    chosen_size = tk.Label(frame2, 
                          text=f'Engine Size (Litres): {values["Size"]}',
                          bg = background,
                          fg = "white",
                          font=("Rockwell", 20)
                         ).place(rely=0.35,relx=0.8,anchor=CENTER)
    
    
    # result of algorithm is displayed here
    result_label = tk.Label(frame2, 
                      text=f'Estimated price: £{lower_price}-£{upper_price}',
                      bg = background,
                      fg = "white",
                      font=("Rockwell", 50)
                     ).place(rely=0.5,relx=0.5,anchor=CENTER)
    
    # back button to the original dataframe
    conversion = ck.CTkButton(master=frame2,
                           width = 0.15*desc_width,
                           height = 0.18*desc_height,
                           text="Back",
                           corner_radius = 0.01*desc_width,
                           fg_color = "#F18A00",
                           font = ("Rockwell",24),
                              command = load_frame1
                          ).place(rely=0.75,relx=0.38, anchor=E)
    
    # disclaimer message
    disclaimer_label = tk.Label(frame2, 
                      text=disclaimer,
                      bg = background,
                      fg = "white",
                      font=("Rockwell", 20)
                     ).place(rely=0.6,relx=0.5,anchor=CENTER)    

    # convert to dollars
    next_page = ck.CTkButton(master=frame2,
                           width = 0.2*desc_width,
                           height = 0.09*desc_height,
                           text="Convert to dollars",
                           corner_radius = 0.01*desc_width,
                           fg_color = "#F18A00",
                           font = ("Rockwell",24),
                             command = convert_us
                          ).place(rely=0.75,relx=0.5, anchor=N)

    # convert to euros
    next_page = ck.CTkButton(master=frame2,
                           width = 0.2*desc_width,
                           height = 0.09*desc_height,
                           text="Convert to euros",
                           corner_radius = 0.01*desc_width,
                           fg_color = "#F18A00",
                           font = ("Rockwell",24),
                             command = convert_eu
                          ).place(rely=0.75,relx=0.5, anchor=S)
    
    # conversion output is shown here
    global label
    label = tk.Label(frame2, 
                      text='Converted cost',
                      bg = background,
                      fg = "white",
                      font=("Rockwell", 40)
                     )
    label.place(rely=0.75,relx=0.65,anchor=W)
    
'''
Running code that starts the GUI
'''
# run the function to find the size before starting the window
get_display_size()

# generate the window
window = ck.CTk()

# fit the window onto the screen
window.geometry("%dx%d-12+0" % (desc_width, desc_height))
window.title("Autotrader Application")

# create frames
frame1 = tk.Frame(window,
                  width=desc_width*1.5,
                  height=desc_height*1.5,
                  bg=background)

frame2 = tk.Frame(window,
                  width=desc_width*1.5,
                  height=desc_height*1.5,
                  bg=background)

# placing the frame widget in the window
for frame in (frame1, frame2):
    frame.place(rely=0.5,relx=0.5, anchor = CENTER)

# load the first frame
load_frame1()

# run app
window.mainloop()
