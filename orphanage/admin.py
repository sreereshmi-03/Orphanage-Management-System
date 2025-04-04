from django.contrib import admin
from .models import User, Child, Caretaker, Donation, AdoptionRequest, Report

admin.site.register(User)
admin.site.register(Child)
admin.site.register(Caretaker)
admin.site.register(Donation)
admin.site.register(AdoptionRequest)
admin.site.register(Report)
