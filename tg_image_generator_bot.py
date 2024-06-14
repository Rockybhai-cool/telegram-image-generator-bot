import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from dotenv import load_dotenv
#import logging

# Load environment variables from .env file
load_dotenv()

# Secure sensitive information using environment variables
TOKEN: Final = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME: Final = '@Image_Generator45_Bot'
ACCESS_KEY: Final = os.getenv('UNSPLASH_ACCESS_KEY')

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
if not ACCESS_KEY:
    raise ValueError("No UNSPLASH_ACCESS_KEY found. Please set the UNSPLASH_ACCESS_KEY environment variable.")

#print(f"Token: {TOKEN}")  #---> For debugging purpose 
# Configure logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

########## Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, welcome to the Image generator Bot by Karlos :)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''
Available commands:
/start - Welcome message
/help - List of commands
/generate <keyword> - Generate an Image based on the Keyword
/info - Information about the bot
''')

async def details_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello there! I am an Image generator Bot. This bot is made using python-telegram-bot by Python Developer - @Karlos_5160.")

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text.split()) > 1:
        category = ' '.join(text.split()[1:])
        imgdata = await generate_image(category)
        if imgdata:
            await update.message.reply_photo(imgdata)
        else:
            await update.message.reply_text("Sorry, I couldn't find an image for that keyword.")
    else:
        await update.message.reply_text("Please provide a keyword after /generate")

async def generate_image(category: str):
    try:
        url = f'https://api.unsplash.com/photos/random?query={category}&orientation=landscape&client_id={ACCESS_KEY}'
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        imgdata = requests.get(data["urls"]["regular"]).content
        return imgdata
    except requests.RequestException as e:
        error(f'Error fetching image: {e}')
        return None

########## Responses
import re
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if re.search(r'\bhello\b', processed):
        return 'Hey there!'
    elif re.search(r'\bhi\b', processed):
        return 'Hello! Nice to meet you. I am an Image generator Bot.'
    elif re.search(r'\bhow are you\b', processed):
        return "I'm fine, thank you! How about you?"
    elif re.search(r'\bfine\b', processed):
        return "Nice to hear that, Sir."
    else:
        return 'I am unable to understand what you wrote. Please use /help to see available commands.'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}" ')

    if message_type == 'group':
        if BOT_USERNAME in text.split()[0]:  # Check if bot's username is mentioned at the beginning of the message
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            await update.message.reply_text(response)
        else:
            return
    else:
        response: str = handle_response(text)
        await update.message.reply_text(response)

    print('Bot: ', response)

    await update.message.reply_text("To generate an image, please use /generate followed by a keyword.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # logger.warning(f'Update {update} caused error {context.error}')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I couldn't find an image for that keyword"
    )

if __name__ == '__main__':
    print("Starting bot.....")
    app = Application.builder().token(TOKEN).build()

    ########## Handling Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('info', details_command))

    ########## Handling Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    ########## Handling Errors
    app.add_error_handler(error)

    ########## Polls the Bot
    print('Polling....')
    app.run_polling(poll_interval=2)  # check for new message updates every 2 seconds
