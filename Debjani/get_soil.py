import tkinter as tk
import csv
import time
import msgpack
import subprocess
from datetime import datetime


def read_last_line():
    with open('/home/pi/Documents/Debjani/Soil/Soil_Type.txt', 'r') as f:
        lines = f.readlines()
    last_line = lines[-1].strip()
    app.value8_label.config(text=last_line)

def read_crop():
    with open('/home/pi/Documents/Debjani/Soil/crop.txt', 'r') as f:
        lines = f.readlines()
    last_line = lines[-1].strip()
    app.value10_label.config(text=last_line)

def read_fertilizer():
    with open('/home/pi/Documents/Debjani/Soil/fertilizer.txt', 'r') as f:
        lines = f.readlines()
    last_line = lines[-1].strip()
    app.value12_label.config(text=last_line)

def run_command1():
    folder_path = '/home/pi/Documents/Debjani/Soil/'
    command = "./stbash.sh"  # replace with your desired command
    subprocess.run(command, cwd=folder_path, shell=True)

def run_command2():
    folder_path = '/home/pi/Documents/Debjani/Soil/'
    command = "./btoarchive.sh"  # replace with your desired command
    subprocess.run(command, cwd=folder_path, shell=True)

def run_command3():
    folder_path = '/home/pi/Documents/Debjani/CropFertilizerPrediction/'
    command = "./crop_bash.sh"  # replace with your desired command
    subprocess.run(command, cwd=folder_path, shell=True)

def run_command4():
    folder_path = '/home/pi/Documents/Debjani/CropFertilizerPrediction/'
    command = "./fertilizer_bash.sh"  # replace with your desired command
    subprocess.run(command, cwd=folder_path, shell=True)

def shutdown():
    command = "sudo poweroff"
    subprocess.run(command, shell=True)

def deserialize(data):
   try:
      return msgpack.loads(data, unicode_errors='ignore')
   except Exception as e:
      print("error")
def run_processes():
    #run_command1()
    read_last_line()
    #run_command2()

def finalCrop():
    #run_command3()
    read_crop()

def finalFertilizer():
    #run_command4()
    read_fertilizer()

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Soil Health Monitoring")
        self.grid()
        self.create_widgets()

        # Set the interval (in seconds) for updating the labels
        self.update_interval = 5

    def create_widgets(self):
        # Create labels for the CSV data
        self.configure(bg="black")
        #self.label0 = tk.Label(self, text="Soil Health Monitoring Device",bg="black",fg="gr>
        #self.label0.grid(row=0, column=1, padx=25, pady=25, sticky=tk.W)

        self.label1 = tk.Label(self, text="Temperature(oC):",bg="black", fg="green2")
        self.label1.grid(row=1, column=0, padx=5, pady=3, sticky=tk.W)

        self.label2 = tk.Label(self, text="Moisture(%RH):",bg="black",fg="green2")
        self.label2.grid(row=2, column=0, padx=5, pady=3, sticky=tk.W)

        self.label3 = tk.Label(self, text="Nitrogen(mg/kg):",bg="black",fg="green2")
        self.label3.grid(row=3, column=0, padx=5, pady=3, sticky=tk.W)

        self.label4 = tk.Label(self, text="Phosphorous(mg/kg):",bg="black",fg="green2")
        self.label4.grid(row=4, column=0, padx=5, pady=3, sticky=tk.W)

        self.label5 = tk.Label(self, text="Potassium(mg/kg):",bg="black",fg="green2")
        self.label5.grid(row=5, column=0, padx=5, pady=3, sticky=tk.W)

        self.label6 = tk.Label(self, text="pH:",bg="black",fg="green2")
        self.label6.grid(row=6, column=0, padx=5, pady=3, sticky=tk.W)

        self.label7 = tk.Label(self, text="Electrical Conductivity(uS/cm):",bg="black",fg="green2")
        self.label7.grid(row=7, column=0, padx=5, pady=3, sticky=tk.W)

        # Create labels to display the CSV data
        self.value1_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value1_label.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

        self.value2_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value2_label.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)

        self.value3_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value3_label.grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)

        self.value4_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value4_label.grid(row=4, column=1, padx=5, pady=3, sticky=tk.W)

        self.value5_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value5_label.grid(row=5, column=1, padx=5, pady=3, sticky=tk.W)

        self.value6_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value6_label.grid(row=6, column=1, padx=5, pady=3, sticky=tk.W)

        self.value7_label = tk.Label(self, text="0",bg="black",fg="green2")
        self.value7_label.grid(row=7, column=1, padx=5, pady=3, sticky=tk.W)

        self.value8_label = tk.Label(self, text="N.A.", bg="black",fg="green2")
        self.value8_label.grid(row=8, column=1, padx=5, pady=3, sticky=tk.W)

        self.value9_label = tk.Label(self, text="Soil Type: ", bg="black",fg="green2")
        self.value9_label.grid(row=8, column=0, padx=5, pady=3, sticky=tk.W)

        self.value10_label = tk.Label(self, text="N.A.", bg="black",fg="green2")
        self.value10_label.grid(row=1, column=4, padx=5, pady=3, sticky=tk.W)

        self.value11_label = tk.Label(self, text="Crop Type: ", bg="black",fg="green2")
        self.value11_label.grid(row=1, column=3, padx=5, pady=3, sticky=tk.W)

        self.value12_label = tk.Label(self, text="N.A.", bg="black",fg="green2")
        self.value12_label.grid(row=2, column=4, padx=5, pady=3, sticky=tk.W)

        self.value13_label = tk.Label(self, text="Fertilizer: ", bg="black",fg="green2")
        self.value13_label.grid(row=2, column=3, padx=5, pady=3, sticky=tk.W)
        
        # Create a label for the date
        self.date_label = tk.Label(self, text="Date: ", bg="black", fg="green2")
        self.date_label.grid(row=3, column=3, padx=5, pady=3, sticky=tk.W)

        # Create a label to display the current date
        self.current_date_label = tk.Label(self, text=self.get_current_date(), bg="black", fg="green2")
        self.current_date_label.grid(row=3, column=4, padx=5, pady=3, sticky=tk.W)
        # Create a label for the time
        self.time_label = tk.Label(self, text="Time: ", bg="black", fg="green2")
        self.time_label.grid(row=4, column=3, padx=5, pady=3, sticky=tk.W)

        # Create a label to display the current time
        self.current_time_label = tk.Label(self, text=self.get_current_time(), bg="black", fg="green2")
        self.current_time_label.grid(row=4, column=4, padx=5, pady=3, sticky=tk.W)
        
         # Create a label for the Battery Percent field
        self.battery_label = tk.Label(self, text="Battery Percent:", bg="black", fg="green2")
        self.battery_label.grid(row=5, column=3, padx=5, pady=3, sticky=tk.W)

        # Create a label to display the current battery percentage value
        self.current_battery_label = tk.Label(self, text="0%", bg="black", fg="green2")
        self.current_battery_label.grid(row=5, column=4, padx=5, pady=3, sticky=tk.W)

        # Update the time label every second
        self.update_time()
        # Start updating the battery percentage periodically
        self.update_battery_percent()
        

# Create a button to quit the application
        self.quit_button = tk.Button(self, text="ShutDown",bg="green2",fg="black", command=shutdown)
        self.quit_button.grid(row=8, column=4, padx=5, pady=3, sticky=tk.S)

        # Create a button to quit the application
        self.soil_button = tk.Button(self, text="Soil",bg="green2",fg="black", command=run_processes)
        self.soil_button.grid(row=8, column=3, padx=5, pady=3, sticky=tk.S)

        self.crop_button = tk.Button(self, text="Crop",bg="green2",fg="black", command=finalCrop)
        self.crop_button.grid(row=7, column=3, padx=5, pady=3, sticky=tk.S)

        self.fertilizer_button = tk.Button(self, text="Fertilizer",bg="green2",fg="black", command=finalFertilizer)
        self.fertilizer_button.grid(row=7, column=4, padx=5, pady=3, sticky=tk.S)

        self.quit1_button = tk.Button(self, text="Quit",bg="green2",fg="black", command=self.master.quit)
        self.quit1_button.grid(row=6, column=4, padx=5, pady=3, sticky=tk.S)

    def get_current_date(self):
        """Return the current date as a string."""
        return datetime.now().strftime("%d-%m-%Y")

    def get_current_time(self):
        """Return the current time as a string."""
        return datetime.now().strftime("%H:%M:%S")

    def update_time(self):
        """Update the current time label every second."""
        current_time = self.get_current_time()
        self.current_time_label.config(text=current_time)

        # Update the date (in case the day changes at midnight)
        current_date = self.get_current_date()
        self.current_date_label.config(text=current_date)
        self.master.after(1000, self.update_time)  # Schedule the update every 1000ms (1 second)
    def update_battery_percent(self):
        try:
            # Read the latest battery percentage from the file
            with open("/home/pi/Documents/Debjani/UPS_HAT_D/latest_percentage.txt", "r") as file:
                percent = file.readline().strip()
        except FileNotFoundError:
            percent = "N/A"  # Handle missing file case

        # Update the label with the latest percentage value
        self.current_battery_label.config(text=f"{percent}%")

        # Schedule the next update in 2 seconds
        self.after(2000, self.update_battery_percent)
    def update_labels(self):
     try:
        # Read the CSV file and update the label values
        with open('/home/pi/Documents/Debjani/testing.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                # Check if the row has exactly 7 columns
                if len(row) == 7:
                    try:
                        # Validate and convert each value
                        values = [float(value) for value in row if self.is_valid_number(value)]

                        # Ensure we have exactly 7 valid values
                        if len(values) == 7:
                            # Update labels with valid values
                            self.value1_label.config(text="{:.2f}".format(values[0]))
                            self.value2_label.config(text="{:.2f}".format(values[1]))
                            self.value3_label.config(text="{:.2f}".format(values[2]))
                            self.value4_label.config(text="{:.2f}".format(values[3]))
                            self.value5_label.config(text="{:.2f}".format(values[4]))
                            self.value6_label.config(text="{:.2f}".format(values[5]))
                            self.value7_label.config(text="{:.2f}".format(values[6]))
                        else:
                            print(f"Row does not contain 7 valid numbers: {row}")
                            self.set_default_values()
                    except ValueError as e:
                        # Handle conversion errors
                        print(f"Non-numeric data in row: {row}, Error: {e}")
                        self.set_default_values()
                else:
                    # Handle rows with incorrect column counts
                    print(f"Invalid row length: {row}")
                    self.set_default_values()
     except FileNotFoundError:
        print("File not found: testing.csv")
        self.set_default_values()

    # Schedule the next update
     self.after(self.update_interval * 1000, self.update_labels)
    def is_valid_number(self, value):
     """Check if a string is a valid float or integer."""
     try:
        float(value)
        return True
     except ValueError:
        return False
    def set_default_values(self):
     """Set default values for all labels."""
     self.value1_label.config(text="0")
     self.value2_label.config(text="0")
     self.value3_label.config(text="0")
     self.value4_label.config(text="0")
     self.value5_label.config(text="0")
     self.value6_label.config(text="0")
     self.value7_label.config(text="0")
"""
    def update_labels(self):
          # Read the CSV file and update the label values
        with open('/home/pi/Documents/Debjani/testing.csv') as f:
            reader = csv.reader(f)
            #next(reader) # Skip the header row
            values = []
            for row in reader:
                print(deserialize(row))
                if (len(row)) == 7:
                    # print("Hello")
                    # if not isinstance(row, (int, float)):
                    #     print("Ohh")
                    #     break
                    # else:
                    print(type(row))
                    values = list(map(float, row)) # Convert values to float
                    self.value1_label.config(text="{:.2f}".format(values[0]))
                    self.value2_label.config(text="{:.2f}".format(values[1]))
                    self.value3_label.config(text="{:.2f}".format(values[2]))
                    self.value4_label.config(text="{:.2f}".format(values[3]))
                    self.value5_label.config(text="{:.2f}".format(values[4]))
                    self.value6_label.config(text="{:.2f}".format(values[5]))
                    self.value7_label.config(text="{:.2f}".format(values[6]))
                else:
                    print("World")
                    self.value1_label.config(text="0")
                    self.value2_label.config(text="0")
                    self.value3_label.config(text="0")
                    self.value4_label.config(text="0")
                    self.value5_label.config(text="0")
                    self.value6_label.config(text="0")
                    self.value7_label.config(text="0")

        # Schedule the next update
        self.after(self.update_interval*1000, self.update_labels)
"""
if __name__ == '__main__':
    root = tk.Tk()
    root.configure(bg="black")
    root.attributes('-fullscreen', True)
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("%dx%d" % (width, height))
    root.title("Soil Health Monitoring Device")
    label = tk.Label(root, text="Soil Health Monitoring Device",bg="black",fg="green2",font=('Courier',18,"bold"))
    label.grid(row=0, column=0, padx=25, pady=15, sticky=tk.E)
    app = App(master=root)
    app.update_labels() # Start the label updating process
    root.mainloop()
