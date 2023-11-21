from datetime import datetime

def append_to_file(text):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs.txt", 'a', encoding='utf-8') as file:
        file.write('\n' + current_time + '\n')
        file.write(text + '\n')