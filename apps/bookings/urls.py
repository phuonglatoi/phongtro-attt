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
    # CUSTOMER ROUTES
    # ============================================
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),

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
    path('landlord/phongtro/<int:pk>/edit/', views.edit_phongtro, name='edit_phongtro'),
    path('landlord/phongtro/<int:pk>/status/', views.update_phongtro_status, name='update_phongtro_status'),

    # Appointment management
    path('landlord/henxem/<int:pk>/confirm/', views.confirm_henxem, name='confirm_henxem'),
    path('landlord/henxem/<int:pk>/reject/', views.reject_henxem, name='reject_henxem'),

    # ============================================
    # ADMIN ROUTES
    # ============================================
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/approve-landlord/<int:pk>/', views.approve_landlord_request, name='approve_landlord_request'),
    path('dashboard/admin/reject-landlord/<int:pk>/', views.reject_landlord_request, name='reject_landlord_request'),
    path('dashboard/admin/approve-room/<int:pk>/', views.approve_room, name='approve_room'),
    path('dashboard/admin/reject-room/<int:pk>/', views.reject_room, name='reject_room'),
    path('dashboard/admin/customers/', views.manage_customers, name='manage_customers'),
    path('dashboard/admin/customers/add/', views.add_user, name='add_user'),
    path('dashboard/admin/customers/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('dashboard/admin/customers/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('dashboard/admin/customers/toggle/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    path('dashboard/admin/rooms/', views.admin_manage_rooms, name='admin_manage_rooms'),
    path('dashboard/admin/rooms/delete/<int:pk>/', views.admin_delete_room, name='admin_delete_room'),
    path('dashboard/admin/active-rooms/', views.manage_active_rooms, name='manage_active_rooms'),
    path('dashboard/admin/history/', views.admin_history, name='admin_history'),
]