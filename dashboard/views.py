from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from tickets.models import Ticket, Route, RouteStop, Schedule, Town
from .forms import RouteForm, ScheduleForm


@login_required
def home(request):
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'schedule__route', 'drop_off_stop__town'
    ).order_by('travel_date')

    active_tickets = tickets.filter(status='active')
    upcoming_tickets = active_tickets.filter(travel_date__gte=date.today())
    used_count = tickets.filter(status='used').count()
    cancelled_count = tickets.filter(status='cancelled').count()

    context = {
        'tickets': tickets,
        'upcoming_tickets': upcoming_tickets,
        'active_count': active_tickets.count(),
        'used_count': used_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'dashboard/home.html', context)


def company_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.user_type not in ('company', 'admin'):
            messages.error(request, 'Acceso solo para cuentas empresa.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@company_required
def company_dashboard(request):
    routes = Route.objects.annotate(stop_count=Count('stops')).prefetch_related('stops__town').order_by('name')
    tickets = Ticket.objects.select_related('user', 'schedule__route', 'drop_off_stop__town').order_by('-purchase_date')
    all_towns = Town.objects.all()

    total_routes = routes.count()
    total_schedules = Schedule.objects.count()
    active_tickets = tickets.filter(status='active').count()
    towns_count = all_towns.count()

    active_route = None
    edit_route = None
    edit_stop = None
    edit_schedule_obj = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_route':
            route_id = request.POST.get('route_id')
            description = request.POST.get('description', '').strip()
            if route_id:
                route = get_object_or_404(Route, id=route_id)
                route.name = description or route.name
                route.description = description
                route.save()
                messages.success(request, f'Viaje actualizado.')
            else:
                name = description or f"Viaje #{Route.objects.count() + 1}"
                route = Route.objects.create(name=name, description=description)
                messages.success(request, f'Viaje creado.')
            return redirect(f"{reverse('company_dashboard')}?tab=viajes&viaje_id={route.id}")

        elif action == 'save_stop':
            route_id = request.POST.get('route_id')
            stop_id = request.POST.get('stop_id')
            town_name = request.POST.get('town_name', '').strip()
            order = request.POST.get('order')
            price = request.POST.get('price_from_origin', 0)
            route = get_object_or_404(Route, id=route_id)

            if not town_name:
                messages.error(request, 'Debes indicar una localidad.')
            else:
                town, _ = Town.objects.get_or_create(name=town_name)
                if stop_id:
                    stop = get_object_or_404(RouteStop, id=stop_id)
                    stop.town = town
                    stop.order = order
                    stop.price_from_origin = price
                    stop.save()
                    messages.success(request, 'Parada actualizada.')
                else:
                    RouteStop.objects.create(route=route, town=town, order=order, price_from_origin=price)
                    messages.success(request, 'Parada agregada.')
            return redirect(f"{reverse('company_dashboard')}?tab=viajes&viaje_id={route_id}")

        elif action == 'save_schedule':
            route_id = request.POST.get('route_id')
            schedule_id = request.POST.get('schedule_id')
            day_type = request.POST.get('day_type')
            departure_time = request.POST.get('departure_time')
            route = get_object_or_404(Route, id=route_id)
            if schedule_id:
                schedule = get_object_or_404(Schedule, id=schedule_id)
                schedule.day_type = day_type
                schedule.departure_time = departure_time
                schedule.save()
                messages.success(request, 'Horario actualizado.')
            else:
                Schedule.objects.create(route=route, day_type=day_type, departure_time=departure_time)
                messages.success(request, 'Horario creado.')
            return redirect(f"{reverse('company_dashboard')}?tab=viajes&viaje_id={route_id}")

    viaje_id = request.GET.get('viaje_id')
    if viaje_id:
        active_route = get_object_or_404(
            Route.objects.prefetch_related('stops__town', 'schedules'), id=viaje_id
        )

    edit_route_id = request.GET.get('edit_route')
    edit_stop_id = request.GET.get('edit_stop')
    edit_sched_id = request.GET.get('edit_schedule')

    if edit_route_id:
        edit_route = get_object_or_404(Route, id=edit_route_id)
    if edit_stop_id and active_route:
        edit_stop = get_object_or_404(RouteStop, id=edit_stop_id)
    if edit_sched_id and active_route:
        edit_schedule_obj = get_object_or_404(Schedule, id=edit_sched_id)

    context = {
        'total_routes': total_routes,
        'total_schedules': total_schedules,
        'active_tickets': active_tickets,
        'towns_count': towns_count,
        'routes': routes,
        'tickets': tickets,
        'all_towns': all_towns,
        'active_route': active_route,
        'edit_route': edit_route,
        'edit_stop': edit_stop,
        'edit_schedule': edit_schedule_obj,
    }
    return render(request, 'dashboard/company.html', context)


@company_required
def manage_towns(request):
    towns = Town.objects.all()

    if request.method == 'POST':
        town_id = request.POST.get('town_id')
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'El nombre de la localidad no puede estar vacío.')
        elif town_id:
            town = get_object_or_404(Town, id=town_id)
            town.name = name
            town.save()
            messages.success(request, f'Localidad "{name}" actualizada.')
        else:
            if Town.objects.filter(name__iexact=name).exists():
                messages.error(request, f'La localidad "{name}" ya existe.')
            else:
                Town.objects.create(name=name)
                messages.success(request, f'Localidad "{name}" creada.')

        return redirect(f"{reverse('company_dashboard')}?tab=viajes")

    edit_id = request.GET.get('edit')
    edit_town = get_object_or_404(Town, id=edit_id) if edit_id else None

    context = {
        'towns': towns,
        'edit_town': edit_town,
    }
    return render(request, 'dashboard/towns/list.html', context)


@company_required
def delete_town(request, town_id):
    town = get_object_or_404(Town, id=town_id)
    if RouteStop.objects.filter(town=town).exists():
        messages.error(request, f'No se puede eliminar "{town.name}" porque tiene paradas asociadas.')
    else:
        town.delete()
        messages.success(request, f'Localidad "{town.name}" eliminada.')
    return redirect(f"{reverse('company_dashboard')}?tab=viajes")


@company_required
def manage_trips(request):
    routes = Route.objects.annotate(stop_count=Count('stops')).order_by('name')

    if request.method == 'POST':
        route_id = request.POST.get('route_id')
        description = request.POST.get('description', '').strip()

        if route_id:
            route = get_object_or_404(Route, id=route_id)
            route.name = description or route.name
            route.description = description
            route.save()
            messages.success(request, 'Viaje actualizado.')
        else:
            name = description or f"Viaje #{Route.objects.count() + 1}"
            Route.objects.create(name=name, description=description)
            messages.success(request, 'Viaje creado.')

        return redirect(f"{reverse('company_dashboard')}?tab=viajes")

    edit_route = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_route = get_object_or_404(Route, id=edit_id)

    context = {
        'routes': routes,
        'edit_route': edit_route,
    }
    return render(request, 'dashboard/trips/list.html', context)


@company_required
def manage_routes(request):
    routes = Route.objects.annotate(stop_count=Count('stops')).order_by('name')

    if request.method == 'POST':
        route_id = request.POST.get('route_id')
        description = request.POST.get('description', '').strip()

        if route_id:
            route = get_object_or_404(Route, id=route_id)
            route.name = description or route.name
            route.description = description
            route.save()
            messages.success(request, 'Ruta actualizada.')
        else:
            name = description or f"Ruta #{Route.objects.count() + 1}"
            Route.objects.create(name=name, description=description)
            messages.success(request, 'Ruta creada.')

        return redirect(f"{reverse('company_dashboard')}?tab=viajes")

    edit_route = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_route = get_object_or_404(Route, id=edit_id)

    context = {
        'routes': routes,
        'edit_route': edit_route,
    }
    return render(request, 'dashboard/routes/list.html', context)


@company_required
def delete_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    route.delete()
    messages.success(request, f'Viaje "{route.name}" eliminado.')
    return redirect(f"{reverse('company_dashboard')}?tab=viajes")


@company_required
def manage_stops(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    stops = route.stops.all().select_related('town').order_by('order')

    if request.method == 'POST':
        stop_id = request.POST.get('stop_id')
        town_id = request.POST.get('town')
        order = request.POST.get('order')
        price = request.POST.get('price_from_origin')

        town = get_object_or_404(Town, id=town_id)

        if stop_id:
            stop = get_object_or_404(RouteStop, id=stop_id)
            stop.town = town
            stop.order = order
            stop.price_from_origin = price
            stop.save()
            messages.success(request, 'Parada actualizada.')
        else:
            RouteStop.objects.create(
                route=route, town=town, order=order, price_from_origin=price
            )
            messages.success(request, 'Parada agregada.')

        return redirect(f"{reverse('company_dashboard')}?tab=viajes")

    all_towns = Town.objects.all()
    edit_stop_id = request.GET.get('edit')
    edit_stop = get_object_or_404(RouteStop, id=edit_stop_id) if edit_stop_id else None

    context = {
        'route': route,
        'stops': stops,
        'all_towns': all_towns,
        'edit_stop': edit_stop,
    }
    return render(request, 'dashboard/trips/stops.html', context)


@company_required
def delete_stop(request, stop_id):
    stop = get_object_or_404(RouteStop, id=stop_id)
    route_id = stop.route.id
    stop.delete()
    messages.success(request, 'Parada eliminada.')
    return redirect(f"{reverse('company_dashboard')}?tab=viajes&viaje_id={route_id}")


@company_required
def manage_schedules(request):
    schedules = Schedule.objects.select_related('route').order_by('route__name', 'day_type', 'departure_time')

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        route_id = request.POST.get('route')
        day_type = request.POST.get('day_type')
        departure_time = request.POST.get('departure_time')

        route = get_object_or_404(Route, id=route_id)

        if schedule_id:
            schedule = get_object_or_404(Schedule, id=schedule_id)
            schedule.route = route
            schedule.day_type = day_type
            schedule.departure_time = departure_time
            schedule.save()
            messages.success(request, 'Horario actualizado.')
        else:
            Schedule.objects.create(route=route, day_type=day_type, departure_time=departure_time)
            messages.success(request, 'Horario creado.')

    return redirect(f"{reverse('company_dashboard')}?tab=viajes")

    routes = Route.objects.all()
    edit_id = request.GET.get('edit')
    edit_schedule = get_object_or_404(Schedule, id=edit_id) if edit_id else None

    context = {
        'schedules': schedules,
        'routes': routes,
        'edit_schedule': edit_schedule,
    }
    return render(request, 'dashboard/schedules/list.html', context)


@company_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.delete()
    messages.success(request, 'Horario eliminado.')
    return redirect(f"{reverse('company_dashboard')}?tab=viajes")


@company_required
def company_tickets(request):
    tickets = Ticket.objects.select_related(
        'user', 'schedule__route', 'drop_off_stop__town'
    ).order_by('-purchase_date')

    context = {'tickets': tickets}
    return render(request, 'dashboard/tickets/list.html', context)


@company_required
def mark_ticket_used(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.status == 'active':
        ticket.status = 'used'
        ticket.save()
        messages.success(request, f'Pasaje {ticket.ticket_code} marcado como usado.')
    return redirect(f"{reverse('company_dashboard')}?tab=pasajes")
