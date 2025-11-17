from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from siswa_app.models import PendaftaranPKL, InboxSiswa
from .forms import PendaftaranPKLForm
from django.utils import timezone
from guru_app.models import InboxGuru  # pastikan ini import model inbox guru
from django.contrib.auth import get_user_model
from admin_app.models import Perusahaan 
from django.contrib import messages
from user_app.models import CustomUser
from django.shortcuts import render, get_object_or_404

User = get_user_model()

# Home siswa Agro ================================================================
@login_required
def dashboard_siswa_agro(request):
    siswa = request.user

    # Ambil semua pendaftaran siswa
    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")

    # Ambil inbox dari guru untuk siswa ini (khusus jurusan AGRO)
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="agro"
    ).order_by("-tanggal_kirim")

    # Update status terbaru tiap pendaftaran
    for p in pendaftarans:
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            if p.status_terbaru == "wawancara":
                p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara or p.tanggal_wawancara
            else:
                p.tanggal_wawancara_display = None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    # Tentukan apakah kolom wawancara ditampilkan
    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)

    # Hitung jumlah pesan guru belum dibaca
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/agro/home.html", {
        "title": "Dashboard Siswa AGRO",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })
# Data Perusahaan Agro ---
@login_required
def perusahaan_siswa_list_agro(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="agro").order_by("nama_perusahaan")
    return render(request, "siswa_app/agro/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan Agro",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan Agro ---
@login_required
def perusahaan_siswa_detail_agro(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="agro")
    return render(request, "siswa_app/agro/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL Agro ---
@login_required
def pendaftaran_pkl_agro(request):
    siswa = request.user

    # Pastikan siswa benar-benar jurusan AGRO
    if siswa.jurusan.lower() != "agro":
        messages.error(request, "Anda bukan siswa jurusan Agro.")
        return redirect('dashboard_siswa_agro')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            #  CEGAH PKL DUPLIKAT
            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_agro')

            # SIMPAN PKL
            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()


            # KIRIM NOTIFIKASI KE SEMUA GURU AGRO (ANTI DUPLIKAT GLOBAL)
            semua_guru = CustomUser.objects.filter(
                role="guru",
                jurusan__iexact="agro"
            )

            # Cek apakah notifikasi siswa-perusahaan sudah pernah dibuat
            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            # SISWA HANYA MENERIMA 1 NOTIFIKASI SAJA
            if not InboxSiswa.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():

                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing Agro.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru Agro menerima notifikasi.")
            return redirect('dashboard_siswa_agro')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="agro"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/agro/pendaftaran.html", {
        "title": "Pendaftaran PKL Agro",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran Agro ---
@login_required
def edit_pendaftaran_agro(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "agro":
        messages.error(request, "Anda bukan siswa jurusan Agro.")
        return redirect('dashboard_siswa_agro')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_agro', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_agro')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="agro"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/agro/edit.html", {
        "title": "Edit Pendaftaran PKL Agro",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus Agro
@login_required
def pendaftaran_pkl_delete(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_agro")
# Inbox Agro
@login_required
def inbox_siswa_agro(request):
    user = request.user

    # 🔹 Ambil pesan dari InboxSiswa
    inbox_siswa = InboxSiswa.objects.filter(
        siswa=user
    ).order_by("-tanggal_kirim")

    # 🔹 Ambil pesan dari guru (InboxGuru → dikirim ke siswa)
    inbox_guru = InboxGuru.objects.filter(
        siswa=user,
        dikirim_oleh="guru"   # hanya pesan yang guru kirim
    ).order_by("-tanggal_kirim")

    # 🔹 Gabungkan dua inbox dalam satu list tanpa duplikat
    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    # 🔹 Hitung notif belum dibaca (dari dua tabel)
    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        +
        InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    # 🔹 Tandai pesan dari kedua tabel menjadi dibaca
    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/agro/inbox.html", {
        "title": "Inbox Siswa Agro",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })

# Home siswa PM ================================================================
@login_required
def dashboard_siswa_pm(request):
    siswa = request.user

    # Ambil semua pendaftaran siswa
    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")

    # Ambil inbox dari guru untuk siswa ini (khusus jurusan PM)
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="pm"
    ).order_by("-tanggal_kirim")  # pastikan yang terbaru paling atas

    # Update status terbaru tiap pendaftaran
    for p in pendaftarans:
        # Ambil inbox terbaru untuk perusahaan ini
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            if p.status_terbaru == "wawancara":
                p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara or p.tanggal_wawancara
            else:
                p.tanggal_wawancara_display = None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    # Tentukan apakah kolom wawancara ditampilkan
    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)

    # Hitung jumlah pesan guru belum dibaca
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/pm/home.html", {
        "title": "Dashboard Siswa PM",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })

# Data Perusahaan PM ---
@login_required
def perusahaan_siswa_list_pm(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="pm").order_by("nama_perusahaan")
    return render(request, "siswa_app/pm/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan PM",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan PM ---
@login_required
def perusahaan_siswa_detail_pm(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="pm")
    return render(request, "siswa_app/pm/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL PM ---
@login_required
def pendaftaran_pkl_pm(request):
    siswa = request.user

    # Pastikan siswa benar-benar jurusan PM
    if siswa.jurusan.lower() != "pm":
        messages.error(request, "Anda bukan siswa jurusan Pemasaran.")
        return redirect('dashboard_siswa_pm')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            # CEGAH PKL DUPLIKAT
            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_pm')

            # SIMPAN
            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()

            # KIRIM NOTIFIKASI KE SEMUA GURU PM
            semua_guru = CustomUser.objects.filter(
                role="guru",
                jurusan__iexact="pm"
            )

            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            #  SISWA HANYA MENERIMA 1 NOTIFIKASI
            if not InboxSiswa.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():

                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing Pemasaran.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru PM menerima notifikasi.")
            return redirect('dashboard_siswa_pm')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="pm"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/pm/pendaftaran.html", {
        "title": "Pendaftaran PKL PM",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran PM -----------------------------------------------------
@login_required
def edit_pendaftaran_pm(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "pm":
        messages.error(request, "Anda bukan siswa jurusan Pemasaran.")
        return redirect('dashboard_siswa_pm')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_pm', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_pm')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="pm"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/pm/edit.html", {
        "title": "Edit Pendaftaran PKL PM",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus PM
@login_required
def pendaftaran_pkl_delete_pm(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_pm")
# Inbox PM
@login_required
def inbox_siswa_pm(request):
    user = request.user

    inbox_siswa = InboxSiswa.objects.filter(
        siswa=user
    ).order_by("-tanggal_kirim")

    inbox_guru = InboxGuru.objects.filter(
        siswa=user,
        dikirim_oleh="guru"
    ).order_by("-tanggal_kirim")

    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        +
        InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/pm/inbox.html", {
        "title": "Inbox Siswa PM",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })


# Home siswa RPL ================================================================
@login_required
def dashboard_siswa_rpl(request):
    siswa = request.user

    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="rpl"
    ).order_by("-tanggal_kirim")

    for p in pendaftarans:
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara if latest_inbox.status == "wawancara" else None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/rpl/home.html", {
        "title": "Dashboard Siswa RPL",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })
# Data Perusahaan RPL ---
@login_required
def perusahaan_siswa_list_rpl(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="rpl").order_by("nama_perusahaan")
    return render(request, "siswa_app/rpl/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan RPL",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan RPL ---
@login_required
def perusahaan_siswa_detail_rpl(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="rpl")
    return render(request, "siswa_app/rpl/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL RPL ---
@login_required
def pendaftaran_pkl_rpl(request):
    siswa = request.user

    # Pastikan siswa benar-benar jurusan RPL
    if siswa.jurusan.lower() != "rpl":
        messages.error(request, "Anda bukan siswa jurusan RPL.")
        return redirect('dashboard_siswa_rpl')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            # CEGAH DUPLIKAT
            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_rpl')

            # SIMPAN PKL
            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()

            #  KIRIM NOTIFIKASI KE SEMUA GURU RPL
            semua_guru = CustomUser.objects.filter(
                role="guru",
                jurusan__iexact="rpl"
            )

            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            #SISWA HANYA MENERIMA 1 NOTIFIKASI
            if not InboxSiswa.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():

                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing RPL.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru RPL menerima notifikasi.")
            return redirect('dashboard_siswa_rpl')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="rpl"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/rpl/pendaftaran.html", {
        "title": "Pendaftaran PKL RPL",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran RPL ---
@login_required
def edit_pendaftaran_rpl(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "rpl":
        messages.error(request, "Anda bukan siswa jurusan RPL.")
        return redirect('dashboard_siswa_rpl')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_rpl', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_rpl')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="rpl"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/rpl/edit.html", {
        "title": "Edit Pendaftaran PKL RPL",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus RPL
@login_required
def pendaftaran_pkl_delete_rpl(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_rpl")
# Inbox RPL ---
@login_required
def inbox_siswa_rpl(request):
    user = request.user

    inbox_siswa = InboxSiswa.objects.filter(
        siswa=user
    ).order_by("-tanggal_kirim")

    inbox_guru = InboxGuru.objects.filter(
        siswa=user,
        dikirim_oleh="guru"
    ).order_by("-tanggal_kirim")

    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        +
        InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/rpl/inbox.html", {
        "title": "Inbox Siswa RPL",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })


# Home siswa TEI ================================================================
@login_required
def dashboard_siswa_tei(request):
    siswa = request.user

    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="tei"
    ).order_by("-tanggal_kirim")

    for p in pendaftarans:
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara if latest_inbox.status == "wawancara" else None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/tei/home.html", {
        "title": "Dashboard Siswa TEI",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })
# Data Perusahaan TEI ---
@login_required
def perusahaan_siswa_list_tei(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tei").order_by("nama_perusahaan")
    return render(request, "siswa_app/tei/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan TEI",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan TEI ---
@login_required
def perusahaan_siswa_detail_tei(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="tei")
    return render(request, "siswa_app/tei/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL TEI ---
@login_required
def pendaftaran_pkl_tei(request):
    siswa = request.user

    # Pastikan siswa benar-benar jurusan TEI
    if siswa.jurusan.lower() != "tei":
        messages.error(request, "Anda bukan siswa jurusan TEI.")
        return redirect('dashboard_siswa_tei')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            # CEGAH DUPLIKAT
            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_tei')

            # SIMPAN PKL
            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()

            # KIRIM NOTIFIKASI KE SEMUA GURU TEI
            semua_guru = CustomUser.objects.filter(
                role="guru",
                jurusan__iexact="tei"
            )

            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            # SISWA HANYA MENERIMA 1 NOTIF
            if not InboxSiswa.objects.filter(
                siswa=siswa,
                perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():

                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing TEI.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru TEI menerima notifikasi.")
            return redirect('dashboard_siswa_tei')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tei"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tei/pendaftaran.html", {
        "title": "Pendaftaran PKL TEI",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran TEI ---
@login_required
def edit_pendaftaran_tei(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "tei":
        messages.error(request, "Anda bukan siswa jurusan TEI.")
        return redirect('dashboard_siswa_tei')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa,
                perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_tei', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_tei')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tei"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tei/edit.html", {
        "title": "Edit Pendaftaran PKL TEI",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus TEI ---
@login_required
def pendaftaran_pkl_delete_tei(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_tei")
# Inbox TEI ---
@login_required
def inbox_siswa_tei(request):
    user = request.user

    inbox_siswa = InboxSiswa.objects.filter(
        siswa=user
    ).order_by("-tanggal_kirim")

    inbox_guru = InboxGuru.objects.filter(
        siswa=user,
        dikirim_oleh="guru"
    ).order_by("-tanggal_kirim")

    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        +
        InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/tei/inbox.html", {
        "title": "Inbox Siswa TEI",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })

# Home siswa TKI ================================================================
@login_required
def dashboard_siswa_tki(request):
    siswa = request.user

    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="tki"
    ).order_by("-tanggal_kirim")

    for p in pendaftarans:
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara if latest_inbox.status == "wawancara" else None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/tki/home.html", {
        "title": "Dashboard Siswa TKI",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })
# Data Perusahaan TKI ---
@login_required
def perusahaan_siswa_list_tki(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tki").order_by("nama_perusahaan")
    return render(request, "siswa_app/tki/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan TKI",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan TKI ---
@login_required
def perusahaan_siswa_detail_tki(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="tki")
    return render(request, "siswa_app/tki/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL TKI ---
@login_required
def pendaftaran_pkl_tki(request):
    siswa = request.user

    if siswa.jurusan.lower() != "tki":
        messages.error(request, "Anda bukan siswa jurusan TKI.")
        return redirect('dashboard_siswa_tki')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa, perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_tki')

            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()

            semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="tki")

            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa, perusahaan=pkl.perusahaan, dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            if not InboxSiswa.objects.filter(
                siswa=siswa, perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():
                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing TKI.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru TKI menerima notifikasi.")
            return redirect('dashboard_siswa_tki')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tki"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tki/pendaftaran.html", {
        "title": "Pendaftaran PKL TKI",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran TKI ---
@login_required
def edit_pendaftaran_tki(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "tki":
        messages.error(request, "Anda bukan siswa jurusan TKI.")
        return redirect('dashboard_siswa_tki')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa, perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_tki', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_tki')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tki"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tki/edit.html", {
        "title": "Edit Pendaftaran PKL TKI",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus TKI ---
@login_required
def pendaftaran_pkl_delete_tki(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_tki")
# Inbox TKI ---
@login_required
def inbox_siswa_tki(request):
    user = request.user

    inbox_siswa = InboxSiswa.objects.filter(siswa=user).order_by("-tanggal_kirim")
    inbox_guru = InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru").order_by("-tanggal_kirim")

    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        + InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/tki/inbox.html", {
        "title": "Inbox Siswa TKI",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })

# Home siswa TKJ ================================================================
@login_required
def dashboard_siswa_tkj(request):
    siswa = request.user

    pendaftarans = PendaftaranPKL.objects.filter(siswa=siswa).order_by("-id")
    inbox_siswa = InboxGuru.objects.filter(
        siswa=siswa,
        dikirim_oleh="guru",
        guru__jurusan__iexact="tkj"
    ).order_by("-tanggal_kirim")

    for p in pendaftarans:
        latest_inbox = inbox_siswa.filter(perusahaan=p.perusahaan).first()
        if latest_inbox:
            p.status_terbaru = latest_inbox.status
            p.tanggal_wawancara_display = latest_inbox.tanggal_wawancara if latest_inbox.status == "wawancara" else None
        else:
            p.status_terbaru = p.status
            p.tanggal_wawancara_display = None

    show_wawancara_column = any(p.status_terbaru == "wawancara" for p in pendaftarans)
    inbox_unread_count = inbox_siswa.filter(is_read=False).count()

    return render(request, "siswa_app/tkj/home.html", {
        "title": "Dashboard Siswa TKJ",
        "user": siswa,
        "pendaftarans": pendaftarans,
        "show_wawancara_column": show_wawancara_column,
        "inbox_unread_count": inbox_unread_count,
    })
# Data Perusahaan TKJ ---
@login_required
def perusahaan_siswa_list_tkj(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tkj").order_by("nama_perusahaan")
    return render(request, "siswa_app/tkj/perusahaan/perusahaan.html", {
        "title": "Daftar Perusahaan TKJ",
        "perusahaan": perusahaan,
    })
# Detail Perusahaan TKJ ---
@login_required
def perusahaan_siswa_detail_tkj(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan, jurusan__iexact="tkj")
    return render(request, "siswa_app/tkj/perusahaan/perusahaan_detail.html", {
        "title": f"Detail {perusahaan.nama_perusahaan}",
        "perusahaan": perusahaan,
    })
# Form Pendaftaran PKL TKJ ---
@login_required
def pendaftaran_pkl_tkj(request):
    siswa = request.user

    if siswa.jurusan.lower() != "tkj":
        messages.error(request, "Anda bukan siswa jurusan TKJ.")
        return redirect('dashboard_siswa_tkj')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES)
        if form.is_valid():

            perusahaan_dipilih = form.cleaned_data['perusahaan']
            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa, perusahaan=perusahaan_dipilih
            ).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('pendaftaran_pkl_tkj')

            pkl = form.save(commit=False)
            pkl.siswa = siswa
            pkl.save()

            semua_guru = CustomUser.objects.filter(role="guru", jurusan__iexact="tkj")

            sudah_ada_global = InboxGuru.objects.filter(
                siswa=siswa, perusahaan=pkl.perusahaan, dikirim_oleh="siswa"
            ).exists()

            if not sudah_ada_global:
                for guru in semua_guru:
                    InboxGuru.objects.create(
                        guru=guru,
                        siswa=siswa,
                        perusahaan=pkl.perusahaan,
                        pesan=f"{siswa.first_name} mendaftar PKL di {pkl.perusahaan.nama_perusahaan}.",
                        status="menunggu",
                        tanggal_kirim=timezone.now(),
                        dikirim_oleh="siswa",
                        is_read=False,
                    )

            if not InboxSiswa.objects.filter(
                siswa=siswa, perusahaan=pkl.perusahaan,
                pesan__icontains="Pendaftaran PKL berhasil",
            ).exists():
                InboxSiswa.objects.create(
                    siswa=siswa,
                    perusahaan=pkl.perusahaan,
                    pesan="Pendaftaran PKL berhasil dikirim ke guru Pembimbing TKJ.",
                    status="menunggu",
                )

            messages.success(request, "✅ Pendaftaran berhasil! Guru TKJ menerima notifikasi.")
            return redirect('dashboard_siswa_tkj')

    else:
        form = PendaftaranPKLForm()
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tkj"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tkj/pendaftaran.html", {
        "title": "Pendaftaran PKL TKJ",
        "form": form,
        "siswa": siswa,
    })
# Edit Pendaftaran TKJ ---
@login_required
def edit_pendaftaran_tkj(request, pk):
    siswa = request.user
    pendaftaran = get_object_or_404(PendaftaranPKL, id=pk, siswa=siswa)

    if siswa.jurusan.lower() != "tkj":
        messages.error(request, "Anda bukan siswa jurusan TKJ.")
        return redirect('dashboard_siswa_tkj')

    if request.method == 'POST':
        form = PendaftaranPKLForm(request.POST, request.FILES, instance=pendaftaran)

        if form.is_valid():
            perusahaan_baru = form.cleaned_data['perusahaan']

            sudah_daftar = PendaftaranPKL.objects.filter(
                siswa=siswa, perusahaan=perusahaan_baru
            ).exclude(id=pendaftaran.id).exists()

            if sudah_daftar:
                messages.error(request, "Anda sudah pernah mendaftar ke perusahaan ini.")
                return redirect('edit_pendaftaran_tkj', pk=pendaftaran.id)

            form.save()
            messages.success(request, "✅ Pendaftaran berhasil diperbarui!")
            return redirect('dashboard_siswa_tkj')

    else:
        form = PendaftaranPKLForm(instance=pendaftaran)
        form.fields['perusahaan'].queryset = Perusahaan.objects.filter(
            jurusan__iexact="tkj"
        ).order_by('nama_perusahaan')

    return render(request, "siswa_app/tkj/edit.html", {
        "title": "Edit Pendaftaran PKL TKJ",
        "form": form,
        "siswa": siswa,
        "pendaftaran": pendaftaran,
    })
# Hapus TKJ ---
@login_required
def pendaftaran_pkl_delete_tkj(request, pk):
    pendaftaran = get_object_or_404(PendaftaranPKL, pk=pk)
    nama = pendaftaran.siswa.first_name

    pendaftaran.delete()
    messages.success(request, f"🗑️ Pendaftaran PKL milik {nama} berhasil dihapus.")
    return redirect("dashboard_siswa_tkj")
# Inbox TKJ ---
@login_required
def inbox_siswa_tkj(request):
    user = request.user

    inbox_siswa = InboxSiswa.objects.filter(siswa=user).order_by("-tanggal_kirim")
    inbox_guru = InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru").order_by("-tanggal_kirim")

    combined_inbox = sorted(
        list(inbox_siswa) + list(inbox_guru),
        key=lambda x: x.tanggal_kirim,
        reverse=True
    )

    notif_count = (
        InboxSiswa.objects.filter(siswa=user, is_read=False).count()
        + InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).count()
    )

    InboxSiswa.objects.filter(siswa=user, is_read=False).update(is_read=True)
    InboxGuru.objects.filter(siswa=user, dikirim_oleh="guru", is_read=False).update(is_read=True)

    return render(request, "siswa_app/tkj/inbox.html", {
        "title": "Inbox Siswa TKJ",
        "inbox": combined_inbox,
        "notif_count": notif_count,
        "user": user
    })
