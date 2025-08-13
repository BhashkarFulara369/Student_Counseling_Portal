from django.urls import path

from SCP_PORTAL import views

urlpatterns = [
    path("", views.index, name='home'),
    path("signup",views.signup,name='signup'),
    path("login_view",views.login_view,name='login_view'),
    path('student/login/', views.student_login, name='student_login'),
    path('admin/login/', views.admin_login, name='admin_login'),


    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/submit-info/', views.submit_personal_info, name='submit_personal_info'),
    path('student/education/', views.education_info, name='education_info'),
    path('student/submit-education/', views.submit_education_info, name='submit_education_info'),
    
    path('student/choices/', views.choice_filling, name='choice_filling'),
    path('student/submit-choices/', views.submit_choices, name='submit_choices'),
    path('student/accept-allocation/', views.accept_allocation, name='accept_allocation'),
    path('student/upload-receipt/', views.upload_receipt, name='upload_receipt'),
    path('student/download-offer-letter/', views.download_offer_letter, name='download_offer_letter'),
  # ADMIN PANEL RELATED PATHS 
   path('admin-panel/', views.staff_admin_panel, name='staff_admin_panel'),
  # Staff Admin Panel Actions
   path('admin-panel/allocate/<int:student_id>/', views.allocate_branch, name='allocate_branch'),
   path('admin-panel/toggle-acceptance/<int:student_id>/', views.toggle_acceptance, name='toggle_acceptance'),
   path('admin-panel/verify-payment/<int:student_id>/', views.verify_payment, name='verify_payment'),
   path('admin-panel/offer-letter/<int:student_id>/', views.generate_offer_letter, name='generate_offer_letter'),

   path('logout/', views.logout_view, name='logout'),
]


