from django.urls import path
from .api_views import (
    CreateRoomAPIView, PlayRoomAPIView, SubmitTaskAPIView,
    CreateRoomInviteAPIView, JoinRoomByLinkAPIView
)

from django.urls import path
from .api_views import (
    DistrictListAPIView, LevelListAPIView, LevelDetailAPIView, TaskListAPIView
)

urlpatterns = [
    path("create/<int:level_id>/", CreateRoomAPIView.as_view(), name="create-room"),
    path("<int:room_id>/play/", PlayRoomAPIView.as_view(), name="play-room"),
    path("<int:room_id>/submit/", SubmitTaskAPIView.as_view(), name="submit-task"),
    path("<int:room_id>/invite/", CreateRoomInviteAPIView.as_view(), name="create-invite"),
    path("join/<uuid:token>/", JoinRoomByLinkAPIView.as_view(), name="join-room"),
     path("districts/", DistrictListAPIView.as_view(), name="districts-list"),
    path("districts/<int:district_id>/levels/", LevelListAPIView.as_view(), name="levels-by-district"),
    path("levels/<int:id>/", LevelDetailAPIView.as_view(), name="level-detail"),
    path("levels/<int:level_id>/tasks/", TaskListAPIView.as_view(), name="tasks-by-level"),

]


