'''
This file contains all the functions used to crop the input podcast and the selected video.
'''
from moviepy.editor import *
from assemblyai.types import Word
import os, discord, assemblyai, requests

async def edit_and_send(raw_clip:str, game_clip: str, music: str | None, volume: float, font: tuple, channel: discord.DMChannel, token: str):
    cropped_path = crop_video(raw_clip, game_clip)
    audio = get_mp3_only(raw_clip)
    final_video = add_subtitles_and_music(cropped_path, font[0], font[1], font[2], music, audio=audio, volume=volume)
    path = os.path.join(os.getcwd(), f'videos/{os.urandom(8).hex()}.mp4')
    final_video.write_videofile(path)
    
    send_message(channel, "Here is the video you requested!", discord.File(path), token)

    os.remove(path)
    return

def get_mp3_only(clip: str):
    return AudioFileClip(clip)

# bypass discord.py's limitations
def send_message(channel: discord.DMChannel, message: str, file: discord.File | None, token: str):
    headers = {
        'Authorization' : f'Bot {token}',
    }
    content = {
        'content' : message
    }
    
    file = {
        'file' : (file.filename, file.fp, 'multipart/form-data')
    }
    
    requests.post(
        f'https://discord.com/api/v10/channels/{channel.id}/messages',
        headers=headers,
        data=content,
        files=file
    )

def crop_video(raw_clip: str, game_clip: str):
    raw = VideoFileClip(raw_clip)
    game = VideoFileClip(game_clip, audio=False)
    game = game.subclip(0, raw.duration)
    
    raw = raw.resize(newsize=(1080, 1920))
    (w, h) = raw.size
    assert w == 1080 and h == 1920
    raw = raw.crop(y1=h//4, y2=h//2+h//4)
    
    game = game.resize(newsize=(1080, 1920))
    (w, h) = game.size
    assert w == 1080 and h == 1920
    game = game.crop(y1=h//4, y2=h//2+h//4)

    video = clips_array([[raw], [game]])
    
    return video

def add_subtitles_and_music(video: CompositeVideoClip, font: str, font_color: str, font_size: int, music: str, audio: AudioFileClip, volume: float):
    audio.write_audiofile('temp/audio.mp3')
    subtitles = get_subtitles("temp/audio.mp3")
    os.remove('temp/audio.mp3')
    
    subtitle_clips = create_subtitle_clips(subtitles, video.size, font=font, color=font_color, fontsize=font_size)
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    if music:
        print(music)
        music_audio = AudioFileClip(music).set_duration(final_video.duration)
        music_audio = music_audio.fx(afx.volumex, volume)
        new_audio = CompositeAudioClip([final_video.audio, music_audio])
        final_video = final_video.set_audio(new_audio)
    
    return final_video

def time_to_seconds(time):
    return time / 1000

def create_subtitle_clips(subtitles: list[Word], videosize, fontsize=95, font='Impact', color='White'):
    subtitle_clips = []

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time
        zoom_duration = 0.05

        video_width, video_height = videosize
        
        text_clip = TextClip(subtitle.text.upper(), fontsize=fontsize, font=font, color=color, stroke_width=4, stroke_color='Black', bg_color = 'transparent',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height* 1 / 2
        
        # 3. Define the Scaling Function for Text Resizing
        def resize(t):
            # Define starting and ending scale factors
            start_scale = 0.8
            end_scale = 1
            # Compute the scaling factor linearly over the clip's duration
            if t > zoom_duration: t = zoom_duration
            scale_factor = start_scale + t/zoom_duration * (end_scale - start_scale)
            return scale_factor

        # 4. Define the Positioning Function to Center the Text
        def translate(t):
            # Calculate the current scale at time t
            current_scale = resize(t)
            # Get the original dimensions of the text
            text_width, text_height = text_clip.size
            # Calculate the position to keep the text centered after scaling
            x = (video_width - text_width * current_scale) / 2
            y = (video_height - text_height * current_scale) / 2
            return (x, y)
        
        text_clip = text_clip.resize(lambda t: resize(t)).set_position(translate)
        text_position = (subtitle_x_position, subtitle_y_position)                    
        subtitle_clips.append(text_clip.set_position(text_position))

    return subtitle_clips

def get_subtitles(raw_clip: str) -> list[Word]:
    '''Returns the path of the file containing the transcript of the given audio file.'''
    assemblyai.settings.api_key = os.getenv('assemblyai_key')
    transcript = assemblyai.Transcriber().transcribe(raw_clip)
    return transcript.words