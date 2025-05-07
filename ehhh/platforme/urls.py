from django.urls import path
from . import views

urlpatterns = [
    path('api/concours/<int:pk>/', views.concours_detail_api, name='concours_api'),
    path('', views.home, name='home'),
    path('platforme/', views.registration_form, name='registration_form'),
    path('confirmation/<int:candidat_id>/', views.confirmation, name='confirmation'),
]