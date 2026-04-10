from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import Account, Subscriber, Budget, Receipt, Worker


# ─── Account Admin with password hashing ─────────────────────────────────────

class AccountAdminForm(forms.ModelForm):
    """Custom admin form: shows a plain-text password field and hashes it on save."""
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text='اتركه فارغاً إن لم تريد تغيير كلمة المرور',
    )

    class Meta:
        model = Account
        fields = ('generator_name', 'phone', 'password', 'is_active')

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw = self.cleaned_data.get('password', '').strip()
        if raw:
            # Only rehash when a new password is typed
            instance.password_hash = make_password(raw)
        elif not instance.password_hash:
            # If field is blank AND no existing hash, set a placeholder
            instance.password_hash = make_password('changeme')
        if commit:
            instance.save()
        return instance


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    form = AccountAdminForm
    list_display = ('generator_name', 'phone', 'is_active', 'date_created')
    search_fields = ('generator_name', 'phone')
    list_filter = ('is_active',)


# ─── Worker Admin with password hashing ──────────────────────────────────────

class WorkerAdminForm(forms.ModelForm):
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text='اتركه فارغاً إن لم تريد تغيير كلمة المرور',
    )

    class Meta:
        model = Worker
        fields = ('generator', 'name', 'phone', 'password', 'is_active')

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw = self.cleaned_data.get('password', '').strip()
        if raw:
            instance.password_hash = make_password(raw)
        elif not instance.password_hash:
            instance.password_hash = make_password('changeme')
        if commit:
            instance.save()
        return instance


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    form = WorkerAdminForm
    list_display = ('name', 'phone', 'generator', 'is_active', 'date_created')
    search_fields = ('name', 'phone')
    list_filter = ('generator', 'is_active')


# ─── Other models ─────────────────────────────────────────────────────────────

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'circuit_number', 'ambers', 'phone', 'generator', 'is_active')
    search_fields = ('name', 'circuit_number', 'phone')
    list_filter = ('generator', 'is_active')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('generator', 'year', 'month', 'amber_price', 'date_created')
    list_filter = ('generator', 'year', 'month')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'generator', 'subscriber', 'year', 'month',
        'amber_price', 'amount_paid', 'worker', 'date_received',
    )
    search_fields = ('subscriber__name',)
    list_filter = ('generator', 'year', 'month')