'''
This file contains all the functions used to retrieve the files in the 3 folders:
- Clips
- Music
- Fonts
'''

import os, typing
from enum import Enum
from discord import app_commands

class Directories(Enum):
    Clips = './Clips/'
    Music = './Music/'
    Fonts = './Fonts/'

def check_param(param: Directories) -> bool:
    return isinstance(param, Directories)

def check_directories() -> bool:
    return os.path.exists(Directories.Clips.value) and os.path.exists(Directories.Music.value) and os.path.exists(Directories.Fonts.value)

def verify_file(file_name: str, type: Directories) -> bool:
    return os.path.exists(type.value + file_name)

def retrieve_Files(type: Directories) -> list[str]:
    if check_param(type) is False: raise Exception
    
    return os.listdir(type.value)

def get_Choices(type: Directories, criteria: str) -> list[app_commands.Choice]:
    results = []
    for file in retrieve_Files(type=type):
        if criteria in file:
            results.append(app_commands.Choice(name=file, value=file))
    return results