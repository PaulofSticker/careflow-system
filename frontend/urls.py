from django.urls import path
from .views import (
    dashboard,
    create_session,
    clients_list,
    client_detail,
    client_create,
    package_create,
    packages_list,
    sessions_list,
    installments_list,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('schedule/create/', create_session, name='create_session'),

    path('clients/', clients_list, name='clients_list'),
    path('clients/new/', client_create, name='client_create'),
    path('clients/<int:client_id>/package/new/', package_create, name='package_create'),
    path('clients/<int:client_id>/', client_detail, name='client_detail'),
    path('packages/', packages_list, name='packages_list'),
    path('sessions/', sessions_list, name='sessions_list'),
    path('installments/', installments_list, name='installments_list'),
]