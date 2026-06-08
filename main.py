import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from yt_dlp import YoutubeDL

# Твой токен вставлен напрямую
BOT_TOKEN = '8928787007:AAGEMfcyBRsRjBjM6P8Xyi6EAcIGsqxv5dI'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_video(url):
    """
    Функция для скачивания видео с помощью yt-dlp.
    Возвращает имя скачанного файла.
    """
    ydl_opts = {
        'format': 'best', # Выбирает лучшее доступное качество
        'outtmpl': '%(id)s.%(ext)s', # Формат имени файла
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне ссылку на видео (YouTube, TikTok, Instagram), и я скачаю его для тебя.")

@dp.message()
async def handle_url(message: types.Message):
    url = message.text
    
    # Базовая проверка, что текст похож на ссылку
    if "http" not in url:
        await message.answer("Пожалуйста, отправь корректную ссылку на видео.")
        return

    # Сообщаем пользователю, что процесс пошел
    status_msg = await message.answer("Начинаю загрузку видео. Пожалуйста, подождите...")

    try:
        # Запускаем скачивание в отдельном потоке
        filename = await asyncio.to_thread(download_video, url)

        # Отправляем файл пользователю
        video_file = FSInputFile(filename)
        await message.answer_video(video_file)
        
        # Удаляем файл с сервера после отправки, чтобы не забивать память
        os.remove(filename)
        
        # Удаляем сообщение "Начинаю загрузку..."
        await status_msg.delete()
        
    except Exception as e:
        await message.answer(f"Произошла ошибка при скачивании: проверьте ссылку или попробуйте позже.\nТекст ошибки: {e}")

async def main():
    # Запуск процесса поллинга (ожидания новых сообщений)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
