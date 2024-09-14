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
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from azure.storage.blob import BlobServiceClient

from datetime import datetime

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
# def start(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     update.message.reply_markdown_v2(
#         rf"Hi {user.mention_markdown_v2()}\!",
#         reply_markup=ForceReply(selective=True),
#     )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Type /tv or use the side menu to receive the TV updates")


def awesome_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Marina, you are awesome!🥳")


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    # update.message.reply_text(update.message.text)
    update.message.reply_text("Please type /tv to start using the bot")


def tv(update: Update, context: CallbackContext) -> None:

    args = context.args
    day = args[0] if args else None
    cadena = args[1] if len(args) > 1 else None
    data = None

    # init day 0
    # today = data[0]["day"]
    line = ""
    list_events = []
    dict_event = {}
    found = True
    n = 0

    # with open(get_json(day)) as f:
    #     data = json.load(f)

    if day is None:
        with open(get_json(day)) as f:
            data = json.load(f)
        day = data[0]["day"]
    else:
        with open("log_1902.json") as f:
            data = json.load(f)

    # If cadena is provided, filter data to include only matches containing the cadena
    if cadena:
        data = [d for d in data if cadena.lower() in d["match"].lower()]

    # Si no hay resultados después del filtrado, enviar un mensaje indicando que no se encontraron resultados
    if not data:
        update.message.reply_text("No results :(")
        return

    # init message body
    message = "🗓️ " + day + "\n\n"

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
        "Motor": "🏁",
        "UFC": "🥊",
        "JJ.OO.": "🥇"
    }
    dict_event_formated = {
        "liga regular": "Liga",
        "laliga santander": "Liga",
        "liga femenima": "Liga Femenina",
        "dakar": "DAKAR",
        "premier league": "Premier",
        "united cup": "United Cup",
    }

    while n < len(data):
        emoji = dict_sport_emoji.get(data[n]["sport"], "")
        line = (
            data[n]["time"]
            + " "
            + data[n]["match"]
            + " ("
            + data[n]["channel"]
            + ")"
            + "\n"
        )

        if n > 0:
            m = 0
            found = False
            while m < n and found == False:
                if (
                    data[m]["sport"] == data[n]["sport"]
                    and data[m]["competition"] == data[n]["competition"]
                ):
                    dict_event_copy = copy.deepcopy(dict_event)
                    result = find_element(
                        list_events,
                        "sport",
                        "competition",
                        data[m]["sport"],
                        data[m]["competition"],
                    )
                    dict_event_copy = list_events[result]
                    dict_event_copy["message"] = dict_event_copy["message"] + line
                    found = True
                m += 1
            if found == False:
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
        n += 1

    for event in range(len(list_events)):
        emoji = dict_sport_emoji.get(list_events[event]["sport"], "")
        message += (
            emoji
            + " "
            + list_events[event]["competition"]
            + "\n"
            + list_events[event]["message"]
            + "\n"
        )

    update.message.reply_text(message)


def find_element(array, key, key2, value, value2):
    for dictionary in array:
        if dictionary[key] == value and dictionary[key2] == value2:
            return array.index(dictionary)
    return None


def get_json(day=None):

    if day is None:
        time = datetime.now()
        date = time.strftime("%d%m%Y")
    else:
        date_object = datetime.strptime(day, "%d%m")
        date = date_object.strftime("%d de %B de %Y")

    # time = datetime.now()
    # date = time.strftime("%d%m%Y")

    STORAGEACCOUNTURL = "https://scraperlogs.blob.core.windows.net"
    STORAGEACCOUNTKEY = os.environ.get("STORAGEACCOUNTKEY")
    CONTAINERNAME = "logs"
    BLOBNAME = "log_" + date + ".json"
    # BLOBNAME = "test.json"

    blob_service_client = BlobServiceClient(
        STORAGEACCOUNTURL, credential=STORAGEACCOUNTKEY
    )

    download_file_path = os.path.join(
        os.getcwd(), str.replace("log.json", ".txt", "DOWNLOAD.txt")
    )

    container_client = blob_service_client.get_container_client(container=CONTAINERNAME)

    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(BLOBNAME).readall())

    if day is not None:
        # Filtrar el archivo según el día
        filtered_data = []
        with open(download_file_path, "r") as json_file:
            data = json.load(json_file)
            for entry in data:
                if entry.get("day") == day:
                    filtered_data.append(entry)

        # Escribir los datos filtrados en el archivo
        with open(download_file_path, "w") as json_file:
            json.dump(filtered_data, json_file)

    return download_file_path


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    telegram_updater = os.environ.get("TELEGRAM_UPDATER")
    # telegram_updater = os.environ.get("TELEGRAM_UPDATER_DEV")
    updater = Updater(telegram_updater)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("awesome", awesome_command))
    dispatcher.add_handler(CommandHandler("tv", tv))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
