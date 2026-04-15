from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
import os
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

def expand_url(short_url):
    try:
        r = requests.get(short_url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return short_url

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("Send TikTok link only.")
        return

    await update.message.reply_text("Processing... ⚡")

    try:
        url = expand_url(url)

        # 🔹 FIRST TRY: TikWM API
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url).json()

        if res.get("data"):
            data = res["data"]

            video_url = data.get("play") or data.get("wmplay")
            audio_url = data.get("music")
            images = data.get("images", [])[:30]

            if video_url:
                await update.message.reply_video(video=video_url)
                if audio_url:
                    await update.message.reply_audio(audio=audio_url)
                return

            if images:
                for i in range(0, len(images), 10):
                    batch = images[i:i+10]
                    media = [InputMediaPhoto(media=img) for img in batch]
                    await update.message.reply_media_group(media)

                if audio_url:
                    await update.message.reply_audio(audio=audio_url)
                return

            if audio_url:
                await update.message.reply_audio(audio=audio_url)
                return

        # 🔥 SECOND TRY: yt-dlp fallback (force video)
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            await update.message.reply_video(video=open(file_name, "rb"))
            os.remove(file_name)

    except Exception as e:
        print(e)
        await update.message.reply_text("Error 😢")

print("Bot is running...")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()