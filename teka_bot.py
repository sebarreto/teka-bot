import os
import requests
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig, SpeechSynthesizer

# Configuración de claves
TELEGRAM_BOT_TOKEN = "7886432333:AAFv7kC8pkkPCEl8Rt-2ck6zxF1RHxBfkyc"
AZURE_SPEECH_KEY = "5PBQ5CDBZj5dDNvUnNZFxBIdBehpVAkrPP0APzLPbQBjgIq9nJl0JQQJ99BAACYeBjFXJ3w3AAAYACOGvD6b"
AZURE_REGION = "eastus"
OPENAI_API_KEY = "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"

# Configurar Azure Speech
speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
speech_config.speech_recognition_language = "es-ES"
speech_synthesizer = SpeechSynthesizer(speech_config)

def speech_to_text(audio_file):
    audio_config = AudioConfig(filename=audio_file)
    recognizer = SpeechRecognizer(speech_config, audio_config)
    result = recognizer.recognize_once()
    return result.text if result.reason == 3 else ""

def text_to_speech(text, output_file):
    speech_synthesizer.speak_text_async(text).get()
    return output_file

def query_gpt(text):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": text}], "max_tokens": 200}
    )
    return response.json()["choices"][0]["message"]["content"].strip()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Hola! Envíame un mensaje de voz o texto para que te ayude.")

def handle_text(update: Update, context: CallbackContext):
    user_text = update.message.text
    response = query_gpt(user_text)
    update.message.reply_text(response)
    
    audio_file = "response.wav"
    text_to_speech(response, audio_file)
    update.message.reply_voice(voice=open(audio_file, "rb"))

def handle_voice(update: Update, context: CallbackContext):
    voice_file = context.bot.getFile(update.message.voice.file_id)
    audio_path = "voice.ogg"
    voice_file.download(audio_path)
    text = speech_to_text(audio_path)
    if text:
        response = query_gpt(text)
        update.message.reply_text(response)
        
        audio_file = "response.wav"
        text_to_speech(response, audio_file)
        update.message.reply_voice(voice=open(audio_file, "rb"))
    else:
        update.message.reply_text("No pude entender el mensaje de voz.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
