import requests
from PIL import Image
import os
import tempfile
from django.core.files.storage import default_storage
from .models import Product, ProcessingRequest

def process_images(request_id):
    products = Product.objects.filter(request__request_id=request_id)

    for product in products:
        input_urls = product.input_urls.split(',')
        output_urls_list = []

        for url in input_urls:
            try:
                image_name = url.split("/")[-1]
                response = requests.get(url, stream=True)

                if response.status_code == 200:
                    img = Image.open(response.raw)
                    img = img.convert("RGB")

                    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    img.save(temp_output.name, "JPEG", quality=50)

                    output_path = f"compressed/{image_name}"
                    default_storage.save(output_path, open(temp_output.name, 'rb'))
                    output_url = f"/media/{output_path}"
                    output_urls_list.append(output_url)

                    os.remove(temp_output.name)

            except Exception as e:
                print(f"Error processing image {url}: {e}")

        product.output_urls = ','.join(output_urls_list)
        product.save()

    processing_request = ProcessingRequest.objects.get(request_id=request_id)
    processing_request.status = 'Completed'
    processing_request.save()
