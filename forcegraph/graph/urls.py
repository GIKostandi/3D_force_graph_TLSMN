from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth_view, name='auth_view'),
    path("proxy-image/", views.proxy_image, name="proxy_image"),
]