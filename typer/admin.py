from django.contrib import admin

from .models import Die, DieImage, TypedDie

admin.site.register(Die)
admin.site.register(DieImage)
admin.site.register(TypedDie)
