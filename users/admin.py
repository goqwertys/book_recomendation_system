from django.contrib import admin

from interactions.models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'timestamp')
    list_filter = ('rating', )
    search_fields = ('user__username', 'book__title')
    ordering = ('-timestamp',)
