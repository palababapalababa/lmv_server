# Generated by Django 5.0.3 on 2024-05-13 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DialogflowApp', '0003_remove_player_assists_per_game_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='api_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='id for api identification'),
        ),
        migrations.AlterField(
            model_name='game',
            name='mvp_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='DialogflowApp.player', verbose_name='MVP of the game'),
        ),
        migrations.AlterField(
            model_name='player',
            name='api_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='id for api identification'),
        ),
        migrations.AlterField(
            model_name='player',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name="player's birth date"),
        ),
        migrations.AlterField(
            model_name='player',
            name='citizenship',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="player's citizenship"),
        ),
        migrations.AlterField(
            model_name='player',
            name='height_feet',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="player's height, feet part"),
        ),
        migrations.AlterField(
            model_name='player',
            name='height_inches',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="player's height, inches part"),
        ),
        migrations.AlterField(
            model_name='player',
            name='height_meters',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="player's height in meters"),
        ),
        migrations.AlterField(
            model_name='player',
            name='team_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='DialogflowApp.team', verbose_name="player's team"),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight_kilograms',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="player's weight in kilograms"),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight_pounds',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="player's weight in pounds"),
        ),
        migrations.AlterField(
            model_name='team',
            name='api_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='id for api identification'),
        ),
    ]
