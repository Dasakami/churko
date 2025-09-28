from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from quests.models import Level
# Create your views here.
from django.utils import timezone
from django.contrib import messages

def create_room(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    room = Room.objects.create(level=level, created_by=request.user)
    RoomMember.objects.create(room=room, user=request.user)

    first_task = level.tasks.order_by('order').first()
    RoomProgress.objects.create(room=room, current_task=first_task, task_index=0)

    return redirect('play_room', room_id=room.id)


def play_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if not room.members.filter(user=request.user).exists():
        messages.error(request, "Вы не состоите в этой комнате.")
        return redirect('main')
    
    progress = room.progress
    members = room.members.all()
    messages_list = ChatMessage.objects.filter(room=room).order_by('timestamp') 
    invites = RoomInvite.objects.filter(room=room, status='pending')
    invite_links = [request.build_absolute_uri(f'/rooms/room/join/{invite.token}/') for invite in invites]

    # Назначаем первую задачу, если current_task пустой
    if not progress.current_task:
        first_task = room.level.tasks.order_by('order').first()
        if first_task:
            progress.current_task = first_task
            progress.task_index = 0
            progress.task_started_at = timezone.now()
            progress.save()
        else:
            messages.error(request, "В этом уровне нет задач")
            return redirect('room_detail', room_id=room.id)

    if progress.completed:
        return render(request, 'rooms/room_completed.html', {'room': room})
    
    if progress.time_left_for_level() <= 0 or progress.time_left_for_task() <= 0:
        progress.completed = False
        progress.save()
        return render(request, 'rooms/time_over.html', {'room': room})
    

    if request.method == "POST":
        code = request.POST.get('code').strip()
        if progress.current_task and code == progress.current_task.correct_code:
            next_task = room.level.tasks.order_by('order')[progress.task_index + 1:progress.task_index + 2].first()
            if next_task:
                progress.current_task = next_task
                progress.task_index += 1
                progress.task_started_at = timezone.now()
                progress.save()
            else:
                progress.completed = True
                progress.save()
                return redirect('play_room', room_id=room.id)

    return render(request, 'rooms/play_room.html', {
        'room': room,
        'task': progress.current_task,
        'members': members,
        'progress': progress,
        'messages': messages_list,
        'invites': invites,
        'invite_links': invite_links,
        'progress': {
        'task_index': progress.task_index,
        'time_left_for_task': int(progress.time_left_for_task())  # <- важно int
    }
    })




def add_member(request, room_id):
    if request.method == 'POST':
        username = request.POST.get('username')
        from users.models import User
        user = get_object_or_404(User, username=username)
        room = get_object_or_404(Room, id=room_id)
        RoomMember.objects.create(room=room,user=user)
        return redirect('room_detail', room_id=room.id)
    return redirect('room_detail', room_id=room_id)

def create_room_invite_link(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Проверяем, что текущий пользователь — владелец комнаты
    if room.created_by != request.user:
        messages.error(request, "Только владелец комнаты может создавать приглашения.")
        return redirect('play_room', room_id=room.id)

    # Удаляем все старые приглашения со статусом 'pending'
    RoomInvite.objects.filter(room=room, status='pending').delete()

    # Создаем новое приглашение
    invite = RoomInvite.objects.create(
        room=room,
        sender=request.user
    )

    # Генерируем ссылку
    link = request.build_absolute_uri(f'/rooms/room/join/{invite.token}/')
    messages.success(request, f"Ссылка для приглашения создана: {link}")
    return redirect('play_room', room_id=room.id)

def join_room_by_link(request, token):
    invite = get_object_or_404(RoomInvite, token=token)

    if invite.status != 'pending':
        messages.info(request, "Ссылка уже использована или отклонена")
        return redirect('dashboard')

    # Проверка: если пользователь уже в комнате — ничего не делаем
    if not invite.room.members.filter(user=request.user).exists():
        invite.accept(request.user)
        messages.success(request, f"Вы присоединились к комнате {invite.room.id}")

    return redirect('play_room', room_id=invite.room.id)
