from django.db import transaction

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import EmployeeReport
from payroll.serializers import EmployeeReportSerializer, FileUploadSerializer
from payroll.services import PayrollReportService

# Use transaction for rollback, do it when you're done the management command task 
# Transaction rollback won't show me all the errors 
class UploadFile(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = FileUploadSerializer

    @transaction.atomic
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        check_duplicate_report = PayrollReportService().check_duplicate_report(name=file.name, user=request.user)
        if check_duplicate_report == True:
            return Response({"status": "upload failed due to duplicate report"}, status=status.HTTP_400_BAD_REQUEST)
        csv_data = PayrollReportService().deserialize_csv(file)
        PayrollReportService().add_records(csv_data=csv_data, name=file.name, user=request.user)
        return Response({"status": "success"}, status.HTTP_201_CREATED)


class EmployeeReportList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        reports = EmployeeReport.objects.filter(employer=request.user)
        serializer = EmployeeReportSerializer(reports, many=True)
        employeeReports = {'employeeReports': serializer.data}
        payrollReport = {'payrollReport': employeeReports}
        return Response(payrollReport)