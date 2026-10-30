from rest_framework import serializers
from .models import MaterialExtra, PaymentOrder, ServiceMessage

class StrictInput(serializers.Serializer):
    def validate(self, attrs):
        if set(self.initial_data) - set(self.fields):
            raise serializers.ValidationError('Hay campos no permitidos en la petición.')
        return attrs

class MaterialInput(StrictInput):
    description = serializers.CharField(max_length=240)
    quantity = serializers.IntegerField(min_value=1, max_value=10000)
    unit_price = serializers.IntegerField(min_value=1, max_value=100000000)

class DecisionInput(StrictInput):
    decision = serializers.ChoiceField(choices=['APPROVED', 'REJECTED'])

class DemoResultInput(StrictInput):
    outcome = serializers.ChoiceField(choices=['approved', 'rejected'])

class MessageInput(StrictInput):
    text = serializers.CharField(max_length=2000)

class MaterialRead(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    def get_total(self, obj):
        return obj.quantity * obj.unit_price
    class Meta:
        model = MaterialExtra
        fields = ['id', 'description', 'quantity', 'unit_price', 'total', 'status', 'created_at', 'decided_at']

class PaymentRead(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    fiscal_document = serializers.SerializerMethodField()
    def get_currency(self, obj):
        return 'CLP'
    def get_fiscal_document(self, obj):
        return False
    class Meta:
        model = PaymentOrder
        fields = ['id', 'mode', 'status', 'currency', 'service_amount', 'materials_amount', 'net_amount', 'vat_amount', 'vat_percent', 'total', 'snapshot', 'fiscal_document', 'created_at', 'paid_at', 'refunded_at', 'commission_percent', 'commission_amount', 'provider_amount']

class MessageRead(serializers.ModelSerializer):
    class Meta:
        model = ServiceMessage
        fields = ['id', 'sender_id', 'text', 'created_at']
