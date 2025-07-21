from django.db import models

class Subscriber(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Subscriber Name")
    circuit_number = models.CharField(max_length=50, unique=False,default="0000", verbose_name="Circuit Number")
    Ambers = models.PositiveIntegerField(verbose_name="Ambers", default=0)
    phone = models.CharField(max_length=15, blank=True, null=True,default="07", verbose_name="Phone Number")

    def __str__(self):
        return self.name

class Worker(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Worker Name")
    phone = models.CharField(max_length=15, blank=True, null=True,default="07", verbose_name="Phone Number")

    def __str__(self):
        return self.name

class Budget(models.Model):
    year_month = models.CharField(max_length=7, help_text="Format: YYYY-MM", unique=True)
    year=models.PositiveIntegerField()
    month=models.PositiveIntegerField()
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_subscribers = models.ManyToManyField(Subscriber, blank=True, related_name="budgets_paid")

    def __str__(self):
        return f"Budget for {self.year_month}"
    def save(self, *args, **kwargs):
        # Automatically set the year and month fields based on the year_month field
        self.year_month = f"{self.year}-{self.month:02d}"
        super().save(*args, **kwargs)

class Receipt(models.Model):
    year_month_subscriber_id = models.CharField(max_length=11, help_text="Format: YYYY-MM-ID",unique=True)
    year=models.PositiveIntegerField()
    month=models.PositiveIntegerField()
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="receipts")
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, related_name="receipts", null=True)
    image = models.ImageField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"Receipt for {self.subscriber.name} - {self.year_month} - {self.amount_paid} IQD"
    def save(self, *args, **kwargs):
        # Automatically set the year and month fields based on the year_month_subscriber_id field

        
        self.year_month_subscriber_id = f"{self.year}-{self.month:02d}-{self.subscriber.id}"
        super().save(*args, **kwargs)
        Budget.objects.filter(year=self.year, month=self.month).update(paid_subscribers=models.F('paid_subscribers').union([self.subscriber]))