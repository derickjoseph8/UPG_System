"""
UPG System Workflow Visual Documentation Generator
Generates a comprehensive PDF with visual diagrams of system workflows
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, Frame, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics import renderPDF
from datetime import datetime
import os

class UPGWorkflowPDF:
    def __init__(self, filename="UPG_System_Visual_Workflow.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.width, self.height = A4

        # Define custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5f8d'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )

        self.heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#3a6f9f'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )

        self.bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6
        )

    def add_cover_page(self):
        """Create an attractive cover page"""
        # Title
        title = Paragraph(
            "UPG MANAGEMENT SYSTEM<br/><br/>Visual Workflow Documentation",
            self.title_style
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))

        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2c5f8d'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        subtitle = Paragraph(
            "Complete Workflow & System Architecture Guide<br/>Ultra-Poor Graduation Program",
            subtitle_style
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 1*inch))

        # System overview box
        overview_data = [
            ['System Overview', ''],
            ['Purpose', 'Track households through 12-month graduation pathway'],
            ['Target', 'Ultra-poor households in Kenya'],
            ['Duration', '12 months per cycle'],
            ['Key Components', '9 core modules, 7 user roles'],
            ['Technology', 'Django 4.2, MySQL, Bootstrap 5'],
        ]

        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d9e0')),
        ]))

        self.story.append(overview_table)
        self.story.append(Spacer(1, 1*inch))

        # Date and version
        info_style = ParagraphStyle(
            'Info',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y')}<br/>Version 1.0"
        info = Paragraph(date_text, info_style)
        self.story.append(info)

        self.story.append(PageBreak())

    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("TABLE OF CONTENTS", self.heading1_style))
        self.story.append(Spacer(1, 0.3*inch))

        toc_data = [
            ['1.', 'System Architecture Overview', '3'],
            ['2.', 'User Roles & Permissions Matrix', '4'],
            ['3.', 'Module Interaction Diagram', '5'],
            ['4.', 'Workflow A: Household Targeting & Enrollment', '6'],
            ['5.', 'Workflow B: Business Group & Grant Cycle', '8'],
            ['6.', 'Workflow C: Training Delivery Process', '10'],
            ['7.', 'Workflow D: Grant Application & Approval', '11'],
            ['8.', 'Workflow E: Reporting & Monitoring', '12'],
            ['9.', 'Workflow F: System Administration', '13'],
            ['10.', '12-Month Timeline Visualization', '14'],
            ['11.', 'Database Relationships', '15'],
            ['12.', 'Integration Points', '16'],
        ]

        toc_table = Table(toc_data, colWidths=[0.5*inch, 5*inch, 0.7*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
        ]))

        self.story.append(toc_table)
        self.story.append(PageBreak())

    def add_system_architecture(self):
        """Add system architecture overview"""
        self.story.append(Paragraph("1. SYSTEM ARCHITECTURE OVERVIEW", self.heading1_style))

        text = """The UPG Management Information System is built on a modular architecture with
        9 core modules that interact to support the complete 12-month graduation pathway. Each module
        has specific responsibilities and data models that work together seamlessly."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Modules table
        modules_data = [
            ['Module', 'Primary Function', 'Key Models'],
            ['Core', 'Foundation & shared services', 'Mentor, Village, BM Cycle, Program, Audit Log, SMS Log'],
            ['Accounts', 'User authentication & roles', 'User (7 roles), UserProfile, UserSettings'],
            ['Households', 'Beneficiary management', 'Household, Members, PPI, Surveys, Programs, Milestones'],
            ['Business Groups', 'Enterprise management', 'BusinessGroup, Members, SB/PR Grants, Progress Surveys'],
            ['Savings Groups', 'Community savings', 'BSG, Members, Savings Records, Progress Surveys'],
            ['Training', 'Capacity building', 'Training, Attendance, Visits, Phone Nudges, Reports'],
            ['UPG Grants', 'Grant management', 'HouseholdGrant, SBGrant, PRGrant, Disbursements'],
            ['Programs', 'Program enrollment', 'Program, Applications, Beneficiaries'],
            ['Reports', 'Analytics & monitoring', 'Dashboards, Custom Reports, Exports'],
        ]

        modules_table = Table(modules_data, colWidths=[1.2*inch, 1.8*inch, 3.5*inch])
        modules_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4f8'), colors.white]),
        ]))

        self.story.append(modules_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Technology Stack
        self.story.append(Paragraph("Technology Stack", self.heading2_style))

        tech_data = [
            ['Component', 'Technology', 'Purpose'],
            ['Backend Framework', 'Django 4.2', 'Web application framework'],
            ['Database', 'MySQL (Production), SQLite (Dev)', 'Data persistence'],
            ['Frontend', 'Bootstrap 5, HTML5, JavaScript', 'User interface'],
            ['SMS Integration', "Africa's Talking, Twilio", 'Notifications'],
            ['Data Collection', 'KoboToolbox API', 'Survey data import'],
            ['Reports', 'ReportLab, Excel export', 'Document generation'],
        ]

        tech_table = Table(tech_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f8d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
        ]))

        self.story.append(tech_table)
        self.story.append(PageBreak())

    def add_roles_matrix(self):
        """Add user roles and permissions matrix"""
        self.story.append(Paragraph("2. USER ROLES & PERMISSIONS MATRIX", self.heading1_style))

        text = """The system implements 7 distinct user roles, each with specific permissions
        and access levels. This ensures data security and appropriate access control."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Roles overview
        roles_data = [
            ['Role', 'Primary Responsibilities', 'Access Level'],
            ['County Executive\n(CECM/Governor)', '• High-level oversight\n• Reports viewing\n• Strategic decisions', 'Read-only\n(All data)'],
            ['County Assembly\nMember', '• Ward-specific monitoring\n• Constituency oversight\n• Progress tracking', 'Read-only\n(Ward data)'],
            ['ICT Administrator', '• Full system access\n• User management\n• System configuration\n• Technical support', 'Full access\n(All modules)'],
            ['M&E Staff', '• Data collection\n• Survey management\n• Report generation\n• Quality monitoring', 'Full data access\n(No system config)'],
            ['Field Associate/\nMentor Supervisor', '• Mentor oversight\n• Village management\n• Training coordination\n• Performance review', 'Regional access\n(Assigned areas)'],
            ['Mentor', '• Household registration\n• Training delivery\n• Field data collection\n• Grant applications', 'Village access\n(Assigned villages)'],
            ['Beneficiary', '• View own data\n• Update contact info\n• Submit reports', 'Personal data only'],
        ]

        roles_table = Table(roles_data, colWidths=[1.3*inch, 3*inch, 2.2*inch])
        roles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4f8'), colors.white]),
        ]))

        self.story.append(roles_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Permissions matrix
        self.story.append(Paragraph("Detailed Permissions Matrix", self.heading2_style))

        perm_data = [
            ['Action', 'ICT Admin', 'M&E Staff', 'Field Assoc.', 'Mentor', 'County Officials'],
            ['Create Households', '✓', '✓', '✓', '✓', '✗'],
            ['Edit Households', '✓', '✓', '✓', '✓ (assigned)', '✗'],
            ['Delete Households', '✓', '✗', '✗', '✗', '✗'],
            ['Create Training', '✓', '✓', '✓', '✗', '✗'],
            ['Mark Attendance', '✓', '✓', '✓', '✓', '✗'],
            ['Create Grants', '✓', '✓', '✓', '✓', '✗'],
            ['Review Grants', '✓', '✓', '✓', '✗', '✗'],
            ['Approve Grants', '✓', '✓', '✗', '✗', '✗'],
            ['Disburse Grants', '✓', '✗', '✗', '✗', '✗'],
            ['View Reports', '✓', '✓', '✓', '✓ (limited)', '✓'],
            ['Export Data', '✓', '✓', '✗', '✗', '✗'],
            ['User Management', '✓', '✗', '✗', '✗', '✗'],
            ['System Config', '✓', '✗', '✗', '✗', '✗'],
        ]

        perm_table = Table(perm_data, colWidths=[1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.1*inch])
        perm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f8d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4f8'), colors.white]),
        ]))

        self.story.append(perm_table)
        self.story.append(PageBreak())

    def add_module_interaction(self):
        """Add module interaction diagram using ASCII art"""
        self.story.append(Paragraph("3. MODULE INTERACTION DIAGRAM", self.heading1_style))

        text = """The diagram below shows how different modules interact with each other.
        Arrows indicate data flow and dependencies between modules."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Create interaction flow
        interaction_text = """
        <pre>
┌─────────────────────────────────────────────────────────┐
│                    DASHBOARD MODULE                     │
│         (Role-based views, Navigation, Alerts)          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│                     CORE MODULE                        │
│   (Mentor, Village, BM Cycle, Program, Audit, SMS)    │
└───┬──────┬──────────┬──────────┬──────────┬───────────┘
    │      │          │          │          │
    ▼      ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌─────────┐┌─────────┐┌─────────┐
│ACCOUNTS││HOUSE-  ││BUSINESS ││SAVINGS  ││TRAINING │
│        ││HOLDS   ││GROUPS   ││GROUPS   ││         │
│Users   ││        ││         ││         ││Modules  │
│Profiles││Members ││Members  ││Members  ││Attend.  │
│Roles   ││PPI     ││SB/PR    ││Savings  ││Visits   │
└────────┘└───┬────┘└────┬────┘└────┬────┘└────┬────┘
              │          │          │          │
              └──────────┴──────────┴──────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   UPG GRANTS     │
              │  HouseholdGrant  │
              │    SBGrant       │
              │    PRGrant       │
              └─────────┬────────┘
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
   ┌───────────────┐      ┌──────────────────┐
   │   PROGRAMS    │      │     REPORTS      │
   │  Applications │      │   Performance    │
   │  Beneficiary  │      │   Analytics      │
   └───────────────┘      └──────────────────┘
        </pre>
        """

        mono_style = ParagraphStyle(
            'Mono',
            parent=self.styles['Code'],
            fontSize=7,
            fontName='Courier',
            leftIndent=0,
            leading=10
        )

        self.story.append(Paragraph(interaction_text, mono_style))
        self.story.append(Spacer(1, 0.3*inch))

        # Key dependencies
        self.story.append(Paragraph("Key Module Dependencies", self.heading2_style))

        dep_bullets = [
            "• <b>Core → All Modules:</b> Provides foundation data (villages, mentors, programs)",
            "• <b>Accounts → All Modules:</b> Authentication and role-based access control",
            "• <b>Households → Business Groups:</b> Households join to form business groups",
            "• <b>Households → Savings Groups:</b> Households participate in savings groups",
            "• <b>Business Groups → UPG Grants:</b> Groups apply for SB and PR grants",
            "• <b>Training → Households:</b> Households enroll in training modules",
            "• <b>Programs → All:</b> Enrollment and tracking across all activities",
            "• <b>Reports → All:</b> Aggregates data from all modules for analytics",
        ]

        for bullet in dep_bullets:
            self.story.append(Paragraph(bullet, self.bullet_style))

        self.story.append(PageBreak())

    def add_workflow_a(self):
        """Add Workflow A: Household Targeting & Enrollment"""
        self.story.append(Paragraph("4. WORKFLOW A: HOUSEHOLD TARGETING & ENROLLMENT", self.heading1_style))

        # Flowchart
        flowchart = """
        <pre>
START
  │
  ▼
┌─────────────────────────────────┐
│ STEP 1: Data Import (Optional) │
│ Actor: M&E Staff                │
│ • Import ESR from KoboToolbox   │
│ • Map external data to system   │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ STEP 2: Household Registration  │
│ Actor: Mentor                   │
│ • Enter household details       │
│ • Add household members         │
│ • Capture GPS coordinates       │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ STEP 3: Eligibility Assessment  │
│ System: Automatic Scoring       │
│ • Poverty Index (30%)           │
│ • Income Level (25%)            │
│ • Asset Ownership (15%)         │
│ • Social Factors (15%)          │
│ • Geographic (10%)              │
│ • Demographic (5%)              │
└─────────────┬───────────────────┘
              │
              ▼
        ┌─────────┐
        │Score>=60?│ ──NO──► END (Not Eligible)
        └────┬────┘
             │YES
             ▼
┌─────────────────────────────────┐
│ STEP 4: PPI Assessment          │
│ Actor: Mentor                   │
│ • Conduct 10-question survey    │
│ • Record PPI score (0-100)      │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ STEP 5: Program Enrollment      │
│ System: Create Program Record   │
│ • Status: enrolled → active     │
│ • Assign mentor                 │
│ • Set enrollment date           │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ STEP 6: Initialize Milestones   │
│ System: Create 12 Milestones    │
│ • Month 1: PPI & Training       │
│ • Month 2: Group Formation      │
│ • Month 3: Business Plan        │
│ • Month 4-12: Grant & Growth    │
└─────────────┬───────────────────┘
              │
              ▼
            END (Enrolled in UPG Program)
        </pre>
        """

        mono_style = ParagraphStyle('Mono', parent=self.styles['Code'], fontSize=8, fontName='Courier', leading=11)
        self.story.append(Paragraph(flowchart, mono_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Eligibility levels table
        self.story.append(Paragraph("Eligibility Scoring Levels", self.heading2_style))

        elig_data = [
            ['Score Range', 'Level', 'Action'],
            ['80 - 100', 'Highly Eligible', 'Priority enrollment'],
            ['60 - 79', 'Eligible', 'Standard enrollment'],
            ['40 - 59', 'Marginally Eligible', 'Case-by-case review'],
            ['0 - 39', 'Not Eligible', 'Refer to other programs'],
        ]

        elig_table = Table(elig_data, colWidths=[1.5*inch, 2*inch, 3*inch])
        elig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#90EE90')),
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#98FB98')),
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#FFFFE0')),
            ('BACKGROUND', (0, 4), (0, 4), colors.HexColor('#FFB6C1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
        ]))

        self.story.append(elig_table)
        self.story.append(PageBreak())

    def add_workflow_b(self):
        """Add Workflow B: Business Group & Grant Cycle"""
        self.story.append(Paragraph("5. WORKFLOW B: BUSINESS GROUP & GRANT CYCLE", self.heading1_style))
        self.story.append(Paragraph("12-Month Business Development Process", self.heading2_style))

        # Timeline flowchart
        timeline = """
        <pre>
MONTHS 1-3: TRAINING PHASE
│
├─► Training Setup (Field Associate)
│   └─► Create BM Cycle & Training Modules
│
├─► Training Delivery (Mentor)
│   ├─► Enroll households (max 25)
│   ├─► Conduct sessions
│   ├─► Record daily attendance
│   └─► Submit weekly reports
│
└─► Business Group Formation (Month 2)
    └─► Form groups of 2-3 households
        └─► Assign roles: Leader, Treasurer, Secretary

MONTHS 4-5: SB GRANT PHASE
│
├─► Grant Application (Mentor)
│   ├─► Create business plan
│   ├─► Project income/expenses
│   └─► Submit application (Status: pending)
│
├─► Review Process (M&E Staff)
│   ├─► Review business viability
│   ├─► Score application (0-100)
│   └─► Status: pending → under_review
│
├─► Approval (Program Manager)
│   ├─► Approve/reject decision
│   └─► Status: under_review → approved
│
└─► Disbursement (Finance)
    ├─► Process payment (Bank/Mobile/Cash)
    ├─► Record transaction
    └─► Status: approved → disbursed
        │
        └─► GRANT AMOUNT: KES 10,000 - 25,000
            Base: KES 15,000
            + Group size bonus (10-20%)
            + Business type bonus (15%)
            + Location bonus (5%)
            + Performance bonus (10%)

MONTHS 6-8: BUSINESS OPERATIONS
│
├─► Business Launch
│   ├─► Purchase inventory/assets
│   └─► Begin revenue generation
│
├─► Progress Monitoring (Mentor)
│   ├─► Monthly BusinessProgressSurvey
│   ├─► Track: Grant usage, Profit, Inventory
│   └─► Health Status: Red / Yellow / Green
│
└─► BSG Formation (Month 8)
    └─► Create Business Savings Group
        ├─► Target: 25 members
        ├─► Set meeting schedule
        └─► Record savings transactions

MONTHS 9-10: PR GRANT PHASE
│
├─► Eligibility Assessment (System + Mentor)
│   ├─► SB grant disbursed ✓
│   ├─► Utilization report submitted ✓
│   ├─► Good business performance
│   └─► Performance: excellent/good/satisfactory
│
├─► PR Grant Application (Mentor)
│   ├─► Document business metrics
│   ├─► Revenue, jobs created, savings
│   └─► Growth plans (Base: KES 10,000)
│
└─► Review & Approval (Same as SB Grant)
    └─► Disbursement → Status: disbursed

MONTHS 11-12: GRADUATION
│
├─► Business Assessment (Month 11)
│   ├─► Financial sustainability check
│   ├─► Savings verification
│   └─► Group cohesion assessment
│
└─► Graduation Assessment (Month 12)
    ├─► Conduct endline PPI
    ├─► Compare baseline vs endline
    ├─► Verify graduation criteria:
    │   ├─► Stable income source
    │   ├─► Regular savings
    │   ├─► Improved living conditions
    │   └─► Reduced vulnerability
    └─► Status: active → GRADUATED ✓
        </pre>
        """

        mono_style = ParagraphStyle('Mono', parent=self.styles['Code'], fontSize=7, fontName='Courier', leading=9)
        self.story.append(Paragraph(timeline, mono_style))
        self.story.append(PageBreak())

    def add_workflow_c(self):
        """Add Workflow C: Training Delivery"""
        self.story.append(Paragraph("6. WORKFLOW C: TRAINING DELIVERY PROCESS", self.heading1_style))

        training_flow = """
        <pre>
┌────────────────────────────────────────────────┐
│ STAGE 1: TRAINING SETUP                        │
├────────────────────────────────────────────────┤
│ Field Associate:                               │
│ 1. Create BusinessMentorCycle (e.g., FY25C1)   │
│ 2. Create Training Module                      │
│    • Assign mentor                             │
│    • Set dates & location                      │
│    • Max: 25 households                        │
│    • Status: planned                           │
└────────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────────┐
│ STAGE 2: HOUSEHOLD ENROLLMENT                  │
├────────────────────────────────────────────────┤
│ Mentor:                                        │
│ 1. Select households from assigned villages    │
│ 2. System enforces:                            │
│    • Max 25 per training                       │
│    • 1 household = 1 training at a time        │
│ 3. Create HouseholdTrainingEnrollment          │
│    • Status: enrolled                          │
│ 4. Optional: Send SMS reminders                │
└────────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────────┐
│ STAGE 3: TRAINING DELIVERY                     │
├────────────────────────────────────────────────┤
│ Mentor:                                        │
│ 1. Start Training (Status: planned → active)   │
│ 2. Conduct training sessions                   │
│ 3. Record Daily Attendance:                    │
│    • Select date                               │
│    • Mark present/absent for each household    │
│    • System records: mentor, timestamp         │
│ 4. Multi-day support:                          │
│    • Separate attendance per date              │
└────────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────────┐
│ STAGE 4: MENTORING SUPPORT                     │
├────────────────────────────────────────────────┤
│ Mentor logs:                                   │
│ • On-site visits (MentoringVisit)             │
│   - Visit type, topics, detailed notes         │
│ • Phone nudges (PhoneNudge)                    │
│   - Types: reminder, follow-up, support        │
│   - Duration, success status                   │
│ • Weekly/Monthly reports (MentoringReport)     │
│   - Activities, challenges, successes, plans   │
└────────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────────┐
│ STAGE 5: COMPLETION                            │
├────────────────────────────────────────────────┤
│ Mentor:                                        │
│ 1. Complete Training                           │
│    • Status: active → completed                │
│ 2. System calculates:                          │
│    • Overall attendance rate                   │
│    • Households who completed (>80% attend.)   │
│ 3. Update HouseholdTrainingEnrollment          │
│    • Status: enrolled → completed              │
│ 4. Optional: Generate certificates             │
└────────────────────────────────────────────────┘
        </pre>
        """

        mono_style = ParagraphStyle('Mono', parent=self.styles['Code'], fontSize=8, fontName='Courier', leading=11)
        self.story.append(Paragraph(training_flow, mono_style))

        # Training statistics
        self.story.append(Paragraph("Training Metrics Tracked", self.heading2_style))

        metrics = [
            "• <b>Real-time Statistics:</b> Total enrolled, present count, absent count, attendance rate %",
            "• <b>Recent Activity Log:</b> Last 10 attendance changes with household, date, status, marked by",
            "• <b>Attendance History:</b> Per-household attendance across all training dates",
            "• <b>Completion Rate:</b> Percentage of households completing training (>80% attendance)",
            "• <b>Performance Bonus:</b> High attendance rates increase SB grant amount by up to 10%",
        ]

        for metric in metrics:
            self.story.append(Paragraph(metric, self.bullet_style))

        self.story.append(PageBreak())

    def add_workflow_d(self):
        """Add Workflow D: Grant Application & Approval"""
        self.story.append(Paragraph("7. WORKFLOW D: GRANT APPLICATION & APPROVAL", self.heading1_style))

        grant_flow = """
        <pre>
┌──────────────────────────────────────┐
│ STEP 1: APPLICATION CREATION         │
│ Actor: Mentor / Field Associate      │
├──────────────────────────────────────┤
│ 1. Select Grant Type:                │
│    • Seed Business Grant             │
│    • Performance Recognition Grant   │
│    • Livelihood Grant                │
│    • Emergency Grant                 │
│    • Education Support               │
│    • Housing Improvement             │
│    • Other                           │
│                                      │
│ 2. Select Applicant:                 │
│    • Household                       │
│    • Business Group                  │
│    • Savings Group                   │
│                                      │
│ 3. Fill Application:                 │
│    • Title & purpose                 │
│    • Requested amount                │
│    • Expected outcomes               │
│    • Itemized budget                 │
│    • Supporting documents            │
│                                      │
│ 4. Submit                            │
│    Status: draft → submitted         │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ STEP 2: REVIEW PROCESS               │
│ Actor: M&E Staff / Program Manager   │
├──────────────────────────────────────┤
│ 1. Access Pending Reviews            │
│ 2. Review application:               │
│    • Applicant eligibility           │
│    • Purpose & justification         │
│    • Budget reasonableness           │
│    • Alignment with program goals    │
│    • Supporting documentation        │
│                                      │
│ 3. Enter review notes & score (0-100)│
│    Status: submitted → under_review  │
│                                      │
│ 4. Record review date & reviewer     │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ STEP 3: APPROVAL DECISION            │
│ Actor: Program Manager / County Dir  │
│       / Executive                    │
├──────────────────────────────────────┤
│ Review comprehensive package:        │
│ • Review notes & score               │
│ • Budget alignment                   │
│ • Program budget availability        │
│ • Strategic priority                 │
│                                      │
│ Make Decision:                       │
│                                      │
│ ┌─► APPROVE                          │
│ │   • Set approved_amount            │
│ │   • Enter approval notes           │
│ │   • Status: under_review→approved  │
│ │   • Record approver & date         │
│ │                                    │
│ ├─► REJECT                           │
│ │   • Enter rejection reasons        │
│ │   • Status: under_review→rejected  │
│ │                                    │
│ └─► REQUEST MORE INFO                │
│     • Add notes for applicant        │
│     • Status: remains under_review   │
└──────────┬───────────────────────────┘
           │ (if approved)
           ▼
┌──────────────────────────────────────┐
│ STEP 4: DISBURSEMENT                 │
│ Actor: Finance / ICT Admin           │
├──────────────────────────────────────┤
│ 1. Access Approved Grants            │
│ 2. Select grant for disbursement     │
│ 3. Enter disbursement details:       │
│    • Disbursement date               │
│    • Disbursement amount             │
│      (full or partial)               │
│    • Method:                         │
│      - Bank transfer                 │
│      - Mobile money (M-Pesa)         │
│      - Cash                          │
│      - Check                         │
│    • Reference number (transaction)  │
│                                      │
│ 4. System updates:                   │
│    • disbursed_amount field          │
│    • remaining_amount calculated     │
│    • disbursement_percentage shown   │
│    • Status: approved → disbursed    │
│      (when fully disbursed)          │
│                                      │
│ 5. Optional: Send SMS notification   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ STEP 5: UTILIZATION & FOLLOW-UP      │
│ Actor: Mentor / M&E Staff            │
├──────────────────────────────────────┤
│ 1. Recipient uses grant funds        │
│ 2. Mentor conducts follow-up visits  │
│ 3. Recipient submits utilization:    │
│    • How funds were used             │
│    • Outcomes achieved               │
│    • Challenges faced                │
│                                      │
│ 4. Mentor verifies & uploads report  │
│ 5. System tracks utilization date    │
│ 6. M&E generates impact reports      │
└──────────────────────────────────────┘
        </pre>
        """

        mono_style = ParagraphStyle('Mono', parent=self.styles['Code'], fontSize=7, fontName='Courier', leading=9)
        self.story.append(Paragraph(grant_flow, mono_style))
        self.story.append(PageBreak())

    def add_workflow_e(self):
        """Add Workflow E: Reporting & Monitoring"""
        self.story.append(Paragraph("8. WORKFLOW E: REPORTING & MONITORING (M&E)", self.heading1_style))

        text = """M&E Staff have comprehensive dashboards and reporting tools to monitor program
        performance, mentor activities, and generate custom reports."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Dashboard metrics
        self.story.append(Paragraph("M&E Dashboard Components", self.heading2_style))

        dashboard_data = [
            ['Component', 'Metrics Tracked', 'Purpose'],
            ['Performance Metrics', '• Total mentoring reports\n• Pending reports (30 days)\n• Training completion rate\n• Household visits\n• Phone nudges\n• Total mentor activities', 'Real-time program monitoring'],
            ['Recent Activities', '• Last 10 mentoring visits\n• Last 10 phone nudges\n• Sorted by recency', 'Track latest field activities'],
            ['Mentor Activity\nSummary', '• Visits count (30 days)\n• Calls count (30 days)\n• Total activities per mentor\n• Sorted by activity level', 'Identify active/inactive mentors'],
            ['Geographic\nCoverage', '• Villages by county\n• Household distribution\n• Saturation levels\n• Program area status', 'Ensure equitable coverage'],
            ['Financial Tracking', '• Total grants disbursed\n• Business progress metrics\n• Savings accumulated\n• Income generation trends', 'Monitor financial outcomes'],
        ]

        dashboard_table = Table(dashboard_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
        dashboard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4f8'), colors.white]),
        ]))

        self.story.append(dashboard_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Report types
        self.story.append(Paragraph("Standard Report Types", self.heading2_style))

        reports = [
            "• <b>Household Graduation Pipeline:</b> Eligible → Enrolled → Active → Graduated (with dropout analysis)",
            "• <b>Business Group Performance:</b> Health status distribution (Red/Yellow/Green), grant utilization, profit margins",
            "• <b>Savings Group Financials:</b> Total savings by group, average per member, meeting attendance, sustainability",
            "• <b>Training Effectiveness:</b> Attendance rates by module, completion rates, correlation with business performance",
            "• <b>Mentor Performance:</b> Households assigned, visits conducted, phone nudges, training sessions, report compliance",
            "• <b>County-Level Summaries:</b> Aggregated statistics by county, ward-level breakdowns, constituency comparisons",
        ]

        for report in reports:
            self.story.append(Paragraph(report, self.bullet_style))

        self.story.append(Spacer(1, 0.2*inch))

        # Data quality monitoring
        self.story.append(Paragraph("Data Quality Monitoring", self.heading2_style))

        quality_checks = [
            "• <b>Completeness Checks:</b> Households missing key information, incomplete PPI assessments, missing milestone updates",
            "• <b>Validation Reports:</b> Households eligible but not enrolled, business groups without SB grant applications",
            "• <b>Anomaly Detection:</b> Outlier grant amounts, unusual attendance patterns, data entry errors (duplicates, invalid dates)",
        ]

        for check in quality_checks:
            self.story.append(Paragraph(check, self.bullet_style))

        self.story.append(PageBreak())

    def add_workflow_f(self):
        """Add Workflow F: System Administration"""
        self.story.append(Paragraph("9. WORKFLOW F: SYSTEM ADMINISTRATION (ICT ADMIN)", self.heading1_style))

        admin_sections = [
            ("User Management", [
                "• <b>Create User Accounts:</b> Username, email, password, role (1 of 7 roles), contact info",
                "• <b>Assign Village Access:</b> For Mentors/Field Associates, restrict to assigned villages only",
                "• <b>Permission Review:</b> Test access levels, modify permissions as needed",
                "• <b>Password Reset:</b> Admin direct reset or user self-service with 24-hour token validity",
            ]),
            ("System Configuration", [
                "• <b>System Settings:</b> Key-value pairs (SMS_ENABLED, SMS_PROVIDER, DEFAULT_GRANT_AMOUNT, etc.)",
                "• <b>System Alerts:</b> Create alerts (info/warning/error/maintenance/security) with scope and expiration",
                "• <b>SMS Configuration:</b> Africa's Talking (primary) and Twilio (fallback) API setup and testing",
            ]),
            ("Data Management", [
                "• <b>ESR Import:</b> Upload CSV/Excel from KoboToolbox, map columns, validate, process, review results",
                "• <b>Backup & Restore:</b> Full/Incremental/Database/Media backups with file tracking and restore capability",
                "• <b>Data Export:</b> Select model, filters, fields, format (Excel/CSV/JSON), generate and download (logged)",
            ]),
            ("Geographic Setup", [
                "• <b>Administrative Units:</b> Add County → SubCounty → Village hierarchy",
                "• <b>Village Details:</b> Distance to market, program area status, saturation level, qualified households capacity",
                "• <b>BM Cycle Management:</b> Create/Edit/Delete cycles, assign mentors, link trainings",
            ]),
            ("Security & Compliance", [
                "• <b>Audit Log Monitoring:</b> Review all system actions (login, data changes, exports) with filters",
                "• <b>Session Management:</b> 1-hour timeout, expire at browser close, force logout inactive users",
                "• <b>Password Policy:</b> Min 8 chars (uppercase, lowercase, number), optional expiration, 2FA support",
            ]),
        ]

        for section, items in admin_sections:
            self.story.append(Paragraph(section, self.heading2_style))
            for item in items:
                self.story.append(Paragraph(item, self.bullet_style))
            self.story.append(Spacer(1, 0.1*inch))

        self.story.append(PageBreak())

    def add_timeline(self):
        """Add 12-month timeline visualization"""
        self.story.append(Paragraph("10. 12-MONTH TIMELINE VISUALIZATION", self.heading1_style))

        text = """Visual representation of the complete Ultra-Poor Graduation pathway over 12 months."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Timeline table
        timeline_data = [
            ['Month', 'Milestone', 'Key Activities', 'Status Checkpoints'],
            ['1', 'PPI Assessment &\nTraining Start', '• Conduct baseline PPI\n• Enroll in training\n• Begin capacity building', '• Household active\n• Training enrolled'],
            ['2', 'Business Group\nFormation', '• Form groups of 2-3\n• Assign roles\n• Team building', '• Group formed\n• Members active'],
            ['3', 'Business Plan\nDevelopment', '• Develop business plan\n• Identify business idea\n• Estimate costs & income', '• Plan completed\n• Budget approved'],
            ['4', 'SB Grant\nApplication', '• Submit SB grant application\n• Business plan review\n• Budget justification', '• Application submitted\n• Under review'],
            ['5', 'SB Grant\nDisbursement', '• Grant approval\n• Funds disbursement\n• KES 10K-25K received', '• Grant approved\n• Funds disbursed'],
            ['6', 'Business\nOperations Start', '• Purchase inventory\n• Setup business\n• Begin operations', '• Business launched\n• Revenue started'],
            ['7', 'Mid-term\nAssessment', '• Conduct midline PPI\n• Progress evaluation\n• Challenge identification', '• Midline completed\n• Performance scored'],
            ['8', 'BSG Formation', '• Create savings group\n• Recruit 25 members\n• Start savings', '• BSG formed\n• Savings initiated'],
            ['9', 'PR Grant\nEligibility', '• Assess business performance\n• Review SB grant utilization\n• Performance scoring', '• Eligibility confirmed\n• Performance: good+'],
            ['10', 'PR Grant\nApplication', '• Submit PR grant application\n• Document achievements\n• Growth plans', '• Application submitted\n• Under review'],
            ['11', 'Final Business\nAssessment', '• Financial sustainability\n• Savings verification\n• Group cohesion check', '• Business viable\n• Savings regular'],
            ['12', 'Graduation\nAssessment', '• Conduct endline PPI\n• Compare baseline vs endline\n• Graduation decision', '• Status: GRADUATED\n• Program completed'],
        ]

        timeline_table = Table(timeline_data, colWidths=[0.6*inch, 1.3*inch, 2.5*inch, 2.1*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            # Phase coloring
            ('BACKGROUND', (0, 1), (0, 3), colors.HexColor('#E6F3FF')),  # Months 1-3: Training
            ('BACKGROUND', (0, 4), (0, 5), colors.HexColor('#FFE6E6')),  # Months 4-5: SB Grant
            ('BACKGROUND', (0, 6), (0, 8), colors.HexColor('#E6FFE6')),  # Months 6-8: Operations
            ('BACKGROUND', (0, 9), (0, 10), colors.HexColor('#FFF4E6')), # Months 9-10: PR Grant
            ('BACKGROUND', (0, 11), (0, 12), colors.HexColor('#F0E6FF')),# Months 11-12: Graduation
        ]))

        self.story.append(timeline_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Legend
        legend_data = [
            ['Phase', 'Months', 'Focus'],
            ['Training Phase', '1-3', 'Capacity building & group formation'],
            ['SB Grant Phase', '4-5', 'Seed capital acquisition'],
            ['Operations Phase', '6-8', 'Business launch & BSG formation'],
            ['PR Grant Phase', '9-10', 'Performance recognition & growth'],
            ['Graduation Phase', '11-12', 'Final assessment & exit'],
        ]

        legend_table = Table(legend_data, colWidths=[1.5*inch, 1*inch, 4*inch])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5f8d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E6F3FF')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFE6E6')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E6FFE6')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#FFF4E6')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#F0E6FF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
        ]))

        self.story.append(Paragraph("Phase Legend", self.heading3_style))
        self.story.append(legend_table)

        self.story.append(PageBreak())

    def add_database_relationships(self):
        """Add database relationships diagram"""
        self.story.append(Paragraph("11. DATABASE RELATIONSHIPS", self.heading1_style))

        text = """Entity Relationship Diagram showing core data models and their connections."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        erd = """
        <pre>
┌──────────────┐
│     USER     │
│ (Accounts)   │
└──────┬───────┘
       │
       ├─────1:1────► ┌──────────────┐
       │              │    MENTOR    │
       │              │    (Core)    │
       │              └──────┬───────┘
       │                     │
       │                     │ assigned to
       │                     ▼
       │              ┌─────────────────────┐
       │              │ BUSINESS MENTOR     │
       │              │     CYCLE           │
       │              │    (Core)           │
       │              └──────┬──────────────┘
       │                     │
       │                     │ has many
       │                     ▼
       │              ┌─────────────────────┐
       │              │     TRAINING        │
       │              │   (Training)        │
       │              └──────┬──────────────┘
       │                     │
       │                     │ attendance
       │                     ▼
       ├─────1:1────► ┌──────────────┐
       │              │ USER PROFILE │
       │              │  (Accounts)  │
       │              └──────────────┘
       │                     │
       │                     │ assigned villages (M:M)
       │                     ▼
       └─────────────► ┌──────────────┐
                       │   VILLAGE    │
                       │    (Core)    │
                       └──────┬───────┘
                              │
                              │ has many
                              ▼
                       ┌──────────────┐
                       │  HOUSEHOLD   │
                       │ (Households) │
                       └──────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  HOUSEHOLD   │     │     PPI      │     │  HOUSEHOLD   │
│   MEMBER     │     │  (Baseline/  │     │   PROGRAM    │
│ (Households) │     │   Midline/   │     │ (Households) │
└──────────────┘     │   Endline)   │     └──────┬───────┘
                     │ (Households) │            │
                     └──────────────┘            │
                                                 │ has 12
                                                 ▼
                                          ┌──────────────┐
                                          │UPG MILESTONE │
                                          │ (Households) │
                                          │  (Month 1-12)│
                                          └──────────────┘

┌──────────────┐
│  HOUSEHOLD   │
└──────┬───────┘
       │
       ├──────────────► ┌──────────────────┐
       │                │ BUSINESS GROUP   │
       │  (member of)   │   MEMBER         │
       │                │ (Business Groups)│
       │                └────────┬─────────┘
       │                         │
       │                         │ belongs to
       │                         ▼
       │                  ┌──────────────────┐
       │                  │  BUSINESS GROUP  │
       │                  │ (Business Groups)│
       │                  └────────┬─────────┘
       │                           │
       │            ┌──────────────┼──────────────┐
       │            │              │              │
       │            ▼              ▼              ▼
       │     ┌───────────┐  ┌───────────┐  ┌───────────┐
       │     │  SB GRANT │  │  PR GRANT │  │ BUSINESS  │
       │     │   (UPG    │  │   (UPG    │  │ PROGRESS  │
       │     │  Grants)  │  │  Grants)  │  │  SURVEY   │
       │     └─────┬─────┘  └─────┬─────┘  │ (Business)│
       │           │              │         └───────────┘
       │           │    1:1       │
       │           └──────────────┘
       │           (PR requires SB)
       │
       └──────────────► ┌──────────────────┐
                        │    BSG MEMBER    │
          (member of)   │ (Savings Groups) │
                        └────────┬─────────┘
                                 │
                                 │ belongs to
                                 ▼
                          ┌──────────────────┐
                          │  BUSINESS SAVINGS│
                          │      GROUP       │
                          │ (Savings Groups) │
                          └────────┬─────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            ┌───────────┐  ┌───────────┐  ┌───────────┐
            │  SAVINGS  │  │    BSG    │  │ BUSINESS  │
            │  RECORD   │  │ PROGRESS  │  │   GROUP   │
            │ (Savings) │  │  SURVEY   │  │   (M:M)   │
            └───────────┘  │ (Savings) │  └───────────┘
                           └───────────┘

GRANT APPLICATION HIERARCHY:

┌──────────────────────────┐
│ HOUSEHOLD GRANT          │
│    APPLICATION           │
│    (UPG Grants)          │
└────────┬─────────────────┘
         │
         │ can be for (nullable FKs):
         │
         ├────► Household
         ├────► Business Group
         └────► Savings Group
         │
         │ linked to:
         │
         ├────► Program (optional)
         ├────► Submitted By (User)
         ├────► Reviewed By (User)
         └────► Approved By (User)
        </pre>
        """

        mono_style = ParagraphStyle('Mono', parent=self.styles['Code'], fontSize=6, fontName='Courier', leading=8)
        self.story.append(Paragraph(erd, mono_style))

        self.story.append(PageBreak())

    def add_integration_points(self):
        """Add integration points overview"""
        self.story.append(Paragraph("12. INTEGRATION POINTS & EXTERNAL SYSTEMS", self.heading1_style))

        text = """The UPG system integrates with several external services to enhance functionality."""
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))

        # Integration table
        integration_data = [
            ['System', 'Purpose', 'Integration Type', 'Data Flow'],
            ['KoboToolbox', 'Mobile survey data collection', 'API (REST)', 'Import survey responses\n→ Create/update households\n→ ESRImport tracking'],
            ["Africa's Talking", 'SMS notifications (Primary)', 'API (REST)', 'Send SMS to households\n← Delivery reports\n→ SMS log tracking'],
            ['Twilio', 'SMS notifications (Fallback)', 'API (REST)', 'Send SMS when AT fails\n← Delivery status\n→ SMS log tracking'],
            ['MySQL Database', 'Production data storage', 'Direct connection', 'All application data\n↔ CRUD operations\n→ Backup/restore'],
            ['Excel/CSV', 'Data import/export', 'File-based', 'Import ESR lists\n→ Export reports\n↔ Bulk operations'],
            ['Email (SMTP)', 'User notifications', 'SMTP protocol', 'Password resets\n→ System alerts\n→ Report delivery'],
        ]

        integration_table = Table(integration_data, colWidths=[1.2*inch, 1.8*inch, 1.5*inch, 2*inch])
        integration_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d9e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f4f8'), colors.white]),
        ]))

        self.story.append(integration_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Security considerations
        self.story.append(Paragraph("Security & Data Protection", self.heading2_style))

        security = [
            "• <b>API Authentication:</b> All external API calls use API keys/tokens stored securely",
            "• <b>Data Encryption:</b> HTTPS for all web traffic, encrypted database connections",
            "• <b>PII Protection:</b> Personal Identifiable Information (phone numbers, IDs) encrypted at rest",
            "• <b>Access Logging:</b> All API calls logged in SystemAuditLog with timestamps and user attribution",
            "• <b>Rate Limiting:</b> API requests rate-limited to prevent abuse and ensure fair usage",
            "• <b>Backup Security:</b> Database backups encrypted and stored securely with access controls",
        ]

        for item in security:
            self.story.append(Paragraph(item, self.bullet_style))

        self.story.append(Spacer(1, 0.3*inch))

        # Mobile features
        self.story.append(Paragraph("Mobile Data Collection Features", self.heading2_style))

        mobile = [
            "• <b>Responsive Design:</b> Works on smartphones and tablets (iOS, Android)",
            "• <b>GPS Capture:</b> Automatic location tagging for households and field activities",
            "• <b>Offline Mode:</b> (Planned) Local data storage with sync when online",
            "• <b>Photo Upload:</b> Support for uploading supporting documents and photos",
            "• <b>QR Code Scanning:</b> Quick household lookup via QR codes",
            "• <b>Voice Input:</b> (Planned) Voice-to-text for notes and observations",
        ]

        for item in mobile:
            self.story.append(Paragraph(item, self.bullet_style))

        self.story.append(PageBreak())

        # Footer page
        self.add_footer_page()

    def add_footer_page(self):
        """Add final page with contact and version info"""
        self.story.append(Spacer(1, 2*inch))

        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        title = Paragraph("<b>UPG Management Information System</b>", footer_style)
        self.story.append(title)

        info = [
            "Visual Workflow Documentation",
            "",
            "Developed for: Village Enterprise",
            "Program: Ultra-Poor Graduation (UPG)",
            "Location: Kenya",
            "",
            f"Document Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            "Version: 1.0",
            "",
            "Technology Stack: Django 4.2, MySQL, Bootstrap 5",
            "Mobile-Responsive | SMS-Enabled | API-Integrated",
        ]

        for line in info:
            p = Paragraph(line, footer_style)
            self.story.append(p)

        self.story.append(Spacer(1, 1*inch))

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )

        disclaimer = Paragraph(
            "<i>This document provides a comprehensive visual overview of the UPG system workflows, "
            "architecture, and processes. For technical documentation and API details, please refer to "
            "the system's README.md and code documentation.</i>",
            disclaimer_style
        )
        self.story.append(disclaimer)

    def generate(self):
        """Generate the complete PDF document"""
        print("Generating UPG System Visual Workflow PDF...")

        # Add all sections
        self.add_cover_page()
        self.add_table_of_contents()
        self.add_system_architecture()
        self.add_roles_matrix()
        self.add_module_interaction()
        self.add_workflow_a()
        self.add_workflow_b()
        self.add_workflow_c()
        self.add_workflow_d()
        self.add_workflow_e()
        self.add_workflow_f()
        self.add_timeline()
        self.add_database_relationships()
        self.add_integration_points()

        # Build the PDF
        self.doc.build(self.story)
        print(f"[SUCCESS] PDF generated successfully: {self.filename}")
        print(f"[SUCCESS] File size: {os.path.getsize(self.filename) / 1024:.2f} KB")

if __name__ == "__main__":
    pdf = UPGWorkflowPDF("UPG_System_Visual_Workflow.pdf")
    pdf.generate()
    print("\nDone! Open 'UPG_System_Visual_Workflow.pdf' to view the document.")
