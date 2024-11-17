from django.contrib import admin
from .models import ProcessingRequest, Product

class ProcessingRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'status')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('request', 'serial_number', 'product_name', 'input_urls', 'output_urls')

admin.site.register(ProcessingRequest, ProcessingRequestAdmin)
admin.site.register(Product, ProductAdmin)
