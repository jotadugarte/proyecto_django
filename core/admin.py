from django.contrib import admin
from .models import GameSettings

@admin.register(GameSettings)
class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('building_growth_factor', 'production_speed_multiplier')
    
    def has_add_permission(self, request):
        # Prevent adding more than one instance since it's a singleton
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

# Register your models here.
