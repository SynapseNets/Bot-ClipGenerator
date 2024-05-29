import discord, requests, os, gallery, typing
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
    await raw_clip.save('./' + str(interaction.user.id) + raw_clip.filename)
    
    if gallery.verify_file(type=gallery.Directories.Clips, file_name=video) and gallery.verify_file(type=gallery.Directories.Music, file_name=music) and gallery.verify_file(type=gallery.Directories.Fonts, file_name=font):
        await interaction.response.send_modal(Modal_TextSettings())
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
    load_dotenv()
    bot.run(os.getenv('token'))