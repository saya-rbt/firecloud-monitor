# Generated by Django 3.0.1 on 2020-01-10 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_truck_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sensor',
            unique_together={('posx', 'posy')},
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='state',
        ),
    ]
