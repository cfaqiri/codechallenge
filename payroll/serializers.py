from rest_framework import serializers
from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, TimekeepingRecord


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    

class Employee(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['job_group']


class JobGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobGroup
        fields = ['title', 'rate']


class TimekeepingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimekeepingRecord
        fields = ['date', 'hours', 'employee']


class PayPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPeriod
        fields = ['start_date', 'end_date']


class EmployeeReportSerializer(serializers.ModelSerializer):
    pay_period = PayPeriodSerializer(read_only=True)

    class Meta:
        model = EmployeeReport
        fields = ['employee', 'pay_period', 'amount_paid']