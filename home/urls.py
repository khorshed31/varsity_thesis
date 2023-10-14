from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name="home"),
    path('web_cam', views.web_cam, name="web_cam"),
    path('therapy', views.therapy, name="therapy"),
    path('recorded_video', views.recorded_video, name="recorded_video"),
    path('classify_therapy', views.classify_therapy, name="classify_therapy"),
    path('upload_video', views.upload_video, name="upload_video"),
    path('results_page', views.results_page, name='results_page'),
    path('create_report', views.save_form_data, name='create_report'),
    path('my_reports', views.my_reports, name='my_reports'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)