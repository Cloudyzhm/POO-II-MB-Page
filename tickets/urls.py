from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_routes, name='search_routes'),
    path('purchase/', views.purchase, name='purchase'),
    path('cancel/', views.cancel_ticket, name='cancel_ticket'),

]
