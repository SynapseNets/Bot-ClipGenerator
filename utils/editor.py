'''
This file contains all the functions used to crop the input podcast and the selected video.
'''
from moviepy.editor import *
import os, discord, assemblyai, dotenv, pysrt

async def edit_and_send(raw_clip:str, game_clip: str, user: discord.User):
    result_path = crop_video(raw_clip, game_clip)
    final_video = add_subtitles(result_path)
    #TODO: add music
    channel = await user.create_dm()
    await channel.send(content="Here is the video you requested!", file=discord.File(final_video))
    os.remove(result_path)
    os.remove(final_video)
    os.remove(raw_clip)

def crop_video(raw_clip: str, game_clip: str):
    raw = VideoFileClip(raw_clip)
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

def add_subtitles(raw_clip: str):
    video = VideoFileClip(raw_clip)
    subtitles_file = get_subtitles(raw_clip)
    subtitles = pysrt.open(subtitles_file)
    
    subtitle_clips = create_subtitle_clips(subtitles, video.size)
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

        video_width, video_height = videosize
        
        text_clip = TextClip(subtitle.text.upper(), fontsize=fontsize, font=font, color=color, stroke_width=4, stroke_color='Black', bg_color = 'transparent',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height* 1 / 2
        
        # 3. Define the Scaling Function for Text Resizing
        def resize(t):
            # Define starting and ending scale factors
            start_scale = 1
            end_scale = 2
            # Compute the scaling factor linearly over the clip's duration
            scale_factor = start_scale + t/duration * (end_scale - start_scale)
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
    subtitles = transcript.export_subtitles_srt(chars_per_caption=30)
    
    file_out = open(f"{raw_clip.split('.')[0]}.srt", "w")
    file_out.write(subtitles)
    file_out.close()
    
    return file_out.name

