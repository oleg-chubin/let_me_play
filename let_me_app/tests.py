from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from let_me_app.persistence import get_my_chats
from let_me_auth.models import User
from let_me_app.models import InternalMessage, ChatParticipant


class TestChatList(TestCase):
    def test_get_for_anonymous(self):
        anonym = AnonymousUser()
        result = get_my_chats(anonym)
        self.assertEqual(list(result), [])

    def test_empty_chat_list(self):
        user = User.objects.create(email='some@ema.il')
        result = get_my_chats(user)
        self.assertEqual(list(result), [])

    def test_only_users_chats_returned(self):
        user = User.objects.create(email='some@ema.il')
        other_user = User.objects.create(email='other@ema.il')
        chat = InternalMessage.objects.create()
        ChatParticipant.objects.create(user=other_user, chat=chat)
        result = get_my_chats(user)
        self.assertEqual(list(result), [])

    def test_returned_chat_order(self):
        user = User.objects.create(email='some@ema.il')
        other_users = []
        for email in ['other1@ma.il', 'other2@ma.il', 'other3@ma.il']:
            other_users.append(
                User.objects.create(email=email)
            )

        chats = []
        for other_user in other_users:
            chat = InternalMessage.objects.create()
            chats.append(chat)
            ChatParticipant.objects.create(user=other_user, chat=chat)
            ChatParticipant.objects.create(user=user, chat=chat)

        for chat in reversed(chats):
            chat.save()

        result = get_my_chats(user)
        result = [
            [x.user.email for x in i.chatparticipant_set.all()] for i in result
        ]
        expected_result = [
            ['other3@ma.il', 'some@ema.il'],
            ['other2@ma.il', 'some@ema.il'],
            ['other1@ma.il', 'some@ema.il']
        ]
        self.assertEqual([sorted(i) for i in result], expected_result)