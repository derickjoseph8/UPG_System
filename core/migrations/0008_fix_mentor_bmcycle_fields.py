# Generated manually for fixing Mentor and BusinessMentorCycle model constraints

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_systemsettings'),
    ]

    operations = [
        # Fix Mentor model
        migrations.AlterField(
            model_name='mentor',
            name='office',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='mentor',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        # Fix BusinessMentorCycle model
        migrations.AlterField(
            model_name='businessmentorcycle',
            name='business_mentor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.mentor'),
        ),
        migrations.AlterField(
            model_name='businessmentorcycle',
            name='field_associate',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='businessmentorcycle',
            name='cycle',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='businessmentorcycle',
            name='project',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='businessmentorcycle',
            name='office',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
