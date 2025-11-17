from django.urls import path
from . import views

urlpatterns = [
# ==================================================================================================
# Dashboard Sebelum Login 
path("", views.dashboard, name="dashboard"),

# ==================================================================================================
# Login,Logout dan Kembali untuk login ke dashboard utama 
path("login/", views.login_view, name="login"),
path("logout/", views.logout_view, name="logout"),
path("back/", views.back_to_dashboard, name="back_to_dashboard"),

# ==================================================================================================
# Halaman Home Admin
path("home/", views.home, name="home"),

# ==================================================================================================
# Halaman Dashboard Guru per Jurusan
path("dashboard_agro/", views.dashboard_agro, name="dashboard_agro"),
path("dashboard_tkj/", views.dashboard_tkj, name="dashboard_tkj"),
path("dashboard_pm/", views.dashboard_pm, name="dashboard_pm"),
path("dashboard_rpl/", views.dashboard_rpl, name="dashboard_rpl"),
path("dashboard_tki/", views.dashboard_tki, name="dashboard_tki"),
path("dashboard_tei/", views.dashboard_tei, name="dashboard_tei"),

# ==================================================================================================
# Halaman Dashboard Siswa per Jurusan
path("dashboard_siswa_agro/", views.dashboard_siswa_agro, name="dashboard_siswa_agro"),
path("dashboard_siswa_tkj/", views.dashboard_siswa_tkj, name="dashboard_siswa_tkj"),
path("dashboard_siswa_pm/", views.dashboard_siswa_pm, name="dashboard_siswa_pm"),
path("dashboard_siswa_rpl/", views.dashboard_siswa_rpl, name="dashboard_siswa_rpl"),
path("dashboard_siswa_tki/", views.dashboard_siswa_tki, name="dashboard_siswa_tki"),
path("dashboard_siswa_tei/", views.dashboard_siswa_tei, name="dashboard_siswa_tei"),
]
