from django.shortcuts import render, redirect, get_object_or_404
from .models import District
from rooms.models import Room

def main(request):
    return render(request, 'index.html')

def store(request):
    return render(request, 'shop/store.html')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

def permission_denied(request, exception):
    return render(request, '403.html', status=403)

def bad_request(request, exception):
    return render(request, '400.html', status=400)


def district_list(request):
    districts = District.objects.filter(is_active=True)
    return render(request, 'quests/district_list.html', {'districts': districts})


def level_list(request, district_id):
    district = get_object_or_404(District, id=district_id)
    levels = district.levels.all()
    levels_comp = district.levels.filter(status='completed').count()

    # Используем объект request.user, а не request.user.id
    user_rooms_qs = Room.objects.filter(members__user=request.user, is_active=True).select_related('level')

    # словарь {level_id: room_id}
    user_rooms = {room.level.id: room.id for room in user_rooms_qs}

    return render(request, 'quests/level_list.html', {
        'district': district,
        'levels': levels,
        'user_rooms': user_rooms,
        'levels_comp': levels_comp
    })
