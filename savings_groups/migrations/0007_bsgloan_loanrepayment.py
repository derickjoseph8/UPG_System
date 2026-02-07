# Generated migration for BSGLoan and LoanRepayment models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('savings_groups', '0006_add_created_by_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='BSGLoan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_amount', models.DecimalField(decimal_places=2, help_text='Amount borrowed', max_digits=10)),
                ('interest_rate', models.DecimalField(decimal_places=2, default=10.0, help_text='Interest rate in percentage', max_digits=5)),
                ('total_due', models.DecimalField(decimal_places=2, default=0, help_text='Principal + Interest', max_digits=10)),
                ('amount_repaid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('loan_date', models.DateField(help_text='Date loan was issued')),
                ('due_date', models.DateField(help_text='Date loan should be fully repaid')),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('disbursed', 'Disbursed'), ('partially_repaid', 'Partially Repaid'), ('fully_repaid', 'Fully Repaid'), ('defaulted', 'Defaulted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('purpose', models.TextField(blank=True, help_text='Reason for taking the loan')),
                ('approved_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_bsg_loans', to=settings.AUTH_USER_MODEL)),
                ('bsg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='savings_groups.businesssavingsgroup')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='savings_groups.bsgmember')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_bsg_loans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'upg_bsg_loans',
                'ordering': ['-loan_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LoanRepayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('repayment_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repayments', to='savings_groups.bsgloan')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'upg_loan_repayments',
                'ordering': ['-repayment_date', '-created_at'],
            },
        ),
    ]
