# Generated by Django 5.0.3 on 2024-05-12 11:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DialogflowApp', '0002_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='assists_per_game',
        ),
        migrations.RemoveField(
            model_name='player',
            name='field_goal_pct',
        ),
        migrations.RemoveField(
            model_name='player',
            name='games_played',
        ),
        migrations.RemoveField(
            model_name='player',
            name='minutes_per_game',
        ),
        migrations.RemoveField(
            model_name='player',
            name='points_per_game',
        ),
        migrations.RemoveField(
            model_name='player',
            name='rebounds_per_game',
        ),
        migrations.RemoveField(
            model_name='player',
            name='three_point_pct',
        ),
        migrations.AddField(
            model_name='game',
            name='api_id',
            field=models.IntegerField(null=True, verbose_name='id for api identification'),
        ),
        migrations.AddField(
            model_name='player',
            name='api_id',
            field=models.IntegerField(null=True, verbose_name='id for api identification'),
        ),
        migrations.AddField(
            model_name='player',
            name='birth_date',
            field=models.DateField(null=True, verbose_name="player's birth date"),
        ),
        migrations.AddField(
            model_name='player',
            name='citizenship',
            field=models.CharField(max_length=255, null=True, verbose_name="player's citizenship"),
        ),
        migrations.AddField(
            model_name='player',
            name='height_feet',
            field=models.CharField(max_length=10, null=True, verbose_name="player's height, feet part"),
        ),
        migrations.AddField(
            model_name='player',
            name='height_inches',
            field=models.CharField(max_length=10, null=True, verbose_name="player's height, inches part"),
        ),
        migrations.AddField(
            model_name='player',
            name='height_meters',
            field=models.CharField(max_length=10, null=True, verbose_name="player's height in meters"),
        ),
        migrations.AddField(
            model_name='player',
            name='weight_kilograms',
            field=models.CharField(max_length=10, null=True, verbose_name="player's weight in kilograms"),
        ),
        migrations.AddField(
            model_name='player',
            name='weight_pounds',
            field=models.CharField(max_length=10, null=True, verbose_name="player's weight in pounds"),
        ),
        migrations.AddField(
            model_name='team',
            name='api_id',
            field=models.IntegerField(null=True, verbose_name='id for api identification'),
        ),
        migrations.CreateModel(
            name='PlayerStatisticPerGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.IntegerField(verbose_name='id for api identification')),
                ('scored_points', models.IntegerField(verbose_name='amount of scored points')),
                ('minutes_on_field', models.CharField(max_length=10, verbose_name='players time on field')),
                ('position', models.CharField(max_length=10, verbose_name="player's position")),
                ('fgm', models.IntegerField(verbose_name='field goal made')),
                ('fga', models.IntegerField(verbose_name='field goal attempts')),
                ('fgp', models.CharField(max_length=10, verbose_name='field goal percentage')),
                ('ftm', models.IntegerField(verbose_name='field throw made')),
                ('fta', models.IntegerField(verbose_name='field throw attempts')),
                ('ftp', models.CharField(max_length=10, verbose_name='field throw percentage')),
                ('tpm', models.IntegerField(verbose_name='three points made')),
                ('tpa', models.IntegerField(verbose_name='three points attempts')),
                ('tpp', models.CharField(max_length=10, verbose_name='three points percentage')),
                ('offReb', models.IntegerField(verbose_name='offensive rebounds')),
                ('defReb', models.IntegerField(verbose_name='defensive rebounds')),
                ('totReb', models.IntegerField(verbose_name='total rebounds')),
                ('assists', models.IntegerField(verbose_name='total assists')),
                ('pFoulds', models.IntegerField(verbose_name='personal fouls')),
                ('steals', models.IntegerField(verbose_name='steals')),
                ('turnovers', models.IntegerField(verbose_name='turnovers')),
                ('blocks', models.IntegerField(verbose_name='blocks')),
                ('game_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DialogflowApp.game', verbose_name='game id')),
                ('player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DialogflowApp.player', verbose_name='player id')),
            ],
        ),
    ]