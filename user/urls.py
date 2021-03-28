from django.urls import path
from user import views


urlpatterns = [
# get the accesss_token and user data
    path('authenticate/', views.CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path('analytics/', views.DashboardAnalytics.as_view(),
        name='get the analytics of the user'),
    path('work-logs/',views.WorkLogs.as_view(),
        name = "it will create the work logs"),
    path('manage-work-logs/<int:pk>/',views.ManageWorkLogs.as_view(),
        name = "it will manage the work logs"),
    path('work-logs/status/',views.WorkLogsStatus.as_view(),
        name = "it will give the status work logs"),
    path('notices/',views.Notices.as_view(),
        name = "it will give the status work logs"),
    path('manage_notices/<int:pk>/',views.ManageNotices.as_view(),
        name = "it will update the notices logs"),
    
    path('work-logs-break/',views.WorkLogsBreakType.as_view(),
        name = "it will create the break of logs"),
    path('styling/',views.Styling.as_view(),
        name = "it will get the styling "),
    path('typography/',views.Typography.as_view(),
        name = "it will get the styling "),
    path('styling_typography/',views.StylingTypography.as_view(),
        name = "it will get the styling "),
]
