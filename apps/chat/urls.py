from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('with/<int:recipient_id>/', views.chat_history, name='chat_history'),
]