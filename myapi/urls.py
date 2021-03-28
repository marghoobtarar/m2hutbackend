from django.urls import path, include, re_path
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static
from django.conf import settings
from adminside.views import FrontendAppView
from django.conf.urls import url, include
from .view import GeneratePDF, GeneratePDFMonth
from django.contrib import admin

urlpatterns = [
    path('admin/' , admin.site.urls),
     path('api/token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
     path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
     path('pdf/<str:pk>/',GeneratePDF.as_view(), name='download the pdf static'),
     path('pdf_month/<str:pk>/',GeneratePDFMonth.as_view(), name='download the pdf month statics'),

     path('adminuser/', include('adminside.urls')),
    
     path('user/', include('user.urls')),
     path('userAuth/', include('UserAuth.urls')),

#     path('core/', include('core.urls')),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path(r'^', FrontendAppView.as_view())]
