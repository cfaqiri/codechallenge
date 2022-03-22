from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from payroll import views


app_name = 'payroll'
urlpatterns = [
    path('upload/', views.UploadFile.as_view()),
    path('retrieve/', views.EmployeeReportList.as_view(), name='retrieve'),
    path('register/', views.RegisterUser.as_view()),
    path('api-token-auth/', obtain_auth_token, name="login")
]