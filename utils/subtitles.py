import assemblyai as aai
import json, os

def getSubtitles():
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe("https://storage.googleapis.com/aai-web-samples/news.mp4")
    print(transcript.words)

if __name__ == '__main__':
    aai.settings.api_key = os.getenv('assemblyai')