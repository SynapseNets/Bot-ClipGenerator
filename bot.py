import discord, os, asyncio, nest_asyncio
import utils.gallery as gallery
import utils.editor as editor
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv
from threading import Thread

class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
loop_handler = AsyncLoopThread()
nest_asyncio.apply(loop=loop_handler.loop)
loop_handler.start()

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity("Watching TikTok"))
    synced = await bot.tree.sync()
    
    print(f"{len(synced)} commands loaded.")
    print(f'We have logged in as {bot.user}')

class Modal_TextSettings(ui.Modal, title='Text Settings'):
    fontSize = ui.TextInput(label='Font Size', style=discord.TextStyle.short, required=True)

    def __init__(self, raw_clip: discord.Attachment, gamevideo: str, music: str, font: str):
        self.raw_clip = raw_clip
        self.video = gamevideo
        self.music = music
        self.font = font
        # self.font_size = font_size
        super().__init__()
        
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        raw_file = await gallery.save_raw_file(self.raw_clip, interaction.user.id)

        await interaction.followup.send(f'Settings received, the result video will be sent to you shortly.', ephemeral=True)
        asyncio.run_coroutine_threadsafe(
            editor.edit_and_send(raw_file, os.path.join(os.getcwd(), f'clips/{self.video}'), interaction.user), 
            loop_handler.loop
        )
        
@bot.tree.command(name='ping', description='Replies with pong!')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"pong! requested by {interaction.user.mention}")

@bot.tree.command(name='create', description='Creates a new video for you.')
async def create(interaction: discord.Interaction, raw_clip: discord.Attachment, video: str, music: str, font: str):

    if gallery.check_extension(raw_clip.filename) is False: 
        await interaction.response.send_message(content="The sent file hasn't got a supported extension, list of supported extensions: " + str(gallery.valid_exts), ephemeral=True)
        return
    
    if gallery.verify_file(type=gallery.Directories.Clips, file_name=video) and gallery.verify_file(type=gallery.Directories.Music, file_name=music) and gallery.verify_file(type=gallery.Directories.Fonts, file_name=font):
        await interaction.response.send_modal(Modal_TextSettings(raw_clip, video, music, font))
    else: 
        await interaction.response.send_message(content="Invalid input.")

#autocomplete functions
@create.autocomplete('video')
async def autocomplete_callback(interaction: discord.Interaction, current: str):
    return gallery.get_Choices(type=gallery.Directories.Clips, criteria=current)

@create.autocomplete('music')
async def autocomplete_callback(interaction: discord.Interaction, current: str):
    return gallery.get_Choices(type=gallery.Directories.Music, criteria=current)

@create.autocomplete('font')
async def autocomplete_callback(interaction: discord.Interaction, current: str):
    return gallery.get_Choices(type=gallery.Directories.Fonts, criteria=current)

def main():
    # seems we dont use docker
    if not os.path.exists("temp"): 
        os.mkdir("temp")
    if not os.path.exists("videos"):
        os.mkdir("videos")

    load_dotenv()    
    bot.run(os.getenv('token'))

if __name__ == "__main__":
    main()