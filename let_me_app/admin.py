from django.contrib import admin

from django.contrib import admin
from let_me_app.models import (InternalMessage, Peeper, PrivateComment,
    Changelog, Site, Court, Occasion, BookingPolicy, Invoice, InventoryList,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit, ChatParticipant)


model_list = (InternalMessage, Peeper, PrivateComment,
    Changelog, Site, Court, Occasion, BookingPolicy, Invoice, ChatParticipant,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit
)

for model in model_list:
    admin.site.register(model)


class InlineInventory(admin.TabularInline):
    model = Inventory
    extra = 1


class InventoryListAdmin(admin.ModelAdmin):
    inlines = [InlineInventory]


admin.site.register(InventoryList, InventoryListAdmin)