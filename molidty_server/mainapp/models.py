from django.db import models

class Subscriber(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Subscriber Name")
    circuit_number = models.CharField(max_length=50, unique=True)
    Ambers = models.PositiveIntegerField(verbose_name="Ambers", default=0)
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")

    def __str__(self):
        return self.name

class Worker(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Worker Name")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")

    def __str__(self):
        return self.name

class Budget(models.Model):
    year_month = models.CharField(max_length=7, unique=True, help_text="Format: YYYY-MM")
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_subscribers = models.ManyToManyField(Subscriber, blank=True, related_name="budgets_paid")
    unpaid_subscribers = models.ManyToManyField(Subscriber, blank=True, related_name="budgets_unpaid")

    def __str__(self):
        return f"Budget for {self.year_month}"

class Receipt(models.Model):
    year_month = models.CharField(max_length=7, help_text="Format: YYYY-MM")
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="receipts")
    amber_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, related_name="receipts", null=True)
    image = models.ImageField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"Receipt for {self.subscriber.name} - {self.year_month} - {self.amount_paid} IQD"
