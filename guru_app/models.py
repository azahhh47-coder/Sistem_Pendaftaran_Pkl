from django.db import models
from user_app.models import CustomUser
from admin_app.models import Perusahaan

# ============================================================
# MODEL INBOX GURU — Komunikasi dua arah (guru <-> siswa)
# ============================================================
class InboxGuru(models.Model):
    STATUS_CHOICES = [
        ("menunggu", "Menunggu"),
        ("wawancara", "Wawancara"),
        ("diterima", "Diterima"),
        ("ditolak", "Ditolak"),
        ("dipindahkan", "Dipindahkan"),
    ]

    PENGIRIM_CHOICES = [
        ("siswa", "Siswa"),
        ("guru", "Guru"),
        ("system", "Sistem"),
    ]

    guru = models.ForeignKey(
        CustomUser,
        to_field="nip",
        limit_choices_to={'role': 'guru'},
        on_delete=models.CASCADE,
        related_name="inbox_guru"
    )
    siswa = models.ForeignKey(
        CustomUser,
        to_field="nisn",
        limit_choices_to={'role': 'siswa'},
        on_delete=models.CASCADE,
        related_name="inbox_siswa_from_guru"
    )
    perusahaan = models.ForeignKey(
        Perusahaan,
        to_field="nama_perusahaan",
        on_delete=models.CASCADE,
        related_name="inbox_perusahaan_guru"
    )

    pesan = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="menunggu")
    tanggal_wawancara = models.DateTimeField(blank=True, null=True)
    tanggal_kirim = models.DateTimeField(auto_now_add=True)

    perusahaan_lama = models.ForeignKey(
        Perusahaan,
        to_field="nama_perusahaan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inbox_perusahaan_lama_guru"
    )
    perusahaan_baru = models.ForeignKey(
        Perusahaan,
        to_field="nama_perusahaan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inbox_perusahaan_baru_guru"
    )
    alasan_pemindahan = models.TextField(blank=True, null=True)

    # 🔹 Menandakan siapa yang kirim pesan
    dikirim_oleh = models.CharField(
        max_length=10,
        choices=PENGIRIM_CHOICES,
        default="guru",  # ubah default ke guru biar pesan awal tampil benar
        help_text="Menandakan siapa pengirim pesan (siswa/guru/sistem)"
    )

    is_read = models.BooleanField(default=False)  # True jika penerima sudah baca
    is_active = models.BooleanField(default=True)

    def __str__(self):
        pengirim = (
            self.guru.get_full_name() if self.dikirim_oleh == "guru"
            else self.siswa.get_full_name() if self.dikirim_oleh == "siswa"
            else "Sistem"
        )
        penerima = (
            self.siswa.get_full_name() if self.dikirim_oleh == "guru"
            else self.guru.get_full_name()
        )
        return f"Pesan dari {pengirim} ke {penerima} — {self.status}"
