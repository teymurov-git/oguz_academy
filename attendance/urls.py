from django.urls import path
from attendance.views import AttendanceListView, AttendanceCreateView

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance_list'),
    path('add/', AttendanceCreateView.as_view(), name='attendance_add'),
]
