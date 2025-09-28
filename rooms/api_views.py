from rest_framework import generics, permissions
from quests.models import District, Level, Task
from .serializers import DistrictSerializer, LevelSerializer, TaskSerializer


# Получить список районов
class DistrictListAPIView(generics.ListAPIView):
    queryset = District.objects.filter(is_active=True)
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]


# Уровни конкретного района
class LevelListAPIView(generics.ListAPIView):
    serializer_class = LevelSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        district_id = self.kwargs.get("district_id")
        return Level.objects.filter(district_id=district_id, is_active=True)


# Детали уровня (с задачами)
class LevelDetailAPIView(generics.RetrieveAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    lookup_field = "id"
    permission_classes = [permissions.AllowAny]


# Список задач уровня
class TaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        level_id = self.kwargs.get("level_id")
        return Task.objects.filter(level_id=level_id).order_by("order")


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Room, RoomMember, RoomProgress, ChatMessage, RoomInvite

from .serializers import (
    RoomSerializer, RoomMemberSerializer, RoomProgressSerializer,
    ChatMessageSerializer, RoomInviteSerializer
)

User = get_user_model()


# Создать комнату
class CreateRoomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, level_id):
        level = get_object_or_404(Level, id=level_id)
        room = Room.objects.create(level=level, created_by=request.user)
        RoomMember.objects.create(room=room, user=request.user)

        first_task = level.tasks.order_by('order').first()
        RoomProgress.objects.create(room=room, current_task=first_task, task_index=0)

        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


# Играть в комнате (получить инфу)
class PlayRoomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        progress = room.progress
        members = room.members.all()
        messages_list = ChatMessage.objects.filter(room=room).order_by("timestamp")
        invites = RoomInvite.objects.filter(room=room, status="pending")

        data = {
            "room": RoomSerializer(room).data,
            "progress": RoomProgressSerializer(progress).data,
            "members": RoomMemberSerializer(members, many=True).data,
            "messages": ChatMessageSerializer(messages_list, many=True).data,
            "invites": RoomInviteSerializer(invites, many=True).data,
        }
        return Response(data)


# Ответ на задачу
class SubmitTaskAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        progress = room.progress
        code = request.data.get("code", "").strip()

        if not progress.current_task:
            return Response({"error": "Нет активной задачи"}, status=status.HTTP_400_BAD_REQUEST)

        if code == progress.current_task.correct_code:
            next_task = room.level.tasks.order_by("order")[progress.task_index + 1:progress.task_index + 2].first()
            if next_task:
                progress.current_task = next_task
                progress.task_index += 1
                progress.task_started_at = timezone.now()
            else:
                progress.completed = True
            progress.save()
            return Response(RoomProgressSerializer(progress).data)
        return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)


# Пригласить в комнату (ссылка)
class CreateRoomInviteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if room.created_by != request.user:
            return Response({"error": "Только владелец может создавать приглашения"}, status=status.HTTP_403_FORBIDDEN)

        RoomInvite.objects.filter(room=room, status="pending").delete()
        invite = RoomInvite.objects.create(room=room, sender=request.user)
        return Response(RoomInviteSerializer(invite).data)


# Присоединиться по ссылке
class JoinRoomByLinkAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        invite = get_object_or_404(RoomInvite, token=token)

        if invite.status != "pending":
            return Response({"error": "Ссылка уже использована или отклонена"}, status=status.HTTP_400_BAD_REQUEST)

        invite.accept(request.user)
        return Response({"success": f"Вы присоединились к комнате {invite.room.id}"})
