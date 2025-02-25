from django.contrib import admin

from .models import Driver
from .models import Trip
from .models import SharePart

admin.site.register(Driver)
admin.site.register(Trip)
admin.site.register(SharePart)
