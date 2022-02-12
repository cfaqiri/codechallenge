import csv
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import EmployeeReport
from payroll.serializers import EmployeeReportSerializer, FileUploadSerializer
from payroll.services import PayrollReportService


# How do I properly raise an error in DRF when the report uploaded is a duplicate?
# You said that CreateAPIView here may not necessary but I can't do just APIView or I get an error when I post a file
# The json I return isn't camelcased - should I be renaming my models?
# How come employee ID doesnt come up in quotes in the json response?
# What's the best way for me to add the the dollar sign in front of the amount in amount_paid?
# How do I set up my json response so that I first have a payrollReport object 
# What do you think of the relationships between my models? 
## For example, when I delete a report, it deletes the timekeeping information, but not the employee records, pay periods or employees. Is that wrong?
# How do you think I should break up the add records method under PayrollReportService so it's not super long?
# What tests should I run?
# Should I add authentication?


class UploadFile(generics.CreateAPIView):

    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        # Use service to deserialize contents of csv
        csv_data = PayrollReportService().deserialize_csv(file)
        # Use service to archive timekeeping information inside data by creating model instances
        new_records = PayrollReportService().add_records(csv_data=csv_data, name=file.name)
        return Response({"status": "success"}, status.HTTP_201_CREATED)


class EmployeeReportList(APIView):

    # List all employee reports
    def get(self, request, format=None):
        reports = EmployeeReport.objects.order_by('employee_id')
        serializer = EmployeeReportSerializer(reports, many=True)
        return Response(serializer.data)