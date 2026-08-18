from django.db import models
from django.conf import settings


class AdminUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="admin_profile", verbose_name="İstifadəçi",
    )
    first_name = models.CharField(max_length=100, verbose_name="Ad")
    last_name = models.CharField(max_length=100, verbose_name="Soyad")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="Telefon")
    position = models.CharField(max_length=255, blank=True, default="", verbose_name="Vəzifə")
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir?")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_admins",
        verbose_name="Yaradan",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin istifadəçi"
        verbose_name_plural = "Admin istifadəçiləri"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=["is_staff"])


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Modul adı")
    display_name = models.CharField(max_length=255, verbose_name="Görünən ad")
    icon = models.CharField(max_length=100, blank=True, default="", verbose_name="İkon")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Modul"
        verbose_name_plural = "Modullar"
        ordering = ["order"]

    def __str__(self):
        return self.display_name


class ModuleList(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        related_name="lists", verbose_name="Modul",
    )
    name = models.CharField(max_length=100, verbose_name="Siyahı adı")
    model_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Model adı")
    api_endpoint = models.CharField(max_length=255, blank=True, default="", verbose_name="API endpoint")

    class Meta:
        verbose_name = "Modul siyahısı"
        verbose_name_plural = "Modul siyahıları"
        unique_together = ["module", "name"]

    def __str__(self):
        return f"{self.module} → {self.name}"


class ListField(models.Model):
    module_list = models.ForeignKey(
        ModuleList, on_delete=models.CASCADE,
        related_name="fields", verbose_name="Siyahı",
    )
    name = models.CharField(max_length=100, verbose_name="Sahə adı")
    field_type = models.CharField(
        max_length=50, default="text",
        verbose_name="Sahə tipi",
    )

    class Meta:
        verbose_name = "Siyahı sahəsi"
        verbose_name_plural = "Siyahı sahələri"

    def __str__(self):
        return f"{self.module_list} → {self.name}"


class ModulePermission(models.Model):
    admin_user = models.ForeignKey(
        AdminUser, on_delete=models.CASCADE,
        related_name="module_permissions", verbose_name="Admin",
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        verbose_name="Modul",
    )
    can_view = models.BooleanField(default=False, verbose_name="Görmək")
    can_create = models.BooleanField(default=False, verbose_name="Yaratmaq")
    can_edit = models.BooleanField(default=False, verbose_name="Redaktə etmək")
    can_delete = models.BooleanField(default=False, verbose_name="Silmək")

    class Meta:
        verbose_name = "Modul icazəsi"
        verbose_name_plural = "Modul icazələri"
        unique_together = ["admin_user", "module"]

    def __str__(self):
        return f"{self.admin_user} → {self.module}"


class ListPermission(models.Model):
    admin_user = models.ForeignKey(
        AdminUser, on_delete=models.CASCADE,
        related_name="list_permissions", verbose_name="Admin",
    )
    module_list = models.ForeignKey(
        ModuleList, on_delete=models.CASCADE,
        verbose_name="Siyahı",
    )
    can_view = models.BooleanField(default=False, verbose_name="Görmək")
    can_create = models.BooleanField(default=False, verbose_name="Yaratmaq")
    can_edit = models.BooleanField(default=False, verbose_name="Redaktə etmək")
    can_delete = models.BooleanField(default=False, verbose_name="Silmək")

    class Meta:
        verbose_name = "Siyahı icazəsi"
        verbose_name_plural = "Siyahı icazələri"
        unique_together = ["admin_user", "module_list"]

    def __str__(self):
        return f"{self.admin_user} → {self.module_list}"


class FieldPermission(models.Model):
    admin_user = models.ForeignKey(
        AdminUser, on_delete=models.CASCADE,
        related_name="field_permissions", verbose_name="Admin",
    )
    list_field = models.ForeignKey(
        ListField, on_delete=models.CASCADE,
        verbose_name="Sahə",
    )
    can_view = models.BooleanField(default=False, verbose_name="Görmək")
    can_edit = models.BooleanField(default=False, verbose_name="Redaktə etmək")

    class Meta:
        verbose_name = "Sahə icazəsi"
        verbose_name_plural = "Sahə icazələri"
        unique_together = ["admin_user", "list_field"]

    def __str__(self):
        return f"{self.admin_user} → {self.list_field}"


class PermissionLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Yaradıldı"
        UPDATED = "updated", "Yeniləndi"
        DELETED = "deleted", "Silindi"
        ACCESSED = "accessed", "Giriş edildi"

    admin_user = models.ForeignKey(
        AdminUser, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Admin",
    )
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name="Hərəkət")
    module_name = models.CharField(max_length=100, verbose_name="Modul adı")
    details = models.JSONField(default=dict, blank=True, verbose_name="Detallar")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İcazə jurnalı"
        verbose_name_plural = "İcazə jurnalları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.admin_user} — {self.action} — {self.module_name}"
