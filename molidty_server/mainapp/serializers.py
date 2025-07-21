from rest_framework import serializers
from .models import Subscriber, Worker, Budget, Receipt

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = '__all__'

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    year_month = serializers.CharField(read_only=True)
    class Meta:
        model = Budget
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):
    year_month_subscriber_id = serializers.CharField(read_only=True)
    class Meta:
        model = Receipt
        fields = '__all__'