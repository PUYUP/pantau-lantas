from django.contrib import admin

# Register your models here.
from .models import PoliceNumber
from .models import Reported
from .models import Violation
from .models import Vehicle

# Extending list display
class ReportedDisplay(admin.ModelAdmin):
	""" Laporan """
	list_display = ("reporter", "violation", "police_number", "location", "date_created")
	list_filter = ("violation",)
	
	
class PoliceNumberDisplay(admin.ModelAdmin):
	""" Nomor polisi """
	list_display = ("reporter", "vehicle", "number", "date_created", "is_claimed")
	list_filter = ("vehicle",)


# Show to admin
admin.site.register(PoliceNumber, PoliceNumberDisplay)
admin.site.register(Reported, ReportedDisplay)
admin.site.register(Violation)
admin.site.register(Vehicle)