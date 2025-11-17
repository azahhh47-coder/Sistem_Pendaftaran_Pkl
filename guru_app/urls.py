from django.urls import path
from . import views  # hanya import views, jangan import urls lain

urlpatterns = [

# Halaman Guru Agro ============================================================================
path("dashboard/agro/", views.dashboard_agro, name="dashboard_agro"),
path("dashboard/agro/terima/<str:nisn>/", views.terima_siswa_agro, name="terima_siswa_agro"),
path("dashboard/agro/tolak/<str:nisn>/", views.tolak_siswa_agro, name="tolak_siswa_agro"),
path("dashboard/agro/wawancara/<str:nisn>/", views.jadwalkan_wawancara_agro, name="jadwal_wawancara_agro"),
path("dashboard/agro/pindahkan/<str:nisn>/", views.pindahkan_siswa_agro, name="pindahkan_siswa_agro"),  
path("dashboard/agro/menunggu/<str:nisn>/", views.menunggu_siswa_agro, name="menunggu_siswa_agro"),    
path("dashboard/agro/data/", views.data_agro, name="data_agro"),
path("dashboard/agro/inbox/", views.inbox_guru_agro, name="inbox_guru_agro"),
path("dashboard/agro/detail/<str:nisn>/", views.detail_siswa_agro, name="detail_siswa_agro"),
path("agro/perusahaan/", views.perusahaan_agro_guru, name="perusahaan_agro_guru"),
path("agro/perusahaan/create/", views.perusahaan_agro_guru_create, name="perusahaan_agro_guru_create"),
path('dashboard/agro/detail/<str:nisn>/<int:pk>/', views.detail_siswa_agro, name='detail_siswa_agro'),
path("perusahaan/agro/<str:nama_perusahaan>/", views.perusahaan_agro_guru_detail, name="perusahaan_agro_guru_detail"),
path("agro/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_agro_guru_edit, name="perusahaan_agro_guru_edit"),
path("agro/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_agro_guru_delete, name="perusahaan_agro_guru_delete"),


# Halaman Guru PM ============================================================================
path("dashboard/pm/", views.dashboard_pm, name="dashboard_pm"),
path("dashboard/pm/terima/<str:nisn>/", views.terima_siswa_pm, name="terima_siswa_pm"),
path("dashboard/pm/tolak/<str:nisn>/", views.tolak_siswa_pm, name="tolak_siswa_pm"),
path("dashboard/pm/wawancara/<str:nisn>/", views.jadwalkan_wawancara_pm, name="jadwal_wawancara_pm"),
path("dashboard/pm/pindahkan/<str:nisn>/", views.pindahkan_siswa_pm, name="pindahkan_siswa_pm"),
path("dashboard/pm/menunggu/<str:nisn>/", views.menunggu_siswa_pm, name="menunggu_siswa_pm"),
path("dashboard/pm/data/", views.data_pm, name="data_pm"),
path("dashboard/pm/inbox/", views.inbox_guru_pm, name="inbox_guru_pm"),
path("dashboard/pm/detail/<str:nisn>/<int:pk>/", views.detail_siswa_pm, name="detail_siswa_pm"),
path("pm/perusahaan/", views.perusahaan_pm_guru, name="perusahaan_pm_guru"),
path("pm/perusahaan/create/", views.perusahaan_pm_guru_create, name="perusahaan_pm_guru_create"),
path("pm/perusahaan/<str:nama_perusahaan>/", views.perusahaan_pm_guru_detail, name="perusahaan_pm_guru_detail"),
path("pm/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_pm_guru_edit, name="perusahaan_pm_guru_edit"),
path("pm/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_pm_guru_delete, name="perusahaan_pm_guru_delete"),


# Halaman Guru RPL ============================================================================
path("dashboard/rpl/", views.dashboard_rpl, name="dashboard_rpl"),
path("dashboard/rpl/terima/<str:nisn>/", views.terima_siswa_rpl, name="terima_siswa_rpl"),
path("dashboard/rpl/tolak/<str:nisn>/", views.tolak_siswa_rpl, name="tolak_siswa_rpl"),
path("dashboard/rpl/wawancara/<str:nisn>/", views.jadwalkan_wawancara_rpl, name="jadwal_wawancara_rpl"),
path("dashboard/rpl/pindahkan/<str:nisn>/", views.pindahkan_siswa_rpl, name="pindahkan_siswa_rpl"),
path("dashboard/rpl/menunggu/<str:nisn>/", views.menunggu_siswa_rpl, name="menunggu_siswa_rpl"),
path("dashboard/rpl/data/", views.data_rpl, name="data_rpl"),
path("dashboard/rpl/inbox/", views.inbox_guru_rpl, name="inbox_guru_rpl"),
path("dashboard/rpl/detail/<str:nisn>/<int:pk>/", views.detail_siswa_rpl, name="detail_siswa_rpl"),
path("rpl/perusahaan/", views.perusahaan_rpl_guru, name="perusahaan_rpl_guru"),
path("rpl/perusahaan/create/", views.perusahaan_rpl_guru_create, name="perusahaan_rpl_guru_create"),
path("rpl/perusahaan/<str:nama_perusahaan>/", views.perusahaan_rpl_guru_detail, name="perusahaan_rpl_guru_detail"),
path("rpl/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_rpl_guru_edit, name="perusahaan_rpl_guru_edit"),
path("rpl/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_rpl_guru_delete, name="perusahaan_rpl_guru_delete"),

# Halaman Guru TEI ============================================================================
path("dashboard/tei/", views.dashboard_tei, name="dashboard_tei"),
path("dashboard/tei/terima/<str:nisn>/", views.terima_siswa_tei, name="terima_siswa_tei"),
path("dashboard/tei/tolak/<str:nisn>/", views.tolak_siswa_tei, name="tolak_siswa_tei"),
path("dashboard/tei/wawancara/<str:nisn>/", views.jadwalkan_wawancara_tei, name="jadwal_wawancara_tei"),
path("dashboard/tei/pindahkan/<str:nisn>/", views.pindahkan_siswa_tei, name="pindahkan_siswa_tei"),
path("dashboard/tei/menunggu/<str:nisn>/", views.menunggu_siswa_tei, name="menunggu_siswa_tei"),
path("dashboard/tei/data/", views.data_tei, name="data_tei"),
path("dashboard/tei/inbox/", views.inbox_guru_tei, name="inbox_guru_tei"),
path("dashboard/tei/detail/<str:nisn>/<int:pk>/", views.detail_siswa_tei, name="detail_siswa_tei"),
path("tei/perusahaan/", views.perusahaan_tei_guru, name="perusahaan_tei_guru"),
path("tei/perusahaan/create/", views.perusahaan_tei_guru_create, name="perusahaan_tei_guru_create"),
path("tei/perusahaan/<str:nama_perusahaan>/", views.perusahaan_tei_guru_detail, name="perusahaan_tei_guru_detail"),
path("tei/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_tei_guru_edit, name="perusahaan_tei_guru_edit"),
path("tei/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_tei_guru_delete, name="perusahaan_tei_guru_delete"),


# Halaman Guru TKI ============================================================================
path("dashboard/tki/", views.dashboard_tki, name="dashboard_tki"),
path("dashboard/tki/terima/<str:nisn>/", views.terima_siswa_tki, name="terima_siswa_tki"),
path("dashboard/tki/tolak/<str:nisn>/", views.tolak_siswa_tki, name="tolak_siswa_tki"),
path("dashboard/tki/wawancara/<str:nisn>/", views.jadwalkan_wawancara_tki, name="jadwal_wawancara_tki"),
path("dashboard/tki/pindahkan/<str:nisn>/", views.pindahkan_siswa_tki, name="pindahkan_siswa_tki"),
path("dashboard/tki/menunggu/<str:nisn>/", views.menunggu_siswa_tki, name="menunggu_siswa_tki"),
path("dashboard/tki/data/", views.data_tki, name="data_tki"),
path("dashboard/tki/inbox/", views.inbox_guru_tki, name="inbox_guru_tki"),
path("dashboard/tki/detail/<str:nisn>/<int:pk>/", views.detail_siswa_tki, name="detail_siswa_tki"),
path("tki/perusahaan/", views.perusahaan_tki_guru, name="perusahaan_tki_guru"),
path("tki/perusahaan/create/", views.perusahaan_tki_guru_create, name="perusahaan_tki_guru_create"),
path("tki/perusahaan/<str:nama_perusahaan>/", views.perusahaan_tki_guru_detail, name="perusahaan_tki_guru_detail"),
path("tki/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_tki_guru_edit, name="perusahaan_tki_guru_edit"),
path("tki/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_tki_guru_delete, name="perusahaan_tki_guru_delete"),

# Halaman Guru TKJ ============================================================================
path("dashboard/tkj/", views.dashboard_tkj, name="dashboard_tkj"),
path("dashboard/tkj/terima/<str:nisn>/", views.terima_siswa_tkj, name="terima_siswa_tkj"),
path("dashboard/tkj/tolak/<str:nisn>/", views.tolak_siswa_tkj, name="tolak_siswa_tkj"),
path("dashboard/tkj/wawancara/<str:nisn>/", views.jadwalkan_wawancara_tkj, name="jadwal_wawancara_tkj"),
path("dashboard/tkj/pindahkan/<str:nisn>/", views.pindahkan_siswa_tkj, name="pindahkan_siswa_tkj"),
path("dashboard/tkj/menunggu/<str:nisn>/", views.menunggu_siswa_tkj, name="menunggu_siswa_tkj"),
path("dashboard/tkj/data/", views.data_tkj, name="data_tkj"),
path("dashboard/tkj/inbox/", views.inbox_guru_tkj, name="inbox_guru_tkj"),
path("dashboard/tkj/detail/<str:nisn>/<int:pk>/", views.detail_siswa_tkj, name="detail_siswa_tkj"),
path("tkj/perusahaan/", views.perusahaan_tkj_guru, name="perusahaan_tkj_guru"),
path("tkj/perusahaan/create/", views.perusahaan_tkj_guru_create, name="perusahaan_tkj_guru_create"),
path("tkj/perusahaan/<str:nama_perusahaan>/", views.perusahaan_tkj_guru_detail, name="perusahaan_tkj_guru_detail"),
path("tkj/perusahaan/<str:nama_perusahaan>/edit/", views.perusahaan_tkj_guru_edit, name="perusahaan_tkj_guru_edit"),
path("tkj/perusahaan/<str:nama_perusahaan>/delete/", views.perusahaan_tkj_guru_delete, name="perusahaan_tkj_guru_delete"),

]