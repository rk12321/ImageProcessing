import csv
import threading
import uuid
import requests
from io import StringIO
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ProcessingRequest, Product
from django.core.files.storage import default_storage
from .tasks import process_images

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'Invalid file format'}, status=400)

        request_id = str(uuid.uuid4())
        processing_request = ProcessingRequest.objects.create(request_id=request_id)

        file_data = file.read().decode('utf-8')
        csv_reader = csv.reader(StringIO(file_data))
        next(csv_reader)

        products = []
        for row in csv_reader:
            serial_number, product_name, input_urls = row
            products.append(Product(
                request=processing_request,
                serial_number=int(serial_number),
                product_name=product_name,
                input_urls=input_urls
            ))

        Product.objects.bulk_create(products)

        threading.Thread(target=process_images, args=(request_id,)).start()

        return JsonResponse({'request_id': request_id})



def check_status(request, request_id):
    try:
        processing_request = ProcessingRequest.objects.get(request_id=request_id)
        status = processing_request.status
        return JsonResponse({'status': status})
    except ProcessingRequest.DoesNotExist:
        return JsonResponse({'error': 'Request ID not found'}, status=404)



def download_output_csv(request, request_id):
    try:
        processing_request = ProcessingRequest.objects.get(request_id=request_id)
        print(processing_request.status)

        if processing_request.status != 'Completed':
            return JsonResponse({'error': 'Processing not yet completed'}, status=400)

        products = Product.objects.filter(request=processing_request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{request_id}_output.csv"'

        writer = csv.writer(response)
        writer.writerow(['Serial Number', 'Product Name', 'Input URLs', 'Output URLs'])

        for product in products:
            writer.writerow([
                product.serial_number,
                product.product_name,
                product.input_urls,
                'http://127.0.0.1:8000'+product.output_urls
            ])

        return response

    except ProcessingRequest.DoesNotExist:
        return JsonResponse({'error': 'Request ID not found'}, status=404)
