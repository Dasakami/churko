
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'quests.views.page_not_found'
handler500 = 'quests.views.server_error'
handler403 = 'quests.views.permission_denied'
handler400 = 'quests.views.bad_request'


urlpatterns = [
    path('sokka/', admin.site.urls),
    path('', include('quests.urls')),
    path('rooms/', include('rooms.urls')),
    path('user/', include('users.urls')),
    path('api/', include('rooms.api_urls')),
    path('api/auth/', include('users.api_urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
