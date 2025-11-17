from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Tampilkan kolom yang ingin terlihat di tabel admin
    list_display = ('username', 'role', 'jurusan', 'nip', 'nisn', 'is_staff', 'is_superuser', 'is_active')
    
    # Bisa filter berdasarkan role dan status lain
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'jurusan')
    
    # Searchable berdasarkan username atau NIP/NISN
    search_fields = ('username', 'nip', 'nisn')

    # Field tambahan di form edit user
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'jurusan', 'nip', 'nisn')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'jurusan', 'nip', 'nisn')}),
    )
