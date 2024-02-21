# exchange/urls.py
from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fetch-exchange-rates/', views.fetch_and_save_exchange_rates),
    path('last-update/', views.get_last_update_time),
    path('convert_currency/', views.convert_currency),


]
