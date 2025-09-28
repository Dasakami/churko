from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, FriendRequest, FriendShip
from .serializers import UserSerializer, RegisterSerializer, FriendRequestSerializer,  FriendShipSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Регистрация
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# Список запросов в друзья
class FriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, status='pending')




# Получить текущего пользователя
class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# Logout
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # JWT можно просто игнорировать на клиенте, или реализовать blacklist
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

# Список друзей
class FriendListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        friendships = FriendShip.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        serializer = FriendShipSerializer(friendships, many=True)
        return Response(serializer.data)

# Отправка запроса в друзья
class SendFriendRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        receiver = get_object_or_404(User, id=user_id)
        sender = request.user

        if FriendShip.are_friends(sender, receiver):
            return Response({"detail": "Вы уже друзья"}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(
            (Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)),
            status='pending'
        ).exists():
            return Response({"detail": "Заявка уже отправлена"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

# Принять запрос
class AcceptFriendRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.accept()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

# Отклонить запрос
class DeclineFriendRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
        friend_request.decline()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

# Поиск пользователей
class SearchUsersAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
