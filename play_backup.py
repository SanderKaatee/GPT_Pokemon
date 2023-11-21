from pyboy import PyBoy, WindowEvent
from PIL import Image
import time
import threading, queue
import os


from GPThandler import *
from logger import append_to_file

def split_goals(text):
    return [item.split('. ', 1)[1] for item in text.split('\n') if '. ' in item]


def process_button_sequence(s):
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


q = queue.Queue()

screenshot_event = threading.Event()


def comms():
    vision = '''The image features the title screen from a classic video game. It shows the word "Pok�mon" in a stylized font, followed by "Red Version" underneath. There's an illustration of a fictional creature, which looks like a turtle with a plant bulb on its back, and a character that appears to be a young male trainer wearing a cap and a backpack. Below the illustrations, there's a copyright notice with the years 1995, 1996, and 1998, followed by "GAME FREAK inc." indicating the company responsible for its development.'''
    medium_term_goals = split_goals(request_goal("medium-term goal", vision, "to defeat the Final Four"))
    short_term_goals = split_goals(request_goal("short-term goal", vision, medium_term_goals[0]))
    tasks = split_goals(request_goal("task", vision, short_term_goals[0]))
    while True:
        steps = split_goals(request_goal("step", vision, tasks[0]))
        print(steps)
        button_sequence = request_button_sequence(vision, steps, tasks[0])
        sequence = process_button_sequence(button_sequence)

        for command in sequence:
            q.put(command)  # Put the command in the queue
            # Add a sleep for 0.3 seconds for press and 2 second for release
            time.sleep(0.3 if command <= 8 else 2)
        q.put("SCREENSHOT")
        screenshot_event.wait()
        screenshot_event.clear()
        vision = request_image_content("current_vision.jpg")
        completed_tasks = split_goals(verify_task_completion("previous_vision.jpg", "current_vision.jpg", tasks))
        if completed_tasks == None:
            pass
        else:
            remaining_tasks = [task for task in tasks if task not in completed_tasks]
            tasks = split_goals(request_goal("task", vision, short_term_goals[0], tasks[0], completed_tasks))





def run_pyboy():
    # Path to your Pokemon Red ROM
    rom_path = 'Pokemon Red.gb'

    # Initializing PyBoy with the ROM
    pyboy = PyBoy(rom_path, sound=True)
    pyboy.set_emulation_speed(0)  # Set this to 0 for unbounded speed

    for _ in range(1500):
        pyboy.tick()

    pyboy.set_emulation_speed(1) 
    while not pyboy.tick():
        try:
            command = q.get(block=False)
            print("sending command", command)
            if command == "SCREENSHOT":
                os.remove("previous_vision.jpg")
                os.rename("current_vision.jpg", "previous_vision.jpg")
                screenshot = pyboy.screen_image()
                screenshot.save("current_vision.jpg", "JPEG")
                screenshot_event.set()
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