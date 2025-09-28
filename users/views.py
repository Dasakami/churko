from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import FriendRequest, FriendShip
from django.views.generic import UpdateView, DetailView
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password  =  form.cleaned_data.get('password1')
            user = authenticate(username=username,password=raw_password)
            login(request,user)
            messages.success(request, f'Добро пожаловать, Искатель {username}!')
            return redirect('district_list')
    else:
        form= CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'user/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('district_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('district_list')
    else:
        form = CustomAuthenticationForm()
    context = {
        'form':form
    }
    return render(request, 'user/login.html', context)

def profile(request):
    profile = request.user
    experience_percentage = profile.get_experience_percentage()
    return render(request, 'user/profile.html', {'profile':profile, 'experience_percentage':experience_percentage})

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/update_profile.html'
    success_url = reverse_lazy('user:profile')

    def get_object(self, queryset=None):
        # Чтобы редактировать только свой профиль
        return self.request.user

class FriendProfileView(DetailView):
    model = User
    template_name = 'user/friend_profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        u = self.request.user

        # Проверка статуса дружбы
        status = None
        if u.is_authenticated and u != profile_user:
            if FriendShip.are_friends(u, profile_user):
                status = 'friends'
            elif FriendRequest.objects.filter(sender=u, receiver=profile_user, status='pending').exists():
                status = 'request_sent'
            elif FriendRequest.objects.filter(sender=profile_user, receiver=u, status='pending').exists():
                status = 'request_received'
        context['friendship_status'] = status

        # Данные для шаблона
        context['experience'] = profile_user.experience
        context['experience_needed'] = profile_user.experience_needed
        context['level'] = profile_user.level
        context['coins'] = profile_user.coins
        context['hints'] = profile_user.hints
        context['completed_levels'] = getattr(profile_user, 'completed_levels', 0)  # если есть
        context['experience_percentage'] = profile_user.get_experience_percentage()
        context['friends_count'] = FriendShip.objects.filter(   
            Q(user1=profile_user) | Q(user2=profile_user)
        ).count()
        context['achievements'] = profile_user.achievements.all()
        context['activity_logs'] = profile_user.activity_logs.all()[:5]

        return context

@login_required
def remove_friend(request, username):
    other_user = get_object_or_404(User, username=username)
    user = request.user

    # Ищем дружбу
    friendship = FriendShip.objects.filter(
        Q(user1=user, user2=other_user) | Q(user1=other_user, user2=user)
    ).first()

    if friendship:
        friendship.delete()

    return redirect('user:friend_list')

def friend_list(request):
    friendships = FriendShip.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    friends = []
    for friendship in friendships:
        friend = friendship.user2 if friendship.user1 == request.user else friendship.user1
        friends.append(friend)

    context = {
        'friends': friends
    }

    return render(request, 'friends/friends_list.html', context)


def send_friend_request(request, user_id):
    reciever_user = get_object_or_404(User, id=user_id)
    sender_user = request.user

    if FriendShip.are_friends(reciever_user, sender_user):
        messages.info(request,'Вы уже друзья')
        return redirect('user:friend_list')
    
    if FriendRequest.objects.filter(
        (Q(sender=sender_user, receiver=reciever_user) | Q(receiver=sender_user, sender=reciever_user)), status='pending'
    ).exists():
        messages.info('Заявка отправлена')
        return redirect('user:friend_list')
    
    FriendRequest.objects.create(sender=sender_user,  receiver=reciever_user)
    messages.success(request, 'Заявка отправлено!')
    return redirect('user:friend_list')

def accept_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
    friend_request.accept()
    messages.success(request,  f'{friend_request.sender.user.username} добавлен в друзья!')
    return redirect('user:friend_list')

def decline_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status='pending')
    friend_request.decline()
    messages.success(request,  'Заявка отклонена!')
    return redirect('user:friend_list')


def friend_requests(request):
    recieved_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status='pending'
    )
    sender_requests = FriendRequest.objects.filter(
        sender=request.user,
        status='pending'
    )

    context = {
        'recieved_requests': recieved_requests,
        'sender_requests':sender_requests
    }

    return render(request, 'friends/friend_requests.html', context)


def search_users(request):
    query = request.GET.get('q', '')
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
    else:
        users = []

    # pending заявки
    friend_requests = FriendRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & 
        Q(status='pending')
    )

    context = {
        'users': users,
        'friend_requests': friend_requests,
        'query': query,
    }

    return render(request, 'friends/search_users.html', context)