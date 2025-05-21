import sys
import inspect

TOKEN = "YOUR_BOT_TOKEN"

'''
#################
^^^ enter your telegram bot token above

^^^ введите свой токен telegram-бота выше
#################
'''

LIBRARIES = {
    '1': False,
    '2': False,
    '3': False
}

try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.utils import executor
    LIBRARIES['1'] = True
except ImportError:
    pass

try:
    from telegram import Update, Bot as PTBBot
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    LIBRARIES['2'] = True
except ImportError:
    pass

try:
    import telebot
    from telebot import TeleBot
    LIBRARIES['3'] = True
except ImportError:
    pass

COMMAND_TEXT = """Write to me to buy this bot.\n\nНапишите мне, чтобы купить этого бота\n===\n\n

@roman_tgbot / @ftdt800

"""

class BotHandler:
    @staticmethod
    def create_bot(token):
        if LIBRARIES['1']:
            return AiogramBot(token)
        if LIBRARIES['2']:
            return PTBBotWrapper(token)
        if LIBRARIES['3']:
            return TeleBotWrapper(token)
        raise RuntimeError("No supported libraries installed")

class BaseBot:
    def __init__(self, token):
        self.token = token
    
    def start(self):
        raise NotImplementedError

    def _is_async(self):
        return inspect.iscoroutinefunction(self.start)

class AiogramBot(BaseBot):
    def __init__(self, token):
        super().__init__(token)
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)
        
        @self.dp.message_handler(commands=['start', 'help'])
        async def send_welcome(message: types.Message):
            await message.reply(COMMAND_TEXT)
            
        @self.dp.message_handler()
        async def echo(message: types.Message):
            await message.answer(message.text)

    def start(self):
        executor.start_polling(self.dp, skip_updates=True)

class PTBBotWrapper(BaseBot):
    def __init__(self, token):
        super().__init__(token)
        self.updater = Updater(token)
        
        def start(update: Update, context: CallbackContext):
            update.message.reply_text(COMMAND_TEXT)
            
        def echo(update: Update, context: CallbackContext):
            update.message.reply_text(update.message.text)
            
        self.updater.dispatcher.add_handler(CommandHandler(['start', 'help'], start))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

class TeleBotWrapper(BaseBot):
    def __init__(self, token):
        super().__init__(token)
        self.bot = TeleBot(token)
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, COMMAND_TEXT)
            
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            self.bot.reply_to(message, message.text)

    def start(self):
        self.bot.polling(none_stop=True)

if __name__ == '__main__':
    try:
        bot = BotHandler.create_bot(TOKEN)
        
        if bot._is_async():
            import asyncio
            asyncio.run(bot.start())
        else:
            bot.start()
    except RuntimeError as e:
        sys.exit(1)