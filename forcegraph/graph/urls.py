from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth_view, name='auth_view'),
    path('graph/', views.graph_view, name='graph_view')
]