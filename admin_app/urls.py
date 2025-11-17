from django.urls import path
from . import views

urlpatterns = [
    
# Halaman User ================================================================================================== 
# Dashboard Utama User 
path("dashboard/", views.dashboard_user, name="dashboard_user"),

# User Admin ------------------------------------------------------------------
path("users/admin/", views.user_admin, name="user_admin"),
path("users/admin/create/", views.admin_create, name="admin_create"),
path("users/admin/<int:user_id>/edit/", views.admin_edit, name="admin_edit"),
path("users/admin/<int:user_id>/delete/", views.admin_delete, name="admin_delete"),

# User Guru ------------------------------------------------------------------
# Dashboard Utama User Guru 
path("users/guru/", views.user_guru, name="user_guru"),   

# User Guru Agro  ---
path("users/guru/agro/", views.guru_agro, name="tabel_agro"),
path("agro/guru/create/", views.guru_agro_create, name="guru_agro_create"),
path("agro/guru/edit/<int:user_id>/", views.guru_agro_edit, name="guru_agro_edit"),
path("agro/guru/delete/<int:user_id>/", views.guru_agro_delete, name="guru_agro_delete"),
# User Guru PM  ---
path("users/guru/pm/", views.guru_pm, name="tabel_pm"),
path("pm/guru/create/", views.guru_pm_create, name="guru_pm_create"),
path("pm/guru/edit/<int:user_id>/", views.guru_pm_edit, name="guru_pm_edit"),
path("pm/guru/delete/<int:user_id>/", views.guru_pm_delete, name="guru_pm_delete"),
# User Guru Rpl ---
path("users/guru/rpl/", views.guru_rpl, name="tabel_rpl"),
path("rpl/guru/create/", views.guru_rpl_create, name="guru_rpl_create"),
path("rpl/guru/edit/<int:user_id>/", views.guru_rpl_edit, name="guru_rpl_edit"),
path("rpl/guru/delete/<int:user_id>/", views.guru_rpl_delete, name="guru_rpl_delete"),
# User Guru Tei ---
path("users/guru/tei/", views.guru_tei, name="tabel_tei"),
path("tei/guru/create/", views.guru_tei_create, name="guru_tei_create"),
path("tei/guru/edit/<int:user_id>/", views.guru_tei_edit, name="guru_tei_edit"),
path("tei/guru/delete/<int:user_id>/", views.guru_tei_delete, name="guru_tei_delete"),
# User Guru TKI ---
path("users/guru/tki/", views.guru_tki, name="tabel_tki"),
path("tki/guru/create/", views.guru_tki_create, name="guru_tki_create"),
path("tki/guru/edit/<int:user_id>/", views.guru_tki_edit, name="guru_tki_edit"),
path("tki/guru/delete/<int:user_id>/", views.guru_tki_delete, name="guru_tki_delete"),
# User Guru TKJ ---
path("users/guru/tkj/", views.guru_tkj, name="tabel_tkj"),
path("tkj/guru/create/", views.guru_tkj_create, name="guru_tkj_create"),
path("tkj/guru/edit/<int:user_id>/", views.guru_tkj_edit, name="guru_tkj_edit"),
path("tkj/guru/delete/<int:user_id>/", views.guru_tkj_delete, name="guru_tkj_delete"),


# User Siswa ------------------------------------------------------------------
# Dashboard Utama User Siswa
path("users/siswa/", views.user_siswa, name="user_siswa"),

# User Siswa Agro ---
path("users/siswa/agro/", views.siswa_agro, name="tabel_siswa_agro"),
path("agro/siswa/create/", views.siswa_agro_create, name="siswa_agro_create"),
path("agro/siswa/edit/<int:user_id>/", views.siswa_agro_edit, name="siswa_agro_edit"),
path("agro/siswa/delete/<int:user_id>/", views.siswa_agro_delete, name="siswa_agro_delete"),
# User Siswa PM  ---
path("users/siswa/pm/", views.siswa_pm, name="tabel_siswa_pm"),
path("pm/siswa/create/", views.siswa_pm_create, name="siswa_pm_create"),
path("pm/siswa/edit/<int:user_id>/", views.siswa_pm_edit, name="siswa_pm_edit"),
path("pm/siswa/delete/<int:user_id>/", views.siswa_pm_delete, name="siswa_pm_delete"),
# User Siswa Rpl  ---
path("users/siswa/rpl/", views.siswa_rpl, name="tabel_siswa_rpl"),
path("rpl/siswa/create/", views.siswa_rpl_create, name="siswa_rpl_create"),
path("rpl/siswa/edit/<int:user_id>/", views.siswa_rpl_edit, name="siswa_rpl_edit"),
path("rpl/siswa/delete/<int:user_id>/", views.siswa_rpl_delete, name="siswa_rpl_delete"),
# User Siswa TEI  ---
path("users/siswa/tei/", views.siswa_tei, name="tabel_siswa_tei"),
path("tei/siswa/create/", views.siswa_tei_create, name="siswa_tei_create"),
path("tei/siswa/edit/<int:user_id>/", views.siswa_tei_edit, name="siswa_tei_edit"),
path("tei/siswa/delete/<int:user_id>/", views.siswa_tei_delete, name="siswa_tei_delete"),
# User Siswa TKI  ---
path("users/siswa/tki/", views.siswa_tki, name="tabel_siswa_tki"),
path("tki/siswa/create/", views.siswa_tki_create, name="siswa_tki_create"),
path("tki/siswa/edit/<int:user_id>/", views.siswa_tki_edit, name="siswa_tki_edit"),
path("tki/siswa/delete/<int:user_id>/", views.siswa_tki_delete, name="siswa_tki_delete"),
# User Siswa TKJ  ---
path("users/siswa/tkj/", views.siswa_tkj, name="tabel_siswa_tkj"),
path("tkj/siswa/create/", views.siswa_tkj_create, name="siswa_tkj_create"),
path("tkj/siswa/edit/<int:user_id>/", views.siswa_tkj_edit, name="siswa_tkj_edit"),
path("tkj/siswa/delete/<int:user_id>/", views.siswa_tkj_delete, name="siswa_tkj_delete"),

# Halaman Data Guru ==================================================================================================
# Dashboard Utama Guru 
path("dashboard_guru/", views.dashboard_guru, name="dashboard_guru"),

# Data Guru Agro  ---
path("guru/agro/", views.data_guru_agro, name="data_guru_agro"),
path("guru/agro/<str:nip>/edit/", views.edit_foto_guru_agro, name="edit_foto_guru_agro"),
# Data Guru PM ---
path("guru/pm/", views.data_guru_pm, name="data_guru_pm"),
path("guru/pm/<str:nip>/edit/", views.edit_foto_guru_pm, name="edit_foto_guru_pm"),
# Data Guru RPL ---
path("guru/rpl/", views.data_guru_rpl, name="data_guru_rpl"),
path("guru/rpl/<str:nip>/edit/", views.edit_foto_guru_rpl, name="edit_foto_guru_rpl"),
# Data Guru TEI ---
path("guru/tei/", views.data_guru_tei, name="data_guru_tei"),
path("guru/tei/<str:nip>/edit/", views.edit_foto_guru_tei, name="edit_foto_guru_tei"),
# Data Guru TKI ---
path("guru/tki/", views.data_guru_tki, name="data_guru_tki"),
path("guru/tki/<str:nip>/edit/", views.edit_foto_guru_tki, name="edit_foto_guru_tki"),
# Data Guru TKJ ---
path("guru/tkj/", views.data_guru_tkj, name="data_guru_tkj"),
path("guru/tkj/<str:nip>/edit/", views.edit_foto_guru_tkj, name="edit_foto_guru_tkj"),


# Halaman Data Siswa ==================================================================================================
# Dashboard Utama Siswa
path("dashboard_siswa/", views.dashboard_siswa, name="dashboard_siswa"),

# Data Siswa  Agro ----
path("dashboard/agro/", views.data_siswa_agro, name="data_siswa_agro"),
path("siswa/agro/edit-foto/<str:nisn>/", views.edit_foto_siswa_agro, name="edit_foto_siswa_agro"),
path("dashboard/agro/detail/<str:nisn>/", views.detail_pendaftaran_agro, name="detail_pendaftaran_agro"),
path("dashboard/agro/download-cv/<str:nisn>/", views.download_cv_agro, name="download_cv_agro"),
# Data Siswa  Pm ----
path("dashboard/pm/", views.data_siswa_pm, name="data_siswa_pm"),
path("siswa/pm/edit-foto/<str:nisn>/", views.edit_foto_siswa_pm, name="edit_foto_siswa_pm"),
path("dashboard/pm/detail/<str:nisn>/", views.detail_pendaftaran_pm, name="detail_pendaftaran_pm"),
path("dashboard/pm/download-cv/<str:nisn>/", views.download_cv_pm, name="download_cv_pm"),
# Data Siswa  Rpl  ----
path("dashboard/rpl/", views.data_siswa_rpl, name="data_siswa_rpl"),
path("siswa/rpl/edit-foto/<str:nisn>/", views.edit_foto_siswa_rpl, name="edit_foto_siswa_rpl"),
path("dashboard/rpl/detail/<str:nisn>/", views.detail_pendaftaran_rpl, name="detail_pendaftaran_rpl"),
path("dashboard/rpl/download-cv/<str:nisn>/", views.download_cv_rpl, name="download_cv_rpl"),
# Data Siswa Tei  ----
path("dashboard/tei/", views.data_siswa_tei, name="data_siswa_tei"),
path("siswa/tei/edit-foto/<str:nisn>/", views.edit_foto_siswa_tei, name="edit_foto_siswa_tei"),
path("dashboard/tei/detail/<str:nisn>/", views.detail_pendaftaran_tei, name="detail_pendaftaran_tei"),
path("dashboard/tei/download-cv/<str:nisn>/", views.download_cv_tei, name="download_cv_tei"),
# Data Siswa Tki  ----
path("dashboard/tki/", views.data_siswa_tki, name="data_siswa_tki"),
path("siswa/tki/edit-foto/<str:nisn>/", views.edit_foto_siswa_tki, name="edit_foto_siswa_tki"),
path("dashboard/tki/detail/<str:nisn>/", views.detail_pendaftaran_tki, name="detail_pendaftaran_tki"),
path("dashboard/tki/download-cv/<str:nisn>/", views.download_cv_tki, name="download_cv_tki"),
# Data Siswa Tkj   ----
path("dashboard/tkj/", views.data_siswa_tkj, name="data_siswa_tkj"),
path("siswa/tkj/edit-foto/<str:nisn>/", views.edit_foto_siswa_tkj, name="edit_foto_siswa_tkj"),
path("dashboard/tkj/detail/<str:nisn>/", views.detail_pendaftaran_tkj, name="detail_pendaftaran_tkj"),
path("dashboard/tkj/download-cv/<str:nisn>/", views.download_cv_tkj, name="download_cv_tkj"),



# Halaman Data Perusahaan ==================================================================================================
# Dashboard Utama Data Perusahaan 
path("data_perusahaan/", views.data_perusahaan, name="data_perusahaan"),

# Data Perusahaan  Agro ----
path("perusahaan/agro/", views.perusahaan_agro, name="perusahaan_agro"),
path("perusahaan/agro/create/", views.perusahaan_agro_create, name="perusahaan_agro_create"),
path("perusahaan/agro/<str:nama_perusahaan>/", views.perusahaan_agro_detail, name="perusahaan_agro_detail"),
path("perusahaan/agro/<str:nama_perusahaan>/edit/", views.perusahaan_agro_edit, name="perusahaan_agro_edit"),
path("perusahaan/agro/<str:nama_perusahaan>/delete/", views.perusahaan_agro_delete, name="perusahaan_agro_delete"),
# Data Perusahaan  PM ----
path("perusahaan/pm/", views.perusahaan_pm, name="perusahaan_pm"),
path("perusahaan/pm/create/", views.perusahaan_pm_create, name="perusahaan_pm_create"),
path("perusahaan/pm/<str:nama_perusahaan>/", views.perusahaan_pm_detail, name="perusahaan_pm_detail"),
path("perusahaan/pm/<str:nama_perusahaan>/edit/", views.perusahaan_pm_edit, name="perusahaan_pm_edit"),
path("perusahaan/pm/<str:nama_perusahaan>/delete/", views.perusahaan_pm_delete, name="perusahaan_pm_delete"),
# Data Perusahaan rpl ----
path("perusahaan/rpl/", views.perusahaan_rpl, name="perusahaan_rpl"),
path("perusahaan/rpl/create/", views.perusahaan_rpl_create, name="perusahaan_rpl_create"),
path("perusahaan/rpl/<str:nama_perusahaan>/", views.perusahaan_rpl_detail, name="perusahaan_rpl_detail"),
path("perusahaan/rpl/<str:nama_perusahaan>/edit/", views.perusahaan_rpl_edit, name="perusahaan_rpl_edit"),
path("perusahaan/rpl/<str:nama_perusahaan>/delete/", views.perusahaan_rpl_delete, name="perusahaan_rpl_delete"),
# Data Perusahaan tei  ----
path("perusahaan/tei/", views.perusahaan_tei, name="perusahaan_tei"),
path("perusahaan/tei/create/", views.perusahaan_tei_create, name="perusahaan_tei_create"),
path("perusahaan/tei/<str:nama_perusahaan>/", views.perusahaan_tei_detail, name="perusahaan_tei_detail"),
path("perusahaan/tei/<str:nama_perusahaan>/edit/", views.perusahaan_tei_edit, name="perusahaan_tei_edit"),
path("perusahaan/tei/<str:nama_perusahaan>/delete/", views.perusahaan_tei_delete, name="perusahaan_tei_delete"),
# Data Perusahaan  tki ----
path("perusahaan/tki/", views.perusahaan_tki, name="perusahaan_tki"),
path("perusahaan/tki/create/", views.perusahaan_tki_create, name="perusahaan_tki_create"),
path("perusahaan/tki/<str:nama_perusahaan>/", views.perusahaan_tki_detail, name="perusahaan_tki_detail"),
path("perusahaan/tki/<str:nama_perusahaan>/edit/", views.perusahaan_tki_edit, name="perusahaan_tki_edit"),
path("perusahaan/tki/<str:nama_perusahaan>/delete/", views.perusahaan_tki_delete, name="perusahaan_tki_delete"),
# Data Perusahaan tkj ----
path("perusahaan/tkj/", views.perusahaan_tkj, name="perusahaan_tkj"),
path("perusahaan/tkj/create/", views.perusahaan_tkj_create, name="perusahaan_tkj_create"),
path("perusahaan/tkj/<str:nama_perusahaan>/", views.perusahaan_tkj_detail, name="perusahaan_tkj_detail"),
path("perusahaan/tkj/<str:nama_perusahaan>/edit/", views.perusahaan_tkj_edit, name="perusahaan_tkj_edit"),
path("perusahaan/tkj/<str:nama_perusahaan>/delete/", views.perusahaan_tkj_delete, name="perusahaan_tkj_delete"),


]