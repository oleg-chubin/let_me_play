from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils import timezone


class AccountKitBackend(ModelBackend):
    def authenticate(self, cell_phone):
        UserModel = get_user_model()
        try:
            return UserModel._default_manager.get(cell_phone=cell_phone)
        except UserModel.DoesNotExist:
            return None


class NewcomerHashBackend(ModelBackend):
    def authenticate(self, newcomer_hash):
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(
                newcomer__code=newcomer_hash,
                newcomer__expired_at__gt=timezone.now())

        except UserModel.DoesNotExist:
            return None
        return user
