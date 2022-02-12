from django.contrib import admin

from payroll.models import Employee, EmployeeReport, JobGroup, PayPeriod, Report, TimekeepingRecord


admin.site.register(Employee)
admin.site.register(EmployeeReport)
admin.site.register(JobGroup)
admin.site.register(PayPeriod)
admin.site.register(Report)
admin.site.register(TimekeepingRecord)


