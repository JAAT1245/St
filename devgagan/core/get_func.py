import asyncio
import time
import os
import re
import subprocess
import requests
from devgagan import app
from devgagan import sex as gf
from telethon.tl.types import DocumentAttributeVideo
import pymongo
from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, PeerIdInvalid
from pyrogram.enums import MessageMediaType
from devgagan.core.func import progress_bar, video_metadata, screenshot, chk_user, progress_callback, prog_bar
from devgagan.core.mongo import db
from devgagan.modules.shrink import is_user_verified
from pyrogram.types import Message
from config import MONGO_DB as MONGODB_CONNECTION_STRING, LOG_GROUP, OWNER_ID, STRING
import cv2
import random
from devgagan.core.mongo.db import set_session, remove_session, get_data
import string
from telethon import events, Button
from io import BytesIO
from SpyLib import fast_upload
def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else None
DB_NAME = "smart_users"
COLLECTION_NAME = "super_user"
VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'webm', 'mpg', 'mpeg', '3gp', 'ts', 'm4v', 'f4v', 'vob']
mongo_client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]
if STRING:
    from devgagan import pro
    print("App imported from devgagan.")
else:
    pro = None
    print("STRING is not available. 'app' is set to None.")
async def fetch_upload_method(user_id):
    """Fetch the user's preferred upload method."""
    user_data = collection.find_one({"user_id": user_id})
    return user_data.get("upload_method", "Pyrogram") if user_data else "Pyrogram"
async def get_msg(userbot, sender, edit_id, msg_link, i, message):
    edit = ""
    chat = ""
    progress_message = None
    round_message = False
    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]
    msg_id = int(msg_link.split("/")[-1]) + int(i)
    saved_channel_ids = load_saved_channel_ids()
    if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
        parts = msg_link.split("/")
        if 't.me/b/' not in msg_link:
            chat = int('-100' + str(parts[parts.index('c') + 1]))
        else:
            chat = msg_link.split("/")[-2]
        if chat in saved_channel_ids:
            await app.edit_message_text(message.chat.id, edit_id, "Sorry! dude 😎 This channel is protected 🔐 by **__CR CHOUDHARY__**")
            return
        file = ""
        try:
            size_limit = 2 * 1024 * 1024 * 1024
            chatx = message.chat.id
            msg = await userbot.get_messages(chat, msg_id)
            target_chat_id = user_chat_ids.get(chatx, chatx)
            freecheck = await chk_user(message, sender)
            verified = await is_user_verified(sender)
            original_caption = msg.caption if msg.caption else ''
            custom_caption = get_user_caption_preference(sender)
            final_caption = f"{original_caption}" if custom_caption else f"{original_caption}"       
            replacements = load_replacement_words(sender)
            for word, replace_word in replacements.items():
                final_caption = final_caption.replace(word, replace_word)
            caption = f"{final_caption}\n\n__**{custom_caption}**__" if custom_caption else f"{final_caption}"
            custom_rename_tag = get_user_rename_preference(chatx)
            upload_method = await fetch_upload_method(sender)
            delete_words = load_delete_words(chatx)
            if msg.service is not None:
                return None 
            if msg.empty is not None:
                return None
            if msg.media:
                if msg.media == MessageMediaType.WEB_PAGE:
                    target_chat_id = user_chat_ids.get(chatx, chatx)
                    await edit.edit("Cloning...")
                    devgaganin = await app.send_message(target_chat_id, msg.text.markdown)
                    await devgaganin.copy(LOG_GROUP)                  
                    await edit.delete()
                    return
            if not msg.media:
                if msg.text:
                    target_chat_id = user_chat_ids.get(chatx, chatx)
                    edit = await app.edit_message_text(sender, edit_id, "Cloning...")
                    devgaganin = await app.send_message(target_chat_id, msg.text.markdown)
                    if msg.pinned_message:
                        try:
                            await devgaganin.pin(both_sides=True)
                        except Exception as e:
                            await devgaganin.pin()
                    await devgaganin.copy(LOG_GROUP)
                    await edit.delete()
                    return
            if msg.sticker:
                edit = await app.edit_message_text(sender, edit_id, "Sticker detected...")
                result = await app.send_sticker(target_chat_id, msg.sticker.file_id)
                await result.copy(LOG_GROUP)
                await edit.delete(2)
                return
                    
            file_size = None
            if msg.document or msg.photo or msg.video:
                file_size = msg.document.file_size if msg.document else (msg.photo.file_size if msg.photo else msg.video.file_size)
            if file_size and file_size > size_limit and (freecheck == 1 and not verified):
                await edit.edit("**__❌ File size is greater than 2 GB, purchase premium to proceed or use /token to get 3 hour access for free__")
                return
            edit = await app.edit_message_text(sender, edit_id, "Trying to Download...")
            file = await userbot.download_media(
                msg,
                progress=progress_bar,
                progress_args=("╭─────────────────────╮\n│      **__Downloading__...**\n├─────────────────────",edit,time.time()))
            last_dot_index = str(file).rfind('.')
            if last_dot_index != -1 and last_dot_index != 0:
                ggn_ext = str(file)[last_dot_index + 1:]
                if ggn_ext.isalpha() and len(ggn_ext) <= 9:
                    if ggn_ext.lower() in VIDEO_EXTENSIONS:
                        original_file_name = str(file)[:last_dot_index]
                        file_extension = 'mp4'                 
                    else:
                        original_file_name = str(file)[:last_dot_index]
                        file_extension = ggn_ext
                else:
                    original_file_name = str(file)
                    file_extension = 'mp4'
            else:
                original_file_name = str(file)
                file_extension = 'mp4'
            for word in delete_words:
                original_file_name = original_file_name.replace(word, "")
            replacements = load_replacement_words(chatx)
            for word, replace_word in replacements.items():
                original_file_name = original_file_name.replace(word, replace_word)
            new_file_name = original_file_name + " " + custom_rename_tag + "." + file_extension
            os.rename(file, new_file_name)
            file = new_file_name
            await edit.edit('**__Checking file...__**')
            if os.path.getsize(file) >= 2 * 1024 * 1024 * 1024:
                if pro is None:
                    await edit.edit('**__ ❌ 4GB trigger not found__**')
                    os.remove(file)
                    return
                await edit.edit('**__ ✅ 4GB trigger connected...__**\n\n')
                try:
                    thumb_path = await screenshot(file, duration, chatx)
                    if file_extension in VIDEO_EXTENSIONS:
                        metadata = video_metadata(file)
                        width= metadata['width']
                        height= metadata['height']
                        duration= metadata['duration']
                        dm = await pro.send_video(
                            LOG_GROUP, 
                            video=file,
                            caption=caption,
                            thumb=thumb_path,
                            height=height,
                            width=width,
                            duration=duration,
                            progress=progress_bar,
                            progress_args=(
                                "╭─────────────────────╮\n│       **__4GB Uploader__ ⚡**\n├─────────────────────",
                                edit,
                                time.time()
                            )
                        )
                        from_chat = dm.chat.id
                        from_chat = dm.chat.id
                        mg_id = dm.id
                        await asyncio.sleep(2)
                        await app.copy_message(sender, from_chat, mg_id)
                    else:
                        dm = await pro.send_document(
                            LOG_GROUP, 
                            document=file,
                            caption=caption,
                            thumb=thumb_path,
                            progress=progress_bar,
                            progress_args=(
                                "╭─────────────────────╮\n│      **__4GB Uploader ⚡__**\n├─────────────────────",
                                edit,
                                time.time()
                            )
                        )
                        from_chat = dm.chat.id
                        from_chat = dm.chat.id
                        mg_id = dm.id
                        await asyncio.sleep(2)
                        await app.copy_message(sender, from_chat, mg_id)
                except Exception as e:
                    print(f"Error while sending file: {e}")
                finally:
                    await edit.delete()
                    os.remove(file)
                    return  
            if msg.voice:
                result = await app.send_voice(target_chat_id, file)
                await result.copy(LOG_GROUP)
            elif msg.audio:
                result = await app.send_audio(target_chat_id, file, caption=caption)
                await result.copy(LOG_GROUP)       
            elif msg.media == MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:               
                thumb_path = await screenshot(file, duration, chatx)
                upload_method = await fetch_upload_method(sender)
                try:
                    if upload_method == "Pyrogram":
                        devgaganin = await app.send_video(
                            chat_id=target_chat_id,
                            video=file,
                            caption=caption,
                            supports_streaming=True,
                            height=height,
                            width=width,
                            thumb=thumb_path,
                            duration=duration,
                            progress=progress_bar,
                            progress_args=(
                                "╭─────────────────────╮\n│      **__Pyro Uploader__**\n├─────────────────────",
                                edit,
                                time.time()
                            )
                        )
                        await devgaganin.copy(LOG_GROUP)
                    elif upload_method == "SpyLib":
                        await edit.delete()
                        progress_message = await gf.send_message(sender, "__**Uploading ...**__")
                        uploaded = await fast_upload(
                                gf, file, 
                                reply=progress_message,                 
                                name=None,                
                                progress_bar_function=lambda done, total: progress_callback(done, total, sender)                
                        )
                        await gf.send_file(
                            target_chat_id,
                            uploaded,
                            caption=caption,
                            attributes=[
                                DocumentAttributeVideo(
                                    duration=duration,
                                    w=width,
                                    h=height,
                                    supports_streaming=True
                                )
                            ],
                            thumb=thumb_path
                        )
                except:
                    try:
                        await app.edit_message_text(sender, edit_id, "The bot is not an admin in the specified chat...")
                    except: 
                        await progress_message.edit("Bot is unable to send message to you or specified chat check if it admin or not")
                os.remove(file)
            elif msg.media == MessageMediaType.PHOTO:
                await edit.edit("**Uploading photo...")
                devgaganin = await app.send_photo(chat_id=target_chat_id, photo=file, caption=caption)              
                await devgaganin.copy(LOG_GROUP)
            else:
                try:                    
                    if upload_method == "Pyrogram":
                            devgaganin = await app.send_document(
                            chat_id=target_chat_id,
                            document=file,
                            caption=caption,
                            thumb=thumb_path,
                            progress=progress_bar,
                            progress_args=(
                                "╭─────────────────────╮\n│      **__Pyro Uploader__**\n├─────────────────────",
                                edit,
                                time.time()
                            )
                        )
                            await devgaganin.copy(LOG_GROUP)
                    elif upload_method == "SpyLib":
                            await edit.delete()
                            progress_message = await gf.send_message(sender, "Uploading ...")
                            uploaded = await fast_upload(
                                gf, 
                                file, 
                                reply=progress_message,                 
                                name=None,                
                                progress_bar_function=lambda done, total: progress_callback(done, total, sender)                
                            )
                            await gf.send_file(
                            target_chat_id,
                            uploaded,
                            caption=caption,
                            thumb=thumb_path
                        )
                except Exception:
                    try:
                        await app.edit_message_text(sender, edit_id, "The bot is not an admin in the specified chat.")
                    except:
                        await progress_message.edit("Something Greate happened my jaan")
                os.remove(file)
            await edit.delete()
            if progress_message:
                await progress_message.delete()
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await app.edit_message_text(sender, edit_id, "Have you joined the channel?")
            return
        except Exception as e:
            print(f"Errrrror {e}")
            await edit.delete()    
    else:
        edit = await app.edit_message_text(sender, edit_id, "Cloning...")
        try:
            chat = msg_link.split("/")[-2]
            await copy_message_with_chat_id(app, sender, chat, msg_id) 
            await edit.delete()
        except Exception as e:
            await app.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
async def copy_message_with_chat_id(client, sender, chat_id, message_id):
    target_chat_id = user_chat_ids.get(sender, sender)
    try:
        msg = await client.get_messages(chat_id, message_id)
        custom_caption = get_user_caption_preference(sender)
        original_caption = msg.caption if msg.caption else ''
        final_caption = f"{original_caption}" if custom_caption else f"{original_caption}"        
        delete_words = load_delete_words(sender)
        for word in delete_words:
            final_caption = final_caption.replace(word, '  ')       
        replacements = load_replacement_words(sender)
        for word, replace_word in replacements.items():
            final_caption = final_caption.replace(word, replace_word)    
        caption = f"{final_caption}\n\n__**{custom_caption}**__" if custom_caption else f"{final_caption}"  
        if msg.media:
            if msg.media == MessageMediaType.VIDEO:
                result = await client.send_video(target_chat_id, msg.video.file_id, caption=caption)
            elif msg.media == MessageMediaType.DOCUMENT:
                result = await client.send_document(target_chat_id, msg.document.file_id, caption=caption)
            elif msg.media == MessageMediaType.PHOTO:
                result = await client.send_photo(target_chat_id, msg.photo.file_id, caption=caption)
            else:
                result = await client.copy_message(target_chat_id, chat_id, message_id)
        else:
            result = await client.copy_message(target_chat_id, chat_id, message_id)
        try:
            await result.copy(LOG_GROUP)
        except Exception:
            pass
    except Exception as e:
        error_message = f"Error occurred while sending message to chat ID {target_chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {target_chat_id} and restart the process after /cancel")
user_chat_ids = {}
def load_delete_words(user_id):
    try:
        words_data = collection.find_one({"_id": user_id})
        if words_data:
            return set(words_data.get("delete_words", []))
        else:
            return set()
    except Exception as e:
        print(f"Error loading delete words: {e}")
        return set()
def save_delete_words(user_id, delete_words):
    try:
        collection.update_one(
            {"_id": user_id},
            {"$set": {"delete_words": list(delete_words)}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving delete words: {e}")
def load_replacement_words(user_id):
    try:
        words_data = collection.find_one({"_id": user_id})
        if words_data:
            return words_data.get("replacement_words", {})
        else:
            return {}
    except Exception as e:
        print(f"Error loading replacement words: {e}")
        return {}
def save_replacement_words(user_id, replacements):
    try:
        collection.update_one(
            {"_id": user_id},
            {"$set": {"replacement_words": replacements}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving replacement words: {e}")
user_rename_preferences = {}
user_caption_preferences = {}
def load_user_session(sender_id):
    user_data = collection.find_one({"user_id": sender_id})
    if user_data:
        return user_data.get("session")
    else:
        return None
async def set_rename_command(user_id, custom_rename_tag):
    user_rename_preferences[str(user_id)] = custom_rename_tag
def get_user_rename_preference(user_id):
    return user_rename_preferences.get(str(user_id), 'Team SPY')
async def set_caption_command(user_id, custom_caption):
    user_caption_preferences[str(user_id)] = custom_caption
def get_user_caption_preference(user_id):
    return user_caption_preferences.get(str(user_id), '')
sessions = {}
SET_PIC = "https://iili.io/2ELZVm7.md.jpg"
MESS = "Customize by your end and Configure your s
