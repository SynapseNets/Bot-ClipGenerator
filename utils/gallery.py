'''
This file contains all the functions used to retrieve the files in the 3 folders:
- Clips
- Music
- Fonts
'''

import os
from enum import Enum
from moviepy.editor import TextClip
from discord import app_commands, Attachment

class Directories(Enum):
    Clips = './clips/'
    Music = './music/'
    Fonts = './fonts/'

fontsColors = [
    'blue', 'green', 'white', 'black', 'red',
    'yellow', 'purple', 'orange', 'brown', 'pink',
    'cyan', 'magenta', 'lime', 'teal', 'indigo',
    'violet', 'fuchsia', 'gold', 'silver', 'gray',
    'maroon', 'olive', 'navy', 'aquamarine', 'turquoise'
]
# square = {
#     'blue' : ':blue_square:', 'green' : ':green_square:', 
#     'red' : ':red_square:', 'yellow' : ':yellow_square:',
#     'purple' : ':purple_square:', 'orange' : ':orange_square:',
#     'brown' : ':brown_square:', 'cyan' : ':cyan_square:'
# }
# large_square = {
#     'white' : ':white_large_square:', 'black' : ':black_large_square:'
# }
valid_exts = ['.mp4']

def check_param(param: Directories) -> bool:
    return isinstance(param, Directories)

def check_directories() -> bool:
    return os.path.exists(Directories.Clips.value) and os.path.exists(Directories.Music.value) and os.path.exists(Directories.Fonts.value)

def verify_file(file_name: str, type: Directories) -> bool:
    return os.path.exists(type.value + file_name)

def verify_font(file_name: str) -> bool:
    return file_name in TextClip.list('font')

def verify_font_color(color: str) -> bool:
    return color in fontsColors

def check_extension(file_name: str):
    for ext in valid_exts:
        if file_name.endswith(ext): return True
    
    return False

def retrieve_Files(type: Directories) -> list[str]:
    if check_param(type) is False: raise Exception
    
    list = os.listdir(type.value)
    list.remove('.gitkeep')
    return list

def get_Choices(type: Directories, criteria: str) -> list[app_commands.Choice]:
    results = []
    for file in retrieve_Files(type=type):
        if criteria in file:
            results.append(app_commands.Choice(name=file, value=file))
    return results

def get_font_Choices(criteria: str) -> list[app_commands.Choice]:
    results = []
    for file in TextClip.list('font'):
        if criteria in file:
            results.append(app_commands.Choice(name=file, value=file))
            
    if len(results) > 25:
        print("Too many results, truncating to 25.")
        results = results[:25]
    return results

def get_font_color_Choices(criteria: str) -> list[app_commands.Choice]:
    results = []
    for color in fontsColors:
        if criteria in color:
            results.append(app_commands.Choice(name=color, value=color))
    return results

async def save_raw_file(raw_clip: Attachment, user_id: int):
    path = os.path.join(os.getcwd(), 'temp/' + str(user_id) + '-' + os.urandom(8).hex() + ".mp4")
    await raw_clip.save(path)
    return path