# Bot ClipGenerator 🤖
This repository contains a project of a Discord bot entirely written in *Python 3.10* that allows the generation of meme clips based on customizable input data chosen by the user.

## Purpose ♥️
The bot is designed to simplify the creation of engaging content by allowing users to upload a video. The bot will then add subtitles, crop the video accordingly, add another clip that appears at the bottom of the screen, and include background music.

## How to run 🛠️
Our bot is designed to be run with the following `.env` file in the main directory of the project, containing the private keys for **Discord** and **AssemblyAI**.
```.env
token=xxx
assemblyai_key=yyy
```
You must also create a directory **clips** with all the **`mp4`** videos you want to use in your contents.

## Commands 💬
* `/ping`: replies with **pong** if the bot is online.
* `/create raw_clip=[ARG1] video=[ARG2] music=[ARG2 | None] font=[ARG3] font_color=[ARG4]` : generates the clip with the choosen arguments.

## How does it Work 🔌
### Resource gathering
The bot receives only the video to be added on top and a few parameters from the user. But where does the bot get the clips for the bottom?

The audio and video resources used for editing are saved in designated folders, allowing the user to select whichever they prefer without having to send them.

The owner of the bot can add all the necessary resources in the two sub-folders, which the bot will scan to ask the user which clip, music, or font should be used.

The 2 sub-folders are:
- clips

Where the videos that appear at the bottom are stored.
- fonts

Where the fonts that are used for the subtitles are stored.

There is another sub-folder named 'videos'; this folder is used by the bot to temporarily save videos, and users must not remove or add content to it.

### Video editing process
The bot uses MoviePy to assemble the video by cropping the clips, adding music and subtitles. To add subtitles, the bot uses AssemblyAI API, which provides a free key. Then, the bot uses FFmpeg to optimize the video size. Finally, the result is sent to the user via Discord direct messages.

## License 📖
The use of this product is determined by the ["Commons Clause" License Condition v1.0](https://github.com/SynapseNets/Bot-ClipGenerator/blob/main/LICENSE.md).
