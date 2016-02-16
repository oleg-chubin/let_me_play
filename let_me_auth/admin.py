from django.contrib import admin

from let_me_auth.models import NotificationSettings, User


model_list = ( NotificationSettings, User)

for model in model_list:
    admin.site.register(model)
