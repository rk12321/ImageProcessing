from django.db import models

class ProcessingRequest(models.Model):
    request_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default='Pending')

class Product(models.Model):
    request = models.ForeignKey(ProcessingRequest, on_delete=models.CASCADE)
    serial_number = models.IntegerField()
    product_name = models.CharField(max_length=255)
    input_urls = models.TextField()  # Store comma-separated URLs
    output_urls = models.TextField(null=True, blank=True)
