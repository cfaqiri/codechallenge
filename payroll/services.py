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

    def add_records(self, data=None, name=None):
        # Create new report
        report_id = self.check_duplicate_report(name)
        new_report = Report(id=report_id)
        new_report.save()

        for line in data:
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

            # Find the start date and end date that this record would fall into to use later when assigning pay period
            if new_record.date.day < 15:
                start_date = datetime.datetime(new_record.date.year, new_record.date.month, 1)
                end_date = datetime.datetime(new_record.date.year, new_record.date.month, 15)

            else:
                last_day = calendar.monthrange(new_record.date.year, new_record.date.month)[1]

                start_date = datetime.datetime(new_record.date.year, new_record.date.month, 16)
                end_date = datetime.datetime(new_record.date.year, new_record.date.month, last_day)
            
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
                # If empty, save new employee report
                employee_report = EmployeeReport(
                    employee = employee,
                    pay_period = pay_period,
                    amount_paid = amount_paid
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
