import asyncio, os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from yt_dlp.utils import DownloadError
from config import Config
from helpers import download_progress_hook

app = Client("ytdl_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)

if os.path.exists("downloads"):
    print("Download Path Exist")
else:
    print("Download Path Created")

active_list = []
queue = []

async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)

def link_fil(filter, client, update):
    if "http" in update.text:
        return True
    else:
        return False

link_filter = filters.create(link_fil, name="link_filter")


@app.on_message(filters.command("start"))
async def start(client, message : Message):
    await message.reply("Hi, I am yt-dlp bot.\nI can download videos from many sites.\n\nSend a video URL to get started.")

@app.on_message(link_filter)
async def options(client, message : Message):
    print(message.text)
    await message.reply("Which quality you want?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("240p", f"240 {message.text}")], [InlineKeyboardButton("480p", f"480 {message.text}")], [InlineKeyboardButton("720p", f"720 {message.text}")], [InlineKeyboardButton("1080p", f"1080 {message.text}")]]))

@app.on_callback_query()
async def download_video(client, callback : CallbackQuery):
    url = callback.data.split(" ",1)[1]
    quality = callback.data.split()[0]
    msg = await callback.message.edit("Downloading...")
    user_id = callback.message.from_user.id

    if user_id in active_list:
        await callback.message.edit("Sorry! You can download only one video at a time")
        return
    else:
        active_list.append(user_id)

    ydl_opts = {
            "format": f"best[height<={quality}]",
            "progress_hooks": [lambda d: download_progress_hook(d, callback.message, client)]
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            await run_async(ydl.download, [url])
        except DownloadError:
            await callback.message.edit("Sorry, There was a problem with that particular video")
            return

    for file in os.listdir('.'):
        if file.endswith(".mp4"):
            await callback.message.reply_video(f"{file}", caption="**Here Is your Requested Video**\n@SJ_Bots",
                                reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))
            os.remove(f"{file}")
            break
        else:
            continue

    await msg.delete()
    active_list.remove(user_id)


@app.on_message(filters.command("cc"))
async def download_video(client, message : Message):
    files = os.listdir("downloads")
    await message.reply(files)




app.run()
