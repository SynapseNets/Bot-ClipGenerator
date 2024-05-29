import discord, requests, os
import utils.gallery as gallery
import utils.editor as editor
from discord.ext import commands, tasks
from discord import app_commands, ui
from dotenv import load_dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity("Watching TikTok"))
    synced = await bot.tree.sync()
            
    print(f"{len(synced)} commands loaded.")
    print(f'We have logged in as {bot.user}')

class Modal_TextSettings(ui.Modal, title='Text Settings'):
    settings = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Settings received, the result video will be sent to you shortly.', ephemeral=True)
        
@bot.tree.command(name='ping', description='Replies with pong!')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"pong! requested by {interaction.user.mention}")

@bot.tree.command(name='create', description='Creates a new video for you.')
async def create(interaction: discord.Interaction, raw_clip: discord.Attachment, video: str, music: str, font: str):
    if gallery.check_extension(raw_clip.filename) is False: 
        await interaction.response.send_message(content="The sent file hasn't got a supported extension, list of supported extensions: " + str(gallery.valid_exts), ephemeral=True)
        return
    
    raw_file = await gallery.save_raw_file(raw_clip, interaction.user.id)
    
    if gallery.verify_file(type=gallery.Directories.Clips, file_name=video) and gallery.verify_file(type=gallery.Directories.Music, file_name=music) and gallery.verify_file(type=gallery.Directories.Fonts, file_name=font):
        # await interaction.response.send_modal(Modal_TextSettings())
        await interaction.response.send_message('Hey this is the file you asked!', ephemeral=True)
        path = editor.crop_video(raw_file, os.path.join(os.getcwd(), f'Clips/{video}'))
        await interaction.channel.send(file=discord.File(path))
    else: 
        await interaction.response.send_message("Invalid input.")

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


if __name__ == "__main__":
    # seems we dont use docker
    try:
        os.mkdir("temp")
    except:
        pass
    try:
        os.mkdir("videos")
    except:
        pass
    load_dotenv()
    bot.run(os.getenv('token'))