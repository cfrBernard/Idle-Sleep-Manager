import subprocess
import threading
from pynput import keyboard, mouse
import tkinter as tk
from tkinter import ttk

def sleep_computer():

    # Windows - This command is only valid for Windows
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "Sleep"])

    # ------------------------
    # The following commands are commented out because they only work on Linux or macOS:
    # - Linux: systemctl suspend
    # - macOS: pmset sleepnow
    # Uncomment these lines if you are using another system and want to test:
    #
    # Command to put the computer to sleep on Linux:
    # subprocess.run(["systemctl", "suspend"], check=True)
    #
    # Command to put the computer to sleep on macOS:
    # subprocess.run(["pmset", "sleepnow"], check=True)
    #
    # ------------------------
    
    root.destroy()

# Global variables
counter = 0
timeout = 300  # Default timeout is 5 minutes
listening_thread = None  
stop_event = threading.Event()

# Function to monitor events
def on_event(x=None, y=None, key=None):
    global counter
    counter = 0

# Function to update the timeout
def update_timeout(event):
    global timeout
    selected_duration = timeout_combobox.get()
    timeout_map = {
        "5 min": 5 * 60,
        "15 min": 15 * 60,
        "30 min": 30 * 60,
        "1 h": 1 * 60 * 60,
        "2 h": 2 * 60 * 60,
        "3 h": 3 * 60 * 60,
        "4 h": 4 * 60 * 60,
        "5 h": 5 * 60 * 60
    }
    timeout = timeout_map.get(selected_duration, 300)
    print(f"Timeout updated to {timeout} seconds.")

# Function to start listening for events
def start_listening():
    global timeout, counter, listening_thread, keyboard_listener, mouse_listener
    stop_event.clear()  
    counter = 0  

    # Create listeners for keyboard and mouse
    keyboard_listener = keyboard.Listener(on_press=on_event)
    mouse_listener = mouse.Listener(on_move=on_event)

    # Start listeners in a separate thread
    keyboard_listener.start()
    mouse_listener.start()

    # Check to avoid creating multiple threads
    if listening_thread is None or not listening_thread.is_alive():
        listening_thread = threading.Thread(target=listen_for_inactivity)
        listening_thread.daemon = True  
        listening_thread.start()

# Function to monitor inactivity in a separate thread
def listen_for_inactivity():
    global timeout, counter
    while not stop_event.is_set():
        stop_event.wait(timeout=5)  # Wait 5 seconds
        counter += 5  # Increment by 5 seconds
        print(f"Counter: {counter} seconds")
        if counter >= timeout:
            print(f"Inactivity time exceeded ({timeout} seconds). Putting the computer to sleep...")
            sleep_computer()
            stop_listening()  
            break

# Function to stop listening for events
def stop_listening():
    stop_event.set()  # Signal to stop the threads
    if listening_thread and listening_thread.is_alive():
        listening_thread.join()  # Wait for the thread to finish
    if 'keyboard_listener' in globals() and keyboard_listener:
        keyboard_listener.stop()  # Stop the keyboard listener
    if 'mouse_listener' in globals() and mouse_listener:
        mouse_listener.stop()  # Stop the mouse listener

# Tkinter Interface
root = tk.Tk()
root.title("Inactivity Monitoring")

# Create widgets
timeout_label = ttk.Label(root, text="Choose the timeout:")
timeout_label.grid(row=0, column=0, padx=10, pady=10)

# Dropdown menu for predefined durations
timeout_options = ["5 min", "15 min", "30 min", "1 h", "2 h", "3 h", "4 h", "5 h"] 
timeout_combobox = ttk.Combobox(root, values=timeout_options, state="readonly")
timeout_combobox.set(timeout_options[0])  # Default to 5 minutes
timeout_combobox.grid(row=0, column=1, padx=10, pady=10)

timeout_combobox.bind("<<ComboboxSelected>>", update_timeout)

start_listening()
root.mainloop()
