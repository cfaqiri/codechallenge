from django.db.models.signals import post_save
from django.dispatch import receiver

from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, TimekeepingRecord
from payroll.services import PayrollReportService

@receiver(post_save, sender=TimekeepingRecord)
def create_pay_period(sender, instance, created, **kwargs):
    if created:
        pay_period_dates = PayrollReportService.get_start_and_end_date(instance)
        start_date = pay_period_dates[0]
        end_date = pay_period_dates[1]
        pay_period = PayPeriod.objects.get_or_create(start_date=start_date, end_date=end_date, employer=instance.employer)[0]
        
        # If a corresponding employee report exists, return a queryset
        employee_report = EmployeeReport.objects.filter(
            employee = instance.employee,
            pay_period = pay_period
        )
        
        amount_paid = instance.employee.job_group.rate * instance.hours

        # Check if the employee report queryset is empty
        if len(employee_report) == 0:
            # If empty (meaning one doesn't exist), save new employee report
            employee_report = EmployeeReport(
                employee = instance.employee,
                pay_period = pay_period,
                amount_paid = amount_paid,
                employer = instance.employer
            )
            employee_report.save()
            employee_report.report.add(instance.report)
            # Add the employee report to the timekeeping record
            instance.employee_report = employee_report
            instance.save()
        else:
            # If not empty, adjust amount paid in existing report
            employee_report[0].amount_paid += amount_paid
            employee_report[0].save()
            # Add the employee report to the timekeeping record
            instance.employee_report = employee_report[0]
            instance.save()
