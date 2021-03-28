from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ('email',)
    list_filter = ('is_staff',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),
        }),
    )

    search_fields = ('password',)
    ordering = ('password',)


admin.site.register(User, UserAdmin)