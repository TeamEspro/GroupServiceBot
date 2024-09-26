from GroupService import pbot as app
from pyrogram import Client, filters
import re

# Pyrogram client initialize karein


# Function to check for links
def contains_link(text):
    # Common URL patterns ke liye regex
    url_pattern = re.compile(r"(https?://[^\s]+)|(www\.[^\s]+)|([a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+)")
    return url_pattern.search(text) is not None

# Filter for handling messages with links
@app.on_message(filters.group)
def delete_links(client, message):
    if message.text:
        if contains_link(message.text):
            # Agar message me link ho to us message ko delete kar do
            message.delete()
            print(f"Deleted message with link: {message.text}")
