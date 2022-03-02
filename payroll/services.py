import calendar, csv, datetime, re
from decimal import Decimal
from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, Report, TimekeepingRecord


class PayrollReportService:

    def get_report_number(self, name=None):
        report_number = int(re.sub('\D', '', name))
        return report_number

    def check_duplicate_report(self, name=None, user=None):
        report_number = self.get_report_number(name=name)
        existing_report = Report.objects.filter(number=report_number, employer=user)
        if len(existing_report) == 0:
            return False
        return True

    def deserialize_csv(self, file):
        # Use if else statement to differentiate between when file comes from view vs command
        content = file.read().decode('utf-8')
        csv_data = csv.DictReader(content.splitlines())
        return csv_data

    def add_report(self, name=None, user=None):
        report_number = self.get_report_number(name=name)
        new_report = Report(number=report_number, employer=user)
        new_report.save()
        return new_report

    @staticmethod
    def get_start_and_end_date(record=None):
        if record.date.day < 15:
            first_day_of_pay_period = 1
            last_day_of_pay_period = 15
        else:
            first_day_of_pay_period = 15
            last_day_of_pay_period = calendar.monthrange(record.date.year, record.date.month)[1]

        start_date = datetime.datetime(record.date.year, record.date.month, first_day_of_pay_period)
        end_date = datetime.datetime(record.date.year, record.date.month, last_day_of_pay_period)
        pay_period_dates = (start_date, end_date)

        return pay_period_dates

    def add_records(self, csv_data=None, name=None, user=None):
        # Create the new report
        new_report = self.add_report(name=name, user=user)

        for line in csv_data:
            # Get the job group, employee_id and hours since I'll need it later down
            job_group = JobGroup.objects.get(title=line["job group"], employer=user)
            employee_number = line["employee id"]
            hours = Decimal(line["hours worked"])

            # Save the timekeeping record
            new_record = TimekeepingRecord(
                date = datetime.datetime.strptime(line["date"], "%d/%m/%Y"),
                hours = hours,
                # Remember that get or create gives you a tuple, so the [0] is selecting the object
                employee = Employee.objects.get_or_create(number=employee_number, job_group=job_group, employer=user)[0],
                report = new_report,
                employer = user
            )
            new_record.save()