from django.contrib import admin
from .models import Payment

# Register your models here.


@admin.register(Payment)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ("pk", "transaction_id", "enrollment", "currency", "amount")
    list_display_links = ("pk", "transaction_id")
    search_fields = ("transaction_id", "enrollment__enrollment_no")
