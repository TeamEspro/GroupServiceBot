from GroupService import pbot as app
from pyrogram import Client, filters

# Filter for forwarded messages
@app.on_message(filters.forwarded & filters.group)
async def delete_forwarded(client, message):
    chat_id = message.chat.id   # Get the chat ID
    message_id = message.message_id  # Get the message ID

    # Delete the forwarded message using Telegram API
    await client.delete_messages(chat_id=chat_id, message_ids=[message_id])

# Filter for forwarded messages
@app.on_message(filters.forwarded)
async def get_forwarded_channel_id(client, message):
    # Check if the forwarded message is from a channel
    if message.forward_from_chat and message.forward_from_chat.type == "channel":
        channel_id = message.forward_from_chat.id  # Get the channel ID
        await message.reply(f"Channel ID: {channel_id}")  # Send the channel ID as a reply
    else:
        await message.reply("Yeh message kisi channel se forward nahi kiya gaya hai.")



