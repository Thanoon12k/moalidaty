from rest_framework import serializers
from .models import Account, Subscriber, Budget, Receipt, Worker


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'generator_name', 'phone', 'is_active', 'date_created']
        read_only_fields = ['id', 'date_created']


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = [
            'id', 'generator', 'name', 'circuit_number',
            'ambers', 'phone', 'date_subscribed', 'is_active', 'date_created',
        ]
        read_only_fields = ['id', 'generator', 'date_created', 'date_subscribed']


class BudgetSerializer(serializers.ModelSerializer):
    paid_count = serializers.ReadOnlyField()
    unpaid_count = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = [
            'id', 'generator', 'year', 'month',
            'amber_price', 'paid_count', 'unpaid_count', 'date_created',
        ]
        read_only_fields = ['id', 'generator', 'date_created']


class WorkerSerializer(serializers.ModelSerializer):
    generator_name = serializers.CharField(
        source='generator.generator_name', read_only=True
    )
    password = serializers.CharField(write_only=True, required=True, min_length=4)

    class Meta:
        model = Worker
        fields = [
            'id', 'generator', 'generator_name',
            'name', 'phone', 'password', 'is_active', 'date_created',
        ]
        read_only_fields = ['id', 'generator', 'generator_name', 'date_created']

    def create(self, validated_data):
        password = validated_data.pop('password')
        worker = Worker(**validated_data)
        worker.set_password(password)
        worker.save()
        return worker

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ReceiptSerializer(serializers.ModelSerializer):
    # Denormalised read-only fields for display
    subscriber_name = serializers.CharField(source='subscriber.name', read_only=True)
    subscriber_circuit = serializers.CharField(
        source='subscriber.circuit_number', read_only=True
    )
    subscriber_phone = serializers.CharField(source='subscriber.phone', read_only=True)
    subscriber_ambers = serializers.IntegerField(
        source='subscriber.ambers', read_only=True
    )
    worker_name = serializers.CharField(
        source='worker.name', read_only=True, allow_null=True, default=None
    )
    receipt_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = [
            'id', 'generator', 'subscriber', 'subscriber_name',
            'subscriber_circuit', 'subscriber_phone', 'subscriber_ambers',
            'worker', 'worker_name',
            'year', 'month',
            'amber_price', 'amount_paid',
            'receipt_image', 'receipt_image_url',
            'notes', 'date_received',
        ]
        read_only_fields = [
            'id', 'generator', 'date_received',
            'receipt_image_url',
        ]

    def get_receipt_image_url(self, obj):
        request = self.context.get('request')
        if obj.receipt_image and hasattr(obj.receipt_image, 'url') and request:
            return request.build_absolute_uri(obj.receipt_image.url)
        return None