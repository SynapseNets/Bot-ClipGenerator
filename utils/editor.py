'''
This file contains all the functions used to crop the input podcast and the selected video.
'''
from moviepy.editor import *
import os, discord

async def edit_and_send(raw_clip:str, game_clip: str, user: discord.User):
    result_path = crop_video(raw_clip, game_clip)
    channel = await user.create_dm()
    await channel.send(content="Here is the video you requested!", file=discord.File(result_path))
    os.remove(result_path)
    os.remove(raw_clip)

def crop_video(raw_clip: str, game_clip: str):
    raw = VideoFileClip(raw_clip).subclip(0, 5) # TODO CHANGE
    game = VideoFileClip(game_clip).subclip(0, raw.duration)
    
    raw = raw.resize(newsize=(1080, 1920))
    (w, h) = raw.size
    assert w == 1080 and h == 1920
    raw = raw.crop(y1=h//4, y2=h//2+h//4)
    
    game = game.resize(newsize=(1080, 1920))
    (w, h) = game.size
    assert w == 1080 and h == 1920
    game = game.crop(y1=h//4, y2=h//2+h//4)

    video = clips_array([[raw], [game]])
    video = add_audio(video, game.audio)
    
    path = os.path.join(os.getcwd(), "videos/" + os.urandom(8).hex() + ".mp4")
    video.write_videofile(path)
    return path

def add_audio(video: CompositeVideoClip, game: AudioFileClip) -> CompositeVideoClip:
    audio = CompositeAudioClip([video.audio, game])
    video = video.set_audio(audio)
    return video