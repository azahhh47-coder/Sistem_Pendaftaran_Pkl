from django.contrib import messages  
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404 
from user_app.models import CustomUser  #Ambil dari model user_app
from .models import Perusahaan # Ambil dari model admin_app
from siswa_app.models import PendaftaranPKL #Ambil dari model siswa_app
from django.http import FileResponse, Http404

User = get_user_model()  # CustomUser

# Khusus Halaman User  ============================================================================
# Halaman Utama Admin ----
@login_required
def home(request):
    return render(request, "admin_app/home.html")


# Dashboard User untuk akun admin,guru dan siswa ----------------
@login_required
def dashboard_user(request):
    users = User.objects.all()
    return render(request, "admin_app/user/dashboard_user.html", {
        "users": users,
        "title": "Dashboard User"
    })

# User Admin ------
@login_required
def user_admin(request):
    users = User.objects.filter(role="admin").order_by('username')
    return render(request, "admin_app/user/user_admin/user_admin.html", {
        "users": users,
        "title": "Daftar Admin"
    })
# Create Admin
@login_required
def admin_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return redirect("admin_create")

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username sudah digunakan.")
            return redirect("admin_create")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="admin",
            is_staff=True,
            is_superuser=True
        )

        messages.success(request, f"Admin {username} berhasil ditambahkan.")
        return redirect("user_admin")

    return render(request, "admin_app/user/user_admin/admin_create.html", {
        "title": "Tambah Admin"
    })
# Edit Admin
@login_required
def admin_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="admin")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user.username = username
        user.email = email

        if password:
            user.set_password(password)
            user.save()
            if request.user.id == user.id:
                update_session_auth_hash(request, user)
        else:
            user.save()

        messages.success(request, "Data admin berhasil diperbarui.")
        return redirect("user_admin")

    return render(request, "admin_app/user/user_admin/admin_edit.html", {
        "user": user,
        "title": "Edit Admin"
    })
# Delete Admin
@login_required
def admin_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="admin")
    user.delete()
    messages.success(request, f"Admin {user.username} berhasil dihapus.")
    return redirect("user_admin")

# Halaman Utama User Guru  ----------------
@login_required
def user_guru(request):
    users = User.objects.filter(role="guru")
    return render(request, "admin_app/user/user_guru/user_guru.html", {
        "users": users,
        "title": "Daftar Guru"
    })

# Halaman User Guru Agro ---
@login_required
def guru_agro(request):
    users = User.objects.filter(role="guru", jurusan__iexact="agro")
    return render(request, "admin_app/user/user_guru/agro/tabel_agro.html", {
        "users": users,
        "title": "Daftar Guru Agro"
    })
# Create User Guru Agro
@login_required
def guru_agro_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/agro/guru_agro_create.html", {
                "title": "Tambah Guru Agro",
                "post_data": post_data
            })

        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/agro/guru_agro_create.html", {
                "title": "Tambah Guru Agro",
                "post_data": post_data
            })

        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/agro/guru_agro_create.html", {
                "title": "Tambah Guru Agro",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="agro",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru Agro baru berhasil ditambahkan.")
        return redirect("tabel_agro")

    return render(request, "admin_app/user/user_guru/agro/guru_agro_create.html", {
        "title": "Tambah Guru Agro",
        "post_data": post_data
    })
# Edit User Guru Agro
@login_required
def guru_agro_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="agro")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_agro_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru Agro berhasil diperbarui.")
        return redirect("tabel_agro")

    return render(request, "admin_app/user/user_guru/agro/guru_agro_edit.html", {
        "user": user,
        "title": "Edit Guru Agro"
    })
# Delete User Guru Agro 
@login_required
def guru_agro_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="agro")
    user.delete()
    messages.success(request, "🗑️ Guru Agro berhasil dihapus.")
    return redirect("tabel_agro")

# Halaman User Guru PM  ---
@login_required
def guru_pm(request):
    users = User.objects.filter(role="guru", jurusan__iexact="pm")
    return render(request, "admin_app/user/user_guru/pm/tabel_pm.html", {
        "users": users,
        "title": "Daftar Guru Pemasaran"
    })
# Create User Guru PM
@login_required
def guru_pm_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/pm/guru_pm_create.html", {
                "title": "Tambah Guru Pemasaran",
                "post_data": post_data
            })

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/pm/guru_pm_create.html", {
                "title": "Tambah Guru Pemasaran",
                "post_data": post_data
            })

        # Cek duplikat
        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/pm/guru_pm_create.html", {
                "title": "Tambah Guru Pemasaran",
                "post_data": post_data
            })

        # Simpan data guru baru
        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="pm",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru Pemasaran baru berhasil ditambahkan.")
        return redirect("tabel_pm")

    return render(request, "admin_app/user/user_guru/pm/guru_pm_create.html", {
        "title": "Tambah Guru Pemasaran",
        "post_data": post_data
    })
# Edit User Guru PM
@login_required
def guru_pm_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="pm")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_pm_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru Pemasaran berhasil diperbarui.")
        return redirect("tabel_pm")

    return render(request, "admin_app/user/user_guru/pm/guru_pm_edit.html", {
        "user": user,
        "title": "Edit Guru Pemasaran"
    })
# Hapus  User Guru PM
@login_required
def guru_pm_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="pm")
    user.delete()
    messages.success(request, "🗑️ Guru Pemasaran berhasil dihapus.")
    return redirect("tabel_pm")

# Halaman User Guru RPL ---
@login_required
def guru_rpl(request):
    users = User.objects.filter(role="guru", jurusan__iexact="rpl")
    return render(request, "admin_app/user/user_guru/rpl/tabel_rpl.html", {
        "users": users,
        "title": "Daftar Guru RPL"
    })
# Create User Guru RPL
@login_required
def guru_rpl_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/rpl/guru_rpl_create.html", {
                "title": "Tambah Guru RPL",
                "post_data": post_data
            })

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/rpl/guru_rpl_create.html", {
                "title": "Tambah Guru RPL",
                "post_data": post_data
            })

        # Cek duplikat
        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/rpl/guru_rpl_create.html", {
                "title": "Tambah Guru RPL",
                "post_data": post_data
            })

        # Simpan data guru baru
        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="rpl",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru RPL baru berhasil ditambahkan.")
        return redirect("tabel_rpl")

    return render(request, "admin_app/user/user_guru/rpl/guru_rpl_create.html", {
        "title": "Tambah Guru RPL",
        "post_data": post_data
    })
# Edit User Guru RPL
@login_required
def guru_rpl_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="rpl")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_rpl_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru RPL berhasil diperbarui.")
        return redirect("tabel_rpl")

    return render(request, "admin_app/user/user_guru/rpl/guru_rpl_edit.html", {
        "user": user,
        "title": "Edit Guru RPL"
    })
# Hapus User Guru RPL
@login_required
def guru_rpl_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="rpl")
    user.delete()
    messages.success(request, "🗑️ Guru RPL berhasil dihapus.")
    return redirect("tabel_rpl")

# Halaman User Guru TEI ---
@login_required
def guru_tei(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tei")
    return render(request, "admin_app/user/user_guru/tei/tabel_tei.html", {
        "users": users,
        "title": "Daftar Guru TEI"
    })
# Create User Guru TEI
@login_required
def guru_tei_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/tei/guru_tei_create.html", {
                "title": "Tambah Guru TEI",
                "post_data": post_data
            })

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/tei/guru_tei_create.html", {
                "title": "Tambah Guru TEI",
                "post_data": post_data
            })

        # Cek duplikat
        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/tei/guru_tei_create.html", {
                "title": "Tambah Guru TEI",
                "post_data": post_data
            })

        # Simpan data guru baru
        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="tei",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru TEI baru berhasil ditambahkan.")
        return redirect("tabel_tei")

    return render(request, "admin_app/user/user_guru/tei/guru_tei_create.html", {
        "title": "Tambah Guru TEI",
        "post_data": post_data
    })
# Edit User Guru TEI
@login_required
def guru_tei_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tei")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_tei_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru TEI berhasil diperbarui.")
        return redirect("tabel_tei")

    return render(request, "admin_app/user/user_guru/tei/guru_tei_edit.html", {
        "user": user,
        "title": "Edit Guru TEI"
    })
# Hapus User Guru TEI
@login_required
def guru_tei_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tei")
    user.delete()
    messages.success(request, "🗑️ Guru TEI berhasil dihapus.")
    return redirect("tabel_tei")

# Halaman User Guru TKI ---
@login_required
def guru_tki(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tki")
    return render(request, "admin_app/user/user_guru/tki/tabel_tki.html", {
        "users": users,
        "title": "Daftar Guru TKI"
    })
# Create User Guru TKI
@login_required
def guru_tki_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/tki/guru_tki_create.html", {
                "title": "Tambah Guru TKI",
                "post_data": post_data
            })

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/tki/guru_tki_create.html", {
                "title": "Tambah Guru TKI",
                "post_data": post_data
            })

        # Cek duplikat
        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/tki/guru_tki_create.html", {
                "title": "Tambah Guru TKI",
                "post_data": post_data
            })

        # Simpan data guru baru
        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="tki",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru TKI baru berhasil ditambahkan.")
        return redirect("tabel_tki")

    return render(request, "admin_app/user/user_guru/tki/guru_tki_create.html", {
        "title": "Tambah Guru TKI",
        "post_data": post_data
    })
# Edit User Guru TKI
@login_required
def guru_tki_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tki")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_tki_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru TKI berhasil diperbarui.")
        return redirect("tabel_tki")

    return render(request, "admin_app/user/user_guru/tki/guru_tki_edit.html", {
        "user": user,
        "title": "Edit Guru TKI"
    })
# Hapus User Guru TKI
@login_required
def guru_tki_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tki")
    user.delete()
    messages.success(request, "🗑️ Guru TKI berhasil dihapus.")
    return redirect("tabel_tki")

# Halaman User Guru TKJ ---
@login_required
def guru_tkj(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tkj")
    return render(request, "admin_app/user/user_guru/tkj/tabel_tkj.html", {
        "users": users,
        "title": "Daftar Guru TKJ"
    })
# Create User Guru TKJ
@login_required
def guru_tkj_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password
        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_guru/tkj/guru_tkj_create.html", {
                "title": "Tambah Guru TKJ",
                "post_data": post_data
            })

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return render(request, "admin_app/user/user_guru/tkj/guru_tkj_create.html", {
                "title": "Tambah Guru TKJ",
                "post_data": post_data
            })

        # Cek duplikat
        if User.objects.filter(username=nip).exists():
            messages.error(request, "❌ NIP sudah digunakan.")
            return render(request, "admin_app/user/user_guru/tkj/guru_tkj_create.html", {
                "title": "Tambah Guru TKJ",
                "post_data": post_data
            })

        # Simpan data guru baru
        user = User.objects.create_user(
            username=nip,
            email=email,
            password=password,
            role="guru",
            jurusan="tkj",
            nip=nip,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Guru TKJ baru berhasil ditambahkan.")
        return redirect("tabel_tkj")

    return render(request, "admin_app/user/user_guru/tkj/guru_tkj_create.html", {
        "title": "Tambah Guru TKJ",
        "post_data": post_data
    })
# Edit User Guru TKJ
@login_required
def guru_tkj_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tkj")

    if request.method == "POST":
        nip = request.POST.get("nip")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validasi NIP
        if not nip or not nip.isdigit() or len(nip) != 16:
            messages.error(request, "❌ NIP wajib diisi 16 digit angka.")
            return redirect("guru_tkj_edit", user_id=user_id)

        user.nip = nip
        user.username = nip
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Guru TKJ berhasil diperbarui.")
        return redirect("tabel_tkj")

    return render(request, "admin_app/user/user_guru/tkj/guru_tkj_edit.html", {
        "user": user,
        "title": "Edit Guru TKJ"
    })
# Hapus User Guru TKJ
@login_required
def guru_tkj_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="guru", jurusan__iexact="tkj")
    user.delete()
    messages.success(request, "🗑️ Guru TKJ berhasil dihapus.")
    return redirect("tabel_tkj")


# Halaman User Siswa ----------------
@login_required
def user_siswa(request):
    users = User.objects.filter(role="siswa")
    return render(request, "admin_app/user/user_siswa/user_siswa.html", {
        "users": users,
        "title": "Daftar Siswa"
    })

# Halaman User Siswa Agro ---
@login_required
def siswa_agro(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="agro")
    return render(request, "admin_app/user/user_siswa/agro/tabel_siswa_agro.html", {
        "users": users,
        "title": "Daftar Siswa Agro"
    })
# Create User Siswa Agro
@login_required
def siswa_agro_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/agro/siswa_agro_create.html", {
                "title": "Tambah Siswa Agro",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/agro/siswa_agro_create.html", {
                "title": "Tambah Siswa Agro",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/agro/siswa_agro_create.html", {
                "title": "Tambah Siswa Agro",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="agro",  # wajib isi jurusan
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa Agro baru berhasil ditambahkan.")
        return redirect("tabel_siswa_agro")  # redirect ke siswa, bukan guru

    return render(request, "admin_app/user/user_siswa/agro/siswa_agro_create.html", {
        "title": "Tambah Siswa Agro",
        "post_data": post_data
    })
# Edit User Siswa Agro
@login_required
def siswa_agro_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="agro")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "agro")  # ambil jurusan dari form, default agro

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_agro_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan  # wajib disimpan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa Agro berhasil diperbarui.")
        return redirect("tabel_siswa_agro")  # redirect ke siswa

    return render(request, "admin_app/user/user_siswa/agro/siswa_agro_edit.html", {
        "user": user,
        "title": "Edit Siswa Agro"
    })
# Delete User Siswa Agro
@login_required
def siswa_agro_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="agro")
    user.delete()
    messages.success(request, "🗑️ Siswa Agro berhasil dihapus.")
    return redirect("tabel_siswa_agro")

# Halaman User Siswa PM ---
@login_required
def siswa_pm(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="pm")
    return render(request, "admin_app/user/user_siswa/pm/tabel_siswa_pm.html", {
        "users": users,
        "title": "Daftar Siswa PM"
    })
# Create User Siswa PM
@login_required
def siswa_pm_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/pm/siswa_pm_create.html", {
                "title": "Tambah Siswa PM",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/pm/siswa_pm_create.html", {
                "title": "Tambah Siswa PM",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/pm/siswa_pm_create.html", {
                "title": "Tambah Siswa PM",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="pm",  # jurusan PM
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa PM baru berhasil ditambahkan.")
        return redirect("tabel_siswa_pm")  # redirect ke tabel PM

    return render(request, "admin_app/user/user_siswa/pm/siswa_pm_create.html", {
        "title": "Tambah Siswa PM",
        "post_data": post_data
    })
# Edit User Siswa PM
@login_required
def siswa_pm_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="pm")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "pm")  # default PM

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_pm_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa PM berhasil diperbarui.")
        return redirect("tabel_siswa_pm")

    return render(request, "admin_app/user/user_siswa/pm/siswa_pm_edit.html", {
        "user": user,
        "title": "Edit Siswa PM"
    })
# Delete User Siswa PM
@login_required
def siswa_pm_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="pm")
    user.delete()
    messages.success(request, "🗑️ Siswa PM berhasil dihapus.")
    return redirect("tabel_siswa_pm")

# Halaman User Siswa RPL ---
@login_required
def siswa_rpl(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="rpl")
    return render(request, "admin_app/user/user_siswa/rpl/tabel_siswa_rpl.html", {
        "users": users,
        "title": "Daftar Siswa RPL"
    })
# Create User Siswa RPL
@login_required
def siswa_rpl_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/rpl/siswa_rpl_create.html", {
                "title": "Tambah Siswa RPL",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/rpl/siswa_rpl_create.html", {
                "title": "Tambah Siswa RPL",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/rpl/siswa_rpl_create.html", {
                "title": "Tambah Siswa RPL",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="rpl",
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa RPL baru berhasil ditambahkan.")
        return redirect("tabel_siswa_rpl")

    return render(request, "admin_app/user/user_siswa/rpl/siswa_rpl_create.html", {
        "title": "Tambah Siswa RPL",
        "post_data": post_data
    })
# Edit User Siswa RPL
@login_required
def siswa_rpl_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="rpl")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "rpl")

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_rpl_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa RPL berhasil diperbarui.")
        return redirect("tabel_siswa_rpl")

    return render(request, "admin_app/user/user_siswa/rpl/siswa_rpl_edit.html", {
        "user": user,
        "title": "Edit Siswa RPL"
    })
# Delete User Siswa RPL
@login_required
def siswa_rpl_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="rpl")
    user.delete()
    messages.success(request, "🗑️ Siswa RPL berhasil dihapus.")
    return redirect("tabel_siswa_rpl")

# Halaman User Siswa TEI ---
@login_required
def siswa_tei(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tei")
    return render(request, "admin_app/user/user_siswa/tei/tabel_siswa_tei.html", {
        "users": users,
        "title": "Daftar Siswa TEI"
    })
# Create User Siswa TEI
@login_required
def siswa_tei_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/tei/siswa_tei_create.html", {
                "title": "Tambah Siswa TEI",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/tei/siswa_tei_create.html", {
                "title": "Tambah Siswa TEI",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/tei/siswa_tei_create.html", {
                "title": "Tambah Siswa TEI",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="tei",
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa TEI baru berhasil ditambahkan.")
        return redirect("tabel_siswa_tei")

    return render(request, "admin_app/user/user_siswa/tei/siswa_tei_create.html", {
        "title": "Tambah Siswa TEI",
        "post_data": post_data
    })
# Edit User Siswa TEI
@login_required
def siswa_tei_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tei")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "tei")

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_tei_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa TEI berhasil diperbarui.")
        return redirect("tabel_siswa_tei")

    return render(request, "admin_app/user/user_siswa/tei/siswa_tei_edit.html", {
        "user": user,
        "title": "Edit Siswa TEI"
    })
# Delete User Siswa TEI
@login_required
def siswa_tei_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tei")
    user.delete()
    messages.success(request, "🗑️ Siswa TEI berhasil dihapus.")
    return redirect("tabel_siswa_tei")

# Halaman User Siswa TKI ---
@login_required
def siswa_tki(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tki")
    return render(request, "admin_app/user/user_siswa/tki/tabel_siswa_tki.html", {
        "users": users,
        "title": "Daftar Siswa TKI"
    })
# Create User Siswa TKI
@login_required
def siswa_tki_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/tki/siswa_tki_create.html", {
                "title": "Tambah Siswa TKI",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/tki/siswa_tki_create.html", {
                "title": "Tambah Siswa TKI",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/tki/siswa_tki_create.html", {
                "title": "Tambah Siswa TKI",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="tki",
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa TKI baru berhasil ditambahkan.")
        return redirect("tabel_siswa_tki")

    return render(request, "admin_app/user/user_siswa/tki/siswa_tki_create.html", {
        "title": "Tambah Siswa TKI",
        "post_data": post_data
    })
# Edit User Siswa TKI
@login_required
def siswa_tki_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tki")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "tki")

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_tki_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa TKI berhasil diperbarui.")
        return redirect("tabel_siswa_tki")

    return render(request, "admin_app/user/user_siswa/tki/siswa_tki_edit.html", {
        "user": user,
        "title": "Edit Siswa TKI"
    })
# Delete User Siswa TKI
@login_required
def siswa_tki_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tki")
    user.delete()
    messages.success(request, "🗑️ Siswa TKI berhasil dihapus.")
    return redirect("tabel_siswa_tki")

# Halaman User Siswa TKJ ---
@login_required
def siswa_tkj(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tkj")
    return render(request, "admin_app/user/user_siswa/tkj/tabel_siswa_tkj.html", {
        "users": users,
        "title": "Daftar Siswa TKJ"
    })
# Create User Siswa TKJ
@login_required
def siswa_tkj_create(request):
    post_data = request.POST if request.method == "POST" else None

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Password dan konfirmasi password tidak sama.")
            return render(request, "admin_app/user/user_siswa/tkj/siswa_tkj_create.html", {
                "title": "Tambah Siswa TKJ",
                "post_data": post_data
            })

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return render(request, "admin_app/user/user_siswa/tkj/siswa_tkj_create.html", {
                "title": "Tambah Siswa TKJ",
                "post_data": post_data
            })

        if User.objects.filter(username=nisn).exists():
            messages.error(request, "❌ NISN sudah digunakan.")
            return render(request, "admin_app/user/user_siswa/tkj/siswa_tkj_create.html", {
                "title": "Tambah Siswa TKJ",
                "post_data": post_data
            })

        user = User.objects.create_user(
            username=nisn,
            email=email,
            password=password,
            role="siswa",
            jurusan="tkj",
            nisn=nisn,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "✅ Siswa TKJ baru berhasil ditambahkan.")
        return redirect("tabel_siswa_tkj")

    return render(request, "admin_app/user/user_siswa/tkj/siswa_tkj_create.html", {
        "title": "Tambah Siswa TKJ",
        "post_data": post_data
    })
# Edit User Siswa TKJ
@login_required
def siswa_tkj_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tkj")

    if request.method == "POST":
        nisn = request.POST.get("nisn")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        jurusan = request.POST.get("jurusan", "tkj")

        if not nisn or not nisn.isdigit() or len(nisn) != 10:
            messages.error(request, "❌ NISN wajib diisi 10 digit angka.")
            return redirect("siswa_tkj_edit", user_id=user_id)

        user.nisn = nisn
        user.username = nisn
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.jurusan = jurusan

        if password:
            user.set_password(password)

        user.save()
        if request.user.id == user.id and password:
            update_session_auth_hash(request, user)

        messages.success(request, "✅ Data Siswa TKJ berhasil diperbarui.")
        return redirect("tabel_siswa_tkj")

    return render(request, "admin_app/user/user_siswa/tkj/siswa_tkj_edit.html", {
        "user": user,
        "title": "Edit Siswa TKJ"
    })
# Delete User Siswa TKJ
@login_required
def siswa_tkj_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id, role="siswa", jurusan__iexact="tkj")
    user.delete()
    messages.success(request, "🗑️ Siswa TKJ berhasil dihapus.")
    return redirect("tabel_siswa_tkj")


# Khusus Halaman Data Guru  ============================================================================
@login_required 
def dashboard_guru(request):
    users = User.objects.filter(groups__name="guru")
    return render(request, "admin_app/data_guru/dashboard_guru.html", { 
        "title": "Dashboard Guru",
        "users": users
    })

# Data Guru Agro ---
@login_required
def data_guru_agro(request):
    users = User.objects.filter(role="guru", jurusan__iexact="agro").order_by("first_name")
    return render(request, "admin_app/data_guru/agro/data_guru_agro.html", {
        "title": "Data Guru Agro",
        "users": users
    })
# Edit Foto Guru Agro  (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_agro(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")

    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")

        # Validasi form
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_agro", nip=nip)

        # Simpan foto baru
        guru.foto_guru = foto_guru
        guru.save()

        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_agro")

    # Tampilkan form edit foto
    return render(request, "admin_app/data_guru/agro/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Data Guru PM ---
@login_required
def data_guru_pm(request):
    users = User.objects.filter(role="guru", jurusan__iexact="pm").order_by("first_name")
    return render(request, "admin_app/data_guru/pm/data_guru_pm.html", {
        "title": "Data Guru PM",
        "users": users
    })
# Edit Foto Guru PM  (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_pm(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")
    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_pm", nip=nip)
        guru.foto_guru = foto_guru
        guru.save()
        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_pm")
    return render(request, "admin_app/data_guru/pm/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Data Guru RPL ---
@login_required
def data_guru_rpl(request):
    users = User.objects.filter(role="guru", jurusan__iexact="rpl").order_by("first_name")
    return render(request, "admin_app/data_guru/rpl/data_guru_rpl.html", {
        "title": "Data Guru RPL",
        "users": users
    })
# Edit Foto Guru RPL  (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_rpl(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")
    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_rpl", nip=nip)
        guru.foto_guru = foto_guru
        guru.save()
        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_rpl")
    return render(request, "admin_app/data_guru/rpl/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Data Guru TEI ---
@login_required
def data_guru_tei(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tei").order_by("first_name")
    return render(request, "admin_app/data_guru/tei/data_guru_tei.html", {
        "title": "Data Guru TEI",
        "users": users
    })
# Edit Foto Guru TEI  (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_tei(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")
    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_tei", nip=nip)
        guru.foto_guru = foto_guru
        guru.save()
        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_tei")
    return render(request, "admin_app/data_guru/tei/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Data Guru TKI ---
@login_required
def data_guru_tki(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tki").order_by("first_name")
    return render(request, "admin_app/data_guru/tki/data_guru_tki.html", {
        "title": "Data Guru TKI",
        "users": users
    })
# Edit Foto Guru TKI (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_tki(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")
    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_tki", nip=nip)
        guru.foto_guru = foto_guru
        guru.save()
        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_tki")
    return render(request, "admin_app/data_guru/tki/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Data Guru TKJ ----
@login_required
def data_guru_tkj(request):
    users = User.objects.filter(role="guru", jurusan__iexact="tkj").order_by("first_name")
    return render(request, "admin_app/data_guru/tkj/data_guru_tkj.html", {
        "title": "Data Guru TKJ",
        "users": users
    })
# Edit Foto Guru TKJ (Agar bisa ganti foto guru)
@login_required
def edit_foto_guru_tkj(request, nip):
    guru = get_object_or_404(User, nip=nip, role="guru")
    if request.method == "POST":
        foto_guru = request.FILES.get("foto_guru")
        if not foto_guru:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_guru_tkj", nip=nip)
        guru.foto_guru = foto_guru
        guru.save()
        messages.success(request, f"✅ Foto {guru.first_name} {guru.last_name} berhasil diperbarui.")
        return redirect("data_guru_tkj")
    return render(request, "admin_app/data_guru/tkj/edit_foto.html", {
        "title": f"Edit Foto - {guru.first_name} {guru.last_name}",
        "guru": guru
    })

# Khusus Halaman Data Siswa  ============================================================================
@login_required 
def dashboard_siswa(request):
    users = User.objects.filter(groups__name="siswa")
    return render(request, "admin_app/data_siswa/dashboard_siswa.html", { 
        "title": "Dashboard Siswa",
        "users": users
    })

# Data Siswa Agro ---
@login_required
def data_siswa_agro(request):
    # Ambil semua siswa jurusan Agro, urut berdasarkan nama depan (A-Z)
    users = User.objects.filter(role="siswa", jurusan__iexact="agro").order_by("first_name")

    # Ambil semua pendaftaran siswa (gunakan nisn karena ForeignKey ke to_field="nisn")
    pendaftar_dict = {
        p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")
    }

    # Gabungkan data siswa + status pendaftaran
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })

    return render(request, "admin_app/data_siswa/agro/data_siswa_agro.html", {
        "title": "Data Siswa Agro",
        "siswa_data": siswa_data,
    })
# Detail Siswa Agro
@login_required
def detail_pendaftaran_agro(request, nisn):
    # Ambil data siswa & pendaftarannya
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="agro")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)

    return render(request, "admin_app/data_siswa/agro/detail_pendaftaran_agro.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV Agro
@login_required
def download_cv_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)

    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")

    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename=\"{siswa.first_name}_{siswa.last_name}_CV.pdf\"'
    return response
# Edit Data Siswa Agro
@login_required
def edit_foto_siswa_agro(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")

    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")

        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_agro", nisn=nisn)

        siswa.foto_siswa = foto_siswa
        siswa.save()

        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_agro")

    return render(request, "admin_app/data_siswa/agro/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })

# Data Siswa PM ---
@login_required
def data_siswa_pm(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="pm").order_by("first_name")
    pendaftar_dict = {p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")}
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })
    return render(request, "admin_app/data_siswa/pm/data_siswa_pm.html", {
        "title": "Data Siswa PM",
        "siswa_data": siswa_data,
    })
# Detail Siswa PM
@login_required
def detail_pendaftaran_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="pm")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    return render(request, "admin_app/data_siswa/pm/detail_pendaftaran_pm.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV pm
@login_required
def download_cv_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")
    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{siswa.first_name}_{siswa.last_name}_CV.pdf"'
    return response
#Edit Data Siswa PM
@login_required
def edit_foto_siswa_pm(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")
        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_pm", nisn=nisn)
        siswa.foto_siswa = foto_siswa
        siswa.save()
        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_pm")
    return render(request, "admin_app/data_siswa/pm/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })

# Data Siswa RPL ---
@login_required
def data_siswa_rpl(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="rpl").order_by("first_name")
    pendaftar_dict = {p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")}
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })
    return render(request, "admin_app/data_siswa/rpl/data_siswa_rpl.html", {
        "title": "Data Siswa RPL",
        "siswa_data": siswa_data,
    })
# Detail Siswa RPL
@login_required
def detail_pendaftaran_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="rpl")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    return render(request, "admin_app/data_siswa/rpl/detail_pendaftaran_rpl.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV RPL
@login_required
def download_cv_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")
    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{siswa.first_name}_{siswa.last_name}_CV.pdf"'
    return response
#Edit Data Siswa RPL
@login_required
def edit_foto_siswa_rpl(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")
        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_rpl", nisn=nisn)
        siswa.foto_siswa = foto_siswa
        siswa.save()
        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_rpl")
    return render(request, "admin_app/data_siswa/rpl/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })

# Data Siswa TEI ---
@login_required
def data_siswa_tei(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tei").order_by("first_name")
    pendaftar_dict = {p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")}
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })
    return render(request, "admin_app/data_siswa/tei/data_siswa_tei.html", {
        "title": "Data Siswa TEI",
        "siswa_data": siswa_data,
    })
# Detail Siswa Tei
@login_required
def detail_pendaftaran_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tei")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    return render(request, "admin_app/data_siswa/tei/detail_pendaftaran_tei.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV Tei
@login_required
def download_cv_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")
    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{siswa.first_name}_{siswa.last_name}_CV.pdf"'
    return response
#Edit Data Siswa Tei
@login_required
def edit_foto_siswa_tei(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")
        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_tei", nisn=nisn)
        siswa.foto_siswa = foto_siswa
        siswa.save()
        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_tei")
    return render(request, "admin_app/data_siswa/tei/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })

# Data Siswa TKI ---
@login_required
def data_siswa_tki(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tki").order_by("first_name")
    pendaftar_dict = {p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")}
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })
    return render(request, "admin_app/data_siswa/tki/data_siswa_tki.html", {
        "title": "Data Siswa TKI",
        "siswa_data": siswa_data,
    })
# Detail Siswa Tki
@login_required
def detail_pendaftaran_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tki")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    return render(request, "admin_app/data_siswa/tki/detail_pendaftaran_tki.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV Tki
@login_required
def download_cv_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")
    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{siswa.first_name}_{siswa.last_name}_CV.pdf"'
    return response
#Edit Data Siswa Tki
@login_required
def edit_foto_siswa_tki(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")
        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_tki", nisn=nisn)
        siswa.foto_siswa = foto_siswa
        siswa.save()
        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_tki")
    return render(request, "admin_app/data_siswa/tki/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })

# Data Siswa TKJ ---
@login_required
def data_siswa_tkj(request):
    users = User.objects.filter(role="siswa", jurusan__iexact="tkj").order_by("first_name")
    pendaftar_dict = {p.siswa.nisn: p for p in PendaftaranPKL.objects.select_related("siswa", "perusahaan")}
    siswa_data = []
    for siswa in users:
        pendaftaran = pendaftar_dict.get(siswa.nisn)
        siswa_data.append({
            "obj": siswa,
            "sudah_daftar": bool(pendaftaran),
            "pendaftaran": pendaftaran,
        })
    return render(request, "admin_app/data_siswa/tkj/data_siswa_tkj.html", {
        "title": "Data Siswa TKJ",
        "siswa_data": siswa_data,
    })
# Detail Siswa Tkj
@login_required
def detail_pendaftaran_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa", jurusan__iexact="tkj")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    return render(request, "admin_app/data_siswa/tkj/detail_pendaftaran_tkj.html", {
        "title": f"Detail Pendaftaran - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa,
        "pendaftaran": pendaftaran
    })
# Download CV Tkj
@login_required
def download_cv_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    pendaftaran = get_object_or_404(PendaftaranPKL, siswa__nisn=nisn)
    if not pendaftaran.cv:
        raise Http404("CV tidak ditemukan.")
    response = FileResponse(open(pendaftaran.cv.path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{siswa.first_name}_{siswa.last_name}_CV.pdf"'
    return response
#Edit Data Siswa Tkj
@login_required
def edit_foto_siswa_tkj(request, nisn):
    siswa = get_object_or_404(User, nisn=nisn, role="siswa")
    if request.method == "POST":
        foto_siswa = request.FILES.get("foto_siswa")
        if not foto_siswa:
            messages.error(request, "❌ Harap pilih foto terlebih dahulu.")
            return redirect("edit_foto_siswa_tkj", nisn=nisn)
        siswa.foto_siswa = foto_siswa
        siswa.save()
        messages.success(request, f"✅ Foto {siswa.first_name} {siswa.last_name} berhasil diperbarui.")
        return redirect("data_siswa_tkj")
    return render(request, "admin_app/data_siswa/tkj/edit_foto.html", {
        "title": f"Edit Foto - {siswa.first_name} {siswa.last_name}",
        "siswa": siswa
    })


# Khusus Halaman Data Perusahaan  ============================================================================
@login_required
def data_perusahaan(request):
    users = User.objects.filter(role="perusahaan")
    return render(request, "admin_app/data_perusahaan/home_perusahaan.html", {
        "users": users,
        "title": "Data Perusahaan"
    })

# Data Perusahaan Agro ---
@login_required
def perusahaan_agro(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="agro").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/agro/perusahaan_agro.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan Agro"
    })
# Create Perusahaan Agro
@login_required
def perusahaan_agro_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "agro")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_agro_create")

        # 💡 bikin nama unik gabungan jurusan + nama perusahaan
        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_agro_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_agro")

    return render(request, "admin_app/data_perusahaan/agro/create.html", {
        "title": "Tambah Perusahaan Agro"
    })
# Delete Perusahaan Agro
@login_required
def perusahaan_agro_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan  # simpan dulu sebelum dihapus
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_agro")
# Detail Perusahaan Agro
@login_required
def perusahaan_agro_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)

    if request.method == "POST":
        # Tidak mengubah data, hanya buat rapi dan seragam sama create/edit
        messages.info(request, f"ℹ️ Anda sedang melihat detail '{perusahaan.nama_perusahaan}'.")
        return redirect("perusahaan_agro_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/agro/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan Agro
@login_required
def perusahaan_agro_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "agro")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_agro_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_agro_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/agro/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })

# Data Perusahaan PM ---
@login_required
def perusahaan_pm(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="pm").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/pm/perusahaan_pm.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan PM"
    })
# Create Perusahaan PM
@login_required
def perusahaan_pm_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "pm")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_pm_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_pm_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_pm")

    return render(request, "admin_app/data_perusahaan/pm/create.html", {
        "title": "Tambah Perusahaan PM"
    })
# Delete Perusahaan PM
@login_required
def perusahaan_pm_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_pm")
# Detail Perusahaan PM
@login_required
def perusahaan_pm_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "admin_app/data_perusahaan/pm/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan PM
@login_required
def perusahaan_pm_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "pm")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_pm_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_pm_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/pm/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })

# Perusahaan Rpl ---
@login_required
def perusahaan_rpl(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="rpl").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/rpl/perusahaan_rpl.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan RPL"
    })
# Create Perusahaan Rpl
@login_required
def perusahaan_rpl_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "rpl")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_rpl_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_rpl_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_rpl")

    return render(request, "admin_app/data_perusahaan/rpl/create.html", {
        "title": "Tambah Perusahaan RPL"
    })
# Delete Perusahaan Rpl
@login_required
def perusahaan_rpl_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_rpl")
# Detail Perusahaan Rpl
@login_required
def perusahaan_rpl_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "admin_app/data_perusahaan/rpl/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan Rpl
@login_required
def perusahaan_rpl_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "rpl")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_rpl_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_rpl_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/rpl/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })

# Data Perusahaan TEI ---
@login_required
def perusahaan_tei(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tei").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/tei/perusahaan_tei.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan TEI"
    })
# Create Perusahaan TEI
@login_required
def perusahaan_tei_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tei")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tei_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tei_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tei")

    return render(request, "admin_app/data_perusahaan/tei/create.html", {
        "title": "Tambah Perusahaan TEI"
    })
# Delete Perusahaan TEI
@login_required
def perusahaan_tei_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tei")
# Detail Perusahaan TEI
@login_required
def perusahaan_tei_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "admin_app/data_perusahaan/tei/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan TEI
@login_required
def perusahaan_tei_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tei")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tei_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tei_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/tei/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })

# Data Perusahaan TKI ----
@login_required
def perusahaan_tki(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tki").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/tki/perusahaan_tki.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan TKI"
    })
# Create Perusahaan TKI
@login_required
def perusahaan_tki_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tki")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tki_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tki_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tki")

    return render(request, "admin_app/data_perusahaan/tki/create.html", {
        "title": "Tambah Perusahaan TKI"
    })
# Delete Perusahaan TKI
@login_required
def perusahaan_tki_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tki")
# Detail Perusahaan TKI
@login_required
def perusahaan_tki_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "admin_app/data_perusahaan/tki/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan TKI
@login_required
def perusahaan_tki_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tki")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tki_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tki_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/tki/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })

# Data Perusahaan TKJ ----
@login_required
def perusahaan_tkj(request):
    perusahaan = Perusahaan.objects.filter(jurusan__iexact="tkj").order_by("nama_perusahaan")
    return render(request, "admin_app/data_perusahaan/tkj/perusahaan_tkj.html", {
        "perusahaan": perusahaan,
        "title": "Perusahaan TKJ"
    })
# Create Perusahaan TKJ
@login_required
def perusahaan_tkj_create(request):
    if request.method == "POST":
        nama_perusahaan = request.POST.get("nama_perusahaan")
        jurusan = request.POST.get("jurusan", "tkj")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        foto = request.FILES.get("foto")

        if not nama_perusahaan or not alamat or not deskripsi or not foto:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tkj_create")

        nama_unik = f"{nama_perusahaan} - {jurusan.upper()}"

        if Perusahaan.objects.filter(nama_perusahaan=nama_unik).exists():
            messages.error(request, "❌ Nama perusahaan ini sudah ada di jurusan yang sama.")
            return redirect("perusahaan_tkj_create")

        Perusahaan.objects.create(
            nama_perusahaan=nama_unik,
            jurusan=jurusan,
            alamat=alamat,
            deskripsi=deskripsi,
            foto_perusahaan=foto,
        )

        messages.success(request, f"✅ Perusahaan '{nama_perusahaan}' berhasil ditambahkan ke jurusan {jurusan.upper()}.")
        return redirect("perusahaan_tkj")

    return render(request, "admin_app/data_perusahaan/tkj/create.html", {
        "title": "Tambah Perusahaan TKJ"
    })
# Delete Perusahaan TKJ
@login_required
def perusahaan_tkj_delete(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    nama = perusahaan.nama_perusahaan
    perusahaan.delete()
    messages.success(request, f"🗑️ Perusahaan '{nama}' berhasil dihapus.")
    return redirect("perusahaan_tkj")
# Detail Perusahaan TKJ
@login_required
def perusahaan_tkj_detail(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, pk=nama_perusahaan)
    return render(request, "admin_app/data_perusahaan/tkj/detail.html", {
        "perusahaan": perusahaan,
        "title": f"Detail Perusahaan - {perusahaan.nama_perusahaan}",
    })
# Edit Perusahaan TKJ
@login_required
def perusahaan_tkj_edit(request, nama_perusahaan):
    perusahaan = get_object_or_404(Perusahaan, nama_perusahaan=nama_perusahaan)

    if request.method == "POST":
        nama = request.POST.get("nama_perusahaan")
        alamat = request.POST.get("alamat")
        deskripsi = request.POST.get("deskripsi")
        jurusan = request.POST.get("jurusan", "tkj")

        if not nama or not alamat or not deskripsi:
            messages.error(request, "❌ Semua field wajib diisi.")
            return redirect("perusahaan_tkj_edit", nama_perusahaan=perusahaan.nama_perusahaan)

        perusahaan.nama_perusahaan = nama
        perusahaan.alamat = alamat
        perusahaan.deskripsi = deskripsi
        perusahaan.jurusan = jurusan

        if "foto_perusahaan" in request.FILES:
            perusahaan.foto_perusahaan = request.FILES["foto_perusahaan"]

        perusahaan.save()
        messages.success(request, f"✅ Data '{perusahaan.nama_perusahaan}' berhasil diperbarui.")
        return redirect("perusahaan_tkj_detail", nama_perusahaan=perusahaan.nama_perusahaan)

    return render(request, "admin_app/data_perusahaan/tkj/edit.html", {
        "perusahaan": perusahaan,
        "title": f"Edit Perusahaan - {perusahaan.nama_perusahaan}",
    })
