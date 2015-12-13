from django.contrib import admin

from django.contrib import admin
from let_me_app.models import (InternalMessage, Peeper, PrivateComment,
    Changelog, Site, Court, Occasion, BookingPolicy, Invoice, InventoryList,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit,
    ChatParticipant, GalleryImage, ActivityType, StaffRole, EventStaff, StaffProfile)
from let_me_app import admin_forms


model_list = (InternalMessage, Peeper, PrivateComment, GalleryImage,
    Changelog, Court, Occasion, BookingPolicy, Invoice, ChatParticipant,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit, Site,
    ActivityType, StaffRole, EventStaff, StaffProfile
)

for model in model_list:
    admin.site.register(model)


class InlineInventory(admin.TabularInline):
    model = Inventory
    extra = 1


class InventoryListAdmin(admin.ModelAdmin):
    inlines = [InlineInventory]


admin.site.register(InventoryList, InventoryListAdmin)
