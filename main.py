import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from yt_dlp import YoutubeDL

# Твой токен вставлен напрямую (Строка 10)
BOT_TOKEN = '8928787007:AAEO_aJiHQmr8fX2zzj_i0kAXYj2EHyvtF4'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_video(url):
    """Функция для скачивания видео"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'cookiefile': 'cookiesyou.txt', # <--- ДОБАВЛЯЕМ ЭТУ СТРОЧКУ
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне ссылку на видео (YouTube, TikTok, Instagram), и я скачаю его для тебя.")

@dp.message()
async def handle_url(message: types.Message):
    url = message.text
    if "http" not in url:
        await message.answer("Пожалуйста, отправь корректную ссылку на видео.")
        return

    status_msg = await message.answer("Начинаю загрузку видео. Пожалуйста, подождите...")

    try:
        filename = await asyncio.to_thread(download_video, url)
        video_file = FSInputFile(filename)
        await message.answer_video(video_file)
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await message.answer(f"Произошла ошибка при скачивании.\nТекст ошибки: {e}")

# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_web(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render сам задаст нужный порт через переменную PORT
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
# --------------------------------------

async def main():
    # Запускаем заглушку одновременно с ботом
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
