'''
This file contains all the functions used to crop the input podcast and the selected video.
'''
from moviepy.editor import VideoFileClip, clips_array, vfx
import os

def crop_video(raw_clip: str, game_clip: str):
    raw = VideoFileClip(raw_clip)
    game = VideoFileClip(game_clip).subclip(0, raw.duration)
    
    raw.without_audio()
    raw.fx(vfx.resize,(1080, 960), width=1080)
    game.fx(vfx.resize, (1080, 960), width=1080)
    
    video = clips_array([[raw], [game]])
    video.fx(vfx.resize,(1080,1920),width= 1080)

    path = os.path.join(os.getcwd(), "videos/" + os.urandom(8).hex() + ".mp4")
    video.write_videofile(path)
    return path   