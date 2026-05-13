from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Town, Route, RouteStop, Schedule, Ticket


def search_routes(request):
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    travel_date_str = request.GET.get('date')

    if not (origin_id and destination_id and travel_date_str):
        return redirect('home')

    results = []
    origin_town = None
    destination_town = None

    try:
        selected_date = date.fromisoformat(travel_date_str)
        origin_town = get_object_or_404(Town, id=origin_id)
        destination_town = get_object_or_404(Town, id=destination_id)

        day_type_map = {0: 'weekday', 1: 'weekday', 2: 'weekday', 3: 'weekday', 4: 'weekday', 5: 'saturday', 6: 'sunday'}
        day_type = day_type_map[selected_date.weekday()]

        routes = Route.objects.filter(
            stops__town=origin_town
        ).filter(
            stops__town=destination_town
        ).distinct()

        for route in routes:
            route_stops = list(route.stops.all().select_related('town'))
            origin_stop = next((s for s in route_stops if s.town_id == origin_town.id), None)
            destination_stop = next((s for s in route_stops if s.town_id == destination_town.id), None)

            if origin_stop and destination_stop and origin_stop.order < destination_stop.order:
                price = destination_stop.price_from_origin - origin_stop.price_from_origin
                schedules = route.schedules.filter(day_type=day_type)

                for schedule in schedules:
                    results.append({
                        'route': route,
                        'schedule': schedule,
                        'origin_stop': origin_stop,
                        'destination_stop': destination_stop,
                        'price': price,
                        'origin_town': origin_town,
                        'destination_town': destination_town,
                    })

        results.sort(key=lambda r: r['schedule'].departure_time)

    except (ValueError, TypeError):
        pass

    return render(request, 'tickets/results.html', {
        'results': results,
        'search_origin': origin_town,
        'search_destination': destination_town,
        'search_date': travel_date_str,
    })


@login_required
def purchase(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        stop_id = request.POST.get('stop_id')
        travel_date_str = request.POST.get('travel_date')

        try:
            schedule = get_object_or_404(Schedule, id=schedule_id)
            drop_off_stop = get_object_or_404(RouteStop, id=stop_id)
            travel_date = date.fromisoformat(travel_date_str)

            last_ticket = Ticket.objects.order_by('id').last()
            next_num = (last_ticket.id + 1) if last_ticket else 1
            ticket_code = f"MGB-{next_num:06d}"

            ticket = Ticket.objects.create(
                user=request.user,
                schedule=schedule,
                drop_off_stop=drop_off_stop,
                travel_date=travel_date,
                ticket_code=ticket_code,
                price=drop_off_stop.price_from_origin,
                status='active',
            )

            messages.success(request, f'Pasaje {ticket_code} comprado exitosamente.')
            return redirect('dashboard')

        except (ValueError, TypeError):
            messages.error(request, 'Error al procesar la compra.')

    return redirect('home')


def cancel_ticket(request):
    if request.method == 'POST':
        ticket_code = request.POST.get('ticket_code', '').strip()

        try:
            ticket = Ticket.objects.get(ticket_code=ticket_code)
            if ticket.status == 'active':
                ticket.status = 'cancelled'
                ticket.save()
                messages.success(request, f'Pasaje {ticket_code} anulado exitosamente.')
            elif ticket.status == 'cancelled':
                messages.warning(request, f'El pasaje {ticket_code} ya estaba anulado.')
            else:
                messages.error(request, f'El pasaje {ticket_code} no se puede anular (estado: {ticket.get_status_display()}).')
        except Ticket.DoesNotExist:
            messages.error(request, f'No se encontró ningún pasaje con el código {ticket_code}.')

    return redirect('home')



