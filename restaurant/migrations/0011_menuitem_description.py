# Generated by Django 4.2.6 on 2024-08-20 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0010_order_item_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='description',
            field=models.CharField(db_index=True, default='No description', max_length=500),
        ),
    ]
