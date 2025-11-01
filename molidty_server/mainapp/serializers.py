from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import ElectricGeneratorModel, Subscriber, Worker, Budget, Receipt

class SubscriberSerializer(serializers.ModelSerializer):
    barcode_image=serializers.ImageField(read_only=True)
    date_subscribed=serializers.DateField(read_only=True)
    class Meta:
        model = Subscriber
        fields = '__all__'

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    year_month = serializers.CharField(read_only=True)
    unpaid_subscribers = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    paid_subscribers = serializers.PrimaryKeyRelatedField(many=True,read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'
    def create(self, validated_data):
        validated_data['year_month'] = f"{validated_data['year']}-{validated_data['month']}"
        budget=Budget.objects.create(**validated_data)
        budget.unpaid_subscribers.set(Subscriber.objects.all())
        budget.paid_subscribers.set([])
        return budget


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_id = serializers.CharField(read_only=True)
    date_received=serializers.DateTimeField(read_only=True)
    class Meta:
        model = Receipt
        fields = '__all__'
class electricGeneratorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricGeneratorModel
        fields = '__all__'