from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("Send TikTok link only.")
        return

    await update.message.reply_text("Processing... ⚡")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()

        if res.get("data"):
            data = res["data"]

            # 🎥 VIDEO FIRST (NO WATERMARK)
            if data.get("play"):
                video_url = data["play"]
                await update.message.reply_video(video=video_url)
                return

            # 🖼 PHOTO (SLIDESHOW)
            images = data.get("images", [])
            if images:
                for i in range(0, len(images), 10):
                    batch = images[i:i+10]
                    media = [InputMediaPhoto(media=img) for img in batch]
                    await update.message.reply_media_group(media)
                return

            # 🎵 AUDIO LAST
            if data.get("music"):
                audio_url = data["music"]
                await update.message.reply_audio(audio=audio_url)
                return

        await update.message.reply_text("Cannot download 😢")

    except Exception as e:
        print(e)
        await update.message.reply_text("Error 😢")

print("Bot is running...")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()