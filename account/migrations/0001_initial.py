# Generated by Django 4.2.2 on 2023-08-31 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
                ('image', models.IntegerField()),
                ('price_id', models.CharField(max_length=200)),
            ],
        ),
    ]
