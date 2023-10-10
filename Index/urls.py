from django.urls import path,include
from .import views
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/account/signin/'), name='home'),
    path('account/',include('account.urls')),
    path('home/',include('home.urls')),
]