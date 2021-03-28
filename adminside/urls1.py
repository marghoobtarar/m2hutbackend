from django.urls import path
from adminside import views

urlpatterns = [

    path('hello/', views.HelloView.as_view(), name='hello'),


    path('pitstop/', views.PitStop.as_view(), name='PitStop'),
    path('pitstop_Search_like/', views.PitStopSearch.as_view(), name='PitStop'),

    path('pitstop_list/', views.PitStopList.as_view(), name='PitStop'),
    path('pitstop_all/', views.PitStopAll.as_view(), name='PitStop'),

    path('file_pit_stop/', views.FilePitStop.as_view(), name='PitStop'),

    path('manage_pitstop/<int:pk>/',
         views.ManagePitStop.as_view(), name='ManagePitStop'),

    path('location/', views.Location.as_view(), name='Location'),
    path('location_list/', views.LocationList.as_view(), name='Location'),
    path('location_search_like/', views.LocationSearch.as_view(), name='Location'),

    path('manage_locations/<int:pk>/',
         views.ManageLocation.as_view(), name='manage_location'),

    path('recommended_location/<int:pk>/', views.RecommendedLocation.as_view(),
         name='RecommendedLocation'),
    path('manage_recommended_location/<int:pk>/',
         views.ManageRecommendedLocation.as_view(), name='ManageRecommendedLocation'),
    path('recommended_position/<int:pk>/', views.RecommendedPosition.as_view(),
         name='Recommended position'),
    path('manage_recommended_position/<int:pk>/',
         views.ManageRecommendedPosition.as_view(), name='Recommended position manage'),

    path('recommended_position_location/<int:pk>/', views.RecommendedPositionLocation.as_view(),
         name='Recommended positon location'),
    path('manage_recommended_position_location/<int:pk>/',
         views.ManageRecommendedPositionLocation.as_view(), name='Recommended positon location'),

     path('resolve_migration/',views.resolveMigration.as_view(), name='Resolving migration')


]
