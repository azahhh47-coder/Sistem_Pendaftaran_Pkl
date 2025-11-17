from django.db import models
from user_app.models import CustomUser

class Perusahaan(models.Model):
    nama_perusahaan = models.CharField(max_length=255, primary_key=True)
    jurusan = models.CharField(max_length=50, choices=CustomUser.JURUSAN_CHOICES)
    alamat = models.TextField()
    deskripsi = models.TextField()
    foto_perusahaan = models.ImageField(upload_to="perusahaan_foto/", blank=True, null=True)

    def __str__(self):
        return f"{self.nama_perusahaan} ({self.jurusan})"
