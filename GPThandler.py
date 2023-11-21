import base64
import requests
import json

import config
from logger import append_to_file


# OpenAI API Key
api_key = config.API_KEY
MODEL = "gpt-4-1106-preview"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def append_strings_with_numbers(strings):
    # Using list comprehension to format and combine the strings
    return "\n".join(f"{i+1}. {s}" for i, s in enumerate(strings))

# Function to construct the payload
def construct_payload(model, role_content, user_content, max_tokens, image_base64=None):
    messages = [
        {"role": "system", "content": role_content},
        {"role": "user", "content": user_content}
    ]

    if image_base64:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })


    return {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }

# Generic function for OpenAI API requests
def openai_request(payload):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_dict = response.json()
    print(response_dict)
    return response_dict['choices'][0]['message']['content']

# Example usage
def request_goal(request_type, vision, goal, current=None, completed=None):
    model = MODEL
    if request_type == "medium-term goal":
        higher_order_type = "ultimate goal"
        explanation = "These should be broader and encompass larger segments of the game. Focus on overarching objectives that require multiple steps to achieve."
    elif request_type == "short-term goal":
        higher_order_type = "medium-term goal"
        explanation = "Break down medium-term goals into chunks that represent significant progress but avoid overly specific steps like menu navigation. Focus on gameplay actions rather than preparatory or administrative tasks."
    elif request_type == "task":
        higher_order_type = "short-term goal"
        explanation = "Translate short-term goals into specific, actionable items. Clear instructions that do not require further breakdown for execution."
    elif request_type == "step":
        higher_order_type = "task"
        explanation = "The most granular level, translating tasks into direct button presses. Each step represents a singular action on the Gameboy."
    else:
        print("incorrect request type")


    if current and completed:
        completed_list = append_strings_with_numbers(completed)
        role_content = ("Your role is to act as a sequence of '" + request_type + 
                        "'s manager for Pokémon Red. List exactly one '" + request_type + 
                        "' in response to the user's query. Do not respond with anything other than that one '" + 
                        request_type + "'. If you think you will reach your '" + higher_order_type + 
                        "' after the remaining '" + request_type + "'s, then reply 'DONE' and nothing else. The scope of these '" + request_type + "'s is as follows: " + explanation)

        user_content = [{
            "type": "text",
            "text": ("You're playing Pokémon Red. Your screen currently displays the following: \n" + vision + 
                    "\n From this point on, you have to move towards your '" + higher_order_type + 
                    "', which is: " + goal + ". You just finished '" + completed_list + 
                    "'. Your remaining '" + request_type + "'s are " + current + 
                    ". What would be the next '" + request_type + "' after these '" + request_type + "'s? If you think you will have completed your '" + 
                    higher_order_type + "' after the remaining '" + request_type + "'s, then reply 'DONE'.")
        }]
    else:
        role_content = ("Your role is to act as a '" + request_type + 
                        "' determiner for Pokémon Red. List exactly five sequential '" + request_type + 
                        "'s in response to the user's query. Do not respond with anything other than the list of five '" + 
                        request_type + "'s. The scope of these '" + request_type + "'s is as follows: " + explanation)

        user_content = [{
            "type": "text",
            "text": ("You're playing Pokémon Red. Your screen currently displays the following: \n" + vision + 
                    "\n\n From this point on, you have to move towards your '" + higher_order_type + 
                    "', which is: " + goal + ". What would your first five concrete and sequential '" + request_type + 
                    "'s be to move towards or complete this '" + higher_order_type + "'?")
        }]
    max_tokens = 150  # or 30 based on your use case
    payload = construct_payload(model, role_content, user_content, max_tokens)
    append_to_file(role_content)
    append_to_file(user_content[0]["text"])

    message = openai_request(payload)
    append_to_file(message)
    return message

# Function to request image content analysis
def request_image_content(image_path):
    base64_image = encode_image(image_path)
    model = "gpt-4-vision-preview"
    user_content = [
        {"type": "text", "text": "What is currently visible on the screen"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}}
    ]
    max_tokens = 300

    payload = construct_payload(model, "", user_content, max_tokens)
    message = openai_request(payload)
    append_to_file(message)
    return message

def request_button_sequence(vision, steps, goal):
    model = MODEL
    step_list = append_strings_with_numbers(steps)
    role_content = ("Your role is to act as a button sequencer. You are given a sequence of steps that need to be performed to complete a certain task. Your job is to translate that sequence of steps into a sequence of button presses for the original GameBoy. \n\n Think before making the sequence of button presses. However, you should eventually provide the sequence as follows: [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]. This means two opening square brackets, any sequence of presses to perform the steps and complete the task, then two closing square brackets. DO NOT EXPLAIN AFTER THE SEQUENCE, only think before if necessary. DO NOT put anything other than the possible buttons between the brackets!!")

    user_content = [{
        "type": "text",
        "text": ("You're playing Pokémon Red. Your screen currently displays the following: \n" + vision + 
                "\n\n You need to perform the following sequence of steps: \n" + step_list + 
                "\n in order to complete '" + goal + "'. Provide the required sequence of button presses contained in double square brackets. Only use the following terms between the brackets to denote the button presses: [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]")
    }]

    max_tokens = 300  # or 30 based on your use case
    payload = construct_payload(model, role_content, user_content, max_tokens)
    append_to_file(role_content)
    append_to_file(user_content[0]["text"])

    message = openai_request(payload)
    append_to_file(message)
    return message

def verify_task_completion(previous_vision_path, vision_path, tasks):
    model = "gpt-4-vision-preview"
    previous_vision_base64 = encode_image(previous_vision_path)
    vision_base64 = encode_image(vision_path)

    task_list = append_strings_with_numbers(tasks)

    role_content = ("Your role is to act as a task completion verifier for Pokémon Red. You are given images of the previous game screen state, the current game screen state, and a list of tasks. Your job is to analyze the changes between the two visions to determine which tasks, if any, have been completed. List the completed tasks based on your analysis. If none of the tasks are completed, respond with 'NONE'. VERY IMPORTANT: List NOTHING else than the completed tasks or 'NONE'")

    user_content = [{
        "type": "text",
        "text": f"You're playing Pokémon Red. The previous game screen and current game screen are appended below. Given these changes in the game state, and considering the following tasks: \n{task_list}\nWhich of these tasks have been completed? If none are completed, respond with 'NONE'."
    }, {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{previous_vision_base64}", "detail": "low"}
    }, {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{vision_base64}", "detail": "low"}
    }]

    max_tokens = 300  # Adjust based on your use case
    payload = construct_payload(model, role_content, user_content, max_tokens)

    message = openai_request(payload)
    append_to_file(message)
    return message


def request_initial_goals(vision_path):
    model = "gpt-4-vision-preview"
    vision_base64 = encode_image(vision_path)

    user_content = [
        {"type": "text", "text": '''You're playing Pokémon Red. Your ultimate goal is to defeat the Elite Four. Based on the game screen below, define the following goals:
    medium-term goals - These should be broader and encompass larger segments of the game. Focus on overarching objectives that require multiple steps to achieve.
    short-term goals - Break down medium-term goals into chunks that represent significant progress but avoid overly specific steps like menu navigation. Focus on gameplay actions rather than preparatory or administrative tasks.
    tasks - Translate short-term goals into specific, actionable items. Clear instructions that do not require further breakdown for execution.
    step - The most granular level, translating tasks into direct button presses. Each step represents a singular action on the Gameboy.
    confidence in steps - Provide some thoughts about your confidence in how many steps you could do in one go right now (e.g.: "I'm quite sure about the first 4 steps, lets try them to do them all in one button sequence" or however you prefer to reason about it). 
    button-sequence - Provide the required sequence of button presses contained in double square brackets. Only use the following terms between the brackets to denote the button presses: [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]. Give only ONE button sequence in EXACTLY this format, adhere to the following format ONLY, DO NOT ADD ANYTHING ELSE:

    MEDIUM-TERM GOALS:
    1. ...
    ...
    SHORT-TERM GOALS:
    1. ...
    ...
    TASKS:
    1. ...
    ...
    STEPS:
    1. 
    ...
    ...

    -confidence in steps- 
    
    BUTTON-SEQUENCE:
    [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]"
        '''},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{vision_base64}", "detail": "low"}}
    ]

    role_content = "Your role is to define goals for Pokémon Red at different levels based on the initial game screen. Provide a sequential stack of goals for each level: medium-term, short-term, tasks, and steps. Format the output for easy extraction with regex as follows:\n\nMEDIUM-TERM GOALS:\n1. ...\n...\n\nSHORT-TERM GOALS:\n1. ...\n...\n\nTASKS:\n1. ...\n...\n\nSTEPS:\n1. ...\n...\n\nBUTTON-SEQUENCE:\n[[START SELECT A B UP DOWN LEFT RIGHT LB RB]]"

    max_tokens = 700  # Adjust based on your use case
    payload = construct_payload(model, role_content, user_content, max_tokens)

    message = openai_request(payload)
    append_to_file(message)
    return message

def request_progress_update(minus_two, minus_one, previous_vision_path, current_vision_path, goals):
    model = "gpt-4-vision-preview"

    previous_vision_base64 = encode_image(previous_vision_path)
    current_vision_base64 = encode_image(current_vision_path)
   
    user_content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{previous_vision_base64}", "detail": "low"}},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{current_vision_base64}", "detail": "high"}},
        {"type": "text", "text": f'''You are an AI that is playing Pokémon Red (YOU ARE THE PLAYER), your ultimate goal is to defeat the Elite Four. Do not forget that you yourself are playing the game, there is no outside influence. 

    Here were your previous thoughts:
    {goals}

    The game has progressed since then since the button sequence you provided was inputted into the game. Now you repeat this task:

    Compare the previous screen and the current game screen below.

    First describe each image, focus on relevant aspects of the game. Be sure to be very verbose about the current screen, describe it in detail. Try to describe the location of important objects such as the player or the cursor in a menu. 
    
    Think step by step about what's going right and wrong. Determine which tasks and steps are completed, if adjustments are needed, and what the next set of actions should be. BE CRITICAL: are you playing the game correctly? Have you been progressing? Where did you expect to be and where are you now?
    
    First mention your thoughts, important lessons and then reply the full (adjusted) goals in the format provided. Add important lessons you've learned to the list of important lessons when necessary. Provide the required sequence of button presses contained in double square brackets at the end, also provide some thoughts about your confidence in how many steps you could do in one go right now (e.g.: "I'm quite sure about the first 4 steps, lets try them to do them all in one button sequence" or however you prefer to reason about it). Only use the following terms between the brackets to denote the button presses: [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]. Give a button sequence (preferably on a length that works with your confidence) in EXACTLY this format.

    Here's how you can structure your thoughts:
    
    -screen analyses-

    -thoughts-
    
    -important lessons- 
    
    MEDIUM-TERM GOALS:
    1. ...
    ...
    SHORT-TERM GOALS:
    1. ...
    ...
    TASKS:
    1. ...
    ...
    STEPS:
    1. 
    ...
    ...

    -confidence in steps- 
    
    BUTTON-SEQUENCE:
    [[START SELECT A B UP DOWN LEFT RIGHT LB RB]]"
        '''}
    ]
    

    role_content = "You are an AI that is playing Pokemon Red as part of an experiment, your ultimate goal is to defeat the Final Four. IT IS YOU THAT IS PLAYING, YOU ARE THE PLAYER -> the goal of the experiment is to see if you are able to complete this game. Analyze changes in the game state for Pokémon Red and update the progress towards set goals. Provide THE FULL sequential stack of goals for each level: medium-term, short-term, tasks, and steps."

    max_tokens = 4096
    payload = construct_payload(model, role_content, user_content, max_tokens)

    message = openai_request(payload)
    append_to_file(message)
    return message
