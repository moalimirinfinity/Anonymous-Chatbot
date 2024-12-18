import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for user management
waiting_users = []  # Users waiting for a chat partner
active_chats = {}  # Maps user_id to partner_id

# Command: /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        "Welcome to Anonymous Chat Bot! Use /connect to find a chat partner or /help for more options."
    )

# Command: /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "/start - Start the bot\n/connect - Connect to a random user\n/next - Find a new chat partner\n/stop - End the chat"
    )

# Command: /connect
def connect(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if the user is already in an active chat
    if user_id in active_chats:
        update.message.reply_text("You're already in a chat. Use /stop to leave your current chat.")
        return

    # Check for available users
    if waiting_users:
        partner_id = waiting_users.pop(0)

        # Ensure the user does not get paired with themselves
        if partner_id == user_id:
            waiting_users.append(partner_id)
            update.message.reply_text("Retrying to find a partner...")
            connect(update, context)
            return

        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        context.bot.send_message(partner_id, "You have been connected to a new chat partner! Say hi!")
        update.message.reply_text("You are now connected to a chat partner! Say hi!")
    else:
        waiting_users.append(user_id)
        update.message.reply_text("Waiting for a chat partner...")

# Command: /next
def next(update: Update, context: CallbackContext) -> None:
    stop(update, context)  # Stop the current chat if any
    connect(update, context)  # Find a new chat partner

# Command: /stop
def stop(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if the user is in an active chat
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)

        context.bot.send_message(partner_id, "Your chat partner has left the chat.")
        update.message.reply_text("You have left the chat.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        update.message.reply_text("You have left the waiting queue.")
    else:
        update.message.reply_text("You're not in a chat or waiting queue.")

# Handle messages
def relay_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if the user is in an active chat
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        if partner_id in active_chats and active_chats[partner_id] == user_id:
            context.bot.send_message(partner_id, update.message.text)
        else:
            update.message.reply_text("Your chat partner is no longer available. Use /connect to find a new partner.")
    else:
        update.message.reply_text("You're not in a chat. Use /connect to find a partner.")

# Main function to run the bot
def main() -> None:
    # Replace 'YOUR_TOKEN_HERE' with your bot token
    updater = Updater("123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("connect", connect))
    dispatcher.add_handler(CommandHandler("next", next))
    dispatcher.add_handler(CommandHandler("stop", stop))

    # Register message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, relay_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
