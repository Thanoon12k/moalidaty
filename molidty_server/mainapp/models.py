
import io
from django.core.files.base import ContentFile
import qrcode
from django.db import models
from datetime import datetime,date


class MyManager(models.Model):
    generator_name = models.CharField(max_length=100, unique=True, verbose_name="Generator Name")
    phone = models.CharField(max_length=15,blank=False, null=False, verbose_name="Phone Number",help_text=" 077 xxx xxx xx")
    password=models.CharField(max_length=100,blank=False, null=False,verbose_name="Password")
    date_created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    def __str__(self):
        return self.generator_name
    
    
    
    
class Subscriber(models.Model):
    generator=models.ForeignKey(MyManager, on_delete=models.CASCADE, related_name="subscribers",null=False,blank=False,verbose_name="Electric Generator Manager")
    name = models.CharField(max_length=100, unique=False, verbose_name="Subscriber Name")
    circuit_number = models.CharField(max_length=50, unique=False,blank=False, null=False, verbose_name="Circuit Number")
    Ambers = models.PositiveIntegerField(verbose_name="Ambers", blank=False, null=False)
    phone = models.CharField(max_length=15, default="000", verbose_name="Phone Number",help_text=" 077 xxx xxx xx")
    barcode_image = models.ImageField(upload_to='subscribers_barcodes/', verbose_name="Barcode Image")
    date_subscribed = models.DateField(default=date.today, verbose_name="Date Subscribed",blank=True,null=True)
    date_created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.barcode_image:
            # Generate QR code for the data string (supporting Arabic)
            qr_data = f"CODE--{self.generator}-{self.name}-{self.circuit_number}"
            qr = qrcode.make(qr_data)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            self.barcode_image.save(f"qr_{self.generator}_{self.name}_{self.circuit_number}.png", ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)


class Worker(models.Model):
    generator=models.ForeignKey(MyManager, on_delete=models.CASCADE, related_name="workers",null=False,blank=False,verbose_name="Electric Generator Manager")
    name = models.CharField(max_length=100, unique=False, verbose_name="Worker Name")
    phone = models.CharField(max_length=15, default="000", verbose_name="Phone Number",help_text=" 077 xxx xxx xx")
    date_created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    password=models.CharField(max_length=100,verbose_name="Password")
    def __str__(self):
        return self.name

class Budget(models.Model):
    generator=models.ForeignKey(MyManager, on_delete=models.CASCADE, related_name="budgets",null=False,blank=False,verbose_name="Electric Generator Manager")
    budget_id = models.CharField(max_length=7, help_text="Format: generator-YYYY-MM", unique=True,auto_created=True)
    year=models.PositiveIntegerField()
    month=models.PositiveIntegerField()
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_subscribers = models.ManyToManyField(Subscriber, blank=True, related_name="budgets_paid")
    unpaid_subscribers = models.ManyToManyField(Subscriber, blank=True, related_name="budgets_unpaid")
    date_created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return f"Budget for {self.year_month}"
    
    

        

    

class Receipt(models.Model):
    generator=models.ForeignKey(MyManager, on_delete=models.CASCADE, related_name="receipts",null=False,blank=False,verbose_name="Electric Generator Manager")
    receipt_id = models.CharField(max_length=11, help_text="Format: generatorname-YYYY-MM-receiptid",unique=True)
    year=models.PositiveIntegerField()
    month=models.PositiveIntegerField()
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="receipts")
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, related_name="receipts", null=True,blank=False)
    image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    date_received = models.DateTimeField(default=datetime.now,blank=True,null=True)

    def __str__(self):
        return f"Paid ({self.amount_paid} IQD)"
    def save(self, *args, **kwargs):
        
        
        self.year_month_subscriber_id = f"{self.generator}-{self.year}-{self.month:02d}-{self.subscriber.id}"
        super().save(*args, **kwargs)
        budget=Budget.objects.filter(year=self.year, month=self.month,generator=self.generator).first()
        budget.paid_subscribers.add(self.subscriber)
        budget.unpaid_subscribers.remove(self.subscriber)