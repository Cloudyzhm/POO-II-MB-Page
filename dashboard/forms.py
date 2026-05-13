from django import forms
from tickets.models import Route, RouteStop, Schedule, Town


class TownForm(forms.ModelForm):
    class Meta:
        model = Town
        fields = ('name',)


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ('name', 'description')


class RouteStopForm(forms.ModelForm):
    class Meta:
        model = RouteStop
        fields = ('route', 'town', 'order', 'price_from_origin')


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('route', 'day_type', 'departure_time')
        widgets = {
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
        }
