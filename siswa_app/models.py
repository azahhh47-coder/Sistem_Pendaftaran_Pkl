from django.db import models
from user_app.models import CustomUser
from admin_app.models import Perusahaan

# ===============================
# MODEL PENDAFTARAN PKL
# ===============================
class PendaftaranPKL(models.Model):
    siswa = models.ForeignKey(
        CustomUser,
        to_field="nisn",
        limit_choices_to={'role': 'siswa'},
        on_delete=models.CASCADE,
        related_name="pendaftaran_pkl"
    )
    perusahaan = models.ForeignKey(
        Perusahaan,
        to_field="nama_perusahaan",
        on_delete=models.CASCADE,
        related_name="pendaftaran_perusahaan_siswa"
    )
    KELAS_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C')]
    kelas = models.CharField(max_length=1, choices=KELAS_CHOICES, default='A')
    alasan = models.TextField()
    cv = models.FileField(upload_to="cv_siswa/")
    STATUS_CHOICES = [
        ("menunggu", "Menunggu"),
        ("wawancara", "Wawancara"),
        ("diterima", "Diterima"),
        ("ditolak", "Ditolak"),
        ("dipindahkan", "Dipindahkan"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="menunggu")
    tanggal_wawancara = models.DateTimeField(blank=True, null=True)
    tanggal_daftar = models.DateTimeField(auto_now_add=True)
    notifikasi = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.siswa} ({self.kelas}) daftar {self.perusahaan}"


# ===============================
# MODEL INBOX SISWA (LAMA, OPSIONAL)
# ===============================
class InboxSiswa(models.Model):
    siswa = models.ForeignKey(
        CustomUser,
        to_field="nisn",
        limit_choices_to={'role': 'siswa'},
        on_delete=models.CASCADE,
        related_name="inbox_siswa"
    )
    guru = models.ForeignKey(
        CustomUser,
        to_field="nip",
        limit_choices_to={'role': 'guru'},
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inbox_siswa_guru"
    )
    perusahaan = models.ForeignKey(
        Perusahaan,
        to_field="nama_perusahaan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inbox_siswa_perusahaan"
    )
    pesan = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("menunggu", "Menunggu"),
            ("wawancara", "Wawancara"),
            ("diterima", "Diterima"),
            ("ditolak", "Ditolak"),
            ("dipindahkan", "Dipindahkan"),
        ],
        default="menunggu"
    )
    tanggal_kirim = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="True jika siswa sudah membaca pesan.")

    class Meta:
        ordering = ['-tanggal_kirim']

    def __str__(self):
        perusahaan_nama = self.perusahaan.nama_perusahaan if self.perusahaan else "Belum ada"
        return f"InboxSiswa {self.siswa} ({perusahaan_nama}) [DEPRECATED]"
