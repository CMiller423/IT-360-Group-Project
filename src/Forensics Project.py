import tkinter as tk
from tkinter import ttk # For themed widgets (optional, but good practice)
import platform
import psutil
import netifaces

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

def get_active_processes():
    """
    Retrieves and prints the PID and name of all active processes.
    """
    print("Active Processes:")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def get_active_connections():
    """
    Retrieves and displays active network connections.
    """
    connections = psutil.net_connections(kind='inet')  # 'inet' for IPv4 and IPv6 connections
    
    print(f"{'Protocol':<10} {'Local Address':<25} {'Remote Address':<25} {'Status':<15} {'PID':<8} {'Process Name':<20}")
    print("-" * 105)

    for conn in connections:
        laddr_ip = conn.laddr.ip if conn.laddr else "N/A"
        laddr_port = conn.laddr.port if conn.laddr else "N/A"
        raddr_ip = conn.raddr.ip if conn.raddr else "N/A"
        raddr_port = conn.raddr.port if conn.raddr else "N/A"

        local_address = f"{laddr_ip}:{laddr_port}"
        remote_address = f"{raddr_ip}:{raddr_port}" if raddr_ip != "N/A" else "N/A"
        
        process_name = "N/A"
        if conn.pid:
            try:
                process = psutil.Process(conn.pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        print(f"{conn.type.name:<10} {local_address:<25} {remote_address:<25} {conn.status:<15} {str(conn.pid):<8} {process_name:<20}")

def show_routing_table():
    """
    Prints the routing table information using the netifaces library.
    """
    gws = netifaces.gateways()
    default_gateway = gws.get('default', {}).get(netifaces.AF_INET)

    if not default_gateway:
        print("Could not find default gateway information.")
        return

    default_gateway_ip, default_interface = default_gateway
    print(f"Default Gateway: {default_gateway_ip} via interface {default_interface}\n")

    print("{:<18} {:<18} {:<18}".format("Destination", "Gateway", "Interface"))
    print("-" * 54)

    for iface in netifaces.interfaces():
        try:
            for family, routes in netifaces.ifaddresses(iface).items():
                if family == netifaces.AF_INET:
                    for route in routes:
                        # netifaces routing information is not as complete as shell commands,
                        # so we focus on the most relevant details available.
                        addr = route.get('addr', 'N/A')
                        netmask = route.get('netmask', 'N/A')
                        print("{:<18} {:<18} {:<18}".format(addr, 'N/A', iface))
        except ValueError:
            # Some interfaces may not have an IPv4 address
            pass

# Create the main application window
root = tk.Tk()
root.title("System Tools")
root.geometry("300x300") # Set initial window size (width x height)

# Create a label widget
label = ttk.Label(root, text="Hello, World!")
label.pack(pady=20) # Pack the label into the window with some padding

# Create a button widget
button = ttk.Button(root, text="Get Info", command=button_click)
button.pack(pady=10) # Pack the button into the window with some padding

button2 = ttk.Button(root, text="Get Processes", command=get_active_processes)
button2.pack(pady=10) # Pack the button into the window with some padding

button3 = ttk.Button(root, text="Get Network Connections", command=get_active_connections)
button3.pack(pady=10) # Pack the button into the window with some padding

button4 = ttk.Button(root, text="Get ARP Table", command=show_routing_table)
button4.pack(pady=10) # Pack the button into the window with some padding

# Start the Tkinter event loop
root.mainloop()