# Generated by Django 4.2.3 on 2023-11-09 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execrise_type', models.CharField(max_length=255)),
                ('execrise_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'home_execrise',
            },
        ),
    ]
