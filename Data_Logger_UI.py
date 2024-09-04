# import serial
# import concurrent.futures
import tkintermapview
import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime, date
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import threading
import random
import queue


bg_color = "#cccccc"         # Light gray
label_bg_color = "#bbbbbb"   # Slightly darker gray
header_bg_color = "#021526"  # Dark blue

# Create the main GUI window
root = tk.Tk()
root.title("Serial Data Logger")
root.geometry("1300x750")

################################# Map view ############################################
# Create a frame for the map view
map_frame = ttk.Frame(root)


def show_map_view():
    if plot_frame.winfo_ismapped():  # If the plot frame is currently shown
        plot_frame.pack_forget()     # Hide the plot frame
        map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        show_map()


def show_map():
    map_widget = tkintermapview.TkinterMapView(map_frame, width=1300, height=600)
    map_widget.pack(side=tk.RIGHT, padx=5, pady=10)
    map_widget.set_position(32.113582, 34.817434) # Tel aviv, israel
    #Set a path on the map
    rand_position_list = [(32.113582, 34.817434), (32.113593, 34.817635), (32.113483, 34.818596)]
    demo_path = map_widget.set_path(rand_position_list, color="#021526", width=8)
    demo_path.set_position_list(rand_position_list)


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
                                     command=lambda i=i: enable_plotting(i))
            plot_button.grid(row=2, column=i, padx=5, pady=5, sticky="ew")
            plot_buttons.append(plot_button)

    # Create a timestamp label
    ts_label = ttk.Label(d_frame, text="", font=("Arial", 12), background=bg_color)
    ts_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    return ts_label


timestamp_label = create_labels_and_buttons(data_frame, column_labels,
                                            value_labels, plot_buttons, label_bg_color, bg_color)

# Create a stop event for the thread
stop_event = threading.Event()


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


################################# Plot view ############################################
# Define global variables for plotting data
global plot_index, fig, ax, ani


def animate(i):
    data = []
    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        next(reader)  # Skip header row
        for row in reader:
            data.append(row)

    if data:
        y_values = [float(row[plot_index]) for row in data]

        # Filter to the last 60 seconds of data
        if len(y_values) > 60:
            y_values = y_values[-60:]

        # Generate x-values from 60 to 0 (assuming 1 second intervals)
        x_values = list(range(60 - len(y_values), 60))

        ax.clear()
        ax.plot(x_values, y_values, label=column_labels[plot_index])
        ax.legend(loc='upper left')
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel(column_labels[plot_index])
        ax.set_title(f"{column_labels[plot_index]} vs Time")

        # Set the x-axis limit to 0-60
        ax.set_xlim([0, 60])

        # Set x-ticks to every 10 seconds
        ax.set_xticks(range(0, 61, 10))  # Ticks at 0, 10, 20, ..., 60

        # Add gridlines at every 10 seconds
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)


def enable_plotting(index):
    global plot_index, fig, ax, ani
    plot_index = index

    # Close any existing plot before opening a new one
    close_plot()

    # Create a new figure and axis for the new plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ani = FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

    # Show the close plot button
    close_plot_button.pack(side=tk.BOTTOM, pady=15)


def close_plot():
    for widget in plot_frame.winfo_children():
        widget.destroy()
        # Hide the plot button after closing the plot
        close_plot_button.pack_forget()


close_plot_button = ttk.Button(root, text="Close Plot", command=close_plot)

# Start the serial data reading in a separate thread
serial_thread = threading.Thread(target=generate_random_serial_data)
serial_thread.daemon = True  # Exit the thread when the main program exits
serial_thread.start()


def on_close():
    stop_event.set()             # Set the stop event to exit the thread
    serial_thread.join()         # Wait for the thread to finish
    root.after_cancel(after_id)  # Cancel the timestamp update
    root.quit()


update_gui()

root.protocol("WM_DELETE_WINDOW", on_close)

# Start the main GUI loop
root.mainloop()


