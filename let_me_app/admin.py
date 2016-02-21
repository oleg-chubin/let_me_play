from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin


from django.contrib import admin
from let_me_app.models import (InternalMessage, Peeper, PrivateComment,
    Changelog, Site, Court, Occasion, BookingPolicy, Invoice, InventoryList,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit,
    ChatParticipant, GalleryImage, ActivityType, StaffRole,
    VisitRole, IndexParametr, CoachRecommendation, VisitIndex)


model_list = (InternalMessage, Peeper, PrivateComment, GalleryImage,
    Changelog, Court, Occasion, BookingPolicy, Invoice, ChatParticipant,
    Event, Equipment, Inventory, Proposal, Application, Receipt, Visit,
    ActivityType, StaffRole, VisitRole, IndexParametr,
    CoachRecommendation, VisitIndex
)

for model in (Site,):
    admin.site.register(model, LeafletGeoAdmin)


for model in model_list:
    admin.site.register(model)


class InlineInventory(admin.TabularInline):
    model = Inventory
    extra = 1


class InventoryListAdmin(admin.ModelAdmin):
    inlines = [InlineInventory]


admin.site.register(InventoryList, InventoryListAdmin)
