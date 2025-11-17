from django.urls import path
from . import views

urlpatterns = [

# Data Agro ============================================================================
path("dashboard_siswa_agro/", views.dashboard_siswa_agro, name="dashboard_siswa_agro"),
path("perusahaan/agro/", views.perusahaan_siswa_list_agro, name="perusahaan_siswa_list_agro"),
path("perusahaan/agro/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_agro, name="perusahaan_siswa_detail_agro"),
path("pendaftaran_pkl_agro/", views.pendaftaran_pkl_agro, name="pendaftaran_pkl_agro"),
path("inbox_siswa_agro/", views.inbox_siswa_agro, name="inbox_siswa_agro"),
path('pendaftaran/edit/<int:pk>/', views.edit_pendaftaran_agro, name='edit_pendaftaran_agro'),
path('pendaftaran/delete/<int:pk>/', views.pendaftaran_pkl_delete, name='pendaftaran_pkl_delete'),


# Data PM ============================================================================
path("dashboard_siswa_pm/", views.dashboard_siswa_pm, name="dashboard_siswa_pm"),
path("perusahaan/pm/", views.perusahaan_siswa_list_pm, name="perusahaan_siswa_list_pm"),
path("perusahaan/pm/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_pm, name="perusahaan_siswa_detail_pm"),
path("pendaftaran_pkl_pm/", views.pendaftaran_pkl_pm, name="pendaftaran_pkl_pm"),
path("inbox_siswa_pm/", views.inbox_siswa_pm, name="inbox_siswa_pm"),
path('pendaftaran_pm/edit/<int:pk>/', views.edit_pendaftaran_pm, name='edit_pendaftaran_pm'),
path('pendaftaran_pm/delete/<int:pk>/', views.pendaftaran_pkl_delete_pm, name='pendaftaran_pkl_delete_pm'),

# Data RPL ============================================================================
path("dashboard_siswa_rpl/", views.dashboard_siswa_rpl, name="dashboard_siswa_rpl"),
path("perusahaan/rpl/", views.perusahaan_siswa_list_rpl, name="perusahaan_siswa_list_rpl"),
path("perusahaan/rpl/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_rpl, name="perusahaan_siswa_detail_rpl"),
path("pendaftaran_pkl_rpl/", views.pendaftaran_pkl_rpl, name="pendaftaran_pkl_rpl"),
path("inbox_siswa_rpl/", views.inbox_siswa_rpl, name="inbox_siswa_rpl"),
path('pendaftaran_rpl/edit/<int:pk>/', views.edit_pendaftaran_rpl, name='edit_pendaftaran_rpl'),
path('pendaftaran_rpl/delete/<int:pk>/', views.pendaftaran_pkl_delete_rpl, name='pendaftaran_pkl_delete_rpl'),

# Data TEI ============================================================================
path("dashboard_siswa_tei/", views.dashboard_siswa_tei, name="dashboard_siswa_tei"),
path("perusahaan/tei/", views.perusahaan_siswa_list_tei, name="perusahaan_siswa_list_tei"),
path("perusahaan/tei/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_tei, name="perusahaan_siswa_detail_tei"),
path("pendaftaran_pkl_tei/", views.pendaftaran_pkl_tei, name="pendaftaran_pkl_tei"),
path("inbox_siswa_tei/", views.inbox_siswa_tei, name="inbox_siswa_tei"),
path('pendaftaran_tei/edit/<int:pk>/', views.edit_pendaftaran_tei, name='edit_pendaftaran_tei'),
path('pendaftaran_tei/delete/<int:pk>/', views.pendaftaran_pkl_delete_tei, name='pendaftaran_pkl_delete_tei'),

# Data TKI ============================================================================
path("dashboard_siswa_tki/", views.dashboard_siswa_tki, name="dashboard_siswa_tki"),
path("perusahaan/tki/", views.perusahaan_siswa_list_tki, name="perusahaan_siswa_list_tki"),
path("perusahaan/tki/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_tki, name="perusahaan_siswa_detail_tki"),
path("pendaftaran_pkl_tki/", views.pendaftaran_pkl_tki, name="pendaftaran_pkl_tki"),
path("inbox_siswa_tki/", views.inbox_siswa_tki, name="inbox_siswa_tki"),
path('pendaftaran_tki/edit/<int:pk>/', views.edit_pendaftaran_tki, name='edit_pendaftaran_tki'),
path('pendaftaran_tki/delete/<int:pk>/', views.pendaftaran_pkl_delete_tki, name='pendaftaran_pkl_delete_tki'),

# Data TKJ ============================================================================
path("dashboard_siswa_tkj/", views.dashboard_siswa_tkj, name="dashboard_siswa_tkj"),
path("perusahaan/tkj/", views.perusahaan_siswa_list_tkj, name="perusahaan_siswa_list_tkj"),
path("perusahaan/tkj/<str:nama_perusahaan>/", views.perusahaan_siswa_detail_tkj, name="perusahaan_siswa_detail_tkj"),
path("pendaftaran_pkl_tkj/", views.pendaftaran_pkl_tkj, name="pendaftaran_pkl_tkj"),
path("inbox_siswa_tkj/", views.inbox_siswa_tkj, name="inbox_siswa_tkj"),
path('pendaftaran_tkj/edit/<int:pk>/', views.edit_pendaftaran_tkj, name='edit_pendaftaran_tkj'),
path('pendaftaran_tkj/delete/<int:pk>/', views.pendaftaran_pkl_delete_tkj, name='pendaftaran_pkl_delete_tkj'),

]
