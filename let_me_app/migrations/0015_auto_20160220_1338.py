# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def merge_staff(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    EventStaff = apps.get_model("let_me_app", "EventStaff")
    existing_staff = EventStaff.objects.all()
    Visit = apps.get_model("let_me_app", "Visit")
    VisitRole = apps.get_model("let_me_app", "VisitRole")
    for staff in existing_staff:
        visit, _ = Visit.objects.get_or_create(
            event_id=staff.event_id,
            user_id=staff.staff_id,
            status=2)
        VisitRole.objects.create(visit_id=visit.id, role_id=staff.role_id)


def create_staff_role(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    StaffRole = apps.get_model("let_me_app", "StaffRole")
    role, _ = StaffRole.objects.get_or_create(name="visitor")
    VisitRole = apps.get_model("let_me_app", "VisitRole")

    Visit = apps.get_model("let_me_app", "Visit")
    for visit in Visit.objects.all():
        VisitRole.objects.get_or_create(visit=visit, role=role)


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0014_auto_20160216_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('invoice', models.ForeignKey(verbose_name='invoice', null=True, blank=True, to='let_me_app.Invoice')),
                ('role', models.ForeignKey(verbose_name='role', to='let_me_app.StaffRole')),
                ('visit', models.ForeignKey(verbose_name='Visit', to='let_me_app.Visit')),
            ],
        ),
        migrations.AlterField(
            model_name='coachrecommendation',
            name='coach',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(create_staff_role),
        migrations.RunPython(merge_staff),
        migrations.AddField(
            model_name='activitytype',
            name='default_role',
            field=models.ForeignKey(to='let_me_app.StaffRole', default=1),
            preserve_default=False,
        ),

        migrations.DeleteModel(
            name='EventStaff',
        ),
        migrations.DeleteModel(
            name='StaffProfile',
        ),
    ]
