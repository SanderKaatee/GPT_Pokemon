# Pokemon Red AI Player

An experimental framework that uses GPT-4 Vision to autonomously play Pokemon Red by analyzing screenshots and generating button sequences.

## Overview

This project creates an AI agent that can play Pokemon Red by:
- Taking screenshots of the game using PyBoy emulator
- Sending screenshots to GPT-4 Vision for analysis
- Creating hierarchical goals (medium-term → short-term → tasks → steps)
- Generating Game Boy button sequences to execute plans
- Verifying task completion and adapting strategy
- Continuously iterating through this process

## Architecture

The system operates on a hierarchical goal structure:

1. **Medium-term Goals**: Broad objectives (e.g., "Obtain the first Gym badge from Brock in Pewter City")
2. **Short-term Goals**: Intermediate steps (e.g., "Choose a starter Pokémon")  
3. **Tasks**: Specific actionable items (e.g., "Start a new game and proceed through initial setup")
4. **Steps**: Granular actions (e.g., "Press 'A' to start a new game")

## Files

- `play.py` - Main orchestrator managing the game loop, screenshots, and GPT communication
- `GPThandler.py` - OpenAI API integration with specialized functions for Pokemon gameplay
- `logger.py` - Simple logging functionality to track the AI's decision-making process
- `test.py` - Basic PyBoy emulator test script

## Requirements

```bash
pip install pyboy pillow requests
```

You'll also need:
- Pokemon Red ROM file (`Pokemon Red.gb`)
- OpenAI API key
- `config.py` file with your API key:

```python
API_KEY = "your-openai-api-key-here"
```

## Usage

1. Place your Pokemon Red ROM file as `Pokemon Red.gb` in the project directory
2. Create `config.py` with your OpenAI API key
3. Run the main script:

```bash
python play.py
```

The AI will start playing Pokemon Red automatically, with its thought process logged to `logs.txt`.

## How It Works

1. **Screenshot Capture**: PyBoy emulator captures the current game screen
2. **Vision Analysis**: GPT-4 Vision analyzes the screenshot and current game state
3. **Goal Planning**: AI creates/updates hierarchical goals based on game progress
4. **Action Generation**: AI generates specific button sequences to achieve immediate goals
5. **Execution**: Button sequences are sent to the emulator
6. **Verification**: AI compares before/after screenshots to verify task completion
7. **Iteration**: Process repeats with updated goals and strategy

## Key Features

- **Adaptive Planning**: AI adjusts goals based on actual game progress
- **Visual Understanding**: Uses computer vision to understand game state
- **Hierarchical Thinking**: Breaks down complex objectives into actionable steps
- **Error Recovery**: Can detect when actions don't produce expected results
- **Comprehensive Logging**: Tracks the AI's reasoning and decision-making process

## Example Output

The AI generates structured plans like:

```
MEDIUM-TERM GOALS:
1. Obtain the first Gym badge from Brock in Pewter City
2. Capture and train a well-balanced team of Pokémon

SHORT-TERM GOALS:
1. Choose a starter Pokémon
2. Defeat the rival in the first battle

TASKS:
1. Start a new game and select a starter Pokémon
2. Engage in the first battle with the rival

STEPS:
1. Press 'A' to start a new game
2. Select the 'New Game' option with the 'A' button

BUTTON-SEQUENCE:
[[A A UP A A]]
```

## Historical Context

This project was created in November 2023 as an experiment in autonomous game playing using large language models with vision capabilities. It represents an early exploration of how AI can understand and interact with classic video games through visual analysis and strategic planning.

## Limitations

- Requires OpenAI API access (costs money per API call)
- Performance depends on GPT-4's interpretation of game screenshots
- May get stuck in certain game situations
- No guarantee of optimal gameplay strategies

## License

This is an experimental project for research/educational purposes. Ensure you own a legal copy of Pokemon Red before using this software.
