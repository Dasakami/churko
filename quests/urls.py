from django.urls import path
from . import views
urlpatterns = [
    path('', views.main , name='main'),
    path('store/', views.store, name='store'),
    path('districts/', views.district_list, name='district_list'),
    path('<int:district_id>/levels/', views.level_list, name='level_list'),
]