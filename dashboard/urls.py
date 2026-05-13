from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    path('empresa/', views.company_dashboard, name='company_dashboard'),
    path('empresa/localidades/', views.manage_towns, name='manage_towns'),
    path('empresa/localidades/<int:town_id>/eliminar/', views.delete_town, name='delete_town'),
    path('empresa/viajes/', views.manage_trips, name='manage_trips'),
    path('empresa/rutas/', views.manage_routes, name='manage_routes'),
    path('empresa/rutas/<int:route_id>/eliminar/', views.delete_route, name='delete_route'),
    path('empresa/rutas/<int:route_id>/paradas/', views.manage_stops, name='manage_stops'),
    path('empresa/paradas/<int:stop_id>/eliminar/', views.delete_stop, name='delete_stop'),
    path('empresa/horarios/', views.manage_schedules, name='manage_schedules'),
    path('empresa/horarios/<int:schedule_id>/eliminar/', views.delete_schedule, name='delete_schedule'),
    path('empresa/pasajes/', views.company_tickets, name='company_tickets'),
    path('empresa/pasajes/<int:ticket_id>/usado/', views.mark_ticket_used, name='mark_ticket_used'),
]
