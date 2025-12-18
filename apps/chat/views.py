from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TinNhan
from apps.accounts.models import Khachhang

@login_required
def chat_history(request, recipient_id):
    """Xem lịch sử chat với một người cụ thể"""
    sender = get_object_or_404(Khachhang, matk=request.user)
    recipient = get_object_or_404(Khachhang, pk=recipient_id)
    
    # Lấy tin nhắn giữa 2 người (2 chiều)
    messages = TinNhan.objects.filter(
        models.Q(nguoigui=sender, nguoinhan=recipient) | 
        models.Q(nguoigui=recipient, nguoinhan=sender)
    ).order_by('tg_tao')
    
    # Đánh dấu là đã đọc khi mở hội thoại
    TinNhan.objects.filter(nguoigui=recipient, nguoinhan=sender, trangthai=False).update(trangthai=True)

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            TinNhan.objects.create(nguoigui=sender, nguoinhan=recipient, tinnhan=content)
            return redirect('chat:chat_history', recipient_id=recipient_id)

    return render(request, 'chat/conversation.html', {
        'messages': messages,
        'recipient': recipient
    })