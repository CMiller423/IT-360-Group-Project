import tkinter as tk
from tkinter import ttk # For themed widgets (optional, but good practice)
import platform
import psutil

def button_click():
    """Function to be executed when the button is clicked."""
    label.config(text="Button Clicked!")
    print(f"System: {platform.system()}")
    print(f"Node Name: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Platform: {platform.platform()}")


    # CPU Information
    print("\nCPU Information:")
    print(f"Physical Cores: {psutil.cpu_count(logical=False)}")
    print(f"Total Cores (Logical): {psutil.cpu_count(logical=True)}")
    print(f"CPU Usage (%): {psutil.cpu_percent(interval=1)}")
    

    # Memory Information
    print("\nMemory Information:")
    memory = psutil.virtual_memory()
    print(f"Total Memory: {memory.total / (1024**3):.2f} GB")
    print(f"Available Memory: {memory.available / (1024**3):.2f} GB")
    print(f"Used Memory: {memory.used / (1024**3):.2f} GB")
    print(f"Memory Usage (%): {memory.percent}")
    print(f"Memory Usage (%): {psutil.pids}")

    # Disk Information
    print("\nDisk Information:")
    disk_usage = psutil.disk_usage('/') # For root directory on Linux/macOS, or C:\ on Windows
    print(f"Total Disk Space: {disk_usage.total / (1024**3):.2f} GB")
    print(f"Used Disk Space: {disk_usage.used / (1024**3):.2f} GB")
    print(f"Free Disk Space: {disk_usage.free / (1024**3):.2f} GB")
    print(f"Disk Usage (%): {disk_usage.percent}")

# Create the main application window
root = tk.Tk()
root.title("Simple GUI")
root.geometry("300x150") # Set initial window size (width x height)

# Create a label widget
label = ttk.Label(root, text="Hello, World!")
label.pack(pady=20) # Pack the label into the window with some padding

# Create a button widget
button = ttk.Button(root, text="Click Me", command=button_click)
button.pack(pady=10) # Pack the button into the window with some padding

# Start the Tkinter event loop
root.mainloop()