from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import EmployeeReport
from payroll.serializers import EmployeeReportSerializer, FileUploadSerializer
from payroll.services import PayrollReportService


class UploadFile(APIView):
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = FileUploadSerializer

    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        check_duplicate_report = PayrollReportService().check_duplicate_report(file.name)
        if check_duplicate_report == True:
            return Response({"status": "upload failed due to duplicate report"}, status=status.HTTP_400_BAD_REQUEST)
        csv_data = PayrollReportService().deserialize_csv(file)
        PayrollReportService().add_records(csv_data=csv_data, name=file.name)
        return Response({"status": "success"}, status.HTTP_201_CREATED)


class EmployeeReportList(APIView):

    def get(self, request, format=None):
        reports = EmployeeReport.objects.all()
        serializer = EmployeeReportSerializer(reports, many=True)
        employeeReports = {'employeeReports': serializer.data}
        payrollReport = {'payrollReport': employeeReports}
        return Response(payrollReport)