from django.contrib import admin
from employees.models import Employee, Position
from oguz.admin_site import admin_site


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'position_fk', 'salary_type', 'salary', 'is_active')
    list_filter = ('department', 'salary_type', 'is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)


admin_site.register(Position, PositionAdmin)
admin_site.register(Employee, EmployeeAdmin)
