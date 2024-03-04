from pyrogram import filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db
from helper.token import none_admin_utils
from asyncio import sleep
from PIL import Image
import os, time
from Krito import ubot, pbot
import asyncio, re

# Your regular expression for season and episode extraction
pattern = re.compile(r'(?:s|season)?\s*(\d{1,2})\s*[_\-\s]?(?:e|ep|x|episode)?\s*(\d{1,2})', re.IGNORECASE)

@pbot.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    try:
        user_id = message.from_user.id
        none_admin_msg, error_buttons = await none_admin_utils(message)
        error_msg = []
        if none_admin_msg:
            error_msg.extend(none_admin_msg)
            await client.send_message(
                chat_id=message.chat.id,
                text='\n'.join(error_msg),
                reply_markup=InlineKeyboardMarkup(error_buttons)
            )
            return

        file = getattr(message, message.media.value)

        if file.file_size > 3.2 * 1024 * 1024 * 1024:
            await message.reply_text("Sorry, this bot doesn't support uploading files bigger than 3.2GB")
            return
        elif file.file_size > 1.9 * 1024 * 1024 * 1024:
            if ubot and ubot.is_connected:
                form_list = await db.get_template(user_id)
                uploadtype = await db.get_uploadtype(user_id)
                exten = await db.get_exten(user_id)
                if form_list is None or uploadtype is None or exten is None:
                    return await message.reply_text("Please set template, uploadtype, extension")
            else:
                await message.reply_text("+4gb not active to process it. Anyone wanna donate string to enable 4gb Contact owner @devil_testing_bot", reply_to_message_id=message.id)
                return
        else:
            form_list = await db.get_template(user_id)
            uploadtype = await db.get_uploadtype(user_id)
            exten = await db.get_exten(user_id)
            if form_list is None or uploadtype is None or exten is None:
                return await message.reply_text("Please set template, uploadtype, extension")

        filename = file.file_name
        match = pattern.search(filename)
        if match:
            season, episode = match.groups()

            for form_template in form_list:
                filled_form = form_template.format(season=season, episode=episode, cz_name=filename)
                new_file_name = f"{filled_form}.{exten}"
                file_path = f"downloads/{new_file_name}"
                
        ms = await message.reply_text("Trying To Downloading....")
        try:
            path = await client.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("Download Started....", ms, time.time()))
        except Exception as e:
            await ms.edit(str(e))
            return
        duration = 0
        resolution = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').second
            if metadata.has("resolution"):
                resolution = metadata.get("resolution")
        except:
            pass

        ph_path = None
        c_caption = await db.get_caption(user_id)
        c_thumb = await db.get_thumbnail(user_id)

        if c_caption:
            try:
                caption = c_caption.format(filename=new_filename, filesize=humanbytes(file.file_size), duration=convert(duration), resolution=(resolution))
            except Exception as e:
                await ms.edit(text=f"Your Caption Error Except Keyword Argument ●> ({e})")
                return
        else:
            caption = f"**{new_filename}**"
            
        if media.thumbs or c_thumb:
            if c_thumb:
                ph_path = await bot.download_media(c_thumb)
            else:
                ph_path = await bot.download_media(media.thumbs[0].file_id)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")

        value = 1.9 * 1024 * 1024 * 1024
        chat_id = await db.get_chat_id(user_id)
        if file.file_size > value:
            fupload = int(-1001682783965)
            client = ubot
        else:
            client = pbot
            
        await ms.edit("Trying To Uploading....")
        type = uploadtype
        try:
            if type == "document":
                suc = await client.send_document(
                    chat_id=fupload,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started....", ms, time.time())
                )
            elif type == "video":
                suc = await client.send_video(
                    chat_id=fupload,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started....", ms, time.time())
                )
            elif type == "audio":
                suc = await client.send_audio(
                    chat_id=fupload,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload Started....", ms, time.time())
                )

            if client == ubot:
                await pbot.copy_message(
                    chat_id=chat_id if chat_id is not None else update.message.chat.id,
                    from_chat_id=suc.chat.id,
                    message_id=suc.message_id
                )
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            await ms.edit(f"Error: {e}")
            return

        await ms.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

    except Exception as e:
        await update.message.edit_text(f"An error occurred: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
