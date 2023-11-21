from pyboy import PyBoy, WindowEvent
from PIL import Image
import time
import threading, queue
import os
import re


from GPThandler import *
from logger import append_to_file

def split_goals(text):
    return [item.split('. ', 1)[1] for item in text.split('\n') if '. ' in item]


def process_button_sequence(goals):
    pattern = r"\[\[.*?\]\]"
    match = re.search(pattern, goals)
    
    if match:
        s = match.group(0)  # Returns the found button sequence
    else:
        print("no button sequence found")
        return

    # Mapping from button names to press and release variables
    button_map = {
        "UP": (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
        "DOWN": (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
        "LEFT": (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
        "RIGHT": (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
        "A": (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
        "B": (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
        "SELECT": (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT),
        "START": (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START)
    }

    # Remove square brackets and split by space to get individual button commands
    commands = s.strip("[]").split()

    # Create a list to hold the sequence of press and release commands
    button_sequence = []

    for command in commands:
        if command in button_map:
            # Add press and release commands to the sequence
            press, release = button_map[command]
            button_sequence.append(press)
            button_sequence.append(release)

    return button_sequence

def remove_button_sequence_and_following(text):
    # Regular expression pattern to find the line starting with "BUTTON-SEQUENCE:" and everything after
    pattern = r"BUTTON-SEQUENCE:.*\[\[.*?\]\](.|\s)*"
    modified_text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    return modified_text

def update_screenshots(pyboy):
    # Check if the minus_two screenshot exists and remove it
    if os.path.exists("minus_two.jpg"):
        os.remove("minus_two.jpg")

    # Rename minus_one to minus_two if it exists
    if os.path.exists("minus_one.jpg"):
        os.rename("minus_one.jpg", "minus_two.jpg")

    # Rename previous to minus_one if it exists
    if os.path.exists("previous_vision.jpg"):
        os.rename("previous_vision.jpg", "minus_one.jpg")

    # Rename current to previous
    if os.path.exists("current_vision.jpg"):
        os.rename("current_vision.jpg", "previous_vision.jpg")

    # Take a new screenshot and save it as current
    screenshot = pyboy.screen_image()
    screenshot.save("current_vision.jpg", "JPEG")

    # Trigger any event if necessary (e.g., for synchronization)
    if screenshot_event:
        screenshot_event.set()

q = queue.Queue()

screenshot_event = threading.Event()


def comms():
    no_command_count = 0 
    screenshot_event.wait()
    screenshot_event.clear()
    goals = request_initial_goals("current_vision.jpg")
    while True:
        sequence = process_button_sequence(goals)
        if sequence:
            no_command_count = 0
            for command in sequence:
                q.put(command)  # Put the command in the queue
                # Add a sleep for 0.3 seconds for press and 2 second for release
                time.sleep(0.3 if command <= 8 else 2)
        else:
            no_command_count += 1
        
        if no_command_count == 2:
            append_to_file("NO COMMANDS SENT FOR 2 SEQUENCES IN A ROW")
            break
        q.put("SCREENSHOT")
        screenshot_event.wait()
        screenshot_event.clear()
        goals = request_progress_update("minus_two.jpg", "minus_one.jpg", "previous_vision.jpg", "current_vision.jpg", goals)


def run_pyboy():
    # Path to your Pokemon Red ROM
    rom_path = 'Pokemon Red.gb'

    # Initializing PyBoy with the ROM
    pyboy = PyBoy(rom_path, sound=True)
    pyboy.set_emulation_speed(0)  # Set this to 0 for unbounded speed

    for _ in range(1400):
        pyboy.tick()

    pyboy.set_emulation_speed(1)

    screenshot = pyboy.screen_image()
    screenshot.save("minus_two.jpg", "JPEG")
    screenshot.save("minus_one.jpg", "JPEG")
    screenshot.save("previous_vision.jpg", "JPEG")
    screenshot.save("current_vision.jpg", "JPEG")
    screenshot_event.set()

    while not pyboy.tick():
        try:
            command = q.get(block=False)
            print("sending command", command)
            if command == "SCREENSHOT":
                update_screenshots(pyboy)
            else:
                pyboy.send_input(command)
        except queue.Empty:
            pass
    pyboy.stop()



# Start the game in a separate thread
pyboy_thread = threading.Thread(target=run_pyboy)
pyboy_thread.start()

# Start the comms thread to send button sequences
comms_thread = threading.Thread(target=comms)
comms_thread.start()