from django.urls import path
from .api_views import RegisterView, MeAPIView, FriendListAPIView,  LogoutAPIView, SearchUsersAPIView, AcceptFriendRequestAPIView,  DeclineFriendRequestAPIView, SendFriendRequestAPIView, FriendRequestsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeAPIView.as_view(), name="me"),
    path("friend-requests/", FriendRequestsView.as_view(), name="friend_requests"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("friends/", FriendListAPIView.as_view(), name="friend_list"),
    path("friends/send/<int:user_id>/", SendFriendRequestAPIView.as_view(), name="send_friend_request"),
    path("friends/accept/<int:request_id>/", AcceptFriendRequestAPIView.as_view(), name="accept_friend_request"),
    path("friends/decline/<int:request_id>/", DeclineFriendRequestAPIView.as_view(), name="decline_friend_request"),
    path("users/search/", SearchUsersAPIView.as_view(), name="search_users"),
]


