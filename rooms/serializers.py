from rest_framework import serializers
from .models import Room, RoomMember, RoomProgress, ChatMessage, RoomInvite
from quests.models import Task, Level, District
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
User = get_user_model()





class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name", "slug", "image", "is_active"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "order", "text", "correct_code", "time_limit"]


class LevelSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Level
        fields = [
            "id", "name", "slug", "description", "status",
            "difficulty", "district", "is_active", "total_time", "tasks"
        ]




class RoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ["id", "level", "created_by", "created_at", "is_active", "invite_code"]


class RoomMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoomMember
        fields = ["id", "user", "room"]




class RoomProgressSerializer(serializers.ModelSerializer):
    current_task = TaskSerializer(read_only=True)

    class Meta:
        model = RoomProgress
        fields = [
            "id", "room", "current_task", "task_index",
            "completed", "started_at", "task_started_at",
            "level_time_limit", "task_time_limit",
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "user", "message", "timestamp"]


class RoomInviteSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = RoomInvite
        fields = ["id", "room", "sender", "receiver_email", "token", "status", "created_at"]
