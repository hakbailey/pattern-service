from django.contrib import admin

from .models import Automation
from .models import ControllerLabel
from .models import Pattern
from .models import PatternInstance

# Register your models here.

admin.site.register(Pattern)
admin.site.register(ControllerLabel)
admin.site.register(PatternInstance)
admin.site.register(Automation)
