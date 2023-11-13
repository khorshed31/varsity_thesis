from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup' ),
    path('signin/', views.signin, name='signin' ),
    path('signout', views.signout, name='signout' ),
    path('physiotherapist/',views.physiotherapist,name="physiotherapist"),
    path('toggle_patient_status', views.toggle_patient_status, name='toggle_patient_status'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    #path('recovery/', views.recovery, name='recovery'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)