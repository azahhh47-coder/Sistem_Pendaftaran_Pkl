from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomLoginForm  

# ---------------------------
# Mapping jurusan -> dashboard
# ---------------------------
# Dictionary ini berfungsi untuk menghubungkan (memetakan) jurusan guru ke halaman dashboard masing-masing.
# Jadi jika guru jurusan RPL login, akan diarahkan ke dashboard_rpl, dan seterusnya.
JURUSAN_DASHBOARD_GURU = {
    "agro": "dashboard_agro",
    "tkj": "dashboard_tkj",
    "pm": "dashboard_pm",
    "rpl": "dashboard_rpl",
    "tki": "dashboard_tki",
    "tei": "dashboard_tei",
}
#sama dengan guru 
JURUSAN_DASHBOARD_SISWA = {
    "agro": "dashboard_siswa_agro",
    "tkj": "dashboard_siswa_tkj",
    "pm": "dashboard_siswa_pm",
    "rpl": "dashboard_siswa_rpl",
    "tki": "dashboard_siswa_tki",
    "tei": "dashboard_siswa_tei",
}

# Dashboard sebelum login ================================================================
def dashboard(request):
    return render(request, "user_app/dashboard.html")

# Login (Admin, Guru, Siswa) -------------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Berhasil login, selamat datang {user.username}!")

            # Routing sesuai role + jurusan
            jurusan = (user.jurusan or "").lower()

            if user.is_staff or user.role == "admin":
                return redirect("home")

            elif user.role == "guru" and jurusan in JURUSAN_DASHBOARD_GURU:
                return redirect(JURUSAN_DASHBOARD_GURU[jurusan])

            elif user.role == "siswa" and jurusan in JURUSAN_DASHBOARD_SISWA:
                return redirect(JURUSAN_DASHBOARD_SISWA[jurusan])

            else:
                messages.error(request, "❌ Jurusan atau role tidak dikenali.")
                return redirect("dashboard")

        else:
            messages.error(request, "❌ Username atau password salah")
    else:
        form = CustomLoginForm(request)

    return render(request, "user_app/login.html", {"form": form})

# Logout (Admin, Guru, Siswa) -------------------------------------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Anda berhasil logout.")
    return redirect("dashboard")

# Kembali ke dashboard dari halaman login (tanpa notifikasi) ----------------------------
def back_to_dashboard(request):
    return redirect("dashboard")


# Home Admin ========================================================================
@login_required
def home(request):
    return render(request, "admin_app/home.html", {"user": request.user})


# GURU --------------------------------------------------------------------------------------------------------
# Home Guru Agro ========================================================================
@login_required
def dashboard_agro(request):
    return render(request, "guru_app/agro/home.html", {"user": request.user})

# Home Guru PM ========================================================================
@login_required
def dashboard_pm(request):
    return render(request, "guru_app/pm/home.html", {"user": request.user})

# Home Guru RPL ========================================================================
@login_required
def dashboard_rpl(request):
    return render(request, "guru_app/rpl/home.html", {"user": request.user})

# Home Guru TEI ========================================================================
@login_required
def dashboard_tei(request):
    return render(request, "guru_app/tei/home.html", {"user": request.user})

# Home Guru TKI ========================================================================
@login_required
def dashboard_tki(request):
    return render(request, "guru_app/tki/home.html", {"user": request.user})

# Home Guru TKJ ========================================================================
@login_required
def dashboard_tkj(request):
    return render(request, "guru_app/tkj/home.html", {"user": request.user})


# SISWA  --------------------------------------------------------------------------------------------------------

# Home Siswa Agro ========================================================================
@login_required
def dashboard_siswa_agro(request):
    return render(request, "siswa_app/agro/home.html", {"user": request.user})

# Home Siswa PM ========================================================================
@login_required
def dashboard_siswa_pm(request):
    return render(request, "siswa_app/pm/home.html", {"user": request.user})

# Home Siswa RPL ========================================================================
@login_required
def dashboard_siswa_rpl(request):
    return render(request, "siswa_app/rpl/home.html", {"user": request.user})

# Home Siswa TEI ========================================================================
@login_required
def dashboard_siswa_tei(request):
    return render(request, "siswa_app/tei/home.html", {"user": request.user})

# Home Siswa TKI ========================================================================
@login_required
def dashboard_siswa_tki(request):
    return render(request, "siswa_app/tki/home.html", {"user": request.user})

# Home Siswa TKJ ========================================================================
@login_required
def dashboard_siswa_tkj(request):
    return render(request, "siswa_app/tkj/home.html", {"user": request.user})
