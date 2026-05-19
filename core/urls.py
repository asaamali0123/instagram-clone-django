from django.urls import path
from posts import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_user, name='search'),
    path('upload', views.upload, name='upload'),
    path('like-post', views.like_post, name='like-post'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('settings', views.settings, name='settings'), # Matches the renamed view below
    path('delete-post/<uuid:post_id>', views.delete_post, name='delete-post'),
    path('edit-post', views.edit_post, name='edit-post'),
    path('post-comment', views.post_comment, name='post-comment'),
    path('explore', views.explore, name='explore'),
    path('reels/', views.reels, name='reels'),
     # ADD THIS LINE BELOW TO FIX THE 404 ERROR
    path('follow', views.follow, name='follow'),
    path('messages/', views.messenger, name='messenger'),
    path('messages/<str:username>/', views.messenger, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('send-message/', views.send_message, name='send_message'),
    path('notifications/', views.notifications, name='notifications'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)