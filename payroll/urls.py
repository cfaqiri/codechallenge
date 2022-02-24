from django.urls import path, include
from payroll import views


urlpatterns = [
    path('upload/', views.UploadFile.as_view()),
    path('retrieve/', views.EmployeeReportList.as_view())
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]