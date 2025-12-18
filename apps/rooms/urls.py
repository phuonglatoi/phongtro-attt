# ============================================
# apps/rooms/urls.py
# ============================================

from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('rooms/', views.room_list_view, name='room_list'),
    path('rooms/<int:pk>/', views.room_detail_view, name='room_detail'),
    path('rooms/create/', views.room_create_view, name='room_create'),
    path('rooms/<int:pk>/update/', views.room_update_view, name='room_update'),
    path('rooms/<int:pk>/delete/', views.room_delete_view, name='room_delete'),
    path('search/', views.search_view, name='search'),

    # Policy pages
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('policies/', views.policies_view, name='policies'),
    path('contact/', views.contact_view, name='contact'),
]
