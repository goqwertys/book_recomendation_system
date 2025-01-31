from django.contrib import admin

from interactions.models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'viewed', 'timestamp')
    list_filter = ('viewed', 'rating')
    search_fields = ('user__username', 'book__title')
    ordering = ('-timestamp',)
