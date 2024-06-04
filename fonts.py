#!/usr/bin/env python3
import subprocess, os

def get_fonts():
    fonts = []
    result = subprocess.run(['fc-list'], stdout=subprocess.PIPE).stdout
    result = result.decode('utf-8').split("\n")[:-1]
    
    for i in result:
        fonts.append(i.split(":")[0])
        
    for i in fonts:
        head, tail = os.path.split(i)
        tail = tail.split(".")[0]
        os.system(f"ln -s {i} ./fonts/{tail}")

if __name__ == '__main__':
    try:
        get_fonts()
    except Exception as e:
        print(f"Error: {e}")