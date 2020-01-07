# Generated by Django 3.0.1 on 2020-01-07 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_truck_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fire',
            old_name='startDate',
            new_name='startdate',
        ),
        migrations.RemoveField(
            model_name='fire',
            name='position',
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='position',
        ),
        migrations.RemoveField(
            model_name='station',
            name='position',
        ),
        migrations.RemoveField(
            model_name='truck',
            name='position',
        ),
        migrations.AddField(
            model_name='fire',
            name='latitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fire',
            name='longitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensor',
            name='latitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensor',
            name='longitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensor',
            name='posx',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensor',
            name='posy',
            field=models.IntegerField(default=10.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='latitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='longitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='truck',
            name='latitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='truck',
            name='longitude',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
    ]