import uuid
from django.db import models
from django.conf import settings


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Ad', max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField('Təsvir', blank=True)
    is_system = models.BooleanField('Sistem rolu', default=False)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Rol'
        verbose_name_plural = 'Rollar'

    def __str__(self):
        return self.name


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.CharField(max_length=150, unique=True)
    name = models.CharField('Ad', max_length=255)
    module = models.CharField('Modul', max_length=100)
    action = models.CharField('Əməliyyat', max_length=50)
    created_at = models.DateTimeField('Yaradılma tarixi', auto_now_add=True)

    class Meta:
        ordering = ('module', 'codename')
        verbose_name = 'İcazə'
        verbose_name_plural = 'İcazələr'

    def __str__(self):
        return self.codename


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions', verbose_name='Rol')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions', verbose_name='İcazə')

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = 'Rol icazəsi'
        verbose_name_plural = 'Rol icazələri'

    def __str__(self):
        return f"{self.role} - {self.permission}"


class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles', verbose_name='İstifadəçi')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Rol')
    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'İstifadəçi rolu'
        verbose_name_plural = 'İstifadəçi rolları'

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
