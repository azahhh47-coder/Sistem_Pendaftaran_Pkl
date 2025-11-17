from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

def validate_nip(value):
    if not value.isdigit() or len(value) != 16:
        raise ValidationError("NIP guru harus 16 digit angka.")

def validate_nisn(value):
    if not value.isdigit() or len(value) != 10:
        raise ValidationError("NISN siswa harus 10 digit angka.")

class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, password=None, **extra_fields):
        role = extra_fields.get("role")
        if role == "admin" and not username:
            raise ValueError("Username wajib diisi untuk admin.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("guru", "Guru"),
        ("siswa", "Siswa"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    nama = models.CharField(max_length=150, blank=True, null=True)

    JURUSAN_CHOICES = (
        ("agro", "Agribisnis Pembibitan Tanaman"),
        ("pm", "Pemasaran"),
        ("rpl", "Rekayasa Perangkat Lunak"),
        ("tki", "Kimia Industri"),
        ("tei", "Teknik Elektronika Industri"),
        ("tkj", "Teknik Komputer dan Jaringan"),
    )
    jurusan = models.CharField(max_length=50, choices=JURUSAN_CHOICES, blank=True, null=True)

    nip = models.CharField(max_length=16, blank=True, null=True, unique=True, validators=[validate_nip])
    nisn = models.CharField(max_length=10, blank=True, null=True, unique=True, validators=[validate_nisn])
    foto_guru = models.ImageField(upload_to='guru_foto/', blank=True, null=True)
    foto_siswa = models.ImageField(upload_to='siswa_foto/', blank=True, null=True)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.role:
            raise ValidationError("Role harus diisi (admin/guru/siswa).")
        if self.role == "admin":
            self.is_staff = True
            self.is_superuser = True
            self.is_active = True
            if not self.username:
                raise ValidationError("Username wajib diisi untuk admin.")
            self.first_name = self.first_name or ""
            self.last_name = self.last_name or ""
        elif self.role == "guru":
            if not self.nip:
                raise ValidationError("Guru wajib memiliki NIP.")
            if not self.first_name or not self.last_name:
                raise ValidationError("Guru wajib memiliki nama depan & belakang.")
            self.is_staff = False
            self.is_superuser = False
        elif self.role == "siswa":
            if not self.nisn:
                raise ValidationError("Siswa wajib memiliki NISN.")
            if not self.first_name or not self.last_name:
                raise ValidationError("Siswa wajib memiliki nama depan & belakang.")
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username or self.nama} ({self.role})"
