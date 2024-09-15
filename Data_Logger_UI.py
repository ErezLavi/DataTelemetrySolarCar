# import serial
# import concurrent.futures
import tkintermapview
import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime, date
import time
import threading
import random
import queue
import plotting


bg_color = "#cccccc"         # Light gray
label_bg_color = "#bbbbbb"   # Slightly darker gray
header_bg_color = "#021526"  # Dark blue

# Create the main GUI window
root = tk.Tk()
root.title("Serial Data Logger")
root.geometry("1300x750")
global after_id

################################# Map view ############################################
# Create a frame for the map view
map_frame = ttk.Frame(root)

# Initialize stop_event
stop_event = threading.Event()
rand_position_list = [(32.113582, 34.817434)]


def show_map_view():
    if plot_frame.winfo_ismapped():  # If the plot frame is currently shown
        plot_frame.pack_forget()     # Hide the plot frame
        map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        show_map()


def show_map():
    global rand_position_list
    map_widget = tkintermapview.TkinterMapView(map_frame, width=1300, height=600)
    map_widget.pack(side=tk.RIGHT, padx=5, pady=10)
    # Set initial position (Afeka college, TLV)
    center_lat, center_lng = 32.113582, 34.817434
    map_widget.set_position(center_lat, center_lng)

    demo_path = map_widget.set_path(rand_position_list, color="#021526", width=8)
    # Periodically update the path
    def update_path():
        if not stop_event.is_set():
            demo_path.set_position_list(rand_position_list)
            map_widget.after(1000, update_path)  # Schedule next update

    update_path()  # Start updating path


def generate_random_gps_line():
    global rand_position_list
    current_lat, current_lng = rand_position_list[-1]
    lng_step = 0.0001

    while not stop_event.is_set():
        current_lng += lng_step
        rand_position_list.append((current_lat, current_lng))
        time.sleep(1)  # Update position every 1 second


def close_map():
    for widget in map_frame.winfo_children():
        widget.destroy()

########################################################################################


def create_header_frame(rt, header_bg, background_color):
    header_f = tk.Frame(rt, bg=header_bg, relief="solid", bd=1)
    header_f.pack(fill=tk.X, padx=5, pady=5, ipady=10)

    create_header_label(header_f, header_bg_color, background_color)
    create_header_buttons(header_f)

    return header_f


def create_header_label(header_f, header_bg, background_color):
    header_label = tk.Label(header_f, text="Serial Data Logger", font=("Arial", 20),
                            background=header_bg, fg=background_color)
    header_label.pack(side=tk.LEFT, padx=10)


def create_header_buttons(header_f):
    button_trip_analysis = ttk.Button(header_f, text="Trip analysis")
    button_trip_analysis.pack(side=tk.RIGHT, padx=15)

    button_gps = ttk.Button(header_f, text="GPS", command=show_map_view)
    button_gps.pack(side=tk.RIGHT, padx=15)

    button_data = ttk.Button(header_f, text="Data", command=show_plot_view)
    button_data.pack(side=tk.RIGHT, padx=15)


def create_data_frame(rt):
    data_f = ttk.Frame(rt)
    data_f.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
    return data_f


def create_plot_frame(rt):
    plot_f = ttk.Frame(rt)
    plot_f.pack(fill=tk.BOTH, expand=True, padx=5)
    return plot_f


def show_plot_view():
    if map_frame.winfo_ismapped():  # If the map frame is currently shown
        map_frame.pack_forget()      # Hide the map frame
        close_map()
    plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)


header_frame = create_header_frame(root, header_bg_color, bg_color)
data_frame = create_data_frame(root)
plot_frame = create_plot_frame(root)


# Data column labels
column_labels = ["Timestamp", "Ah", "Voltage (V)", "Current (A)", "Power (Watt)", "Speed (m/s)",
                 "Distance (m)", "Degree (°)", "RPM (Rounds/Minute)", "ThO", "ThI",
                 "AuxA", "AuxD", "Flgs"]

value_labels = []
plot_buttons = []


def create_labels_and_buttons(d_frame, c_label, v_labels, plot_buttons, label_bg_color, bg_color):
    for i, label_text in enumerate(c_label):
        # Create label for the column header
        label = ttk.Label(d_frame, text=label_text, font=("Arial", 12, "bold"), background=label_bg_color)
        label.grid(row=0, column=i, padx=3, pady=5, sticky="ew")

        if i != 0:  # Exclude the timestamp label
            # Create label for the data value
            value_label = ttk.Label(d_frame, text="", font=("Arial", 12), background=bg_color)
            value_label.grid(row=1, column=i, padx=5, pady=5, sticky="ew")
            v_labels.append(value_label)

            # Create button for plotting
            plot_button = ttk.Button(d_frame, text="Plot", state=tk.DISABLED, width=8,
                                     command=lambda i=i: plotting.enable_plotting(i, plot_frame, csv_filename,
                                                                                  column_labels, close_plot_button))

            plot_button.grid(row=2, column=i, padx=5, pady=5, sticky="ew")
            plot_buttons.append(plot_button)

    # Create a timestamp label
    ts_label = ttk.Label(d_frame, text="", font=("Arial", 12), background=bg_color)
    ts_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    return ts_label


timestamp_label = create_labels_and_buttons(data_frame, column_labels,
                                            value_labels, plot_buttons, label_bg_color, bg_color)


def create_csv_file():
    current_date = date.today().strftime("%Y-%m-%d")
    csv_name = f"serial_data_{current_date}.csv"
    with open(csv_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='\t')
        csv_writer.writerow(column_labels)
    return csv_name


csv_filename = create_csv_file()

# Queue to store data for updating the GUI
data_queue = queue.Queue()

################################# Serial Data ############################################
def generate_random_serial_data():
    while not stop_event.is_set():
        # Generate random values for each column except timestamp
        serial_data = [
            round(random.uniform(0.1, 5.0), 2),  # Ah
            round(random.uniform(10.0, 20.0), 2),  # Voltage (V)
            round(random.uniform(0.5, 10.0), 2),  # Current (A)
            round(random.uniform(0.0, 100.0), 2),  # Speed (m/s)
            round(random.uniform(0.0, 1000.0), 2),  # Distance (m)
            round(random.uniform(25, 32), 2),  # Degree (°)
            round(random.uniform(0.0, 5000.0), 2),  # RPM
            round(random.uniform(0.0, 1.0), 2),  # ThO
            round(random.uniform(0.0, 1.0), 2),  # ThI
            round(random.uniform(0.0, 1.0), 2),  # AuxA
            round(random.uniform(0.0, 1.0), 2),  # AuxD
            random.randint(0, 255)  # Flgs
        ]

        # Calculate power and insert it into the correct position
        timestamp = datetime.now().strftime("%H:%M:%S")
        current, voltage = serial_data[2], serial_data[1]
        power = round(current * voltage, 2)
        serial_data.insert(0, timestamp)
        serial_data.insert(4, power)
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_data_writer = csv.writer(csvfile, delimiter='\t')
            csv_data_writer.writerow(serial_data)

        data_queue.put(serial_data)
        time.sleep(1)  # Simulate a 1-second delay between data readings


################################# GUI Update ############################################
def update_gui():
    global after_id
    if not stop_event.is_set():
        # Update the timestamp label
        current_time = datetime.now().strftime("%H:%M:%S")
        timestamp_label.config(text=current_time)

        # Update the GUI from the queue
        try:
            data = data_queue.get_nowait()
            for i in range(min(len(data), len(value_labels))):
                value_labels[i].config(text=data[i + 1])  # Skip the timestamp value
                plot_buttons[i].config(state=tk.NORMAL)
        except queue.Empty:
            pass
        except tk.TclError:
            return  # Stop updating if there's a TclError (e.g., when closing the GUI)

        # Schedule the next update
        after_id = root.after(1000, update_gui)  # Update every 1 second (1000 milliseconds)


close_plot_button = ttk.Button(root, text="Close Plot", command=lambda: plotting.close_plot(plot_frame))

# Start the serial data reading in a separate thread
serial_thread = threading.Thread(target=generate_random_serial_data)
serial_thread.daemon = True  # Exit the thread when the main program exits
serial_thread.start()

# Start the GPS data reading in a separate thread
gps_thread = threading.Thread(target=generate_random_gps_line)
gps_thread.daemon = True
gps_thread.start()


def on_close():
    stop_event.set()             # Set the stop event to exit the thread
    serial_thread.join()         # Wait for the thread to finish
    root.after_cancel(after_id)  # Cancel the timestamp update
    root.quit()


update_gui()

root.protocol("WM_DELETE_WINDOW", on_close)

# Start the main GUI loop
root.mainloop()


