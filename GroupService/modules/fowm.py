from pyrogram import Client, filters

# Filter for forwarded messages
@app.on_message(filters.forwarded & filters.group)
async def delete_forwarded(client, message):
    chat_id = message.chat.id   # Get the chat ID
    message_id = message.message_id  # Get the message ID

    # Delete the forwarded message using Telegram API
    await client.delete_messages(chat_id=chat_id, message_ids=[message_id])

