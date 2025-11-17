from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user_app.models import CustomUser
from django.contrib.auth import get_user_model
from admin_app.models import Perusahaan
from siswa_app.models import PendaftaranPKL, InboxSiswa
from .models import InboxGuru
from django.utils import timezone

User = get_user_model()

# DASHBOARD GURU AGRO ============================================
@login_required
def dashboard_agro(request):
    guru = request.user

    # Session tetap aktif sampai browser ditutup
    request.session.set_expiry(0)
    request.session.modified = True
    
    # 🔹 Ambil semua pendaftaran PKL sesuai jurusan guru
    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="agro"
    ).order_by("-id")

    # 🔹 Pesan dari siswa yang belum dibaca
    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    # 🔹 Notifikasi ketika baru login
    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru Agro!")
        request.session["just_logged_in"] = False  # reset flag

    context = {
        "title": "Dashboard Guru Agro",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/agro/home.html", context)
# Terima Siswa Agro ---
@login_required
def terima_siswa_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",  # ✅ tambahkan ini
            is_read=False,  # ✅ biar gak keitung notif
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_agro")
# Tolak siswa Agro ---
@login_required
def tolak_siswa_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",  # ✅
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_agro")
# Jadwal Wawancara Siswa Agro ---
@login_required
def jadwalkan_wawancara_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")

        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_agro")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 🌱",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",  # ✅
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_agro")

    context = {"title": "Jadwalkan Wawancara", "siswa": siswa}
    return render(request, "guru_app/agro/jadwal_wawancara.html", context)
# Pindahkan perusahaan agro ---
@login_required
def pindahkan_siswa_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")

        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_agro", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",  # ✅
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_agro")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    context = {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    }
    return render(request, "guru_app/agro/pindahkan_siswa.html", context)
# Menunggu Siswa Agro ---
@login_required
def menunggu_siswa_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari pihak perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",  # ✅
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_agro")
# Inbox Guru Agro ------ 
@login_required
def inbox_guru_agro(request):
    guru = request.user

    # 🔹 Ambil semua pesan jurusan Agro (semua guru), hilangkan duplikat per siswa/pesan/status
    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="agro"
    ).order_by("-tanggal_kirim")

    # 🔹 Hilangkan duplikat manual (bisa dipakai di SQLite/MySQL)
    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    # 🔹 Tandai pesan siswa → guru ini sebagai dibaca
    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_agro")

        # 🔹 Ambil siswa valid
        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_agro")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        # =============================================================
        # 🔹 Cek duplikat di InboxGuru (per guru)
        # =============================================================
        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_agro")

        # =============================================================
        # 🔥 Broadcast ke semua guru — tetap catat semua aksi
        # =============================================================
        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="agro")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        # =============================================================
        # 🔥 Notifikasi siswa — hanya 1 entry per aksi/hari
        # =============================================================
        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"  # 20 karakter pertama
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_agro")

    context = {
        "title": "Inbox Guru Agro",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="agro"),
    }
    return render(request, "guru_app/agro/inbox.html", context)
# Detai pendaftaran Agro ---
@login_required
def detail_siswa_agro(request, nisn, pk):
    # ambil data siswa berdasarkan nisn
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")

    # ambil pendaftaran sesuai id (pk) yang diklik di dashboard guru
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    # kirim semua data ke template
    context = {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    }

    return render(request, "guru_app/agro/detail_pendaftaran.html", context)
# Data Siswa Agro 
@login_required
def data_agro(request):
    # Ambil semua siswa jurusan agro dan urutkan berdasarkan nama depan (abjad)
    users = CustomUser.objects.filter(
        role="siswa", jurusan__iexact="agro"
    ).order_by("first_name")

    # Ambil semua data pendaftaran PKL siswa agro
    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="agro")
    }

    # Gabungkan data siswa + status pendaftaran
    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": sudah_daftar,
        })

    return render(request, "guru_app/agro/data_siswa.html", {
        "title": "Data Siswa Agro",
        "siswa_data": siswa_data,
    })
# Data Perusahaan Agro ---
@login_required
def perusahaan_agro_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="agro").order_by("nama_perusahaan")
    return render(request, "guru_app/agro/data_perusahaan/perusahaan_agro.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan AGRO (Guru)"
    })
# Create Perusahaan Agro ---
@login_required
def perusahaan_agro_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "agro")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        # Validasi form
        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_agro_guru_create")

        # Buat nama unik (misal: Yogya - AGRO)
        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        # Cek apakah sudah ada
        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_agro_guru_create")

        # Simpan ke database
        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_agro_guru")

    return render(request, "guru_app/agro/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan AGRO (Guru)"
    })
# Detail Perusahaan Agro ---
@login_required
def perusahaan_agro_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/agro/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan Agro ---
@login_required
def perusahaan_agro_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "agro")

        # Validasi input
        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_agro_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        # Update data
        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_agro_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/agro/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete Perusahaan Agro ---
@login_required
def perusahaan_agro_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_agro_guru")


# DASHBOARD GURU PM ============================================
@login_required
def dashboard_pm(request):
    guru = request.user

    # Session tetap aktif sampai browser ditutup
    request.session.set_expiry(0)
    request.session.modified = True
    
    # 🔹 Ambil semua pendaftaran PKL sesuai jurusan guru
    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="pm"
    ).order_by("-id")

    # 🔹 Pesan dari siswa yang belum dibaca
    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    # 🔹 Notifikasi ketika baru login
    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru PM!")
        request.session["just_logged_in"] = False  # reset flag

    context = {
        "title": "Dashboard Guru PM",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/pm/home.html", context)
# Terima Siswa PM ---
@login_required
def terima_siswa_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_pm")
# Tolak Siswa PM ---
@login_required
def tolak_siswa_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_pm")
# Jadwal Wawancara Siswa PM ---
@login_required
def jadwalkan_wawancara_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")
        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_pm")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 📊",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_pm")

    context = {"title": "Jadwalkan Wawancara", "siswa": siswa}
    return render(request, "guru_app/pm/jadwal_wawancara.html", context)
# Pindahkan siswa PM ---
@login_required
def pindahkan_siswa_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")
        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_pm", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_pm")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    context = {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    }
    return render(request, "guru_app/pm/pindahkan_siswa.html", context)
# Menunggu Siswa PM ---
@login_required
def menunggu_siswa_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari pihak perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_pm")
# Inbox Guru PM ------
@login_required
def inbox_guru_pm(request):
    guru = request.user

    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="pm"
    ).order_by("-tanggal_kirim")

    # Hilangkan duplikat manual
    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    # Tandai pesan siswa → guru ini sebagai dibaca
    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_pm")

        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_pm")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        # Cek duplikat
        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_pm")

        # Broadcast ke semua guru PM
        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="pm")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        # Notifikasi siswa — hanya 1 entry per aksi/hari
        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_pm")

    context = {
        "title": "Inbox Guru PM",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="pm"),
    }
    return render(request, "guru_app/pm/inbox.html", context)
# Detail pendaftaran PM ---
@login_required
def detail_siswa_pm(request, nisn, pk):
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    context = {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    }

    return render(request, "guru_app/pm/detail_pendaftaran.html", context)
# Data Siswa PM ---
@login_required
def data_pm(request):
    users = CustomUser.objects.filter(
        role="siswa", jurusan__iexact="pm"
    ).order_by("first_name")

    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="pm")
    }

    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": sudah_daftar,
        })

    return render(request, "guru_app/pm/data_siswa.html", {
        "title": "Data Siswa PM",
        "siswa_data": siswa_data,
    })
# Data Perusahaan PM ---
@login_required
def perusahaan_pm_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="pm").order_by("nama_perusahaan")
    return render(request, "guru_app/pm/data_perusahaan/perusahaan_pm.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan PM (Guru)"
    })
# Create Perusahaan PM ---
@login_required
def perusahaan_pm_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "pm")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_pm_guru_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_pm_guru_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_pm_guru")

    return render(request, "guru_app/pm/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan PM (Guru)"
    })
# Detail Perusahaan PM ---
@login_required
def perusahaan_pm_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/pm/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan PM ---
@login_required
def perusahaan_pm_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "pm")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_pm_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_pm_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/pm/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete Perusahaan PM ---
@login_required
def perusahaan_pm_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_pm_guru")


# DASHBOARD GURU RPL ============================================
@login_required
def dashboard_rpl(request):
    guru = request.user

    request.session.set_expiry(0)
    request.session.modified = True

    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="rpl"
    ).order_by("-id")

    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru RPL!")
        request.session["just_logged_in"] = False

    context = {
        "title": "Dashboard Guru RPL",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/rpl/home.html", context)
# Terima siswa RPL
@login_required
def terima_siswa_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_rpl")
# Tolak siswa RPL
@login_required
def tolak_siswa_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_rpl")
# Jadwalkan wawancara RPL
@login_required
def jadwalkan_wawancara_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")

        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_rpl")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 💻",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_rpl")

    return render(request, "guru_app/rpl/jadwal_wawancara.html", {"title": "Jadwalkan Wawancara", "siswa": siswa})
# Pindahkan siswa RPL
@login_required
def pindahkan_siswa_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")

        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_rpl", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_rpl")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    return render(request, "guru_app/rpl/pindahkan_siswa.html", {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    })
# Status menunggu siswa RPL
@login_required
def menunggu_siswa_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_rpl")
# Inbox guru RPL
@login_required
def inbox_guru_rpl(request):
    guru = request.user

    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="rpl"
    ).order_by("-tanggal_kirim")

    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_rpl")

        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_rpl")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_rpl")

        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="rpl")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_rpl")

    return render(request, "guru_app/rpl/inbox.html", {
        "title": "Inbox Guru RPL",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="rpl"),
    })
# Detail pendaftaran RPL
@login_required
def detail_siswa_rpl(request, nisn, pk):
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    return render(request, "guru_app/rpl/detail_pendaftaran.html", {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    })
# Data siswa RPL
@login_required
def data_rpl(request):
    users = CustomUser.objects.filter(role="siswa", jurusan__iexact="rpl").order_by("first_name")

    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="rpl")
    }

    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({"obj": siswa, "sudah_daftar": sudah_daftar})

    return render(request, "guru_app/rpl/data_siswa.html", {
        "title": "Data Siswa RPL",
        "siswa_data": siswa_data,
    })
# Data perusahaan RPL
@login_required
def perusahaan_rpl_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="rpl").order_by("nama_perusahaan")
    return render(request, "guru_app/rpl/data_perusahaan/perusahaan_rpl.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan RPL (Guru)"
    })
# Create perusahaan RPL
@login_required
def perusahaan_rpl_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "rpl")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_rpl_guru_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_rpl_guru_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_rpl_guru")

    return render(request, "guru_app/rpl/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan RPL (Guru)"
    })
# Detail perusahaan RPL
@login_required
def perusahaan_rpl_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/rpl/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit perusahaan RPL ---
@login_required
def perusahaan_rpl_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "rpl")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_rpl_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_rpl_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/rpl/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete perusahaan RPL ---
@login_required
def perusahaan_rpl_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_rpl_guru")


# DASHBOARD GURU TEI ============================================
@login_required
def dashboard_tei(request):
    guru = request.user

    request.session.set_expiry(0)
    request.session.modified = True

    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="tei"
    ).order_by("-id")

    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru TEI!")
        request.session["just_logged_in"] = False

    context = {
        "title": "Dashboard Guru TEI",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/tei/home.html", context)
# Terima siswa TEI
@login_required
def terima_siswa_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tei")
# Tolak siswa TEI
@login_required
def tolak_siswa_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tei")
# Jadwalkan wawancara TEI
@login_required
def jadwalkan_wawancara_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")

        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_tei")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 💻",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_tei")

    return render(request, "guru_app/tei/jadwal_wawancara.html", {"title": "Jadwalkan Wawancara", "siswa": siswa})
# Pindahkan siswa TEI
@login_required
def pindahkan_siswa_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")

        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_tei", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_tei")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    return render(request, "guru_app/tei/pindahkan_siswa.html", {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    })
# Status menunggu siswa TEI
@login_required
def menunggu_siswa_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tei")
# Inbox guru TEI
@login_required
def inbox_guru_tei(request):
    guru = request.user

    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="tei"
    ).order_by("-tanggal_kirim")

    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_tei")

        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_tei")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_tei")

        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="tei")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_tei")

    return render(request, "guru_app/tei/inbox.html", {
        "title": "Inbox Guru TEI",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="tei"),
    })
# Detail pendaftaran TEI
@login_required
def detail_siswa_tei(request, nisn, pk):
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    return render(request, "guru_app/tei/detail_pendaftaran.html", {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    })
# Data siswa TEI
@login_required
def data_tei(request):
    users = CustomUser.objects.filter(role="siswa", jurusan__iexact="tei").order_by("first_name")

    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="tei")
    }

    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({"obj": siswa, "sudah_daftar": sudah_daftar})

    return render(request, "guru_app/tei/data_siswa.html", {
        "title": "Data Siswa TEI",
        "siswa_data": siswa_data,
    })
# Data perusahaan TEI
@login_required
def perusahaan_tei_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tei").order_by("nama_perusahaan")
    return render(request, "guru_app/tei/data_perusahaan/perusahaan_tei.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan TEI (Guru)"
    })
# Create perusahaan TEI
@login_required
def perusahaan_tei_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tei")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tei_guru_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tei_guru_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tei_guru")

    return render(request, "guru_app/tei/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan TEI (Guru)"
    })
# Detail perusahaan TEI
@login_required
def perusahaan_tei_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/tei/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit perusahaan TEI ---
@login_required
def perusahaan_tei_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tei")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tei_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tei_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/tei/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete perusahaan TEI
@login_required
def perusahaan_tei_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tei_guru")


# DASHBOARD GURU TKI ============================================
@login_required
def dashboard_tki(request):
    guru = request.user

    request.session.set_expiry(0)
    request.session.modified = True

    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="tki"
    ).order_by("-id")

    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru TKI!")
        request.session["just_logged_in"] = False

    context = {
        "title": "Dashboard Guru TKI",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/tki/home.html", context)
# Terima siswa TKI
@login_required
def terima_siswa_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tki")
# Tolak siswa TKI
@login_required
def tolak_siswa_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tki")
# Jadwalkan wawancara TKI
@login_required
def jadwalkan_wawancara_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")

        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_tki")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 💻",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_tki")

    return render(request, "guru_app/tki/jadwal_wawancara.html", {"title": "Jadwalkan Wawancara", "siswa": siswa})
# Pindahkan siswa TKI
@login_required
def pindahkan_siswa_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")

        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_tki", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_tki")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    return render(request, "guru_app/tki/pindahkan_siswa.html", {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    })
# Status menunggu siswa TKI
@login_required
def menunggu_siswa_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tki")
# Inbox guru TKI
@login_required
def inbox_guru_tki(request):
    guru = request.user

    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="tki"
    ).order_by("-tanggal_kirim")

    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_tki")

        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_tki")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_tki")

        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="tki")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_tki")

    return render(request, "guru_app/tki/inbox.html", {
        "title": "Inbox Guru TKI",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="tki"),
    })
# Detail pendaftaran TKI
@login_required
def detail_siswa_tki(request, nisn, pk):
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    return render(request, "guru_app/tki/detail_pendaftaran.html", {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    })
# Data siswa TKI
@login_required
def data_tki(request):
    users = CustomUser.objects.filter(role="siswa", jurusan__iexact="tki").order_by("first_name")

    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="tki")
    }

    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({"obj": siswa, "sudah_daftar": sudah_daftar})

    return render(request, "guru_app/tki/data_siswa.html", {
        "title": "Data Siswa TKI",
        "siswa_data": siswa_data,
    })
# Data perusahaan TKI
@login_required
def perusahaan_tki_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tki").order_by("nama_perusahaan")
    return render(request, "guru_app/tki/data_perusahaan/perusahaan_tki.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan TKI (Guru)"
    })
# Create perusahaan TKI
@login_required
def perusahaan_tki_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tki")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tki_guru_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tki_guru_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tki_guru")

    return render(request, "guru_app/tki/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan TKI (Guru)"
    })
# Detail perusahaan TKI
@login_required
def perusahaan_tki_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/tki/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit perusahaan TKI
@login_required
def perusahaan_tki_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tki")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tki_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tki_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/tki/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete perusahaan TKI
@login_required
def perusahaan_tki_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tki_guru")


# DASHBOARD GURU TKJ ============================================
@login_required
def dashboard_tkj(request):
    guru = request.user

    request.session.set_expiry(0)
    request.session.modified = True

    pendaftarans = PendaftaranPKL.objects.filter(
        perusahaan__jurusan__iexact="tkj"
    ).order_by("-id")

    notif_unread = InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).order_by("-tanggal_kirim")

    if request.session.get("just_logged_in", False):
        messages.info(request, "👋 Selamat datang kembali di Dashboard Guru TKJ!")
        request.session["just_logged_in"] = False

    context = {
        "title": "Dashboard Guru TKJ",
        "user": guru,
        "pendaftarans": pendaftarans,
        "inbox_unread_count": notif_unread.count(),
    }
    return render(request, "guru_app/tkj/home.html", context)
# Terima siswa TKJ
@login_required
def terima_siswa_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "diterima"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, selamat! Kamu telah diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}.",
            status="diterima",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.success(request, f"✅ Siswa {siswa.first_name} {siswa.last_name} diterima dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tkj")
# Tolak siswa TKJ
@login_required
def tolak_siswa_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "ditolak"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, mohon maaf, kamu belum diterima untuk PKL di {pendaftaran.perusahaan.nama_perusahaan}. Tetap semangat ya!",
            status="ditolak",
            dikirim_oleh="guru",
            is_read=False,
        )
        messages.error(request, f"❌ Siswa {siswa.first_name} {siswa.last_name} ditolak dan notifikasi terkirim.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tkj")
# Jadwalkan wawancara TKJ
@login_required
def jadwalkan_wawancara_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if request.method == "POST":
        tanggal_wawancara = request.POST.get("tanggal_wawancara")

        if not tanggal_wawancara:
            messages.error(request, "Tanggal wawancara harus diisi!")
            return redirect("dashboard_tkj")

        pendaftaran.status = "wawancara"
        pendaftaran.tanggal_wawancara = tanggal_wawancara
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, kamu dijadwalkan wawancara di {pendaftaran.perusahaan.nama_perusahaan} pada {tanggal_wawancara}. 💻",
            status="wawancara",
            tanggal_wawancara=tanggal_wawancara,
            tanggal_kirim=timezone.now(),
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.info(request, f"📅 Jadwal wawancara untuk {siswa.first_name} telah ditentukan.", extra_tags="wawancara")
        return redirect("dashboard_tkj")

    return render(request, "guru_app/tkj/jadwal_wawancara.html", {"title": "Jadwalkan Wawancara", "siswa": siswa})
# Pindahkan siswa TKJ
@login_required
def pindahkan_siswa_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
    perusahaan_lama = pendaftaran.perusahaan if pendaftaran else None

    if request.method == "POST":
        perusahaan_baru_nama = request.POST.get("perusahaan_baru")
        alasan = request.POST.get("alasan")

        if not perusahaan_baru_nama or not alasan:
            messages.error(request, "Harap pilih perusahaan baru dan tuliskan alasan pemindahan.")
            return redirect("pindahkan_siswa_tkj", nisn=nisn)

        perusahaan_baru = get_object_or_404(
            Perusahaan,
            nama_perusahaan=perusahaan_baru_nama,
            jurusan__iexact=siswa.jurusan
        )

        if pendaftaran:
            pendaftaran.perusahaan = perusahaan_baru
            pendaftaran.status = "dipindahkan"
            pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=perusahaan_lama,
            perusahaan_lama=perusahaan_lama,
            perusahaan_baru=perusahaan_baru,
            alasan_pemindahan=alasan,
            pesan=alasan,
            status="dipindahkan",
            dikirim_oleh="guru",
            is_read=False,
        )

        messages.warning(request, f"🔶 Siswa {siswa.first_name} berhasil dipindahkan ke {perusahaan_baru.nama_perusahaan}.", extra_tags="dipindahkan")
        return redirect("dashboard_tkj")

    perusahaan_list = Perusahaan.objects.filter(jurusan__iexact=siswa.jurusan)
    if perusahaan_lama:
        perusahaan_list = perusahaan_list.exclude(nama_perusahaan=perusahaan_lama.nama_perusahaan)

    return render(request, "guru_app/tkj/pindahkan_siswa.html", {
        "title": "Pindahkan Siswa",
        "siswa": siswa,
        "perusahaan_lama": perusahaan_lama,
        "perusahaan_list": perusahaan_list,
    })
# Status menunggu siswa TKJ
@login_required
def menunggu_siswa_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()

    if pendaftaran:
        pendaftaran.status = "menunggu"
        pendaftaran.save()

        InboxGuru.objects.create(
            guru=request.user,
            siswa=siswa,
            perusahaan=pendaftaran.perusahaan,
            pesan=f"Halo {siswa.first_name}, status kamu saat ini masih dalam tahap menunggu konfirmasi dari perusahaan.",
            status="menunggu",
            dikirim_oleh="guru",
            is_read=True,
        )
        messages.info(request, f"🕓 Status siswa {siswa.first_name} {siswa.last_name} diubah menjadi menunggu.")
    else:
        messages.error(request, "Data pendaftaran tidak ditemukan.")

    return redirect("dashboard_tkj")
# Inbox guru TKJ
@login_required
def inbox_guru_tkj(request):
    guru = request.user

    raw_inbox = InboxGuru.objects.filter(
        siswa__jurusan__iexact="tkj"
    ).order_by("-tanggal_kirim")

    seen = set()
    inbox = []
    for msg in raw_inbox:
        key = (msg.siswa.id, msg.pesan, msg.status)
        if key not in seen:
            inbox.append(msg)
            seen.add(key)

    InboxGuru.objects.filter(
        guru=guru,
        is_read=False,
        dikirim_oleh="siswa"
    ).update(is_read=True)

    if request.method == "POST":
        siswa_nisn = request.POST.get("siswa_nisn")
        pesan_text = request.POST.get("pesan")

        if not siswa_nisn or not pesan_text:
            messages.error(request, "Harap pilih siswa dan isi pesan sebelum mengirim.")
            return redirect("inbox_guru_tkj")

        siswa = CustomUser.objects.filter(nisn=siswa_nisn, role="siswa").first()
        if not siswa:
            messages.error(request, "Siswa tidak ditemukan.")
            return redirect("inbox_guru_tkj")

        pendaftaran = PendaftaranPKL.objects.filter(siswa=siswa).last()
        perusahaan = pendaftaran.perusahaan if pendaftaran else None

        if InboxGuru.objects.filter(
            guru=guru,
            siswa=siswa,
            pesan=pesan_text,
            dikirim_oleh="guru",
            tanggal_kirim__date=timezone.now().date()
        ).exists():
            messages.warning(request, "⚠️ Pesan ini sudah pernah dikirim hari ini.")
            return redirect("inbox_guru_tkj")

        semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="tkj")
        for g in semua_guru:
            InboxGuru.objects.create(
                guru=g,
                siswa=siswa,
                perusahaan=perusahaan,
                pesan=pesan_text,
                status="menunggu",
                tanggal_kirim=timezone.now(),
                dikirim_oleh="guru",
                is_read=False,
            )

        kode_group = f"{siswa.nisn}-{timezone.now().date()}-{pesan_text[:20]}"
        if not InboxSiswa.objects.filter(siswa=siswa, kode_group=kode_group).exists():
            InboxSiswa.objects.create(
                siswa=siswa,
                guru=guru,
                perusahaan=perusahaan,
                pesan=f"Pesan dari {guru.first_name}: {pesan_text}",
                status="menunggu",
                kode_group=kode_group,
                is_read=False
            )

        messages.success(request, "📨 Pesan berhasil dikirim ke semua guru dan ke siswa tanpa duplikat.")
        return redirect("inbox_guru_tkj")

    return render(request, "guru_app/tkj/inbox.html", {
        "title": "Inbox Guru TKJ",
        "inbox_guru": inbox,
        "siswa_list": CustomUser.objects.filter(role="siswa", jurusan__iexact="tkj"),
    })
# Detail pendaftaran TKJ
@login_required
def detail_siswa_tkj(request, nisn, pk):
    siswa = CustomUser.objects.get(nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    return render(request, "guru_app/tkj/detail_pendaftaran.html", {
        "title": f"Detail Pendaftaran {siswa.first_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran,
        "kelas_pendaftaran": pendaftaran.kelas,
        "perusahaan_daftar": pendaftaran.perusahaan,
        "tanggal_daftar": pendaftaran.tanggal_daftar,
        "status": pendaftaran.status,
    })
# Data siswa TKJ
@login_required
def data_tkj(request):
    users = CustomUser.objects.filter(role="siswa", jurusan__iexact="tkj").order_by("first_name")

    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
        .filter(siswa__jurusan__iexact="tkj")
    }

    siswa_data = []
    for siswa in users:
        sudah_daftar = siswa.nisn in pendaftar_dict
        siswa_data.append({"obj": siswa, "sudah_daftar": sudah_daftar})

    return render(request, "guru_app/tkj/data_siswa.html", {
        "title": "Data Siswa TKJ",
        "siswa_data": siswa_data,
    })
# Data perusahaan TKJ
@login_required
def perusahaan_tkj_guru(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tkj").order_by("nama_perusahaan")
    return render(request, "guru_app/tkj/data_perusahaan/perusahaan_tkj.html", {
        "perusahaan": perusahaan,
        "title": "Data Perusahaan TKJ (Guru)"
    })
# Create perusahaan TKJ
@login_required
def perusahaan_tkj_guru_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tkj")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tkj_guru_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tkj_guru_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tkj_guru")

    return render(request, "guru_app/tkj/data_perusahaan/create.html", {
        "title": "Tambah Perusahaan TKJ (Guru)"
    })
# Detail perusahaan TKJ
@login_required
def perusahaan_tkj_guru_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "guru_app/tkj/data_perusahaan/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit perusahaan TKJ ---
@login_required
def perusahaan_tkj_guru_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tkj")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tkj_guru_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tkj_guru_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "guru_app/tkj/data_perusahaan/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Delete perusahaan TKJ
@login_required
def perusahaan_tkj_guru_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tkj_guru")

