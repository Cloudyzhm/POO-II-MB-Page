from django.contrib import admin
from .models import Town, Route, RouteStop, Schedule, Ticket


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'destination')
    inlines = [RouteStopInline, ScheduleInline]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'town', 'order', 'price_from_origin')
    list_filter = ('route',)
    search_fields = ('town__name',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'day_type', 'departure_time')
    list_filter = ('day_type', 'route')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'travel_date', 'status', 'price')
    list_filter = ('status', 'travel_date')
    search_fields = ('ticket_code', 'user__username')



