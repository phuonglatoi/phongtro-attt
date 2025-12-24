from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # ============================================
    # TENANT ROUTES
    # ============================================

    # Booking management
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('henxem/<int:room_id>/', views.create_henxem, name='create_henxem'),
    path('henxem/cancel/<int:pk>/', views.cancel_henxem, name='cancel_henxem'),

    # Reviews
    path('review/<int:room_id>/', views.create_review, name='create_review'),

    # Messages
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:partner_id>/', views.conversation, name='conversation'),
    path('message/room/<int:room_id>/', views.send_message_to_landlord, name='send_message_to_landlord'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),

    # ============================================
    # LANDLORD ROUTES
    # ============================================

    # Request to become landlord
    path('request-landlord/', views.request_landlord, name='request_landlord'),

    # Landlord dashboard
    path('landlord/', views.landlord_dashboard, name='landlord_dashboard'),

    # Property management
    path('landlord/nhatro/', views.manage_nhatro, name='manage_nhatro'),
    path('landlord/nhatro/create/', views.create_nhatro, name='create_nhatro'),
    path('landlord/nhatro/<int:nhatro_id>/phongtro/', views.manage_phongtro, name='manage_phongtro'),
    path('landlord/nhatro/<int:nhatro_id>/phongtro/create/', views.create_phongtro, name='create_phongtro'),
    path('landlord/phongtro/<int:pk>/status/', views.update_phongtro_status, name='update_phongtro_status'),

    # Appointment management
    path('landlord/henxem/<int:pk>/confirm/', views.confirm_henxem, name='confirm_henxem'),
    path('landlord/henxem/<int:pk>/reject/', views.reject_henxem, name='reject_henxem'),

    # ============================================
    # ADMIN ROUTES
    # ============================================
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('quan_tri/admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('quan_tri/approve-landlord/<int:pk>/', views.approve_landlord_request, name='approve_landlord_request'),
    path('quan_tri/reject-landlord/<int:pk>/', views.reject_landlord_request, name='reject_landlord_request'),
    path('quan_tri/approve-room/<int:pk>/', views.approve_room, name='approve_room'),
    path('quan_tri/reject-room/<int:pk>/', views.reject_room, name='reject_room'),
    # path('admin-dashboard/approve-landlord/<int:pk>/', views.approve_landlord_request, name='approve_landlord_request'),
    # path('admin-dashboard/reject-landlord/<int:pk>/', views.reject_landlord_request, name='reject_landlord_request'),
    # path('admin-dashboard/approve-room/<int:pk>/', views.approve_room, name='approve_room'),
    # path('admin-dashboard/reject-room/<int:pk>/', views.reject_room, name='reject_room'),
    path('quan_tri/customers/', views.manage_customers, name='manage_customers'),
    path('quan_tri/customers/toggle/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    path('quan_tri/active-rooms/', views.manage_active_rooms, name='manage_active_rooms'),
    path('quan_tri/history/', views.admin_history, name='admin_history'),
]