import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

global plot_index, fig, ax, ani


def animate(i, csv_filename, column_labels):
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
        ax.set_xticks(range(0, 61, 10))

        # Add gridlines at every 10 seconds
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)


def enable_plotting(index, plot_frame, csv_filename, column_labels, close_plot_button):
    global plot_index, fig, ax, ani
    plot_index = index

    # Close any existing plot before opening a new one
    close_plot(plot_frame, close_plot_button)

    # Create a new figure and axis for the new plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ani = FuncAnimation(fig, animate, fargs=(csv_filename, column_labels), interval=1000, cache_frame_data=False)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

    # Show the close plot button
    close_plot_button.pack(side=tk.BOTTOM, pady=15)


def close_plot(plot_frame, close_plot_button):
    for widget in plot_frame.winfo_children():
        widget.destroy()
    if close_plot_button:
        close_plot_button.pack_forget()

