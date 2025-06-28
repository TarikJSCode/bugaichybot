import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

async def reply_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_hello))
    app.run_polling()
