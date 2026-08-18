from django.urls import path
from attendance.views import AttendanceListView, AttendanceCreateView, AttendanceMarkView, AttendanceCalendarView

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance_list'),
    path('add/', AttendanceCreateView.as_view(), name='attendance_add'),
    path('mark/', AttendanceMarkView.as_view(), name='attendance_mark'),
    path('calendar/', AttendanceCalendarView.as_view(), name='attendance_calendar'),
]
