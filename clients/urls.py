from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page),

    path('dashboard/', views.dashboard),

    path('clients/', views.view_clients),

    path('add-client/', views.add_client),

    path(
        'edit-client/<str:id>/',
        views.edit_client
    ),

    path(
        'delete-client/<str:id>/',
        views.delete_client
    ),

    path(
        'users/',
        views.view_users
    ),

    path(
        'add-user/',
        views.add_user
    ),

    path(
        'delete-user/<str:id>/',
        views.delete_user
    ),
    path(
    'change-password/',
    views.change_password
),
    path(
    'domains/',
    views.domains
),
    path(
    'settings/',
    views.settings
),
    path(
        'logout/',
        views.logout
    ),
]