from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import *

class SubscriberSerializer(serializers.ModelSerializer):
    barcode_image=serializers.ImageField(read_only=True)
    date_subscribed=serializers.DateField(read_only=True)
    class Meta:
        model = Subscriber
        fields = '__all__'



class BudgetSerializer(serializers.ModelSerializer):
    budget_uuid = serializers.CharField(read_only=True)
    unpaid_subscribers = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    paid_subscribers = serializers.PrimaryKeyRelatedField(many=True,read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'
    def create(self, validated_data):
        validated_data['budget_uuid'] = f"{validated_data['generator']}-{validated_data['year']}-{validated_data['month']}"
        budget=Budget.objects.create(**validated_data)
        budget.unpaid_subscribers.set(Subscriber.objects.all())
        budget.paid_subscribers.set([])
        return budget


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_uuid = serializers.CharField(read_only=True)
    date_received=serializers.DateTimeField(read_only=True)
    class Meta:
        model = Receipt
        fields = '__all__'
        
    def create(self, validated_data):
        
        validated_data['receipt_uuid'] = f"{validated_data['generator']}-{validated_data['year']}-{validated_data['month']:02d}-{validated_data['subscriber']}"
        receipt=Receipt.objects.create(**validated_data)
        
        budget=Budget.objects.filter(year=receipt.year, month=receipt.month,generator=receipt.generator).first()
        budget.paid_subscribers.add(receipt.subscriber)
        budget.unpaid_subscribers.remove(receipt.subscriber)
        return receipt
    
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
class WorkerSerializer(serializers.ModelSerializer):
    generator_name = serializers.CharField(source='generator.generator_name',read_only=True)

    class Meta:
        model = Worker
        fields = '__all__'