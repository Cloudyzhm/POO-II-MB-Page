from django.core.management.base import BaseCommand
from tickets.models import Town, Route, RouteStop, Schedule
import math


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos iniciales de rutas, paradas y horarios'

    def handle(self, *args, **options):
        self.stdout.write('Poblando datos...')

        towns_data = ['Concepción', 'Coelemu', 'Quirihue', 'Cobquecura', 'Buchupureo', 'Ñipas', 'Guarilihue']
        towns = {}
        for name in towns_data:
            town, _ = Town.objects.get_or_create(name=name)
            towns[name] = town
        self.stdout.write(f'  ✓ {len(towns)} localidades creadas')

        def create_route(name, stops_with_prices):
            route, _ = Route.objects.get_or_create(name=name)
            for i, (town_name, price) in enumerate(stops_with_prices, 1):
                RouteStop.objects.get_or_create(
                    route=route,
                    town=towns[town_name],
                    defaults={'order': i, 'price_from_origin': price}
                )
            return route

        create_route('Concepción → Coelemu', [
            ('Concepción', 0),
            ('Coelemu', 2500),
        ])

        create_route('Concepción → Coelemu → Quirihue', [
            ('Concepción', 0),
            ('Coelemu', 2500),
            ('Quirihue', 3500),
        ])

        create_route('Concepción → Coelemu → Ñipas', [
            ('Concepción', 0),
            ('Coelemu', 2500),
            ('Ñipas', 3000),
        ])

        create_route('Concepción → Coelemu → Guarilihue', [
            ('Concepción', 0),
            ('Coelemu', 2500),
            ('Guarilihue', 3000),
        ])

        create_route('Concepción → Coelemu → Quirihue → Cobquecura → Buchupureo', [
            ('Concepción', 0),
            ('Coelemu', 2500),
            ('Quirihue', 3500),
            ('Cobquecura', 5000),
            ('Buchupureo', 6000),
        ])

        create_route('Coelemu → Concepción', [
            ('Coelemu', 0),
            ('Concepción', 2500),
        ])

        create_route('Quirihue → Concepción', [
            ('Quirihue', 0),
            ('Coelemu', 1500),
            ('Concepción', 3500),
        ])

        create_route('Guarilihue → Concepción', [
            ('Guarilihue', 0),
            ('Coelemu', 800),
            ('Concepción', 3000),
        ])

        create_route('Ñipas → Concepción', [
            ('Ñipas', 0),
            ('Coelemu', 1000),
            ('Concepción', 3000),
        ])

        create_route('Buchupureo → Concepción', [
            ('Buchupureo', 0),
            ('Cobquecura', 1500),
            ('Quirihue', 3000),
            ('Coelemu', 4000),
            ('Concepción', 6000),
        ])

        create_route('Cobquecura → Concepción', [
            ('Cobquecura', 0),
            ('Quirihue', 1500),
            ('Coelemu', 3000),
            ('Concepción', 5000),
        ])

        self.stdout.write(f'  ✓ {Route.objects.count()} rutas creadas')
        self.stdout.write(f'  ✓ {RouteStop.objects.count()} paradas creadas')

        route_map = {}
        for r in Route.objects.all():
            route_map[r.name] = r

        def add_schedule(route_name, day_type, times):
            route = route_map[route_name]
            for time_str in times:
                h, m = map(int, time_str.split(':'))
                Schedule.objects.get_or_create(
                    route=route,
                    day_type=day_type,
                    departure_time=f'{h:02d}:{m:02d}:00',
                )

        add_schedule('Concepción → Coelemu', 'weekday', [
            '07:00', '08:40', '09:35', '17:00', '17:30', '19:30', '20:30'
        ])
        add_schedule('Concepción → Coelemu', 'saturday', ['19:30'])
        add_schedule('Concepción → Coelemu', 'sunday', ['19:30', '20:15'])

        add_schedule('Concepción → Coelemu → Quirihue', 'weekday', [
            '06:40', '08:10', '10:00', '10:40', '14:30', '16:30'
        ])
        add_schedule('Concepción → Coelemu → Quirihue', 'saturday', [
            '08:30', '09:35', '14:30', '16:30', '18:30'
        ])
        add_schedule('Concepción → Coelemu → Quirihue', 'sunday', [
            '09:00', '14:30', '16:30'
        ])

        add_schedule('Concepción → Coelemu → Ñipas', 'weekday', [
            '12:30', '18:00'
        ])
        add_schedule('Concepción → Coelemu → Ñipas', 'saturday', ['12:30', '17:30'])
        add_schedule('Concepción → Coelemu → Ñipas', 'sunday', ['16:30'])

        add_schedule('Concepción → Coelemu → Guarilihue', 'weekday', ['13:30', '15:30'])
        add_schedule('Concepción → Coelemu → Guarilihue', 'saturday', ['13:30'])

        add_schedule('Concepción → Coelemu → Quirihue → Cobquecura → Buchupureo', 'weekday', ['18:30'])
        add_schedule('Concepción → Coelemu → Quirihue → Cobquecura → Buchupureo', 'saturday', ['10:40'])
        add_schedule('Concepción → Coelemu → Quirihue → Cobquecura → Buchupureo', 'sunday', ['10:40', '18:30'])

        add_schedule('Coelemu → Concepción', 'weekday', [
            '06:10', '06:25', '06:40', '07:00', '07:20', '08:30', '09:00', '09:30',
            '10:30', '11:30', '12:25', '13:40', '14:25', '15:25', '16:25', '17:10',
            '18:25', '20:10'
        ])
        add_schedule('Coelemu → Concepción', 'saturday', [
            '07:20', '08:30', '09:30', '10:30', '12:25', '14:25', '15:25',
            '16:30', '17:10', '18:25'
        ])
        add_schedule('Coelemu → Concepción', 'sunday', [
            '08:30', '12:25', '14:25', '17:10', '18:00', '19:00', '20:10'
        ])

        add_schedule('Quirihue → Concepción', 'weekday', [
            '06:40', '08:40', '11:20', '13:00', '16:10', '17:10', '19:00'
        ])
        add_schedule('Quirihue → Concepción', 'saturday', [
            '06:40', '11:20', '13:00', '16:10', '17:10'
        ])
        add_schedule('Quirihue → Concepción', 'sunday', [
            '11:20', '16:10', '17:10', '19:00'
        ])

        add_schedule('Guarilihue → Concepción', 'weekday', ['09:30', '15:30'])
        add_schedule('Guarilihue → Concepción', 'saturday', ['09:30', '15:30'])

        add_schedule('Ñipas → Concepción', 'weekday', ['12:00', '14:40'])
        add_schedule('Ñipas → Concepción', 'saturday', ['14:40'])
        add_schedule('Ñipas → Concepción', 'sunday', ['18:20'])

        add_schedule('Buchupureo → Concepción', 'weekday', ['05:45', '15:00'])
        add_schedule('Buchupureo → Concepción', 'saturday', ['05:45', '15:00'])
        add_schedule('Buchupureo → Concepción', 'sunday', ['15:00'])

        add_schedule('Cobquecura → Concepción', 'weekday', ['06:00', '15:15'])
        add_schedule('Cobquecura → Concepción', 'saturday', ['06:00', '15:15'])
        add_schedule('Cobquecura → Concepción', 'sunday', ['15:15'])

        self.stdout.write(f'  ✓ {Schedule.objects.count()} horarios creados')

        self.stdout.write(self.style.SUCCESS('Datos poblados exitosamente.'))
