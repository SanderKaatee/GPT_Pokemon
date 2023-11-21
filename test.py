from pyboy import PyBoy

# Path to your Pokémon Red ROM
rom_path = "Pokemon Red.gb"

# Initialize PyBoy with the ROM
pyboy = PyBoy(rom_path, window_type="SDL2", debug=False, sound=True)

# Start the game
pyboy.set_emulation_speed(1)  # Set to 0 for unlimited speed
while not pyboy.tick():
    pass

# Shut down PyBoy
pyboy.stop(save=True)
