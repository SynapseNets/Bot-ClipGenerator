'''
This file contains all the functions used to crop the input podcast and the selected video.
'''
from moviepy.editor import *
from assemblyai.types import TranscriptError
import os, discord, assemblyai, pysrt, requests

async def edit_and_send(raw_clip:str, game_clip: str, music: str | None, font: tuple, channel: discord.DMChannel, token: str):
    
    cropped_path = crop_video(raw_clip, game_clip)
    result_path = add_background_music(cropped_path, music)
    audio = get_mp3_only(raw_clip)
    final_video = add_subtitles(result_path, font[0], font[1], font[2], audio=audio)
        
    send_message(channel, "Here is the video you requested!", discord.File(final_video), token)
    
    os.remove(result_path)
    os.remove(cropped_path)
    os.remove(final_video)
    os.remove(raw_clip)
    return

def get_mp3_only(clip: str):
    audio = AudioFileClip(clip)
    audio.write_audiofile(clip.split('.')[0] + ".mp3")
    return clip.split('.')[0] + ".mp3"

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
    
    path = os.path.join(os.getcwd(), "videos/" + os.urandom(8).hex() + ".mp4")
    video.write_videofile(path)
    return path

def add_background_music(raw_clip: str, music: str | None = None):
    if music is None:
        return raw_clip
    
    video = VideoFileClip(raw_clip)
    
    audio = AudioFileClip(music)
    audio = audio.fx(afx.volumex, 0.3)
    audio = audio.set_duration(video.duration)
    new_audio = CompositeAudioClip([video.audio, audio])
    
    final_video = video.set_audio(new_audio)
    final_path = raw_clip.split('.')[0] + "_with_music.mp4"
    
    final_video.write_videofile(final_path)

    return final_path

def add_subtitles(raw_clip: str, font: str, font_color: str, font_size: int, audio: str):
    video = VideoFileClip(raw_clip)
    subtitles_file = get_subtitles(audio)
    subtitles = pysrt.open(subtitles_file)
    
    subtitle_clips = create_subtitle_clips(subtitles, video.size, font=font, color=font_color, fontsize=font_size)
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    final_path = raw_clip.split('.')[0] + "_subtitled.mp4"
    final_video.write_videofile(final_path)
    os.remove(subtitles_file)
    
    return final_path

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

def create_subtitle_clips(subtitles, videosize, fontsize=95, font='Impact', color='White'):
    subtitle_clips = []

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time
        zoom_duration = 0.1

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

def get_subtitles(raw_clip: str) -> str:
    '''Returns the path of the file containing the transcript of the given audio file.'''
    assemblyai.settings.api_key = os.getenv('assemblyai_key')
    transcript = assemblyai.Transcriber().transcribe(raw_clip) #TODO: send only audio to save time and resources
    try:
        subtitles = transcript.export_subtitles_srt(chars_per_caption=15)
    except TranscriptError as e:
        subtitles = ''
        pass
    
    file_out = open(f"{raw_clip.split('.')[0]}.srt", "w")
    file_out.write(subtitles)
    file_out.close()
    
    return file_out.name