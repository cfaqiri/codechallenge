import calendar, csv, datetime, re
from decimal import Decimal

from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, Report, TimekeepingRecord


class PayrollReportService:

    def deserialize_csv(self, file):
        content = file.read().decode('utf-8')
        # Manually deserializing the csv into data I can parse
        csv_data = csv.DictReader(content.splitlines())
        return csv_data

    def check_duplicate_report(self, name=None):
        # Use regex to get the report's id
        report_id = re.sub('\D', '', name)
        return report_id

    def add_report(self, name=None):
        report_id = self.check_duplicate_report(name)
        new_report = Report(id=report_id)
        new_report.save()
        return new_report

    def get_start_and_end_date(self, record=None):
        if record.date.day < 15:
            first_day = 1
            last_day = 15
        else:
            first_day = 15
            last_day = calendar.monthrange(record.date.year, record.date.month)[1]

        start_date = datetime.datetime(record.date.year, record.date.month, first_day)
        end_date = datetime.datetime(record.date.year, record.date.month, last_day)
        pay_period_dates = (start_date, end_date)

        return pay_period_dates

    def add_records(self, csv_data=None, name=None):
        # Create the new report
        new_report = self.add_report(name=name)

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
                employee = Employee.objects.get_or_create(id=employee_id, job_group=job_group)[0],
                report = new_report
            )
            new_record.save()
            
            # Get pay period dates as a tuple
            pay_period_dates = self.get_start_and_end_date(new_record)
            start_date = pay_period_dates[0]
            end_date = pay_period_dates[1]
            
            # Get or create the employee object
            employee = Employee.objects.get_or_create(id=employee_id)[0]

            # Get or create the pay period the record belongs to
            pay_period = PayPeriod.objects.get_or_create(start_date=start_date, end_date=end_date)[0]

            # Calculate amount paid 
            amount_paid = job_group.rate * new_record.hours

            # Get or create the employee report it belongs to
            employee_report = EmployeeReport.objects.filter(
                employee = employee,
                pay_period = pay_period
            )
            
            # Check if the employee report list is empty
            if len(employee_report) == 0:
                # If empty (meaning one doesn't exist), save new employee report
                employee_report = EmployeeReport(
                    employee = employee,
                    pay_period = pay_period,
                    amount_paid = amount_paid,
                    report = new_report
                )
                employee_report.save()
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
