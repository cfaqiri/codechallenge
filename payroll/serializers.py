from django.contrib.auth.models import User
from rest_framework import serializers
from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, Report, TimekeepingRecord


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id']


class JobGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobGroup
        fields = ['title', 'rate']


class TimekeepingRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimekeepingRecord
        fields = ['date', 'hours', 'employee']


class PayPeriodSerializer(serializers.ModelSerializer):
    startDate = serializers.CharField(source='start_date')
    endDate = serializers.CharField(source='end_date')
    
    class Meta:
        model = PayPeriod
        fields = ['startDate', 'endDate']


class EmployeeReportSerializer(serializers.ModelSerializer):
    employeeId = serializers.CharField(source='employee_id')
    payPeriod = PayPeriodSerializer(source='pay_period')
    amountPaid = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeReport
        fields = ['employeeId', 'payPeriod', 'amountPaid']

    def get_amountPaid(self, obj):
        obj.amount_paid = f'${obj.amount_paid}'
        return obj.amount_paid