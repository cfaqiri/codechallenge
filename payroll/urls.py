from django.urls import path, include
from payroll import views


app_name = 'payroll'
urlpatterns = [
    path('upload/', views.UploadFile.as_view()),
    path('retrieve/', views.EmployeeReportList.as_view(), name='retrieve'),
    path('register/', views.RegisterUser.as_view())
]