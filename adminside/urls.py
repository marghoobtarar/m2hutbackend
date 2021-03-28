from django.urls import path
from adminside import views

urlpatterns = [
    path('notices/',views.Notices.as_view(),
        name = "it will create notices and get them"),
    path('work-logs-break/',views.WorkLogsBreakType.as_view(),
        name = "it will create the break of logs"),
    path('manage_notices/<int:pk>/',views.ManageNotices.as_view(),
        name = "it will update the notices"),
    path('styling/',views.Styling.as_view(),
        name = "it will update the notices"),
    path('manage_styling/<int:pk>/',views.ManageStyling.as_view(),
        name = "it will update the notices"),
    path('typography/',views.Typography.as_view(),
        name = "it will get the styling "),
    path('manage_typography/<int:pk>/',views.ManageTypography.as_view(),
        name = "it will update the typography "),

    path('register_email/',views.RegisterEmail.as_view(),
        name = "it will get and post the register email"),
    path('manage_register_email/<int:pk>/',views.ManageRegisterEmail.as_view(),
        name = "it will update the register email"),
    
    path('suspend_email/',views.SuspendEmail.as_view(),
        name = "it will get and post the suspend email"),

    path('manage_suspend_email/<int:pk>/',views.ManageSuspendEmail.as_view(),
        name = "it will update the suspend email "),
    path('ckeditor_image/',views.CkeditorImage.as_view(),
        name = "it will upload the ckeditor image and return url"),
      path('admin_email/',views.AdminEmail.as_view(),
        name = "it will post and get the admin email"),

    path('manage_admin_email/<int:pk>/',views.ManageAdminEmail.as_view(),
        name = "it will update and delete the  admin email"),
    
    path('dashboard_analytics/',views.DashboardAnalytics.as_view(),
        name = 'it will get the analytics of the user')
]
