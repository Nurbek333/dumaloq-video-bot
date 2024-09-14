from loader import dp, bot
from aiogram import F, types
from aiogram.types import FSInputFile
from pathlib import Path
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop
import os
import logging

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)

download_path = Path().joinpath("videos")
download_path.mkdir(parents=True, exist_ok=True)

@dp.message(F.video)
async def echo(message: types.Message):
    if message.video.duration > 60 * 3:
        await message.answer("Iltimos 3 minutdan kam bo'lgan video yuboring...")
        return
    
    name = None
    kname = None

    try:
        await bot.send_chat_action(message.chat.id, 'record_video_note')

        # Video faylni yuklab olish
        file_path = download_path / "temp_video.mp4"
        await bot.download(file=message.video.file_id, destination=file_path)
        
        if not file_path.exists():
            raise Exception("Faylni yuklab olishda xatolik")
        
        name = file_path.name
        logging.info(f"Yuklab olingan fayl yo'li: {file_path}")

        clips = VideoFileClip(str(file_path))
        start = 0
        while start < clips.duration:
            end = min(start + 60, clips.duration)
            clip = clips.subclip(start, end)

            width, height = clip.size

            if width > height:
                if height > 640:
                    height = 640
                x_center = width / 2
                x1 = x_center - height / 2
                x2 = x_center + height / 2
                y1 = 0
                y2 = height
            else:
                if width > 640:
                    width = 640
                y_center = height / 2
                y1 = y_center - width / 2
                y2 = y_center + width / 2
                x1 = 0
                x2 = width

            square_clip = clip.fx(crop, x1=x1, y1=y1, x2=x2, y2=y2)
            kname = download_path / (name.split('.')[0] + f'_{start}.mp4')
            square_clip.write_videofile(str(kname))

            await message.answer("Tayyor 🚀🚀🚀")
            await bot.send_chat_action(message.chat.id, 'record_video_note')
            await bot.send_video_note(chat_id=message.chat.id, video_note=FSInputFile(path=str(kname)))
            
            start += 60
        
    except Exception as ex:
        logging.error("Xatolik yuz berdi: %s", ex)
        if kname and kname.exists():
            try:
                os.remove(kname)
            except Exception as cleanup_ex:
                logging.error("Tozalash xatosi: %s", cleanup_ex)
        await message.answer("Xatolik yuz berdi")
    
    finally:
        if name and (download_path / name).exists():
            os.remove(download_path / name)
        if (download_path / "temp_video.mp4").exists():
            os.remove(download_path / "temp_video.mp4")