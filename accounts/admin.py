from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_number', 'name', 'last_name', 'family_name', 'email', 'id_card', 'education_level',
                    'work_place', 'education_place', 'home', 'deletion_date', 'avatar', 'is_active', 'is_admin', 'is_superuser')
    list_filter = ('is_admin', 'is_active', 'is_superuser')
    fieldsets = (
        ('Personal info', {'fields': ('phone_number', 'password', 'name', 'last_name', 'family_name', 'email',
                                      'id_card', 'education_level', 'work_place', 'education_place', 'home', 'deletion_date', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'last_name', 'family_name', 'email', 'id_card', 'education_level',
                       'work_place', 'education_place', 'home', 'deletion_date', 'avatar', 'password1', 'password2', 'is_active', 'is_admin', 'is_superuser'),
        }),
    )
    search_fields = ('phone_number', 'email', 'name', 'last_name')
    ordering = ('phone_number',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)



