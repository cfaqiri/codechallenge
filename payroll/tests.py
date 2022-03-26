import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status

from payroll.models import Employee, JobGroup, Report, TimekeepingRecord


class UserTests(TestCase):
    def setUp(self):
        user = User(
            email='test_user@gmail.com',
            username='test_user'
        )
        user.set_password('admin123')
        user.save()

    def test_user_registration(self):
        '''Check if we can register a new account'''

        client = APIClient()
        response = client.post(
            '/register/', {
                'email': 'test123@gmail.com',
                'username': 'test_user2',
                'password': 'test_password123'
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        client = APIClient()
        response = client.post(
            reverse('payroll:login'), {
                'username': 'test_user',
                'password': 'admin123',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.content.decode('utf-8'))


class FileUploadTests(TestCase):
    def setUp(self):
        user = User(
            email='test_user@gmail.com',
            username='testing_file_upload'
        )
        user.set_password('admin123')
        user.save()

        self.token, _ = Token.objects.get_or_create(user=user)

        JobGroup.objects.create(title='A', rate=20.00, employer=user)
        JobGroup.objects.create(title='B', rate=30.00, employer=user)

    def test_file_upload(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        client.login(username='testing_file_upload', password='admin123')

        with open('/Users/cfaqiri/Documents/time-report-16.csv') as fp:
            response = client.post('/upload/', {'file': fp})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), {"status": "success"})

    def test_file_duplicate(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        client.login(username='testing_file_upload', password='admin123')

        with open('/Users/cfaqiri/Documents/time-report-16.csv') as file:
            client.post('/upload/', {'file': file})

        with open('/Users/cfaqiri/Documents/time-report-16.csv') as file:
            response = client.post('/upload/', {'file': file})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {
                         "status": "upload failed due to duplicate report"})


class EmployeeReportTests(TestCase):
    def setUp(self):
        user = User(
            email='test_user@gmail.com',
            username='testing_file_upload'
        )
        user.set_password('admin123')
        user.save()

        self.token, _ = Token.objects.get_or_create(user=user)

        JobGroup.objects.create(title='A', rate=20.00, employer=user)
        JobGroup.objects.create(title='B', rate=30.00, employer=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        with open('/Users/cfaqiri/Documents/time-report-16.csv') as file:
            client.post('/upload/', {'file': file})

    def test_get_employee_report_view(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        client.login(username='testing_file_upload', password='admin123')
        response = client.get(reverse('payroll:retrieve'))

        content = {"payrollReport": {"employeeReports": [{"employeeId": "1", "payPeriod": {"startDate": "2023-01-01", "endDate": "2023-01-15"}, "amountPaid": "$300.00"}, {"employeeId": "1", "payPeriod": {
            "startDate": "2023-01-15", "endDate": "2023-01-31"}, "amountPaid": "$80.00"}, {"employeeId": "2", "payPeriod": {"startDate": "2023-01-15", "endDate": "2023-01-31"}, "amountPaid": "$90.00"}]}}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)


class EmployeeReportSignalsTests(TestCase):
    def setUp(self):
        user = User(
            email='test_user@gmail.com',
            username='test_user'
        )
        user.set_password('admin123')
        user.save()

        JobGroup.objects.create(title='A', rate=20.00, employer=user)
        JobGroup.objects.create(title='B', rate=30.00, employer=user)

        client = APIClient()
        client.login(username='testing_user', password='admin123')

    def test_timekeeping_record_created_signal(self):

        user = User.objects.get(username='test_user')
        report = Report.objects.create(employer=user, number=1)
        job_group = JobGroup.objects.get(employer=user, title='A')
        employee = Employee.objects.create(
            employer=user, number=17, job_group=job_group)

        record = TimekeepingRecord.objects.create(
            employer=user,
            report=report,
            date=datetime.datetime(2021, 5, 17),
            hours=10,
            employee=employee
        )

        record.save()

        start_date, end_date = user.pay_periods.all(
        )[0].start_date, user.pay_periods.all()[0].end_date

        test_start_date = datetime.date(2021, 5, 15)
        test_end_date = datetime.date(2021, 5, 31)

        self.assertEqual(start_date, test_start_date)
        self.assertEqual(end_date, test_end_date)
