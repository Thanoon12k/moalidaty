from datetime import date
from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password


class Account(models.Model):
    """Electric generator owner/manager account.
    Authentication: generator_name + password (hashed)."""
    generator_name = models.CharField(
        max_length=100, unique=True, verbose_name="اسم المولدة"
    )
    phone = models.CharField(
        max_length=15, unique=True,
        verbose_name="رقم الهاتف", help_text="07XXXXXXXXX"
    )
    password_hash = models.CharField(
        max_length=256, verbose_name="كلمة المرور (مشفرة)", default=""
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "حساب مولدة"
        verbose_name_plural = "حسابات المولدات"
        ordering = ['generator_name']

    def __str__(self):
        return self.generator_name

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def check_credentials(self, raw_password: str) -> bool:
        """Login check: generator_name is the username, password is the credential."""
        return self.is_active and django_check_password(raw_password, self.password_hash)


class Subscriber(models.Model):
    """A subscriber connected to a generator."""
    generator = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='subscribers', verbose_name="المولدة"
    )
    name = models.CharField(max_length=100, verbose_name="اسم المشترك")
    circuit_number = models.CharField(max_length=20, verbose_name="رقم الجوزة")
    ambers = models.PositiveIntegerField(verbose_name="الأمبيرات")
    phone = models.CharField(
        max_length=15, blank=True, default='', verbose_name="رقم الهاتف"
    )
    date_subscribed = models.DateField(
        default=date.today, verbose_name="تاريخ الاشتراك"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "مشترك"
        verbose_name_plural = "المشتركون"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.circuit_number})"


class Budget(models.Model):
    """Monthly budget/pricing period for a generator."""
    generator = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='budgets', verbose_name="المولدة"
    )
    year = models.PositiveIntegerField(verbose_name="السنة")
    month = models.PositiveIntegerField(verbose_name="الشهر")
    amber_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00, verbose_name="سعر الأمبير (د.ع)"
    )
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        unique_together = ('generator', 'year', 'month')
        verbose_name = "ميزانية"
        verbose_name_plural = "الميزانيات"
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.generator.generator_name} — {self.year}/{self.month:02d}"

    @property
    def paid_count(self):
        return Receipt.objects.filter(
            generator=self.generator, year=self.year, month=self.month
        ).count()

    @property
    def unpaid_count(self):
        total = self.generator.subscribers.filter(is_active=True).count()
        return max(0, total - self.paid_count)


class Worker(models.Model):
    """Worker/employee for a generator.
    Authentication: phone + password (hashed)."""
    generator = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='workers', verbose_name="المولدة"
    )
    name = models.CharField(max_length=100, verbose_name="اسم العامل")
    phone = models.CharField(
        max_length=15, unique=True, verbose_name="رقم الهاتف"
    )
    password_hash = models.CharField(
        max_length=256, verbose_name="كلمة المرور (مشفرة)"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "عامل"
        verbose_name_plural = "العمال"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.generator.generator_name}"

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return self.is_active and django_check_password(raw_password, self.password_hash)


class Receipt(models.Model):
    """Payment receipt for one subscriber in one month."""
    generator = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='receipts', verbose_name="المولدة"
    )
    subscriber = models.ForeignKey(
        Subscriber, on_delete=models.CASCADE,
        related_name='receipts', verbose_name="المشترك"
    )
    worker = models.ForeignKey(
        Worker, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='collected_receipts', verbose_name="العامل"
    )
    year = models.PositiveIntegerField(verbose_name="السنة")
    month = models.PositiveIntegerField(verbose_name="الشهر")
    amber_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="سعر الأمبير"
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع"
    )
    receipt_image = models.ImageField(
        upload_to='receipts/', blank=True, null=True, verbose_name="صورة الإيصال"
    )
    notes = models.TextField(blank=True, default='', verbose_name="ملاحظات")
    date_received = models.DateTimeField(
        auto_now_add=True, verbose_name="تاريخ الاستلام"
    )

    class Meta:
        unique_together = ('generator', 'subscriber', 'year', 'month')
        verbose_name = "إيصال"
        verbose_name_plural = "الإيصالات"
        ordering = ['-date_received']

    def __str__(self):
        return f"إيصال {self.subscriber.name} — {self.year}/{self.month:02d}"