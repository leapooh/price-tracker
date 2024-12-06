#!/usr/bin/env python

import asyncio
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import ConfigManager

config = ConfigManager()
config = config.read()
manager = ConfigManager()

admin = config["admin"]
password = config["password"]
log = config["log"]
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id == admin:
        await update.message.reply_html(
            rf"Hi {user.mention_html()}, welcome!",
            reply_markup=ForceReply(selective=True),
        )
    else:
        await update.message.reply_html(
            rf"Hi {user.mention_html()}, you don't have permissions to use this bot",
            reply_markup=ForceReply(selective=True),
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        await update.message.reply_text("Commands:\n\n/stop_bot\n/start_bot\n/settings\n/execute_command\n/help")
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        await update.message.reply_text("Are you sure you want to stop the bot? (yes/no)")
        user_data[update.effective_user.id] = "stop_bot"
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        manager.update("enabled", True)
        manager.save()
        await update.message.reply_text("Bot started.")
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        await update.message.reply_text("Please reply with a percentage")
        user_data[update.effective_user.id] = "settings"
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        await update.message.reply_text("Please reply with a command as root")
        user_data[update.effective_user.id] = "execute_command"
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == admin:
        await update.message.reply_text("Type /help to display all available commands")
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id == admin:
        if user_id in user_data:
            if user_data[user_id] == "stop_bot":
                if update.message.text.lower() == "yes":
                    manager.update("enabled", False)
                    manager.save()
                    await update.message.reply_text("Bot stopped.")
                else:
                    await update.message.reply_text("Action canceled.")
                del user_data[user_id]
            elif user_data[user_id] == "settings":
                try:
                    percentage_value = float(update.message.text)
                    if 0.01 <= percentage_value <= 100:
                        manager.update("tolerance", percentage_value)
                        manager.save()
                        await update.message.reply_text(f"Percentage set to {percentage_value}.")
                    else:
                        await update.message.reply_text("Please enter a value between 0.01 and 100.")
                except ValueError:
                    await update.message.reply_text("Invalid input. Please enter a number.")
                del user_data[user_id]
            elif user_data[user_id] == "execute_command":
                try:
                    command = update.message.text
                    stdout, stderr, returncode = await run_command(command, password)
                    with open(log, 'w') as file:
                        file.write(stdout.decode() + stderr.decode())
                    if returncode == 0:
                        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(log, 'rb'), caption="Success")
                    else:
                        await update.message.reply_text("Failed")
                        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(log, 'rb'), caption="Failed")
                except Exception as ex:
                    await update.message.reply_text(f"An error occurred: {str(ex)}")
                del user_data[user_id]
        else:
            await update.message.reply_text("I'm sorry, I didn't understand that.")
    else:
        await update.message.reply_text("You don't have permissions to use this bot")


async def run_command(command, password):
    full_command = f'echo "{password}" | sudo -S {command}'

    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    return stdout, stderr, process.returncode


def main() -> None:
    token = config["token"]
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stop_bot", stop_bot))
    application.add_handler(CommandHandler("start_bot", start_bot))
    application.add_handler(CommandHandler("start_bot", start_bot))
    application.add_handler(CommandHandler("execute_command", execute_command))
    application.add_handler(CommandHandler("settings", settings))

    application.add_handler(MessageHandler(filters.REPLY, handle_reply))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
