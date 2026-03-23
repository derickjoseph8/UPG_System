# Generated migration for Ward model and Village update
# This adds the Ward model and updates Village to link to Ward instead of SubCounty

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_fix_mentor_bmcycle_fields'),
    ]

    operations = [
        # Create the Ward model
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subcounty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wards', to='core.subcounty')),
            ],
            options={
                'verbose_name_plural': 'Wards',
                'db_table': 'upg_wards',
                'unique_together': {('name', 'subcounty')},
            },
        ),
        # Add ward field to Village (nullable for backward compatibility)
        migrations.AddField(
            model_name='village',
            name='ward',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages', to='core.ward'),
        ),
        # Rename existing subcounty_obj field's related_name for legacy support
        migrations.AlterField(
            model_name='village',
            name='subcounty_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages_legacy', to='core.subcounty'),
        ),
    ]
