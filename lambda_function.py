import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    temp_file_path = download_from_s3(bucket, key)

    # Image processing
    processed_image = process_image(temp_file_path)

    upload_to_s3(processed_image, bucket, f"processed/{key}")

def download_from_s3(bucket, key):
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name

    s3.download_file(bucket, key, temp_file_path)

    return temp_file_path

def process_image(input_path):
    
    img = Image.open(input_path)

    # Resize
    
    resized_img = img.resize((300, 300))

    # Compress
    
    compressed_img = tempfile.NamedTemporaryFile(delete=False)
    resized_img.save(compressed_img, format='JPEG', quality=85)

    # watermark
    
    watermarked_img = add_text_watermark(resized_img, "Your Watermark Text")

    return watermarked_img

def add_text_watermark(image, text):

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    text_position = (10, 10)

    text_color = (255, 255, 255, 128)

    draw.text(text_position, text, font=font, fill=text_color)

    return image

def upload_to_s3(processed_image, bucket, key):

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    processed_image.save(temp_file_path, format='JPEG')

    s3.upload_file(temp_file_path, bucket, key)

    os.remove(temp_file_path)  # Clean up the temporary files