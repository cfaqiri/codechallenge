from django.urls import path
from payroll import views


urlpatterns = [
    path('upload/', views.UploadFile.as_view()),
    path('retrieve/', views.EmployeeReportList.as_view())
]