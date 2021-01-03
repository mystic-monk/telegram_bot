import sys
import os
# from box import Box
import yaml
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging

#Enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


# Load from yaml file
# Here it is also possible to use PyYAML arguments, 
# for example to specify different loaders e.g. SafeLoader or FullLoader
# config = Box.from_yaml(filename="./config.yaml", Loader=yaml.SafeLoader)

def restricted_user_space(update, context):
    update.message.reply_text('Hi, Welcome to Nirats Bot')

# def start(update, context):
def start(update, context):
    '''Send a message when the command /start is issued.'''
    user = update.message.from_user
    send = f"{user.username} started your bot. \n First name {user.first_name} \n ID:{user.id}"

    # bot.send_message(chat_id=user_id, text=send)
    update.message.reply_text(send)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('COMMANDS \n /view_events@eventattendbot \n /add_event@eventattendbot \n '
                              '/remove_event@eventattendbot \n')

def message(update, context):
    update.message.reply_text(f"Command: {update.message.text}")

def recieve_image(update, context):
    try:
        print(update)
        obj = context.bot.getfile(file_id=update.message.document.file_id)
        obj.download()
        update.message.reply_text("File has been downloaded.")
    except Exception as e:
        print(str(e))

def recieve_audio(update, context):
    try:
        print(update)
        audio_obj = context.bot.getfile(file_id=update.message.audio.file_id)
        audio_obj.download()
        update.message.reply_text("Your audio has been processed.")
    except Exception as e:
        print(str(e))
           
def command_handler(update, context):
    # context.bot.send_message(chat_id=update.effective_chat_id, text=dir(update.effective_chat))
    update.message.reply_text(f"Command: {update.message.text}")

def error(update, context, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error) 
    
def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    config = yaml.load(open(os.path.join(base_path, 'config.yaml')).read(), Loader=yaml.FullLoader)

    ## start the bot 
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(MessageHandler(Filters.text, message))
    # dp.add_handler(MessageHandler(Filters.command, command_handler))
    dp.add_handler(MessageHandler(Filters.audio, recieve_audio))
    dp.add_handler(MessageHandler(Filters.document.jpg, recieve_image))

    # user handler to restrict the user with chat id
    user_handler = MessageHandler(Filters.chat(username=config['general']['usernames']), restricted_user_space)
    dp.add_handler(user_handler)
    dp.add_error_handler(error)
    run(updater)

 
    # start polling for updates from Telegram
    # updater.start_polling()
    # print('Started!')
    # # block until a signal (like one sent by CTRL+C) is sent
    # updater.idle()

if __name__ == '__main__':
    main()
