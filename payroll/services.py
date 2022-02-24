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
        content = file.read().decode('utf-8')
        csv_data = csv.DictReader(content.splitlines())
        return csv_data

    def add_report(self, name=None, user=None):
        report_number = self.get_report_number(name=name)
        new_report = Report(number=report_number, employer=user)
        new_report.save()
        return new_report

    def get_start_and_end_date(self, record=None):
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
            job_group = JobGroup.objects.get(title=line["job group"])
            employee_id = line["employee id"]
            hours = Decimal(line["hours worked"])

            # Save the timekeeping record
            new_record = TimekeepingRecord(
                date = datetime.datetime.strptime(line["date"], "%d/%m/%Y"),
                hours = hours,
                # Remember that get or create gives you a tuple, so the [0] is selecting the object
                employee = Employee.objects.get_or_create(employee_id=employee_id, job_group=job_group, employer=user)[0],
                report = new_report,
                employer = user
            )
            new_record.save()
            
            # Get pay period dates as a tuple
            pay_period_dates = self.get_start_and_end_date(new_record)
            start_date = pay_period_dates[0]
            end_date = pay_period_dates[1]
            
            employee = Employee.objects.get_or_create(employee_id=employee_id)[0]
            pay_period = PayPeriod.objects.get_or_create(start_date=start_date, end_date=end_date, employer=user)[0]
            amount_paid = job_group.rate * new_record.hours

            # If a corresponding employee report exists, return a queryset
            employee_report = EmployeeReport.objects.filter(
                employee = employee,
                pay_period = pay_period
            )
            
            # Check if the employee report queryset is empty
            if len(employee_report) == 0:
                # If empty (meaning one doesn't exist), save new employee report
                employee_report = EmployeeReport(
                    employee = employee,
                    pay_period = pay_period,
                    amount_paid = amount_paid,
                    employer = user
                )
                employee_report.save()
                employee_report.report.add(new_report)
                # Add the employee report to the timekeeping record
                new_record.employee_report = employee_report
                new_record.save()
            else:
                # If not empty, adjust amount paid in existing report
                employee_report[0].amount_paid += amount_paid
                employee_report[0].save()
                # Add the employee report to the timekeeping record
                new_record.employee_report = employee_report[0]
                new_record.save()
