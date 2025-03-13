import logging
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from gtts import gTTS
import random

# Bot Token
TOKEN = "7679508704:AAGZJoeTB-Ln1HjH1jRV6mNKta2LrQ-zJ1w"

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Connect to SQLite Database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        language TEXT
    )
""")
conn.commit()

# Sample words/phrases
WORDS = {
    "english": ["Hello - Hola", "Thank you - Gracias", "Goodbye - Adiós"],
    "french": ["Hello - Bonjour", "Thank you - Merci", "Goodbye - Au revoir"],
    "spanish": ["Hello - Hola", "Thank you - Gracias", "Goodbye - Adiós"]
}

# Start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("English"))
    keyboard.add(KeyboardButton("French"))
    keyboard.add(KeyboardButton("Spanish"))
    
    await message.reply("Choose your language to start learning:", reply_markup=keyboard)

# Handle language selection
@dp.message_handler(lambda message: message.text.lower() in WORDS)
async def set_language(message: types.Message):
    user_id = message.from_user.id
    language = message.text.lower()
    
    cursor.execute("REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    
    await message.reply(f"Language set to {language.capitalize()}! Send /word to get a new word.")

# Send a random word
@dp.message_handler(commands=['word'])
async def send_word(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        language = row[0]
        word = random.choice(WORDS[language])
        
        # Generate pronunciation
        tts = gTTS(text=word.split(" - ")[1], lang=language[:2])
        audio_path = "pronunciation.mp3"
        tts.save(audio_path)
        
        with open(audio_path, "rb") as audio:
            await message.reply(word)
            await bot.send_voice(message.chat.id, audio)
    else:
        await message.reply("Please choose your language first using /start.")

# Run bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
