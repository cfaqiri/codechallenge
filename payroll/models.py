from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Report(models.Model):
    report_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.report_id)


class JobGroup(models.Model):
    title = models.CharField(max_length=1)
    rate = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.title)


class Employee(models.Model):
    # Job groups should not be deleted, unless no longer needed for any employees
    employee_id = models.IntegerField(primary_key=True)
    job_group = models.ForeignKey(JobGroup, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.employee_id)


class PayPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"


class EmployeeReport(models.Model):
    report = models.ManyToManyField(Report)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    pay_period = models.ForeignKey(PayPeriod, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee} from {self.pay_period.start_date} to {self.pay_period.end_date}: {self.amount_paid}"


class TimekeepingRecord(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # Null is true because the employee report may be created after the timekeeping instance is saved
    # Restrict because an employee report shouldn't get deleted unless all of its timekeeping records are first deleted
    employee_report = models.ForeignKey(EmployeeReport, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        date = str(self.date)
        return f"{self.employee} on {date}"
