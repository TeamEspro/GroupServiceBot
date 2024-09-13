from GroupService import pbot as app
import io
import boto3
from google.cloud import vision
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from msrest.authentication import CognitiveServicesCredentials
from pyrogram import Client, filters
from pyrogram.types import Message


# Google Cloud Vision Client
client_vision = vision.ImageAnnotatorClient()

# AWS Rekognition Client
rekognition_client = boto3.client('rekognition', region_name='us-east-1')

# Azure Content Moderator Client
azure_client = ContentModeratorClient(
    endpoint="https://<your-azure-endpoint>.cognitiveservices.azure.com/",
    credentials=CognitiveServicesCredentials("<your-azure-key>")
)

# Google Cloud Vision: Function to detect pornographic content
def google_detect_porn(photo_bytes) -> bool:
    image = vision.Image(content=photo_bytes)
    response = client_vision.safe_search_detection(image=image)
    safe_search = response.safe_search_annotation

    if safe_search.adult == vision.Likelihood.VERY_LIKELY or safe_search.racy == vision.Likelihood.VERY_LIKELY:
        return True
    return False

# AWS Rekognition: Function to detect explicit content
def aws_detect_porn(photo_bytes) -> bool:
    response = rekognition_client.detect_moderation_labels(
        Image={'Bytes': photo_bytes},
        MinConfidence=80
    )
    for label in response['ModerationLabels']:
        if label['Name'] in ["Explicit Nudity", "Pornography", "Sexual Content"]:
            return True
    return False

# Azure Content Moderator: Function to detect NSFW content
def azure_detect_porn(photo_bytes) -> bool:
    response = azure_client.image_moderation.byte_array(
        "image", io.BytesIO(photo_bytes), content_type="image/jpeg"
    )
    if response.is_image_adult_classified or response.is_image_racy_classified:
        return True
    return False

# Function to check if an image contains pornographic content using all APIs
def is_pornographic_content(photo_bytes) -> bool:
    if google_detect_porn(photo_bytes):
        return True
    if aws_detect_porn(photo_bytes):
        return True
    if azure_detect_porn(photo_bytes):
        return True
    return False

# Filter to handle all media messages (photos, videos, etc.)
@app.on_message(filters.photo)
def detect_and_delete_porn(client, message: Message):
    # Get the file from Telegram server
    file_id = message.photo.file_id
    file = client.download_media(file_id)

    # Read the image bytes
    with io.open(file, 'rb') as image_file:
        content = image_file.read()

    # Detect pornographic content using multiple APIs
    if is_pornographic_content(content):
        # Delete the message if it's pornographic
        message.delete()
        message.reply_text("Pornographic content is not allowed in this group!")
