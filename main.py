#!/usr/bin/env python
# pylint: disable=C0116,W0613

"""
Simple TV Bot for Telegram
Usage:
/tv -- shows daily program scraped for today from marca.com
"""

import logging
import json
import os
import copy


from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from azure.storage.blob import BlobServiceClient

from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def awesome_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Marina, you are awesome!🥳')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    # update.message.reply_text(update.message.text)
    update.message.reply_text("hola Marina :)")

def tv(update: Update, context: CallbackContext) -> None:
    
    with open(get_json()) as f:
        data = json.load(f)
    
    # init day 0
    today = data[0]["day"]
    line = ""
    list_events = []
    dict_event = {}
    found = True
    n = 0
    
    # init message body
    message = "🗓️ "+today+"\n\n"

    # dictionaries map
    dict_sport_emoji = {
        "Tenis": "🎾",
        "Fútbol": "⚽️",
        "NBA": "🏀",
        "Baloncesto": "🏀",
        "Ciclismo": "🚴‍♀️",
        "Golf": "⛳️",
        "Balonmano": "🤾‍♀️",
        "Badminton": "🏸",
        "NFL": "🏈",
        "Rugby": "🏈",
        "NHL": "🏒",
        "Motor": "🏁"
    }
    dict_event_formated = {
        "liga regular": "Liga",
        "laliga santander": "Liga",
        "liga femenima": "Liga Femenina",
        "dakar": "DAKAR",
        "premier league": "Premier",
        "united cup": "United Cup"
    }

    while (data[n]["day"] == today):
        emoji = dict_sport_emoji.get(data[n]["sport"],"")
        line = data[n]["time"]+" "+data[n]["match"]+" ("+data[n]["channel"]+")"+"\n"

        if(n>0):
            m = 0
            found = False
            while (m<n and found == False):
                if (data[m]['sport'] == data[n]['sport'] and data[m]['competition'] == data[n]['competition']):
                    dict_event_copy = copy.deepcopy(dict_event)
                    result = find_element(list_events, 'sport','competition', data[m]['sport'], data[m]['competition'])
                    dict_event_copy = list_events[result]
                    dict_event_copy["message"] = dict_event_copy["message"] + line
                    found = True
                m+=1
            if (found == False):
                dict_event_copy = copy.deepcopy(dict_event)
                dict_event_copy["sport"] = data[n]["sport"]
                dict_event_copy["competition"] = data[n]["competition"]
                dict_event_copy["message"] = line
                list_events.append(dict_event_copy)
        else:
            dict_event["sport"] = data[n]["sport"]
            dict_event["competition"] = data[n]["competition"]
            dict_event["message"] = line
            list_events.append(dict_event)
        n+=1

    for event in range(len(list_events)):
        emoji = dict_sport_emoji.get(list_events[event]["sport"],"")
        message += emoji+" "+list_events[event]["competition"]+"\n"+list_events[event]["message"]+"\n"

    update.message.reply_text(message)

def find_element(array, key, key2, value, value2):
  for dictionary in array:
    if (dictionary[key] == value and dictionary[key2] == value2):
      return array.index(dictionary)
  return None

def get_json():

    time = datetime.now()
    date = time.strftime("%d%m%Y")

    STORAGEACCOUNTURL = "https://scraperlogs.blob.core.windows.net"
    STORAGEACCOUNTKEY = os.environ.get('STORAGEACCOUNTKEY')
    CONTAINERNAME = "logs"
    BLOBNAME = "log_"+date+".json"
    # BLOBNAME = "myblob"
    blob_service_client = BlobServiceClient(STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY)

    download_file_path = os.path.join(os.getcwd(), str.replace("log.json" ,'.txt', 'DOWNLOAD.txt'))

    container_client = blob_service_client.get_container_client(container= CONTAINERNAME) 
    
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(BLOBNAME).readall())

    return "log.json"

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    telegram_updater = os.environ.get('TELEGRAM_UPDATER')
    updater = Updater(telegram_updater)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("awesome", awesome_command))
    dispatcher.add_handler(CommandHandler("tv", tv))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
