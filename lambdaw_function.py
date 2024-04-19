import os
import tempfile
from wand.image import Image
from wand.drawing import Drawing
from wand.font import Font
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

    with Image(filename=input_path) as img:
        # Resize
        img.resize(300, 300)

        # Compress
        compressed_img = tempfile.NamedTemporaryFile(delete=False)
        img.save(filename=compressed_img.name)

        # watermark
        add_text_watermark(img, "Navodita")

    return compressed_img

def add_text_watermark(img, text):

    with Drawing() as draw:
        font = Font()
        draw.font = font
        draw.font_size = 20
        draw.text_alignment = 'left'
        draw.fill_color = 'white'

        text_position = (10, 10)

        draw.text(text_position, text)
        draw(img)

def upload_to_s3(processed_image, bucket, key):

    s3.upload_file(processed_image.name, bucket, key)

    os.remove(processed_image.name)     # Clean up the temporary files


