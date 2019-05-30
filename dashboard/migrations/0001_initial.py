# Generated by Django 2.2 on 2019-05-30 17:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Politician',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('pre_name', models.CharField(max_length=30)),
                ('faction', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('voting_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField()),
                ('genre', models.CharField(max_length=30)),
                ('topic', models.TextField(default='')),
                ('description', models.TextField()),
                ('votes', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IndividualVoting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voting_id', models.IntegerField()),
                ('vote', models.IntegerField(null=True)),
                ('individual_voting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Voting')),
                ('politicians', models.ManyToManyField(to='dashboard.Politician')),
            ],
        ),
    ]
