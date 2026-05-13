from django.db import models
from django.conf import settings


class Town(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Route(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def origin(self):
        return self.stops.first().town if self.stops.exists() else None

    def destination(self):
        return self.stops.last().town if self.stops.exists() else None


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    price_from_origin = models.PositiveIntegerField(help_text="Precio acumulado desde el origen en pesos")

    class Meta:
        ordering = ['route', 'order']
        unique_together = ['route', 'town']

    def __str__(self):
        return f"{self.route.name} → {self.town.name} (${self.price_from_origin:,})"


class Schedule(models.Model):
    DAY_CHOICES = [
        ('weekday', 'Lunes a Viernes'),
        ('saturday', 'Sábado'),
        ('sunday', 'Domingo'),
    ]
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    day_type = models.CharField(max_length=10, choices=DAY_CHOICES)
    departure_time = models.TimeField()

    class Meta:
        ordering = ['route', 'day_type', 'departure_time']

    def __str__(self):
        return f"{self.route.name} - {self.get_day_type_display()} {self.departure_time.strftime('%H:%M')}"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('cancelled', 'Anulado'),
        ('used', 'Usado'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT)
    drop_off_stop = models.ForeignKey(RouteStop, on_delete=models.PROTECT)
    travel_date = models.DateField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    ticket_code = models.CharField(max_length=20, unique=True)
    price = models.PositiveIntegerField()

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.ticket_code} - {self.user.username}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(help_text="Porcentaje de descuento (0-100)")
    valid_from = models.DateField()
    valid_until = models.DateField()
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
