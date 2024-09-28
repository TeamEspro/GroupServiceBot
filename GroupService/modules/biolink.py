from GroupService import pbot as app
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import re

url_pattern = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*'
)

warnings = {}
punishment = {}

default_warning_limit = 3  # Default Warning Limit
default_punishment = "mute" # Default punishment Limit 
default_punishment_set = ("warn", default_warning_limit, default_punishment)

async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

async def has_permissions(client, chat_id, user_id, permissions):
    chat_member = await client.get_chat_member(chat_id, user_id)
    for perm in permissions:
        if not getattr(chat_member.privileges, perm, False):
            return False
    return True

# Configuration handler
@app.on_message(filters.group & filters.command("config"))
async def configure(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("<b>❌ You are not administrator</b>", parse_mode=enums.ParseMode.HTML)
        await message.delete()  # Delete the command message
        return

    current_punishment = punishment.get(chat_id, default_punishment_set)[2]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn", callback_data="warn")],
        [InlineKeyboardButton("Mute ✅" if current_punishment == "mute" else "Mute", callback_data="mute"), 
         InlineKeyboardButton("Ban ✅" if current_punishment == "ban" else "Ban", callback_data="ban")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    await message.reply_text("<b>Select punishment for users who have links in their bio:</b>", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    await message.delete()  # Delete the command message

# Callback handler for punishments and warnings
@app.on_callback_query()
async def callback_handler(client, callback_query):
    # Callback query ke data ko handle karein
    data = callback_query.data
    
    if data == "option1":
        await callback_query.message.reply_text("You selected option 1!")
    elif data == "option2":
        await callback_query.message.reply_text("You selected option 2!")
    
    # Acknowledge the callback
    await callback_query.answer()


# Bio link check
@app.on_message(filters.group)
async def check_bio(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Fetch user bio
    user_full = await client.get_chat(user_id)
    bio = user_full.bio
    if user_full.username:
        user_name = f"@{user_full.username} [<code>{user_id}</code>]"
    else:
        user_name = f"{user_full.first_name} {user_full.last_name} [<code>{user_id}</code>]" if user_full.last_name else f"{user_full.first_name} [<code>{user_id}</code>]"

    if bio and re.search(url_pattern, bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            await message.reply_text("Please grant me delete permission.")
            return

        action = punishment.get(chat_id, default_punishment_set)
        if action[0] == "warn":
            if user_id not in warnings:
                warnings[user_id] = 0
            warnings[user_id] += 1
            sent_msg = await message.reply_text(f"{user_name} please remove any links from your bio. warned {warnings[user_id]}/{action[1]}", parse_mode=enums.ParseMode.HTML)
            if warnings[user_id] >= action[1]:
                try:
                    if action[2] == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute ✅", callback_data=f"unmute_{user_id}")]])
                        await sent_msg.edit(f"{user_name} has been 🔇 muted for [ Link In Bio ].", reply_markup=keyboard)
                    elif action[2] == "ban":
                        await client.ban_chat_member(chat_id, user_id)
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Unban ✅", callback_data=f"unban_{user_id}")]])
                        await sent_msg.edit(f"{user_name} has been 🔨 banned for [ Link In Bio ].", reply_markup=keyboard)
                except errors.ChatAdminRequired:
                    await sent_msg.edit(f"I don't have permission to {action[2]} users.")
        elif action[0] == "mute":
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute", callback_data=f"unmute_{user_id}")]])
                await message.reply_text(f"{user_name} has been 🔇 muted for [ Link In Bio ].", reply_markup=keyboard)
            except errors.ChatAdminRequired:
                await message.reply_text("I don't have permission to mute users.")
        elif action[0] == "ban":
            try:
                await client.ban_chat_member(chat_id, user_id)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Unban", callback_data=f"unban_{user_id}")]])
                await message.reply_text(f"{user_name} has been 🔨 banned for [ Link In Bio ].", reply_markup=keyboard)
            except errors.ChatAdminRequired:
                await message.reply_text("I don't have permission to ban users.")
    else:
        if user_id in warnings:
            del warnings[user_id]

# Added message link deletion
@app.on_message(filters.group & filters.text)
async def check_links(client, message):
    chat_id = message.chat.id
    text = message.text

    # Check if the message contains a URL using regex
    if re.search(url_pattern, text):
        try:
            await message.delete()  # Delete the message with a link
        except errors.MessageDeleteForbidden:
            await message.reply_text("I don't have permission to delete messages.")
        else:
            await message.reply_text(f"<b>❌ Links are not allowed in this group.</b>", parse_mode=enums.ParseMode.HTML)
