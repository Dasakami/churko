from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
app_name = 'user'
urlpatterns = [
    path('register/', register, name='register' ),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='update_profile'),
        path('profile/<str:username>/', FriendProfileView.as_view(), name='friend_profile'),
    path('friends/', friend_list, name='friend_list'),
    path('requests/', friend_requests, name='friend_requests'),
    path('search/', search_users, name='search_users'),
    path('send_request/<int:user_id>', send_friend_request, name='send_request'),
    path('accept_request/<int:request_id>', accept_request, name='accept_request'),
    path('decline_request/<int:request_id>', decline_request, name='decline_request'),
    path('remove_friend/<slug:username>/', remove_friend, name='remove_friend')
]