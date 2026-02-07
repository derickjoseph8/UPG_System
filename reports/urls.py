from django.urls import path
from . import views
from . import excel_views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),

    # Download Reports (CSV)
    path('download/households/', views.download_household_report, name='download_household_report'),
    path('download/ppi/', views.download_ppi_report, name='download_ppi_report'),
    path('download/program-participation/', views.download_program_participation_report, name='download_program_participation_report'),
    path('download/business-groups/', views.download_business_groups_report, name='download_business_groups_report'),
    path('download/savings-groups/', views.download_savings_groups_report, name='download_savings_groups_report'),
    path('download/grants/', views.download_grants_report, name='download_grants_report'),
    path('download/training/', views.download_training_report, name='download_training_report'),
    path('download/mentoring/', views.download_mentoring_report, name='download_mentoring_report'),
    path('download/geographic/', views.download_geographic_report, name='download_geographic_report'),

    # Download Reports (Excel)
    path('excel/households/', excel_views.download_households_excel, name='download_households_excel'),
    path('excel/business-groups/', excel_views.download_business_groups_excel, name='download_business_groups_excel'),
    path('excel/savings-groups/', excel_views.download_savings_groups_excel, name='download_savings_groups_excel'),
    path('excel/grants/', excel_views.download_grants_excel, name='download_grants_excel'),
    path('excel/training/', excel_views.download_training_excel, name='download_training_excel'),
    path('excel/comprehensive/', excel_views.download_comprehensive_excel, name='download_comprehensive_excel'),

    # PDF Reports with Visualizations
    path('download/mentoring-pdf/', views.download_mentoring_pdf_report, name='download_mentoring_pdf_report'),
    path('download/comprehensive-pdf/', views.download_comprehensive_pdf_report, name='download_comprehensive_pdf_report'),
    path('download/households-pdf/', views.download_household_pdf_report, name='download_household_pdf_report'),
    path('download/business-groups-pdf/', views.download_business_groups_pdf_report, name='download_business_groups_pdf_report'),
    path('download/savings-groups-pdf/', views.download_savings_groups_pdf_report, name='download_savings_groups_pdf_report'),
    path('download/grants-pdf/', views.download_grants_pdf_report, name='download_grants_pdf_report'),
    path('download/training-pdf/', views.download_training_pdf_report, name='download_training_pdf_report'),
    path('download/geographic-pdf/', views.download_geographic_pdf_report, name='download_geographic_pdf_report'),

    # Analytics and Performance Dashboards
    path('performance-dashboard/', views.performance_dashboard, name='performance_dashboard'),
    path('mentoring-activities/', views.mentoring_activities_dashboard, name='mentoring_activities_dashboard'),
    path('custom-report-builder/', views.custom_report_builder, name='custom_report_builder'),
    path('download/custom-report/', views.download_custom_report, name='download_custom_report'),

    # Comparative Reports
    path('comparative/', views.comparative_report, name='comparative_report'),
    path('download/comparative/', views.download_comparative_report, name='download_comparative_report'),
]