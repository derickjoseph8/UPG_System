# UPG (Ultra Poor Graduation) System - Complete User Manual

**Version:** 1.0.0
**Last Updated:** October 3, 2025
**System Type:** Web-based Django Application
**Database:** MySQL (MariaDB Compatible)

---

## Table of Contents

### Part 1: User Manual Documentation
1. [System Overview](#1-system-overview)
2. [User Roles & Permissions](#2-user-roles--permissions)
3. [Module Documentation](#3-module-documentation)
   - [3.1 Accounts Module](#31-accounts-module)
   - [3.2 Core Module](#32-core-module)
   - [3.3 Households Module](#33-households-module)
   - [3.4 Business Groups Module](#34-business-groups-module)
   - [3.5 Savings Groups Module](#35-savings-groups-module)
   - [3.6 Training Module](#36-training-module)
   - [3.7 Surveys Module](#37-surveys-module)
   - [3.8 Programs Module](#38-programs-module)
   - [3.9 Grants Module](#39-grants-module)
   - [3.10 UPG Grants Module](#310-upg-grants-module)
   - [3.11 Forms Module](#311-forms-module)
   - [3.12 Reports Module](#312-reports-module)
   - [3.13 Dashboard Module](#313-dashboard-module)
   - [3.14 Settings Module](#314-settings-module)
4. [Step-by-Step User Guides](#4-step-by-step-user-guides)
5. [Troubleshooting](#5-troubleshooting)

### Part 2: Complete Source Code Appendix
6. [Appendix: Complete Source Code](#6-appendix-complete-source-code)

---

# Part 1: User Manual Documentation

## 1. System Overview

### 1.1 What is the UPG System?

The **Ultra-Poor Graduation (UPG) Management System** is a comprehensive web-based platform designed to manage and track the implementation of poverty graduation programs in Kenya. The system supports the complete lifecycle of the UPG program, from household identification and enrollment through training, business development, grant management, and graduation tracking.

### 1.2 Purpose

The UPG System serves multiple critical purposes:

- **Household Management**: Track ultra-poor households, their demographics, and eligibility for programs
- **Program Implementation**: Manage training modules, mentoring activities, and business development
- **Grant Administration**: Process and track SB (Seed Business) and PR (Performance Recognition) grants
- **Business Group Management**: Facilitate formation and tracking of entrepreneurial business groups
- **Savings Group Tracking**: Monitor community savings groups and their financial activities
- **Reporting & Analytics**: Generate comprehensive reports for M&E and program management
- **Multi-level Access Control**: Role-based access for different stakeholders (County Executives, M&E Staff, Field Associates, Mentors, Beneficiaries)

### 1.3 System Architecture

**Technology Stack:**
- **Framework**: Django 4.x (Python)
- **Database**: MySQL 8.0 (via XAMPP for local development)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Django's built-in authentication with custom User model
- **Forms**: Django Crispy Forms with Bootstrap 5

**Key Components:**
1. **Web Application Layer**: Django-based MVC architecture
2. **Database Layer**: MySQL relational database with normalized schema
3. **Business Logic Layer**: Python models with custom methods and properties
4. **Presentation Layer**: Bootstrap-based responsive UI
5. **Security Layer**: Role-based access control and audit logging

**Deployment Architecture:**
- **Development**: Local server via Django's development server on localhost:8000
- **Database**: XAMPP MySQL server on localhost:3306
- **Static Files**: Served via Django's staticfiles system
- **Media Files**: User uploads stored in /media directory

### 1.4 System Requirements

**Server Requirements:**
- Windows 10 or higher / Linux / macOS
- Python 3.8 or higher
- MySQL 8.0 or MariaDB 10.5+
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

**Client Requirements:**
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection (for initial setup and updates)
- Screen resolution: 1280x720 minimum

---

## 2. User Roles & Permissions

The UPG System implements a hierarchical role-based access control system. Each role has specific permissions across different modules.

### 2.1 Role Definitions

#### County Executive (CECM & Governor)
**Access Level**: Executive Overview
**Primary Functions**: Strategic oversight, high-level reporting, grant approval
**Full Access Modules**:
- Dashboard (executive view)
- Grants (view and approve)
- Reports (comprehensive)

**Read-Only Access**:
- Programs
- Households
- Business Groups
- Savings Groups
- Training

**Restricted Access**:
- No direct access to Settings
- Cannot modify training or household data

#### County Assembly Member
**Access Level**: Legislative Oversight
**Primary Functions**: Monitoring, program review, report viewing
**Full Access Modules**:
- Dashboard (legislative view)
- Reports

**Read-Only Access**:
- Programs
- Households
- Business Groups
- Savings Groups

#### ICT Administrator
**Access Level**: System Administrator
**Primary Functions**: System configuration, user management, full data access
**Full Access Modules**: ALL modules including:
- Dashboard (admin view)
- Programs
- Households
- Business Groups
- Savings Groups
- Surveys
- Training
- Grants
- Reports
- Settings
- User Management

#### M&E (Monitoring & Evaluation) Staff
**Access Level**: Program Management
**Primary Functions**: Data collection, report generation, program monitoring
**Full Access Modules**:
- Dashboard (M&E view)
- Programs
- Households
- Business Groups
- Savings Groups
- Surveys
- Training
- Reports

**Read-Only Access**:
- Grants

#### Field Associate / Mentor Supervisor
**Access Level**: Field Operations Management
**Primary Functions**: Mentor oversight, training coordination, field data entry
**Full Access Modules**:
- Dashboard (field associate view)
- Households
- Business Groups
- Savings Groups
- Surveys
- Training
- Grants (application and tracking)

**Read-Only Access**:
- Programs
- Reports

#### Mentor (Business Mentor)
**Access Level**: Direct Beneficiary Interaction
**Primary Functions**: Training delivery, household visits, mentoring, data collection
**Full Access Modules**:
- Dashboard (mentor view)
- Households (assigned only)
- Business Groups (assigned only)
- Savings Groups (assigned only)
- Surveys (data collection)
- Training (assigned trainings)

**Read-Only Access**:
- Programs
- Reports (limited to own activities)

#### Beneficiary
**Access Level**: Self-service View
**Primary Functions**: View own household data, program participation
**Full Access Modules**:
- Dashboard (beneficiary view)

**Read-Only Access**:
- Own household information
- Business group participation
- Savings group participation
- Training schedules

### 2.2 Permission Matrix

| Module | County Exec | Assembly | ICT Admin | M&E Staff | Field Associate | Mentor | Beneficiary |
|--------|-------------|----------|-----------|-----------|-----------------|--------|-------------|
| **Dashboard** | Full | Full | Full | Full | Full | Full | Read |
| **Programs** | Read | Read | Full | Full | Read | Read | Read |
| **Households** | Read | Read | Full | Full | Full | Full (assigned) | Read (own) |
| **Business Groups** | Read | Read | Full | Full | Full | Full (assigned) | Read (own) |
| **Savings Groups** | Read | Read | Full | Full | Full | Full (assigned) | Read (own) |
| **Training** | Read | - | Full | Full | Full | Full (assigned) | Read |
| **Surveys** | - | - | Full | Full | Full | Full | - |
| **Grants** | Full | - | Full | Read | Full | - | - |
| **UPG Grants** | Approve | - | Full | Read | Full | - | - |
| **Reports** | Full | Full | Full | Full | Read | Read | - |
| **Settings** | - | - | Full | - | - | - | - |
| **Forms** | - | - | Full | Full | Full (assigned) | Full (assigned) | - |

**Legend:**
- **Full**: Create, Read, Update, Delete
- **Read**: View only
- **-**: No access

---

## 3. Module Documentation

### 3.1 Accounts Module

**Purpose**: User authentication, registration, and profile management

#### Features:
1. **User Registration & Login**
   - Secure login with username and password
   - Session management (1-hour timeout)
   - Password reset functionality
   - Email-based password recovery

2. **User Profile Management**
   - Profile information (avatar, bio)
   - Village assignments for mentors
   - Activity tracking

3. **Password Reset Flow**
   - Forgot password request
   - Token-based reset (24-hour validity)
   - Email notification
   - Secure password update

#### User Model Fields:
- Username (unique)
- Email (unique)
- First Name, Last Name
- Role (from predefined choices)
- Phone Number
- Office/Location
- Country (default: Kenya)
- Active status
- Created/Updated timestamps

#### Key URLs:
- `/accounts/login/` - Login page
- `/accounts/logout/` - Logout
- `/accounts/profile/` - User profile
- `/accounts/forgot-password/` - Password reset request
- `/accounts/reset-password/<token>/` - Password reset form

#### How to Use:

**Logging In:**
1. Navigate to the system URL (e.g., http://localhost:8000)
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to your role-specific dashboard

**Resetting Password:**
1. Click "Forgot Password?" on login page
2. Enter your registered email address
3. Check your email for reset link
4. Click the link and enter new password
5. Confirm new password
6. Return to login page

---

### 3.2 Core Module

**Purpose**: Core system entities and geographical data management

#### Key Entities:

**1. Counties**
- Manages county-level geographical data
- Links to sub-counties and villages
- Supports multi-county programs

**2. Sub-Counties**
- Second-level administrative divisions
- Linked to parent county
- Contains multiple villages

**3. Villages**
- Lowest level of geographic organization
- Tracks saturation levels
- Distance to market (in kilometers)
- Program area designation
- Qualified households count

**4. Mentors**
- Business mentor contact information
- Linked to user accounts
- Country and office information

**5. Business Mentor Cycles (BM Cycles)**
- Training cycle management
- Links mentors to field associates
- Project and office tracking
- Cycle identifier (e.g., FY25C1)

**6. Programs**
- Program definition and management
- Start/end dates
- Target households and villages
- Status tracking (planning, active, completed, suspended)
- Budget and cycle information

**7. Audit Logs**
- Complete system activity tracking
- User actions (create, update, delete, view, login, logout)
- IP address logging
- Timestamp tracking
- Change descriptions

**8. ESR Import System**
- External Service Record import tracking
- File upload and processing
- Success/failure tracking
- Error logging
- Support for household, business group, savings group, and survey data

**9. SMS Logging**
- SMS notification tracking
- Provider tracking (Africa's Talking, Twilio)
- Success/failure status
- Delivery timestamps
- Linked to households, trainings, and mentors

#### Key Features:

**Geographic Hierarchy:**
```
Country (Kenya)
  └── County
       └── Sub-County
            └── Village
                 └── Households
```

**Audit Trail:**
- Every significant action is logged
- User identity tracking
- IP address recording
- Detailed change descriptions
- Searchable audit history

**SMS Integration:**
- Africa's Talking API (primary)
- Twilio API (fallback)
- Configurable sender ID
- Delivery status tracking
- Error handling and logging

---

### 3.3 Households Module

**Purpose**: Comprehensive household data management and eligibility tracking

#### Key Entities:

**1. Household**
Complete household information including:
- Geographic/Administrative Information:
  - Village, Sub-County, County
  - Constituency, District, Division
  - Location, Sub-Location
  - GPS Coordinates (latitude/longitude)

- Household Head Information:
  - Full name (first, middle, last)
  - Gender, Date of Birth
  - National ID Number
  - Phone Number

- Socio-Economic Data:
  - Monthly income
  - Assets (stored as JSON)
  - Electricity access
  - Clean water access
  - Location type (rural/urban/remote)
  - Disability status

- Program Participation:
  - Consent status
  - Eligibility assessments
  - Program enrollment tracking

**2. PPI (Poverty Probability Index)**
- Household poverty scoring
- Eligibility score (0-100)
- Assessment date
- Baseline, midline, endline tracking

**3. Household Members**
- Individual member records
- Relationship to household head
- Age, gender, education level
- ID/Birth certificate numbers
- Program participation flag

**4. Household Programs**
- Program participation tracking
- Enrollment/graduation dates
- Mentor assignment
- Participation status:
  - Eligible
  - Enrolled
  - Active
  - Graduated
  - Dropped Out
- Dropout reason tracking

**5. UPG Milestones**
12-month graduation milestones:
- Month 1: PPI Assessment & Business Training Start
- Month 2: Business Group Formation
- Month 3: Business Plan Development
- Month 4: SB Grant Application
- Month 5: SB Grant Disbursement
- Month 6: Business Operations Start
- Month 7: Mid-term Assessment
- Month 8: Business Savings Group Formation
- Month 9: PR Grant Eligibility Assessment
- Month 10: PR Grant Application
- Month 11: Final Business Assessment
- Month 12: Graduation Assessment

Milestone Statuses:
- Not Started
- In Progress
- Completed
- Delayed
- Skipped

**6. Household Surveys**
- Baseline, midline, endline surveys
- Income level tracking
- Assets inventory
- Savings amount
- Survey date and surveyor tracking

#### Eligibility Assessment System:

The system includes comprehensive eligibility assessment tools:

**Quick Eligibility Check:**
- Basic criteria validation
- PPI score verification
- Consent verification

**Comprehensive Scoring:**
- Multi-factor eligibility calculation
- Weighted scoring system
- Automatic qualification recommendations

**Household Qualification Tool:**
- Full qualification assessment
- Detailed eligibility reports
- Program-specific criteria evaluation

#### Key URLs:
- `/households/` - Household list
- `/households/add/` - Add new household
- `/households/<id>/` - Household detail
- `/households/<id>/edit/` - Edit household
- `/households/<id>/members/` - Manage household members
- `/households/<id>/eligibility/` - Run eligibility assessment
- `/households/<id>/milestones/` - Track UPG milestones

#### How to Use:

**Adding a Household:**
1. Navigate to Households module
2. Click "Add Household"
3. Fill in required fields:
   - Household head information
   - Geographic location
   - Contact details
4. Save the household
5. Add household members
6. Run eligibility assessment

**Tracking Milestones:**
1. Open household detail page
2. Click "UPG Milestones"
3. View 12-month milestone tracker
4. Update milestone status
5. Add completion dates and notes
6. Track overdue milestones

---

### 3.4 Business Groups Module

**Purpose**: Management of entrepreneurial business groups formed by program participants

#### Key Entities:

**1. Business Group**
Core business group information:
- Group name and formation date
- Program linkage
- Business type categories:
  - Crop
  - Retail
  - Service
  - Livestock
  - Skill
- Business type detail (e.g., cereal, barber shop)
- Group size (typically 2-3 entrepreneurs)
- Current business health status:
  - Red: Poor Performance
  - Yellow: Fair Performance
  - Green: Good Performance
- Participation status:
  - Active
  - Withdrawn
  - Suspended

**2. Business Group Members**
Member management:
- Household linkage
- Role in group:
  - Leader
  - Treasurer
  - Secretary
  - Member
- Joined date
- Active status
- One household per business group (unique constraint)

**3. SB Grant (Seed Business Grant)**
Initial capital grants:
- Business group linkage
- Business type and details
- Funding status:
  - Applied
  - Approved
  - Funded
  - Not Funded
- Grant amount (configurable)
- Funded date
- Group leadership details:
  - Leader name
  - Treasurer name
  - Secretary name

**4. PR Grant (Performance Recognition Grant)**
Second-tier performance-based grants:
- Business group linkage
- Business type
- Funding status (same options as SB Grant)
- Grant amount
- Funded date
- Leadership details
- Performance qualification justification

**5. Business Progress Surveys**
Regular progress tracking:
- Survey date and surveyor
- Financial metrics:
  - Grant value
  - Grant used
  - Profit generated
  - Business inputs
  - Business inventory
  - Business cash on hand

#### Business Health Assessment:

The system tracks business health using a color-coded system:

**Green (Good Performance):**
- Regular profit generation
- Full utilization of grants
- Growing inventory and cash reserves
- Consistent member participation

**Yellow (Fair Performance):**
- Moderate profit generation
- Partial grant utilization
- Stable but not growing
- Some member participation issues

**Red (Poor Performance):**
- Little to no profit
- Poor grant utilization
- Declining inventory
- Member dropout or conflict

#### Key URLs:
- `/business-groups/` - Business group list
- `/business-groups/add/` - Create new business group
- `/business-groups/<id>/` - Business group detail
- `/business-groups/<id>/edit/` - Edit business group
- `/business-groups/<id>/members/` - Manage members
- `/business-groups/<id>/progress/` - Track progress surveys
- `/business-groups/<id>/sb-grant/` - SB Grant application
- `/business-groups/<id>/pr-grant/` - PR Grant application

#### How to Use:

**Forming a Business Group:**
1. Navigate to Business Groups module
2. Click "Create Business Group"
3. Enter group details:
   - Group name
   - Business type
   - Formation date
4. Add group members (2-3 households)
5. Assign roles (Leader, Treasurer, Secretary)
6. Save the group

**Applying for SB Grant:**
1. Open business group detail page
2. Click "Apply for SB Grant"
3. Fill in application:
   - Business plan
   - Required grant amount
   - Leadership confirmation
4. Submit application
5. Await review and approval
6. Track funding status

**Tracking Business Progress:**
1. Open business group detail page
2. Click "Add Progress Survey"
3. Enter financial data:
   - Grant utilization
   - Profit/loss
   - Inventory levels
   - Cash on hand
4. Update business health status
5. Save survey

---

### 3.5 Savings Groups Module

**Purpose**: Community-based savings group management and tracking

#### Key Entities:

**1. Business Savings Group (BSG)**
Community savings entities:
- Group name and formation date
- Business group linkages (many-to-many)
- Member count and targets
- Savings to date (cumulative)
- Meeting details:
  - Meeting day (e.g., every Tuesday)
  - Meeting location
  - Savings frequency (weekly, bi-weekly, monthly)
- Active status

**2. BSG Members**
Individual member tracking:
- Household linkage
- Role in savings group:
  - Chairperson
  - Secretary
  - Treasurer
  - Member
- Joined date
- Total savings accumulated
- Active status

**3. Savings Records**
Individual savings transactions:
- BSG and member linkage
- Savings amount
- Savings date
- Recorded by (user)
- Notes
- Chronological tracking

**4. BSG Progress Surveys**
Monthly performance tracking:
- Survey date
- Savings last month
- Month recorded
- Attendance at meeting
- Surveyor information

#### Savings Group Features:

**Automatic Calculations:**
- Total members (individual + business group members)
- Cumulative savings
- Average savings per member
- Attendance rates
- Monthly savings trends

**Meeting Management:**
- Regular meeting schedules
- Location tracking
- Attendance recording
- Savings collection tracking

**Financial Tracking:**
- Individual member savings
- Group cumulative savings
- Monthly savings patterns
- Withdrawal tracking (if applicable)

#### Key URLs:
- `/savings-groups/` - Savings group list
- `/savings-groups/add/` - Create new savings group
- `/savings-groups/<id>/` - Savings group detail
- `/savings-groups/<id>/edit/` - Edit savings group
- `/savings-groups/<id>/members/` - Manage members
- `/savings-groups/<id>/savings/` - Record savings
- `/savings-groups/<id>/progress/` - Progress surveys

#### How to Use:

**Creating a Savings Group:**
1. Navigate to Savings Groups module
2. Click "Create Savings Group"
3. Enter group details:
   - Group name
   - Target member count
   - Meeting schedule
   - Meeting location
4. Link business groups (if applicable)
5. Add individual members
6. Assign roles (Chairperson, Secretary, Treasurer)
7. Save the group

**Recording Savings:**
1. Open savings group detail page
2. Click "Record Savings"
3. Select member
4. Enter amount saved
5. Add date and notes
6. Save transaction
7. View updated member total savings

**Monthly Progress Tracking:**
1. Open savings group detail page
2. Click "Add Progress Survey"
3. Enter:
   - Total savings for the month
   - Meeting attendance
   - Month being recorded
4. Save survey
5. View savings trends over time

---

### 3.6 Training Module

**Purpose**: Comprehensive training and mentoring activity management

#### Key Entities:

**1. Training**
Training modules and sessions:
- Name and module ID
- Module number (sequential)
- BM Cycle linkage
- Assigned mentor
- Training details:
  - Duration in hours
  - Location/venue
  - Participant count
  - Training dates (multiple sessions)
- Status:
  - Planned
  - Active
  - Completed
  - Cancelled
- Start and end dates
- Maximum households per training (default: 25)
- Description

**2. Training Attendance**
Attendance tracking:
- Training linkage
- Household linkage
- Attendance status (present/absent)
- Training date
- Marked by (mentor)
- Attendance marked timestamp

**3. Household Training Enrollment**
Enrollment management:
- One household per training rule
- Training linkage
- Enrollment date
- Enrollment status:
  - Enrolled
  - Completed
  - Dropped Out
  - Transferred
- Completion date

**4. Mentoring Visits**
On-site household visits:
- Visit name and household
- Mentor
- Topic covered
- Visit type:
  - On-site
  - Phone Check
  - Virtual
- Visit date
- Detailed notes

**5. Phone Nudges**
Phone call tracking:
- Household and mentor
- Nudge type:
  - Training Reminder
  - Follow-up Call
  - Support Call
  - Regular Check-in
  - Business Advice
- Call date and time
- Duration in minutes
- Successful contact status
- Call notes

**6. Mentoring Reports**
Periodic mentor reporting:
- Reporting period (weekly, monthly, quarterly)
- Period start and end dates
- Summary statistics:
  - Households visited
  - Phone nudges made
  - Trainings conducted
  - New households enrolled
- Narrative report:
  - Key activities
  - Challenges faced
  - Successes achieved
  - Next period plans

#### Training System Features:

**Enrollment Management:**
- Automatic slot tracking (25 max per training)
- Available slots calculation
- One household per training enforcement
- Enrollment status tracking

**Attendance Tracking:**
- Session-by-session attendance
- Mentor-marked attendance
- Timestamp tracking
- Attendance rate calculations

**Mentoring Activity Tracking:**
- Comprehensive visit logging
- Phone call documentation
- Activity type categorization
- Time tracking
- Success rate monitoring

**Reporting System:**
- Structured periodic reports
- Statistical summaries
- Narrative reporting
- Challenge documentation
- Success tracking

#### Key URLs:
- `/training/` - Training list
- `/training/add/` - Create new training
- `/training/<id>/` - Training detail
- `/training/<id>/edit/` - Edit training
- `/training/<id>/attendance/` - Mark attendance
- `/training/<id>/enroll/` - Enroll households
- `/training/mentoring-visits/` - Mentoring visit list
- `/training/mentoring-visits/add/` - Add visit
- `/training/phone-nudges/` - Phone nudge list
- `/training/phone-nudges/add/` - Add phone nudge
- `/training/reports/` - Mentoring reports
- `/training/reports/add/` - Create report

#### How to Use:

**Creating a Training:**
1. Navigate to Training module
2. Click "Create Training"
3. Enter training details:
   - Name and module number
   - BM Cycle
   - Assigned mentor
   - Location and duration
   - Training dates
4. Set maximum households (default 25)
5. Save training

**Enrolling Households:**
1. Open training detail page
2. Click "Enroll Households"
3. Select households from available list
4. System checks:
   - Available slots
   - Household not in another training
5. Confirm enrollments

**Marking Attendance:**
1. Open training detail page
2. Click "Mark Attendance"
3. Select training date
4. Check attendance for each household
5. Save attendance
6. View attendance rates

**Recording Mentoring Visit:**
1. Navigate to Mentoring Visits
2. Click "Add Visit"
3. Enter visit details:
   - Household visited
   - Visit type (on-site, phone, virtual)
   - Topic covered
   - Visit date
   - Detailed notes
4. Save visit

**Logging Phone Nudges:**
1. Navigate to Phone Nudges
2. Click "Add Phone Nudge"
3. Enter call details:
   - Household called
   - Nudge type
   - Call date/time
   - Duration
   - Successful contact (yes/no)
   - Call notes
4. Save nudge

**Submitting Mentoring Report:**
1. Navigate to Mentoring Reports
2. Click "Create Report"
3. Select reporting period
4. Enter period dates
5. Fill in statistics:
   - Households visited
   - Phone calls made
   - Trainings conducted
6. Write narrative:
   - Key activities
   - Challenges
   - Successes
   - Next period plans
7. Submit report

---

### 3.7 Surveys Module

**Purpose**: Dynamic survey and data collection management

#### Key Entities:

**1. Survey**
Survey definitions:
- Name and description
- Version tracking
- Active status
- Created by (M&E staff)
- Creation date

**2. Survey Response**
Survey submissions:
- Survey linkage
- Respondent (household)
- Surveyor (user)
- Response data (JSON format)
- Completed status
- Submission timestamp

#### Survey Features:

**Dynamic Survey Creation:**
- Flexible survey structure
- Multiple question types
- Version control
- Activation/deactivation

**Response Collection:**
- Mobile-friendly data entry
- JSON-based data storage
- Respondent tracking
- Completion status
- Surveyor attribution

**Data Management:**
- Structured data storage
- Easy export capabilities
- Response aggregation
- Version comparison

#### Key URLs:
- `/surveys/` - Survey list
- `/surveys/add/` - Create new survey
- `/surveys/<id>/` - Survey detail
- `/surveys/<id>/edit/` - Edit survey
- `/surveys/<id>/respond/` - Fill survey
- `/surveys/<id>/responses/` - View responses

#### How to Use:

**Creating a Survey (M&E Staff):**
1. Navigate to Surveys module
2. Click "Create Survey"
3. Enter survey name and description
4. Set version number
5. Define survey questions (in survey structure)
6. Activate survey
7. Assign to field staff/mentors

**Filling a Survey (Mentor/Field Associate):**
1. Navigate to assigned surveys
2. Select survey to complete
3. Select household (respondent)
4. Fill in all required fields
5. Review responses
6. Submit survey
7. Confirmation message displayed

---

### 3.8 Programs Module

**Purpose**: Independent program creation and management beyond UPG

#### Key Entities:

**1. Program**
Program definitions:
- Name and description (unique)
- Program type:
  - Ultra-Poor Graduation
  - Microfinance
  - Agricultural Support
  - Education Support
  - Health Initiative
  - Infrastructure Development
  - Skills Training
  - Youth Empowerment
  - Women Empowerment
  - Other
- Status:
  - Draft
  - Active
  - Suspended
  - Completed
  - Cancelled
- Budget and target beneficiaries
- Duration in months
- Start/end dates
- Application deadline
- Created by (County Executive or ICT Admin)
- County and sub-county
- Eligibility criteria
- Application requirements
- Flags:
  - Accepting applications
  - Requires approval

**2. Program Application**
Household applications to programs:
- Program and household linkage
- Application status:
  - Pending Review
  - Under Review
  - Approved
  - Rejected
  - Waitlisted
  - Withdrawn
- Application date
- Motivation letter
- Additional notes
- Review process:
  - Reviewed by (user)
  - Review date
  - Review notes
- Approval process:
  - Approved by (user)
  - Approval date

**3. Program Beneficiary**
Active program participants:
- Program and household linkage
- Participation status:
  - Active
  - Suspended
  - Graduated
  - Dropped Out
  - Terminated
- Enrollment date
- Graduation date
- Progress notes
- Benefits received (monetary value)

#### Program Features:

**UPG-Specific Features:**
Programs with type "Ultra-Poor Graduation" automatically support:
- PPI scoring requirement
- Business group formation
- Savings group formation
- Graduation milestone tracking
- SB/PR grant eligibility
- 12-month default duration

**Application Workflow:**
1. Household submits application
2. Status: Pending Review
3. Staff reviews application
4. Status: Under Review
5. Approval/rejection decision
6. Status: Approved/Rejected
7. If approved, household becomes beneficiary

**Beneficiary Tracking:**
- Enrollment tracking
- Progress monitoring
- Benefits quantification
- Graduation pathway
- Dropout management

#### Key URLs:
- `/programs/` - Program list
- `/programs/add/` - Create new program
- `/programs/<id>/` - Program detail
- `/programs/<id>/edit/` - Edit program
- `/programs/<id>/apply/` - Submit application
- `/programs/<id>/applications/` - View applications
- `/programs/<id>/beneficiaries/` - View beneficiaries

#### How to Use:

**Creating a Program (County Executive):**
1. Navigate to Programs module
2. Click "Create Program"
3. Enter program details:
   - Name and description
   - Program type
   - Budget and targets
   - Duration
   - Start/end dates
4. Define eligibility criteria
5. List application requirements
6. Set application deadline
7. Enable "Accepting Applications"
8. Save program

**Applying to Program (Household):**
1. Navigate to Programs
2. Browse available programs
3. Click "Apply" on desired program
4. Read eligibility criteria
5. Fill application form:
   - Motivation letter
   - Supporting information
6. Submit application
7. Track application status

**Reviewing Applications (Staff):**
1. Navigate to program applications
2. Filter by status (Pending Review)
3. Open application for review
4. Read application details
5. Check eligibility
6. Add review notes
7. Approve or reject application
8. System updates status

**Managing Beneficiaries:**
1. Navigate to program beneficiaries
2. View enrolled households
3. Track progress
4. Update participation status
5. Record benefits received
6. Manage graduations or dropouts

---

### 3.9 Grants Module

**Purpose**: Basic grant management functionality

The Grants module provides foundational grant management capabilities that are extended by the UPG Grants module for program-specific grant types.

#### Key URLs:
- `/grants/` - Grant list
- `/grants/add/` - Create grant
- `/grants/<id>/` - Grant detail

---

### 3.10 UPG Grants Module

**Purpose**: Comprehensive UPG-specific grant management (SB & PR grants)

#### Key Entities:

**1. Household Grant Application**
Universal grant application system:
- Applicant types:
  - Individual household
  - Business group
  - Savings group
- Submitted by (user)
- Program linkage (optional)
- Grant types:
  - Seed Business Grant
  - Performance Recognition Grant
  - Livelihood Grant
  - Emergency Grant
  - Education Support Grant
  - Housing Improvement Grant
  - Other
- Status workflow:
  - Draft
  - Submitted
  - Under Review
  - Approved
  - Rejected
  - Disbursed
  - Cancelled
- Financial details:
  - Requested amount
  - Approved amount
  - Disbursed amount
- Application content:
  - Title and purpose
  - Business plan
  - Expected outcomes
  - Budget breakdown (JSON)
  - Supporting documents
- Review process:
  - Reviewed by
  - Review date
  - Review notes
  - Review score (0-100)
- Approval process:
  - Approved by (requires specific roles)
  - Approval date
  - Approval notes
- Disbursement tracking:
  - Disbursement date
  - Disbursed amount
  - Disbursed by
  - Disbursement method (bank transfer, mobile money, cash, check)
  - Reference number
- Utilization tracking:
  - Utilization report
  - Final outcomes

**2. SB Grant (Seed Business Grant)**
Initial seed capital for business groups:
- Program and applicant linkage
- Submitted by
- Grant amount calculations:
  - Base grant amount (default: 15,000 KES)
  - Calculated grant amount (auto-calculated)
  - Final grant amount (approved amount)
- Calculation factors:
  - Group size factor (multiplier based on group size)
  - Business type factor (multiplier based on business type)
  - Location factor (geographic adjustment)
  - Performance factor (based on training completion, etc.)
- Status:
  - Pending
  - Under Review
  - Approved
  - Disbursed
  - Rejected
  - Cancelled
- Disbursement status:
  - Not Disbursed
  - Partially Disbursed
  - Fully Disbursed
- Application details:
  - Business plan
  - Projected income
  - Startup costs
  - Monthly expenses
- Review and approval process
- Disbursement tracking
- Utilization reporting

**Grant Amount Calculation Algorithm:**
```
Base Amount = 15,000 KES

Group Size Factor:
- 20+ members: 1.20 (20% bonus)
- 15-19 members: 1.10 (10% bonus)
- 8-14 members: 1.00 (standard)
- <8 members: 0.90 (10% reduction)

Business Type Factor:
- Agriculture/Livestock: 1.15 (15% bonus)
- Manufacturing/Processing: 1.10 (10% bonus)
- Others: 1.00 (standard)

Location Factor:
- Remote/Rural: 1.05 (5% bonus)
- Urban: 1.00 (standard)

Performance Factor:
- Training completion ≥90%: 1.10 (10% bonus)
- Training completion 60-89%: 1.00 (standard)
- Training completion <60%: 0.95 (5% reduction)

Calculated Amount = Base × Group Size × Business Type × Location × Performance

Caps:
- Maximum: 25,000 KES
- Minimum: 10,000 KES
```

**3. PR Grant (Performance Recognition Grant)**
Performance-based second grant:
- Requires successful SB Grant completion
- Program and applicant linkage
- SB Grant linkage (required)
- Grant amount (default: 10,000 KES)
- Status:
  - Not Eligible Yet
  - Eligible
  - Pending
  - Under Review
  - Approved
  - Disbursed
  - Rejected
  - Cancelled
- Performance assessment:
  - Performance score (0-100)
  - Performance rating:
    - Excellent Performance
    - Good Performance
    - Satisfactory Performance
    - Poor Performance
  - Performance assessment narrative
- Business metrics:
  - Revenue generated
  - Jobs created
  - Savings accumulated
- Eligibility assessment:
  - Assessed by
  - Assessment date
- Approval and disbursement tracking

**PR Grant Eligibility Criteria:**
1. SB Grant must be fully disbursed
2. SB Grant utilization report must be completed
3. Business performance metrics must meet minimum standards
4. Training completion requirements met
5. Savings group participation (for graduation programs)

**4. Grant Disbursement**
Individual disbursement transaction tracking:
- Grant linkage (SB or PR)
- Disbursement type
- Amount
- Disbursement date
- Method (bank transfer, mobile money, cash, check)
- Transaction details:
  - Reference number
  - Recipient name
  - Recipient contact
- Processed by (user)
- Processing notes

#### Grant Management Features:

**Automatic Calculations:**
- SB Grant amount auto-calculation based on multiple factors
- Remaining amount tracking
- Disbursement percentage calculation
- Eligibility scoring

**Workflow Management:**
- Draft → Submitted → Under Review → Approved → Disbursed
- Role-based approval requirements
- Review score assignment
- Approval notes and documentation

**Financial Tracking:**
- Requested vs. approved amounts
- Partial disbursement support
- Multiple disbursement transactions
- Utilization tracking
- Final outcome reporting

**Reporting:**
- Grant pipeline reports
- Disbursement reports
- Utilization reports
- Performance analysis

#### Key URLs:
- `/upg-grants/` - UPG grant list
- `/upg-grants/household-applications/` - Household grant applications
- `/upg-grants/household-applications/add/` - New household grant application
- `/upg-grants/sb-grants/` - SB Grant list
- `/upg-grants/sb-grants/add/` - New SB Grant application
- `/upg-grants/sb-grants/<id>/` - SB Grant detail
- `/upg-grants/pr-grants/` - PR Grant list
- `/upg-grants/pr-grants/add/` - New PR Grant application
- `/upg-grants/pr-grants/<id>/` - PR Grant detail
- `/upg-grants/pr-grants/<id>/eligibility/` - Check PR Grant eligibility
- `/upg-grants/disbursements/` - Disbursement list

#### How to Use:

**Applying for Household Grant:**
1. Navigate to UPG Grants → Household Grant Applications
2. Click "New Application"
3. Select applicant type (household, business group, or savings group)
4. Select specific applicant
5. Choose grant type
6. Enter requested amount
7. Fill in application:
   - Title and purpose
   - Business plan (if applicable)
   - Expected outcomes
   - Budget breakdown
8. Upload supporting documents
9. Save as draft or submit
10. Track application status

**Applying for SB Grant (Business Group):**
1. Ensure business group is formed
2. Navigate to UPG Grants → SB Grants
3. Click "New SB Grant Application"
4. Select business group
5. System auto-calculates grant amount
6. Review calculation factors:
   - Group size
   - Business type
   - Location
   - Training performance
7. Fill in business plan:
   - Projected income
   - Startup costs
   - Monthly expenses
8. Submit application
9. System creates application with calculated amount

**Reviewing Grant Application:**
1. Navigate to pending applications
2. Open application for review
3. Check eligibility criteria
4. Review business plan and financials
5. Assign review score (0-100)
6. Add review notes
7. Update status to "Under Review"
8. Submit for approval or reject

**Approving Grant (County Executive/Director):**
1. Navigate to applications under review
2. Open application
3. Review all documentation:
   - Application details
   - Review notes
   - Review score
4. Make approval decision:
   - Approve: Set approved amount
   - Reject: Provide rejection reason
5. Add approval notes
6. Confirm approval/rejection
7. System updates status

**Disbursing Grant:**
1. Navigate to approved grants
2. Select grant for disbursement
3. Verify approved amount
4. Click "Disburse Funds"
5. Enter disbursement details:
   - Amount (full or partial)
   - Disbursement date
   - Method (bank, mobile money, cash)
   - Reference number
   - Recipient details
6. Add processing notes
7. Confirm disbursement
8. System records transaction
9. System updates disbursement status

**Applying for PR Grant:**
1. Ensure SB Grant is disbursed
2. Complete SB Grant utilization report
3. Navigate to UPG Grants → PR Grants
4. Click "New PR Grant Application"
5. Select business group with SB Grant
6. System checks eligibility:
   - SB Grant disbursed
   - Utilization report completed
   - Performance metrics
7. If eligible, fill in PR application:
   - Performance assessment
   - Revenue generated
   - Jobs created
   - Savings accumulated
8. Submit PR Grant application
9. Follow same review/approval/disbursement workflow

**Recording Grant Utilization:**
1. Navigate to disbursed grants
2. Open grant detail
3. Click "Add Utilization Report"
4. Enter:
   - How funds were used
   - Items purchased
   - Outcomes achieved
5. Upload receipts/photos (if applicable)
6. Set utilization date
7. Save report
8. Mark grant as "Utilized"

---

### 3.11 Forms Module

**Purpose**: Dynamic forms system for M&E staff to create and assign surveys

#### Key Entities:

**1. Form Template**
Dynamic form definitions:
- Name and description
- Form type:
  - Household Survey
  - Business Progress Survey
  - PPI Assessment
  - Baseline Survey
  - Midline Survey
  - Endline Survey
  - Training Evaluation
  - Mentoring Report
  - Custom Form
- Status:
  - Draft
  - Active
  - Inactive
  - Archived
- Form structure (JSON-based field definitions)
- Created by (M&E staff)
- Form settings:
  - Allow multiple submissions
  - Require photo evidence
  - Require GPS location
  - Auto-assign to mentors

**2. Form Field**
Individual field definitions:
- Form template linkage
- Field name and label
- Field type:
  - Text Input
  - Text Area
  - Number Input
  - Email Input
  - Phone Number
  - Date Picker
  - Date & Time
  - Dropdown Select
  - Radio Buttons
  - Checkboxes
  - Yes/No
  - File Upload
  - Image Upload
  - Rating Scale
  - GPS Location
  - Digital Signature
- Field configuration:
  - Required/optional
  - Help text
  - Placeholder
  - Default value
- Choice options (for select/radio/checkbox)
- Validation rules:
  - Min/max length
  - Min/max value
  - Regex pattern
- Display order
- Conditional display rules

**3. Form Assignment**
Assignment of forms to field staff:
- Form template linkage
- Assigned by (M&E staff)
- Assignment type:
  - Direct to Mentor
  - Via Field Associate
- Assignee (field associate or mentor)
- Assignment details:
  - Title and instructions
  - Due date
  - Priority (low, medium, high, urgent)
- Status:
  - Pending
  - Accepted
  - In Progress
  - Completed
  - Overdue
  - Cancelled
- Target criteria:
  - Target villages (JSON list)
  - Target households (JSON list)
  - Target business groups (JSON list)
  - Minimum submissions required

**4. Form Assignment Mentor**
Field associate delegation to mentors:
- Assignment linkage
- Mentor
- Assigned by field associate
- Instructions
- Due date
- Status tracking

**5. Form Submission**
Completed form submissions:
- Assignment and form template linkage
- Submitted by (mentor/field associate)
- Submission date
- Form data (JSON)
- Attachments:
  - Photo evidence
  - Document attachments
- Location data:
  - GPS latitude/longitude
  - Location name
- Status:
  - Draft
  - Submitted
  - Reviewed
  - Approved
  - Rejected
- Review process:
  - Reviewed by
  - Review date
  - Review notes
- Entity linkages:
  - Household
  - Business group

#### Forms System Features:

**Dynamic Form Builder:**
- Drag-and-drop field creation (conceptual)
- Multiple field types
- Conditional logic
- Validation rules
- Custom field ordering

**Assignment Workflow:**
```
M&E Staff creates form template
    ↓
M&E Staff assigns to Field Associate or Mentor
    ↓
Field Associate (optional) reassigns to Mentors
    ↓
Mentor receives assignment notification
    ↓
Mentor accepts and starts form
    ↓
Mentor completes form in field
    ↓
Mentor submits form
    ↓
M&E Staff reviews submission
    ↓
M&E Staff approves or requests revision
```

**Mobile Data Collection:**
- GPS location capture
- Photo evidence upload
- Offline data entry (conceptual)
- GPS-based field verification

**Data Quality:**
- Required field enforcement
- Validation rules
- Review and approval workflow
- Revision tracking

#### Key URLs:
- `/forms/` - Form template list
- `/forms/create/` - Create new form template
- `/forms/<id>/` - Form template detail
- `/forms/<id>/edit/` - Edit form template
- `/forms/<id>/fields/` - Manage form fields
- `/forms/<id>/assign/` - Assign form
- `/forms/assignments/` - My form assignments
- `/forms/assignments/<id>/` - Assignment detail
- `/forms/assignments/<id>/submit/` - Submit form
- `/forms/submissions/` - Submission list
- `/forms/submissions/<id>/` - Submission detail
- `/forms/submissions/<id>/review/` - Review submission

#### How to Use:

**Creating a Form Template (M&E Staff):**
1. Navigate to Forms module
2. Click "Create Form Template"
3. Enter form details:
   - Name and description
   - Form type
4. Add form fields:
   - Click "Add Field"
   - Select field type
   - Configure field properties
   - Set validation rules
   - Add help text
   - Set display order
5. Configure form settings:
   - Multiple submissions allowed
   - Photo evidence required
   - GPS location required
6. Save form as draft
7. Test form
8. Activate form

**Assigning Form to Field Staff:**
1. Open form template
2. Click "Assign Form"
3. Choose assignment type:
   - Direct to Mentor
   - Via Field Associate
4. Select assignee(s)
5. Enter assignment details:
   - Title and instructions
   - Due date
   - Priority level
6. Set target criteria (optional):
   - Specific villages
   - Specific households
   - Specific business groups
7. Set minimum submissions required
8. Send assignment

**Field Associate Delegating to Mentors:**
1. View assigned forms
2. Open assignment
3. Click "Assign to Mentors"
4. Select mentors
5. Add specific instructions for each mentor
6. Set individual due dates
7. Confirm assignments

**Completing Form (Mentor):**
1. View assigned forms
2. Open assignment
3. Click "Fill Form"
4. Select target entity (household/business group)
5. Fill all required fields
6. Capture GPS location (if required)
7. Take photos (if required)
8. Review all entries
9. Save as draft or submit
10. Confirmation message

**Reviewing Submission (M&E Staff):**
1. Navigate to Form Submissions
2. Filter by pending review
3. Open submission
4. Review all data:
   - Form responses
   - Photos
   - GPS location
5. Check data quality
6. Add review notes
7. Approve or request revision
8. If approved, data becomes final
9. If revision needed, notify submitter

---

### 3.12 Reports Module

**Purpose**: Reporting and analytics system

#### Key Entities:

**1. Report**
Report definitions:
- Name and description
- Report type:
  - Dashboard
  - Tabular Report
  - Chart/Graph
  - Custom Report
- Configuration (JSON)
- Created by
- Active status

#### Reporting Features:

**Built-in Reports:**
- Household enrollment reports
- Training completion reports
- Grant disbursement reports
- Business group performance
- Savings group progress
- Mentor activity reports
- Program performance dashboards

**Report Generation:**
- Filter by date range
- Filter by geographic area
- Filter by program
- Export to CSV/Excel
- PDF generation (conceptual)

**Dashboard Analytics:**
- Real-time statistics
- Visual charts and graphs
- Trend analysis
- Performance indicators

#### Key URLs:
- `/reports/` - Report list
- `/reports/<id>/` - View report
- `/reports/<id>/generate/` - Generate report
- `/reports/<id>/export/` - Export report

#### How to Use:

**Generating a Report:**
1. Navigate to Reports module
2. Select report type
3. Set filters:
   - Date range
   - Geographic area
   - Program
   - Other criteria
4. Click "Generate Report"
5. View report on screen
6. Export if needed (CSV/Excel)

---

### 3.13 Dashboard Module

**Purpose**: Role-based dashboard views with key metrics

#### Dashboard Types:

**1. Admin Dashboard (ICT Admin)**
Comprehensive system overview:
- Program overview statistics
- Geographic coverage maps
- Financial metrics (all grant types)
- Training progress
- Total households enrolled
- Active business groups
- Grant disbursements (SB, PR, Household)
- Mentor activity logs
- System health indicators

**2. Mentor Dashboard**
Mentor-specific view:
- Assigned trainings (current and upcoming)
- Assigned households
- Recent mentoring visits
- Recent phone nudges
- Grant applications from assigned households
- Upcoming training sessions (next 7 days)
- Monthly activity statistics
- Household grant status tracking

**3. Executive Dashboard (County Executive/Assembly)**
High-level strategic overview:
- Total program statistics
- Financial summary (all grant disbursements)
- Active households and programs
- Mentor coverage
- Key performance indicators
- Budget utilization

**4. M&E Dashboard**
Monitoring and evaluation focus:
- Total mentor activities (visits + calls)
- Recent mentoring visits (last 30 days)
- Recent phone nudges (last 30 days)
- Mentor activity rankings
- Training completion rates
- Survey completion status
- Data quality indicators

**5. Field Associate Dashboard**
Field operations overview:
- Managed mentors
- Total and active trainings
- Households in training
- Form assignments
- Mentor performance

**6. General Dashboard**
Basic system statistics for other roles

#### Dashboard Features:

**Real-time Statistics:**
- Auto-refreshing data
- Interactive charts
- Drill-down capabilities
- Quick action links

**Personalized Views:**
- Role-based content
- User-specific data
- Geographic filtering
- Program filtering

**Activity Tracking:**
- Recent activities
- Pending tasks
- Overdue items
- Upcoming deadlines

#### Key URLs:
- `/` - Main dashboard (role-based routing)

#### Dashboard Usage:

**Accessing Your Dashboard:**
1. Log in to the system
2. Automatically redirected to role-appropriate dashboard
3. View key statistics and metrics
4. Access quick links to common tasks
5. Monitor pending activities
6. Review recent updates

---

### 3.14 Settings Module

**Purpose**: System configuration and preferences

#### Key Entities:

**1. System Configuration**
System-wide settings:
- Key-value pairs
- Setting types:
  - String
  - Integer
  - Boolean
  - JSON
  - File Path
- Categories (general, email, SMS, security, etc.)
- Public/private flags
- Editable flags
- Modified by tracking

**2. User Settings**
User-specific preferences:
- Email notifications
- SMS notifications
- Dashboard layout (JSON)
- Theme (light/dark)
- Language (English/Swahili)
- Timezone (default: Africa/Nairobi)
- Two-factor authentication
- Last password change date

**3. System Audit Log**
Comprehensive activity logging:
- User and action type
- Model name and object ID
- Request information:
  - IP address
  - User agent
  - Request path
  - Request method
- Change details (JSON)
- Success/error status
- Timestamp indexing

**4. System Alert**
System-wide notifications:
- Title and message
- Alert type:
  - Information
  - Warning
  - Error
  - Maintenance
  - Security
- Alert scope:
  - System Wide
  - Role Specific
  - User Specific
- Display settings:
  - Active status
  - Show until (expiration)
  - Dismissible flag
- Targeting:
  - Target roles (JSON list)
  - Target users (many-to-many)

**5. User Alert Dismissal**
Track dismissed alerts per user

**6. System Backup**
Backup tracking:
- Backup type:
  - Full Backup
  - Incremental Backup
  - Database Only
  - Media Files Only
- Status:
  - Pending
  - Running
  - Completed
  - Failed
- File path and size
- Duration calculation
- Started by
- Timestamps
- Error logging

#### Settings Features:

**Configuration Management:**
- Centralized settings
- Type-safe value storage
- Category organization
- Change tracking

**User Preferences:**
- Personalized experience
- Notification control
- UI customization
- Security settings

**Audit Trail:**
- Complete activity logging
- User action tracking
- IP address logging
- Change history

**Alert System:**
- Targeted notifications
- Role-based alerts
- Dismissible messages
- Expiration dates

**Backup Management:**
- Scheduled backups
- Manual backups
- Backup restoration (conceptual)
- Storage management

#### Key URLs:
- `/settings/` - Settings home
- `/settings/system/` - System configuration
- `/settings/user/` - User preferences
- `/settings/audit/` - Audit log
- `/settings/alerts/` - System alerts
- `/settings/backup/` - Backup management

#### How to Use:

**Configuring System Settings (ICT Admin):**
1. Navigate to Settings → System Configuration
2. Browse settings by category
3. Select setting to edit
4. Enter new value (respecting type)
5. Save changes
6. System logs change in audit trail

**Managing User Preferences:**
1. Navigate to Settings → User Preferences
2. Configure notifications:
   - Email notifications (on/off)
   - SMS notifications (on/off)
3. Customize dashboard layout
4. Select theme (light/dark)
5. Choose language
6. Set timezone
7. Enable/disable two-factor authentication
8. Save preferences

**Viewing Audit Log:**
1. Navigate to Settings → Audit Log
2. Filter by:
   - User
   - Action type
   - Date range
   - Model name
3. View detailed activity log
4. Export for analysis

**Creating System Alert (ICT Admin):**
1. Navigate to Settings → Alerts
2. Click "Create Alert"
3. Enter alert details:
   - Title and message
   - Alert type
   - Scope (system/role/user)
4. Set targeting:
   - If role-specific: select roles
   - If user-specific: select users
5. Set display settings:
   - Expiration date
   - Dismissible (yes/no)
6. Activate alert
7. Alert appears for targeted users

**Managing Backups:**
1. Navigate to Settings → Backup
2. View existing backups
3. Create new backup:
   - Select backup type
   - Add notes
   - Initiate backup
4. Monitor backup progress
5. View completed backups
6. Download backup files (if needed)

---

## 4. Step-by-Step User Guides

### 4.1 Complete Household Enrollment Process

**Scenario**: Enroll a new household in the UPG program

**Steps:**

1. **Initial Household Registration**
   - Log in as Field Associate or M&E Staff
   - Navigate to Households → Add Household
   - Fill in household head information:
     - First name, middle name, last name
     - Gender and date of birth
     - National ID number
     - Phone number
   - Fill in geographic information:
     - Select county
     - Select sub-county
     - Select village
     - Optional: Constituency, district, division, location
   - Add GPS coordinates (if available)
   - Enter socio-economic data:
     - Monthly income
     - Assets (JSON format)
     - Electricity access
     - Clean water access
     - Location type (rural/urban/remote)
   - Save household

2. **Add Household Members**
   - Open newly created household
   - Click "Add Member"
   - Enter member details:
     - Name (or first, middle, last)
     - Gender and age
     - Relationship to head
     - Education level
     - National ID or birth certificate
   - Repeat for all household members
   - Identify household head and mark appropriately

3. **Run Eligibility Assessment**
   - Open household detail page
   - Click "Run Eligibility Assessment"
   - System calculates:
     - PPI score (if assessment data available)
     - Income level eligibility
     - Asset criteria
     - Geographic eligibility
   - View eligibility results
   - System provides recommendation (eligible/not eligible)

4. **Record Baseline PPI**
   - Click "Add PPI Assessment"
   - Select "Baseline PPI"
   - Enter assessment date
   - Input PPI score (0-100)
   - Save PPI record

5. **Obtain Household Consent**
   - Verify household understands program requirements
   - Update household record:
     - Set "Consent Given" = Yes
   - Save household

6. **Enroll in Program**
   - Navigate to Households → Household Programs
   - Click "Enroll in Program"
   - Select program (e.g., UPG FY25C1)
   - Assign mentor (if known)
   - Set enrollment date
   - Status: "Enrolled"
   - Save enrollment

7. **Initialize UPG Milestones**
   - Open household program enrollment
   - Click "Initialize Milestones"
   - System creates 12 monthly milestones
   - Set target dates for each milestone
   - Save milestones

8. **Assign to Training**
   - Navigate to Training module
   - Select appropriate training module
   - Click "Enroll Households"
   - Find and select household
   - Confirm enrollment
   - System checks training capacity (max 25)

**Result**: Household is fully enrolled, eligible, consented, and assigned to training with milestone tracking activated.

---

### 4.2 Complete Training Module Delivery

**Scenario**: Mentor conducts and tracks a complete training module

**Steps:**

**Phase 1: Training Preparation**

1. **View Assigned Training**
   - Log in as Mentor
   - View dashboard → Assigned Trainings
   - Click on training to open details
   - Review:
     - Training name and module number
     - Training location and dates
     - Enrolled households (list)
     - Training materials/topics

2. **Review Enrolled Households**
   - View list of enrolled households
   - Note: Maximum 25 households per training
   - Check household details
   - Plan logistics

3. **Send Training Reminders**
   - Navigate to Training → Phone Nudges
   - Click "Add Phone Nudge"
   - For each household:
     - Select household
     - Nudge type: "Training Reminder"
     - Set call date/time
     - Record call duration
     - Mark successful contact
     - Add notes (e.g., confirmed attendance)
   - Repeat for all households

**Phase 2: Training Delivery**

4. **Conduct Training Session**
   - Physical training session at specified location
   - Deliver training content
   - Note attendees
   - Track session duration

5. **Mark Attendance**
   - After training session
   - Navigate to Training → Training Detail
   - Click "Mark Attendance"
   - Select training date
   - For each household:
     - Check "Present" or leave unchecked for "Absent"
   - Add notes (if needed)
   - System records:
     - Attendance status
     - Marked by (mentor)
     - Timestamp
   - Save attendance

**Phase 3: Post-Training Follow-up**

6. **Record Mentoring Visits**
   - Navigate to Training → Mentoring Visits
   - Click "Add Mentoring Visit"
   - For households visited:
     - Select household
     - Visit type: "On-site"
     - Select topic (e.g., "Business Plan Development")
     - Set visit date
     - Add detailed notes:
       - What was discussed
       - Household progress
       - Challenges identified
       - Next steps
   - Save visit

7. **Follow-up Phone Calls**
   - Navigate to Training → Phone Nudges
   - For households not visited or needing additional support:
     - Add phone nudge
     - Nudge type: "Follow-up Call"
     - Record call details
     - Document support provided

8. **Update Training Status**
   - Once all sessions completed
   - Navigate to training detail
   - Update status from "Active" to "Completed"
   - Save training

**Phase 4: Reporting**

9. **Submit Mentoring Report**
   - Navigate to Training → Mentoring Reports
   - Click "Create Report"
   - Select reporting period (e.g., Monthly)
   - Enter period start and end dates
   - Fill in statistics:
     - Households visited: [count]
     - Phone nudges made: [count]
     - Trainings conducted: 1
     - New households enrolled: [count]
   - Write narrative report:
     - Key activities:
       - "Conducted [Training Name] for 23 households"
       - "Completed 15 follow-up visits"
       - "Made 20 phone calls for training reminders"
     - Challenges faced:
       - "5 households had transportation issues"
       - "2 households needed additional time for business plan"
     - Successes achieved:
       - "92% attendance rate"
       - "All attending households completed business plans"
     - Next period plans:
       - "Support households in SB Grant applications"
       - "Form business groups"
   - Submit report

10. **Update Household Milestones**
    - For each household that completed training
    - Navigate to Household → UPG Milestones
    - Update appropriate milestone:
      - Example: "Month 1 - PPI Assessment & Business Training Start"
      - Set status: "Completed"
      - Set completion date
      - Add notes
    - Save milestone

**Result**: Training module delivered, attendance tracked, follow-up conducted, and reporting completed.

---

### 4.3 Business Group Formation and SB Grant Application

**Scenario**: Form a business group and apply for Seed Business (SB) Grant

**Steps:**

**Phase 1: Business Group Formation**

1. **Identify Participants**
   - Review households that completed business training
   - Identify 2-3 households interested in same business type
   - Verify all households:
     - Completed required training
     - Are active in program
     - Have given consent

2. **Create Business Group**
   - Log in as Field Associate or Mentor
   - Navigate to Business Groups → Add Business Group
   - Fill in group details:
     - Group name (e.g., "Makutano Maize Growers")
     - Select program (e.g., UPG FY25C1)
     - Business type: Select category (Crop, Retail, Service, Livestock, Skill)
     - Business type detail: (e.g., "Maize farming", "Barber shop")
     - Group size: 3 (adjust as needed)
     - Formation date: [today's date]
     - Current business health: "Yellow" (Fair - just starting)
     - Participation status: "Active"
   - Save business group

3. **Add Group Members**
   - Open newly created business group
   - Click "Add Members"
   - For first household:
     - Select household
     - Role: "Leader"
     - Joined date: [formation date]
     - Is active: Yes
     - Save
   - For second household:
     - Select household
     - Role: "Treasurer"
     - Joined date: [formation date]
     - Is active: Yes
     - Save
   - For third household:
     - Select household
     - Role: "Secretary"
     - Joined date: [formation date]
     - Is active: Yes
     - Save
   - Verify all members added

4. **Update Household Milestones**
   - For each member household:
     - Navigate to Household → UPG Milestones
     - Update "Month 2 - Business Group Formation"
     - Status: "Completed"
     - Completion date: [formation date]
     - Notes: "Member of [Group Name]"
     - Save

**Phase 2: Business Plan Development**

5. **Develop Business Plan with Group**
   - Physical meeting with business group
   - Discuss and document:
     - Business description
     - Products/services to be offered
     - Target market
     - Startup costs (itemized)
     - Projected monthly income
     - Monthly expenses
     - First 6-month projections
   - Review and refine plan with group
   - Group approves final plan

6. **Update Milestone**
   - For each member household:
     - Update "Month 3 - Business Plan Development"
     - Status: "Completed"
     - Completion date: [today's date]
     - Save

**Phase 3: SB Grant Application**

7. **Prepare SB Grant Application**
   - Navigate to UPG Grants → SB Grants
   - Click "New SB Grant Application"
   - Fill in application:
     - Select program
     - Select business group
     - Submitted by: [current user]
     - Business plan: [paste full business plan]
     - Projected income: [amount in KES]
     - Startup costs: [amount in KES]
     - Monthly expenses: [amount in KES]
   - System auto-calculates grant amount:
     - Base: 15,000 KES
     - Group size factor: [calculated]
     - Business type factor: [calculated]
     - Location factor: [calculated]
     - Performance factor: [calculated]
     - Calculated grant amount: [shown]
   - Review calculation
   - If needed, admin can adjust final grant amount
   - Leader name: [from member list]
   - Treasurer name: [from member list]
   - Secretary name: [from member list]
   - Save application

8. **Submit Application**
   - Review all details
   - Confirm accuracy
   - Click "Submit Application"
   - Status changes to "Pending"
   - Application enters review queue

9. **Update Milestone**
   - For each member household:
     - Update "Month 4 - SB Grant Application"
     - Status: "Completed"
     - Completion date: [today's date]
     - Save

**Phase 4: Application Review and Approval**

10. **Review Application (M&E Staff or County Director)**
    - Navigate to UPG Grants → SB Grants
    - Filter: Status = "Pending"
    - Open application
    - Review all details:
      - Business plan
      - Financial projections
      - Group composition
      - Training completion
    - Verify eligibility:
      - All members completed training
      - Business plan is realistic
      - Financials are reasonable
    - Add review notes
    - Assign review score (0-100)
    - Change status to "Under Review"
    - Save

11. **Approve Application (County Executive or Authorized Approver)**
    - Navigate to SB Grants under review
    - Open application
    - Review:
      - Application details
      - Review notes and score
    - Make decision:
      - If approved:
        - Confirm final grant amount
        - Add approval notes
        - Set approval date
        - Change status to "Approved"
      - If rejected:
        - Add rejection reason
        - Change status to "Rejected"
    - Save decision
    - System notifies applicant

**Phase 5: Grant Disbursement**

12. **Disburse Funds**
    - Navigate to approved SB Grants
    - Open grant
    - Click "Disburse Funds"
    - Enter disbursement details:
      - Disbursement date: [today's date]
      - Amount: [full or partial amount]
      - Method: [Bank Transfer, Mobile Money, Cash, or Check]
      - Reference number: [transaction ID]
      - Recipient name: [Leader name]
      - Recipient contact: [Leader phone]
    - Add disbursement notes
    - Confirm disbursement
    - Status changes to "Disbursed"
    - Disbursement status: "Fully Disbursed" (if full amount)
    - System records transaction

13. **Update Milestone**
    - For each member household:
      - Update "Month 5 - SB Grant Disbursement"
      - Status: "Completed"
      - Completion date: [disbursement date]
      - Notes: "Grant amount: [amount] KES"
      - Save

14. **Notify Business Group**
    - Send SMS notification (if enabled)
    - Or call group leader
    - Confirm funds received
    - Remind about:
      - Proper fund utilization
      - Record keeping
      - Business launch timeline
      - Next milestone: "Month 6 - Business Operations Start"

**Result**: Business group formed, business plan developed, SB Grant applied for, approved, and disbursed. Ready to launch business.

---

### 4.4 Savings Group Setup and Tracking

**Scenario**: Form a savings group and track monthly savings

**Steps:**

**Phase 1: Savings Group Formation**

1. **Identify Potential Members**
   - Target: 25 members (can be smaller to start)
   - Can include:
     - Individual households
     - Entire business groups
   - Members should be:
     - In same geographic area
     - Able to meet regularly
     - Committed to savings

2. **Create Savings Group**
   - Log in as Field Associate or Mentor
   - Navigate to Savings Groups → Add Savings Group
   - Fill in details:
     - Group name (e.g., "Kapenguria Women's Savings Group")
     - Target members: 25
     - Formation date: [today's date]
     - Meeting day: "Every Tuesday"
     - Meeting location: "Kapenguria Community Center"
     - Savings frequency: "Weekly"
     - Is active: Yes
   - Save savings group

3. **Link Business Groups (Optional)**
   - If entire business groups are joining:
     - Click "Link Business Groups"
     - Select business group(s)
     - All business group members automatically become savings group members
     - Save

4. **Add Individual Members**
   - Click "Add Members"
   - For each individual household:
     - Select household
     - Role: "Chairperson", "Secretary", "Treasurer", or "Member"
     - Joined date: [formation date]
     - Total savings: 0 (will be updated as savings recorded)
     - Is active: Yes
     - Save
   - Ensure key roles filled:
     - 1 Chairperson
     - 1 Secretary
     - 1 Treasurer
     - Remaining members

5. **Initial Meeting**
   - Conduct first savings group meeting
   - Explain:
     - Savings rules
     - Meeting schedule
     - Contribution amounts
     - Withdrawal policies
   - Elect/confirm leadership
   - Collect initial savings (if any)

**Phase 2: Regular Savings Tracking**

6. **Weekly Savings Recording**
   - After each weekly meeting
   - Navigate to Savings Group → Record Savings
   - For each member who saved:
     - Click "Add Savings Record"
     - Select BSG
     - Select member (household)
     - Enter amount: [amount in KES]
     - Savings date: [meeting date]
     - Recorded by: [current user]
     - Add notes (optional): "Week 1 contribution"
     - Save record
   - System automatically:
     - Updates member's total savings
     - Updates group's savings to date

7. **Monthly Progress Survey**
   - At end of each month
   - Navigate to Savings Group → Add Progress Survey
   - Fill in survey:
     - BSG: [select group]
     - Survey date: [today's date]
     - Saving last month: [total saved in past month]
     - Month recorded: [month/year]
     - Attendance this meeting: [number of members present]
     - Surveyor: [current user]
   - Save survey

**Phase 3: Monitoring and Support**

8. **Track Member Participation**
   - Review member savings records
   - Identify:
     - Regular savers
     - Inconsistent savers
     - Non-participating members
   - Plan interventions:
     - Phone calls to remind
     - Home visits for challenges
     - Group encouragement

9. **Update Household Milestones**
   - For UPG program households:
     - Navigate to Household → UPG Milestones
     - Update "Month 8 - Business Savings Group Formation"
     - Status: "Completed"
     - Completion date: [formation date]
     - Notes: "Member of [Savings Group Name]"
     - Save

10. **Regular Reporting**
    - Monthly reports to show:
      - Total group savings
      - Number of active members
      - Savings trends
      - Member participation rates
    - Use for M&E and program evaluation

**Phase 4: Long-term Tracking**

11. **Quarterly Review**
    - Every 3 months:
      - Review all progress surveys
      - Calculate:
        - Average monthly savings per member
        - Group growth rate
        - Member retention rate
      - Identify successful patterns
      - Address challenges

12. **Annual Assessment**
    - At end of first year:
      - Total group savings accumulated
      - Member graduation from ultra-poor status
      - Impact on household income
      - Sustainability assessment
    - Report to program management

**Result**: Savings group formed, regular savings tracked, monthly progress monitored, and member participation documented.

---

### 4.5 PR Grant Application Process

**Scenario**: Business group applies for Performance Recognition (PR) Grant after successfully utilizing SB Grant

**Steps:**

**Phase 1: Prerequisites Check**

1. **Verify SB Grant Completion**
   - Navigate to Business Group detail
   - Check SB Grant status:
     - Must be "Disbursed"
     - Must have utilization report
   - Verify business operations:
     - Business has been running for at least 6 months
     - Regular business activities

2. **Complete SB Grant Utilization Report**
   - If not yet done:
     - Navigate to SB Grant detail
     - Click "Add Utilization Report"
     - Enter detailed report:
       - How grant was utilized (itemized)
       - Equipment/inventory purchased
       - Business setup completed
       - Challenges encountered
       - Outcomes achieved
     - Upload receipts/photos (if available)
     - Set utilization date
     - Save report
   - Required for PR Grant eligibility

3. **Track Business Performance**
   - Navigate to Business Group → Add Progress Survey
   - Record current performance:
     - Grant value: [original SB Grant amount]
     - Grant used: [amount utilized]
     - Profit: [cumulative profit to date]
     - Business inputs: [current inventory]
     - Business inventory: [items in stock]
     - Business cash: [cash on hand]
   - Save survey
   - Perform multiple surveys over 6-month period

**Phase 2: Performance Assessment**

4. **Conduct Business Assessment**
   - Review all progress surveys
   - Calculate business metrics:
     - Total revenue generated
     - Profit margins
     - Inventory growth
     - Cash flow status
   - Assess business health:
     - Update business health status if needed
     - Should be "Green" (Good) or "Yellow" (Fair) for PR eligibility
   - Document:
     - Jobs created (number)
     - Income increase for members
     - Savings accumulated
     - Community impact

5. **Verify Savings Group Participation**
   - Check if business group members are part of savings group
   - Review savings records:
     - Regular contributions
     - Cumulative savings
   - Important for UPG graduation pathway

**Phase 3: PR Grant Application**

6. **Initiate PR Grant Application**
   - Navigate to UPG Grants → PR Grants
   - Click "New PR Grant Application"
   - Select program (must be UPG type)
   - Select business group (must have SB Grant)
   - System automatically:
     - Links to SB Grant
     - Checks eligibility
     - Shows eligibility status

7. **Fill PR Grant Application**
   - Confirm applicant details
   - Enter performance data:
     - Revenue generated: [total revenue since SB Grant]
     - Jobs created: [number of jobs]
     - Savings accumulated: [total savings]
   - Write performance assessment:
     - Detailed narrative of business performance
     - Challenges overcome
     - Community impact
     - Growth trajectory
   - Grant amount: [default 10,000 KES or as configured]
   - Review all information
   - Save application

8. **Submit Application**
   - Review application thoroughly
   - Click "Submit Application"
   - System checks:
     - SB Grant is disbursed: ✓
     - Utilization report exists: ✓
     - Performance metrics present: ✓
   - If all checks pass:
     - Status changes to "Pending"
     - Application enters review queue
   - If checks fail:
     - System shows error message
     - Complete missing requirements

9. **Update Milestone**
   - For each member household:
     - Navigate to Household → UPG Milestones
     - Update "Month 10 - PR Grant Application"
     - Status: "Completed"
     - Completion date: [today's date]
     - Save

**Phase 4: Review and Assessment**

10. **Eligibility Assessment (M&E Staff)**
    - Navigate to PR Grants → Pending Applications
    - Open application
    - Click "Run Eligibility Check"
    - System verifies:
      - SB Grant successfully completed
      - Utilization report submitted
      - Business metrics meet minimum standards
      - Training requirements met
      - Savings group participation (for UPG)
    - Review business performance:
      - Revenue trends
      - Profit generation
      - Jobs created
      - Savings patterns
    - Assign performance score (0-100)
    - Assign performance rating:
      - Excellent Performance (90-100)
      - Good Performance (70-89)
      - Satisfactory Performance (60-69)
      - Poor Performance (<60)
    - Write detailed assessment
    - Set assessment date
    - If eligible:
      - Status: "Eligible" → "Under Review"
    - If not eligible:
      - Status: "Not Eligible Yet"
      - Provide feedback on what's needed
    - Save assessment

11. **Peer Review (Optional)**
    - Additional review by Field Associate or Program Manager
    - Verify performance metrics
    - Add review notes
    - Confirm eligibility decision

**Phase 5: Approval**

12. **Approval Decision (County Director or Authorized Approver)**
    - Navigate to PR Grants under review
    - Open application
    - Review all documentation:
      - Application details
      - Performance assessment
      - Performance score and rating
      - Business metrics
    - Consider:
      - Business sustainability
      - Community impact
      - Growth potential
      - Program budget availability
    - Make decision:
      - If approved:
        - Confirm grant amount
        - Add approval notes
        - Set approval date
        - Status: "Approved"
      - If rejected:
        - Provide detailed rejection reason
        - Suggest improvements
        - Status: "Rejected"
    - Save decision
    - System notifies applicant

**Phase 6: Disbursement**

13. **Disburse PR Grant**
    - Navigate to approved PR Grants
    - Open grant
    - Click "Disburse Funds"
    - Enter disbursement details:
      - Disbursement date: [today's date]
      - Amount: [grant amount]
      - Method: [Bank Transfer, Mobile Money, Cash, or Check]
      - Reference number: [transaction ID]
      - Recipient: [business group leader]
      - Contact: [leader phone number]
    - Add disbursement notes
    - Confirm disbursement
    - Status changes to "Disbursed"
    - System records transaction

14. **Update Milestone**
    - For each member household:
      - Navigate to Household → UPG Milestones
      - Check if "Month 10 - PR Grant Application" completed
      - Update "Month 11 - Final Business Assessment"
      - Status: "Completed" (or "In Progress")
      - Add notes about PR Grant disbursement
      - Save

15. **Post-Disbursement Follow-up**
    - Schedule mentoring visit
    - Discuss:
      - PR Grant utilization plan
      - Business expansion goals
      - Sustainability planning
      - Graduation pathway
    - Set follow-up dates

**Phase 7: Final Assessment (Leading to Graduation)**

16. **Track PR Grant Utilization**
    - Monitor business over 2-3 months
    - Record progress surveys
    - Update business health status
    - Prepare for graduation assessment

17. **Graduation Assessment**
    - For each member household:
      - Update "Month 12 - Graduation Assessment"
      - Conduct comprehensive assessment:
        - Income increase verification
        - Asset accumulation
        - Business sustainability
        - Savings group participation
        - Community integration
      - Status: "Completed"
      - Completion date: [today's date]
    - Update household program status:
      - From "Active" to "Graduated"
      - Set graduation date
      - Add graduation notes

**Result**: PR Grant successfully applied for, assessed, approved, and disbursed based on business performance. Business group progresses toward graduation.

---

## 5. Troubleshooting

### 5.1 Common Login Issues

**Problem**: Cannot log in / "Invalid username or password" error

**Solutions**:
1. Verify username (case-sensitive)
2. Verify password (case-sensitive)
3. Check Caps Lock key
4. Use "Forgot Password" if password forgotten
5. Contact ICT Administrator if account locked

**Problem**: Password reset email not received

**Solutions**:
1. Check spam/junk folder
2. Verify correct email address registered
3. Wait 5-10 minutes for email delivery
4. Contact ICT Administrator for manual reset

**Problem**: Session timeout / Automatically logged out

**Solutions**:
1. Sessions expire after 1 hour of inactivity (configured in settings)
2. Save work frequently
3. Log back in
4. Contact ICT Admin if timeout too short

---

### 5.2 Data Entry Issues

**Problem**: "Permission denied" when trying to add/edit data

**Solutions**:
1. Verify your role has permission for this action
2. Check if you're assigned to the specific data (e.g., mentor can only edit assigned households)
3. Contact supervisor if permission needed

**Problem**: Cannot save form / Validation errors

**Solutions**:
1. Check all required fields (marked with asterisk *)
2. Verify data format (dates, numbers, emails)
3. Check field length limits
4. Review error messages for specific issues

**Problem**: Duplicate entry errors

**Solutions**:
1. System prevents duplicate entries (e.g., same household in business group)
2. Search for existing record first
3. Update existing record instead of creating new one
4. Contact ICT Admin if legitimate duplicate needed

---

### 5.3 Training Module Issues

**Problem**: Cannot enroll household in training / "Training full" error

**Solutions**:
1. Training has maximum capacity (default 25 households)
2. Check available slots
3. Create additional training session
4. Or remove inactive households from current training

**Problem**: Household already enrolled in another training

**Solutions**:
1. System enforces one household per training
2. Complete or withdraw household from current training
3. Then enroll in new training

**Problem**: Cannot mark attendance

**Solutions**:
1. Verify training date has passed or is today
2. Check if households are enrolled
3. Verify mentor assignment
4. Ensure training status is "Active" or "Completed"

---

### 5.4 Grant Application Issues

**Problem**: SB Grant auto-calculation seems incorrect

**Solutions**:
1. Review calculation factors:
   - Group size
   - Business type
   - Location
   - Training performance
2. Verify business group has members added
3. Check training completion records
4. Contact M&E Staff for calculation review
5. Admin can manually adjust final amount if needed

**Problem**: PR Grant application rejected / "Not eligible"

**Solutions**:
1. Verify SB Grant status is "Disbursed"
2. Ensure SB Grant utilization report completed
3. Check business performance metrics
4. Review training completion rates
5. Verify savings group participation
6. Address feedback from eligibility assessment

**Problem**: Cannot submit grant application

**Solutions**:
1. Check all required fields filled
2. Verify business plan entered
3. Ensure financial projections realistic
4. Confirm applicant type selected (household, business group, or savings group)
5. Review any validation error messages

---

### 5.5 Reporting Issues

**Problem**: Report shows no data / empty results

**Solutions**:
1. Check date range filters
2. Verify geographic filters
3. Ensure data exists for selected criteria
4. Try broader filters
5. Contact M&E Staff if data expected but not showing

**Problem**: Dashboard statistics not updating

**Solutions**:
1. Refresh browser page (F5 or Ctrl+R)
2. Clear browser cache
3. Log out and log back in
4. Check if recent data entry was saved successfully

**Problem**: Cannot export report

**Solutions**:
1. Verify export permission for your role
2. Check browser popup blocker settings
3. Try different export format (CSV instead of Excel)
4. Contact ICT Admin if persistent

---

### 5.6 Forms Module Issues

**Problem**: Cannot access assigned form

**Solutions**:
1. Verify form assignment is "Active"
2. Check assignment hasn't expired (due date)
3. Confirm you're the assignee (mentor or field associate)
4. Check if field associate reassigned form
5. Contact M&E Staff who assigned form

**Problem**: Form submission fails

**Solutions**:
1. Check all required fields completed
2. Verify photo evidence uploaded (if required)
3. Ensure GPS location captured (if required)
4. Check internet connection
5. Save as draft if submission failing
6. Try submitting again later

**Problem**: Photo upload fails

**Solutions**:
1. Check photo file size (max 5MB)
2. Verify photo format (JPG, PNG)
3. Check device storage space
4. Try compressing photo
5. Check internet connection

---

### 5.7 System Performance Issues

**Problem**: System running slowly

**Solutions**:
1. Check internet connection speed
2. Close unnecessary browser tabs
3. Clear browser cache and cookies
4. Try different browser (Chrome, Firefox, Edge)
5. Restart browser
6. Contact ICT Admin if persistent

**Problem**: Page not loading / timeout errors

**Solutions**:
1. Check internet connection
2. Refresh page
3. Clear browser cache
4. Try accessing from different device
5. Check if system maintenance in progress
6. Contact ICT Admin

**Problem**: Changes not saving / "Network error"

**Solutions**:
1. Check internet connection
2. Verify no firewall blocking
3. Try saving again
4. Copy unsaved data to clipboard
5. Refresh page and try again
6. Contact ICT Admin if persistent

---

### 5.8 Getting Help

**Support Channels**:

1. **User Documentation**: This manual and system help pages
2. **Supervisor/Manager**: First point of contact for operational questions
3. **M&E Staff**: For data collection, forms, and reporting questions
4. **ICT Administrator**: For technical issues, permissions, and system errors
5. **System Alerts**: Check dashboard for system-wide notifications

**Reporting Issues**:
1. Describe the problem clearly
2. Note any error messages (screenshot if possible)
3. Specify what you were trying to do
4. Include your username and role
5. Note date and time of issue

**Emergency Contacts**:
- ICT Administrator: [contact information]
- M&E Staff: [contact information]
- Program Manager: [contact information]

---

# Part 2: Complete Source Code Appendix

## 6. Appendix: Complete Source Code

This section contains the complete source code for all major files in the UPG System. The code is organized by module for easy reference.

---

### 6.1 Project Settings

#### File: upg_system/settings.py

```python
"""
Django settings for UPG System project.

Generated for Village Enterprise Ultra-Poor Graduation Management System.
For local development and testing.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-upg-system-dev-key-change-in-production-123456789'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'households',
    'business_groups',
    'savings_groups',
    'training',
    'surveys',
    'reports',
    'programs',
    'dashboard',
    'grants',
    'upg_grants',  # UPG-specific grant management
    'forms',  # Dynamic forms system
    'settings_module',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'upg_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_permissions',
                'core.context_processors.system_alerts',
            ],
        },
    },
]

WSGI_APPLICATION = 'upg_system.wsgi.application'


# Database Configuration

# MySQL Configuration (Active)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'upg_management_system',
        'USER': 'root',
        'PASSWORD': '',  # XAMPP default (no password)
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}

# SQLite Configuration (Backup - data migrated to MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMS Configuration
# Africa's Talking API (Primary SMS provider for Kenya)
AFRICAS_TALKING_API_KEY = ''  # Set in production
AFRICAS_TALKING_USERNAME = 'sandbox'  # Change to production username
SMS_SENDER_ID = 'UPG_SYS'

# Twilio API (Fallback SMS provider)
TWILIO_ACCOUNT_SID = ''  # Set in production
TWILIO_AUTH_TOKEN = ''   # Set in production
TWILIO_PHONE_NUMBER = '' # Set in production

# SMS Settings
SMS_ENABLED = True
SMS_BACKEND = 'core.sms.SMSService'  # Can be changed for testing

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Security Settings for Development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# UPG System Specific Settings
UPG_SYSTEM_VERSION = '1.0.0'
UPG_DEFAULT_COUNTRY = 'Kenya'
UPG_DEFAULT_CURRENCY = 'KES'

# Database compatibility settings
import sys
if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
    # Only apply MySQL/MariaDB settings if using MySQL backend
    if DATABASES['default']['ENGINE'] in ['django.db.backends.mysql', 'django.db.backends.mariadb']:
        if 'OPTIONS' not in DATABASES['default']:
            DATABASES['default']['OPTIONS'] = {}
        DATABASES['default']['OPTIONS']['init_command'] = (
            "SET sql_mode='STRICT_TRANS_TABLES'; "
            "SET SESSION innodb_strict_mode=1; "
        )

# Pagination
ITEMS_PER_PAGE = 25

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

---

### 6.2 Project URLs

#### File: upg_system/urls.py

```python
"""
URL configuration for UPG System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/', include('accounts.urls')),

    # Main Dashboard
    path('', include('dashboard.urls')),

    # Core modules
    path('households/', include('households.urls')),
    path('business-groups/', include('business_groups.urls')),
    path('savings-groups/', include('savings_groups.urls')),
    path('training/', include('training.urls')),
    path('surveys/', include('surveys.urls')),
    path('reports/', include('reports.urls')),
    path('programs/', include('programs.urls')),
    path('grants/', include('grants.urls')),
    path('upg-grants/', include('upg_grants.urls')),
    path('settings/', include('settings_module.urls')),
    path('core/', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site headers
admin.site.site_header = "UPG Management System"
admin.site.site_title = "UPG Admin"
admin.site.index_title = "Ultra-Poor Graduation Management"
```

---

### 6.3 Accounts Module

#### File: accounts/models.py

```python

---

# PART 2: COMPLETE SOURCE CODE APPENDIX

This section contains all 106 Python source code files from the UPG System.

---


## File: accounts\__init__.py

**Location:** `accounts\__init__.py`

```python
# Accounts App
```

---



---

# PART 2: COMPLETE SOURCE CODE APPENDIX

This section contains all 106 Python source code files from the UPG System.

---


## File: accounts\__init__.py

**Location:** `accounts\__init__.py`

```python
# Accounts App
```

---


## File: accounts\admin.py

**Location:** `accounts\admin.py`

```python
"""
Admin configuration for User management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'role', 'office', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'office', 'country')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('UPG System Info', {
            'fields': ('role', 'phone_number', 'office', 'country')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('UPG System Info', {
            'fields': ('email', 'role', 'phone_number', 'office', 'country')
        }),
    )


admin.site.register(User, UserAdmin)
```

---


## File: accounts\apps.py

**Location:** `accounts\apps.py`

```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
```

---


## File: accounts\forms.py

**Location:** `accounts\forms.py`

```python
"""
Authentication Forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'office', 'phone_number')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'office': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

---


## File: accounts\models.py

**Location:** `accounts\models.py`

```python
"""
User and Role Management Models for UPG System
Based on system roles from wireframe
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """
    Custom User model with UPG-specific fields and roles
    """
    ROLE_CHOICES = [
        ('county_executive', 'County Executive (CECM & Governor)'),
        ('county_assembly', 'County Assembly Member'),
        ('ict_admin', 'ICT Administrator'),
        ('me_staff', 'M&E Staff'),
        ('field_associate', 'Field Associate/Mentor Supervisor'),
        ('mentor', 'Mentor'),
        ('beneficiary', 'Beneficiary'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mentor')
    phone_number = models.CharField(max_length=15, blank=True)
    office = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default='Kenya')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Permission groups based on wireframe role-based access control matrix
    def has_module_permission(self, module_name, permission_type='full'):
        """
        Check if user has permission for specific module
        permission_type: 'full', 'read', 'none'
        """
        # Full access permissions (create, read, update, delete)
        full_permissions = {
            'county_executive': ['dashboard', 'grants', 'reports'],
            'county_assembly': ['dashboard', 'reports'],
            'ict_admin': ['dashboard', 'programs', 'households', 'business_groups', 'savings_groups', 'surveys', 'training', 'grants', 'reports', 'settings'],
            'me_staff': ['dashboard', 'programs', 'households', 'business_groups', 'savings_groups', 'surveys', 'training', 'reports'],
            'field_associate': ['dashboard', 'households', 'business_groups', 'savings_groups', 'surveys', 'training', 'grants'],
            'mentor': ['dashboard', 'households', 'business_groups', 'savings_groups', 'surveys', 'training'],
            'beneficiary': ['dashboard'],
        }

        # Read-only permissions
        read_permissions = {
            'county_executive': ['programs', 'households', 'business_groups', 'savings_groups', 'training'],
            'county_assembly': ['programs', 'households', 'business_groups', 'savings_groups'],
            'ict_admin': [],  # ICT admin has full access to everything
            'me_staff': ['grants'],
            'field_associate': ['programs', 'reports'],
            'mentor': ['programs', 'reports'],
            'beneficiary': ['programs', 'households', 'business_groups', 'savings_groups', 'training'],
        }

        user_full_permissions = full_permissions.get(self.role, [])
        user_read_permissions = read_permissions.get(self.role, [])

        if permission_type == 'full':
            return module_name in user_full_permissions
        elif permission_type == 'read':
            return module_name in user_read_permissions or module_name in user_full_permissions
        else:  # any access
            return module_name in user_full_permissions or module_name in user_read_permissions

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    class Meta:
        db_table = 'upg_users'


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    assigned_villages = models.ManyToManyField('core.Village', blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        db_table = 'upg_user_profiles'


class PasswordResetToken(models.Model):
    """
    Password reset tokens for forgot password functionality
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if token is expired (24 hours)"""
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time

    def is_valid(self):
        """Check if token is valid and not used"""
        return self.is_active and not self.used_at and not self.is_expired()

    def mark_as_used(self):
        """Mark token as used"""
        self.used_at = timezone.now()
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Password reset token for {self.user.username}"

    class Meta:
        db_table = 'upg_password_reset_tokens'
        ordering = ['-created_at']
```

---


## File: accounts\urls.py

**Location:** `accounts\urls.py`

```python
"""
Accounts URL Configuration
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Password reset functionality
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('password-reset-sent/', views.password_reset_sent_view, name='password_reset_sent'),
    path('password-reset-complete/', views.password_reset_complete_view, name='password_reset_complete'),
]
```

---


## File: accounts\views.py

**Location:** `accounts\views.py`

```python
"""
Authentication Views for UPG System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import User, PasswordResetToken
from .forms import LoginForm, UserRegistrationForm


def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})


def forgot_password_view(request):
    """Forgot password form"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Deactivate any existing tokens for this user
            PasswordResetToken.objects.filter(user=user, is_active=True).update(is_active=False)

            # Create new reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={'token': reset_token.token})
            )

            # Send email (you may want to use a template for this)
            subject = 'UPG System - Password Reset Request'
            message = f'''
Hello {user.get_full_name() or user.username},

You have requested to reset your password for the UPG Management System.

Please click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
UPG Management System
            '''

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                return redirect('accounts:password_reset_sent')
            except Exception as e:
                messages.error(request, 'Failed to send password reset email. Please contact system administrator.')

        except User.DoesNotExist:
            # Don't reveal whether email exists for security
            return redirect('accounts:password_reset_sent')

    return render(request, 'accounts/forgot_password.html')


def password_reset_sent_view(request):
    """Password reset email sent confirmation"""
    return render(request, 'accounts/password_reset_sent.html')


def reset_password_view(request, token):
    """Reset password with token"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            messages.error(request, 'This password reset link has expired or is invalid.')
            return redirect('accounts:forgot_password')

        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'accounts/reset_password.html', {'token': token})

            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'accounts/reset_password.html', {'token': token})

            # Reset password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.mark_as_used()

            messages.success(request, 'Your password has been reset successfully.')
            return redirect('accounts:password_reset_complete')

        return render(request, 'accounts/reset_password.html', {'token': token})

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:forgot_password')


def password_reset_complete_view(request):
    """Password reset complete confirmation"""
    return render(request, 'accounts/password_reset_complete.html')
```

---


## File: append_source_code.py

**Location:** `append_source_code.py`

```python
"""
Append all source code files to the UPG System Complete Manual
"""
import os

def append_source_code():
    # Get all Python files
    files = []
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, filenames in os.walk(base_dir):
        # Skip unwanted directories
        if any(skip in root for skip in ['venv', '__pycache__', 'migrations', '.git', 'staticfiles']):
            continue

        for f in filenames:
            if f.endswith('.py'):
                filepath = os.path.join(root, f)
                # Get relative path
                rel_path = os.path.relpath(filepath, base_dir)
                files.append((filepath, rel_path))

    # Sort files by relative path
    files.sort(key=lambda x: x[1])

    print(f"Found {len(files)} Python files to append")

    # Append to manual
    manual_path = os.path.join(base_dir, 'UPG_System_Complete_Manual.md')

    with open(manual_path, 'a', encoding='utf-8') as manual:
        manual.write('\n\n---\n\n')
        manual.write('# PART 2: COMPLETE SOURCE CODE APPENDIX\n\n')
        manual.write(f'This section contains all {len(files)} Python source code files from the UPG System.\n\n')
        manual.write('---\n\n')

        for filepath, rel_path in files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Write file header
                manual.write(f'\n## File: {rel_path}\n\n')
                manual.write(f'**Location:** `{rel_path}`\n\n')
                manual.write(f'```python\n')
                manual.write(content)
                manual.write(f'\n```\n\n')
                manual.write('---\n\n')

                print(f'[OK] Added: {rel_path}')
            except Exception as e:
                print(f'[ERROR] Error reading {rel_path}: {e}')
                continue

    print(f'\n{"="*60}')
    print(f'Total files appended: {len(files)}')
    print(f'Manual updated: {manual_path}')

    # Get final file size
    size_kb = os.path.getsize(manual_path) / 1024
    print(f'Final manual size: {size_kb:.2f} KB')
    print(f'{"="*60}')

if __name__ == '__main__':
    append_source_code()

```

---


## File: business_groups\__init__.py

**Location:** `business_groups\__init__.py`

```python
# Business Groups App
```

---


## File: business_groups\management\commands\create_test_business_groups.py

**Location:** `business_groups\management\commands\create_test_business_groups.py`

```python
"""
Management command to create test business groups
"""
from django.core.management.base import BaseCommand
from business_groups.models import BusinessGroup
from core.models import Program
from households.models import Household
from datetime import date


class Command(BaseCommand):
    help = 'Creates test business groups'

    def handle(self, *args, **kwargs):
        program = Program.objects.first()
        if not program:
            self.stdout.write(self.style.ERROR('No programs found'))
            return

        bg_data = [
            ('Kapenguria Women Farmers', 'agriculture'),
            ('Sigor Dairy Cooperative', 'livestock'),
            ('Pokot Poultry Group', 'poultry'),
            ('Mnagei Tailors', 'tailoring'),
            ('Sook Traders', 'retail'),
            ('Riwo Beekeepers', 'apiculture'),
        ]

        for name, btype in bg_data:
            bg, created = BusinessGroup.objects.get_or_create(
                name=name,
                defaults={
                    'business_type': btype,
                    'program': program,
                    'formation_date': date(2024, 1, 15),
                    'participation_status': 'active',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {name} ({btype})'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Business groups ready'))

```

---


## File: business_groups\models.py

**Location:** `business_groups\models.py`

```python
"""
Business Groups Management Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from households.models import Household
from core.models import Program

User = get_user_model()


class BusinessGroup(models.Model):
    """
    Business Group formed to run business jointly (2-3 entrepreneurs)
    """
    BUSINESS_HEALTH_CHOICES = [
        ('red', 'Red - Poor Performance'),
        ('yellow', 'Yellow - Fair Performance'),
        ('green', 'Green - Good Performance'),
    ]

    PARTICIPATION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended'),
    ]

    BUSINESS_TYPE_CHOICES = [
        ('crop', 'Crop'),
        ('retail', 'Retail'),
        ('service', 'Service'),
        ('livestock', 'Livestock'),
        ('skill', 'Skill'),
    ]

    name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    current_business_health = models.CharField(max_length=10, choices=BUSINESS_HEALTH_CHOICES, default='yellow')
    participation_status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS_CHOICES, default='active')
    group_size = models.IntegerField(default=2)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    business_type_detail = models.CharField(max_length=100, blank=True)  # e.g., cereal, barber shop
    formation_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'upg_business_groups'


class BusinessGroupMember(models.Model):
    """
    Household members of business groups
    """
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('treasurer', 'Treasurer'),
        ('secretary', 'Secretary'),
        ('member', 'Member'),
    ]

    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='members')
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.business_group.name} ({self.role})"

    class Meta:
        db_table = 'upg_business_group_members'
        unique_together = ['business_group', 'household']


class SBGrant(models.Model):
    """
    SB Grant (Initial Seed Business Grant) awarded to business groups
    """
    FUNDING_STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('funded', 'Funded'),
        ('not_funded', 'Not Funded'),
    ]

    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='sb_grants')
    business_type = models.CharField(max_length=20)
    funding_status = models.CharField(max_length=20, choices=FUNDING_STATUS_CHOICES, default='applied')
    funded_date = models.DateField(null=True, blank=True)
    grant_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    leader_name = models.CharField(max_length=100)
    treasurer_name = models.CharField(max_length=100)
    secretary_name = models.CharField(max_length=100)
    business_type_detail = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SB Grant - {self.business_group.name}"

    class Meta:
        db_table = 'upg_sb_grants'


class PRGrant(models.Model):
    """
    PR Grant (Performance-based second grant) awarded to business groups
    """
    FUNDING_STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('funded', 'Funded'),
        ('not_funded', 'Not Funded'),
    ]

    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='pr_grants')
    business_type = models.CharField(max_length=20)
    funding_status = models.CharField(max_length=20, choices=FUNDING_STATUS_CHOICES, default='applied')
    funded_date = models.DateField(null=True, blank=True)
    grant_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    leader_name = models.CharField(max_length=100)
    treasurer_name = models.CharField(max_length=100)
    secretary_name = models.CharField(max_length=100)
    business_type_detail = models.CharField(max_length=100, blank=True)
    why_pr_qualified = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PR Grant - {self.business_group.name}"

    class Meta:
        db_table = 'upg_pr_grants'


class BusinessProgressSurvey(models.Model):
    """
    Business group progress and performance tracking
    """
    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='progress_surveys')
    survey_date = models.DateField()
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Financial metrics
    grant_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grant_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business_inputs = models.TextField(blank=True)
    business_inventory = models.TextField(blank=True)
    business_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_group.name} - Progress Survey - {self.survey_date}"

    class Meta:
        db_table = 'upg_business_progress_surveys'
```

---


## File: business_groups\urls.py

**Location:** `business_groups\urls.py`

```python
from django.urls import path
from . import views

app_name = 'business_groups'

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('<int:pk>/add-member/', views.add_member, name='add_member'),
    path('<int:pk>/remove-member/<int:member_id>/', views.remove_member, name='remove_member'),
    path('<int:pk>/update-role/<int:member_id>/', views.update_member_role, name='update_member_role'),
    path('<int:pk>/available-households/', views.get_available_households, name='get_available_households'),
]
```

---


## File: business_groups\views.py

**Location:** `business_groups\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import BusinessGroup, BusinessGroupMember
from households.models import Household
from core.models import Program
from datetime import date

@login_required
def group_list(request):
    """Business Groups list view with role-based filtering"""
    user = request.user

    # Filter business groups based on user role and village assignments
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        # Full access to all business groups
        groups = BusinessGroup.objects.all()
    elif user.role in ['mentor', 'field_associate']:
        # Only groups with members from assigned villages
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            groups = BusinessGroup.objects.filter(
                members__household__village__in=assigned_villages
            ).distinct()
        else:
            # No villages assigned, no groups visible
            groups = BusinessGroup.objects.none()
    else:
        # Other roles have no access to business groups
        groups = BusinessGroup.objects.none()

    groups = groups.order_by('-created_at')

    context = {
        'groups': groups,
        'page_title': 'Business Groups',
        'total_count': groups.count(),
    }

    return render(request, 'business_groups/group_list.html', context)

@login_required
def group_create(request):
    """Create business group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        program_id = request.POST.get('program')
        business_type = request.POST.get('business_type')
        business_type_detail = request.POST.get('business_type_detail', '')
        group_size = request.POST.get('group_size', 2)
        formation_date = request.POST.get('formation_date') or date.today()

        if name and program_id:
            group = BusinessGroup.objects.create(
                name=name,
                program_id=program_id,
                business_type=business_type or 'crop',
                business_type_detail=business_type_detail,
                group_size=int(group_size),
                formation_date=formation_date
            )
            messages.success(request, f'Business group "{group.name}" created successfully!')
            return redirect('business_groups:group_detail', pk=group.pk)
        else:
            messages.error(request, 'Group name and program are required.')

    programs = Program.objects.filter(status='active')
    context = {
        'programs': programs,
        'business_type_choices': BusinessGroup.BUSINESS_TYPE_CHOICES,
        'page_title': 'Create Business Group',
    }
    return render(request, 'business_groups/group_create.html', context)

@login_required
def group_detail(request, pk):
    """Business group detail view"""
    group = get_object_or_404(BusinessGroup, pk=pk)
    context = {
        'group': group,
        'page_title': f'Business Group - {group.name}',
    }
    return render(request, 'business_groups/group_detail.html', context)

@login_required
def group_edit(request, pk):
    """Edit business group"""
    group = get_object_or_404(BusinessGroup, pk=pk)

    if request.method == 'POST':
        group.name = request.POST.get('name', group.name)
        program_id = request.POST.get('program')
        if program_id:
            group.program_id = program_id
        group.business_type = request.POST.get('business_type', group.business_type)
        group.business_type_detail = request.POST.get('business_type_detail', group.business_type_detail)
        group.group_size = request.POST.get('group_size', group.group_size)
        formation_date = request.POST.get('formation_date')
        if formation_date:
            group.formation_date = formation_date

        group.save()
        messages.success(request, f'Business group "{group.name}" updated successfully!')
        return redirect('business_groups:group_detail', pk=group.pk)

    programs = Program.objects.filter(status='active')
    context = {
        'group': group,
        'programs': programs,
        'business_type_choices': BusinessGroup.BUSINESS_TYPE_CHOICES,
        'page_title': f'Edit - {group.name}',
    }
    return render(request, 'business_groups/group_edit.html', context)

@login_required
def add_member(request, pk):
    """Add household to business group"""
    group = get_object_or_404(BusinessGroup, pk=pk)

    if request.method == 'POST':
        household_id = request.POST.get('household_id')
        role = request.POST.get('role', 'member')
        joined_date = request.POST.get('joined_date') or date.today()

        if household_id:
            try:
                household = Household.objects.get(id=household_id)

                # Check if household is already a member
                if BusinessGroupMember.objects.filter(business_group=group, household=household).exists():
                    messages.error(request, f'{household.name} is already a member of this group.')
                else:
                    BusinessGroupMember.objects.create(
                        business_group=group,
                        household=household,
                        role=role,
                        joined_date=joined_date
                    )
                    messages.success(request, f'{household.name} added to {group.name} successfully!')

            except Household.DoesNotExist:
                messages.error(request, 'Selected household not found.')
        else:
            messages.error(request, 'Please select a household.')

    return redirect('business_groups:group_detail', pk=pk)

@login_required
def remove_member(request, pk, member_id):
    """Remove household from business group"""
    group = get_object_or_404(BusinessGroup, pk=pk)
    member = get_object_or_404(BusinessGroupMember, id=member_id, business_group=group)

    if request.method == 'POST':
        household_name = member.household.name
        member.delete()
        messages.success(request, f'{household_name} removed from {group.name}.')

    return redirect('business_groups:group_detail', pk=pk)

@login_required
def update_member_role(request, pk, member_id):
    """Update member role in business group"""
    group = get_object_or_404(BusinessGroup, pk=pk)
    member = get_object_or_404(BusinessGroupMember, id=member_id, business_group=group)

    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(BusinessGroupMember.ROLE_CHOICES):
            member.role = new_role
            member.save()
            messages.success(request, f'{member.household.name} role updated to {member.get_role_display()}.')
        else:
            messages.error(request, 'Invalid role selected.')

    return redirect('business_groups:group_detail', pk=pk)

@login_required
def get_available_households(request, pk):
    """AJAX endpoint to get households that can be added to the group"""
    group = get_object_or_404(BusinessGroup, pk=pk)

    # Get households that are not already members of this group
    existing_member_ids = group.members.values_list('household_id', flat=True)
    available_households = Household.objects.exclude(id__in=existing_member_ids)

    # Filter by user role and village assignments
    user = request.user
    if user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            available_households = available_households.filter(village__in=assigned_villages)

    households_data = []
    for household in available_households[:20]:  # Limit to 20 for performance
        households_data.append({
            'id': household.id,
            'name': household.name,
            'village': household.village.name if household.village else 'No Village'
        })

    return JsonResponse({'households': households_data})
```

---


## File: convert_manual_to_pdf.py

**Location:** `convert_manual_to_pdf.py`

```python
"""
Convert Markdown User Manual to PDF using WeasyPrint
"""

import markdown2
from weasyprint import HTML, CSS
import os

def convert_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF with proper styling"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'toc',
        'code-friendly',
        'break-on-newline'
    ])

    # Create styled HTML document
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }}
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }}

            h1 {{
                color: #2c3e50;
                font-size: 24pt;
                margin-top: 24pt;
                margin-bottom: 12pt;
                border-bottom: 3px solid #3498db;
                padding-bottom: 8pt;
                page-break-after: avoid;
            }}

            h2 {{
                color: #34495e;
                font-size: 18pt;
                margin-top: 20pt;
                margin-bottom: 10pt;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 6pt;
                page-break-after: avoid;
            }}

            h3 {{
                color: #2c3e50;
                font-size: 14pt;
                margin-top: 16pt;
                margin-bottom: 8pt;
                page-break-after: avoid;
            }}

            h4 {{
                color: #555;
                font-size: 12pt;
                margin-top: 12pt;
                margin-bottom: 6pt;
                font-weight: 600;
                page-break-after: avoid;
            }}

            p {{
                margin: 8pt 0;
                text-align: justify;
            }}

            ul, ol {{
                margin: 8pt 0;
                padding-left: 24pt;
            }}

            li {{
                margin: 4pt 0;
            }}

            code {{
                background-color: #f4f4f4;
                padding: 2pt 6pt;
                border-radius: 3pt;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                color: #c7254e;
            }}

            pre {{
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4pt;
                padding: 12pt;
                overflow-x: auto;
                margin: 12pt 0;
                page-break-inside: avoid;
            }}

            pre code {{
                background-color: transparent;
                padding: 0;
                color: #333;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12pt 0;
                font-size: 10pt;
                page-break-inside: avoid;
            }}

            th {{
                background-color: #3498db;
                color: white;
                padding: 8pt;
                text-align: left;
                font-weight: 600;
            }}

            td {{
                border: 1px solid #ddd;
                padding: 8pt;
            }}

            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 16pt;
                margin: 12pt 0;
                color: #555;
                font-style: italic;
                background-color: #f9f9f9;
                padding: 12pt 16pt;
            }}

            strong {{
                color: #2c3e50;
                font-weight: 600;
            }}

            em {{
                color: #555;
            }}

            hr {{
                border: none;
                border-top: 2px solid #e0e0e0;
                margin: 24pt 0;
            }}

            .header {{
                background-color: #3498db;
                color: white;
                padding: 20pt;
                margin: -2.5cm -2cm 2cm -2cm;
                text-align: center;
            }}

            .header h1 {{
                color: white;
                border: none;
                margin: 0;
                padding: 0;
            }}

            .toc {{
                background-color: #f8f9fa;
                padding: 16pt;
                border: 1px solid #dee2e6;
                border-radius: 4pt;
                margin: 16pt 0;
                page-break-after: always;
            }}

            .toc h2 {{
                margin-top: 0;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            .page-break {{
                page-break-after: always;
            }}

            .no-break {{
                page-break-inside: avoid;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert HTML to PDF
    HTML(string=styled_html).write_pdf(pdf_file)

    print(f"✓ PDF created successfully: {pdf_file}")
    print(f"✓ File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == "__main__":
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "mentoring_system_user_manual.md")
    pdf_file = os.path.join(base_dir, "mentoring_system_user_manual.pdf")

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"✗ Error: Markdown file not found: {md_file}")
        exit(1)

    print("Converting Markdown to PDF...")
    print(f"Source: {md_file}")
    print(f"Target: {pdf_file}")
    print()

    try:
        convert_markdown_to_pdf(md_file, pdf_file)
        print()
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"✗ Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

```

---


## File: convert_manual_to_pdf_reportlab.py

**Location:** `convert_manual_to_pdf_reportlab.py`

```python
"""
Convert Markdown User Manual to PDF using ReportLab
"""

import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from html.parser import HTMLParser
import os
import re

class HTMLToParagraphConverter(HTMLParser):
    """Convert HTML to ReportLab flowables"""

    def __init__(self, styles):
        super().__init__()
        self.styles = styles
        self.flowables = []
        self.current_text = []
        self.current_style = styles['Normal']
        self.in_pre = False
        self.in_list = False
        self.list_items = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_style = self.styles['Heading1']
        elif tag == 'h2':
            self.current_style = self.styles['Heading2']
        elif tag == 'h3':
            self.current_style = self.styles['Heading3']
        elif tag == 'h4':
            self.current_style = self.styles['Heading4']
        elif tag == 'p':
            self.current_style = self.styles['Normal']
        elif tag == 'code':
            self.current_text.append('<font name="Courier" size="9" color="#c7254e">')
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')
        elif tag == 'pre':
            self.in_pre = True
        elif tag == 'ul' or tag == 'ol':
            self.in_list = True
            self.list_items = []
        elif tag == 'li':
            pass
        elif tag == 'hr':
            self.flush_text()
            self.flowables.append(Spacer(1, 0.2*inch))

    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'p']:
            self.flush_text()
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'code':
            self.current_text.append('</font>')
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('</b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('</i>')
        elif tag == 'pre':
            self.in_pre = False
            self.flush_text()
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'ul' or tag == 'ol':
            self.in_list = False
            for item in self.list_items:
                self.flowables.append(item)
            self.list_items = []
            self.flowables.append(Spacer(1, 0.1*inch))
        elif tag == 'li':
            self.flush_list_item()

    def handle_data(self, data):
        if data.strip():
            # Escape special characters for ReportLab
            data = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if self.in_pre:
                # Preserve whitespace in code blocks
                self.current_text.append(data)
            else:
                self.current_text.append(data)

    def flush_text(self):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                if self.in_pre:
                    # Code block style
                    code_style = ParagraphStyle(
                        'Code',
                        parent=self.styles['Code'],
                        fontSize=9,
                        fontName='Courier',
                        leftIndent=20,
                        rightIndent=20,
                        spaceBefore=6,
                        spaceAfter=6,
                        backColor=colors.HexColor('#f8f8f8'),
                        borderColor=colors.HexColor('#dddddd'),
                        borderWidth=1,
                        borderPadding=10
                    )
                    para = Paragraph(text, code_style)
                else:
                    para = Paragraph(text, self.current_style)
                self.flowables.append(para)
            self.current_text = []
            self.current_style = self.styles['Normal']

    def flush_list_item(self):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                bullet_style = ParagraphStyle(
                    'Bullet',
                    parent=self.styles['Normal'],
                    leftIndent=20,
                    bulletIndent=10,
                    fontSize=11,
                    spaceBefore=3,
                    spaceAfter=3
                )
                para = Paragraph(f"• {text}", bullet_style)
                self.list_items.append(para)
            self.current_text = []

    def get_flowables(self):
        self.flush_text()
        return self.flowables

def add_page_number(canvas, doc):
    """Add page numbers to each page"""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, text)
    canvas.restoreState()

def convert_markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF using ReportLab"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'code-friendly'
    ])

    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Customize styles
    styles['Heading1'].fontSize = 24
    styles['Heading1'].textColor = colors.HexColor('#2c3e50')
    styles['Heading1'].spaceAfter = 12
    styles['Heading1'].spaceBefore = 24

    styles['Heading2'].fontSize = 18
    styles['Heading2'].textColor = colors.HexColor('#34495e')
    styles['Heading2'].spaceAfter = 10
    styles['Heading2'].spaceBefore = 20

    styles['Heading3'].fontSize = 14
    styles['Heading3'].textColor = colors.HexColor('#2c3e50')
    styles['Heading3'].spaceAfter = 8
    styles['Heading3'].spaceBefore = 16

    styles['Heading4'].fontSize = 12
    styles['Heading4'].textColor = colors.HexColor('#555555')
    styles['Heading4'].spaceAfter = 6
    styles['Heading4'].spaceBefore = 12

    styles['Normal'].fontSize = 11
    styles['Normal'].leading = 14
    styles['Normal'].alignment = TA_JUSTIFY

    # Add custom code style if not exists
    if 'Code' not in styles:
        styles.add(ParagraphStyle(
            name='Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#f8f8f8')
        ))

    # Build flowables
    story = []

    # Add title page
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30
    )

    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("UPG Mentoring System", title_style))
    story.append(Paragraph("User Manual", title_style))
    story.append(Spacer(1, 0.5*inch))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    story.append(Paragraph("Version 1.0", subtitle_style))
    story.append(Paragraph("October 2025", subtitle_style))
    story.append(PageBreak())

    # Parse HTML and add to story
    parser = HTMLToParagraphConverter(styles)
    parser.feed(html_content)
    story.extend(parser.get_flowables())

    # Build PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    print(f"PDF created successfully: {pdf_file}")
    print(f"File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == "__main__":
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "mentoring_system_user_manual.md")
    pdf_file = os.path.join(base_dir, "mentoring_system_user_manual.pdf")

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        exit(1)

    print("Converting Markdown to PDF using ReportLab...")
    print(f"Source: {md_file}")
    print(f"Target: {pdf_file}")
    print()

    try:
        convert_markdown_to_pdf(md_file, pdf_file)
        print()
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

```

---


## File: core\__init__.py

**Location:** `core\__init__.py`

```python
# Core App - Basic system models
```

---


## File: core\apps.py

**Location:** `core\apps.py`

```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

---


## File: core\context_processors.py

**Location:** `core\context_processors.py`

```python
"""
Context processors for UPG System
"""


def user_permissions(request):
    """
    Add user role and permission information to template context
    """
    if request.user.is_authenticated:
        user = request.user

        # Role-based permissions matrix
        permissions = {
            # Module access permissions
            'can_view_programs': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'county_executive', 'county_assembly', 'field_associate'],
            'can_edit_programs': user.is_superuser or user.role in ['ict_admin', 'me_staff'],

            'can_view_households': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],
            'can_edit_households': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],

            'can_view_business_groups': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],
            'can_edit_business_groups': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],

            'can_view_savings_groups': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],
            'can_edit_savings_groups': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],

            'can_view_surveys': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],
            'can_create_surveys': user.is_superuser or user.role in ['ict_admin', 'me_staff'],

            'can_view_training': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor'],
            'can_create_training': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'],
            'can_edit_training': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'],
            'can_delete_training': user.is_superuser or user.role in ['ict_admin', 'me_staff'],
            'can_manage_training': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'],

            'can_view_grants': user.is_superuser or user.role in ['ict_admin', 'county_executive', 'field_associate'],
            'can_manage_grants': user.is_superuser or user.role in ['ict_admin', 'field_associate'],

            'can_view_reports': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'county_executive', 'county_assembly'],
            'can_export_reports': user.is_superuser or user.role in ['ict_admin', 'me_staff', 'county_executive'],

            'can_view_settings': user.is_superuser or user.role == 'ict_admin',
            'can_manage_users': user.is_superuser or user.role == 'ict_admin',

            # ESR Import permissions
            'can_import_esr': user.is_superuser or user.role == 'ict_admin',

            # Geographic restrictions
            'has_village_restrictions': user.role in ['mentor', 'field_associate'] and not user.is_superuser,
        }

        # Add user role information
        role_info = {
            'user_role': user.role,
            'user_role_display': user.get_role_display(),
            'is_mentor': user.role == 'mentor',
            'is_field_associate': user.role == 'field_associate',
            'is_me_staff': user.role == 'me_staff',
            'is_ict_admin': user.role == 'ict_admin',
            'is_county_executive': user.role == 'county_executive',
            'is_county_assembly': user.role == 'county_assembly',
            'is_beneficiary': user.role == 'beneficiary',
        }

        # Village assignments for mentors and field associates
        village_info = {}
        if hasattr(user, 'profile') and user.profile and user.role in ['mentor', 'field_associate']:
            assigned_villages = user.profile.assigned_villages.all()
            village_info.update({
                'assigned_villages': assigned_villages,
                'assigned_villages_count': assigned_villages.count(),
                'has_village_assignments': assigned_villages.exists(),
            })

        return {
            'perms': permissions,
            'role_info': role_info,
            'village_info': village_info,
        }

    return {}


def system_alerts(request):
    """
    Add active system alerts to template context
    """
    if request.user.is_authenticated:
        from settings_module.models import SystemAlert, UserAlertDismissal
        from django.utils import timezone

        # Get active alerts visible to this user
        active_alerts = SystemAlert.objects.filter(
            is_active=True,
            show_until__gt=timezone.now()
        )

        # Filter alerts by scope
        user_alerts = []
        for alert in active_alerts:
            if alert.is_visible_to_user(request.user):
                # Check if user has dismissed this alert
                dismissed = UserAlertDismissal.objects.filter(
                    user=request.user,
                    alert=alert
                ).exists()

                if not dismissed:
                    user_alerts.append(alert)

        return {
            'system_alerts': user_alerts,
            'alerts_count': len(user_alerts),
        }

    return {}
```

---


## File: core\decorators.py

**Location:** `core\decorators.py`

```python
"""
Role-based permission decorators for UPG System
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def role_required(*allowed_roles):
    """
    Decorator to restrict access to views based on user roles
    Usage: @role_required('ict_admin', 'me_staff')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Superusers always have access
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user's role is in allowed roles
            if user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                f"Access denied. This page requires one of these roles: {', '.join(allowed_roles)}. "
                f"Your current role is: {user.get_role_display()}"
            )

        return _wrapped_view
    return decorator


def mentor_or_admin_required(view_func):
    """
    Decorator for views that mentors, field associates, and admins can access
    """
    return role_required('mentor', 'field_associate', 'ict_admin', 'me_staff')(view_func)


def admin_only(view_func):
    """
    Decorator for admin-only views
    """
    return role_required('ict_admin')(view_func)


def me_staff_or_admin(view_func):
    """
    Decorator for M&E staff and admin views
    """
    return role_required('me_staff', 'ict_admin')(view_func)


def executive_access(view_func):
    """
    Decorator for county executive and assembly access
    """
    return role_required('county_executive', 'county_assembly', 'ict_admin', 'me_staff')(view_func)


def has_village_access(user, village_id):
    """
    Check if user has access to a specific village
    """
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        return True

    if user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            assigned_village_ids = user.profile.assigned_villages.values_list('id', flat=True)
            return int(village_id) in assigned_village_ids

    return False


def filter_by_user_villages(queryset, user, village_field='village'):
    """
    Filter a queryset to only include items from user's assigned villages
    """
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        return queryset

    if user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            filter_kwargs = {f'{village_field}__in': assigned_villages}
            return queryset.filter(**filter_kwargs)
        else:
            return queryset.none()

    return queryset.none()


def get_user_accessible_villages(user):
    """
    Get all villages accessible to the user based on their role
    """
    from core.models import Village

    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        return Village.objects.all()

    if user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            return user.profile.assigned_villages.all()
        else:
            return Village.objects.none()

    return Village.objects.none()
```

---


## File: core\management\__init__.py

**Location:** `core\management\__init__.py`

```python

```

---


## File: core\management\commands\__init__.py

**Location:** `core\management\commands\__init__.py`

```python

```

---


## File: core\management\commands\load_west_pokot_data.py

**Location:** `core\management\commands\load_west_pokot_data.py`

```python
"""
Management command to load West Pokot County data
"""
from django.core.management.base import BaseCommand
from core.models import County, SubCounty, Village


class Command(BaseCommand):
    help = 'Load West Pokot County, Sub-Counties, and Villages data'

    def handle(self, *args, **options):
        self.stdout.write('Loading West Pokot County data...')

        # Create West Pokot County
        county, created = County.objects.get_or_create(
            name='West Pokot',
            defaults={'country': 'Kenya'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created county: {county.name}'))
        else:
            self.stdout.write(f'County already exists: {county.name}')

        # West Pokot Sub-Counties
        subcounties_data = [
            'Kapenguria',
            'Sigor',
            'Kacheliba',
            'Pokot South'
        ]

        subcounties = {}
        for subcounty_name in subcounties_data:
            subcounty, created = SubCounty.objects.get_or_create(
                name=subcounty_name,
                county=county
            )
            subcounties[subcounty_name] = subcounty

            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created subcounty: {subcounty_name}'))
            else:
                self.stdout.write(f'  Subcounty already exists: {subcounty_name}')

        # Villages by Sub-County
        villages_data = {
            'Kapenguria': [
                'Mnagei', 'Siyoi', 'Endugh', 'Kapenguria Town', 'Riwo',
                'Sook', 'Lomut', 'Chesegon', 'Keringet', 'Makutano'
            ],
            'Sigor': [
                'Sekerr', 'Masool', 'Muino', 'Weiwei', 'Kishaunet',
                'Chepkopegh', 'Kabichbich', 'Lokitelaebu', 'Akoret', 'Kasei'
            ],
            'Kacheliba': [
                'Suam', 'Kodich', 'Kasei', 'Alale', 'Kapchok',
                'Kiwawa', 'Mnagei', 'Kacheliba Town', 'Akoret', 'Kakomor'
            ],
            'Pokot South': [
                'Chepareria', 'Batei', 'Lelan', 'Tapach', 'Kokwomoing',
                'Lomut', 'Chesogon', 'Kanyarkwat', 'Wei Wei', 'Kapcherop'
            ]
        }

        village_count = 0
        for subcounty_name, village_names in villages_data.items():
            subcounty = subcounties[subcounty_name]

            for village_name in village_names:
                village, created = Village.objects.get_or_create(
                    name=village_name,
                    subcounty_obj=subcounty,
                    defaults={
                        'country': 'Kenya',
                        'is_program_area': True
                    }
                )

                if created:
                    village_count += 1
                    self.stdout.write(f'    Created village: {village_name}')

        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(self.style.SUCCESS(f'  County: 1 (West Pokot)'))
        self.stdout.write(self.style.SUCCESS(f'  Sub-Counties: {len(subcounties_data)}'))
        self.stdout.write(self.style.SUCCESS(f'  New Villages: {village_count}'))
        self.stdout.write(self.style.SUCCESS('\nWest Pokot data loaded successfully!'))

```

---


## File: core\management\commands\update_villages_to_west_pokot.py

**Location:** `core\management\commands\update_villages_to_west_pokot.py`

```python
"""
Management command to update villages from Nairobi to West Pokot
"""
from django.core.management.base import BaseCommand
from core.models import Village, SubCounty
from households.models import Household


class Command(BaseCommand):
    help = 'Update villages from Nairobi to West Pokot'

    def handle(self, *args, **kwargs):
        # Get West Pokot subcounties
        subcounties = SubCounty.objects.filter(county__name='West Pokot')

        if not subcounties.exists():
            self.stdout.write(self.style.ERROR('No West Pokot subcounties found'))
            return

        # West Pokot villages by subcounty
        west_pokot_villages = {
            'Kapenguria': [
                'Mnagei', 'Siyoi', 'Endugh', 'Riwo', 'Kapenguria Town',
                'Sook', 'Muino', 'Talau', 'Chepareria'
            ],
            'Sigor': [
                'Sekerr', 'Lomut', 'Weiwei', 'Masool', 'Tapach',
                'Kishaunet', 'Chepkorio', 'Sigor Town'
            ],
            'Kacheliba': [
                'Suam', 'Kasei', 'Kacheliba Town', 'Alale', 'Kokok',
                'Kalapata', 'Kiwawa'
            ],
            'Pokot South': [
                'Chepareria', 'Batei', 'Lelan', 'Tapach', 'Chesegon',
                'Kapcherop', 'Kanyarkwat'
            ]
        }

        # Get or create villages and assign to subcounties
        for subcounty_name, village_names in west_pokot_villages.items():
            try:
                subcounty = subcounties.get(name=subcounty_name)

                for village_name in village_names:
                    # Check if village exists
                    existing_villages = Village.objects.filter(name=village_name)

                    if existing_villages.count() > 1:
                        # Handle duplicates - keep the one with subcounty, delete others
                        villages_with_subcounty = existing_villages.filter(subcounty_obj__isnull=False).first()
                        if villages_with_subcounty:
                            village = villages_with_subcounty
                            # Delete duplicates without subcounty
                            existing_villages.exclude(id=village.id).delete()
                        else:
                            # Keep first, delete rest
                            village = existing_villages.first()
                            existing_villages.exclude(id=village.id).delete()

                        village.subcounty_obj = subcounty
                        village.is_program_area = True
                        village.save()
                        self.stdout.write(
                            self.style.WARNING(f'Fixed duplicate: {village_name} in {subcounty_name}')
                        )
                    elif existing_villages.count() == 1:
                        village = existing_villages.first()
                        village.subcounty_obj = subcounty
                        village.is_program_area = True
                        village.save()
                        self.stdout.write(
                            self.style.WARNING(f'Updated village: {village_name} to {subcounty_name}')
                        )
                    else:
                        # Create new village
                        village = Village.objects.create(
                            name=village_name,
                            subcounty_obj=subcounty,
                            country='Kenya',
                            is_program_area=True,
                            qualified_hhs_per_village=0,
                            distance_to_market=5,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Created village: {village_name} in {subcounty_name}')
                        )

            except SubCounty.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'SubCounty not found: {subcounty_name}')
                )

        # Update existing households to use West Pokot villages
        nairobi_villages = [
            'Kibera Central', 'Mathare North', 'Korogocho', 'Mukuru Kwa Njenga',
            'Kawangware', 'Viwandani', 'Dandora Phase 2', 'Huruma Estate'
        ]

        west_pokot_village_objects = Village.objects.filter(
            subcounty_obj__county__name='West Pokot'
        ).order_by('?')  # Random order

        if west_pokot_village_objects.exists():
            for nairobi_village_name in nairobi_villages:
                try:
                    nairobi_village = Village.objects.get(name=nairobi_village_name)
                    households = Household.objects.filter(village=nairobi_village)
                    count = households.count()

                    if count > 0:
                        # Distribute households across West Pokot villages
                        for i, household in enumerate(households):
                            new_village = west_pokot_village_objects[i % west_pokot_village_objects.count()]
                            household.village = new_village
                            household.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Moved {count} households from {nairobi_village_name} to West Pokot villages'
                            )
                        )
                except Village.DoesNotExist:
                    pass

        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully updated villages to West Pokot')
        )

```

---


## File: core\middleware.py

**Location:** `core\middleware.py`

```python
"""
Middleware for UPG System
"""

from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from settings_module.models import SystemAuditLog


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuditLogMiddleware:
    """
    Middleware to log user actions and system events
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request info for later use
        request.audit_data = {
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_path': request.path,
            'request_method': request.method,
        }

        response = self.get_response(request)

        # Log certain actions based on response status and path
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._log_action_if_needed(request, response)

        return response

    def _log_action_if_needed(self, request, response):
        """Log actions based on request path and method"""
        path = request.path
        method = request.method
        user = request.user

        # Skip certain paths
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/admin/jsi18n/']
        if any(skip_path in path for skip_path in skip_paths):
            return

        # Log specific actions
        if method == 'POST' and response.status_code in [200, 201, 302]:
            action = 'create'
            model_name = ''
            object_repr = ''

            # Determine action and model based on path
            if '/create' in path or '/add' in path:
                action = 'create'
            elif '/edit' in path or '/update' in path:
                action = 'update'
            elif '/delete' in path:
                action = 'delete'
            elif 'login' in path:
                return  # Handled by signal
            elif 'logout' in path:
                return  # Handled by signal
            else:
                action = 'update'  # Generic POST action

            # Extract model name from URL
            url_parts = path.strip('/').split('/')
            if len(url_parts) > 0:
                model_name = url_parts[0].replace('-', '_').title()

            # Create audit log entry
            try:
                SystemAuditLog.objects.create(
                    user=user,
                    action=action,
                    model_name=model_name,
                    object_repr=object_repr,
                    ip_address=request.audit_data['ip_address'],
                    user_agent=request.audit_data['user_agent'],
                    request_path=request.audit_data['request_path'],
                    request_method=request.audit_data['request_method'],
                    success=True
                )
            except Exception:
                # Don't let audit logging break the application
                pass


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events"""
    try:
        SystemAuditLog.objects.create(
            user=user,
            action='login',
            model_name='User',
            object_repr=str(user),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_path=request.path,
            request_method=request.method,
            success=True
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events"""
    try:
        SystemAuditLog.objects.create(
            user=user,
            action='logout',
            model_name='User',
            object_repr=str(user) if user else 'Anonymous',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_path=request.path,
            request_method=request.method,
            success=True
        )
    except Exception:
        pass
```

---


## File: core\models.py

**Location:** `core\models.py`

```python
"""
Core models for UPG System
Based on Graduation Model Tracking System data dictionary
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    """
    Abstract base model with common fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Mentor(models.Model):
    """
    Business Mentor Contact Information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Kenya')
    office = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'upg_mentors'


class BusinessMentorCycle(models.Model):
    """
    Business Mentor Cycle - logs cycle details and activities
    """
    bm_cycle_name = models.CharField(max_length=100, unique=True)
    business_mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    field_associate = models.CharField(max_length=100)
    cycle = models.CharField(max_length=20)  # e.g., FY25C1
    project = models.CharField(max_length=100)
    office = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bm_cycle_name

    class Meta:
        db_table = 'upg_business_mentor_cycles'


class County(models.Model):
    """
    County information
    """
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50, default='Kenya')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'upg_counties'
        verbose_name_plural = 'Counties'


class SubCounty(models.Model):
    """
    Sub-County information
    """
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.county.name}"

    class Meta:
        db_table = 'upg_subcounties'
        verbose_name_plural = 'Sub-Counties'
        unique_together = ['name', 'county']


class Village(models.Model):
    """
    Village information including subcounty and coverage
    """
    name = models.CharField(max_length=100)
    subcounty_obj = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='villages', null=True, blank=True)
    saturation = models.CharField(max_length=50, blank=True)  # Coverage level
    qualified_hhs_per_village = models.IntegerField(default=0)
    country = models.CharField(max_length=50, default='Kenya')
    distance_to_market = models.IntegerField(default=0, help_text="Distance to market in kilometers")
    is_program_area = models.BooleanField(default=True, help_text="Whether this village is in a program target area")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.subcounty_obj:
            return f"{self.name} - {self.subcounty_obj.name}"
        return f"{self.name}"

    @property
    def subcounty(self):
        """Backward compatibility property"""
        return self.subcounty_obj.name if self.subcounty_obj else ""

    class Meta:
        db_table = 'upg_villages'


class Program(models.Model):
    """
    UPG Program definition and management
    """
    PROGRAM_STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=100)
    cycle = models.CharField(max_length=20)  # e.g., FY25C1
    country = models.CharField(max_length=50, default='Kenya')
    office = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS_CHOICES, default='planning')
    target_households = models.IntegerField(default=0)
    target_villages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.cycle})"

    class Meta:
        db_table = 'upg_programs'


class AuditLog(models.Model):
    """
    System audit trail for all major actions
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"

    class Meta:
        db_table = 'upg_audit_logs'
        ordering = ['-timestamp']


class ESRImport(models.Model):
    """
    ESR (External Service Record) Import tracking
    """
    IMPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    IMPORT_TYPE_CHOICES = [
        ('household', 'Household Data'),
        ('business_group', 'Business Group Data'),
        ('savings_group', 'Savings Group Data'),
        ('survey', 'Survey Data'),
        ('mixed', 'Mixed Data'),
    ]

    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='esr_imports/')
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=IMPORT_STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    import_summary = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ESR Import - {self.file_name} - {self.status}"

    @property
    def success_rate(self):
        if self.total_records == 0:
            return 0
        return (self.successful_imports / self.total_records) * 100

    class Meta:
        db_table = 'upg_esr_imports'
        ordering = ['-started_at']


class ESRImportRecord(models.Model):
    """
    Individual records from ESR imports with mapping details
    """
    RECORD_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    esr_import = models.ForeignKey(ESRImport, on_delete=models.CASCADE, related_name='records')
    row_number = models.IntegerField()
    raw_data = models.JSONField()  # Original data from ESR
    mapped_data = models.JSONField(default=dict)  # Mapped to UPG fields
    status = models.CharField(max_length=20, choices=RECORD_STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_object_type = models.CharField(max_length=100, blank=True)  # Model name
    created_object_id = models.CharField(max_length=100, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ESR Record #{self.row_number} - {self.status}"

    class Meta:
        db_table = 'upg_esr_import_records'
        ordering = ['row_number']


class SMSLog(models.Model):
    """
    SMS notification logging for tracking all SMS communications
    """
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    success = models.BooleanField(default=False)
    provider = models.CharField(max_length=50, help_text="SMS provider used")
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    # Optional relationships
    household = models.ForeignKey('households.Household', on_delete=models.SET_NULL, null=True, blank=True)
    training = models.ForeignKey('training.Training', on_delete=models.SET_NULL, null=True, blank=True)
    mentor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} SMS to {self.phone_number} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = 'upg_sms_logs'
        ordering = ['-sent_at']
```

---


## File: core\sms.py

**Location:** `core\sms.py`

```python
"""
SMS Notification System for UPG Management
Supports multiple SMS providers with fallback capabilities
"""

import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import requests
import json

logger = logging.getLogger(__name__)


class SMSProvider:
    """Base SMS provider class"""

    def send_sms(self, phone_number, message):
        """Send SMS message to phone number"""
        raise NotImplementedError


class AfricasTalkingSMSProvider(SMSProvider):
    """Africa's Talking SMS provider for Kenya"""

    def __init__(self):
        self.api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', '')
        self.username = getattr(settings, 'AFRICAS_TALKING_USERNAME', 'sandbox')
        self.base_url = 'https://api.africastalking.com/version1/messaging'

    def send_sms(self, phone_number, message):
        """Send SMS via Africa's Talking API"""
        if not self.api_key:
            logger.warning("Africa's Talking API key not configured")
            return False

        headers = {
            'apiKey': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        data = {
            'username': self.username,
            'to': phone_number,
            'message': message,
            'from': getattr(settings, 'SMS_SENDER_ID', 'UPG_SYS')
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=data)
            response.raise_for_status()

            result = response.json()
            if result.get('SMSMessageData', {}).get('Recipients'):
                logger.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"SMS failed to send to {phone_number}: {result}")
                return False

        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider as fallback"""

    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    def send_sms(self, phone_number, message):
        """Send SMS via Twilio API"""
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not configured")
            return False

        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)

            message = client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )

            logger.info(f"SMS sent successfully via Twilio to {phone_number}")
            return True

        except ImportError:
            logger.error("Twilio library not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return False


class ConsoleSMSProvider(SMSProvider):
    """Console SMS provider for development/testing"""

    def send_sms(self, phone_number, message):
        """Print SMS to console instead of sending"""
        print(f"\n--- SMS NOTIFICATION ---")
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print(f"Timestamp: {timezone.now()}")
        print(f"--- END SMS ---\n")
        return True


class SMSService:
    """Main SMS service with provider management"""

    def __init__(self):
        self.providers = []
        self._setup_providers()

    def _setup_providers(self):
        """Setup SMS providers based on settings"""
        # Primary provider: Africa's Talking (for Kenya)
        self.providers.append(AfricasTalkingSMSProvider())

        # Fallback provider: Twilio
        self.providers.append(TwilioSMSProvider())

        # Development provider: Console
        if settings.DEBUG:
            self.providers.append(ConsoleSMSProvider())

    def send_sms(self, phone_number, message, template_name=None, context=None):
        """Send SMS with fallback providers"""
        # Format phone number for Kenya (+254)
        formatted_number = self._format_kenyan_number(phone_number)

        # Use template if provided
        if template_name and context:
            message = render_to_string(f'sms/{template_name}', context)

        # Truncate message if too long (SMS limit is usually 160 chars)
        if len(message) > 160:
            message = message[:157] + '...'

        # Try each provider until one succeeds
        for provider in self.providers:
            try:
                if provider.send_sms(formatted_number, message):
                    # Log successful SMS
                    self._log_sms(formatted_number, message, True, provider.__class__.__name__)
                    return True
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                continue

        # All providers failed
        self._log_sms(formatted_number, message, False, 'All providers failed')
        return False

    def _format_kenyan_number(self, phone_number):
        """Format phone number for Kenyan SMS"""
        # Remove all non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))

        # Handle different Kenyan number formats
        if clean_number.startswith('254'):
            return f'+{clean_number}'
        elif clean_number.startswith('0'):
            return f'+254{clean_number[1:]}'
        elif len(clean_number) == 9:
            return f'+254{clean_number}'
        else:
            return f'+{clean_number}'

    def _log_sms(self, phone_number, message, success, provider):
        """Log SMS attempt"""
        try:
            from .models import SMSLog
            SMSLog.objects.create(
                phone_number=phone_number,
                message=message,
                success=success,
                provider=provider,
                sent_at=timezone.now()
            )
        except Exception as e:
            logger.error(f"Failed to log SMS: {e}")

    def send_training_reminder(self, household, training):
        """Send training reminder SMS"""
        context = {
            'household': household,
            'training': training,
            'date': training.start_date,
            'location': training.location,
        }

        return self.send_sms(
            household.primary_contact_phone,
            template_name='training_reminder.txt',
            context=context
        )

    def send_bulk_training_reminders(self, training):
        """Send training reminders to all enrolled households"""
        success_count = 0
        enrolled_households = training.enrolled_households.filter(
            enrollment_status='enrolled'
        ).select_related('household')

        for enrollment in enrolled_households:
            if self.send_training_reminder(enrollment.household, training):
                success_count += 1

        return success_count, enrolled_households.count()


# Global SMS service instance
sms_service = SMSService()
```

---


## File: core\urls.py

**Location:** `core\urls.py`

```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('esr-imports/', views.esr_import_list, name='esr_import_list'),
    path('esr-imports/create/', views.esr_import_create, name='esr_import_create'),
    path('esr-imports/<int:pk>/', views.esr_import_detail, name='esr_import_detail'),

    # Mentor-Village Assignment
    path('assign-mentor/', views.assign_mentor_to_village, name='assign_mentor_to_village'),
    path('mentor-villages/', views.mentor_villages_list, name='mentor_villages_list'),
    path('remove-mentor-village/<int:mentor_id>/<int:village_id>/', views.remove_mentor_village, name='remove_mentor_village'),

    # BM Cycle Management
    path('bm-cycles/', views.bm_cycle_list, name='bm_cycle_list'),
    path('bm-cycles/create/', views.bm_cycle_create, name='bm_cycle_create'),
    path('bm-cycles/<int:cycle_id>/edit/', views.bm_cycle_edit, name='bm_cycle_edit'),
    path('bm-cycles/<int:cycle_id>/delete/', views.bm_cycle_delete, name='bm_cycle_delete'),

    # API endpoints
    path('api/bm-cycles/', views.api_bm_cycles, name='api_bm_cycles'),
    path('api/mentors/', views.api_mentors, name='api_mentors'),
]
```

---


## File: core\views.py

**Location:** `core\views.py`

```python
"""
Core views for UPG System
Includes ESR import functionality and system utilities
"""

import pandas as pd
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import ESRImport, ESRImportRecord, BusinessMentorCycle
from households.models import Household
from business_groups.models import BusinessGroup
from savings_groups.models import BusinessSavingsGroup
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def esr_import_list(request):
    """List all ESR imports - System Admin only"""
    # Check permissions - only system admin (superuser) or ICT Admin can access ESR imports
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role == 'ict_admin'):
        messages.error(request, 'You do not have permission to access ESR import functionality. System administrator access required.')
        return redirect('dashboard:dashboard')
    imports = ESRImport.objects.all().order_by('-started_at')

    # Pagination
    paginator = Paginator(imports, 10)
    page_number = request.GET.get('page')
    imports = paginator.get_page(page_number)

    context = {
        'imports': imports,
        'page_title': 'ESR Import History',
    }
    return render(request, 'core/esr_import_list.html', context)

@login_required
def esr_import_create(request):
    """Create new ESR import - System Admin only"""
    # Check permissions - only system admin (superuser) or ICT Admin can access ESR imports
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role == 'ict_admin'):
        messages.error(request, 'You do not have permission to access ESR import functionality. System administrator access required.')
        return redirect('dashboard:dashboard')
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, 'Please select a file to import.')
            return redirect('core:esr_import_create')

        uploaded_file = request.FILES['file']
        import_type = request.POST.get('import_type')

        # Validate file type
        if not uploaded_file.name.endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, 'Please upload a CSV or Excel file.')
            return redirect('core:esr_import_create')

        # Create ESR import record
        esr_import = ESRImport.objects.create(
            file_name=uploaded_file.name,
            file_path=uploaded_file,
            import_type=import_type,
            imported_by=request.user,
            status='pending'
        )

        # Process the file
        try:
            process_esr_file(esr_import)
            messages.success(request, f'ESR file "{uploaded_file.name}" uploaded and processed successfully!')
        except Exception as e:
            esr_import.status = 'failed'
            esr_import.error_log = str(e)
            esr_import.save()
            messages.error(request, f'Error processing file: {str(e)}')

        return redirect('core:esr_import_detail', pk=esr_import.pk)

    context = {
        'page_title': 'Import ESR Data',
        'import_types': ESRImport.IMPORT_TYPE_CHOICES,
    }
    return render(request, 'core/esr_import_create.html', context)

@login_required
def esr_import_detail(request, pk):
    """ESR import detail view - System Admin only"""
    # Check permissions - only system admin (superuser) or ICT Admin can access ESR imports
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role == 'ict_admin'):
        messages.error(request, 'You do not have permission to access ESR import functionality. System administrator access required.')
        return redirect('dashboard:dashboard')
    esr_import = get_object_or_404(ESRImport, pk=pk)
    records = esr_import.records.all()

    # Pagination for records
    paginator = Paginator(records, 50)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)

    context = {
        'esr_import': esr_import,
        'records': records,
        'page_title': f'ESR Import - {esr_import.file_name}',
    }
    return render(request, 'core/esr_import_detail.html', context)

def process_esr_file(esr_import):
    """Process uploaded ESR file and import data"""
    esr_import.status = 'processing'
    esr_import.save()

    try:
        # Read the file
        file_path = esr_import.file_path.path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        esr_import.total_records = len(df)
        esr_import.save()

        successful = 0
        failed = 0

        # Process each row
        for index, row in df.iterrows():
            try:
                # Create import record
                import_record = ESRImportRecord.objects.create(
                    esr_import=esr_import,
                    row_number=index + 1,
                    raw_data=row.to_dict(),
                    status='pending'
                )

                # Process based on import type
                if esr_import.import_type == 'household':
                    process_household_record(import_record, row)
                elif esr_import.import_type == 'business_group':
                    process_business_group_record(import_record, row)
                elif esr_import.import_type == 'savings_group':
                    process_savings_group_record(import_record, row)
                else:
                    # Try to auto-detect and process
                    auto_process_record(import_record, row)

                import_record.status = 'processed'
                import_record.processed_at = timezone.now()
                import_record.save()
                successful += 1

            except Exception as e:
                import_record.status = 'failed'
                import_record.error_message = str(e)
                import_record.save()
                failed += 1

        # Update import status
        esr_import.successful_imports = successful
        esr_import.failed_imports = failed
        esr_import.status = 'completed'
        esr_import.completed_at = timezone.now()
        esr_import.import_summary = {
            'total': esr_import.total_records,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / esr_import.total_records) * 100 if esr_import.total_records > 0 else 0
        }
        esr_import.save()

    except Exception as e:
        esr_import.status = 'failed'
        esr_import.error_log = str(e)
        esr_import.completed_at = timezone.now()
        esr_import.save()
        raise

def process_household_record(import_record, row):
    """Process household data from ESR"""
    # Map ESR fields to UPG Household fields
    mapped_data = {}

    # Common ESR field mappings
    field_mapping = {
        'household_name': 'name',
        'household_head': 'name',
        'name': 'name',
        'national_id': 'national_id',
        'phone': 'phone_number',
        'phone_number': 'phone_number',
        'disability': 'disability',
        'village': 'village_name',
        'village_name': 'village_name',
    }

    for esr_field, upg_field in field_mapping.items():
        if esr_field in row.index and pd.notna(row[esr_field]):
            mapped_data[upg_field] = row[esr_field]

    import_record.mapped_data = mapped_data
    import_record.save()

    # Create household if doesn't exist
    if 'name' in mapped_data:
        household, created = Household.objects.get_or_create(
            name=mapped_data['name'],
            defaults={
                'national_id': mapped_data.get('national_id', ''),
                'phone_number': mapped_data.get('phone_number', ''),
                'disability': mapped_data.get('disability', False),
            }
        )

        import_record.created_object_type = 'Household'
        import_record.created_object_id = str(household.id)
        import_record.save()

def process_business_group_record(import_record, row):
    """Process business group data from ESR"""
    mapped_data = {}

    # Business group field mappings
    field_mapping = {
        'group_name': 'name',
        'business_group_name': 'name',
        'name': 'name',
        'business_type': 'business_type',
        'formation_date': 'formation_date',
        'group_size': 'group_size',
    }

    for esr_field, upg_field in field_mapping.items():
        if esr_field in row.index and pd.notna(row[esr_field]):
            mapped_data[upg_field] = row[esr_field]

    import_record.mapped_data = mapped_data
    import_record.save()

    # Create business group if doesn't exist
    if 'name' in mapped_data:
        business_group, created = BusinessGroup.objects.get_or_create(
            name=mapped_data['name'],
            defaults={
                'business_type': mapped_data.get('business_type', 'crop'),
                'group_size': mapped_data.get('group_size', 2),
            }
        )

        import_record.created_object_type = 'BusinessGroup'
        import_record.created_object_id = str(business_group.id)
        import_record.save()

def process_savings_group_record(import_record, row):
    """Process savings group data from ESR"""
    mapped_data = {}

    # Savings group field mappings
    field_mapping = {
        'group_name': 'name',
        'savings_group_name': 'name',
        'name': 'name',
        'formation_date': 'formation_date',
        'target_members': 'target_members',
        'total_savings': 'total_savings',
    }

    for esr_field, upg_field in field_mapping.items():
        if esr_field in row.index and pd.notna(row[esr_field]):
            mapped_data[upg_field] = row[esr_field]

    import_record.mapped_data = mapped_data
    import_record.save()

    # Create savings group if doesn't exist
    if 'name' in mapped_data:
        savings_group, created = BusinessSavingsGroup.objects.get_or_create(
            name=mapped_data['name'],
            defaults={
                'target_members': mapped_data.get('target_members', 20),
            }
        )

        import_record.created_object_type = 'BusinessSavingsGroup'
        import_record.created_object_id = str(savings_group.id)
        import_record.save()

def auto_process_record(import_record, row):
    """Auto-detect and process mixed ESR data"""
    # Try to determine what type of data this is based on columns
    columns = [col.lower() for col in row.index]

    if any(col in columns for col in ['household_name', 'household_head']):
        process_household_record(import_record, row)
    elif any(col in columns for col in ['business_group_name', 'group_name']):
        if any(col in columns for col in ['savings', 'total_savings']):
            process_savings_group_record(import_record, row)
        else:
            process_business_group_record(import_record, row)
    else:
        # Default to household
        process_household_record(import_record, row)


# API Endpoints for AJAX calls

@login_required
def api_bm_cycles(request):
    """API endpoint to get BM cycles for dropdowns"""
    user = request.user

    # Check permissions
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    cycles = BusinessMentorCycle.objects.all().order_by('bm_cycle_name')

    # Apply role-based filtering if needed
    if user.role == 'mentor':
        # Mentors only see cycles they're involved in
        cycles = cycles.filter(assigned_mentor=user)
    elif user.role == 'field_associate':
        # Field associates see cycles in their assigned villages
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            cycles = cycles.filter(village__in=assigned_villages)

    data = [
        {
            'id': cycle.id,
            'bm_cycle_name': cycle.bm_cycle_name,
            'village': cycle.village.name if cycle.village else 'N/A'
        }
        for cycle in cycles
    ]

    return JsonResponse(data, safe=False)

@login_required
def api_mentors(request):
    """API endpoint to get mentors for dropdowns"""
    user = request.user

    # Check permissions
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate']):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    mentors = User.objects.filter(role='mentor', is_active=True).order_by('first_name', 'last_name')

    # Apply role-based filtering if needed
    if user.role == 'field_associate':
        # Field associates can only assign mentors in their villages
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            mentors = mentors.filter(profile__assigned_villages__in=assigned_villages).distinct()

    data = [
        {
            'id': mentor.id,
            'full_name': mentor.get_full_name() or mentor.username,
            'username': mentor.username,
            'villages': [v.name for v in mentor.profile.assigned_villages.all()] if hasattr(mentor, 'profile') and mentor.profile else []
        }
        for mentor in mentors
    ]

    return JsonResponse(data, safe=False)


@login_required
def assign_mentor_to_village(request):
    """Field associates assign mentors to villages"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Only field associates and admins can assign mentors
    if not (user.is_superuser or user_role in ['field_associate', 'ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to assign mentors.')
        return redirect('dashboard:dashboard')

    # Get villages - field associates see only their assigned villages
    from .models import Village
    if user_role == 'field_associate':
        if hasattr(user, 'profile') and user.profile:
            villages = user.profile.assigned_villages.all()
        else:
            villages = Village.objects.none()
    else:
        villages = Village.objects.all().select_related('subcounty_obj')

    # Get mentors
    mentors = User.objects.filter(role='mentor').select_related('profile')

    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        village_ids = request.POST.getlist('village_ids[]')

        if not mentor_id or not village_ids:
            messages.error(request, 'Please select a mentor and at least one village.')
            return redirect('core:assign_mentor_to_village')

        try:
            mentor = User.objects.get(id=mentor_id, role='mentor')

            # Get or create profile
            from accounts.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=mentor)

            # Assign villages
            selected_villages = Village.objects.filter(id__in=village_ids)
            profile.assigned_villages.add(*selected_villages)

            village_names = ', '.join([v.name for v in selected_villages])
            messages.success(
                request,
                f'Successfully assigned {mentor.get_full_name()} to {len(selected_villages)} village(s): {village_names}'
            )
            return redirect('core:assign_mentor_to_village')

        except User.DoesNotExist:
            messages.error(request, 'Selected mentor not found.')
        except Exception as e:
            messages.error(request, f'Error assigning mentor: {str(e)}')

    context = {
        'page_title': 'Assign Mentor to Villages',
        'villages': villages.order_by('subcounty_obj__name', 'name'),
        'mentors': mentors.order_by('first_name', 'last_name'),
    }
    return render(request, 'core/assign_mentor.html', context)


@login_required
def mentor_villages_list(request):
    """View all mentor-village assignments"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['field_associate', 'ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to view mentor assignments.')
        return redirect('dashboard:dashboard')

    # Get all mentors with their assigned villages
    mentors = User.objects.filter(role='mentor').select_related('profile').prefetch_related('profile__assigned_villages__subcounty_obj')

    # Filter for field associates
    if user_role == 'field_associate':
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            mentors = mentors.filter(profile__assigned_villages__in=assigned_villages).distinct()

    context = {
        'page_title': 'Mentor-Village Assignments',
        'mentors': mentors,
    }
    return render(request, 'core/mentor_villages_list.html', context)


@login_required
def remove_mentor_village(request, mentor_id, village_id):
    """Remove a village from a mentor's assignment"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['field_associate', 'ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to modify mentor assignments.')
        return redirect('dashboard:dashboard')

    try:
        from .models import Village
        mentor = User.objects.get(id=mentor_id, role='mentor')
        village = Village.objects.get(id=village_id)

        # Check if field associate has permission for this village
        if user_role == 'field_associate':
            if hasattr(user, 'profile') and user.profile:
                if village not in user.profile.assigned_villages.all():
                    messages.error(request, 'You do not have permission to modify this village assignment.')
                    return redirect('core:mentor_villages_list')

        if hasattr(mentor, 'profile') and mentor.profile:
            mentor.profile.assigned_villages.remove(village)
            messages.success(
                request,
                f'Removed {village.name} from {mentor.get_full_name()}\'s assignments.'
            )
        else:
            messages.error(request, 'Mentor profile not found.')

    except (User.DoesNotExist, Village.DoesNotExist):
        messages.error(request, 'Mentor or village not found.')
    except Exception as e:
        messages.error(request, f'Error removing assignment: {str(e)}')

    return redirect('core:mentor_villages_list')


@login_required
def bm_cycle_list(request):
    """List all BM Cycles"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        messages.error(request, 'You do not have permission to manage BM Cycles.')
        return redirect('dashboard:dashboard')

    cycles = BusinessMentorCycle.objects.all().select_related('business_mentor').order_by('-created_at')

    context = {
        'page_title': 'Business Mentor Cycles',
        'cycles': cycles,
    }
    return render(request, 'core/bm_cycle_list.html', context)


@login_required
def bm_cycle_create(request):
    """Create a new BM Cycle"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        messages.error(request, 'You do not have permission to create BM Cycles.')
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        try:
            from .models import Mentor

            bm_cycle_name = request.POST.get('bm_cycle_name')
            business_mentor_id = request.POST.get('business_mentor')
            field_associate = request.POST.get('field_associate')
            cycle = request.POST.get('cycle')
            project = request.POST.get('project')
            office = request.POST.get('office')

            business_mentor = Mentor.objects.get(id=business_mentor_id)

            bm_cycle = BusinessMentorCycle.objects.create(
                bm_cycle_name=bm_cycle_name,
                business_mentor=business_mentor,
                field_associate=field_associate,
                cycle=cycle,
                project=project,
                office=office
            )

            messages.success(request, f'BM Cycle "{bm_cycle_name}" created successfully!')
            return redirect('core:bm_cycle_list')

        except Exception as e:
            messages.error(request, f'Error creating BM Cycle: {str(e)}')

    # Get mentors and field associates for dropdowns
    from .models import Mentor
    mentors = Mentor.objects.all().order_by('first_name', 'last_name')
    field_associates = User.objects.filter(role='field_associate').order_by('first_name', 'last_name')

    context = {
        'page_title': 'Create BM Cycle',
        'mentors': mentors,
        'field_associates': field_associates,
        'cycle': None,
    }
    return render(request, 'core/bm_cycle_form.html', context)


@login_required
def bm_cycle_edit(request, cycle_id):
    """Edit an existing BM Cycle"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        messages.error(request, 'You do not have permission to edit BM Cycles.')
        return redirect('dashboard:dashboard')

    cycle = get_object_or_404(BusinessMentorCycle, id=cycle_id)

    if request.method == 'POST':
        try:
            from .models import Mentor

            cycle.bm_cycle_name = request.POST.get('bm_cycle_name')
            cycle.business_mentor = Mentor.objects.get(id=request.POST.get('business_mentor'))
            cycle.field_associate = request.POST.get('field_associate')
            cycle.cycle = request.POST.get('cycle')
            cycle.project = request.POST.get('project')
            cycle.office = request.POST.get('office')
            cycle.save()

            messages.success(request, f'BM Cycle "{cycle.bm_cycle_name}" updated successfully!')
            return redirect('core:bm_cycle_list')

        except Exception as e:
            messages.error(request, f'Error updating BM Cycle: {str(e)}')

    # Get mentors and field associates for dropdowns
    from .models import Mentor
    mentors = Mentor.objects.all().order_by('first_name', 'last_name')
    field_associates = User.objects.filter(role='field_associate').order_by('first_name', 'last_name')

    context = {
        'page_title': 'Edit BM Cycle',
        'cycle': cycle,
        'mentors': mentors,
        'field_associates': field_associates,
    }
    return render(request, 'core/bm_cycle_form.html', context)


@login_required
def bm_cycle_delete(request, cycle_id):
    """Delete a BM Cycle"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if not (user.is_superuser or user_role in ['ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to delete BM Cycles.')
        return redirect('dashboard:dashboard')

    try:
        cycle = get_object_or_404(BusinessMentorCycle, id=cycle_id)
        cycle_name = cycle.bm_cycle_name
        cycle.delete()
        messages.success(request, f'BM Cycle "{cycle_name}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting BM Cycle: {str(e)}')

    return redirect('core:bm_cycle_list')
```

---


## File: dashboard\__init__.py

**Location:** `dashboard\__init__.py`

```python
# Dashboard App
```

---


## File: dashboard\urls.py

**Location:** `dashboard\urls.py`

```python
"""
Dashboard URL Configuration
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]
```

---


## File: dashboard\views.py

**Location:** `dashboard\views.py`

```python
"""
Dashboard Views for UPG System
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from households.models import Household, HouseholdProgram
from business_groups.models import BusinessGroup
from upg_grants.models import SBGrant, PRGrant, HouseholdGrantApplication
from savings_groups.models import BusinessSavingsGroup
from training.models import Training, MentoringVisit, PhoneNudge, MentoringReport, HouseholdTrainingEnrollment
from core.models import BusinessMentorCycle


@login_required
def dashboard_view(request):
    """Role-based dashboard routing"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Route to specific dashboard based on role
    if user.is_superuser or user_role == 'ict_admin':
        return admin_dashboard_view(request)
    elif user_role == 'mentor':
        return mentor_dashboard_view(request)
    elif user_role in ['county_executive', 'county_assembly']:
        return executive_dashboard_view(request)
    elif user_role in ['me_staff', 'cco_director']:
        return me_dashboard_view(request)
    elif user_role == 'field_associate':
        return field_associate_dashboard_view(request)
    else:
        return general_dashboard_view(request)


@login_required
def admin_dashboard_view(request):
    """System Administrator dashboard view"""
    user = request.user

    # Program Overview Statistics
    program_overview = {
        'total_households_enrolled': Household.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
        'graduation_rate': 0,  # Calculate graduation percentage
        'program_completion_status': '65%'  # Example completion
    }

    # Geographic Coverage - Updated to use subcounty_obj
    geographic_coverage = {
        'villages_by_county': Household.objects.values('village__subcounty_obj').distinct().count(),
        'household_distribution': Household.objects.count(),
        'mentor_coverage_map': 'West Pokot Focus',  # Example
        'saturation_levels': '42%'  # Example
    }

    # Financial Metrics - Calculate total disbursed from all grant types
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    financial_metrics = {
        'grants_disbursed': sb_disbursed + pr_disbursed + household_disbursed,
        'business_progress': BusinessGroup.objects.filter(participation_status='active').count(),
        'savings_accumulated': BusinessSavingsGroup.objects.filter(is_active=True).count() * 50000,  # Example
        'income_generation': '125%'  # Example increase
    }

    # Training Progress
    training_progress = {
        'modules_completed': 8,  # Example
        'attendance_rates': '89%',
        'skill_development': 'High',
        'mentoring_sessions': 156  # Example
    }

    # Basic statistics for existing cards - Include all grant types
    stats = {
        'total_households': Household.objects.count(),
        'active_households': HouseholdProgram.objects.filter(participation_status='active').count(),
        'graduated_households': HouseholdProgram.objects.filter(participation_status='graduated').count(),
        'total_business_groups': BusinessGroup.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
        'total_savings_groups': BusinessSavingsGroup.objects.filter(is_active=True).count(),
        'sb_grants_funded': SBGrant.objects.filter(status='disbursed').count(),
        'pr_grants_funded': PRGrant.objects.filter(status='disbursed').count(),
        'household_grants_funded': HouseholdGrantApplication.objects.filter(status='disbursed').count(),
        'total_grants_funded': (
            SBGrant.objects.filter(status='disbursed').count() +
            PRGrant.objects.filter(status='disbursed').count() +
            HouseholdGrantApplication.objects.filter(status='disbursed').count()
        ),
        # Mentor activity logs for admin
        'total_house_visits': MentoringVisit.objects.count(),
        'total_phone_calls': PhoneNudge.objects.count(),
        'recent_house_visits': MentoringVisit.objects.filter(
            visit_date__gte=timezone.now().date() - timedelta(days=30)
        ).count(),
        'recent_phone_calls': PhoneNudge.objects.filter(
            call_date__gte=timezone.now().date() - timedelta(days=30)
        ).count(),
    }

    # Role-specific data
    if user.role == 'mentor':
        # Mentor sees only their assigned villages/households
        if hasattr(user, 'profile') and user.profile:
            try:
                assigned_villages = user.profile.assigned_villages
                # Check if it's a QuerySet or Manager
                if hasattr(assigned_villages, 'all'):
                    stats['assigned_villages'] = assigned_villages.count()
                elif assigned_villages is not None:
                    # It's a list or other iterable
                    stats['assigned_villages'] = len(assigned_villages)
                else:
                    stats['assigned_villages'] = 0
            except (AttributeError, TypeError):
                stats['assigned_villages'] = 0
        else:
            stats['assigned_villages'] = 0

    elif user.role in ['county_executive', 'county_assembly']:
        # County-level users see high-level summaries
        pass

    elif user.role in ['me_staff', 'cco_director']:
        # M&E and directors see all data
        pass

    context = {
        'user': user,
        'stats': stats,
        'program_overview': program_overview,
        'geographic_coverage': geographic_coverage,
        'financial_metrics': financial_metrics,
        'training_progress': training_progress,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def mentor_dashboard_view(request):
    """Mentor-specific dashboard with training assignments"""
    user = request.user

    # Get mentor's assigned trainings
    assigned_trainings = Training.objects.filter(assigned_mentor=user).order_by('-start_date')

    # Get current/active trainings (includes trainings without end_date)
    from django.db.models import Q
    current_date = timezone.now().date()
    current_trainings = assigned_trainings.filter(
        Q(status__in=['planned', 'active']) &
        Q(start_date__lte=current_date) &
        (Q(end_date__gte=current_date) | Q(end_date__isnull=True))
    )

    # Get households in mentor's assigned villages (more comprehensive)
    if hasattr(user, 'profile') and user.profile:
        try:
            assigned_villages = user.profile.assigned_villages.all()
        except (AttributeError, TypeError):
            # Handle case where assigned_villages might be a list instead of QuerySet
            assigned_villages = getattr(user.profile, 'assigned_villages', [])
            if not hasattr(assigned_villages, 'all'):
                assigned_villages = list(assigned_villages) if assigned_villages else []

        if assigned_villages:
            mentor_households = Household.objects.filter(village__in=assigned_villages).distinct()
        else:
            mentor_households = Household.objects.none()
    else:
        # Fallback to households in mentor's trainings
        mentor_households = Household.objects.filter(
            current_training_enrollment__training__assigned_mentor=user
        ).distinct()

    # Recent mentoring activities (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_visits = MentoringVisit.objects.filter(
        mentor=user,
        visit_date__gte=thirty_days_ago
    ).order_by('-visit_date')

    recent_nudges = PhoneNudge.objects.filter(
        mentor=user,
        call_date__gte=thirty_days_ago
    ).order_by('-call_date')

    # Grant statistics for mentor's households
    mentor_grant_applications = HouseholdGrantApplication.objects.filter(
        household__in=mentor_households
    ).select_related('household', 'program')

    grant_stats = {
        'total_applications': mentor_grant_applications.count(),
        'applied': mentor_grant_applications.filter(status__in=['submitted', 'draft']).count(),
        'under_review': mentor_grant_applications.filter(status='under_review').count(),
        'approved': mentor_grant_applications.filter(status='approved').count(),
        'disbursed': mentor_grant_applications.filter(status='disbursed').count(),
        'rejected': mentor_grant_applications.filter(status='rejected').count(),
    }

    # Recent grant applications (last 5)
    recent_grants = mentor_grant_applications.order_by('-created_at')[:5]

    # Stats for mentor dashboard
    stats = {
        'assigned_trainings': assigned_trainings.count(),
        'active_trainings': current_trainings.count(),
        'total_households': mentor_households.count(),
        'visits_this_month': recent_visits.count(),
        'nudges_this_month': recent_nudges.count(),
        'pending_reports': 0,  # Can be calculated based on reporting schedule
        'total_grant_applications': grant_stats['total_applications'],
    }

    # Upcoming activities (next 7 days)
    upcoming_trainings = assigned_trainings.filter(
        start_date__gte=timezone.now().date(),
        start_date__lte=timezone.now().date() + timedelta(days=7)
    )

    context = {
        'user': user,
        'stats': stats,
        'assigned_trainings': assigned_trainings[:5],  # Latest 5
        'current_trainings': current_trainings,
        'mentor_households': mentor_households,  # All assigned households
        'recent_visits': recent_visits[:5],
        'recent_nudges': recent_nudges[:5],
        'upcoming_trainings': upcoming_trainings,
        'grant_stats': grant_stats,
        'recent_grants': recent_grants,
        'dashboard_type': 'mentor',
    }

    return render(request, 'dashboard/mentor_dashboard.html', context)


@login_required
def executive_dashboard_view(request):
    """County Executive dashboard with high-level metrics"""
    user = request.user

    # High-level statistics - Include all grant types
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    stats = {
        'total_households': Household.objects.count(),
        'active_households': HouseholdProgram.objects.filter(participation_status='active').count(),
        'total_trainings': Training.objects.count(),
        'active_mentors': Training.objects.values('assigned_mentor').distinct().count(),
        'grants_disbursed': sb_disbursed + pr_disbursed + household_disbursed,
        'total_grants_funded': (
            SBGrant.objects.filter(status='disbursed').count() +
            PRGrant.objects.filter(status='disbursed').count() +
            HouseholdGrantApplication.objects.filter(status='disbursed').count()
        ),
    }

    context = {
        'user': user,
        'stats': stats,
        'dashboard_type': 'executive',
    }

    return render(request, 'dashboard/executive_dashboard.html', context)


@login_required
def me_dashboard_view(request):
    """M&E Staff dashboard with monitoring data"""
    user = request.user

    # Get date ranges
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    seven_days_ago = timezone.now().date() - timedelta(days=7)

    # Monitoring & Evaluation specific metrics
    stats = {
        'total_reports': MentoringReport.objects.count(),
        'pending_reports': MentoringReport.objects.filter(
            submitted_date__gte=thirty_days_ago
        ).count(),
        'training_completion_rate': 0,  # Calculate based on training completion
        'household_visits': MentoringVisit.objects.filter(
            visit_date__gte=thirty_days_ago
        ).count(),
        'phone_nudges': PhoneNudge.objects.filter(
            call_date__gte=thirty_days_ago
        ).count(),
        'total_mentor_activities': MentoringVisit.objects.count() + PhoneNudge.objects.count(),
        'recent_visits': MentoringVisit.objects.filter(
            visit_date__gte=seven_days_ago
        ).count(),
        'recent_calls': PhoneNudge.objects.filter(
            call_date__gte=seven_days_ago
        ).count(),
    }

    # Recent mentor activities (last 30 days) - combining visits and calls
    recent_visits = MentoringVisit.objects.filter(
        visit_date__gte=thirty_days_ago
    ).select_related('household', 'mentor', 'household__village').order_by('-visit_date')[:10]

    recent_calls = PhoneNudge.objects.filter(
        call_date__gte=thirty_days_ago
    ).select_related('household', 'mentor', 'household__village').order_by('-call_date')[:10]

    # Mentor activity summary by mentor
    from django.db.models import Count
    mentor_activity = []
    from accounts.models import User
    mentors = User.objects.filter(role='mentor')
    for mentor in mentors:
        visit_count = MentoringVisit.objects.filter(
            mentor=mentor,
            visit_date__gte=thirty_days_ago
        ).count()
        call_count = PhoneNudge.objects.filter(
            mentor=mentor,
            call_date__gte=thirty_days_ago
        ).count()
        mentor_activity.append({
            'mentor': mentor,
            'visits': visit_count,
            'calls': call_count,
            'total': visit_count + call_count
        })

    # Sort by total activity
    mentor_activity.sort(key=lambda x: x['total'], reverse=True)

    context = {
        'user': user,
        'stats': stats,
        'recent_visits': recent_visits,
        'recent_calls': recent_calls,
        'mentor_activity': mentor_activity[:10],  # Top 10 most active mentors
        'dashboard_type': 'me',
    }

    return render(request, 'dashboard/me_dashboard.html', context)


@login_required
def field_associate_dashboard_view(request):
    """Field Associate dashboard with mentor oversight"""
    user = request.user

    # Field Associate specific metrics
    stats = {
        'managed_mentors': Training.objects.values('assigned_mentor').distinct().count(),
        'total_trainings': Training.objects.count(),
        'active_trainings': Training.objects.filter(status='active').count(),
        'households_in_training': HouseholdTrainingEnrollment.objects.filter(
            enrollment_status='enrolled'
        ).count(),
    }

    context = {
        'user': user,
        'stats': stats,
        'dashboard_type': 'field_associate',
    }

    return render(request, 'dashboard/field_associate_dashboard.html', context)


@login_required
def general_dashboard_view(request):
    """General dashboard for users without specific roles"""
    user = request.user

    # Basic statistics
    stats = {
        'total_households': Household.objects.count(),
        'total_business_groups': BusinessGroup.objects.count(),
        'total_trainings': Training.objects.count(),
        'system_users': user._meta.model.objects.count(),
    }

    context = {
        'user': user,
        'stats': stats,
        'dashboard_type': 'general',
    }

    return render(request, 'dashboard/general_dashboard.html', context)
```

---


## File: forms\__init__.py

**Location:** `forms\__init__.py`

```python

```

---


## File: forms\admin.py

**Location:** `forms\admin.py`

```python
from django.contrib import admin

# Register your models here.

```

---


## File: forms\apps.py

**Location:** `forms\apps.py`

```python
from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forms'

```

---


## File: forms\models.py

**Location:** `forms\models.py`

```python
"""
Dynamic Forms System for UPG Management
Allows M&E staff to create editable forms/surveys and assign them to field associates/mentors
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class FormTemplate(models.Model):
    """
    Dynamic form template created by M&E staff
    """
    FORM_TYPE_CHOICES = [
        ('household_survey', 'Household Survey'),
        ('business_survey', 'Business Progress Survey'),
        ('ppi_assessment', 'PPI Assessment'),
        ('baseline_survey', 'Baseline Survey'),
        ('midline_survey', 'Midline Survey'),
        ('endline_survey', 'Endline Survey'),
        ('training_evaluation', 'Training Evaluation'),
        ('mentoring_report', 'Mentoring Report'),
        ('custom_form', 'Custom Form'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=30, choices=FORM_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Form structure stored as JSON
    form_fields = models.JSONField(default=list, help_text="JSON structure defining form fields")

    # Assignment and workflow
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Form settings
    allow_multiple_submissions = models.BooleanField(default=False)
    require_photo_evidence = models.BooleanField(default=False)
    require_gps_location = models.BooleanField(default=False)
    auto_assign_to_mentors = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.get_form_type_display()})"

    class Meta:
        db_table = 'upg_form_templates'
        ordering = ['-created_at']


class FormAssignment(models.Model):
    """
    Assignment of forms to field associates or mentors
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    ASSIGNMENT_TYPE_CHOICES = [
        ('direct_to_mentor', 'Direct to Mentor'),
        ('via_field_associate', 'Via Field Associate'),
    ]

    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_assignments_made')

    # Assignment can be to field associate who then assigns to mentors, or directly to mentor
    assignment_type = models.CharField(max_length=30, choices=ASSIGNMENT_TYPE_CHOICES)
    field_associate = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='assigned_forms',
                                       limit_choices_to={'role': 'field_associate'})
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='assigned_forms_mentor',
                              limit_choices_to={'role': 'mentor'})

    # Assignment details
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')

    # Status tracking
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Target criteria (optional filters for which households/groups to survey)
    target_villages = models.JSONField(default=list, blank=True)
    target_households = models.JSONField(default=list, blank=True)
    target_business_groups = models.JSONField(default=list, blank=True)
    min_submissions_required = models.IntegerField(default=1)

    def __str__(self):
        assignee = self.mentor or self.field_associate
        return f"{self.title} -> {assignee.get_full_name() if assignee else 'Unassigned'}"

    def clean(self):
        if self.assignment_type == 'direct_to_mentor' and not self.mentor:
            raise ValidationError("Mentor is required for direct assignments")
        if self.assignment_type == 'via_field_associate' and not self.field_associate:
            raise ValidationError("Field associate is required for field associate assignments")

    class Meta:
        db_table = 'upg_form_assignments'
        ordering = ['-assigned_at']


class FormSubmission(models.Model):
    """
    Individual form submissions by mentors
    """
    SUBMISSION_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name='submissions')
    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE)

    # Submitter details
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions')
    submission_date = models.DateTimeField(auto_now_add=True)

    # Form data stored as JSON
    form_data = models.JSONField(default=dict)

    # Optional attachments
    photo_evidence = models.ImageField(upload_to='form_submissions/photos/', null=True, blank=True)
    document_attachment = models.FileField(upload_to='form_submissions/docs/', null=True, blank=True)

    # Location data
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=200, blank=True)

    # Review and approval
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='draft')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Related entities (optional)
    household = models.ForeignKey('households.Household', on_delete=models.SET_NULL, null=True, blank=True)
    business_group = models.ForeignKey('business_groups.BusinessGroup', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.form_template.name} - {self.submitted_by.get_full_name()} - {self.submission_date.strftime('%Y-%m-%d')}"

    class Meta:
        db_table = 'upg_form_submissions'
        ordering = ['-submission_date']


class FormField(models.Model):
    """
    Individual form field definition for building dynamic forms
    """
    FIELD_TYPE_CHOICES = [
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('number', 'Number Input'),
        ('email', 'Email Input'),
        ('phone', 'Phone Number'),
        ('date', 'Date Picker'),
        ('datetime', 'Date & Time'),
        ('select', 'Dropdown Select'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('boolean', 'Yes/No'),
        ('file', 'File Upload'),
        ('image', 'Image Upload'),
        ('rating', 'Rating Scale'),
        ('location', 'GPS Location'),
        ('signature', 'Digital Signature'),
    ]

    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)

    # Field configuration
    required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=500, blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    default_value = models.CharField(max_length=500, blank=True)

    # For select, radio, checkbox fields
    choices = models.JSONField(default=list, blank=True, help_text="List of choices for select/radio/checkbox fields")

    # Field validation
    min_length = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    validation_regex = models.CharField(max_length=500, blank=True)

    # Display order
    order = models.IntegerField(default=0)

    # Conditional display
    show_if_field = models.CharField(max_length=100, blank=True, help_text="Show this field only if another field has specific value")
    show_if_value = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.form_template.name} - {self.field_label}"

    class Meta:
        db_table = 'upg_form_fields'
        ordering = ['order', 'id']


class FormAssignmentMentor(models.Model):
    """
    Many-to-many relationship for field associates assigning forms to multiple mentors
    """
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mentor'})
    assigned_by_fa = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fa_mentor_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.assignment.title} -> {self.mentor.get_full_name()}"

    class Meta:
        db_table = 'upg_form_assignment_mentors'
        unique_together = ['assignment', 'mentor']

```

---


## File: forms\tests.py

**Location:** `forms\tests.py`

```python
from django.test import TestCase

# Create your tests here.

```

---


## File: forms\urls.py

**Location:** `forms\urls.py`

```python
from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.forms_dashboard, name='dashboard'),

    # Form Templates
    path('templates/', views.form_template_list, name='template_list'),
    path('templates/create/', views.form_template_create, name='template_create'),
    path('templates/<int:pk>/builder/', views.form_template_builder, name='template_builder'),

    # Form Assignments
    path('assignments/create/', views.form_assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_pk>/assign-mentor/', views.assign_to_mentor, name='assign_to_mentor'),
    path('assignments/<int:assignment_pk>/fill/', views.fill_form, name='fill_form'),

    # Submissions
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),

    # User-specific views
    path('my-assignments/', views.my_assignments, name='my_assignments'),
]
```

---


## File: forms\views.py

**Location:** `forms\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
import json

from .models import FormTemplate, FormAssignment, FormSubmission, FormField, FormAssignmentMentor
from core.models import Village
from households.models import Household
from business_groups.models import BusinessGroup

User = get_user_model()

@login_required
def forms_dashboard(request):
    """Main forms dashboard showing different views based on user role"""
    user = request.user
    context = {
        'page_title': 'Dynamic Forms Dashboard',
    }

    if user.role in ['me_staff', 'ict_admin'] or user.is_superuser:
        # M&E staff view - can create and manage forms
        form_templates = FormTemplate.objects.filter(created_by=user)[:5]
        recent_assignments = FormAssignment.objects.filter(assigned_by=user)[:5]
        recent_submissions = FormSubmission.objects.all()[:5]

        context.update({
            'can_create_forms': True,
            'form_templates': form_templates,
            'recent_assignments': recent_assignments,
            'recent_submissions': recent_submissions,
            'total_templates': FormTemplate.objects.filter(created_by=user).count(),
            'active_assignments': FormAssignment.objects.filter(assigned_by=user, status__in=['pending', 'accepted', 'in_progress']).count(),
        })

    elif user.role == 'field_associate':
        # Field associate view - can assign forms to mentors
        assigned_forms = FormAssignment.objects.filter(field_associate=user)
        my_mentor_assignments = FormAssignmentMentor.objects.filter(assigned_by_fa=user)

        context.update({
            'can_assign_to_mentors': True,
            'assigned_forms': assigned_forms,
            'mentor_assignments': my_mentor_assignments,
            'pending_assignments': assigned_forms.filter(status='pending').count(),
        })

    elif user.role == 'mentor':
        # Mentor view - can fill out assigned forms
        my_assignments = FormAssignment.objects.filter(mentor=user)
        my_mentor_assignments = FormAssignmentMentor.objects.filter(mentor=user)
        my_submissions = FormSubmission.objects.filter(submitted_by=user)

        context.update({
            'can_fill_forms': True,
            'my_assignments': my_assignments,
            'my_mentor_assignments': my_mentor_assignments,
            'my_submissions': my_submissions,
            'pending_forms': (my_assignments.filter(status__in=['pending', 'accepted']).count() +
                            my_mentor_assignments.filter(status__in=['pending', 'accepted']).count()),
        })

    return render(request, 'forms/dashboard.html', context)

```

---


## File: grants\__init__.py

**Location:** `grants\__init__.py`

```python

```

---


## File: grants\apps.py

**Location:** `grants\apps.py`

```python
from django.apps import AppConfig


class GrantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'grants'
```

---


## File: grants\urls.py

**Location:** `grants\urls.py`

```python
from django.urls import path
from . import views

app_name = 'grants'

urlpatterns = [
    path('', views.grants_dashboard, name='grants_dashboard'),
    path('sb-grants/', views.sb_grant_applications, name='sb_grant_applications'),
    path('pr-grants/', views.pr_grant_applications, name='pr_grant_applications'),
    path('grant/<str:grant_type>/<int:grant_id>/', views.grant_detail, name='grant_detail'),
    path('grant/<str:grant_type>/<int:grant_id>/process/', views.process_grant, name='process_grant'),
]
```

---


## File: grants\views.py

**Location:** `grants\views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from upg_grants.models import SBGrant, PRGrant, GrantDisbursement, HouseholdGrantApplication
from business_groups.models import BusinessGroup
from programs.models import Program
from households.models import Household

@login_required
def grants_dashboard(request):
    """Grants management dashboard with comprehensive statistics"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'county_executive', 'field_associate']):
        messages.error(request, 'You do not have permission to access grants management.')
        return redirect('dashboard:dashboard')

    # SB Grant Statistics
    sb_grants = {
        'total': SBGrant.objects.count(),
        'pending': SBGrant.objects.filter(status='pending').count(),
        'approved': SBGrant.objects.filter(status='approved').count(),
        'funded': SBGrant.objects.filter(status='disbursed').count(),
        'rejected': SBGrant.objects.filter(status='rejected').count(),
        'total_amount_funded': SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0,
    }

    # PR Grant Statistics
    pr_grants = {
        'total': PRGrant.objects.count(),
        'pending': PRGrant.objects.filter(status='pending').count(),
        'approved': PRGrant.objects.filter(status='approved').count(),
        'funded': PRGrant.objects.filter(status='disbursed').count(),
        'rejected': PRGrant.objects.filter(status='rejected').count(),
        'total_amount_funded': PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0,
    }

    # Household Grant Statistics
    household_grants = {
        'total': HouseholdGrantApplication.objects.count(),
        'pending': HouseholdGrantApplication.objects.filter(status__in=['submitted', 'under_review']).count(),
        'approved': HouseholdGrantApplication.objects.filter(status='approved').count(),
        'disbursed': HouseholdGrantApplication.objects.filter(status='disbursed').count(),
        'rejected': HouseholdGrantApplication.objects.filter(status='rejected').count(),
        'total_amount_approved': HouseholdGrantApplication.objects.filter(status='approved').aggregate(total=Sum('approved_amount'))['total'] or 0,
    }

    # Recent activities
    recent_sb_grants = SBGrant.objects.all().order_by('-created_at')[:5]
    recent_pr_grants = PRGrant.objects.all().order_by('-created_at')[:5]
    recent_household_grants = HouseholdGrantApplication.objects.all().order_by('-created_at')[:5]

    # Disbursement statistics - aggregate from all grant types
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    total_disbursed = sb_disbursed + pr_disbursed + household_disbursed

    # Pending disbursements (approved but not yet disbursed)
    sb_pending = SBGrant.objects.filter(status='approved').count()
    pr_pending = PRGrant.objects.filter(status='approved').count()
    household_pending = HouseholdGrantApplication.objects.filter(status='approved').count()
    pending_count = sb_pending + pr_pending + household_pending

    # Completed disbursements count
    sb_completed = SBGrant.objects.filter(status='disbursed').count()
    pr_completed = PRGrant.objects.filter(status='disbursed').count()
    household_completed = HouseholdGrantApplication.objects.filter(status='disbursed').count()
    completed_count = sb_completed + pr_completed + household_completed

    disbursements = {
        'total_disbursed': total_disbursed,
        'pending_disbursements': pending_count,
        'completed_disbursements': completed_count,
        'sb_disbursed': sb_disbursed,
        'pr_disbursed': pr_disbursed,
        'household_disbursed': household_disbursed,
    }

    # Get available applicants for grant application
    households = Household.objects.all().order_by('name')
    business_groups = BusinessGroup.objects.all().order_by('name')

    from savings_groups.models import BusinessSavingsGroup
    savings_groups = BusinessSavingsGroup.objects.filter(is_active=True).order_by('name')

    context = {
        'page_title': 'Grants Management Dashboard',
        'sb_grants': sb_grants,
        'pr_grants': pr_grants,
        'household_grants': household_grants,
        'disbursements': disbursements,
        'recent_sb_grants': recent_sb_grants,
        'recent_pr_grants': recent_pr_grants,
        'recent_household_grants': recent_household_grants,
        'total_grants': sb_grants['total'] + pr_grants['total'] + household_grants['total'],
        'total_funding': sb_grants['total_amount_funded'] + pr_grants['total_amount_funded'] + household_grants['total_amount_approved'],
        'households': households,
        'business_groups': business_groups,
        'savings_groups': savings_groups,
    }
    return render(request, 'grants/grants_dashboard.html', context)

@login_required
def sb_grant_applications(request):
    """View and process SB grant applications"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'county_executive', 'field_associate']):
        messages.error(request, 'You do not have permission to process grants.')
        return redirect('grants:grants_dashboard')

    grants = SBGrant.objects.all().order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        grants = grants.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        grants = grants.filter(
            Q(business_group__name__icontains=search_query) |
            Q(business_group__business_type__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(grants, 10)
    page_number = request.GET.get('page')
    grants = paginator.get_page(page_number)

    context = {
        'page_title': 'SB Grant Applications',
        'grants': grants,
        'status_choices': SBGrant.GRANT_STATUS_CHOICES,
        'search_query': search_query,
        'selected_status': status_filter,
    }
    return render(request, 'grants/sb_grants.html', context)

@login_required
def pr_grant_applications(request):
    """View and process PR grant applications"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'county_executive', 'field_associate']):
        messages.error(request, 'You do not have permission to process grants.')
        return redirect('grants:grants_dashboard')

    grants = PRGrant.objects.all().order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        grants = grants.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        grants = grants.filter(
            Q(business_group__name__icontains=search_query) |
            Q(business_group__business_type__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(grants, 10)
    page_number = request.GET.get('page')
    grants = paginator.get_page(page_number)

    context = {
        'page_title': 'PR Grant Applications',
        'grants': grants,
        'status_choices': PRGrant.GRANT_STATUS_CHOICES,
        'search_query': search_query,
        'selected_status': status_filter,
    }
    return render(request, 'grants/pr_grants.html', context)

@login_required
def grant_detail(request, grant_type, grant_id):
    """View grant application details"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'county_executive', 'field_associate']):
        messages.error(request, 'You do not have permission to view grant details.')
        return redirect('grants:grants_dashboard')

    if grant_type == 'sb':
        grant = get_object_or_404(SBGrant, id=grant_id)
        template = 'grants/sb_grant_detail.html'
    else:
        grant = get_object_or_404(PRGrant, id=grant_id)
        template = 'grants/pr_grant_detail.html'

    context = {
        'page_title': f'{grant_type.upper()} Grant Application',
        'grant': grant,
        'grant_type': grant_type,
    }
    return render(request, template, context)

@login_required
def process_grant(request, grant_type, grant_id):
    """Process grant application (approve/reject)"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'county_executive', 'field_associate']):
        messages.error(request, 'You do not have permission to process grants.')
        return redirect('grants:grants_dashboard')

    if grant_type == 'sb':
        grant = get_object_or_404(SBGrant, id=grant_id)
    else:
        grant = get_object_or_404(PRGrant, id=grant_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        if action == 'approve':
            grant.status = 'funded'
            grant.disbursement_date = timezone.now().date()
            messages.success(request, f'{grant_type.upper()} Grant approved successfully!')
        elif action == 'reject':
            grant.status = 'rejected'
            grant.processed_by = request.user
            grant.notes = notes
            messages.info(request, f'{grant_type.upper()} Grant rejected.')
        elif action == 'review':
            grant.status = 'approved'
            grant.notes = notes
            messages.info(request, f'{grant_type.upper()} Grant moved to review.')

        grant.save()
        return redirect('grants:grant_detail', grant_type=grant_type, grant_id=grant_id)

    return redirect('grants:grant_detail', grant_type=grant_type, grant_id=grant_id)
```

---


## File: households\__init__.py

**Location:** `households\__init__.py`

```python
# Households App
```

---


## File: households\admin.py

**Location:** `households\admin.py`

```python
from django.contrib import admin
from .models import Household, HouseholdMember, PPI, HouseholdSurvey, HouseholdProgram

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'village', 'national_id', 'phone_number', 'created_at')
    list_filter = ('village', 'disability', 'created_at')
    search_fields = ('name', 'national_id', 'phone_number')

@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'household', 'gender', 'age', 'relationship_to_head')
    list_filter = ('gender', 'relationship_to_head', 'is_program_participant')

@admin.register(PPI)
class PPIAdmin(admin.ModelAdmin):
    list_display = ('household', 'name', 'eligibility_score', 'assessment_date')
    list_filter = ('assessment_date',)

@admin.register(HouseholdProgram)
class HouseholdProgramAdmin(admin.ModelAdmin):
    list_display = ('household', 'program', 'participation_status', 'mentor')
    list_filter = ('participation_status', 'program')
```

---


## File: households\apps.py

**Location:** `households\apps.py`

```python
from django.apps import AppConfig

class HouseholdsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'households'
```

---


## File: households\eligibility.py

**Location:** `households\eligibility.py`

```python
"""
Enhanced Household Eligibility and Scoring System
Implements sophisticated scoring algorithms for household qualification
"""

from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EligibilityScorer:
    """
    Advanced eligibility scoring system for household qualification
    """

    # Scoring weights for different criteria
    SCORING_WEIGHTS = {
        'poverty_index': 0.30,      # 30% - PPI score
        'income_level': 0.25,       # 25% - Income assessment
        'asset_ownership': 0.15,    # 15% - Asset evaluation
        'social_factors': 0.15,     # 15% - Social vulnerability
        'geographic': 0.10,         # 10% - Geographic factors
        'demographic': 0.05,        # 5% - Age, family size, etc.
    }

    # Scoring thresholds
    ELIGIBILITY_THRESHOLDS = {
        'highly_eligible': 80,      # 80+ score
        'eligible': 60,             # 60-79 score
        'marginally_eligible': 40,  # 40-59 score
        'not_eligible': 0,          # Below 40
    }

    def __init__(self, household):
        self.household = household
        self.scores = {}
        self.total_score = 0
        self.eligibility_level = 'not_eligible'

    def calculate_comprehensive_score(self):
        """Calculate comprehensive eligibility score"""
        self.scores = {
            'poverty_index': self._score_poverty_index(),
            'income_level': self._score_income_level(),
            'asset_ownership': self._score_asset_ownership(),
            'social_factors': self._score_social_factors(),
            'geographic': self._score_geographic_factors(),
            'demographic': self._score_demographic_factors(),
        }

        # Calculate weighted total score
        self.total_score = sum(
            score * self.SCORING_WEIGHTS[category]
            for category, score in self.scores.items()
        )

        # Determine eligibility level
        if self.total_score >= self.ELIGIBILITY_THRESHOLDS['highly_eligible']:
            self.eligibility_level = 'highly_eligible'
        elif self.total_score >= self.ELIGIBILITY_THRESHOLDS['eligible']:
            self.eligibility_level = 'eligible'
        elif self.total_score >= self.ELIGIBILITY_THRESHOLDS['marginally_eligible']:
            self.eligibility_level = 'marginally_eligible'
        else:
            self.eligibility_level = 'not_eligible'

        return {
            'total_score': round(self.total_score, 2),
            'eligibility_level': self.eligibility_level,
            'category_scores': self.scores,
            'recommendation': self._get_recommendation(),
            'improvement_areas': self._get_improvement_areas(),
        }

    def _score_poverty_index(self):
        """Score based on Poverty Probability Index (PPI)"""
        ppi_score = self.household.latest_ppi_score
        if ppi_score:

            # Convert PPI score to 0-100 scale (lower PPI = higher poverty = higher eligibility)
            if ppi_score <= 20:
                return 100  # Extremely poor - highest eligibility
            elif ppi_score <= 40:
                return 80   # Very poor
            elif ppi_score <= 60:
                return 60   # Moderately poor
            elif ppi_score <= 80:
                return 30   # Less poor
            else:
                return 10   # Least poor - lowest eligibility

        return 50  # Default score if PPI not available

    def _score_income_level(self):
        """Score based on household income"""
        monthly_income = getattr(self.household, 'monthly_income', 0) or 0

        # Kenya poverty line considerations (approximate figures)
        extreme_poverty_line = 2500   # KES per month
        poverty_line = 5000          # KES per month

        if monthly_income <= extreme_poverty_line:
            return 100  # Extreme poverty - highest eligibility
        elif monthly_income <= poverty_line:
            return 80   # Below poverty line
        elif monthly_income <= poverty_line * 1.5:
            return 60   # Vulnerable
        elif monthly_income <= poverty_line * 2:
            return 40   # Low income
        else:
            return 20   # Above target income level

    def _score_asset_ownership(self):
        """Score based on asset ownership"""
        assets = getattr(self.household, 'assets', {}) or {}

        # Define asset categories and weights
        basic_assets = ['bicycle', 'radio', 'mobile_phone']
        productive_assets = ['livestock', 'land', 'business_equipment']
        luxury_assets = ['car', 'motorcycle', 'television', 'refrigerator']

        basic_count = sum(1 for asset in basic_assets if assets.get(asset, False))
        productive_count = sum(1 for asset in productive_assets if assets.get(asset, False))
        luxury_count = sum(1 for asset in luxury_assets if assets.get(asset, False))

        # Calculate score (fewer assets = higher eligibility)
        if luxury_count > 2:
            return 10   # Too many luxury assets
        elif luxury_count > 0 or productive_count > 2:
            return 30   # Some valuable assets
        elif productive_count > 0 or basic_count > 2:
            return 60   # Few basic assets
        elif basic_count > 0:
            return 80   # Very few assets
        else:
            return 100  # No recorded assets - highest eligibility

    def _score_social_factors(self):
        """Score based on social vulnerability factors"""
        score = 50  # Base score

        # Female-headed household
        if getattr(self.household, 'head_gender', '') == 'female':
            score += 15

        # Elderly head of household
        head_age = getattr(self.household, 'head_age', 0)
        if head_age >= 65:
            score += 10
        elif head_age >= 55:
            score += 5

        # Presence of disabled members
        disabled_members = getattr(self.household, 'disabled_members_count', 0)
        if disabled_members > 0:
            score += 15

        # Single-parent household
        if getattr(self.household, 'is_single_parent', False):
            score += 10

        # Number of dependents
        total_members = getattr(self.household, 'total_members', 1)
        working_members = getattr(self.household, 'working_members_count', 1)
        dependency_ratio = (total_members - working_members) / max(working_members, 1)

        if dependency_ratio >= 3:
            score += 15
        elif dependency_ratio >= 2:
            score += 10
        elif dependency_ratio >= 1:
            score += 5

        return min(score, 100)  # Cap at 100

    def _score_geographic_factors(self):
        """Score based on geographic location and accessibility"""
        location = getattr(self.household, 'location', '') or ''
        village = getattr(self.household, 'village', None)

        score = 50  # Base score

        # Remote/rural areas get higher scores
        if any(keyword in location.lower() for keyword in ['remote', 'rural', 'isolated']):
            score += 20

        # Distance to markets, schools, health facilities
        if hasattr(village, 'distance_to_market'):
            market_distance = getattr(village, 'distance_to_market', 0)
            if market_distance > 20:  # km
                score += 15
            elif market_distance > 10:
                score += 10
            elif market_distance > 5:
                score += 5

        # Infrastructure access
        has_electricity = getattr(self.household, 'has_electricity', False)
        has_water_access = getattr(self.household, 'has_clean_water', False)

        if not has_electricity:
            score += 10
        if not has_water_access:
            score += 15

        return min(score, 100)

    def _score_demographic_factors(self):
        """Score based on demographic characteristics"""
        score = 50  # Base score

        # Household size
        total_members = getattr(self.household, 'total_members', 1)
        if total_members >= 8:
            score += 20  # Large households
        elif total_members >= 6:
            score += 15
        elif total_members >= 4:
            score += 10
        elif total_members <= 2:
            score -= 10  # Small households might be less vulnerable

        # Children under 5
        children_under_5 = getattr(self.household, 'children_under_5_count', 0)
        if children_under_5 >= 3:
            score += 15
        elif children_under_5 >= 2:
            score += 10
        elif children_under_5 >= 1:
            score += 5

        # Education level of head
        head_education = getattr(self.household, 'head_education_level', 'none')
        if head_education in ['none', 'primary_incomplete']:
            score += 15
        elif head_education == 'primary_complete':
            score += 10
        elif head_education == 'secondary_incomplete':
            score += 5

        return min(max(score, 0), 100)

    def _get_recommendation(self):
        """Get recommendation based on eligibility level"""
        recommendations = {
            'highly_eligible': "Highly recommended for immediate enrollment. This household meets all criteria for ultra-poor graduation program.",
            'eligible': "Recommended for enrollment. This household would benefit significantly from the UPG program.",
            'marginally_eligible': "Consider for enrollment based on program capacity. May need additional assessment of specific vulnerabilities.",
            'not_eligible': "Not recommended for ultra-poor graduation program. Consider referral to other appropriate programs.",
        }
        return recommendations.get(self.eligibility_level, "Unable to determine recommendation.")

    def _get_improvement_areas(self):
        """Identify areas where household could improve eligibility"""
        areas = []

        for category, score in self.scores.items():
            if score < 60:  # Low scoring areas
                if category == 'poverty_index':
                    areas.append("Consider updated PPI assessment")
                elif category == 'income_level':
                    areas.append("Income documentation may need verification")
                elif category == 'asset_ownership':
                    areas.append("Asset assessment may need review")
                elif category == 'social_factors':
                    areas.append("Social vulnerability factors need assessment")
                elif category == 'geographic':
                    areas.append("Geographic accessibility factors")
                elif category == 'demographic':
                    areas.append("Demographic characteristics assessment")

        return areas

    def is_eligible_for_program(self, program_type='graduation'):
        """Check if household is eligible for specific program type"""
        result = self.calculate_comprehensive_score()

        if program_type == 'graduation':
            # Ultra-poor graduation program
            return result['eligibility_level'] in ['highly_eligible', 'eligible']
        elif program_type == 'general':
            # General poverty alleviation programs
            return result['eligibility_level'] != 'not_eligible'

        return False


class HouseholdQualificationTool:
    """
    Tool for qualifying households with detailed assessment
    """

    def __init__(self, household):
        self.household = household
        self.scorer = EligibilityScorer(household)

    def run_qualification_assessment(self):
        """Run comprehensive qualification assessment"""
        # Get eligibility score
        eligibility_result = self.scorer.calculate_comprehensive_score()

        # Additional qualification checks
        qualification_checks = {
            'geographic_eligibility': self._check_geographic_eligibility(),
            'program_capacity': self._check_program_capacity(),
            'previous_participation': self._check_previous_participation(),
            'consent_and_commitment': self._check_consent_commitment(),
        }

        # Final qualification decision
        final_qualification = self._make_final_decision(
            eligibility_result, qualification_checks
        )

        return {
            'eligibility_assessment': eligibility_result,
            'qualification_checks': qualification_checks,
            'final_qualification': final_qualification,
            'next_steps': self._get_next_steps(final_qualification),
            'assessment_date': timezone.now(),
        }

    def _check_geographic_eligibility(self):
        """Check if household is in program target area"""
        village = getattr(self.household, 'village', None)
        if village and hasattr(village, 'is_program_area'):
            return getattr(village, 'is_program_area', False)
        return True  # Default to true if not specified

    def _check_program_capacity(self):
        """Check if there's capacity in local program"""
        # This would check against active programs and enrollment caps
        return True  # Simplified for now

    def _check_previous_participation(self):
        """Check if household has participated in similar programs"""
        # Check for previous program participation
        return True  # Simplified - would check program history

    def _check_consent_commitment(self):
        """Check household consent and commitment to participate"""
        # This would involve consent forms and commitment assessments
        return getattr(self.household, 'consent_given', False)

    def _make_final_decision(self, eligibility_result, qualification_checks):
        """Make final qualification decision"""
        # Must be eligible and pass all qualification checks
        is_eligible = eligibility_result['eligibility_level'] in ['highly_eligible', 'eligible']
        all_checks_pass = all(qualification_checks.values())

        if is_eligible and all_checks_pass:
            return {
                'qualified': True,
                'qualification_level': eligibility_result['eligibility_level'],
                'priority_score': eligibility_result['total_score'],
                'status': 'qualified',
            }
        elif is_eligible:
            return {
                'qualified': False,
                'qualification_level': 'conditional',
                'priority_score': eligibility_result['total_score'],
                'status': 'needs_review',
                'blocking_factors': [
                    check for check, passed in qualification_checks.items() if not passed
                ],
            }
        else:
            return {
                'qualified': False,
                'qualification_level': 'not_qualified',
                'priority_score': eligibility_result['total_score'],
                'status': 'not_qualified',
            }

    def _get_next_steps(self, final_qualification):
        """Get recommended next steps based on qualification result"""
        if final_qualification['qualified']:
            return [
                "Proceed with program enrollment",
                "Complete household registration",
                "Assign to mentor",
                "Schedule initial training sessions",
            ]
        elif final_qualification['status'] == 'needs_review':
            return [
                "Address blocking factors",
                "Complete additional assessments",
                "Obtain required documentation",
                "Resubmit for qualification review",
            ]
        else:
            return [
                "Refer to alternative programs",
                "Provide resource information",
                "Consider re-assessment in future",
            ]


# Utility functions for quick eligibility checks
def quick_eligibility_check(household):
    """Quick eligibility check for screening purposes"""
    scorer = EligibilityScorer(household)
    result = scorer.calculate_comprehensive_score()
    return result['eligibility_level'] in ['highly_eligible', 'eligible']


def batch_eligibility_assessment(households):
    """Assess eligibility for multiple households"""
    results = []
    for household in households:
        scorer = EligibilityScorer(household)
        result = scorer.calculate_comprehensive_score()
        results.append({
            'household_id': household.id,
            'household_name': household.name,
            'total_score': result['total_score'],
            'eligibility_level': result['eligibility_level'],
            'eligible': result['eligibility_level'] in ['highly_eligible', 'eligible'],
        })

    # Sort by score (highest first)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results
```

---


## File: households\graduation_views.py

**Location:** `households\graduation_views.py`

```python
"""
Graduation Tracking Views for UPG System
Comprehensive milestone and graduation management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from .models import Household, HouseholdProgram, UPGMilestone
from programs.models import Program


@login_required
def graduation_dashboard(request):
    """Comprehensive graduation tracking dashboard"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to access graduation tracking.')
        return redirect('dashboard:dashboard')

    # Filter for UPG programs only
    upg_programs = Program.objects.filter(program_type='graduation')

    # Get household programs for UPG programs
    household_programs = HouseholdProgram.objects.filter(
        program__program_type='graduation'
    ).select_related('household', 'program')

    # Apply role-based filtering
    if user_role == 'mentor':
        if hasattr(request.user, 'profile') and request.user.profile:
            assigned_villages = request.user.profile.assigned_villages.all()
            household_programs = household_programs.filter(household__village__in=assigned_villages)
    elif user_role == 'field_associate':
        if hasattr(request.user, 'profile') and request.user.profile:
            assigned_villages = request.user.profile.assigned_villages.all()
            household_programs = household_programs.filter(household__village__in=assigned_villages)

    # Graduation statistics
    total_participants = household_programs.count()

    # Calculate progress based on milestones
    milestones_stats = UPGMilestone.objects.filter(
        household_program__in=household_programs
    ).aggregate(
        total_milestones=Count('id'),
        completed_milestones=Count('id', filter=Q(status='completed')),
        overdue_milestones=Count('id', filter=Q(
            status__in=['not_started', 'in_progress'],
            target_date__lt=timezone.now().date()
        )),
        in_progress=Count('id', filter=Q(status='in_progress'))
    )

    # Calculate graduation progress
    households_by_progress = {}
    for hp in household_programs:
        completed_count = hp.milestones.filter(status='completed').count()
        progress_percentage = (completed_count / 12) * 100 if completed_count > 0 else 0

        if progress_percentage == 100:
            category = 'graduated'
        elif progress_percentage >= 75:
            category = 'near_graduation'
        elif progress_percentage >= 50:
            category = 'mid_program'
        elif progress_percentage >= 25:
            category = 'early_stage'
        else:
            category = 'just_started'

        households_by_progress.setdefault(category, 0)
        households_by_progress[category] += 1

    # Recent milestone updates
    recent_milestones = UPGMilestone.objects.filter(
        household_program__in=household_programs,
        updated_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('household_program__household').order_by('-updated_at')[:10]

    # Overdue milestones
    overdue_milestones = UPGMilestone.objects.filter(
        household_program__in=household_programs,
        status__in=['not_started', 'in_progress'],
        target_date__lt=timezone.now().date()
    ).select_related('household_program__household').order_by('target_date')[:10]

    # Monthly progress data for charts
    monthly_data = []
    for i in range(12):
        month_milestones = UPGMilestone.objects.filter(
            household_program__in=household_programs,
            milestone=f'month_{i+1}'
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            overdue=Count('id', filter=Q(
                status__in=['not_started', 'in_progress'],
                target_date__lt=timezone.now().date()
            ))
        )
        monthly_data.append({
            'month': i + 1,
            'total': month_milestones['total'],
            'completed': month_milestones['completed'],
            'in_progress': month_milestones['in_progress'],
            'overdue': month_milestones['overdue'],
            'completion_rate': (month_milestones['completed'] / month_milestones['total'] * 100) if month_milestones['total'] > 0 else 0
        })

    context = {
        'page_title': 'Graduation Tracking Dashboard',
        'total_participants': total_participants,
        'milestones_stats': milestones_stats,
        'households_by_progress': households_by_progress,
        'recent_milestones': recent_milestones,
        'overdue_milestones': overdue_milestones,
        'monthly_data': monthly_data,
        'upg_programs': upg_programs,
    }

    return render(request, 'households/graduation_dashboard.html', context)


@login_required
def household_milestones(request, household_id):
    """View and manage milestones for a specific household"""
    household = get_object_or_404(Household, id=household_id)

    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to view household milestones.')
        return redirect('households:household_detail', pk=household_id)

    # Get UPG program enrollment
    try:
        household_program = HouseholdProgram.objects.get(
            household=household,
            program__program_type='graduation'
        )
    except HouseholdProgram.DoesNotExist:
        messages.error(request, 'This household is not enrolled in a UPG program.')
        return redirect('households:household_detail', pk=household_id)

    # Get or create milestones
    milestones = []
    for milestone_choice in UPGMilestone.MILESTONE_CHOICES:
        milestone_key = milestone_choice[0]
        milestone_display = milestone_choice[1]

        milestone, created = UPGMilestone.objects.get_or_create(
            household_program=household_program,
            milestone=milestone_key,
            defaults={
                'status': 'not_started',
                'target_date': None,
            }
        )
        milestones.append(milestone)

    # Calculate progress
    completed_count = sum(1 for m in milestones if m.status == 'completed')
    progress_percentage = (completed_count / len(milestones)) * 100

    context = {
        'page_title': f'Graduation Milestones - {household.name}',
        'household': household,
        'household_program': household_program,
        'milestones': milestones,
        'completed_count': completed_count,
        'total_milestones': len(milestones),
        'progress_percentage': progress_percentage,
    }

    return render(request, 'households/household_milestones.html', context)


@login_required
def update_milestone(request, milestone_id):
    """Update milestone status and details"""
    milestone = get_object_or_404(UPGMilestone, id=milestone_id)

    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        target_date = request.POST.get('target_date')

        if status in dict(UPGMilestone.STATUS_CHOICES):
            milestone.status = status
            milestone.notes = notes
            milestone.completed_by = request.user if status == 'completed' else None

            if status == 'completed' and not milestone.completion_date:
                milestone.completion_date = timezone.now().date()
            elif status != 'completed':
                milestone.completion_date = None

            if target_date:
                try:
                    milestone.target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
                except ValueError:
                    pass

            milestone.save()

            return JsonResponse({
                'success': True,
                'message': f'Milestone updated successfully',
                'status': milestone.get_status_display(),
                'completion_date': milestone.completion_date.strftime('%Y-%m-%d') if milestone.completion_date else None
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid status'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def graduation_reports(request):
    """Generate graduation progress reports"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        messages.error(request, 'You do not have permission to access graduation reports.')
        return redirect('dashboard:dashboard')

    # Get UPG programs
    upg_programs = Program.objects.filter(program_type='graduation')

    # Detailed analytics
    program_analytics = []
    for program in upg_programs:
        household_programs = HouseholdProgram.objects.filter(program=program)
        total_households = household_programs.count()

        if total_households > 0:
            milestones = UPGMilestone.objects.filter(household_program__in=household_programs)

            analytics = {
                'program': program,
                'total_households': total_households,
                'total_milestones': milestones.count(),
                'completed_milestones': milestones.filter(status='completed').count(),
                'overdue_milestones': milestones.filter(
                    status__in=['not_started', 'in_progress'],
                    target_date__lt=timezone.now().date()
                ).count(),
                'graduation_rate': 0,
                'average_progress': 0,
            }

            # Calculate graduation rate and average progress
            graduated_count = 0
            total_progress = 0

            for hp in household_programs:
                completed = hp.milestones.filter(status='completed').count()
                progress = (completed / 12) * 100
                total_progress += progress

                if completed == 12:
                    graduated_count += 1

            analytics['graduation_rate'] = (graduated_count / total_households) * 100
            analytics['average_progress'] = total_progress / total_households
            analytics['remaining_milestones'] = analytics['total_milestones'] - analytics['completed_milestones'] - analytics['overdue_milestones']

            program_analytics.append(analytics)

    # Calculate overall statistics
    total_participants = sum(analytics['total_households'] for analytics in program_analytics)
    overall_graduation_rate = sum(analytics['graduation_rate'] for analytics in program_analytics) / len(program_analytics) if program_analytics else 0

    context = {
        'page_title': 'Graduation Reports',
        'program_analytics': program_analytics,
        'total_participants': total_participants,
        'overall_graduation_rate': overall_graduation_rate,
    }

    return render(request, 'households/graduation_reports.html', context)


@login_required
def export_graduation_reports(request):
    """Export graduation reports in Excel or CSV format"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        return HttpResponse('Permission denied', status=403)

    export_format = request.GET.get('format', 'excel')

    # Get UPG programs
    upg_programs = Program.objects.filter(program_type='graduation')

    # Prepare data
    data = []
    for program in upg_programs:
        household_programs = HouseholdProgram.objects.filter(program=program)
        total_households = household_programs.count()

        if total_households > 0:
            milestones = UPGMilestone.objects.filter(household_program__in=household_programs)

            # Calculate graduation rate
            graduated_count = 0
            for hp in household_programs:
                completed = hp.milestones.filter(status='completed').count()
                if completed == 12:
                    graduated_count += 1

            graduation_rate = (graduated_count / total_households) * 100

            data.append({
                'Program': program.name,
                'Total Households': total_households,
                'Total Milestones': milestones.count(),
                'Completed Milestones': milestones.filter(status='completed').count(),
                'Overdue Milestones': milestones.filter(
                    status__in=['not_started', 'in_progress'],
                    target_date__lt=timezone.now().date()
                ).count(),
                'Graduation Rate (%)': round(graduation_rate, 1),
                'Budget (KES)': program.budget,
                'Start Date': program.start_date.strftime('%Y-%m-%d') if program.start_date else '',
                'Duration (months)': program.duration_months,
            })

    if export_format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="graduation_reports_{timezone.now().strftime("%Y%m%d")}.xlsx"'

        # Note: For production, install openpyxl and implement Excel export
        # For now, return CSV format
        export_format = 'csv'

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="graduation_reports_{timezone.now().strftime("%Y%m%d")}.csv"'

        writer = csv.DictWriter(response, fieldnames=[
            'Program', 'Total Households', 'Total Milestones', 'Completed Milestones',
            'Overdue Milestones', 'Graduation Rate (%)', 'Budget (KES)', 'Start Date', 'Duration (months)'
        ])

        writer.writeheader()
        for row in data:
            writer.writerow(row)

        return response

    return HttpResponse('Invalid format', status=400)
```

---


## File: households\management\__init__.py

**Location:** `households\management\__init__.py`

```python

```

---


## File: households\management\commands\__init__.py

**Location:** `households\management\commands\__init__.py`

```python

```

---


## File: households\management\commands\create_sample_data.py

**Location:** `households\management\commands\create_sample_data.py`

```python
"""
Django management command to create sample household data for testing
Usage: python manage.py create_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, datetime, timedelta
import random

from core.models import Village, Program, Mentor
from households.models import (
    Household, HouseholdMember, HouseholdProgram, UPGMilestone,
    PPI, HouseholdSurvey
)
from training.models import (
    MentoringVisit, PhoneNudge, MentoringReport, Training, TrainingAttendance
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample household data for testing the UPG system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--households',
            type=int,
            default=50,
            help='Number of households to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        households_count = options['households']
        self.stdout.write(f'Creating {households_count} sample households...')

        # Create basic data first
        self.create_villages()
        self.create_programs()
        self.create_mentors()

        # Create households and related data
        self.create_households(households_count)
        self.create_household_programs()
        self.create_milestones()
        self.create_mentoring_activities()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {households_count} households with sample data!')
        )

    def clear_data(self):
        """Clear existing data"""
        MentoringVisit.objects.all().delete()
        PhoneNudge.objects.all().delete()
        MentoringReport.objects.all().delete()
        UPGMilestone.objects.all().delete()
        HouseholdProgram.objects.all().delete()
        HouseholdMember.objects.all().delete()
        HouseholdSurvey.objects.all().delete()
        PPI.objects.all().delete()
        Household.objects.all().delete()
        self.stdout.write('Existing data cleared.')

    def create_villages(self):
        """Create sample villages"""
        villages_data = [
            {'name': 'Kibera Central', 'subcounty': 'Kibra', 'saturation': 'High', 'qualified_hhs_per_village': 120},
            {'name': 'Mathare North', 'subcounty': 'Mathare', 'saturation': 'Medium', 'qualified_hhs_per_village': 85},
            {'name': 'Korogocho', 'subcounty': 'Kasarani', 'saturation': 'High', 'qualified_hhs_per_village': 95},
            {'name': 'Mukuru Kwa Njenga', 'subcounty': 'Embakasi East', 'saturation': 'Medium', 'qualified_hhs_per_village': 110},
            {'name': 'Kawangware', 'subcounty': 'Dagoretti North', 'saturation': 'Low', 'qualified_hhs_per_village': 70},
            {'name': 'Viwandani', 'subcounty': 'Embakasi East', 'saturation': 'Medium', 'qualified_hhs_per_village': 80},
            {'name': 'Dandora Phase 2', 'subcounty': 'Embakasi North', 'saturation': 'High', 'qualified_hhs_per_village': 100},
            {'name': 'Huruma Estate', 'subcounty': 'Mathare', 'saturation': 'Low', 'qualified_hhs_per_village': 60},
        ]

        for village_data in villages_data:
            village, created = Village.objects.get_or_create(
                name=village_data['name'],
                defaults=village_data
            )
            if created:
                self.stdout.write(f'Created village: {village.name}')

    def create_programs(self):
        """Create sample UPG programs"""
        programs_data = [
            {
                'name': 'UPG Nairobi FY25 Cycle 1',
                'cycle': 'FY25C1',
                'office': 'Nairobi',
                'start_date': date(2024, 10, 1),
                'end_date': date(2025, 9, 30),
                'status': 'active',
                'target_households': 200,
                'target_villages': 5,
            },
            {
                'name': 'UPG Nairobi FY24 Cycle 2',
                'cycle': 'FY24C2',
                'office': 'Nairobi',
                'start_date': date(2024, 4, 1),
                'end_date': date(2025, 3, 31),
                'status': 'active',
                'target_households': 150,
                'target_villages': 4,
            }
        ]

        for program_data in programs_data:
            program, created = Program.objects.get_or_create(
                name=program_data['name'],
                defaults=program_data
            )
            if created:
                self.stdout.write(f'Created program: {program.name}')

    def create_mentors(self):
        """Create sample mentor users and mentor profiles"""
        mentors_data = [
            {'username': 'mentor1', 'first_name': 'Grace', 'last_name': 'Wanjiku', 'email': 'grace.wanjiku@upg.org'},
            {'username': 'mentor2', 'first_name': 'John', 'last_name': 'Kiprotich', 'email': 'john.kiprotich@upg.org'},
            {'username': 'mentor3', 'first_name': 'Mary', 'last_name': 'Achieng', 'email': 'mary.achieng@upg.org'},
            {'username': 'mentor4', 'first_name': 'David', 'last_name': 'Mwangi', 'email': 'david.mwangi@upg.org'},
        ]

        for mentor_data in mentors_data:
            user, created = User.objects.get_or_create(
                username=mentor_data['username'],
                defaults={
                    'first_name': mentor_data['first_name'],
                    'last_name': mentor_data['last_name'],
                    'email': mentor_data['email'],
                    'role': 'mentor',
                    'is_staff': False,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created mentor user: {user.get_full_name()}')

            # Create Mentor profile
            mentor_profile, created = Mentor.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': mentor_data['first_name'],
                    'last_name': mentor_data['last_name'],
                    'office': 'Nairobi',
                }
            )
            if created:
                self.stdout.write(f'Created mentor profile: {mentor_profile}')

    def create_households(self, count):
        """Create sample households"""
        villages = list(Village.objects.all())

        # Kenyan names for realistic data
        first_names = [
            'Grace', 'Mary', 'Jane', 'Rose', 'Lucy', 'Ann', 'Catherine', 'Margaret', 'Susan', 'Joyce',
            'John', 'Peter', 'James', 'David', 'Joseph', 'Michael', 'Daniel', 'Paul', 'Samuel', 'Francis',
            'Faith', 'Hope', 'Mercy', 'Esther', 'Ruth', 'Naomi', 'Rachel', 'Sarah', 'Rebecca', 'Hannah'
        ]

        last_names = [
            'Wanjiku', 'Mwangi', 'Kamau', 'Njeri', 'Kiprotich', 'Achieng', 'Otieno', 'Wanjira',
            'Kariuki', 'Njoroge', 'Mutua', 'Kimani', 'Ochieng', 'Gitau', 'Waithaka', 'Kihara',
            'Macharia', 'Mbugua', 'Waweru', 'Gathoni', 'Muthoni', 'Nyambura', 'Wangari', 'Njambi'
        ]

        for i in range(count):
            village = random.choice(villages)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            household = Household.objects.create(
                village=village,
                name=f'{first_name} {last_name}',
                national_id=f'{random.randint(20000000, 40000000)}',
                phone_number=f'+254{random.randint(700000000, 799999999)}',
                disability=random.choice([True, False]) if random.random() < 0.15 else False,
                gps_latitude=-1.2921 + random.uniform(-0.1, 0.1),  # Around Nairobi
                gps_longitude=36.8219 + random.uniform(-0.1, 0.1),
            )

            # Create household members
            self.create_household_members(household, first_name, last_name)

            # Create PPI scores
            self.create_ppi_scores(household)

            # Create surveys
            self.create_household_surveys(household)

    def create_household_members(self, household, head_first_name, head_last_name):
        """Create household members"""
        # Create household head
        HouseholdMember.objects.create(
            household=household,
            name=f'{head_first_name} {head_last_name}',
            gender=random.choice(['male', 'female']),
            age=random.randint(25, 55),
            relationship_to_head='head',
            education_level=random.choice(['none', 'primary', 'secondary']),
            is_program_participant=True,
        )

        # Create spouse (sometimes)
        if random.random() < 0.7:
            spouse_names = ['Margaret', 'Grace', 'Peter', 'John', 'Mary', 'James']
            head_member = household.members.first()
            HouseholdMember.objects.create(
                household=household,
                name=f'{random.choice(spouse_names)} {head_last_name}',
                gender='female' if head_member.gender == 'male' else 'male',
                age=random.randint(22, 50),
                relationship_to_head='spouse',
                education_level=random.choice(['none', 'primary', 'secondary']),
                is_program_participant=False,
            )

        # Create children
        num_children = random.randint(1, 5)
        child_names = ['Faith', 'Hope', 'Joy', 'Blessing', 'Gift', 'Emmanuel', 'Joshua', 'Ruth', 'Daniel']

        for i in range(num_children):
            HouseholdMember.objects.create(
                household=household,
                name=f'{random.choice(child_names)} {head_last_name}',
                gender=random.choice(['male', 'female']),
                age=random.randint(1, 18),
                relationship_to_head='child',
                education_level='none' if random.randint(1, 18) < 6 else random.choice(['primary', 'secondary']),
                is_program_participant=False,
            )

    def create_ppi_scores(self, household):
        """Create PPI scores for household"""
        # Baseline PPI
        PPI.objects.create(
            household=household,
            name='Baseline PPI',
            eligibility_score=random.randint(15, 45),  # Poor households
            assessment_date=date.today() - timedelta(days=random.randint(30, 365)),
        )

        # Some households might have midline/endline PPI
        if random.random() < 0.3:
            PPI.objects.create(
                household=household,
                name='Midline PPI',
                eligibility_score=random.randint(20, 55),  # Slight improvement
                assessment_date=date.today() - timedelta(days=random.randint(1, 180)),
            )

    def create_household_surveys(self, household):
        """Create household surveys"""
        HouseholdSurvey.objects.create(
            household=household,
            survey_type='baseline',
            name='Baseline Household Survey',
            survey_date=date.today() - timedelta(days=random.randint(30, 365)),
            income_level=random.choice(['Very Low', 'Low', 'Below Average']),
            assets_owned='Basic furniture, cooking utensils, radio',
            savings_amount=random.randint(0, 5000),
        )

    def create_household_programs(self):
        """Enroll households in UPG programs"""
        programs = list(Program.objects.all())  # All programs are graduation programs in this system
        households = list(Household.objects.all())
        mentors = list(Mentor.objects.all())

        for household in households:
            if random.random() < 0.8:  # 80% enrollment rate
                program = random.choice(programs)
                mentor = random.choice(mentors) if mentors else None

                enrollment_date = program.start_date + timedelta(days=random.randint(0, 60))

                HouseholdProgram.objects.create(
                    household=household,
                    program=program,
                    mentor=mentor,
                    participation_status=random.choice(['enrolled', 'active', 'graduated']),
                    enrollment_date=enrollment_date,
                )

    def create_milestones(self):
        """Create UPG milestones for enrolled households"""
        household_programs = HouseholdProgram.objects.all()

        for hp in household_programs:
            months_since_enrollment = (date.today() - hp.enrollment_date).days // 30

            # Create milestones based on how long they've been enrolled
            for i, (milestone_key, milestone_name) in enumerate(UPGMilestone.MILESTONE_CHOICES):
                if i < months_since_enrollment:
                    # Past milestones - mostly completed
                    status = random.choices(
                        ['completed', 'completed', 'completed', 'delayed', 'skipped'],
                        weights=[70, 15, 10, 4, 1]
                    )[0]

                    target_date = hp.enrollment_date + timedelta(days=30 * (i + 1))
                    completion_date = target_date + timedelta(days=random.randint(-5, 15)) if status == 'completed' else None

                elif i == months_since_enrollment:
                    # Current milestone - in progress
                    status = random.choice(['in_progress', 'not_started'])
                    target_date = hp.enrollment_date + timedelta(days=30 * (i + 1))
                    completion_date = None
                else:
                    # Future milestones - not started
                    status = 'not_started'
                    target_date = hp.enrollment_date + timedelta(days=30 * (i + 1))
                    completion_date = None

                UPGMilestone.objects.create(
                    household_program=hp,
                    milestone=milestone_key,
                    status=status,
                    target_date=target_date,
                    completion_date=completion_date,
                    notes=f'Sample milestone progress for {milestone_name}' if status == 'completed' else '',
                )

    def create_mentoring_activities(self):
        """Create sample mentoring visits and phone nudges"""
        household_programs = HouseholdProgram.objects.filter(mentor__isnull=False)

        for hp in household_programs:
            mentor_user = hp.mentor.user
            household = hp.household

            # Create visits (1-3 per month since enrollment)
            months_enrolled = (date.today() - hp.enrollment_date).days // 30
            num_visits = random.randint(months_enrolled, months_enrolled * 3)

            for i in range(num_visits):
                visit_date = hp.enrollment_date + timedelta(days=random.randint(0, (date.today() - hp.enrollment_date).days))

                MentoringVisit.objects.create(
                    name=f'{random.choice(["Weekly Check-in", "Business Planning", "Problem Solving", "Training Follow-up"])} - {household.name}',
                    household=household,
                    mentor=mentor_user,
                    topic=random.choice([
                        'Business planning and strategy',
                        'Financial management training',
                        'Savings group participation',
                        'Market linkage support',
                        'Problem-solving session',
                        'Skills development',
                        'Health and nutrition education'
                    ]),
                    visit_type=random.choice(['on_site', 'phone', 'virtual']),
                    visit_date=visit_date,
                    notes=f'Regular mentoring visit. Discussed progress and provided guidance on business development.',
                )

            # Create phone nudges (2-5 per month)
            num_nudges = random.randint(months_enrolled * 2, months_enrolled * 5)

            for i in range(num_nudges):
                call_date = timezone.now() - timedelta(days=random.randint(0, (date.today() - hp.enrollment_date).days))

                PhoneNudge.objects.create(
                    household=household,
                    mentor=mentor_user,
                    nudge_type=random.choice(['reminder', 'follow_up', 'support', 'check_in', 'business_advice']),
                    call_date=call_date,
                    duration_minutes=random.randint(5, 30),
                    notes=f'Regular check-in call to provide support and guidance.',
                    successful_contact=random.choice([True, True, True, False]),  # 75% success rate
                )

        # Create some mentoring reports
        mentors = User.objects.filter(role='mentor')
        for mentor in mentors:
            # Create a recent monthly report
            if random.random() < 0.7:  # 70% chance
                period_start = date.today().replace(day=1) - timedelta(days=30)
                period_end = date.today().replace(day=1) - timedelta(days=1)

                # Count actual activities for the period
                visits_count = MentoringVisit.objects.filter(
                    mentor=mentor,
                    visit_date__gte=period_start,
                    visit_date__lte=period_end
                ).count()

                nudges_count = PhoneNudge.objects.filter(
                    mentor=mentor,
                    call_date__gte=period_start,
                    call_date__lte=period_end
                ).count()

                households_visited = MentoringVisit.objects.filter(
                    mentor=mentor,
                    visit_date__gte=period_start,
                    visit_date__lte=period_end
                ).values('household').distinct().count()

                MentoringReport.objects.create(
                    mentor=mentor,
                    reporting_period='monthly',
                    period_start=period_start,
                    period_end=period_end,
                    households_visited=households_visited,
                    phone_nudges_made=nudges_count,
                    trainings_conducted=random.randint(1, 3),
                    new_households_enrolled=random.randint(0, 2),
                    key_activities=f'Conducted {visits_count} household visits focusing on business development and financial literacy. Provided ongoing support through phone check-ins and problem-solving sessions.',
                    challenges_faced='Some households faced challenges with market access due to transportation costs. Weather conditions affected some planned visits.',
                    successes_achieved='Three households successfully launched their businesses. Improved savings habits observed across most households.',
                    next_period_plans='Focus on market linkage activities and group formation for collective bargaining power.',
                )

        self.stdout.write(f'Created mentoring activities for {household_programs.count()} household-mentor pairs')
```

---


## File: households\models.py

**Location:** `households\models.py`

```python
"""
Household Management Models
Based on Graduation Model Tracking System
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.models import Village, Program, SubCounty, County

User = get_user_model()


class Household(models.Model):
    """
    Household basic information and demographics
    """
    # Geographic/Administrative Information
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.SET_NULL, null=True, blank=True, related_name='households')
    constituency = models.CharField(max_length=100, blank=True, help_text="Constituency")
    district = models.CharField(max_length=100, blank=True, help_text="District")
    division = models.CharField(max_length=100, blank=True, help_text="Division")
    location_name = models.CharField(max_length=100, blank=True, help_text="Location")
    sub_location = models.CharField(max_length=100, blank=True, help_text="Sub Location")

    # Household Head Information
    head_first_name = models.CharField(max_length=100, blank=True, help_text="First Name of Household Head")
    head_middle_name = models.CharField(max_length=100, blank=True, help_text="Middle Name of Household Head")
    head_last_name = models.CharField(max_length=100, blank=True, help_text="Last Name of Household Head")
    head_gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    head_date_of_birth = models.DateField(null=True, blank=True, help_text="Date of Birth of Household Head")
    head_id_number = models.CharField(max_length=50, blank=True, help_text="ID Number of Household Head")
    head_phone_number = models.CharField(max_length=15, blank=True, help_text="Phone Number of Household Head")

    # Legacy fields (kept for backward compatibility)
    name = models.CharField(max_length=100, help_text="Household name or identifier")
    national_id = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    disability = models.BooleanField(default=False)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Additional eligibility fields
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Monthly household income in KES")
    assets = models.JSONField(default=dict, blank=True, help_text="Household assets as JSON")
    has_electricity = models.BooleanField(default=False, help_text="Household has electricity access")
    has_clean_water = models.BooleanField(default=False, help_text="Household has clean water access")
    location = models.CharField(max_length=200, blank=True, help_text="Location description (rural, urban, remote)")
    consent_given = models.BooleanField(default=False, help_text="Household consent for program participation")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.head_full_name:
            return f"{self.head_full_name} - {self.village}"
        return f"{self.name} - {self.village}"

    @property
    def head_full_name(self):
        """Get full name of household head"""
        parts = [self.head_first_name, self.head_middle_name, self.head_last_name]
        return ' '.join([p for p in parts if p])

    def run_eligibility_assessment(self):
        """Run comprehensive eligibility assessment using EligibilityScorer"""
        from .eligibility import EligibilityScorer
        scorer = EligibilityScorer(self)
        return scorer.calculate_comprehensive_score()

    def run_qualification_assessment(self):
        """Run full qualification assessment using HouseholdQualificationTool"""
        from .eligibility import HouseholdQualificationTool
        tool = HouseholdQualificationTool(self)
        return tool.run_qualification_assessment()

    def is_eligible_for_upg(self):
        """Quick check if household is eligible for UPG program"""
        from .eligibility import quick_eligibility_check
        return quick_eligibility_check(self)

    @property
    def latest_ppi_score(self):
        """Get the most recent PPI score"""
        latest_ppi = self.ppi_scores.order_by('-assessment_date').first()
        return latest_ppi.eligibility_score if latest_ppi else None

    @property
    def head_member(self):
        """Get the household head"""
        return self.members.filter(relationship_to_head='head').first()

    @property
    def total_members(self):
        """Get total number of household members"""
        return self.members.count()

    @property
    def children_under_5_count(self):
        """Count children under 5 years old"""
        return self.members.filter(age__lt=5).count()

    @property
    def working_members_count(self):
        """Count working-age members (16-64)"""
        return self.members.filter(age__gte=16, age__lte=64).count()

    @property
    def disabled_members_count(self):
        """Count disabled household members"""
        return 1 if self.disability else 0

    @property
    def head_gender(self):
        """Get gender of household head"""
        head = self.head_member
        return head.gender if head else ''

    @property
    def head_age(self):
        """Get age of household head"""
        head = self.head_member
        return head.age if head else 0

    @property
    def head_education_level(self):
        """Get education level of household head"""
        head = self.head_member
        return head.education_level if head else 'none'

    @property
    def is_single_parent(self):
        """Check if this is a single parent household"""
        head = self.head_member
        if not head:
            return False
        spouses = self.members.filter(relationship_to_head='spouse').count()
        children = self.members.filter(relationship_to_head='child').count()
        return children > 0 and spouses == 0

    class Meta:
        db_table = 'upg_households'


class PPI(models.Model):
    """
    Poverty Probability Index for household
    """
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='ppi_scores')
    name = models.CharField(max_length=100, blank=True)  # e.g., Baseline PPI, Endline PPI
    eligibility_score = models.IntegerField()  # 0-100
    assessment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.name} - {self.eligibility_score}"

    class Meta:
        db_table = 'upg_ppi'


class HouseholdSurvey(models.Model):
    """
    Household living conditions and assets survey
    """
    SURVEY_TYPE_CHOICES = [
        ('baseline', 'Baseline'),
        ('midline', 'Midline'),
        ('endline', 'Endline'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='surveys')
    survey_type = models.CharField(max_length=20, choices=SURVEY_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    survey_date = models.DateField()
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Survey data fields (simplified for demo)
    income_level = models.CharField(max_length=50, blank=True)
    assets_owned = models.TextField(blank=True)
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.survey_type} - {self.survey_date}"

    class Meta:
        db_table = 'upg_household_surveys'


class HouseholdMember(models.Model):
    """
    Individual household members
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    EDUCATION_CHOICES = [
        ('none', 'None'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('tertiary', 'Tertiary'),
    ]

    RELATIONSHIP_CHOICES = [
        ('head', 'Head'),
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, help_text="Full name (for backward compatibility)")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of Birth")
    age = models.IntegerField(help_text="Age in years")
    id_number = models.CharField(max_length=50, blank=True, help_text="National ID or Birth Certificate Number")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Phone Number")
    relationship_to_head = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='none')
    is_program_participant = models.BooleanField(default=False, help_text="Only household head can participate")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.household.name})"

    class Meta:
        db_table = 'upg_household_members'


class HouseholdProgram(models.Model):
    """
    Household participation in UPG programs
    """
    PARTICIPATION_STATUS_CHOICES = [
        ('eligible', 'Eligible'),
        ('enrolled', 'Enrolled'),
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('dropped_out', 'Dropped Out'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='program_participations')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    mentor = models.ForeignKey('core.Mentor', on_delete=models.SET_NULL, null=True, blank=True)
    participation_status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS_CHOICES, default='eligible')
    enrollment_date = models.DateField(null=True, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    dropout_date = models.DateField(null=True, blank=True)
    dropout_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.household.name} - {self.program.name}"

    class Meta:
        db_table = 'upg_household_programs'
        unique_together = ['household', 'program']


class UPGMilestone(models.Model):
    """
    UPG 12-month graduation milestones tracking
    Only applicable for graduation programs
    """
    MILESTONE_CHOICES = [
        ('month_1', 'Month 1 - PPI Assessment & Business Training Start'),
        ('month_2', 'Month 2 - Business Group Formation'),
        ('month_3', 'Month 3 - Business Plan Development'),
        ('month_4', 'Month 4 - SB Grant Application'),
        ('month_5', 'Month 5 - SB Grant Disbursement'),
        ('month_6', 'Month 6 - Business Operations Start'),
        ('month_7', 'Month 7 - Mid-term Assessment'),
        ('month_8', 'Month 8 - Business Savings Group Formation'),
        ('month_9', 'Month 9 - PR Grant Eligibility Assessment'),
        ('month_10', 'Month 10 - PR Grant Application'),
        ('month_11', 'Month 11 - Final Business Assessment'),
        ('month_12', 'Month 12 - Graduation Assessment'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('skipped', 'Skipped'),
    ]

    household_program = models.ForeignKey(HouseholdProgram, on_delete=models.CASCADE, related_name='milestones')
    milestone = models.CharField(max_length=20, choices=MILESTONE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    # Tracking
    target_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['household_program', 'milestone']
        ordering = ['milestone']

    def __str__(self):
        return f"{self.household_program.household.name} - {self.get_milestone_display()}"

    @property
    def is_overdue(self):
        """Check if milestone is overdue"""
        if self.target_date and self.status not in ['completed', 'skipped']:
            from django.utils import timezone
            return timezone.now().date() > self.target_date
        return False
```

---


## File: households\urls.py

**Location:** `households\urls.py`

```python
from django.urls import path
from . import views
from . import graduation_views

app_name = 'households'

urlpatterns = [
    path('', views.household_list, name='household_list'),
    path('create/', views.household_create, name='household_create'),
    path('<int:pk>/', views.household_detail, name='household_detail'),
    path('<int:pk>/edit/', views.household_edit, name='household_edit'),
    path('<int:pk>/delete/', views.household_delete, name='household_delete'),
    path('<int:household_pk>/members/add/', views.member_create, name='member_create'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Graduation tracking URLs
    path('graduation/', graduation_views.graduation_dashboard, name='graduation_dashboard'),
    path('<int:household_id>/milestones/', graduation_views.household_milestones, name='household_milestones'),
    path('milestone/<int:milestone_id>/update/', graduation_views.update_milestone, name='update_milestone'),
    path('graduation/reports/', graduation_views.graduation_reports, name='graduation_reports'),
    path('graduation/reports/export/', graduation_views.export_graduation_reports, name='export_graduation_reports'),

    # Eligibility assessment URLs
    path('<int:household_id>/eligibility/', views.run_eligibility_assessment, name='run_eligibility_assessment'),
    path('<int:household_id>/qualification/', views.run_qualification_assessment, name='run_qualification_assessment'),
    path('eligibility/batch-report/', views.batch_eligibility_report, name='batch_eligibility_report'),
    path('eligibility/dashboard/', views.eligibility_dashboard, name='eligibility_dashboard'),
    path('api/<int:household_id>/eligibility/', views.household_eligibility_api, name='household_eligibility_api'),
]
```

---


## File: households\views.py

**Location:** `households\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Household, HouseholdMember, HouseholdProgram, PPI, HouseholdSurvey
from .eligibility import EligibilityScorer, HouseholdQualificationTool, batch_eligibility_assessment
from core.models import Village
from core.decorators import role_required

@login_required
def household_list(request):
    """Household list view with role-based filtering"""
    user = request.user

    # Filter households based on user role and permissions
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        # Full access to all households
        households = Household.objects.all()
    elif user.role == 'mentor':
        # Mentors can only see households in their assigned villages
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            households = Household.objects.filter(village__in=assigned_villages)
        else:
            # No villages assigned, no households visible
            households = Household.objects.none()
    elif user.role == 'field_associate':
        # Field Associates see households in their area (same as mentors for now)
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            households = Household.objects.filter(village__in=assigned_villages)
        else:
            households = Household.objects.none()
    else:
        # Other roles have no access to households
        households = Household.objects.none()

    households = households.order_by('-created_at')

    context = {
        'households': households,
        'page_title': 'Households',
        'total_count': households.count(),
    }

    return render(request, 'households/household_list.html', context)

@login_required
def household_create(request):
    """Create new household with role-based village filtering"""
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        village_id = request.POST.get('village')
        subcounty_id = request.POST.get('subcounty')
        national_id = request.POST.get('national_id', '')
        disability = request.POST.get('disability') == 'on'

        # Validate village access for mentors
        if user.role == 'mentor' and village_id:
            if hasattr(user, 'profile') and user.profile:
                assigned_villages = user.profile.assigned_villages.values_list('id', flat=True)
                if int(village_id) not in assigned_villages:
                    messages.error(request, 'You can only create households in your assigned villages.')
                    village_id = None

        if name and village_id and subcounty_id:
            household = Household.objects.create(
                name=name,
                phone_number=phone_number or '',
                village_id=village_id,
                subcounty_id=subcounty_id,
                national_id=national_id,
                disability=disability
            )
            messages.success(request, f'Household "{household.name}" created successfully!')
            return redirect('households:household_detail', pk=household.pk)
        else:
            messages.error(request, 'Household name, sub-county, and village are required.')

    # Filter villages based on user role
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        # Full access to all villages
        villages = Village.objects.select_related('subcounty_obj').all()
        from core.models import SubCounty
        subcounties = SubCounty.objects.select_related('county').all()
    elif user.role in ['mentor', 'field_associate']:
        # Only assigned villages
        if hasattr(user, 'profile') and user.profile:
            villages = user.profile.assigned_villages.select_related('subcounty_obj').all()
            # Get subcounties for assigned villages
            from core.models import SubCounty
            subcounty_ids = villages.values_list('subcounty_obj_id', flat=True).distinct()
            subcounties = SubCounty.objects.filter(id__in=subcounty_ids).select_related('county')
        else:
            villages = Village.objects.none()
            subcounties = []
            messages.warning(request, 'You have no assigned villages. Please contact your administrator.')
    else:
        villages = Village.objects.none()
        subcounties = []
        messages.error(request, 'You do not have permission to create households.')

    context = {
        'villages': villages,
        'subcounties': subcounties,
        'page_title': 'Create Household',
    }
    return render(request, 'households/household_create.html', context)

@login_required
def household_detail(request, pk):
    """Household detail view"""
    household = get_object_or_404(Household, pk=pk)

    # Calculate program participant count
    program_participants_count = household.members.filter(is_program_participant=True).count()

    context = {
        'household': household,
        'program_participants_count': program_participants_count,
        'page_title': f'Household - {household.name}',
    }
    return render(request, 'households/household_detail.html', context)

@login_required
def household_edit(request, pk):
    """Edit household"""
    household = get_object_or_404(Household, pk=pk)

    if request.method == 'POST':
        household.name = request.POST.get('name', household.name)
        household.phone_number = request.POST.get('phone_number', household.phone_number)
        village_id = request.POST.get('village')
        subcounty_id = request.POST.get('subcounty')
        if village_id:
            household.village_id = village_id
        if subcounty_id:
            household.subcounty_id = subcounty_id
        household.national_id = request.POST.get('national_id', household.national_id)
        household.disability = request.POST.get('disability') == 'on'

        household.save()
        messages.success(request, f'Household "{household.name}" updated successfully!')
        return redirect('households:household_detail', pk=household.pk)

    villages = Village.objects.select_related('subcounty_obj').all()
    from core.models import SubCounty
    subcounties = SubCounty.objects.select_related('county').all()

    context = {
        'household': household,
        'villages': villages,
        'subcounties': subcounties,
        'page_title': f'Edit - {household.name}',
    }
    return render(request, 'households/household_edit.html', context)

@login_required
def household_delete(request, pk):
    """Delete household"""
    household = get_object_or_404(Household, pk=pk)

    if request.method == 'POST':
        household_name = household.name
        household.delete()
        messages.success(request, f'Household "{household_name}" deleted successfully!')
        return redirect('households:household_list')

    context = {
        'household': household,
        'page_title': f'Delete - {household.name}',
    }
    return render(request, 'households/household_delete.html', context)

@login_required
def member_create(request, household_pk):
    """Add member to household"""
    household = get_object_or_404(Household, pk=household_pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        relationship_to_head = request.POST.get('relationship_to_head')
        education_level = request.POST.get('education_level', 'none')
        is_program_participant = request.POST.get('is_program_participant') == 'on'

        if name and gender and age:
            member = HouseholdMember.objects.create(
                household=household,
                name=name,
                gender=gender,
                age=int(age),
                relationship_to_head=relationship_to_head,
                education_level=education_level,
                is_program_participant=is_program_participant
            )
            messages.success(request, f'Member "{member.name}" added to household successfully!')
            return redirect('households:household_detail', pk=household.pk)
        else:
            messages.error(request, 'Name, gender, and age are required.')

    context = {
        'household': household,
        'gender_choices': HouseholdMember.GENDER_CHOICES,
        'relationship_choices': HouseholdMember.RELATIONSHIP_CHOICES,
        'education_choices': HouseholdMember.EDUCATION_CHOICES,
        'page_title': f'Add Member to {household.name}',
    }
    return render(request, 'households/member_create.html', context)

@login_required
def member_edit(request, pk):
    """Edit household member"""
    member = get_object_or_404(HouseholdMember, pk=pk)
    household = member.household

    if request.method == 'POST':
        member.name = request.POST.get('name', member.name)
        member.gender = request.POST.get('gender', member.gender)
        member.age = request.POST.get('age', member.age)
        member.relationship_to_head = request.POST.get('relationship_to_head', member.relationship_to_head)
        member.education_level = request.POST.get('education_level', member.education_level)
        member.is_program_participant = request.POST.get('is_program_participant') == 'on'

        member.save()
        messages.success(request, f'Member "{member.name}" updated successfully!')
        return redirect('households:household_detail', pk=household.pk)

    context = {
        'member': member,
        'household': household,
        'gender_choices': HouseholdMember.GENDER_CHOICES,
        'relationship_choices': HouseholdMember.RELATIONSHIP_CHOICES,
        'education_choices': HouseholdMember.EDUCATION_CHOICES,
        'page_title': f'Edit Member - {member.name}',
    }
    return render(request, 'households/member_edit.html', context)

@login_required
def member_delete(request, pk):
    """Delete household member"""
    member = get_object_or_404(HouseholdMember, pk=pk)
    household = member.household

    if request.method == 'POST':
        member_name = member.name
        member.delete()
        messages.success(request, f'Member "{member_name}" removed from household!')
        return redirect('households:household_detail', pk=household.pk)

    context = {
        'member': member,
        'household': household,
        'page_title': f'Remove Member - {member.name}',
    }
    return render(request, 'households/member_delete.html', context)


@login_required
@role_required(['me_staff', 'field_associate'])
def run_eligibility_assessment(request, household_id):
    """Run comprehensive eligibility assessment for a household"""
    household = get_object_or_404(Household, id=household_id)

    if request.method == 'POST':
        try:
            # Run eligibility assessment
            eligibility_result = household.run_eligibility_assessment()

            messages.success(request, f"Eligibility assessment completed. Score: {eligibility_result['total_score']}")
            return JsonResponse({
                'success': True,
                'result': eligibility_result
            })
        except Exception as e:
            messages.error(request, f"Error running assessment: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return redirect('households:household_detail', pk=household_id)


@login_required
@role_required(['me_staff', 'field_associate'])
def run_qualification_assessment(request, household_id):
    """Run full qualification assessment for UPG program"""
    household = get_object_or_404(Household, id=household_id)

    if request.method == 'POST':
        try:
            # Run qualification assessment
            qualification_result = household.run_qualification_assessment()

            if qualification_result['final_qualification']['qualified']:
                messages.success(request, f"Household qualified for UPG program!")
            else:
                messages.warning(request, f"Household not qualified. Status: {qualification_result['final_qualification']['status']}")

            return JsonResponse({
                'success': True,
                'result': qualification_result
            })
        except Exception as e:
            messages.error(request, f"Error running qualification: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return redirect('households:household_detail', pk=household_id)


@login_required
@role_required(['me_staff'])
def batch_eligibility_report(request):
    """Generate batch eligibility report for multiple households"""
    if request.method == 'POST':
        # Get selected households or all households
        household_ids = request.POST.getlist('household_ids')

        if household_ids:
            households = Household.objects.filter(id__in=household_ids)
        else:
            # Process all households if none selected
            households = Household.objects.all()[:100]  # Limit to prevent timeout

        try:
            # Run batch assessment
            results = batch_eligibility_assessment(households)

            context = {
                'results': results,
                'total_households': len(results),
                'eligible_count': sum(1 for r in results if r['eligible']),
            }

            return render(request, 'households/batch_eligibility_report.html', context)

        except Exception as e:
            messages.error(request, f"Error generating report: {str(e)}")
            return redirect('households:household_list')

    # Show selection form
    households = Household.objects.all().select_related('village')
    return render(request, 'households/batch_eligibility_form.html', {'households': households})


@login_required
def household_eligibility_api(request, household_id):
    """API endpoint for household eligibility data"""
    household = get_object_or_404(Household, id=household_id)

    try:
        eligibility_result = household.run_eligibility_assessment()
        return JsonResponse({
            'success': True,
            'household_id': household.id,
            'household_name': household.name,
            'eligibility_data': eligibility_result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@role_required(['me_staff'])
def eligibility_dashboard(request):
    """Dashboard showing eligibility statistics and trends"""
    from django.db.models import Count, Avg

    # Get summary statistics
    total_households = Household.objects.count()

    # Get recent assessments (simplified - would cache this in production)
    recent_households = Household.objects.all()[:50]
    assessments = []

    for household in recent_households:
        try:
            result = household.run_eligibility_assessment()
            assessments.append({
                'household_id': household.id,
                'household_name': household.name,
                'score': result['total_score'],
                'level': result['eligibility_level'],
                'eligible': result['eligibility_level'] in ['highly_eligible', 'eligible']
            })
        except:
            continue

    # Calculate statistics
    eligible_count = sum(1 for a in assessments if a['eligible'])
    avg_score = sum(a['score'] for a in assessments) / len(assessments) if assessments else 0

    # Group by eligibility level
    level_counts = {}
    for assessment in assessments:
        level = assessment['level']
        level_counts[level] = level_counts.get(level, 0) + 1

    context = {
        'total_households': total_households,
        'assessed_households': len(assessments),
        'eligible_count': eligible_count,
        'eligibility_rate': (eligible_count / len(assessments) * 100) if assessments else 0,
        'average_score': round(avg_score, 2),
        'level_counts': level_counts,
        'recent_assessments': assessments[:20],
    }

    return render(request, 'households/eligibility_dashboard.html', context)
```

---


## File: manage.py

**Location:** `manage.py`

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

---


## File: programs\__init__.py

**Location:** `programs\__init__.py`

```python

```

---


## File: programs\admin.py

**Location:** `programs\admin.py`

```python
from django.contrib import admin
from .models import Program, ProgramApplication, ProgramBeneficiary

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type', 'status', 'created_by', 'target_beneficiaries', 'application_count', 'created_at']
    list_filter = ['status', 'program_type', 'county', 'is_accepting_applications', 'created_at']
    search_fields = ['name', 'description', 'county', 'sub_county']
    readonly_fields = ['created_at', 'updated_at', 'application_count', 'approved_applications']

    fieldsets = (
        ('Program Information', {
            'fields': ('name', 'description', 'program_type', 'status')
        }),
        ('Program Details', {
            'fields': ('budget', 'target_beneficiaries', 'duration_months')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'application_deadline')
        }),
        ('Location & Management', {
            'fields': ('created_by', 'county', 'sub_county')
        }),
        ('Requirements', {
            'fields': ('eligibility_criteria', 'application_requirements')
        }),
        ('Settings', {
            'fields': ('is_accepting_applications', 'requires_approval')
        }),
        ('Statistics', {
            'fields': ('application_count', 'approved_applications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProgramApplication)
class ProgramApplicationAdmin(admin.ModelAdmin):
    list_display = ['household', 'program', 'status', 'application_date', 'reviewed_by', 'approved_by']
    list_filter = ['status', 'application_date', 'review_date', 'approval_date', 'program__status']
    search_fields = ['household__household_head', 'program__name', 'motivation_letter']
    readonly_fields = ['created_at', 'updated_at', 'application_date']

    fieldsets = (
        ('Application Info', {
            'fields': ('program', 'household', 'status', 'application_date')
        }),
        ('Application Details', {
            'fields': ('motivation_letter', 'additional_notes')
        }),
        ('Review Process', {
            'fields': ('reviewed_by', 'review_date', 'review_notes')
        }),
        ('Approval Process', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProgramBeneficiary)
class ProgramBeneficiaryAdmin(admin.ModelAdmin):
    list_display = ['household', 'program', 'participation_status', 'enrollment_date', 'benefits_received']
    list_filter = ['participation_status', 'enrollment_date', 'graduation_date', 'program__status']
    search_fields = ['household__household_head', 'program__name']
    readonly_fields = ['created_at', 'updated_at']

```

---


## File: programs\apps.py

**Location:** `programs\apps.py`

```python
from django.apps import AppConfig


class ProgramsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'programs'

```

---


## File: programs\models.py

**Location:** `programs\models.py`

```python
from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
from households.models import Household

User = get_user_model()

class Program(BaseModel):
    """Independent Programs that can be created by County Executives"""

    PROGRAM_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PROGRAM_TYPE_CHOICES = [
        ('graduation', 'Ultra-Poor Graduation'),
        ('microfinance', 'Microfinance'),
        ('agricultural', 'Agricultural Support'),
        ('education', 'Education Support'),
        ('health', 'Health Initiative'),
        ('infrastructure', 'Infrastructure Development'),
        ('skills_training', 'Skills Training'),
        ('youth_empowerment', 'Youth Empowerment'),
        ('women_empowerment', 'Women Empowerment'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS_CHOICES, default='draft')

    # Program details
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    target_beneficiaries = models.PositiveIntegerField(default=0)
    duration_months = models.PositiveIntegerField(default=12)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateTimeField(null=True, blank=True)

    # Creator and management
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_programs')
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)

    # Eligibility criteria (stored as JSON or text)
    eligibility_criteria = models.TextField(blank=True, help_text="Eligibility requirements for this program")
    application_requirements = models.TextField(blank=True, help_text="Documents and requirements for application")

    # Flags
    is_accepting_applications = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def application_count(self):
        return self.applications.count()

    @property
    def approved_applications(self):
        return self.applications.filter(status='approved').count()

    @property
    def is_upg_program(self):
        """Check if this is an Ultra-Poor Graduation program"""
        return self.program_type == 'graduation'

    @property
    def requires_ppi_scoring(self):
        """Check if this program requires PPI scoring"""
        return self.is_upg_program

    @property
    def supports_business_groups(self):
        """Check if this program supports business group formation"""
        return self.is_upg_program

    @property
    def supports_savings_groups(self):
        """Check if this program supports savings group formation"""
        return self.is_upg_program

    @property
    def has_graduation_milestones(self):
        """Check if this program tracks graduation milestones"""
        return self.is_upg_program

    @property
    def supports_grants(self):
        """Check if this program supports SB/PR grants"""
        return self.is_upg_program

    @property
    def default_duration_months(self):
        """Get default duration based on program type"""
        if self.is_upg_program:
            return 12  # UPG is 12-month model
        return self.duration_months or 6  # Default for other programs


class ProgramApplication(BaseModel):
    """Applications from households/beneficiaries to programs"""

    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('withdrawn', 'Withdrawn'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='program_applications')

    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)

    # Application details
    motivation_letter = models.TextField(blank=True, help_text="Why the household wants to join this program")
    additional_notes = models.TextField(blank=True)

    # Review process
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Approval process
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_applications')
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-application_date']
        unique_together = ['program', 'household']  # One application per household per program

    def __str__(self):
        return f"{self.household.name} - {self.program.name} ({self.get_status_display()})"


class ProgramBeneficiary(BaseModel):
    """Track households that are active beneficiaries of a program"""

    PARTICIPATION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
        ('dropped_out', 'Dropped Out'),
        ('terminated', 'Terminated'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='beneficiaries')
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='independent_program_participations')

    participation_status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS_CHOICES, default='active')
    enrollment_date = models.DateField()
    graduation_date = models.DateField(null=True, blank=True)

    # Tracking
    progress_notes = models.TextField(blank=True)
    benefits_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['program', 'household']

    def __str__(self):
        return f"{self.household.name} in {self.program.name}"

```

---


## File: programs\tests.py

**Location:** `programs\tests.py`

```python
from django.test import TestCase

# Create your tests here.

```

---


## File: programs\urls.py

**Location:** `programs\urls.py`

```python
from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('create/', views.program_create, name='program_create'),
    path('<int:pk>/', views.program_detail, name='program_detail'),
    path('<int:pk>/edit/', views.program_edit, name='program_edit'),
    path('<int:pk>/delete/', views.program_delete, name='program_delete'),
    path('<int:pk>/toggle-status/', views.program_toggle_status, name='program_toggle_status'),
    path('<int:pk>/applications/', views.program_applications, name='program_applications'),
    path('<int:pk>/apply/', views.program_apply, name='program_apply'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
]
```

---


## File: programs\views.py

**Location:** `programs\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Program, ProgramApplication, ProgramBeneficiary
from households.models import Household

@login_required
def program_list(request):
    """List all programs"""
    programs = Program.objects.filter(status__in=['active', 'draft']).order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(county__icontains=search_query)
        )

    # Filter by program type
    program_type = request.GET.get('type')
    if program_type:
        programs = programs.filter(program_type=program_type)

    # Pagination
    paginator = Paginator(programs, 10)
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)

    context = {
        'programs': programs,
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'search_query': search_query,
        'selected_type': program_type,
        'page_title': 'Programs',
    }

    return render(request, 'programs/program_list.html', context)

@login_required
def program_create(request):
    """Create a new program (County Executives, ICT Admins, and Superusers)"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin']):
        messages.error(request, 'You do not have permission to create programs.')
        return redirect('programs:program_list')

    if request.method == 'POST':
        # Basic form processing - in production, use Django forms
        name = request.POST.get('name')
        description = request.POST.get('description')
        program_type = request.POST.get('program_type')
        budget = request.POST.get('budget') or None
        target_beneficiaries = request.POST.get('target_beneficiaries') or 0

        if name and description:
            program = Program.objects.create(
                name=name,
                description=description,
                program_type=program_type,
                budget=budget,
                target_beneficiaries=target_beneficiaries,
                created_by=request.user,
                county=getattr(request.user, 'county', ''),
                eligibility_criteria=request.POST.get('eligibility_criteria', ''),
                application_requirements=request.POST.get('application_requirements', ''),
            )
            messages.success(request, f'Program "{program.name}" created successfully!')
            return redirect('programs:program_detail', pk=program.pk)
        else:
            messages.error(request, 'Name and description are required.')

    context = {
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'page_title': 'Create New Program',
    }

    return render(request, 'programs/program_create.html', context)

@login_required
def program_detail(request, pk):
    """Program detail view"""
    program = get_object_or_404(Program, pk=pk)

    # Check if current user has already applied
    user_application = None
    if hasattr(request.user, 'household'):
        try:
            user_application = ProgramApplication.objects.get(
                program=program,
                household=request.user.household
            )
        except ProgramApplication.DoesNotExist:
            pass

    context = {
        'program': program,
        'user_application': user_application,
        'can_apply': program.is_accepting_applications and not user_application,
        'page_title': program.name,
    }

    return render(request, 'programs/program_detail.html', context)

@login_required
def program_applications(request, pk):
    """View applications for a program (Program creators, admins, and superusers)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to view applications.')
        return redirect('programs:program_detail', pk=program.pk)

    applications = program.applications.all().order_by('-application_date')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'program': program,
        'applications': applications,
        'status_choices': ProgramApplication.APPLICATION_STATUS_CHOICES,
        'selected_status': status_filter,
        'page_title': f'{program.name} - Applications',
    }

    return render(request, 'programs/program_applications.html', context)

@login_required
def program_apply(request, pk):
    """Apply to a program"""
    program = get_object_or_404(Program, pk=pk)

    if not program.is_accepting_applications:
        messages.error(request, 'This program is not accepting applications.')
        return redirect('programs:program_detail', pk=program.pk)

    # Get or create household for user
    try:
        household = request.user.household
    except:
        messages.error(request, 'You need to be associated with a household to apply.')
        return redirect('programs:program_detail', pk=program.pk)

    # Check if already applied
    if ProgramApplication.objects.filter(program=program, household=household).exists():
        messages.warning(request, 'You have already applied to this program.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        motivation_letter = request.POST.get('motivation_letter', '')
        additional_notes = request.POST.get('additional_notes', '')

        application = ProgramApplication.objects.create(
            program=program,
            household=household,
            motivation_letter=motivation_letter,
            additional_notes=additional_notes,
        )

        messages.success(request, 'Your application has been submitted successfully!')
        return redirect('programs:program_detail', pk=program.pk)

    context = {
        'program': program,
        'page_title': f'Apply to {program.name}',
    }

    return render(request, 'programs/program_apply.html', context)

@login_required
def my_applications(request):
    """View user's applications"""
    applications = []

    try:
        household = request.user.household
        applications = ProgramApplication.objects.filter(household=household).order_by('-application_date')
    except:
        pass

    context = {
        'applications': applications,
        'page_title': 'My Applications',
    }

    return render(request, 'programs/my_applications.html', context)

@login_required
def program_delete(request, pk):
    """Delete program (Superusers and ICT Admins only)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role == 'ict_admin'):
        messages.error(request, 'You do not have permission to delete programs.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        program_name = program.name
        program.delete()
        messages.success(request, f'Program "{program_name}" has been deleted successfully!')
        return redirect('programs:program_list')

    # Count related objects that will be affected
    applications_count = program.applications.count()
    business_groups_count = getattr(program, 'businessgroup_set', None)
    if business_groups_count:
        business_groups_count = business_groups_count.count()
    else:
        business_groups_count = 0

    context = {
        'program': program,
        'applications_count': applications_count,
        'business_groups_count': business_groups_count,
        'page_title': f'Delete Program - {program.name}',
    }
    return render(request, 'programs/program_delete.html', context)

@login_required
def program_edit(request, pk):
    """Edit program (County Executives, ICT Admins, Superusers, and program creators)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'county_executive']):
        messages.error(request, 'You do not have permission to edit this program.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        # Update program fields
        program.name = request.POST.get('name', program.name)
        program.description = request.POST.get('description', program.description)
        program.program_type = request.POST.get('program_type', program.program_type)
        program.budget = request.POST.get('budget') or program.budget
        program.target_beneficiaries = request.POST.get('target_beneficiaries') or program.target_beneficiaries
        program.eligibility_criteria = request.POST.get('eligibility_criteria', program.eligibility_criteria)
        program.application_requirements = request.POST.get('application_requirements', program.application_requirements)

        program.save()
        messages.success(request, f'Program "{program.name}" updated successfully!')
        return redirect('programs:program_detail', pk=program.pk)

    context = {
        'program': program,
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'page_title': f'Edit {program.name}',
    }

    return render(request, 'programs/program_edit.html', context)

@login_required
def program_toggle_status(request, pk):
    """Toggle program status between active/paused/ended"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'county_executive']):
        messages.error(request, 'You do not have permission to change program status.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['active', 'paused', 'ended', 'draft']:
            old_status = program.get_status_display()
            program.status = new_status
            program.save()
            messages.success(request, f'Program status changed from {old_status} to {program.get_status_display()}')
        else:
            messages.error(request, 'Invalid status provided.')

    return redirect('programs:program_detail', pk=program.pk)


@login_required
def approve_application(request, application_id):
    """Approve a program application"""
    from django.utils import timezone

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    application = get_object_or_404(ProgramApplication, id=application_id)

    if request.method == 'POST':
        try:
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()

            # Create program beneficiary entry
            ProgramBeneficiary.objects.get_or_create(
                program=application.program,
                household=application.household,
                defaults={
                    'enrollment_date': timezone.now().date(),
                    'status': 'active'
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'Application for {application.household.name} has been approved'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def reject_application(request, application_id):
    """Reject a program application"""
    from django.utils import timezone

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    application = get_object_or_404(ProgramApplication, id=application_id)

    if request.method == 'POST':
        try:
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.rejection_reason = request.POST.get('reason', '')
            application.save()

            return JsonResponse({
                'success': True,
                'message': f'Application for {application.household.name} has been rejected'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

```

---


## File: reports\__init__.py

**Location:** `reports\__init__.py`

```python
# Reports App
```

---


## File: reports\models.py

**Location:** `reports\models.py`

```python
"""
Reports and Analytics Models
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    """
    Report definitions and configurations
    """
    REPORT_TYPE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('tabular', 'Tabular Report'),
        ('chart', 'Chart/Graph'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='tabular')
    configuration = models.JSONField(blank=True, default=dict)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'upg_reports'
```

---


## File: reports\urls.py

**Location:** `reports\urls.py`

```python
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),

    # Download Reports
    path('download/households/', views.download_household_report, name='download_household_report'),
    path('download/ppi/', views.download_ppi_report, name='download_ppi_report'),
    path('download/program-participation/', views.download_program_participation_report, name='download_program_participation_report'),
    path('download/business-groups/', views.download_business_groups_report, name='download_business_groups_report'),
    path('download/savings-groups/', views.download_savings_groups_report, name='download_savings_groups_report'),
    path('download/grants/', views.download_grants_report, name='download_grants_report'),
    path('download/training/', views.download_training_report, name='download_training_report'),
    path('download/mentoring/', views.download_mentoring_report, name='download_mentoring_report'),
    path('download/geographic/', views.download_geographic_report, name='download_geographic_report'),

    # Analytics and Performance
    path('performance-dashboard/', views.performance_dashboard, name='performance_dashboard'),
    path('custom-report-builder/', views.custom_report_builder, name='custom_report_builder'),
    path('download/custom-report/', views.download_custom_report, name='download_custom_report'),
]
```

---


## File: reports\views.py

**Location:** `reports\views.py`

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from households.models import Household, HouseholdProgram, HouseholdMember, PPI
from business_groups.models import BusinessGroup, BusinessGroupMember
from upg_grants.models import SBGrant, PRGrant
from savings_groups.models import BusinessSavingsGroup, BSGMember
from training.models import Training, HouseholdTrainingEnrollment, MentoringVisit, PhoneNudge
import csv

@login_required
def report_list(request):
    """Reports dashboard view"""
    user = request.user

    # Generate some basic statistics for reports
    reports_data = {
        'total_households': Household.objects.count(),
        'active_programs': HouseholdProgram.objects.filter(participation_status='active').count(),
        'graduated_programs': HouseholdProgram.objects.filter(participation_status='graduated').count(),
        'total_business_groups': BusinessGroup.objects.count(),
    }

    # Mentor logs statistics - visible to M&E, Admin, Field Associates
    mentor_logs_visible = user.is_superuser or user.role in ['me_staff', 'ict_admin', 'field_associate', 'mentor']
    if mentor_logs_visible:
        from datetime import timedelta
        thirty_days_ago = timezone.now().date() - timedelta(days=30)

        reports_data['total_house_visits'] = MentoringVisit.objects.count()
        reports_data['total_phone_calls'] = PhoneNudge.objects.count()
        reports_data['recent_house_visits'] = MentoringVisit.objects.filter(visit_date__gte=thirty_days_ago).count()
        reports_data['recent_phone_calls'] = PhoneNudge.objects.filter(call_date__gte=thirty_days_ago).count()

    context = {
        'reports_data': reports_data,
        'mentor_logs_visible': mentor_logs_visible,
        'page_title': 'Reports & Analytics',
    }

    return render(request, 'reports/report_list.html', context)

@login_required
def download_household_report(request):
    """Download household registration report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="household_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Head of Household', 'Village', 'Parish', 'Subcounty', 'County',
        'Members Count', 'Total Members', 'Program Participants', 'Phone Number', 'Registration Date'
    ])

    for household in Household.objects.select_related('village').prefetch_related('members'):
        program_participants = household.members.filter(is_program_participant=True).count()
        head_of_household = household.members.filter(relationship_to_head='head').first()
        head_name = head_of_household.name if head_of_household else 'Not specified'

        writer.writerow([
            household.name,
            head_name,
            household.village.name if household.village else '',
            '',  # parish not available in current model
            household.village.subcounty if household.village else '',
            household.village.country if household.village else '',  # Country field exists
            getattr(household, 'members_count', household.members.count()),
            household.members.count(),
            program_participants,
            household.phone_number or '',
            household.created_at.strftime('%Y-%m-%d') if household.created_at else ''
        ])

    return response

@login_required
def download_ppi_report(request):
    """Download PPI assessment report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ppi_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Village', 'Subcounty', 'PPI Name', 'Eligibility Score',
        'Assessment Date', 'Created At'
    ])

    for ppi in PPI.objects.select_related('household', 'household__village', 'household__village__subcounty_obj').order_by('-assessment_date'):
        writer.writerow([
            ppi.household.name,
            ppi.household.village.name if ppi.household.village else '',
            ppi.household.village.subcounty_obj.name if ppi.household.village and ppi.household.village.subcounty_obj else '',
            ppi.name or 'PPI Assessment',
            ppi.eligibility_score,
            ppi.assessment_date.strftime('%Y-%m-%d'),
            ppi.created_at.strftime('%Y-%m-%d %H:%M:%S') if ppi.created_at else ''
        ])

    return response

@login_required
def download_program_participation_report(request):
    """Download program participation report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="program_participation_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Village', 'Program Name', 'Participation Status',
        'Enrollment Date', 'Graduation Date', 'Progress (%)'
    ])

    for participation in HouseholdProgram.objects.select_related('household', 'household__village', 'program'):
        writer.writerow([
            participation.household.name,
            participation.household.village.name if participation.household.village else '',
            participation.program.name,
            participation.get_participation_status_display(),
            participation.enrollment_date.strftime('%Y-%m-%d') if participation.enrollment_date else '',
            participation.graduation_date.strftime('%Y-%m-%d') if participation.graduation_date else '',
            participation.progress_percentage or 0
        ])

    return response

@login_required
def download_business_groups_report(request):
    """Download business groups report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="business_groups_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Group Name', 'Business Type', 'Business Detail', 'Formation Date',
        'Group Size', 'Members Count', 'Health Status', 'Participation Status', 'Program'
    ])

    for group in BusinessGroup.objects.select_related('program').prefetch_related('members'):
        writer.writerow([
            group.name,
            group.get_business_type_display(),
            group.business_type_detail,
            group.formation_date.strftime('%Y-%m-%d'),
            group.group_size,
            group.members.count(),
            group.get_current_business_health_display(),
            group.get_participation_status_display(),
            group.program.name if group.program else ''
        ])

    return response

@login_required
def download_savings_groups_report(request):
    """Download savings groups report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="savings_groups_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Group Name', 'Formation Date', 'Members Count', 'Savings to Date (KES)',
        'Meeting Day', 'Meeting Location', 'Active Status'
    ])

    for group in BusinessSavingsGroup.objects.prefetch_related('bsg_members'):
        writer.writerow([
            group.name,
            group.formation_date.strftime('%Y-%m-%d'),
            group.bsg_members.count(),
            f"{group.savings_to_date:,.2f}",
            group.meeting_day,
            group.meeting_location,
            'Active' if group.is_active else 'Inactive'
        ])

    return response

@login_required
def download_grants_report(request):
    """Download grant disbursement report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="grants_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Grant Type', 'Applicant Name', 'Applicant Type', 'Business Type', 'Grant Amount (KES)',
        'Status', 'Disbursement Status', 'Disbursement Date', 'Application Date'
    ])

    # SB Grants
    for grant in SBGrant.objects.select_related('business_group', 'household', 'savings_group'):
        # Get business type from business_group if available
        business_type = grant.business_group.get_business_type_display() if grant.business_group else 'N/A'

        writer.writerow([
            'SB Grant',
            grant.get_applicant_name(),
            grant.get_applicant_type().replace('_', ' ').title(),
            business_type,
            f"{grant.get_grant_amount():,.2f}",
            grant.get_status_display(),
            grant.get_disbursement_status_display(),
            grant.disbursement_date.strftime('%Y-%m-%d') if grant.disbursement_date else '',
            grant.application_date.strftime('%Y-%m-%d') if grant.application_date else ''
        ])

    # PR Grants
    for grant in PRGrant.objects.select_related('business_group', 'household', 'savings_group'):
        # Get business type from business_group if available
        business_type = grant.business_group.get_business_type_display() if grant.business_group else 'N/A'

        writer.writerow([
            'PR Grant',
            grant.get_applicant_name(),
            grant.get_applicant_type().replace('_', ' ').title(),
            business_type,
            f"{grant.grant_amount:,.2f}",
            grant.get_status_display(),
            'N/A',  # PR Grants don't have disbursement_status field
            grant.disbursement_date.strftime('%Y-%m-%d') if grant.disbursement_date else '',
            grant.application_date.strftime('%Y-%m-%d') if grant.application_date else ''
        ])

    return response

@login_required
def download_training_report(request):
    """Download training attendance report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="training_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Training Name', 'Module ID', 'BM Cycle', 'Status', 'Start Date', 'End Date',
        'Enrolled Households', 'Completed Households', 'Completion Rate (%)'
    ])

    for training in Training.objects.select_related('bm_cycle').prefetch_related('enrolled_households'):
        enrolled_count = training.enrolled_households.count()
        completed_count = training.enrolled_households.filter(enrollment_status='completed').count()
        completion_rate = (completed_count / enrolled_count * 100) if enrolled_count > 0 else 0

        writer.writerow([
            training.name,
            training.module_id,
            training.bm_cycle.bm_cycle_name if training.bm_cycle else 'N/A',
            training.get_status_display(),
            training.start_date.strftime('%Y-%m-%d') if training.start_date else '',
            training.end_date.strftime('%Y-%m-%d') if training.end_date else '',
            enrolled_count,
            completed_count,
            f"{completion_rate:.1f}"
        ])

    return response

@login_required
def download_mentoring_report(request):
    """Download mentoring activities report as CSV - accessible by M&E, Admin, Field Associates"""
    user = request.user

    # Check permissions - M&E, Admin, Field Associates, and Mentors can access
    if not (user.is_superuser or user.role in ['me_staff', 'ict_admin', 'field_associate', 'mentor']):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="error.csv"'
        writer = csv.writer(response)
        writer.writerow(['Error', 'You do not have permission to access this report'])
        return response

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mentoring_full_log_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Activity Type', 'Household', 'Village', 'Subcounty', 'Mentor', 'Mentor Email',
        'Date', 'Time', 'Topic/Type', 'Duration (minutes)', 'Successful Contact',
        'Notes', 'Created At', 'Record ID'
    ])

    # Filter based on user role
    visits_query = MentoringVisit.objects.select_related('household', 'household__village', 'household__village__subcounty_obj', 'mentor')
    nudges_query = PhoneNudge.objects.select_related('household', 'household__village', 'household__village__subcounty_obj', 'mentor')

    # Mentors only see their own logs (unless they're superuser/admin)
    if user.role == 'mentor' and not user.is_superuser:
        visits_query = visits_query.filter(mentor=user)
        nudges_query = nudges_query.filter(mentor=user)

    # Apply date filters if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    mentor_id = request.GET.get('mentor_id')

    if date_from:
        visits_query = visits_query.filter(visit_date__gte=date_from)
        nudges_query = nudges_query.filter(call_date__gte=date_from)

    if date_to:
        visits_query = visits_query.filter(visit_date__lte=date_to)
        nudges_query = nudges_query.filter(call_date__lte=date_to)

    if mentor_id and user.role != 'mentor':  # Mentors can't filter by other mentors
        visits_query = visits_query.filter(mentor_id=mentor_id)
        nudges_query = nudges_query.filter(mentor_id=mentor_id)

    # Mentoring Visits
    for visit in visits_query.order_by('-visit_date'):
        writer.writerow([
            'House Visit',
            visit.household.name,
            visit.household.village.name if visit.household.village else '',
            visit.household.village.subcounty_obj.name if visit.household.village and visit.household.village.subcounty_obj else '',
            visit.mentor.get_full_name() if visit.mentor else '',
            visit.mentor.email if visit.mentor else '',
            visit.visit_date.strftime('%Y-%m-%d') if visit.visit_date else '',
            visit.visit_time.strftime('%H:%M') if hasattr(visit, 'visit_time') and visit.visit_time else '',
            visit.topic or '',
            getattr(visit, 'duration_minutes', ''),
            'Yes',
            visit.notes or '',
            visit.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(visit, 'created_at') and visit.created_at else '',
            f"VISIT-{visit.id}"
        ])

    # Phone Nudges
    for nudge in nudges_query.order_by('-call_date'):
        call_date_str = ''
        call_time_str = ''

        # Handle both datetime and date fields
        if hasattr(nudge.call_date, 'date'):
            call_date_str = nudge.call_date.strftime('%Y-%m-%d')
            call_time_str = nudge.call_date.strftime('%H:%M')
        else:
            call_date_str = nudge.call_date.strftime('%Y-%m-%d') if nudge.call_date else ''

        writer.writerow([
            'Phone Call',
            nudge.household.name,
            nudge.household.village.name if nudge.household.village else '',
            nudge.household.village.subcounty_obj.name if nudge.household.village and nudge.household.village.subcounty_obj else '',
            nudge.mentor.get_full_name() if nudge.mentor else '',
            nudge.mentor.email if nudge.mentor else '',
            call_date_str,
            call_time_str,
            nudge.get_nudge_type_display() if hasattr(nudge, 'get_nudge_type_display') else nudge.nudge_type,
            nudge.duration_minutes if nudge.duration_minutes else '',
            'Yes' if nudge.successful_contact else 'No',
            nudge.notes or '',
            nudge.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(nudge, 'created_at') and nudge.created_at else '',
            f"CALL-{nudge.id}"
        ])

    return response

@login_required
def download_geographic_report(request):
    """Download geographic analysis report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="geographic_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'County', 'Subcounty', 'Parish', 'Village', 'Total Households',
        'Active Programs', 'Business Groups', 'Savings Groups', 'Mentors Assigned'
    ])

    # Get all villages with related data
    from core.models import Village
    for village in Village.objects.all():
        households = Household.objects.filter(village=village)
        active_programs = HouseholdProgram.objects.filter(
            household__village=village,
            participation_status='active'
        ).count()

        business_groups = BusinessGroup.objects.filter(
            members__household__village=village
        ).distinct().count()

        # This would need to be adjusted based on your savings group model structure
        savings_groups = 0  # BusinessSavingsGroup doesn't have village relation in current model

        writer.writerow([
            village.country,
            village.subcounty,
            '',  # parish not available in current model
            village.name,
            households.count(),
            active_programs,
            business_groups,
            savings_groups,
            0  # assigned_mentors not available in current model
        ])

    return response

@login_required
def performance_dashboard(request):
    """Performance dashboard with key metrics and charts"""
    # Calculate key performance indicators
    total_households = Household.objects.count()
    active_programs = HouseholdProgram.objects.filter(participation_status='active').count()
    graduated_programs = HouseholdProgram.objects.filter(participation_status='graduated').count()
    total_business_groups = BusinessGroup.objects.count()
    total_savings_groups = BusinessSavingsGroup.objects.count()

    # Program participation statistics
    program_stats = []
    from core.models import Program
    for program in Program.objects.all():
        enrolled = HouseholdProgram.objects.filter(program=program).count()
        active = HouseholdProgram.objects.filter(program=program, participation_status='active').count()
        graduated = HouseholdProgram.objects.filter(program=program, participation_status='graduated').count()
        program_stats.append({
            'name': program.name,
            'enrolled': enrolled,
            'active': active,
            'graduated': graduated,
            'completion_rate': (graduated / enrolled * 100) if enrolled > 0 else 0
        })

    # Geographic distribution
    from core.models import Village
    geographic_stats = []
    for village in Village.objects.all()[:10]:  # Top 10 villages
        household_count = Household.objects.filter(village=village).count()
        active_count = HouseholdProgram.objects.filter(
            household__village=village,
            participation_status='active'
        ).count()
        geographic_stats.append({
            'village': village.name,
            'subcounty': village.subcounty,
            'households': household_count,
            'active_programs': active_count
        })

    context = {
        'page_title': 'Program Performance Dashboard',
        'total_households': total_households,
        'active_programs': active_programs,
        'graduated_programs': graduated_programs,
        'total_business_groups': total_business_groups,
        'total_savings_groups': total_savings_groups,
        'program_stats': program_stats,
        'geographic_stats': geographic_stats,
        'graduation_rate': (graduated_programs / total_households * 100) if total_households > 0 else 0,
    }

    return render(request, 'reports/performance_dashboard.html', context)

@login_required
def custom_report_builder(request):
    """Custom report builder interface"""
    from core.models import Village, Program

    # Available filter options
    villages = Village.objects.all()
    programs = Program.objects.all()

    # Available report types
    report_types = [
        ('households', 'Household Report'),
        ('business_groups', 'Business Groups Report'),
        ('savings_groups', 'Savings Groups Report'),
        ('training', 'Training Report'),
        ('ppi', 'PPI Assessment Report'),
        ('geographic', 'Geographic Analysis'),
    ]

    context = {
        'page_title': 'Custom Report Builder',
        'villages': villages,
        'programs': programs,
        'report_types': report_types,
    }

    return render(request, 'reports/custom_report_builder.html', context)

@login_required
def download_custom_report(request):
    """Download custom report based on user selections"""
    report_type = request.GET.get('report_type', 'households')
    village_id = request.GET.get('village')
    program_id = request.GET.get('program')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="custom_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    if report_type == 'households':
        writer.writerow(['Household Name', 'Village', 'Phone Number', 'Members', 'Registration Date'])

        households = Household.objects.all()
        if village_id:
            households = households.filter(village_id=village_id)
        if date_from:
            households = households.filter(created_at__gte=date_from)
        if date_to:
            households = households.filter(created_at__lte=date_to)

        for household in households.select_related('village'):
            writer.writerow([
                household.name,
                household.village.name if household.village else '',
                household.phone_number or '',
                household.members.count(),
                household.created_at.strftime('%Y-%m-%d') if household.created_at else ''
            ])

    elif report_type == 'business_groups':
        writer.writerow(['Group Name', 'Village', 'Business Type', 'Formation Date', 'Members'])

        groups = BusinessGroup.objects.all()
        if village_id:
            groups = groups.filter(members__household__village_id=village_id).distinct()

        for group in groups:
            village_name = ''
            if group.members.exists():
                first_member = group.members.first()
                if first_member.household.village:
                    village_name = first_member.household.village.name

            writer.writerow([
                group.name,
                village_name,
                group.get_business_type_display(),
                group.formation_date.strftime('%Y-%m-%d'),
                group.members.count()
            ])

    else:
        # Default fallback
        writer.writerow(['Report Type', 'Status'])
        writer.writerow([report_type, 'Not implemented yet'])

    return response
```

---


## File: savings_groups\__init__.py

**Location:** `savings_groups\__init__.py`

```python
# Savings Groups App
```

---


## File: savings_groups\management\commands\fix_savings_totals.py

**Location:** `savings_groups\management\commands\fix_savings_totals.py`

```python
from django.core.management.base import BaseCommand
from django.db.models import Sum
from decimal import Decimal
from savings_groups.models import BusinessSavingsGroup, BSGMember, SavingsRecord


class Command(BaseCommand):
    help = 'Recalculate member total_savings from SavingsRecord data'

    def add_arguments(self, parser):
        parser.add_argument('--group-id', type=int, help='Specific savings group ID to fix')

    def handle(self, *args, **options):
        group_id = options.get('group_id')

        if group_id:
            groups = BusinessSavingsGroup.objects.filter(pk=group_id)
        else:
            groups = BusinessSavingsGroup.objects.filter(is_active=True)

        for sg in groups:
            self.stdout.write(f"\nProcessing: {sg.name}")

            # Recalculate each member's total from their savings records
            for member in sg.bsg_members.filter(is_active=True):
                calculated_total = SavingsRecord.objects.filter(member=member).aggregate(
                    total=Sum('amount'))['total'] or Decimal('0')

                old_total = member.total_savings
                member.total_savings = calculated_total
                member.save()

                self.stdout.write(
                    f"  {member.household.name}: {old_total} -> {calculated_total}"
                )

            # Recalculate group total
            group_total = sg.bsg_members.filter(is_active=True).aggregate(
                total=Sum('total_savings'))['total'] or Decimal('0')

            old_group_total = sg.savings_to_date
            sg.savings_to_date = group_total
            sg.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n  Group Total: {old_group_total} -> {group_total}"
                )
            )

        self.stdout.write(self.style.SUCCESS('\nDone!'))

```

---


## File: savings_groups\models.py

**Location:** `savings_groups\models.py`

```python
"""
Business Savings Groups (BSG) Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from households.models import Household
from business_groups.models import BusinessGroup

User = get_user_model()


class BusinessSavingsGroup(models.Model):
    """
    Community-based savings entity for entrepreneurs
    Can include multiple business groups and individual households
    """
    SAVINGS_FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]

    name = models.CharField(max_length=100)
    business_groups = models.ManyToManyField(BusinessGroup, blank=True, related_name='savings_groups', help_text="Business groups that are part of this savings group")
    members_count = models.IntegerField(default=0)
    target_members = models.IntegerField(default=25, help_text="Target number of members for this savings group")
    savings_to_date = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    formation_date = models.DateField()
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_location = models.CharField(max_length=100, blank=True)
    savings_frequency = models.CharField(max_length=20, choices=SAVINGS_FREQUENCY_CHOICES, default='weekly', help_text="How often members save")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_members(self):
        """Get total count of individual members plus business group members"""
        individual_members = self.bsg_members.filter(is_active=True).count()
        bg_members = sum([bg.members.count() for bg in self.business_groups.all()])
        return individual_members + bg_members

    class Meta:
        db_table = 'upg_business_savings_groups'


class BSGMember(models.Model):
    """
    BSG membership tracking
    """
    ROLE_CHOICES = [
        ('chairperson', 'Chairperson'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('member', 'Member'),
    ]

    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='bsg_members')
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateField()
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.household.name} - {self.bsg.name}"

    class Meta:
        db_table = 'upg_bsg_members'


class BSGProgressSurvey(models.Model):
    """
    Monthly BSG performance tracking
    """
    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='progress_surveys')
    survey_date = models.DateField()
    saving_last_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month_recorded = models.DateField()
    attendance_this_meeting = models.IntegerField(default=0)
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bsg.name} - {self.month_recorded}"

    class Meta:
        db_table = 'upg_bsg_progress_surveys'


class SavingsRecord(models.Model):
    """
    Individual savings record for BSG members
    """
    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='savings_records')
    member = models.ForeignKey(BSGMember, on_delete=models.CASCADE, related_name='savings_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    savings_date = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.household.name} - KES {self.amount} on {self.savings_date}"

    class Meta:
        db_table = 'upg_savings_records'
        ordering = ['-savings_date', '-created_at']
```

---


## File: savings_groups\templatetags\__init__.py

**Location:** `savings_groups\templatetags\__init__.py`

```python

```

---


## File: savings_groups\templatetags\math_filters.py

**Location:** `savings_groups\templatetags\math_filters.py`

```python
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0
```

---


## File: savings_groups\urls.py

**Location:** `savings_groups\urls.py`

```python
from django.urls import path
from . import views

app_name = 'savings_groups'

urlpatterns = [
    path('', views.savings_list, name='savings_list'),
    path('create/', views.savings_group_create, name='savings_group_create'),
    path('<int:pk>/', views.savings_group_detail, name='savings_group_detail'),
    path('<int:pk>/edit/', views.savings_group_edit, name='savings_group_edit'),

    # Member management
    path('<int:pk>/add-member/', views.add_member, name='add_member'),
    path('<int:pk>/remove-member/<int:member_id>/', views.remove_member, name='remove_member'),

    # Business group management
    path('<int:pk>/add-business-group/', views.add_business_group, name='add_business_group'),
    path('<int:pk>/remove-business-group/<int:bg_id>/', views.remove_business_group, name='remove_business_group'),

    # Savings management
    path('<int:pk>/record-savings/', views.record_savings, name='record_savings'),
    path('<int:pk>/savings-report/', views.savings_report, name='savings_report'),
    path('<int:pk>/export-savings/', views.export_savings_data, name='export_savings_data'),
]
```

---


## File: savings_groups\views.py

**Location:** `savings_groups\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from datetime import date
from decimal import Decimal, InvalidOperation
import csv
from .models import BusinessSavingsGroup, BSGMember, SavingsRecord
from core.models import Village
from business_groups.models import BusinessGroup
from households.models import Household

@login_required
def savings_list(request):
    """Savings Groups list view with role-based filtering"""
    user = request.user

    # Filter savings groups based on user role and village assignments
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        # Full access to all savings groups
        savings_groups = BusinessSavingsGroup.objects.filter(is_active=True)
    elif user.role in ['mentor', 'field_associate']:
        # Only groups with members from assigned villages
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            savings_groups = BusinessSavingsGroup.objects.filter(
                is_active=True,
                bsg_members__household__village__in=assigned_villages
            ).distinct()
        else:
            # No villages assigned, no groups visible
            savings_groups = BusinessSavingsGroup.objects.none()
    else:
        # Other roles have no access to savings groups
        savings_groups = BusinessSavingsGroup.objects.none()

    savings_groups = savings_groups.order_by('-formation_date')

    context = {
        'savings_groups': savings_groups,
        'page_title': 'Savings Groups',
        'total_count': savings_groups.count(),
    }

    return render(request, 'savings_groups/savings_list.html', context)

@login_required
def savings_group_create(request):
    """Create savings group with role-based filtering"""
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        village_id = request.POST.get('village')
        business_group_id = request.POST.get('business_group')
        target_members = request.POST.get('target_members', 20)

        # Validate village access for mentors
        if user.role in ['mentor', 'field_associate'] and village_id:
            if hasattr(user, 'profile') and user.profile:
                assigned_villages = user.profile.assigned_villages.values_list('id', flat=True)
                if int(village_id) not in assigned_villages:
                    messages.error(request, 'You can only create savings groups in your assigned villages.')
                    village_id = None

        if name:
            formation_date = request.POST.get('formation_date') or date.today()
            meeting_day = request.POST.get('meeting_day', '')
            meeting_location = request.POST.get('meeting_location', '')

            savings_group = BusinessSavingsGroup.objects.create(
                name=name,
                formation_date=formation_date,
                meeting_day=meeting_day,
                meeting_location=meeting_location,
                members_count=0
            )
            messages.success(request, f'Savings group "{savings_group.name}" created successfully!')
            return redirect('savings_groups:savings_group_detail', pk=savings_group.pk)
        else:
            messages.error(request, 'Savings group name is required.')

    # Filter villages and business groups based on user role
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        villages = Village.objects.all()
        business_groups = BusinessGroup.objects.all()
    elif user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            villages = assigned_villages
            # Business groups with members from assigned villages
            business_groups = BusinessGroup.objects.filter(
                members__household__village__in=assigned_villages
            ).distinct()
        else:
            villages = Village.objects.none()
            business_groups = BusinessGroup.objects.none()
            messages.warning(request, 'You have no assigned villages. Please contact your administrator.')
    else:
        villages = Village.objects.none()
        business_groups = BusinessGroup.objects.none()
        messages.error(request, 'You do not have permission to create savings groups.')

    context = {
        'villages': villages,
        'business_groups': business_groups,
        'page_title': 'Create Savings Group',
    }
    return render(request, 'savings_groups/savings_group_create.html', context)

@login_required
def savings_group_detail(request, pk):
    """Savings group detail view"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    # Calculate membership percentage
    current_members = savings_group.bsg_members.filter(is_active=True).count()
    target_members = savings_group.target_members or 25  # Default target if not set
    membership_percentage = round((current_members * 100) / target_members) if target_members > 0 else 0

    context = {
        'savings_group': savings_group,
        'page_title': f'Savings Group - {savings_group.name}',
        'current_members': current_members,
        'membership_percentage': membership_percentage,
    }
    return render(request, 'savings_groups/savings_group_detail.html', context)

@login_required
def savings_group_edit(request, pk):
    """Edit savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        savings_group.name = request.POST.get('name', savings_group.name)
        formation_date = request.POST.get('formation_date')
        if formation_date:
            savings_group.formation_date = formation_date
        savings_group.meeting_day = request.POST.get('meeting_day', savings_group.meeting_day)
        savings_group.meeting_location = request.POST.get('meeting_location', savings_group.meeting_location)

        # Handle savings_frequency
        savings_frequency = request.POST.get('savings_frequency')
        if savings_frequency:
            savings_group.savings_frequency = savings_frequency

        # Handle target_members
        target_members = request.POST.get('target_members')
        if target_members:
            try:
                savings_group.target_members = int(target_members)
            except ValueError:
                pass  # Keep existing value if invalid input

        savings_group.save()
        messages.success(request, f'Savings group "{savings_group.name}" updated successfully!')
        return redirect('savings_groups:savings_group_detail', pk=savings_group.pk)

    villages = Village.objects.all()
    business_groups = BusinessGroup.objects.all()

    # Calculate membership percentage
    current_members = savings_group.bsg_members.filter(is_active=True).count()
    target_members = savings_group.target_members or 25  # Default target if not set
    membership_percentage = round((current_members * 100) / target_members) if target_members > 0 else 0

    context = {
        'savings_group': savings_group,
        'villages': villages,
        'business_groups': business_groups,
        'page_title': f'Edit - {savings_group.name}',
        'current_members': current_members,
        'membership_percentage': membership_percentage,
    }
    return render(request, 'savings_groups/savings_group_edit.html', context)

@login_required
def add_member(request, pk):
    """Add individual member to savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        household_id = request.POST.get('household')
        role = request.POST.get('role', 'member')
        joined_date = request.POST.get('joined_date') or date.today()

        if household_id:
            try:
                household = Household.objects.get(id=household_id)

                # Check if already a member
                if BSGMember.objects.filter(bsg=savings_group, household=household, is_active=True).exists():
                    messages.warning(request, f'{household.name} is already a member of this savings group.')
                else:
                    BSGMember.objects.create(
                        bsg=savings_group,
                        household=household,
                        role=role,
                        joined_date=joined_date,
                        is_active=True
                    )
                    messages.success(request, f'{household.name} added to {savings_group.name} successfully!')
            except Household.DoesNotExist:
                messages.error(request, 'Selected household does not exist.')
        else:
            messages.error(request, 'Please select a household.')

        return redirect('savings_groups:savings_group_detail', pk=pk)

    # Get available households (not already members)
    existing_member_households = savings_group.bsg_members.filter(is_active=True).values_list('household_id', flat=True)
    available_households = Household.objects.exclude(id__in=existing_member_households).order_by('name')

    context = {
        'savings_group': savings_group,
        'households': available_households,
        'role_choices': BSGMember.ROLE_CHOICES,
        'page_title': f'Add Member to {savings_group.name}',
    }
    return render(request, 'savings_groups/add_member.html', context)

@login_required
def remove_member(request, pk, member_id):
    """Remove individual member from savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    member = get_object_or_404(BSGMember, id=member_id, bsg=savings_group)

    if request.method == 'POST':
        member.is_active = False
        member.save()
        messages.success(request, f'{member.household.name} removed from {savings_group.name}.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'member': member,
        'page_title': f'Remove Member from {savings_group.name}',
    }
    return render(request, 'savings_groups/remove_member_confirm.html', context)

@login_required
def add_business_group(request, pk):
    """Associate business group with savings group and auto-add all members"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        business_group_id = request.POST.get('business_group')

        if business_group_id:
            try:
                business_group = BusinessGroup.objects.get(id=business_group_id)

                # Check if already associated
                if business_group in savings_group.business_groups.all():
                    messages.warning(request, f'{business_group.name} is already part of this savings group.')
                else:
                    # Add business group to savings group
                    savings_group.business_groups.add(business_group)

                    # Automatically add all business group members to savings group
                    members_added = 0
                    for bg_member in business_group.members.all():
                        # Check if household is not already a member
                        if not BSGMember.objects.filter(bsg=savings_group, household=bg_member.household, is_active=True).exists():
                            BSGMember.objects.create(
                                bsg=savings_group,
                                household=bg_member.household,
                                role='member',
                                joined_date=date.today(),
                                is_active=True
                            )
                            members_added += 1

                    messages.success(request, f'{business_group.name} added to {savings_group.name} successfully! {members_added} member(s) added.')
            except BusinessGroup.DoesNotExist:
                messages.error(request, 'Selected business group does not exist.')
        else:
            messages.error(request, 'Please select a business group.')

        return redirect('savings_groups:savings_group_detail', pk=pk)

    # Get available business groups (not already associated)
    available_business_groups = BusinessGroup.objects.exclude(
        id__in=savings_group.business_groups.values_list('id', flat=True)
    ).order_by('name')

    context = {
        'savings_group': savings_group,
        'business_groups': available_business_groups,
        'page_title': f'Add Business Group to {savings_group.name}',
    }
    return render(request, 'savings_groups/add_business_group.html', context)

@login_required
def remove_business_group(request, pk, bg_id):
    """Remove business group from savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    business_group = get_object_or_404(BusinessGroup, id=bg_id)

    if request.method == 'POST':
        savings_group.business_groups.remove(business_group)
        messages.success(request, f'{business_group.name} removed from {savings_group.name}.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'business_group': business_group,
        'page_title': f'Remove Business Group from {savings_group.name}',
    }
    return render(request, 'savings_groups/remove_business_group_confirm.html', context)

@login_required
def record_savings(request, pk):
    """Record savings for a savings group meeting"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        savings_date = request.POST.get('savings_date') or date.today()
        notes = request.POST.get('notes', '')
        records_created = 0

        # Process each member's savings
        for member in savings_group.bsg_members.filter(is_active=True):
            amount_key = f'amount_{member.id}'
            amount = request.POST.get(amount_key, '0')

            try:
                amount = Decimal(str(amount))
                if amount > 0:
                    # Create savings record
                    SavingsRecord.objects.create(
                        bsg=savings_group,
                        member=member,
                        amount=amount,
                        savings_date=savings_date,
                        recorded_by=request.user,
                        notes=notes
                    )

                    # Update member's total savings - refresh from DB first to avoid stale data
                    member.refresh_from_db()
                    current_total = member.total_savings or Decimal('0')
                    member.total_savings = current_total + amount
                    member.save()

                    records_created += 1
            except (ValueError, TypeError, InvalidOperation):
                pass

        # Update group's total savings - refresh first
        savings_group.refresh_from_db()
        total_savings = savings_group.bsg_members.filter(is_active=True).aggregate(
            total=Sum('total_savings'))['total'] or Decimal('0')
        savings_group.savings_to_date = total_savings
        savings_group.save()

        messages.success(request, f'{records_created} savings record(s) created successfully!')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'members': savings_group.bsg_members.filter(is_active=True).order_by('household__name'),
        'page_title': f'Record Savings - {savings_group.name}',
    }
    return render(request, 'savings_groups/record_savings.html', context)


@login_required
def savings_report(request, pk):
    """Generate savings report for a savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Get all savings records
    savings_records = SavingsRecord.objects.filter(bsg=savings_group)

    if date_from:
        savings_records = savings_records.filter(savings_date__gte=date_from)
    if date_to:
        savings_records = savings_records.filter(savings_date__lte=date_to)

    # Calculate totals
    total_savings = savings_records.aggregate(total=Sum('amount'))['total'] or 0

    # Member summaries
    member_summaries = []
    for member in savings_group.bsg_members.filter(is_active=True):
        member_records = savings_records.filter(member=member)
        member_total = member_records.aggregate(total=Sum('amount'))['total'] or 0
        member_summaries.append({
            'member': member,
            'total_savings': member_total,
            'record_count': member_records.count(),
            'latest_savings': member_records.order_by('-savings_date').first(),
        })

    context = {
        'savings_group': savings_group,
        'savings_records': savings_records.order_by('-savings_date'),
        'total_savings': total_savings,
        'member_summaries': member_summaries,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': f'Savings Report - {savings_group.name}',
    }
    return render(request, 'savings_groups/savings_report.html', context)


@login_required
def export_savings_data(request, pk):
    """Export savings data to CSV"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="savings_{savings_group.name}_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Member Name', 'Amount (KES)', 'Recorded By', 'Notes'
    ])

    # Get savings records
    for record in SavingsRecord.objects.filter(bsg=savings_group).order_by('-savings_date'):
        writer.writerow([
            record.savings_date.strftime('%Y-%m-%d'),
            record.member.household.name,
            f"{record.amount:,.2f}",
            record.recorded_by.get_full_name() if record.recorded_by else 'N/A',
            record.notes
        ])

    # Add summary rows
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Savings:', f"KES {savings_group.savings_to_date:,.2f}"])
    writer.writerow(['Total Members:', savings_group.bsg_members.filter(is_active=True).count()])
    writer.writerow(['Savings Frequency:', savings_group.get_savings_frequency_display()])

    return response

```

---


## File: settings_module\__init__.py

**Location:** `settings_module\__init__.py`

```python

```

---


## File: settings_module\apps.py

**Location:** `settings_module\apps.py`

```python
from django.apps import AppConfig


class SettingsModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_module'
```

---


## File: settings_module\management\__init__.py

**Location:** `settings_module\management\__init__.py`

```python

```

---


## File: settings_module\management\commands\__init__.py

**Location:** `settings_module\management\commands\__init__.py`

```python

```

---


## File: settings_module\management\commands\populate_audit_logs.py

**Location:** `settings_module\management\commands\populate_audit_logs.py`

```python
"""
Management command to populate sample audit logs for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from settings_module.models import SystemAuditLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample audit logs for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample audit logs...'))

        # Get users or create sample ones
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Creating sample users...'))
            # Create sample users if none exist
            users = [
                User.objects.create_user(
                    username='admin',
                    email='admin@example.com',
                    role='ict_admin',
                    password='password123'
                ),
                User.objects.create_user(
                    username='mentor1',
                    email='mentor1@example.com',
                    role='mentor',
                    password='password123'
                ),
                User.objects.create_user(
                    username='field_associate1',
                    email='fa1@example.com',
                    role='field_associate',
                    password='password123'
                ),
            ]

        # Sample actions and models
        actions = ['create', 'read', 'update', 'delete', 'login', 'logout', 'export']
        models = ['Household', 'BusinessGroup', 'SavingsGroup', 'User', 'Form', 'Survey', 'Grant']
        ip_addresses = ['127.0.0.1', '192.168.1.100', '10.0.0.50', '172.16.0.25']
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]

        # Create 50 sample audit log entries
        for i in range(50):
            user = random.choice(users)
            action = random.choice(actions)
            model_name = random.choice(models)

            # Create timestamp within last 30 days
            days_ago = random.randint(0, 30)
            timestamp = timezone.now() - timedelta(days=days_ago,
                                                 hours=random.randint(0, 23),
                                                 minutes=random.randint(0, 59))

            # Sample changes data
            changes = {}
            if action == 'update':
                changes = {
                    'old_value': f'old_{i}',
                    'new_value': f'new_{i}',
                    'field': 'status'
                }
            elif action == 'create':
                changes = {'created_fields': ['name', 'status', 'created_at']}

            SystemAuditLog.objects.create(
                user=user,
                action=action,
                model_name=model_name,
                object_id=str(random.randint(1, 100)),
                object_repr=f'{model_name} #{random.randint(1, 100)}',
                ip_address=random.choice(ip_addresses),
                user_agent=random.choice(user_agents),
                request_path=f'/{model_name.lower()}s/',
                request_method=random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                changes=changes,
                success=random.choice([True, True, True, False]),  # 75% success rate
                error_message='Sample error message' if random.random() < 0.25 else '',
                timestamp=timestamp
            )

        # Create some specific recent login/logout entries
        for user in users[:3]:
            # Login entry
            SystemAuditLog.objects.create(
                user=user,
                action='login',
                model_name='User',
                object_repr=str(user),
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                request_path='/accounts/login/',
                request_method='POST',
                success=True,
                timestamp=timezone.now() - timedelta(hours=random.randint(1, 24))
            )

            # Logout entry
            SystemAuditLog.objects.create(
                user=user,
                action='logout',
                model_name='User',
                object_repr=str(user),
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                request_path='/accounts/logout/',
                request_method='POST',
                success=True,
                timestamp=timezone.now() - timedelta(minutes=random.randint(30, 120))
            )

        total_logs = SystemAuditLog.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample audit logs. Total logs in database: {total_logs}'
            )
        )
```

---


## File: settings_module\management\commands\populate_system_config.py

**Location:** `settings_module\management\commands\populate_system_config.py`

```python
"""
Management command to populate sample system configuration settings
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from settings_module.models import SystemConfiguration

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample system configuration settings'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample system configurations...'))

        # Get an admin user or create one
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(role='ict_admin').first()

        if not admin_user:
            admin_user = User.objects.create_user(
                username='config_admin',
                email='admin@example.com',
                role='ict_admin',
                password='password123',
                is_superuser=True
            )

        # Sample configuration settings
        configurations = [
            # General Settings
            {
                'key': 'SYSTEM_NAME',
                'value': 'UPG Management System',
                'setting_type': 'string',
                'description': 'The display name of the system',
                'category': 'general',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'SYSTEM_VERSION',
                'value': '1.0.0',
                'setting_type': 'string',
                'description': 'Current version of the system',
                'category': 'general',
                'is_public': True,
                'is_editable': False,
            },
            {
                'key': 'DEFAULT_LANGUAGE',
                'value': 'en',
                'setting_type': 'string',
                'description': 'Default language for the system',
                'category': 'general',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'DEFAULT_TIMEZONE',
                'value': 'Africa/Nairobi',
                'setting_type': 'string',
                'description': 'Default timezone for the system',
                'category': 'general',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'MAINTENANCE_MODE',
                'value': 'false',
                'setting_type': 'boolean',
                'description': 'Enable maintenance mode to restrict access',
                'category': 'general',
                'is_public': False,
                'is_editable': True,
            },

            # Email Settings
            {
                'key': 'EMAIL_NOTIFICATIONS_ENABLED',
                'value': 'true',
                'setting_type': 'boolean',
                'description': 'Enable email notifications system-wide',
                'category': 'email',
                'is_public': False,
                'is_editable': True,
            },
            {
                'key': 'DEFAULT_FROM_EMAIL',
                'value': 'noreply@upgmanagement.org',
                'setting_type': 'string',
                'description': 'Default sender email address',
                'category': 'email',
                'is_public': False,
                'is_editable': True,
            },
            {
                'key': 'EMAIL_ADMIN_NOTIFICATIONS',
                'value': 'admin@upgmanagement.org',
                'setting_type': 'string',
                'description': 'Email address for admin notifications',
                'category': 'email',
                'is_public': False,
                'is_editable': True,
            },

            # UPG Program Settings
            {
                'key': 'UPG_PROGRAM_DURATION_MONTHS',
                'value': '12',
                'setting_type': 'integer',
                'description': 'Duration of UPG program in months',
                'category': 'program',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'DEFAULT_CURRENCY',
                'value': 'KES',
                'setting_type': 'string',
                'description': 'Default currency for financial transactions',
                'category': 'program',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'MINIMUM_GROUP_SIZE',
                'value': '5',
                'setting_type': 'integer',
                'description': 'Minimum number of members for business groups',
                'category': 'program',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'MAXIMUM_GROUP_SIZE',
                'value': '30',
                'setting_type': 'integer',
                'description': 'Maximum number of members for business groups',
                'category': 'program',
                'is_public': True,
                'is_editable': True,
            },

            # Security Settings
            {
                'key': 'SESSION_TIMEOUT_MINUTES',
                'value': '60',
                'setting_type': 'integer',
                'description': 'User session timeout in minutes',
                'category': 'security',
                'is_public': False,
                'is_editable': True,
            },
            {
                'key': 'PASSWORD_MIN_LENGTH',
                'value': '8',
                'setting_type': 'integer',
                'description': 'Minimum password length requirement',
                'category': 'security',
                'is_public': False,
                'is_editable': True,
            },
            {
                'key': 'ENABLE_TWO_FACTOR_AUTH',
                'value': 'false',
                'setting_type': 'boolean',
                'description': 'Enable two-factor authentication',
                'category': 'security',
                'is_public': False,
                'is_editable': True,
            },

            # Reports Settings
            {
                'key': 'DEFAULT_REPORT_FORMAT',
                'value': 'pdf',
                'setting_type': 'string',
                'description': 'Default format for generated reports',
                'category': 'reports',
                'is_public': True,
                'is_editable': True,
            },
            {
                'key': 'REPORT_RETENTION_DAYS',
                'value': '90',
                'setting_type': 'integer',
                'description': 'Number of days to retain generated reports',
                'category': 'reports',
                'is_public': False,
                'is_editable': True,
            },

            # Advanced Settings
            {
                'key': 'API_RATE_LIMITS',
                'value': '{"per_minute": 60, "per_hour": 1000}',
                'setting_type': 'json',
                'description': 'API rate limiting configuration',
                'category': 'advanced',
                'is_public': False,
                'is_editable': True,
            },
            {
                'key': 'FEATURE_FLAGS',
                'value': '{"experimental_dashboard": false, "beta_reports": true}',
                'setting_type': 'json',
                'description': 'Feature flags for enabling/disabling features',
                'category': 'advanced',
                'is_public': False,
                'is_editable': True,
            },
        ]

        created_count = 0
        for config_data in configurations:
            config, created = SystemConfiguration.objects.get_or_create(
                key=config_data['key'],
                defaults={
                    **config_data,
                    'created_by': admin_user,
                    'modified_by': admin_user,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {config.key}')
            else:
                self.stdout.write(f'Already exists: {config.key}')

        total_configs = SystemConfiguration.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(configurations)} configurations. '
                f'Created {created_count} new configurations. '
                f'Total configurations in database: {total_configs}'
            )
        )
```

---


## File: settings_module\models.py

**Location:** `settings_module\models.py`

```python
"""
Settings Module Models for UPG System
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings
    """
    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('file', 'File Path'),
    ]

    key = models.CharField(max_length=100, unique=True, help_text="Configuration key identifier")
    value = models.TextField(help_text="Configuration value")
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    description = models.TextField(blank=True, help_text="Description of this setting")
    category = models.CharField(max_length=50, default='general', help_text="Setting category")
    is_public = models.BooleanField(default=False, help_text="Can be viewed by non-admin users")
    is_editable = models.BooleanField(default=True, help_text="Can be modified")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_settings')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_settings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    def get_typed_value(self):
        """Return the value converted to the appropriate type"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'integer':
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.setting_type == 'json':
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value

    class Meta:
        db_table = 'upg_system_configurations'
        ordering = ['category', 'key']


class UserSettings(models.Model):
    """
    User-specific settings and preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # System preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    dashboard_layout = models.JSONField(default=dict, blank=True)
    theme = models.CharField(max_length=20, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    language = models.CharField(max_length=10, default='en', choices=[('en', 'English'), ('sw', 'Swahili')])
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')

    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Settings"

    class Meta:
        db_table = 'upg_user_settings'


class SystemAuditLog(models.Model):
    """
    System audit logging for tracking user actions
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('system', 'System Action'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True, help_text="Django model name")
    object_id = models.CharField(max_length=100, blank=True, help_text="ID of the object acted upon")
    object_repr = models.CharField(max_length=200, blank=True, help_text="String representation of the object")

    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)

    # Change details
    changes = models.JSONField(default=dict, blank=True, help_text="Details of what changed")
    additional_data = models.JSONField(default=dict, blank=True, help_text="Additional context data")

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_action_display()} - {self.timestamp}"

    class Meta:
        db_table = 'upg_system_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
        ]


class SystemAlert(models.Model):
    """
    System-wide alerts and notifications
    """
    ALERT_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
        ('security', 'Security'),
    ]

    ALERT_SCOPES = [
        ('system', 'System Wide'),
        ('role', 'Role Specific'),
        ('user', 'User Specific'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info')
    scope = models.CharField(max_length=20, choices=ALERT_SCOPES, default='system')

    # Targeting
    target_roles = models.JSONField(default=list, blank=True, help_text="List of roles if scope is 'role'")
    target_users = models.ManyToManyField(User, blank=True, help_text="Specific users if scope is 'user'")

    # Display settings
    is_active = models.BooleanField(default=True)
    show_until = models.DateTimeField(null=True, blank=True, help_text="Alert expires after this date")
    is_dismissible = models.BooleanField(default=True, help_text="Users can dismiss this alert")

    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_alert_type_display()})"

    def is_expired(self):
        """Check if alert is expired"""
        if self.show_until:
            return timezone.now() > self.show_until
        return False

    def is_visible_to_user(self, user):
        """Check if alert should be shown to a specific user"""
        if not self.is_active or self.is_expired():
            return False

        if self.scope == 'system':
            return True
        elif self.scope == 'role':
            return user.role in self.target_roles
        elif self.scope == 'user':
            return user in self.target_users.all()

        return False

    class Meta:
        db_table = 'upg_system_alerts'
        ordering = ['-created_at']


class UserAlertDismissal(models.Model):
    """
    Track which users have dismissed which alerts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert = models.ForeignKey(SystemAlert, on_delete=models.CASCADE)
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'upg_user_alert_dismissals'
        unique_together = ['user', 'alert']


class SystemBackup(models.Model):
    """
    Track system backups
    """
    BACKUP_TYPES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('database', 'Database Only'),
        ('media', 'Media Files Only'),
    ]

    BACKUP_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=200)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full')
    status = models.CharField(max_length=20, choices=BACKUP_STATUS, default='pending')

    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")

    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    @property
    def duration(self):
        """Calculate backup duration"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

    class Meta:
        db_table = 'upg_system_backups'
        ordering = ['-started_at']
```

---


## File: settings_module\urls.py

**Location:** `settings_module\urls.py`

```python
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_dashboard, name='settings_dashboard'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),

    # System Configuration
    path('config/', views.system_config, name='system_config'),
    path('config/<int:config_id>/edit/', views.config_edit, name='config_edit'),

    # User Settings
    path('user-settings/', views.user_settings, name='user_settings'),
    path('user-settings/<int:user_id>/', views.user_settings, name='user_settings_view'),

    # Audit Logs
    path('audit/', views.audit_logs, name='audit_logs'),

    # System Alerts
    path('alerts/', views.system_alerts, name='system_alerts'),
    path('alerts/create/', views.create_alert, name='create_alert'),
    path('alerts/<int:alert_id>/toggle/', views.toggle_alert, name='toggle_alert'),
    path('alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
]
```

---


## File: settings_module\views.py

**Location:** `settings_module\views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import SystemConfiguration, UserSettings, SystemAuditLog, SystemAlert, UserAlertDismissal, SystemBackup

User = get_user_model()

@login_required
def settings_dashboard(request):
    """System settings dashboard"""
    # Check permissions
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'me_staff']):
        return HttpResponseForbidden("You do not have permission to access system settings.")

    # Get system statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users

    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_logins = SystemAuditLog.objects.filter(
        action='login',
        timestamp__gte=week_ago
    ).count()

    # System alerts
    active_alerts = SystemAlert.objects.filter(
        is_active=True,
        show_until__gt=timezone.now()
    ).count()

    # Configuration count
    config_count = SystemConfiguration.objects.count()

    # Last backup
    last_backup = SystemBackup.objects.filter(status='completed').first()

    context = {
        'page_title': 'System Settings',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'recent_logins': recent_logins,
        'active_alerts': active_alerts,
        'config_count': config_count,
        'last_backup': last_backup,
        'system_version': '1.0.0',
    }
    return render(request, 'settings_module/settings_dashboard.html', context)

@login_required
def user_management(request):
    """User management page"""
    # Check permissions - only ICT admin and superuser can manage users
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('settings:settings_dashboard')

    users = User.objects.all().order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            username__icontains=search_query
        ) | users.filter(
            email__icontains=search_query
        ) | users.filter(
            first_name__icontains=search_query
        ) | users.filter(
            last_name__icontains=search_query
        )

    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'page_title': 'User Management',
        'users': users,
        'role_choices': User.ROLE_CHOICES,
        'search_query': search_query,
        'selected_role': role_filter,
    }
    return render(request, 'settings_module/user_management.html', context)

@login_required
def user_create(request):
    """Create new user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to create users.')
        return redirect('settings:user_management')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')

        if username and email and password:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role=role
                )
                messages.success(request, f'User "{username}" created successfully!')
                return redirect('settings:user_management')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Username, email, and password are required.')

    context = {
        'page_title': 'Create New User',
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'settings_module/user_create.html', context)

@login_required
def user_edit(request, user_id):
    """Edit user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to edit users.')
        return redirect('settings:user_management')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.role = request.POST.get('role', user.role)

        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)

        try:
            user.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('settings:user_management')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

    context = {
        'page_title': f'Edit User - {user.username}',
        'user_obj': user,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'settings_module/user_edit.html', context)

@login_required
@require_POST
def user_toggle_status(request, user_id):
    """Toggle user active status"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    user = get_object_or_404(User, id=user_id)

    # Don't allow deactivating superusers unless request user is also superuser
    if user.is_superuser and not request.user.is_superuser:
        return JsonResponse({'error': 'Cannot modify superuser status'}, status=403)

    # Don't allow users to deactivate themselves
    if user == request.user:
        return JsonResponse({'error': 'Cannot modify your own status'}, status=403)

    user.is_active = not user.is_active
    user.save()

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" has been {status}.')

    return JsonResponse({
        'success': True,
        'status': user.is_active,
        'message': f'User {status} successfully'
    })

@login_required
def user_delete(request, user_id):
    """Delete user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('settings:user_management')

    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('settings:user_management')

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot delete superuser accounts.')
        return redirect('settings:user_management')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
        return redirect('settings:user_management')

    context = {
        'page_title': f'Delete User - {user.username}',
        'user_obj': user,
    }
    return render(request, 'settings_module/user_delete.html', context)


# System Configuration Views
@login_required
def system_config(request):
    """System configuration management"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("You do not have permission to access system configuration.")

    configs = SystemConfiguration.objects.all().order_by('category', 'key')

    # Group configurations by category
    config_groups = {}
    for config in configs:
        if config.category not in config_groups:
            config_groups[config.category] = []
        config_groups[config.category].append(config)

    context = {
        'page_title': 'System Configuration',
        'config_groups': config_groups,
        'total_configs': configs.count(),
    }
    return render(request, 'settings_module/system_config.html', context)


@login_required
def config_edit(request, config_id):
    """Edit system configuration"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    config = get_object_or_404(SystemConfiguration, id=config_id)

    if not config.is_editable:
        messages.error(request, 'This configuration setting cannot be modified.')
        return redirect('settings:system_config')

    if request.method == 'POST':
        old_value = config.value
        config.value = request.POST.get('value', config.value)
        config.modified_by = request.user

        try:
            config.save()

            # Log the change
            SystemAuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='SystemConfiguration',
                object_id=str(config.id),
                object_repr=str(config),
                changes={'old_value': old_value, 'new_value': config.value},
                success=True
            )

            messages.success(request, f'Configuration "{config.key}" updated successfully!')
            return redirect('settings:system_config')
        except Exception as e:
            messages.error(request, f'Error updating configuration: {str(e)}')

    context = {
        'page_title': f'Edit Configuration - {config.key}',
        'config': config,
    }
    return render(request, 'settings_module/config_edit.html', context)


# User Profile Management
@login_required
def user_settings(request, user_id=None):
    """View/edit user settings"""
    if user_id:
        # Admin viewing/editing another user's settings
        if not (request.user.is_superuser or request.user.role == 'ict_admin'):
            return HttpResponseForbidden("Permission denied.")
        user = get_object_or_404(User, id=user_id)
    else:
        # User viewing/editing their own settings
        user = request.user

    settings_obj, created = UserSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update profile picture if uploaded
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            try:
                user.save()
                messages.success(request, 'Profile picture updated successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading profile picture: {str(e)}')

        # Update settings
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.sms_notifications = request.POST.get('sms_notifications') == 'on'
        settings_obj.theme = request.POST.get('theme', settings_obj.theme)
        settings_obj.language = request.POST.get('language', settings_obj.language)
        settings_obj.timezone = request.POST.get('timezone', settings_obj.timezone)

        try:
            settings_obj.save()
            messages.success(request, 'Settings updated successfully!')

            # Log the change
            SystemAuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='UserSettings',
                object_id=str(settings_obj.id),
                object_repr=str(settings_obj),
                success=True
            )

        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')

    context = {
        'page_title': f'User Settings - {user.get_full_name() or user.username}',
        'settings_user': user,
        'settings_obj': settings_obj,
        'is_own_settings': user == request.user,
    }
    return render(request, 'settings_module/user_settings.html', context)


# Audit Log Views
@login_required
def audit_logs(request):
    """View system audit logs"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'me_staff']):
        return HttpResponseForbidden("You do not have permission to view audit logs.")

    logs = SystemAuditLog.objects.all().select_related('user')

    # Filters
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)

    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)

    model_filter = request.GET.get('model')
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)

    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    context = {
        'page_title': 'System Audit Logs',
        'logs': logs,
        'action_choices': SystemAuditLog.ACTION_TYPES,
        'filters': {
            'action': action_filter,
            'user': user_filter,
            'model': model_filter,
            'date_from': date_from,
            'date_to': date_to,
        },
    }
    return render(request, 'settings_module/audit_logs.html', context)


# System Alerts Management
@login_required
def system_alerts(request):
    """Manage system alerts"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    alerts = SystemAlert.objects.all().order_by('-created_at')

    context = {
        'page_title': 'System Alerts',
        'alerts': alerts,
    }
    return render(request, 'settings_module/system_alerts.html', context)


@login_required
def create_alert(request):
    """Create system alert"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        alert_type = request.POST.get('alert_type', 'info')
        scope = request.POST.get('scope', 'system')

        if title and message:
            alert = SystemAlert.objects.create(
                title=title,
                message=message,
                alert_type=alert_type,
                scope=scope,
                created_by=request.user
            )

            # Handle role targeting if scope is 'role'
            if scope == 'role':
                target_roles = request.POST.getlist('target_roles')
                alert.target_roles = target_roles
                alert.save()

            messages.success(request, 'System alert created successfully!')
            return redirect('settings:system_alerts')
        else:
            messages.error(request, 'Title and message are required.')

    context = {
        'page_title': 'Create System Alert',
        'alert_types': SystemAlert.ALERT_TYPES,
        'alert_scopes': SystemAlert.ALERT_SCOPES,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'settings_module/create_alert.html', context)


@login_required
def toggle_alert(request, alert_id):
    """Toggle alert active status"""
    from django.http import JsonResponse

    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    alert = get_object_or_404(SystemAlert, id=alert_id)

    if request.method == 'POST':
        try:
            activate = request.POST.get('activate', 'false') == 'true'
            alert.is_active = activate
            alert.save()

            action = 'activated' if activate else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'Alert "{alert.title}" has been {action}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_alert(request, alert_id):
    """Delete a system alert"""
    from django.http import JsonResponse

    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    alert = get_object_or_404(SystemAlert, id=alert_id)

    if request.method == 'POST':
        try:
            alert_title = alert.title
            alert.delete()

            return JsonResponse({
                'success': True,
                'message': f'Alert "{alert_title}" has been deleted'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
```

---


## File: setup.py

**Location:** `setup.py`

```python
#!/usr/bin/env python
"""
UPG Management System Setup Script
Automated setup for local development and testing
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line


def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*50}")
    print(f"STEP: {description}")
    print(f"{'='*50}")

    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=True, capture_output=True, text=True)

        if result.stdout:
            print(f"Output: {result.stdout}")

        print(f"✅ SUCCESS: {description}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {description}")
        print(f"Error output: {e.stderr if e.stderr else e.stdout}")
        return False


def install_requirements():
    """Install Python requirements"""
    return run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      "Installing Python requirements")


def run_migrations():
    """Run Django migrations"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')

    # Make migrations
    success1 = run_command([sys.executable, 'manage.py', 'makemigrations'],
                          "Creating database migrations")

    # Apply migrations
    success2 = run_command([sys.executable, 'manage.py', 'migrate'],
                          "Applying database migrations")

    return success1 and success2


def create_superuser():
    """Create superuser account"""
    print(f"\n{'='*50}")
    print("STEP: Creating superuser account")
    print(f"{'='*50}")

    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')
        execute_from_command_line(['manage.py', 'createsuperuser'])
        print("✅ SUCCESS: Superuser created")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to create superuser - {e}")
        return False


def load_sample_data():
    """Load sample data"""
    return run_command([sys.executable, 'manage.py', 'loaddata', 'sample_data.json'],
                      "Loading sample data")


def collect_static():
    """Collect static files"""
    return run_command([sys.executable, 'manage.py', 'collectstatic', '--noinput'],
                      "Collecting static files")


def main():
    """Main setup function"""
    print("🚀 UPG Management System Setup")
    print("This script will set up the UPG system for local development and testing\n")

    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ ERROR: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)

    # Step 1: Install requirements
    if not install_requirements():
        print("⚠️  WARNING: Requirements installation failed. Please install manually.")

    # Step 2: Run migrations
    if not run_migrations():
        print("❌ CRITICAL: Database migration failed. Setup cannot continue.")
        sys.exit(1)

    # Step 3: Create superuser
    print("\n📝 Now you need to create a superuser account for system administration:")
    if not create_superuser():
        print("⚠️  WARNING: Superuser creation failed. You can create one later with: python manage.py createsuperuser")

    # Step 4: Collect static files
    if not collect_static():
        print("⚠️  WARNING: Static file collection failed.")

    # Final instructions
    print(f"\n{'='*60}")
    print("🎉 UPG MANAGEMENT SYSTEM SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\n📋 NEXT STEPS:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print("\n2. Open your browser and go to:")
    print("   http://127.0.0.1:8000")
    print("\n3. Login with the superuser account you created")
    print("\n4. Access the admin panel at:")
    print("   http://127.0.0.1:8000/admin")
    print("\n5. Start adding data and testing the system!")
    print(f"\n{'='*60}")


if __name__ == '__main__':
    main()
```

---


## File: surveys\__init__.py

**Location:** `surveys\__init__.py`

```python
# Surveys App
```

---


## File: surveys\models.py

**Location:** `surveys\models.py`

```python
"""
Survey and Data Collection Models
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Survey(models.Model):
    """
    Survey definition and management
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (v{self.version})"

    class Meta:
        db_table = 'upg_surveys'


class SurveyResponse(models.Model):
    """
    Survey responses from field data collection
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey('households.Household', on_delete=models.CASCADE)
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    response_data = models.JSONField()
    completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.survey.name} - {self.respondent.name}"

    class Meta:
        db_table = 'upg_survey_responses'
```

---


## File: surveys\urls.py

**Location:** `surveys\urls.py`

```python
from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('household/create/', views.household_survey_create, name='household_survey_create'),
    path('business/create/', views.business_survey_create, name='business_survey_create'),
    path('household/<int:pk>/', views.household_survey_detail, name='household_survey_detail'),
    path('business/<int:pk>/', views.business_survey_detail, name='business_survey_detail'),
    path('household/<int:pk>/edit/', views.household_survey_edit, name='household_survey_edit'),
    path('business/<int:pk>/edit/', views.business_survey_edit, name='business_survey_edit'),
]
```

---


## File: surveys\views.py

**Location:** `surveys\views.py`

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from households.models import HouseholdSurvey, Household
from business_groups.models import BusinessProgressSurvey, BusinessGroup

@login_required
def survey_list(request):
    """Surveys list view"""
    household_surveys = HouseholdSurvey.objects.all().order_by('-survey_date')
    business_surveys = BusinessProgressSurvey.objects.all().order_by('-survey_date')

    context = {
        'household_surveys': household_surveys,
        'business_surveys': business_surveys,
        'page_title': 'Surveys',
    }

    return render(request, 'surveys/survey_list.html', context)

@login_required
def household_survey_create(request):
    """Create household survey - M&E Staff and Admin only"""
    # Check permissions - only M&E staff, ICT admin, and superusers can create surveys
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['me_staff', 'ict_admin']):
        return HttpResponseForbidden("You do not have permission to create surveys. Only M&E staff and system administrators can create surveys and forms.")

    if request.method == 'POST':
        household_id = request.POST.get('household')
        survey_type = request.POST.get('survey_type', 'General')
        notes = request.POST.get('notes', '')

        if household_id:
            household = get_object_or_404(Household, pk=household_id)
            from django.utils import timezone
            survey = HouseholdSurvey.objects.create(
                household=household,
                survey_type=survey_type,
                name=f"{survey_type} Survey",
                survey_date=timezone.now().date(),
                surveyor=request.user
            )
            messages.success(request, f'Household survey created for {household.name}!')
            return redirect('surveys:household_survey_detail', pk=survey.pk)
        else:
            messages.error(request, 'Please select a household.')

    households = Household.objects.all().order_by('name')
    context = {
        'households': households,
        'page_title': 'New Household Survey',
    }
    return render(request, 'surveys/household_survey_create.html', context)

@login_required
def business_survey_create(request):
    """Create business survey - M&E Staff and Admin only"""
    # Check permissions - only M&E staff, ICT admin, and superusers can create surveys
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['me_staff', 'ict_admin']):
        return HttpResponseForbidden("You do not have permission to create surveys. Only M&E staff and system administrators can create surveys and forms.")

    if request.method == 'POST':
        business_group_id = request.POST.get('business_group')
        notes = request.POST.get('notes', '')

        if business_group_id:
            business_group = get_object_or_404(BusinessGroup, pk=business_group_id)
            from django.utils import timezone
            survey = BusinessProgressSurvey.objects.create(
                business_group=business_group,
                survey_date=timezone.now().date(),
                surveyor=request.user
            )
            messages.success(request, f'Business survey created for {business_group.name}!')
            return redirect('surveys:business_survey_detail', pk=survey.pk)
        else:
            messages.error(request, 'Please select a business group.')

    business_groups = BusinessGroup.objects.all().order_by('name')
    context = {
        'business_groups': business_groups,
        'page_title': 'New Business Survey',
    }
    return render(request, 'surveys/business_survey_create.html', context)

@login_required
def household_survey_detail(request, pk):
    """Household survey detail"""
    survey = get_object_or_404(HouseholdSurvey, pk=pk)
    context = {
        'survey': survey,
        'page_title': f'Household Survey - {survey.household.name}',
    }
    return render(request, 'surveys/household_survey_detail.html', context)

@login_required
def business_survey_detail(request, pk):
    """Business survey detail"""
    survey = get_object_or_404(BusinessProgressSurvey, pk=pk)
    context = {
        'survey': survey,
        'page_title': f'Business Survey - {survey.business_group.name}',
    }
    return render(request, 'surveys/business_survey_detail.html', context)

@login_required
def household_survey_edit(request, pk):
    """Edit household survey - M&E Staff and Admin only"""
    # Check permissions - only M&E staff, ICT admin, and superusers can edit surveys
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['me_staff', 'ict_admin']):
        return HttpResponseForbidden("You do not have permission to edit surveys. Only M&E staff and system administrators can edit surveys and forms.")

    survey = get_object_or_404(HouseholdSurvey, pk=pk)

    if request.method == 'POST':
        survey.survey_type = request.POST.get('survey_type', survey.survey_type)
        survey.notes = request.POST.get('notes', survey.notes)
        survey.save()
        messages.success(request, 'Survey updated successfully!')
        return redirect('surveys:household_survey_detail', pk=survey.pk)

    context = {
        'survey': survey,
        'page_title': f'Edit Survey - {survey.household.name}',
    }
    return render(request, 'surveys/household_survey_edit.html', context)

@login_required
def business_survey_edit(request, pk):
    """Edit business survey - M&E Staff and Admin only"""
    # Check permissions - only M&E staff, ICT admin, and superusers can edit surveys
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['me_staff', 'ict_admin']):
        return HttpResponseForbidden("You do not have permission to edit surveys. Only M&E staff and system administrators can edit surveys and forms.")

    survey = get_object_or_404(BusinessProgressSurvey, pk=pk)

    if request.method == 'POST':
        survey.notes = request.POST.get('notes', survey.notes)
        survey.save()
        messages.success(request, 'Survey updated successfully!')
        return redirect('surveys:business_survey_detail', pk=survey.pk)

    context = {
        'survey': survey,
        'page_title': f'Edit Survey - {survey.business_group.name}',
    }
    return render(request, 'surveys/business_survey_edit.html', context)
```

---


## File: training\__init__.py

**Location:** `training\__init__.py`

```python
# Training App
```

---


## File: training\mentoring_views.py

**Location:** `training\mentoring_views.py`

```python
"""
Mentoring Report Views for UPG System
Comprehensive mentoring activity tracking and reporting
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
import csv
import json
from django.core.paginator import Paginator

from .models import (
    MentoringReport, MentoringVisit, PhoneNudge, Training,
    TrainingAttendance, HouseholdTrainingEnrollment
)
from core.models import Mentor, BusinessMentorCycle
from households.models import Household, HouseholdProgram
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def mentoring_dashboard(request):
    """Comprehensive mentoring activities dashboard"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to access mentoring reports.')
        return redirect('dashboard:dashboard')

    # Filter data based on user role
    if user_role == 'mentor':
        mentor_filter = Q(mentor=request.user)
        # Filter by assigned villages to only show related households
        if hasattr(request.user, 'profile') and request.user.profile:
            assigned_villages = request.user.profile.assigned_villages.all()
            visits = MentoringVisit.objects.filter(
                mentor=request.user,
                household__village__in=assigned_villages
            )
            phone_nudges = PhoneNudge.objects.filter(
                mentor=request.user,
                household__village__in=assigned_villages
            )
            # MentoringReport doesn't have household field - filter by mentor only
            mentoring_reports = MentoringReport.objects.filter(
                mentor=request.user
            )
            # Training doesn't have village field - filter by assigned mentor only
            trainings = Training.objects.filter(
                assigned_mentor=request.user
            )
        else:
            # No profile or assigned villages - show no data
            visits = MentoringVisit.objects.none()
            phone_nudges = PhoneNudge.objects.none()
            mentoring_reports = MentoringReport.objects.filter(mentor=request.user)
            trainings = Training.objects.none()
    else:
        mentor_filter = Q()
        visits = MentoringVisit.objects.all()
        phone_nudges = PhoneNudge.objects.all()
        mentoring_reports = MentoringReport.objects.all()
        trainings = Training.objects.all()

    # Current month statistics
    current_month = timezone.now().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)

    monthly_stats = {
        'visits_this_month': visits.filter(visit_date__gte=current_month, visit_date__lt=next_month).count(),
        'phone_nudges_this_month': phone_nudges.filter(call_date__gte=current_month, call_date__lt=next_month).count(),
        'trainings_this_month': trainings.filter(start_date__gte=current_month, start_date__lt=next_month).count(),
        'active_households': visits.filter(visit_date__gte=current_month).values('household').distinct().count(),
    }

    # Recent activities - order by creation time to show most recently logged items
    recent_visits = visits.order_by('-created_at')[:10]
    recent_phone_nudges = phone_nudges.order_by('-created_at')[:10]
    recent_reports = mentoring_reports.order_by('-submitted_date')[:5]

    # Mentor performance overview
    mentor_stats = []
    if user_role != 'mentor':
        mentors = User.objects.filter(role='mentor')
        for mentor in mentors:
            stats = {
                'mentor': mentor,
                'visits_count': MentoringVisit.objects.filter(mentor=mentor, visit_date__gte=current_month).count(),
                'phone_nudges_count': PhoneNudge.objects.filter(mentor=mentor, call_date__gte=current_month).count(),
                'active_households': MentoringVisit.objects.filter(
                    mentor=mentor, visit_date__gte=current_month
                ).values('household').distinct().count(),
                'avg_call_duration': PhoneNudge.objects.filter(
                    mentor=mentor, call_date__gte=current_month
                ).aggregate(avg_duration=Avg('duration_minutes'))['avg_duration'] or 0,
            }
            mentor_stats.append(stats)

    # Visit type distribution
    visit_type_stats = visits.filter(visit_date__gte=current_month).values('visit_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Phone nudge type distribution
    nudge_type_stats = phone_nudges.filter(call_date__gte=current_month).values('nudge_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Available grants for mentors to apply on behalf of households
    available_grants = []
    if user_role == 'mentor':
        from programs.models import Program
        from upg_grants.models import HouseholdGrantApplication

        # Get all active programs as available grant opportunities
        active_programs = Program.objects.filter(status='active')

        # Get grant type choices
        grant_types = HouseholdGrantApplication.GRANT_TYPE_CHOICES

        available_grants = {
            'programs': active_programs,
            'grant_types': grant_types,
        }

    context = {
        'page_title': 'Mentoring Dashboard',
        'monthly_stats': monthly_stats,
        'recent_visits': recent_visits,
        'recent_phone_nudges': recent_phone_nudges,
        'recent_reports': recent_reports,
        'mentor_stats': mentor_stats,
        'visit_type_stats': visit_type_stats,
        'nudge_type_stats': nudge_type_stats,
        'user_role': user_role,
        'current_month': current_month.strftime('%B %Y'),
        'available_grants': available_grants,
    }

    return render(request, 'training/mentoring_dashboard.html', context)


@login_required
def mentoring_reports(request):
    """View and manage mentoring reports"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to access mentoring reports.')
        return redirect('dashboard:dashboard')

    # Filter reports based on user role
    if user_role == 'mentor':
        reports = MentoringReport.objects.filter(mentor=request.user)
    else:
        reports = MentoringReport.objects.all()

    # Apply filters
    mentor_filter = request.GET.get('mentor')
    period_filter = request.GET.get('period')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if mentor_filter:
        reports = reports.filter(mentor_id=mentor_filter)
    if period_filter:
        reports = reports.filter(reporting_period=period_filter)
    if date_from:
        reports = reports.filter(period_start__gte=date_from)
    if date_to:
        reports = reports.filter(period_end__lte=date_to)

    reports = reports.order_by('-submitted_date')

    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get mentors for filter dropdown (only if not a mentor)
    mentors = []
    if user_role != 'mentor':
        mentors = User.objects.filter(role='mentor').order_by('first_name', 'last_name')

    context = {
        'page_title': 'Mentoring Reports',
        'page_obj': page_obj,
        'mentors': mentors,
        'user_role': user_role,
        'current_filters': {
            'mentor': mentor_filter,
            'period': period_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }

    return render(request, 'training/mentoring_reports.html', context)


@login_required
def create_mentoring_report(request):
    """Create a new mentoring report"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if user_role != 'mentor':
        messages.error(request, 'Only mentors can create mentoring reports.')
        return redirect('training:mentoring_reports')

    if request.method == 'POST':
        try:
            # Extract form data
            reporting_period = request.POST.get('reporting_period')
            period_start = request.POST.get('period_start')
            period_end = request.POST.get('period_end')
            key_activities = request.POST.get('key_activities')
            challenges_faced = request.POST.get('challenges_faced', '')
            successes_achieved = request.POST.get('successes_achieved', '')
            next_period_plans = request.POST.get('next_period_plans', '')

            # Convert dates
            period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
            period_end = datetime.strptime(period_end, '%Y-%m-%d').date()

            # Calculate statistics automatically
            visits_count = MentoringVisit.objects.filter(
                mentor=request.user,
                visit_date__gte=period_start,
                visit_date__lte=period_end
            ).count()

            phone_nudges_count = PhoneNudge.objects.filter(
                mentor=request.user,
                call_date__gte=period_start,
                call_date__lte=period_end
            ).count()

            trainings_count = Training.objects.filter(
                assigned_mentor=request.user,
                start_date__gte=period_start,
                start_date__lte=period_end
            ).count()

            households_visited = MentoringVisit.objects.filter(
                mentor=request.user,
                visit_date__gte=period_start,
                visit_date__lte=period_end
            ).values('household').distinct().count()

            # Create the report
            report = MentoringReport.objects.create(
                mentor=request.user,
                reporting_period=reporting_period,
                period_start=period_start,
                period_end=period_end,
                households_visited=households_visited,
                phone_nudges_made=phone_nudges_count,
                trainings_conducted=trainings_count,
                new_households_enrolled=0,  # This would need additional logic
                key_activities=key_activities,
                challenges_faced=challenges_faced,
                successes_achieved=successes_achieved,
                next_period_plans=next_period_plans,
            )

            messages.success(request, 'Mentoring report created successfully.')
            return redirect('training:mentoring_report_detail', report_id=report.id)

        except Exception as e:
            messages.error(request, f'Error creating report: {str(e)}')

    context = {
        'page_title': 'Create Mentoring Report',
        'reporting_periods': MentoringReport.REPORTING_PERIOD_CHOICES,
    }

    return render(request, 'training/create_mentoring_report.html', context)


@login_required
def mentoring_report_detail(request, report_id):
    """View detailed mentoring report"""
    report = get_object_or_404(MentoringReport, id=report_id)

    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if user_role == 'mentor' and report.mentor != request.user:
        messages.error(request, 'You can only view your own reports.')
        return redirect('training:mentoring_reports')

    # Get related activities for the report period
    visits = MentoringVisit.objects.filter(
        mentor=report.mentor,
        visit_date__gte=report.period_start,
        visit_date__lte=report.period_end
    ).order_by('-visit_date')

    phone_nudges = PhoneNudge.objects.filter(
        mentor=report.mentor,
        call_date__gte=report.period_start,
        call_date__lte=report.period_end
    ).order_by('-call_date')

    trainings = Training.objects.filter(
        assigned_mentor=report.mentor,
        start_date__gte=report.period_start,
        start_date__lte=report.period_end
    ).order_by('-start_date')

    context = {
        'page_title': f'Mentoring Report - {report.period_start} to {report.period_end}',
        'report': report,
        'visits': visits,
        'phone_nudges': phone_nudges,
        'trainings': trainings,
    }

    return render(request, 'training/mentoring_report_detail.html', context)


@login_required
def mentoring_analytics(request):
    """Advanced mentoring analytics and insights"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        messages.error(request, 'You do not have permission to access mentoring analytics.')
        return redirect('dashboard:dashboard')

    # Time period filter
    days_back = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days_back)

    # Overall statistics
    total_mentors = User.objects.filter(role='mentor').count()
    total_visits = MentoringVisit.objects.filter(visit_date__gte=start_date).count()
    total_phone_nudges = PhoneNudge.objects.filter(call_date__gte=start_date).count()
    total_households_reached = MentoringVisit.objects.filter(
        visit_date__gte=start_date
    ).values('household').distinct().count()

    # Mentor performance ranking
    mentor_performance = []
    mentors = User.objects.filter(role='mentor')
    for mentor in mentors:
        visits_count = MentoringVisit.objects.filter(
            mentor=mentor, visit_date__gte=start_date
        ).count()
        nudges_count = PhoneNudge.objects.filter(
            mentor=mentor, call_date__gte=start_date
        ).count()
        households_count = MentoringVisit.objects.filter(
            mentor=mentor, visit_date__gte=start_date
        ).values('household').distinct().count()

        performance_score = (visits_count * 2) + nudges_count + (households_count * 3)

        mentor_performance.append({
            'mentor': mentor,
            'visits': visits_count,
            'nudges': nudges_count,
            'households': households_count,
            'score': performance_score,
        })

    mentor_performance.sort(key=lambda x: x['score'], reverse=True)

    # Monthly trend data
    monthly_data = []
    for i in range(6):  # Last 6 months
        month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        visits = MentoringVisit.objects.filter(
            visit_date__gte=month_start, visit_date__lte=month_end
        ).count()
        nudges = PhoneNudge.objects.filter(
            call_date__gte=month_start, call_date__lte=month_end
        ).count()

        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'visits': visits,
            'nudges': nudges,
        })

    monthly_data.reverse()

    # Visit type analysis
    visit_types = MentoringVisit.objects.filter(
        visit_date__gte=start_date
    ).values('visit_type').annotate(count=Count('id')).order_by('-count')

    # Average call duration by nudge type
    nudge_duration_stats = PhoneNudge.objects.filter(
        call_date__gte=start_date
    ).values('nudge_type').annotate(
        avg_duration=Avg('duration_minutes'),
        total_calls=Count('id')
    ).order_by('-avg_duration')

    context = {
        'page_title': 'Mentoring Analytics',
        'total_mentors': total_mentors,
        'total_visits': total_visits,
        'total_phone_nudges': total_phone_nudges,
        'total_households_reached': total_households_reached,
        'mentor_performance': mentor_performance[:10],  # Top 10
        'monthly_data': monthly_data,
        'visit_types': visit_types,
        'nudge_duration_stats': nudge_duration_stats,
        'days_back': days_back,
        'start_date': start_date,
    }

    return render(request, 'training/mentoring_analytics.html', context)


@login_required
def export_mentoring_reports(request):
    """Export mentoring reports to CSV"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate']):
        return HttpResponse('Permission denied', status=403)

    # Filter reports
    reports = MentoringReport.objects.all().order_by('-submitted_date')

    # Apply filters if provided
    mentor_filter = request.GET.get('mentor')
    period_filter = request.GET.get('period')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if mentor_filter:
        reports = reports.filter(mentor_id=mentor_filter)
    if period_filter:
        reports = reports.filter(reporting_period=period_filter)
    if date_from:
        reports = reports.filter(period_start__gte=date_from)
    if date_to:
        reports = reports.filter(period_end__lte=date_to)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mentoring_reports_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'Mentor Name', 'Reporting Period', 'Period Start', 'Period End',
        'Households Visited', 'Phone Nudges Made', 'Trainings Conducted',
        'New Households Enrolled', 'Key Activities', 'Challenges Faced',
        'Successes Achieved', 'Next Period Plans', 'Submitted Date'
    ])

    # Write data rows
    for report in reports:
        writer.writerow([
            report.mentor.get_full_name(),
            report.get_reporting_period_display(),
            report.period_start.strftime('%Y-%m-%d'),
            report.period_end.strftime('%Y-%m-%d'),
            report.households_visited,
            report.phone_nudges_made,
            report.trainings_conducted,
            report.new_households_enrolled,
            report.key_activities,
            report.challenges_faced,
            report.successes_achieved,
            report.next_period_plans,
            report.submitted_date.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@login_required
def log_visit(request):
    """Log a new mentoring visit"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if user_role not in ['mentor', 'field_associate']:
        messages.error(request, 'Only mentors and field associates can log visits.')
        return redirect('training:mentoring_dashboard')

    if request.method == 'POST':
        try:
            # Extract form data
            household_id = request.POST.get('household')
            name = request.POST.get('name')
            topic = request.POST.get('topic')
            visit_type = request.POST.get('visit_type')
            visit_date = request.POST.get('visit_date')
            notes = request.POST.get('notes', '')

            # Validate household
            household = get_object_or_404(Household, id=household_id)

            # Convert date
            visit_date = datetime.strptime(visit_date, '%Y-%m-%d').date()

            # Create the visit
            visit = MentoringVisit.objects.create(
                name=name,
                household=household,
                mentor=request.user,
                topic=topic,
                visit_type=visit_type,
                visit_date=visit_date,
                notes=notes,
            )

            messages.success(request, f'Visit "{name}" to {household.name} logged successfully on {visit_date}.')
            return redirect('training:mentoring_dashboard')

        except Exception as e:
            messages.error(request, f'Error logging visit: {str(e)}')
            # Continue to render the form with the error message

    # Get households for the mentor (if they have assigned villages)
    households = Household.objects.all().order_by('name')

    # Filter households if mentor has assigned villages
    if hasattr(request.user, 'profile') and request.user.profile:
        assigned_villages = request.user.profile.assigned_villages.all()
        if assigned_villages:
            households = households.filter(village__in=assigned_villages)

    context = {
        'page_title': 'Log Visit',
        'households': households,
        'visit_types': MentoringVisit.VISIT_TYPE_CHOICES,
    }

    return render(request, 'training/log_visit.html', context)


@login_required
def log_phone_nudge(request):
    """Log a new phone nudge"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if user_role not in ['mentor', 'field_associate']:
        messages.error(request, 'Only mentors and field associates can log phone nudges.')
        return redirect('training:mentoring_dashboard')

    if request.method == 'POST':
        try:
            # Extract form data
            household_id = request.POST.get('household')
            nudge_type = request.POST.get('nudge_type')
            call_date = request.POST.get('call_date')
            call_time = request.POST.get('call_time')
            duration_minutes = request.POST.get('duration_minutes')
            duration_seconds = request.POST.get('duration_seconds', '0')  # For auto-tracked duration
            notes = request.POST.get('notes', '')
            successful_contact = request.POST.get('successful_contact') == 'on'

            # Validate household
            household = get_object_or_404(Household, id=household_id)

            # Convert datetime to timezone-aware
            naive_datetime = datetime.strptime(f'{call_date} {call_time}', '%Y-%m-%d %H:%M')
            call_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())

            # Calculate duration in minutes (use seconds if provided)
            if duration_seconds and int(duration_seconds) > 0:
                calculated_duration = int(duration_seconds) // 60
                if calculated_duration == 0 and int(duration_seconds) > 0:
                    calculated_duration = 1  # Minimum 1 minute for calls with duration
            else:
                calculated_duration = int(duration_minutes) if duration_minutes else 0

            # Create the phone nudge
            phone_nudge = PhoneNudge.objects.create(
                household=household,
                mentor=request.user,
                nudge_type=nudge_type,
                call_date=call_datetime,
                duration_minutes=calculated_duration,
                notes=notes,
                successful_contact=successful_contact,
            )

            messages.success(request, f'Phone nudge to {household.name} logged successfully.')
            return redirect('training:mentoring_dashboard')

        except Exception as e:
            messages.error(request, f'Error logging phone nudge: {str(e)}')

    # Get households for the mentor
    households = Household.objects.all().order_by('name')

    # Filter households if mentor has assigned villages
    if hasattr(request.user, 'profile') and request.user.profile:
        assigned_villages = request.user.profile.assigned_villages.all()
        if assigned_villages:
            households = households.filter(village__in=assigned_villages)

    context = {
        'page_title': 'Log Phone Nudge',
        'households': households,
        'nudge_types': PhoneNudge.NUDGE_TYPE_CHOICES,
    }

    return render(request, 'training/log_phone_nudge.html', context)


@login_required
def visit_list(request):
    """View all visits with filtering options"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to view visits.')
        return redirect('dashboard:dashboard')

    # Filter visits based on user role
    if user_role == 'mentor':
        visits = MentoringVisit.objects.filter(mentor=request.user)
    else:
        visits = MentoringVisit.objects.all()

    # Apply filters
    household_filter = request.GET.get('household')
    mentor_filter = request.GET.get('mentor')
    visit_type_filter = request.GET.get('visit_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if household_filter:
        visits = visits.filter(household_id=household_filter)
    if mentor_filter:
        visits = visits.filter(mentor_id=mentor_filter)
    if visit_type_filter:
        visits = visits.filter(visit_type=visit_type_filter)
    if date_from:
        visits = visits.filter(visit_date__gte=date_from)
    if date_to:
        visits = visits.filter(visit_date__lte=date_to)

    visits = visits.order_by('-visit_date').select_related('household', 'mentor')

    # Pagination
    paginator = Paginator(visits, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    households = Household.objects.all().order_by('name')
    mentors = []
    if user_role != 'mentor':
        mentors = User.objects.filter(role='mentor').order_by('first_name', 'last_name')

    context = {
        'page_title': 'Mentoring Visits',
        'page_obj': page_obj,
        'households': households,
        'mentors': mentors,
        'visit_types': MentoringVisit.VISIT_TYPE_CHOICES,
        'user_role': user_role,
        'current_filters': {
            'household': household_filter,
            'mentor': mentor_filter,
            'visit_type': visit_type_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }

    return render(request, 'training/visit_list.html', context)


@login_required
def phone_nudge_list(request):
    """View all phone nudges with filtering options"""
    # Check permissions
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to view phone nudges.')
        return redirect('dashboard:dashboard')

    # Filter phone nudges based on user role
    if user_role == 'mentor':
        phone_nudges = PhoneNudge.objects.filter(mentor=request.user)
    else:
        phone_nudges = PhoneNudge.objects.all()

    # Apply filters
    household_filter = request.GET.get('household')
    mentor_filter = request.GET.get('mentor')
    nudge_type_filter = request.GET.get('nudge_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    contact_status = request.GET.get('contact_status')

    if household_filter:
        phone_nudges = phone_nudges.filter(household_id=household_filter)
    if mentor_filter:
        phone_nudges = phone_nudges.filter(mentor_id=mentor_filter)
    if nudge_type_filter:
        phone_nudges = phone_nudges.filter(nudge_type=nudge_type_filter)
    if date_from:
        phone_nudges = phone_nudges.filter(call_date__gte=date_from)
    if date_to:
        phone_nudges = phone_nudges.filter(call_date__lte=date_to)
    if contact_status == 'successful':
        phone_nudges = phone_nudges.filter(successful_contact=True)
    elif contact_status == 'unsuccessful':
        phone_nudges = phone_nudges.filter(successful_contact=False)

    phone_nudges = phone_nudges.order_by('-call_date').select_related('household', 'mentor')

    # Pagination
    paginator = Paginator(phone_nudges, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    households = Household.objects.all().order_by('name')
    mentors = []
    if user_role != 'mentor':
        mentors = User.objects.filter(role='mentor').order_by('first_name', 'last_name')

    # Calculate statistics
    total_calls = phone_nudges.count()
    successful_calls = phone_nudges.filter(successful_contact=True).count()
    avg_duration = phone_nudges.aggregate(avg_duration=Avg('duration_minutes'))['avg_duration'] or 0

    context = {
        'page_title': 'Phone Nudges',
        'page_obj': page_obj,
        'households': households,
        'mentors': mentors,
        'nudge_types': PhoneNudge.NUDGE_TYPE_CHOICES,
        'user_role': user_role,
        'total_calls': total_calls,
        'successful_calls': successful_calls,
        'avg_duration': avg_duration,
        'current_filters': {
            'household': household_filter,
            'mentor': mentor_filter,
            'nudge_type': nudge_type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'contact_status': contact_status,
        }
    }

    return render(request, 'training/phone_nudge_list.html', context)
```

---


## File: training\models.py

**Location:** `training\models.py`

```python
"""
Training and Mentoring Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from households.models import Household
from core.models import BusinessMentorCycle

User = get_user_model()


class Training(models.Model):
    """
    Training modules and sessions associated with BM Cycles
    """
    TRAINING_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    module_id = models.CharField(max_length=50)
    module_number = models.IntegerField(help_text="Sequential module number (1, 2, 3, etc.)", null=True, blank=True)
    bm_cycle = models.ForeignKey(BusinessMentorCycle, on_delete=models.CASCADE, related_name='trainings', null=True, blank=True)
    assigned_mentor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mentor'}, null=True, blank=True)

    # Enhanced training details from meeting notes
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, help_text="Training length in hours", null=True, blank=True)
    location = models.CharField(max_length=200, help_text="Training location/venue", blank=True)
    participant_count = models.IntegerField(help_text="Actual number of participants", null=True, blank=True)

    time_taken = models.DurationField(help_text="Training duration", null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TRAINING_STATUS_CHOICES, default='planned')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    training_dates = models.JSONField(default=list, blank=True, help_text="List of specific training session dates")
    max_households = models.IntegerField(default=25, help_text="Maximum households per training")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.bm_cycle.bm_cycle_name}"

    @property
    def enrolled_households_count(self):
        return self.attendances.values('household').distinct().count()

    @property
    def available_slots(self):
        return self.max_households - self.enrolled_households_count

    class Meta:
        db_table = 'upg_trainings'


class TrainingAttendance(models.Model):
    """
    Training attendance tracking
    """
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='attendances')
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    attendance = models.BooleanField(default=True)
    training_date = models.DateField()

    # Track who marked attendance and when
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='marked_attendances',
                                 help_text="Mentor who marked this attendance")
    attendance_marked_at = models.DateTimeField(null=True, blank=True,
                                              help_text="When attendance was last updated")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.training.name}"

    class Meta:
        db_table = 'upg_training_attendances'


class MentoringVisit(models.Model):
    """
    Mentoring visit tracking
    """
    VISIT_TYPE_CHOICES = [
        ('on_site', 'On-site'),
        ('phone', 'Phone Check'),
        ('virtual', 'Virtual'),
    ]

    name = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='mentoring_visits')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='on_site')
    visit_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.household.name}"

    class Meta:
        db_table = 'upg_mentoring_visits'


class PhoneNudge(models.Model):
    """
    Phone nudges/calls made by mentors to households
    """
    NUDGE_TYPE_CHOICES = [
        ('reminder', 'Training Reminder'),
        ('follow_up', 'Follow-up Call'),
        ('support', 'Support Call'),
        ('check_in', 'Regular Check-in'),
        ('business_advice', 'Business Advice'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='phone_nudges')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    nudge_type = models.CharField(max_length=20, choices=NUDGE_TYPE_CHOICES)
    call_date = models.DateTimeField()
    duration_minutes = models.IntegerField(help_text="Call duration in minutes")
    notes = models.TextField(blank=True)
    successful_contact = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_nudge_type_display()} - {self.household.name}"

    class Meta:
        db_table = 'upg_phone_nudges'


class MentoringReport(models.Model):
    """
    Weekly/Monthly mentoring reports by mentors
    """
    REPORTING_PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    reporting_period = models.CharField(max_length=20, choices=REPORTING_PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Summary statistics
    households_visited = models.IntegerField(default=0)
    phone_nudges_made = models.IntegerField(default=0)
    trainings_conducted = models.IntegerField(default=0)
    new_households_enrolled = models.IntegerField(default=0)

    # Narrative report
    key_activities = models.TextField(help_text="Key activities during the period")
    challenges_faced = models.TextField(blank=True)
    successes_achieved = models.TextField(blank=True)
    next_period_plans = models.TextField(blank=True)

    submitted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.get_full_name()} - {self.reporting_period} - {self.period_start}"

    class Meta:
        db_table = 'upg_mentoring_reports'
        unique_together = ['mentor', 'reporting_period', 'period_start']


class HouseholdTrainingEnrollment(models.Model):
    """
    Tracks household enrollment in trainings (one household per training rule)
    """
    household = models.OneToOneField(Household, on_delete=models.CASCADE, related_name='current_training_enrollment')
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='enrolled_households')
    enrolled_date = models.DateField()
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Enrolled'),
            ('completed', 'Completed'),
            ('dropped_out', 'Dropped Out'),
            ('transferred', 'Transferred'),
        ],
        default='enrolled'
    )
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.training.name}"

    class Meta:
        db_table = 'upg_household_training_enrollments'
```

---


## File: training\urls.py

**Location:** `training\urls.py`

```python
from django.urls import path
from . import views
from . import mentoring_views

app_name = 'training'

urlpatterns = [
    # Training URLs
    path('', views.training_list, name='training_list'),
    path('create/', views.create_training, name='create_training'),
    path('<int:training_id>/details/', views.training_details, name='training_details'),
    path('<int:training_id>/edit/', views.edit_training, name='edit_training'),
    path('<int:training_id>/start/', views.start_training, name='start_training'),
    path('<int:training_id>/complete/', views.complete_training, name='complete_training'),
    path('<int:training_id>/delete/', views.delete_training, name='delete_training'),
    path('<int:training_id>/attendance/', views.manage_attendance, name='manage_attendance'),
    path('<int:training_id>/available-households/', views.get_available_households, name='get_available_households'),
    path('<int:training_id>/add-household/', views.add_household_to_training, name='add_household_to_training'),
    path('attendance/<int:attendance_id>/toggle/', views.toggle_attendance, name='toggle_attendance'),
    path('attendance/<int:attendance_id>/remove/', views.remove_attendance, name='remove_attendance'),

    # Mentoring URLs
    path('mentoring/', mentoring_views.mentoring_dashboard, name='mentoring_dashboard'),
    path('mentoring/reports/', mentoring_views.mentoring_reports, name='mentoring_reports'),
    path('mentoring/reports/create/', mentoring_views.create_mentoring_report, name='create_mentoring_report'),
    path('mentoring/reports/<int:report_id>/', mentoring_views.mentoring_report_detail, name='mentoring_report_detail'),
    path('mentoring/analytics/', mentoring_views.mentoring_analytics, name='mentoring_analytics'),
    path('mentoring/reports/export/', mentoring_views.export_mentoring_reports, name='export_mentoring_reports'),

    # Visit Logging URLs
    path('mentoring/visits/', mentoring_views.visit_list, name='visit_list'),
    path('mentoring/visits/log/', mentoring_views.log_visit, name='log_visit'),
    path('mentoring/phone-nudges/', mentoring_views.phone_nudge_list, name='phone_nudge_list'),
    path('mentoring/phone-nudges/log/', mentoring_views.log_phone_nudge, name='log_phone_nudge'),
]
```

---


## File: training\views.py

**Location:** `training\views.py`

```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Training, TrainingAttendance
from households.models import Household

@login_required
def training_list(request):
    """Training Sessions list view with role-based filtering"""
    user = request.user

    # Filter trainings based on user role
    if user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate']:
        # Full access to all trainings
        training_sessions = Training.objects.all()
    elif user.role == 'mentor':
        # Mentors only see trainings they're assigned to
        training_sessions = Training.objects.filter(assigned_mentor=user)
    else:
        # Other roles have no access to trainings
        training_sessions = Training.objects.none()

    training_sessions = training_sessions.order_by('-created_at')

    context = {
        'training_sessions': training_sessions,
        'page_title': 'Training Sessions',
        'total_count': training_sessions.count(),
    }

    return render(request, 'training/training_list.html', context)

@login_required
def training_details(request, training_id):
    """Training details page"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return HttpResponseForbidden()

    # Get related data
    attendances = training.attendances.select_related('household__village', 'marked_by').order_by('household__name')

    # Calculate training statistics
    total_enrolled = attendances.count()
    present_count = attendances.filter(attendance=True).count()
    absent_count = total_enrolled - present_count
    attendance_rate = round((present_count * 100) / total_enrolled) if total_enrolled > 0 else 0
    enrollment_rate = round((total_enrolled * 100) / training.max_households) if training.max_households > 0 else 0

    # Get recent activity (last 10 attendance changes)
    recent_activity = attendances.filter(attendance_marked_at__isnull=False).order_by('-attendance_marked_at')[:10]

    context = {
        'training': training,
        'attendances': attendances,
        'page_title': f'Training Details - {training.name}',
        'total_enrolled': total_enrolled,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate,
        'enrollment_rate': enrollment_rate,
        'recent_activity': recent_activity,
    }

    return render(request, 'training/training_details.html', context)

@login_required
@require_http_methods(["POST"])
def start_training(request, training_id):
    """AJAX endpoint to start a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if training.status != 'planned':
        return JsonResponse({'success': False, 'message': 'Training can only be started if it is in planned status'})

    training.status = 'active'
    if not training.start_date:
        training.start_date = timezone.now().date()
    training.save()

    return JsonResponse({'success': True, 'message': 'Training started successfully'})

@login_required
@require_http_methods(["POST"])
def complete_training(request, training_id):
    """AJAX endpoint to complete a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if training.status != 'active':
        return JsonResponse({'success': False, 'message': 'Training can only be completed if it is active'})

    training.status = 'completed'
    if not training.end_date:
        training.end_date = timezone.now().date()
    training.save()

    return JsonResponse({'success': True, 'message': 'Training completed successfully'})

@login_required
@require_http_methods(["DELETE"])
def delete_training(request, training_id):
    """AJAX endpoint to delete a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions - only admin roles can delete
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    # Check if training has attendances
    if training.attendances.exists():
        return JsonResponse({'success': False, 'message': 'Cannot delete training with existing attendance records'})

    training_name = training.name
    training.delete()

    return JsonResponse({'success': True, 'message': f'Training "{training_name}" deleted successfully'})

@login_required
def manage_attendance(request, training_id):
    """Training attendance management interface with daily attendance support"""
    from datetime import datetime, timedelta

    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return HttpResponseForbidden()

    # Get selected date from request or use today's date
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # Get training dates - if training_dates is set, use it; otherwise use start_date
    training_dates = []
    if training.training_dates and isinstance(training.training_dates, list):
        training_dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) else d for d in training.training_dates]
    elif training.start_date:
        # Generate dates from start to end (or just start date if no end date)
        if training.end_date:
            current_date = training.start_date
            while current_date <= training.end_date:
                training_dates.append(current_date)
                current_date += timedelta(days=1)
        else:
            training_dates = [training.start_date]

    # If no dates configured, use current date
    if not training_dates:
        training_dates = [timezone.now().date()]

    # If selected date not in training dates and training has started, add it
    if selected_date not in training_dates and training.status in ['active', 'completed']:
        training_dates.append(selected_date)
        training_dates.sort()

    # Filter attendances for the selected date
    attendances = training.attendances.filter(training_date=selected_date).select_related('household__village', 'marked_by').order_by('household__name')

    # Get unique households enrolled (from all dates)
    enrolled_households = training.attendances.values_list('household', flat=True).distinct()
    total_unique_enrolled = len(set(enrolled_households))

    # Calculate attendance statistics for selected date
    total_enrolled = attendances.count()
    present_count = attendances.filter(attendance=True).count()
    absent_count = total_enrolled - present_count
    attendance_rate = round((present_count * 100) / total_enrolled) if total_enrolled > 0 else 0

    context = {
        'training': training,
        'attendances': attendances,
        'page_title': f'Manage Attendance - {training.name}',
        'total_enrolled': total_enrolled,
        'total_unique_enrolled': total_unique_enrolled,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate,
        'selected_date': selected_date,
        'training_dates': sorted(training_dates),
    }

    return render(request, 'training/manage_attendance.html', context)

@login_required
@require_http_methods(["POST"])
def create_training(request):
    """Create a new training session"""
    user = request.user

    # Check permissions - mentors can now create/schedule trainings
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor']):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        # Extract form data
        name = request.POST.get('name', '').strip()
        module_id = request.POST.get('module_id', '').strip()
        bm_cycle_id = request.POST.get('bm_cycle')
        assigned_mentor_id = request.POST.get('assigned_mentor')
        start_date = request.POST.get('start_date')
        max_households = request.POST.get('max_households', 25)
        time_taken = request.POST.get('time_taken')
        status = request.POST.get('status', 'planned')
        description = request.POST.get('description', '').strip()

        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Training name is required']
        if not module_id:
            errors['module_id'] = ['Module ID is required']

        # Validate BM Cycle exists if provided
        bm_cycle = None
        if bm_cycle_id:
            try:
                from core.models import BusinessMentorCycle
                bm_cycle = BusinessMentorCycle.objects.get(id=bm_cycle_id)
            except BusinessMentorCycle.DoesNotExist:
                errors['bm_cycle'] = ['Invalid BM Cycle selected']

        # Validate mentor exists if provided
        assigned_mentor = None
        if assigned_mentor_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                assigned_mentor = User.objects.get(id=assigned_mentor_id, role='mentor')
            except User.DoesNotExist:
                errors['assigned_mentor'] = ['Invalid mentor selected']

        # Validate max households
        try:
            max_households = int(max_households)
            if max_households < 1 or max_households > 50:
                errors['max_households'] = ['Max households must be between 1 and 50']
        except (ValueError, TypeError):
            errors['max_households'] = ['Invalid number for max households']

        # Validate duration if provided
        time_taken_obj = None
        if time_taken:
            try:
                from datetime import timedelta
                # Expected format: "HH:MM:SS"
                parts = time_taken.split(':')
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
                seconds = int(parts[2]) if len(parts) > 2 else 0
                time_taken_obj = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except (ValueError, IndexError):
                errors['time_taken'] = ['Invalid duration format']

        # Validate start date if provided
        start_date_obj = None
        if start_date:
            try:
                from datetime import datetime
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                errors['start_date'] = ['Invalid date format']

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        # Create training
        training = Training.objects.create(
            name=name,
            module_id=module_id,
            bm_cycle=bm_cycle,
            assigned_mentor=assigned_mentor,
            time_taken=time_taken_obj,
            description=description,
            status=status,
            start_date=start_date_obj,
            max_households=max_households
        )

        return JsonResponse({
            'success': True,
            'message': f'Training "{training.name}" created successfully',
            'training_id': training.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating training: {str(e)}'
        })


@login_required
def edit_training(request, training_id):
    """Edit an existing training session"""
    training = get_object_or_404(Training, id=training_id)
    user = request.user

    # Check permissions - mentors can edit trainings they're assigned to
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if request.method == 'GET':
        # Return training data for the edit form
        from core.models import BusinessMentorCycle, Mentor
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get available options for form
        bm_cycles = BusinessMentorCycle.objects.all()
        mentors = User.objects.filter(role='mentor')

        # Calculate training statistics
        total_enrolled = training.attendances.count()
        present_count = training.attendances.filter(attendance=True).count()
        completion_rate = round((total_enrolled * 100) / training.max_households) if training.max_households > 0 else 0

        context = {
            'training': training,
            'bm_cycles': bm_cycles,
            'mentors': mentors,
            'page_title': f'Edit Training - {training.name}',
            'present_count': present_count,
            'completion_rate': completion_rate,
        }
        return render(request, 'training/edit_training.html', context)

    elif request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name', '').strip()
            module_id = request.POST.get('module_id', '').strip()
            bm_cycle_id = request.POST.get('bm_cycle')
            assigned_mentor_id = request.POST.get('assigned_mentor')
            start_date = request.POST.get('start_date')
            max_households = request.POST.get('max_households', 25)
            time_taken = request.POST.get('time_taken')
            status = request.POST.get('status', training.status)
            description = request.POST.get('description', '').strip()
            module_number = request.POST.get('module_number')
            duration_hours = request.POST.get('duration_hours')
            location = request.POST.get('location', '').strip()
            participant_count = request.POST.get('participant_count')

            # Validation
            errors = {}
            if not name:
                errors['name'] = ['Training name is required']
            if not module_id:
                errors['module_id'] = ['Module ID is required']

            # Validate BM Cycle exists if provided
            bm_cycle = None
            if bm_cycle_id:
                try:
                    from core.models import BusinessMentorCycle
                    bm_cycle = BusinessMentorCycle.objects.get(id=bm_cycle_id)
                except BusinessMentorCycle.DoesNotExist:
                    errors['bm_cycle'] = ['Invalid BM Cycle selected']

            # Validate mentor exists if provided
            assigned_mentor = None
            if assigned_mentor_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    assigned_mentor = User.objects.get(id=assigned_mentor_id, role='mentor')
                except User.DoesNotExist:
                    errors['assigned_mentor'] = ['Invalid mentor selected']

            # Validate max households
            try:
                max_households = int(max_households)
                if max_households < 1 or max_households > 50:
                    errors['max_households'] = ['Max households must be between 1 and 50']
            except (ValueError, TypeError):
                errors['max_households'] = ['Invalid number for max households']

            # Validate duration if provided
            time_taken_obj = None
            if time_taken:
                try:
                    from datetime import timedelta
                    # Expected format: "HH:MM:SS"
                    parts = time_taken.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1]) if len(parts) > 1 else 0
                    seconds = int(parts[2]) if len(parts) > 2 else 0
                    time_taken_obj = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except (ValueError, IndexError):
                    errors['time_taken'] = ['Invalid duration format']

            # Validate start date if provided
            start_date_obj = None
            if start_date:
                try:
                    from datetime import datetime
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    errors['start_date'] = ['Invalid date format']

            # Validate module number if provided
            module_number_obj = None
            if module_number:
                try:
                    module_number_obj = int(module_number)
                except ValueError:
                    errors['module_number'] = ['Module number must be a valid integer']

            # Validate duration hours if provided
            duration_hours_obj = None
            if duration_hours:
                try:
                    duration_hours_obj = float(duration_hours)
                except ValueError:
                    errors['duration_hours'] = ['Duration hours must be a valid number']

            # Validate participant count if provided
            participant_count_obj = None
            if participant_count:
                try:
                    participant_count_obj = int(participant_count)
                except ValueError:
                    errors['participant_count'] = ['Participant count must be a valid integer']

            if errors:
                return JsonResponse({'success': False, 'errors': errors})

            # Update training
            training.name = name
            training.module_id = module_id
            training.bm_cycle = bm_cycle
            training.assigned_mentor = assigned_mentor
            training.time_taken = time_taken_obj
            training.description = description
            training.status = status
            training.start_date = start_date_obj
            training.max_households = max_households
            training.module_number = module_number_obj
            training.duration_hours = duration_hours_obj
            training.location = location
            training.participant_count = participant_count_obj
            training.save()

            return JsonResponse({
                'success': True,
                'message': f'Training "{training.name}" updated successfully',
                'training_id': training.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating training: {str(e)}'
            })


@login_required
def get_available_households(request, training_id):
    """Get list of households available to add to training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    # Get households that are not already in this training
    enrolled_household_ids = training.attendances.values_list('household_id', flat=True)
    available_households = Household.objects.exclude(id__in=enrolled_household_ids).select_related('village')

    households_data = []
    for household in available_households:
        households_data.append({
            'id': household.id,
            'name': household.name,
            'village': household.village.name,
            'phone': household.phone_number
        })

    return JsonResponse({
        'success': True,
        'households': households_data
    })


@login_required
@require_http_methods(["POST"])
def add_household_to_training(request, training_id):
    """Add a household to training attendance"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        household_id = request.POST.get('household_id')
        training_date = request.POST.get('training_date')

        if not household_id:
            return JsonResponse({'success': False, 'message': 'Household is required'})

        if not training_date:
            return JsonResponse({'success': False, 'message': 'Training date is required'})

        # Validate household exists
        from households.models import Household
        household = get_object_or_404(Household, id=household_id)

        # Check if household is already in this training
        if training.attendances.filter(household=household).exists():
            return JsonResponse({'success': False, 'message': 'Household already enrolled in this training'})

        # Check training capacity
        if training.max_households and training.attendances.count() >= training.max_households:
            return JsonResponse({'success': False, 'message': 'Training is at maximum capacity'})

        # Parse training date
        from datetime import datetime, timedelta
        training_date_obj = datetime.strptime(training_date, '%Y-%m-%d').date()

        # Create attendance record for the selected date
        attendance = TrainingAttendance.objects.create(
            training=training,
            household=household,
            training_date=training_date_obj,
            attendance=True,  # Default to present for current date
            marked_by=user,
            attendance_marked_at=timezone.now()
        )

        # Automatically mark absent for all previous training dates
        absent_records_created = 0
        if training.start_date and training_date_obj > training.start_date:
            current_date = training.start_date
            while current_date < training_date_obj:
                # Only create if within training period
                if not training.end_date or current_date <= training.end_date:
                    # Check if attendance record already exists for this date
                    if not training.attendances.filter(household=household, training_date=current_date).exists():
                        TrainingAttendance.objects.create(
                            training=training,
                            household=household,
                            training_date=current_date,
                            attendance=False,  # Mark as absent for past dates
                            marked_by=user,
                            attendance_marked_at=timezone.now()
                        )
                        absent_records_created += 1
                current_date += timedelta(days=1)

        message = f'Household "{household.name}" added to training successfully'
        if absent_records_created > 0:
            message += f'. Automatically marked absent for {absent_records_created} previous date(s).'

        return JsonResponse({
            'success': True,
            'message': message,
            'attendance_id': attendance.id,
            'absent_records_created': absent_records_created
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding household: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def toggle_attendance(request, attendance_id):
    """Toggle attendance status for a household"""
    attendance = get_object_or_404(TrainingAttendance, id=attendance_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and attendance.training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        new_attendance = request.POST.get('attendance') == 'true'
        attendance.attendance = new_attendance
        attendance.marked_by = user
        attendance.attendance_marked_at = timezone.now()
        attendance.save()

        return JsonResponse({
            'success': True,
            'message': f'Attendance updated for {attendance.household.name}',
            'attendance': new_attendance
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating attendance: {str(e)}'
        })


@login_required
@require_http_methods(["DELETE"])
def remove_attendance(request, attendance_id):
    """Remove a household from training attendance"""
    attendance = get_object_or_404(TrainingAttendance, id=attendance_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and attendance.training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        household_name = attendance.household.name
        attendance.delete()

        return JsonResponse({
            'success': True,
            'message': f'Household "{household_name}" removed from training'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error removing household: {str(e)}'
        })
```

---


## File: upg_grants\__init__.py

**Location:** `upg_grants\__init__.py`

```python

```

---


## File: upg_grants\admin.py

**Location:** `upg_grants\admin.py`

```python
"""
Admin configuration for UPG Grants
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SBGrant, PRGrant, GrantDisbursement


@admin.register(SBGrant)
class SBGrantAdmin(admin.ModelAdmin):
    list_display = [
        'business_group', 'program', 'get_grant_amount', 'status',
        'disbursement_status', 'application_date', 'approval_date'
    ]
    list_filter = [
        'status', 'disbursement_status', 'program__name',
        'application_date', 'approval_date'
    ]
    search_fields = [
        'business_group__name', 'program__name',
        'business_group__members__name'
    ]
    readonly_fields = ['application_date', 'disbursement_percentage']

    fieldsets = (
        ('Grant Information', {
            'fields': ('program', 'business_group', 'base_grant_amount', 'calculated_grant_amount', 'final_grant_amount', 'status', 'disbursement_status')
        }),
        ('Application Details', {
            'fields': ('application_date', 'business_plan', 'projected_income')
        }),
        ('Review Process', {
            'fields': ('reviewed_by', 'review_date', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Approval Process', {
            'fields': ('approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        ('Disbursement', {
            'fields': ('disbursement_date', 'disbursed_amount', 'disbursed_by', 'disbursement_percentage'),
            'classes': ('collapse',)
        }),
        ('Utilization', {
            'fields': ('utilization_report', 'utilization_date'),
            'classes': ('collapse',)
        }),
    )

    def get_grant_amount(self, obj):
        """Display the effective grant amount"""
        return f"KES {obj.get_grant_amount():,.2f}"
    get_grant_amount.short_description = "Grant Amount"
    get_grant_amount.admin_order_field = 'final_grant_amount'

    def get_queryset(self, request):
        """Only show SB grants for UPG programs"""
        return super().get_queryset(request).select_related(
            'program', 'business_group', 'reviewed_by', 'approved_by', 'disbursed_by'
        )


@admin.register(PRGrant)
class PRGrantAdmin(admin.ModelAdmin):
    list_display = [
        'business_group', 'program', 'grant_amount', 'status',
        'performance_rating', 'application_date', 'approval_date'
    ]
    list_filter = [
        'status', 'performance_rating', 'program__name',
        'application_date', 'approval_date'
    ]
    search_fields = [
        'business_group__name', 'program__name',
        'business_group__members__name'
    ]
    readonly_fields = ['application_date', 'is_eligible']

    fieldsets = (
        ('Grant Information', {
            'fields': ('program', 'business_group', 'sb_grant', 'grant_amount', 'status')
        }),
        ('Application Details', {
            'fields': ('application_date', 'is_eligible')
        }),
        ('Performance Assessment', {
            'fields': ('performance_score', 'performance_rating', 'performance_assessment'),
        }),
        ('Business Metrics', {
            'fields': ('revenue_generated', 'jobs_created', 'savings_accumulated'),
            'classes': ('collapse',)
        }),
        ('Assessment Process', {
            'fields': ('assessed_by', 'assessment_date'),
            'classes': ('collapse',)
        }),
        ('Approval Process', {
            'fields': ('approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        ('Disbursement', {
            'fields': ('disbursement_date', 'disbursed_by'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Only show PR grants for UPG programs"""
        return super().get_queryset(request).select_related(
            'program', 'business_group', 'sb_grant', 'assessed_by', 'approved_by', 'disbursed_by'
        )


@admin.register(GrantDisbursement)
class GrantDisbursementAdmin(admin.ModelAdmin):
    list_display = [
        'get_grant_name', 'disbursement_type', 'amount',
        'disbursement_date', 'method', 'processed_by'
    ]
    list_filter = [
        'disbursement_type', 'method', 'disbursement_date'
    ]
    search_fields = [
        'sb_grant__business_group__name', 'pr_grant__business_group__name',
        'recipient_name', 'reference_number'
    ]
    readonly_fields = ['get_grant_name']

    fieldsets = (
        ('Disbursement Information', {
            'fields': ('get_grant_name', 'disbursement_type', 'amount', 'disbursement_date', 'method')
        }),
        ('Grant References', {
            'fields': ('sb_grant', 'pr_grant'),
            'classes': ('collapse',)
        }),
        ('Transaction Details', {
            'fields': ('reference_number', 'recipient_name', 'recipient_contact')
        }),
        ('Processing', {
            'fields': ('processed_by', 'notes')
        }),
    )

    def get_grant_name(self, obj):
        """Get the business group name from either SB or PR grant"""
        if obj.sb_grant:
            return obj.sb_grant.business_group.name
        elif obj.pr_grant:
            return obj.pr_grant.business_group.name
        return "N/A"
    get_grant_name.short_description = "Business Group"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sb_grant__business_group', 'pr_grant__business_group', 'processed_by'
        )
```

---


## File: upg_grants\apps.py

**Location:** `upg_grants\apps.py`

```python
from django.apps import AppConfig


class UpgGrantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'upg_grants'

```

---


## File: upg_grants\management\commands\create_test_grants.py

**Location:** `upg_grants\management\commands\create_test_grants.py`

```python
"""
Management command to create test grant applications
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from upg_grants.models import HouseholdGrantApplication
from households.models import Household
from programs.models import Program
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test grant applications with different grant types'

    def handle(self, *args, **kwargs):
        # Get a user to submit applications
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('No users found in the system'))
            return

        # Get households
        households = list(Household.objects.all()[:6])
        if len(households) < 5:
            self.stdout.write(self.style.WARNING(f'Only {len(households)} households available'))

        # Get a program (optional)
        program = Program.objects.first()

        # Grant application data
        grant_data = [
            {
                'grant_type': 'seed_business',
                'title': 'Vegetable Farming Seed Capital',
                'purpose': 'To establish a vegetable farming business selling fresh produce to the local market. This will provide sustainable income for the household.',
                'business_plan': 'Start with 1-acre plot of tomatoes, kales, and spinach. Target local market and schools. Expected harvest cycle: 3 months.',
                'expected_outcomes': 'Generate monthly income of KES 15,000 after 3 months. Create employment for 2 additional laborers.',
                'budget_breakdown': {
                    'Seeds and seedlings': 3000,
                    'Fertilizers and pesticides': 4000,
                    'Irrigation system': 5000,
                    'Farm tools': 3000,
                },
            },
            {
                'grant_type': 'performance_recognition',
                'title': 'Poultry Expansion Performance Grant',
                'purpose': 'Recognition grant for successful completion of initial poultry business. Funds will be used to expand from 50 to 200 chickens.',
                'business_plan': 'Expand existing successful poultry farm. Purchase 150 additional layer chickens. Build larger coop. Expected ROI within 6 months.',
                'expected_outcomes': 'Triple current egg production. Increase monthly income from KES 8,000 to KES 25,000. Supply eggs to 3 local shops.',
                'budget_breakdown': {
                    'Chickens (150 @ 250)': 37500,
                    'Expanded chicken coop': 15000,
                    'Initial feed stock': 8000,
                    'Feeders and waterers': 4500,
                },
            },
            {
                'grant_type': 'livelihood',
                'title': 'Tailoring Equipment for Income Generation',
                'purpose': 'Purchase tailoring equipment to start home-based tailoring business. Will provide clothing alterations and custom garments to community.',
                'expected_outcomes': 'Establish home-based tailoring business serving 20+ customers monthly. Generate steady income of KES 10,000/month.',
                'budget_breakdown': {
                    'Sewing machine': 18000,
                    'Fabric and materials': 7000,
                    'Table and supplies': 5000,
                },
            },
            {
                'grant_type': 'emergency',
                'title': 'Medical Emergency Support',
                'purpose': 'Emergency medical assistance for household member requiring urgent surgery. Critical health situation requiring immediate financial support.',
                'expected_outcomes': 'Complete medical treatment successfully. Return household member to health and productive capacity within 2 months.',
                'budget_breakdown': {
                    'Hospital bills': 35000,
                    'Medications': 8000,
                    'Transportation': 2000,
                },
            },
            {
                'grant_type': 'education',
                'title': 'Secondary School Fees Support',
                'purpose': 'Educational support for 2 children to complete secondary school. School fees are preventing children from attending despite good academic performance.',
                'expected_outcomes': 'Both children complete Form 3 and 4. Improve chances of further education and better employment opportunities.',
                'budget_breakdown': {
                    'School fees (2 students)': 24000,
                    'School uniforms': 4000,
                    'Books and supplies': 6000,
                    'Boarding costs': 16000,
                },
            },
            {
                'grant_type': 'housing',
                'title': 'House Roof Repair and Improvement',
                'purpose': 'Repair leaking roof and improve housing conditions. Current roof is deteriorating and poses health risk during rainy season.',
                'expected_outcomes': 'Safe, weatherproof housing. Improved health conditions. Reduced medical expenses from rain-related illnesses.',
                'budget_breakdown': {
                    'Iron sheets (30 pieces)': 21000,
                    'Timber and poles': 8000,
                    'Nails and fixtures': 3000,
                    'Labor costs': 8000,
                },
            },
        ]

        created_count = 0
        for idx, data in enumerate(grant_data):
            if idx >= len(households):
                break

            household = households[idx]

            # Calculate requested amount from budget breakdown
            requested_amount = sum(data['budget_breakdown'].values())

            # Create application
            application = HouseholdGrantApplication.objects.create(
                household=household,
                submitted_by=user,
                program=program if random.choice([True, False]) else None,  # Randomly assign program
                grant_type=data['grant_type'],
                title=data['title'],
                purpose=data['purpose'],
                business_plan=data.get('business_plan', ''),
                expected_outcomes=data['expected_outcomes'],
                requested_amount=Decimal(str(requested_amount)),
                budget_breakdown=data['budget_breakdown'],
                status=random.choice(['submitted', 'under_review', 'approved', 'submitted']),
                submission_date=timezone.now(),
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {data["grant_type"]} grant for {household.name}: {data["title"]} (KES {requested_amount:,})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} test grant applications')
        )

```

---


## File: upg_grants\management\commands\create_test_sb_pr_grants.py

**Location:** `upg_grants\management\commands\create_test_sb_pr_grants.py`

```python
"""
Management command to create test SB and PR grant applications
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from upg_grants.models import SBGrant, PRGrant
from business_groups.models import BusinessGroup
from programs.models import Program
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test SB and PR grants at different stages'

    def handle(self, *args, **kwargs):
        # Get a user
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('No users found in the system'))
            return

        # Get business groups
        business_groups = list(BusinessGroup.objects.all()[:6])
        if len(business_groups) < 6:
            self.stdout.write(self.style.WARNING(f'Only {len(business_groups)} business groups available, need at least 6'))
            return

        # Get a program
        program = Program.objects.first()
        if not program:
            self.stdout.write(self.style.ERROR('No programs found in the system'))
            return

        # Create 3 SB Grants at different stages
        sb_grants_data = [
            {
                'business_group': business_groups[0],
                'status': 'pending',
                'business_plan': 'Start a vegetable farming collective to supply local markets with fresh produce. Focus on high-demand crops like kales, tomatoes, and onions.',
                'projected_income': Decimal('25000.00'),
                'startup_costs': Decimal('18000.00'),
                'monthly_expenses': Decimal('8000.00'),
            },
            {
                'business_group': business_groups[1],
                'status': 'under_review',
                'business_plan': 'Establish a dairy farming cooperative. Purchase 5 dairy cows and milking equipment. Supply fresh milk to local community and dairy processors.',
                'projected_income': Decimal('35000.00'),
                'startup_costs': Decimal('22000.00'),
                'monthly_expenses': Decimal('12000.00'),
                'reviewed_by': user,
                'review_date': timezone.now().date(),
                'review_notes': 'Strong business plan. Group has good training attendance. Recommended for approval.',
            },
            {
                'business_group': business_groups[2],
                'status': 'approved',
                'business_plan': 'Launch a poultry farming business with 100 chickens. Focus on egg production for local market. Sustainable income source.',
                'projected_income': Decimal('20000.00'),
                'startup_costs': Decimal('16000.00'),
                'monthly_expenses': Decimal('7000.00'),
                'reviewed_by': user,
                'review_date': timezone.now().date(),
                'review_notes': 'Excellent proposal. Group demonstrates strong commitment.',
                'approved_by': user,
                'approval_date': timezone.now().date(),
            },
        ]

        self.stdout.write(self.style.SUCCESS('\n=== Creating SB Grants ==='))
        for idx, data in enumerate(sb_grants_data):
            bg = data.pop('business_group')

            sb_grant = SBGrant.objects.create(
                program=program,
                business_group=bg,
                submitted_by=user,
                **data
            )

            # Calculate grant amount
            sb_grant.calculate_grant_amount()
            sb_grant.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'{idx+1}. SB Grant for {bg.name}: {sb_grant.get_status_display()} - KES {sb_grant.get_grant_amount():,.2f}'
                )
            )

        # Create 3 PR Grants at different stages
        # First, create approved SB grants for the PR grants to reference
        pr_sb_grants = []
        for i in range(3, 6):
            sb_grant = SBGrant.objects.create(
                program=program,
                business_group=business_groups[i],
                submitted_by=user,
                business_plan=f'Initial business for {business_groups[i].name}',
                status='disbursed',
                approved_by=user,
                approval_date=timezone.now().date(),
                disbursement_date=timezone.now().date(),
                disbursed_amount=Decimal('15000.00'),
                utilization_report=f'Successfully utilized SB grant. Business is running well.',
            )
            sb_grant.calculate_grant_amount()
            sb_grant.disbursed_amount = sb_grant.get_grant_amount()
            sb_grant.save()
            pr_sb_grants.append(sb_grant)

        pr_grants_data = [
            {
                'sb_grant': pr_sb_grants[0],
                'business_group': business_groups[3],
                'status': 'pending',
                'performance_assessment': 'Group has shown good performance. Regular savings, good attendance.',
                'revenue_generated': Decimal('45000.00'),
                'jobs_created': 3,
                'savings_accumulated': Decimal('12000.00'),
            },
            {
                'sb_grant': pr_sb_grants[1],
                'business_group': business_groups[4],
                'status': 'under_review',
                'performance_assessment': 'Excellent business growth. Expanded operations and created employment.',
                'revenue_generated': Decimal('65000.00'),
                'jobs_created': 5,
                'savings_accumulated': Decimal('18000.00'),
                'assessed_by': user,
                'assessment_date': timezone.now().date(),
                'performance_score': 85,
                'performance_rating': 'excellent',
            },
            {
                'sb_grant': pr_sb_grants[2],
                'business_group': business_groups[5],
                'status': 'approved',
                'performance_assessment': 'Outstanding performance. Business doubled revenue. Strong community impact.',
                'revenue_generated': Decimal('85000.00'),
                'jobs_created': 7,
                'savings_accumulated': Decimal('25000.00'),
                'assessed_by': user,
                'assessment_date': timezone.now().date(),
                'performance_score': 92,
                'performance_rating': 'excellent',
                'approved_by': user,
                'approval_date': timezone.now().date(),
            },
        ]

        self.stdout.write(self.style.SUCCESS('\n=== Creating PR Grants ==='))
        for idx, data in enumerate(pr_grants_data):
            bg = data.pop('business_group')

            pr_grant = PRGrant.objects.create(
                program=program,
                business_group=bg,
                **data
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'{idx+1}. PR Grant for {bg.name}: {pr_grant.get_status_display()} - KES {pr_grant.grant_amount:,.2f}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created 3 SB grants and 3 PR grants at different stages')
        )

```

---


## File: upg_grants\models.py

**Location:** `upg_grants\models.py`

```python
"""
UPG-Specific Grant Management Models
SB (Seed Business) Grants and PR (Performance Recognition) Grants
Only applicable for Ultra-Poor Graduation programs
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from programs.models import Program
from business_groups.models import BusinessGroup
from savings_groups.models import BusinessSavingsGroup
from core.models import BaseModel

User = get_user_model()


class HouseholdGrantApplication(BaseModel):
    """
    Grant applications submitted by individual households
    Can be reviewed and approved by program managers, county directors, or executives
    """
    GRANT_TYPE_CHOICES = [
        ('seed_business', 'Seed Business Grant'),
        ('performance_recognition', 'Performance Recognition Grant'),
        ('livelihood', 'Livelihood Grant'),
        ('emergency', 'Emergency Grant'),
        ('education', 'Education Support Grant'),
        ('housing', 'Housing Improvement Grant'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('cancelled', 'Cancelled'),
    ]

    # Applicant information - one of these three must be filled
    household = models.ForeignKey('households.Household', on_delete=models.CASCADE, related_name='grant_applications', null=True, blank=True,
                                  help_text="For individual household applications")
    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='grant_applications', null=True, blank=True,
                                       help_text="For business group applications")
    savings_group = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='grant_applications', null=True, blank=True,
                                      help_text="For savings group applications")

    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_grant_applications',
                                    help_text="User who submitted the application")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='household_grant_applications', null=True, blank=True,
                                help_text="Optional - for program-specific funding")

    # Grant details
    grant_type = models.CharField(max_length=30, choices=GRANT_TYPE_CHOICES)
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Application details
    title = models.CharField(max_length=200, help_text="Brief title of grant purpose")
    purpose = models.TextField(help_text="Detailed purpose and justification for the grant")
    business_plan = models.TextField(blank=True, help_text="Business plan if applicable")
    expected_outcomes = models.TextField(help_text="Expected outcomes and impact")
    budget_breakdown = models.JSONField(default=dict, blank=True, help_text="Itemized budget as JSON")

    # Supporting documents (stored as file paths or URLs)
    supporting_documents = models.JSONField(default=list, blank=True, help_text="List of document paths")

    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submission_date = models.DateTimeField(null=True, blank=True)

    # Review process
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_household_grants')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    review_score = models.IntegerField(null=True, blank=True, help_text="Review score 0-100")

    # Approval process (requires program_manager, county_director, or executive role)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_household_grants')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)

    # Disbursement
    disbursement_date = models.DateField(null=True, blank=True)
    disbursed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    disbursed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='disbursed_household_grants')
    disbursement_method = models.CharField(max_length=50, blank=True,
                                          choices=[
                                              ('bank_transfer', 'Bank Transfer'),
                                              ('mobile_money', 'Mobile Money'),
                                              ('cash', 'Cash'),
                                              ('check', 'Check'),
                                          ])
    disbursement_reference = models.CharField(max_length=100, blank=True)

    # Progress tracking
    utilization_report = models.TextField(blank=True, help_text="How the grant was utilized")
    utilization_date = models.DateField(null=True, blank=True)
    final_outcomes = models.TextField(blank=True, help_text="Final outcomes achieved")

    class Meta:
        verbose_name = "Household Grant Application"
        verbose_name_plural = "Household Grant Applications"
        ordering = ['-created_at']
        db_table = 'upg_household_grant_applications'

    def __str__(self):
        applicant_name = self.get_applicant_name()
        return f"{applicant_name} - {self.get_grant_type_display()} - {self.get_status_display()}"

    def get_applicant_name(self):
        """Get the name of the applicant (household, business group, or savings group)"""
        if self.household:
            return self.household.name
        elif self.business_group:
            return self.business_group.name
        elif self.savings_group:
            return self.savings_group.name
        return "Unknown Applicant"

    def get_applicant_type(self):
        """Get the type of applicant"""
        if self.household:
            return "household"
        elif self.business_group:
            return "business_group"
        elif self.savings_group:
            return "savings_group"
        return "unknown"

    def clean(self):
        """Validate that exactly one applicant type is specified"""
        applicants = [self.household, self.business_group, self.savings_group]
        applicants_filled = [a for a in applicants if a is not None]

        if len(applicants_filled) == 0:
            raise ValidationError("Must specify either household, business_group, or savings_group")
        if len(applicants_filled) > 1:
            raise ValidationError("Cannot specify multiple applicant types")

        super().clean()

    def can_be_reviewed_by(self, user):
        """Check if user has permission to review this application"""
        return user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff']

    def can_be_approved_by(self, user):
        """Check if user has permission to approve this application"""
        return user.role in ['program_manager', 'county_director', 'executive']

    @property
    def is_pending_review(self):
        return self.status in ['submitted', 'under_review']

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be disbursed"""
        approved = self.approved_amount or self.requested_amount
        return approved - self.disbursed_amount


class UPGGrantManager(models.Manager):
    """Manager to filter grants only for UPG programs"""

    def get_queryset(self):
        return super().get_queryset().filter(
            program__program_type='graduation'
        )


class SBGrant(BaseModel):
    """
    Seed Business (SB) Grants - Initial capital grants for business groups
    Only available for UPG programs
    """
    GRANT_STATUS_CHOICES = [
        ('pending', 'Pending Application'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    DISBURSEMENT_STATUS_CHOICES = [
        ('not_disbursed', 'Not Disbursed'),
        ('partially_disbursed', 'Partially Disbursed'),
        ('fully_disbursed', 'Fully Disbursed'),
    ]

    # Core relationships
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='sb_grants')
    business_group = models.OneToOneField(BusinessGroup, on_delete=models.CASCADE, related_name='sb_grant', null=True, blank=True,
                                          help_text="For business group applications")
    household = models.ForeignKey('households.Household', on_delete=models.CASCADE, related_name='sb_grants', null=True, blank=True,
                                  help_text="For individual household applications")
    savings_group = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='sb_grants', null=True, blank=True,
                                      help_text="For savings group applications")

    # Application submitter
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_sb_grants',
                                    help_text="User who submitted the application")

    # Grant details - Enhanced calculations
    base_grant_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('15000.00'), help_text="Base grant amount")
    calculated_grant_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Auto-calculated based on criteria")
    final_grant_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Final approved amount")

    # Calculation factors
    group_size_factor = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.00'), help_text="Multiplier based on group size")
    business_type_factor = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.00'), help_text="Multiplier based on business type")
    location_factor = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.00'), help_text="Geographic location adjustment")
    performance_factor = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.00'), help_text="Based on group performance")

    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=GRANT_STATUS_CHOICES, default='pending')
    disbursement_status = models.CharField(max_length=20, choices=DISBURSEMENT_STATUS_CHOICES, default='not_disbursed')

    # Application details
    business_plan = models.TextField(help_text="Business plan submitted with application")
    projected_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    startup_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Estimated startup costs")
    monthly_expenses = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Projected monthly expenses")

    # Approval process
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_sb_grants')
    review_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_sb_grants')
    approval_date = models.DateField(null=True, blank=True)

    # Disbursement tracking
    disbursement_date = models.DateField(null=True, blank=True)
    disbursed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    disbursed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursed_sb_grants')

    # Utilization tracking
    utilization_report = models.TextField(blank=True)
    utilization_date = models.DateField(null=True, blank=True)

    objects = models.Manager()
    upg_objects = UPGGrantManager()

    class Meta:
        verbose_name = "SB Grant (Seed Business)"
        verbose_name_plural = "SB Grants (Seed Business)"
        ordering = ['-created_at']

    def __str__(self):
        applicant_name = self.get_applicant_name()
        return f"SB Grant - {applicant_name} - {self.get_status_display()}"

    def get_applicant_name(self):
        """Get the name of the applicant"""
        if self.business_group:
            return self.business_group.name
        elif self.household:
            return self.household.name
        elif self.savings_group:
            return self.savings_group.name
        return "Unknown Applicant"

    def get_applicant_type(self):
        """Get the type of applicant"""
        if self.business_group:
            return "business_group"
        elif self.household:
            return "household"
        elif self.savings_group:
            return "savings_group"
        return "unknown"

    def calculate_grant_amount(self):
        """Calculate grant amount based on various factors"""
        base_amount = self.base_grant_amount

        # Group size factor (larger groups get more funding)
        group_size = self.business_group.members.count()
        if group_size >= 20:
            self.group_size_factor = Decimal('1.20')  # 20% bonus for large groups
        elif group_size >= 15:
            self.group_size_factor = Decimal('1.10')  # 10% bonus
        elif group_size < 8:
            self.group_size_factor = Decimal('0.90')  # 10% reduction for small groups

        # Business type factor (high-impact businesses get more)
        business_type = getattr(self.business_group, 'business_type', '')
        if business_type in ['agriculture', 'livestock']:
            self.business_type_factor = Decimal('1.15')  # 15% bonus for agriculture
        elif business_type in ['manufacturing', 'processing']:
            self.business_type_factor = Decimal('1.10')  # 10% bonus for manufacturing

        # Location factor (remote areas get more funding)
        location = getattr(self.business_group, 'location', '')
        if 'remote' in location.lower() or 'rural' in location.lower():
            self.location_factor = Decimal('1.05')  # 5% bonus for remote areas

        # Performance factor (based on training completion, group cohesion)
        # This would be calculated based on group's training attendance, savings, etc.
        training_completion_rate = self._get_training_completion_rate()
        if training_completion_rate >= 0.9:
            self.performance_factor = Decimal('1.10')  # 10% bonus for high performers
        elif training_completion_rate < 0.6:
            self.performance_factor = Decimal('0.95')  # 5% reduction for poor performers

        # Calculate final amount
        total_factor = (
            self.group_size_factor *
            self.business_type_factor *
            self.location_factor *
            self.performance_factor
        )

        self.calculated_grant_amount = base_amount * total_factor

        # Apply caps and minimums
        max_grant = Decimal('25000.00')  # Maximum grant
        min_grant = Decimal('10000.00')  # Minimum grant

        if self.calculated_grant_amount > max_grant:
            self.calculated_grant_amount = max_grant
        elif self.calculated_grant_amount < min_grant:
            self.calculated_grant_amount = min_grant

        # Set final amount (can be manually adjusted later)
        if not self.final_grant_amount:
            self.final_grant_amount = self.calculated_grant_amount

        return self.calculated_grant_amount

    def _get_training_completion_rate(self):
        """Calculate training completion rate for the business group"""
        try:
            from training.models import TrainingAttendance
            total_trainings = TrainingAttendance.objects.filter(
                household__business_group_memberships__business_group=self.business_group
            ).count()

            completed_trainings = TrainingAttendance.objects.filter(
                household__business_group_memberships__business_group=self.business_group,
                attendance=True
            ).count()

            if total_trainings > 0:
                return completed_trainings / total_trainings
            return 0.0
        except:
            return 0.8  # Default rate if calculation fails

    def get_grant_amount(self):
        """Get the effective grant amount to use"""
        if self.final_grant_amount:
            return self.final_grant_amount
        elif self.calculated_grant_amount:
            return self.calculated_grant_amount
        else:
            return self.base_grant_amount

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be disbursed"""
        return self.get_grant_amount() - self.disbursed_amount

    @property
    def disbursement_percentage(self):
        """Calculate percentage of grant that has been disbursed"""
        grant_amount = self.get_grant_amount()
        if grant_amount > 0:
            return (self.disbursed_amount / grant_amount) * 100
        return 0

    def can_disburse(self, amount):
        """Check if a specific amount can be disbursed"""
        return (self.disbursed_amount + amount) <= self.get_grant_amount()

    def save(self, *args, **kwargs):
        """Auto-calculate grant amount on save"""
        if not self.calculated_grant_amount:
            self.calculate_grant_amount()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate that this grant is only for UPG programs"""
        # Ensure exactly one applicant type is specified
        applicants = [self.business_group, self.household, self.savings_group]
        applicants_filled = [a for a in applicants if a is not None]

        if len(applicants_filled) == 0:
            raise ValidationError("Must specify either business_group, household, or savings_group")
        if len(applicants_filled) > 1:
            raise ValidationError("Cannot specify multiple applicant types")

        if self.program and not self.program.is_upg_program:
            raise ValidationError("SB Grants are only available for Ultra-Poor Graduation programs")

        # Validate financial calculations
        if self.startup_costs and self.monthly_expenses and self.projected_income:
            if self.startup_costs > self.get_grant_amount() * 2:
                raise ValidationError("Startup costs seem too high relative to grant amount")

            if self.projected_income < self.monthly_expenses:
                raise ValidationError("Projected income should be higher than monthly expenses")

        super().clean()

    @property
    def is_eligible_for_disbursement(self):
        """Check if grant is approved and ready for disbursement"""
        return self.status == 'approved' and self.disbursement_status == 'not_disbursed'

    @property
    def disbursement_percentage(self):
        """Calculate disbursement percentage"""
        if self.grant_amount > 0:
            return (self.disbursed_amount / self.grant_amount) * 100
        return 0


class PRGrant(BaseModel):
    """
    Performance Recognition (PR) Grants - Performance-based grants for business groups
    Only available for UPG programs after SB grant utilization
    """
    GRANT_STATUS_CHOICES = [
        ('not_eligible', 'Not Eligible Yet'),
        ('eligible', 'Eligible'),
        ('pending', 'Pending Application'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    PERFORMANCE_CRITERIA_CHOICES = [
        ('excellent', 'Excellent Performance'),
        ('good', 'Good Performance'),
        ('satisfactory', 'Satisfactory Performance'),
        ('poor', 'Poor Performance'),
    ]

    # Core relationships
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='pr_grants')
    business_group = models.OneToOneField(BusinessGroup, on_delete=models.CASCADE, related_name='pr_grant', null=True, blank=True,
                                          help_text="For business group applications")
    household = models.ForeignKey('households.Household', on_delete=models.CASCADE, related_name='pr_grants', null=True, blank=True,
                                  help_text="For individual household applications")
    savings_group = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='pr_grants', null=True, blank=True,
                                      help_text="For savings group applications")
    sb_grant = models.OneToOneField(SBGrant, on_delete=models.CASCADE, related_name='pr_grant',
                                   help_text="PR grants are only available after SB grant")

    # Grant details
    grant_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10000.00'))
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=GRANT_STATUS_CHOICES, default='not_eligible')

    # Performance assessment
    performance_score = models.IntegerField(null=True, blank=True, help_text="Performance score 0-100")
    performance_rating = models.CharField(max_length=20, choices=PERFORMANCE_CRITERIA_CHOICES, blank=True)
    performance_assessment = models.TextField(blank=True, help_text="Detailed performance assessment")

    # Business metrics (from SB grant period)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    jobs_created = models.PositiveIntegerField(default=0)
    savings_accumulated = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Eligibility assessment
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessed_pr_grants')
    assessment_date = models.DateField(null=True, blank=True)

    # Approval process
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pr_grants')
    approval_date = models.DateField(null=True, blank=True)

    # Disbursement
    disbursement_date = models.DateField(null=True, blank=True)
    disbursed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursed_pr_grants')

    objects = models.Manager()
    upg_objects = UPGGrantManager()

    class Meta:
        verbose_name = "PR Grant (Performance Recognition)"
        verbose_name_plural = "PR Grants (Performance Recognition)"
        ordering = ['-created_at']

    def __str__(self):
        applicant_name = self.get_applicant_name()
        return f"PR Grant - {applicant_name} - {self.get_status_display()}"

    def get_applicant_name(self):
        """Get the name of the applicant"""
        if self.business_group:
            return self.business_group.name
        elif self.household:
            return self.household.name
        elif self.savings_group:
            return self.savings_group.name
        return "Unknown Applicant"

    def get_applicant_type(self):
        """Get the type of applicant"""
        if self.business_group:
            return "business_group"
        elif self.household:
            return "household"
        elif self.savings_group:
            return "savings_group"
        return "unknown"

    def clean(self):
        """Validate that this grant is only for UPG programs"""
        # Ensure exactly one applicant type is specified
        applicants = [self.business_group, self.household, self.savings_group]
        applicants_filled = [a for a in applicants if a is not None]

        if len(applicants_filled) == 0:
            raise ValidationError("Must specify either business_group, household, or savings_group")
        if len(applicants_filled) > 1:
            raise ValidationError("Cannot specify multiple applicant types")

        if self.program and not self.program.is_upg_program:
            raise ValidationError("PR Grants are only available for Ultra-Poor Graduation programs")
        super().clean()

    def check_eligibility(self):
        """Check if business group is eligible for PR grant"""
        # Must have completed SB grant successfully
        if not self.sb_grant or self.sb_grant.status != 'disbursed':
            return False, "SB Grant must be successfully disbursed first"

        # Must have good utilization report
        if not self.sb_grant.utilization_report:
            return False, "SB Grant utilization report required"

        # Add more eligibility criteria as needed
        return True, "Eligible for PR Grant"

    @property
    def is_eligible(self):
        """Check if eligible for PR grant"""
        eligible, _ = self.check_eligibility()
        return eligible


class GrantDisbursement(BaseModel):
    """
    Track individual disbursement transactions for grants
    """
    DISBURSEMENT_TYPE_CHOICES = [
        ('sb_grant', 'SB Grant'),
        ('pr_grant', 'PR Grant'),
    ]

    DISBURSEMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash'),
        ('check', 'Check'),
    ]

    # Grant references (one will be null)
    sb_grant = models.ForeignKey(SBGrant, on_delete=models.CASCADE, null=True, blank=True, related_name='disbursements')
    pr_grant = models.ForeignKey(PRGrant, on_delete=models.CASCADE, null=True, blank=True, related_name='disbursements')

    # Disbursement details
    disbursement_type = models.CharField(max_length=20, choices=DISBURSEMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    disbursement_date = models.DateField()
    method = models.CharField(max_length=20, choices=DISBURSEMENT_METHOD_CHOICES, default='bank_transfer')

    # Transaction details
    reference_number = models.CharField(max_length=100, blank=True)
    recipient_name = models.CharField(max_length=100)
    recipient_contact = models.CharField(max_length=50, blank=True)

    # Processing
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_disbursements')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-disbursement_date']

    def __str__(self):
        grant_name = self.sb_grant.business_group.name if self.sb_grant else self.pr_grant.business_group.name
        return f"{self.get_disbursement_type_display()} - {grant_name} - {self.amount}"

    def clean(self):
        """Ensure exactly one grant reference is provided"""
        if not (self.sb_grant or self.pr_grant):
            raise ValidationError("Must specify either SB Grant or PR Grant")
        if self.sb_grant and self.pr_grant:
            raise ValidationError("Cannot specify both SB Grant and PR Grant")
        super().clean()
```

---


## File: upg_grants\tests.py

**Location:** `upg_grants\tests.py`

```python
from django.test import TestCase

# Create your tests here.

```

---


## File: upg_grants\urls.py

**Location:** `upg_grants\urls.py`

```python
from django.urls import path
from . import views

app_name = 'upg_grants'

urlpatterns = [
    # Grant application list and management
    path('applications/', views.grant_application_list, name='application_list'),
    path('applications/create/', views.grant_application_create, name='application_create_universal'),
    path('applications/create/<int:household_id>/', views.grant_application_create, name='application_create'),
    path('applications/<int:application_id>/', views.grant_application_detail, name='application_detail'),
    path('applications/<int:application_id>/review/', views.grant_application_review, name='application_review'),

    # Review dashboard
    path('reviews/pending/', views.pending_reviews, name='pending_reviews'),

    # Available grants for application
    path('available/', views.available_grants_list, name='available_grants'),
]

```

---


## File: upg_grants\views.py

**Location:** `upg_grants\views.py`

```python
"""
Grant Application and Review Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from households.models import Household
from programs.models import Program
from .models import HouseholdGrantApplication, SBGrant, PRGrant
from decimal import Decimal
import json
from itertools import chain
from operator import attrgetter


@login_required
def grant_application_list(request):
    """List all grant applications (Household, SB, PR) with filtering by status and grant type"""
    user = request.user

    # Get Household grants
    if user.role in ['mentor', 'field_associate']:
        household_grants = HouseholdGrantApplication.objects.filter(
            household__village__in=user.profile.assigned_villages.all() if hasattr(user, 'profile') else []
        ).select_related('household', 'household__village', 'program', 'approved_by', 'reviewed_by', 'submitted_by')
    elif user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff'] or user.is_superuser:
        household_grants = HouseholdGrantApplication.objects.all().select_related('household', 'household__village', 'program', 'approved_by', 'reviewed_by', 'submitted_by')
    else:
        household_grants = HouseholdGrantApplication.objects.none()

    # Get SB and PR grants
    if user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff', 'field_associate'] or user.is_superuser:
        sb_grants = SBGrant.objects.all().select_related('business_group', 'program')
        pr_grants = PRGrant.objects.all().select_related('business_group', 'program', 'sb_grant')
    else:
        sb_grants = SBGrant.objects.none()
        pr_grants = PRGrant.objects.none()

    # Apply filters
    status_filter = request.GET.get('status')
    grant_type_filter = request.GET.get('grant_type')

    if status_filter:
        household_grants = household_grants.filter(status=status_filter)
        sb_grants = sb_grants.filter(status=status_filter)
        pr_grants = pr_grants.filter(status=status_filter)

    if grant_type_filter:
        if grant_type_filter == 'sb':
            household_grants = HouseholdGrantApplication.objects.none()
            pr_grants = PRGrant.objects.none()
        elif grant_type_filter == 'pr':
            household_grants = HouseholdGrantApplication.objects.none()
            sb_grants = SBGrant.objects.none()
        else:
            # Household grant type filter
            household_grants = household_grants.filter(grant_type=grant_type_filter)
            sb_grants = SBGrant.objects.none()
            pr_grants = PRGrant.objects.none()

    # Add grant type attribute to each grant for display
    for grant in household_grants:
        grant.display_type = f'Household - {grant.get_grant_type_display()}'
        grant.grant_category = 'household'

    for grant in sb_grants:
        grant.display_type = 'SB Grant'
        grant.grant_category = 'sb'

    for grant in pr_grants:
        grant.display_type = 'PR Grant'
        grant.grant_category = 'pr'

    # Combine all grants and sort by creation date
    all_grants = sorted(
        chain(household_grants, sb_grants, pr_grants),
        key=attrgetter('created_at'),
        reverse=True
    )

    # Determine user permissions
    can_create = user.role in ['mentor', 'field_associate', 'ict_admin', 'me_staff'] or user.is_superuser
    can_review = user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff'] or user.is_superuser
    can_approve = user.role in ['program_manager', 'county_director', 'executive'] or user.is_superuser

    # Create comprehensive grant type choices
    grant_type_choices = [
        ('sb', 'SB Grant'),
        ('pr', 'PR Grant'),
    ] + list(HouseholdGrantApplication.GRANT_TYPE_CHOICES)

    # Get available grants for mentors and field associates
    available_grants = None
    if user.role in ['mentor', 'field_associate']:
        active_programs = Program.objects.filter(status='active')
        available_grants = {
            'programs': active_programs,
            'grant_types': HouseholdGrantApplication.GRANT_TYPE_CHOICES,
        }

    context = {
        'applications': all_grants,
        'page_title': 'All Grant Applications',
        'can_create': can_create,
        'can_review': can_review,
        'can_approve': can_approve,
        'status_filter': status_filter,
        'grant_type_filter': grant_type_filter,
        'status_choices': HouseholdGrantApplication.STATUS_CHOICES,
        'grant_type_choices': grant_type_choices,
        'available_grants': available_grants,
    }
    return render(request, 'upg_grants/application_list.html', context)


@login_required
def grant_application_create(request, household_id=None):
    """Create a new grant application for household, business group, or savings group"""
    user = request.user

    # Check permissions
    if user.role not in ['mentor', 'field_associate', 'ict_admin', 'me_staff']:
        messages.error(request, 'You do not have permission to create grant applications.')
        return redirect('dashboard:dashboard')

    # Handle both URL parameter and GET parameters
    applicant_type = request.GET.get('applicant_type')
    applicant_id = request.GET.get('applicant_id')
    grant_type_param = request.GET.get('grant_type')

    household = None
    business_group = None
    savings_group = None
    applicant_name = ""

    # If called with household_id (old style)
    if household_id:
        household = get_object_or_404(Household, id=household_id)
        applicant_name = household.name
    # New style with GET parameters
    elif applicant_type and applicant_id:
        from business_groups.models import BusinessGroup
        from savings_groups.models import BusinessSavingsGroup

        if applicant_type == 'household':
            household = get_object_or_404(Household, id=applicant_id)
            applicant_name = household.name
        elif applicant_type == 'business_group':
            business_group = get_object_or_404(BusinessGroup, id=applicant_id)
            applicant_name = business_group.name
        elif applicant_type == 'savings_group':
            savings_group = get_object_or_404(BusinessSavingsGroup, id=applicant_id)
            applicant_name = savings_group.name
    # If only grant_type is provided, show household selection page
    elif grant_type_param:
        # Get households for mentor/field associate
        if user.role in ['mentor', 'field_associate'] and hasattr(user, 'profile'):
            households = Household.objects.filter(
                village__in=user.profile.assigned_villages.all()
            ).select_related('village')
        else:
            households = Household.objects.all().select_related('village')

        context = {
            'households': households,
            'grant_type': grant_type_param,
            'page_title': f'Select Household for {dict(HouseholdGrantApplication.GRANT_TYPE_CHOICES).get(grant_type_param, "Grant")} Application',
        }
        return render(request, 'upg_grants/select_household.html', context)
    else:
        messages.error(request, 'No applicant specified.')
        return redirect('grants:grants_dashboard')

    if request.method == 'POST':
        grant_type = request.POST.get('grant_type')
        requested_amount = Decimal(request.POST.get('requested_amount', 0))
        title = request.POST.get('title')
        purpose = request.POST.get('purpose')
        business_plan = request.POST.get('business_plan', '')
        expected_outcomes = request.POST.get('expected_outcomes')
        program_id = request.POST.get('program')

        # Parse budget breakdown from form
        budget_items = request.POST.getlist('budget_item[]')
        budget_amounts = request.POST.getlist('budget_amount[]')
        budget_breakdown = {}
        for item, amount in zip(budget_items, budget_amounts):
            if item and amount:
                budget_breakdown[item] = float(amount)

        # Program is optional
        program = None
        if program_id:
            program = get_object_or_404(Program, id=program_id)

        application = HouseholdGrantApplication.objects.create(
            household=household,
            business_group=business_group,
            savings_group=savings_group,
            submitted_by=user,
            program=program,
            grant_type=grant_type,
            requested_amount=requested_amount,
            title=title,
            purpose=purpose,
            business_plan=business_plan,
            expected_outcomes=expected_outcomes,
            budget_breakdown=budget_breakdown,
            status='submitted',
            submission_date=timezone.now()
        )

        messages.success(request, f'Grant application "{title}" submitted successfully!')
        return redirect('upg_grants:application_detail', application_id=application.id)

    programs = Program.objects.filter(status='active')

    context = {
        'household': household,
        'business_group': business_group,
        'savings_group': savings_group,
        'applicant_name': applicant_name,
        'programs': programs,
        'page_title': f'Apply for Grant - {applicant_name}',
        'preselected_grant_type': grant_type_param,  # Pre-fill grant type from URL
    }
    return render(request, 'upg_grants/application_create.html', context)


@login_required
def grant_application_detail(request, application_id):
    """View details of a grant application"""
    application = get_object_or_404(HouseholdGrantApplication, id=application_id)

    context = {
        'application': application,
        'can_review': application.can_be_reviewed_by(request.user),
        'can_approve': application.can_be_approved_by(request.user),
        'page_title': f'Grant Application - {application.title}',
    }
    return render(request, 'upg_grants/application_detail.html', context)


@login_required
def grant_application_review(request, application_id):
    """Review interface for grant applications"""
    application = get_object_or_404(HouseholdGrantApplication, id=application_id)

    if not application.can_be_reviewed_by(request.user):
        messages.error(request, 'You do not have permission to review this application.')
        return redirect('upg_grants:application_detail', application_id=application_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'review':
            application.status = 'under_review'
            application.reviewed_by = request.user
            application.review_date = timezone.now()
            application.review_notes = request.POST.get('review_notes', '')
            application.review_score = int(request.POST.get('review_score', 0)) if request.POST.get('review_score') else None
            application.save()
            messages.success(request, 'Application marked as under review.')

        elif action == 'approve' and application.can_be_approved_by(request.user):
            application.status = 'approved'
            application.approved_by = request.user
            application.approval_date = timezone.now()
            application.approval_notes = request.POST.get('approval_notes', '')
            application.approved_amount = Decimal(request.POST.get('approved_amount', application.requested_amount))
            application.save()
            messages.success(request, 'Application approved successfully!')

        elif action == 'reject' and application.can_be_approved_by(request.user):
            application.status = 'rejected'
            application.approved_by = request.user
            application.approval_date = timezone.now()
            application.approval_notes = request.POST.get('approval_notes', '')
            application.save()
            messages.warning(request, 'Application rejected.')

        return redirect('upg_grants:application_detail', application_id=application_id)

    context = {
        'application': application,
        'can_review': application.can_be_reviewed_by(request.user),
        'can_approve': application.can_be_approved_by(request.user),
        'page_title': f'Review Application - {application.title}',
    }
    return render(request, 'upg_grants/application_review.html', context)


@login_required
def pending_reviews(request):
    """List of applications pending review for managers"""
    user = request.user

    # Allow anyone who can access grants to view pending reviews
    if not (user.is_superuser or user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to view pending grant reviews.')
        return redirect('grants:grants_dashboard')

    pending_applications = HouseholdGrantApplication.objects.filter(
        Q(status='submitted') | Q(status='under_review')
    ).select_related('household', 'program', 'submitted_by', 'reviewed_by').order_by('-submission_date')

    # Determine if user can review applications
    can_review = user.is_superuser or user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff']

    context = {
        'applications': pending_applications,
        'page_title': 'Pending Grant Reviews',
        'can_review': can_review,
    }
    return render(request, 'upg_grants/pending_reviews.html', context)


@login_required
def available_grants_list(request):
    """List all available open grants for application"""
    user = request.user

    # Check permissions - mentors and field associates can apply for grants
    if user.role not in ['mentor', 'field_associate', 'ict_admin', 'me_staff']:
        messages.error(request, 'You do not have permission to view available grants.')
        return redirect('dashboard:dashboard')

    # Get all active programs for grant opportunities
    active_programs = Program.objects.filter(status='active')

    # For household grants, these are always available for application
    grant_types = HouseholdGrantApplication.GRANT_TYPE_CHOICES

    context = {
        'active_programs': active_programs,
        'grant_types': grant_types,
        'page_title': 'Available Grants',
    }
    return render(request, 'upg_grants/available_grants.html', context)

```

---


## File: upg_system\__init__.py

**Location:** `upg_system\__init__.py`

```python
# UPG System Django Project
```

---


## File: upg_system\settings.py

**Location:** `upg_system\settings.py`

```python
"""
Django settings for UPG System project.

Generated for Village Enterprise Ultra-Poor Graduation Management System.
For local development and testing.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-upg-system-dev-key-change-in-production-123456789'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'households',
    'business_groups',
    'savings_groups',
    'training',
    'surveys',
    'reports',
    'programs',
    'dashboard',
    'grants',
    'upg_grants',  # UPG-specific grant management
    'forms',  # Dynamic forms system
    'settings_module',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'upg_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_permissions',
                'core.context_processors.system_alerts',
            ],
        },
    },
]

WSGI_APPLICATION = 'upg_system.wsgi.application'


# Database Configuration

# MySQL Configuration (Active)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'upg_management_system',
        'USER': 'root',
        'PASSWORD': '',  # XAMPP default (no password)
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}

# SQLite Configuration (Backup - data migrated to MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMS Configuration
# Africa's Talking API (Primary SMS provider for Kenya)
AFRICAS_TALKING_API_KEY = ''  # Set in production
AFRICAS_TALKING_USERNAME = 'sandbox'  # Change to production username
SMS_SENDER_ID = 'UPG_SYS'

# Twilio API (Fallback SMS provider)
TWILIO_ACCOUNT_SID = ''  # Set in production
TWILIO_AUTH_TOKEN = ''   # Set in production
TWILIO_PHONE_NUMBER = '' # Set in production

# SMS Settings
SMS_ENABLED = True
SMS_BACKEND = 'core.sms.SMSService'  # Can be changed for testing

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Security Settings for Development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# UPG System Specific Settings
UPG_SYSTEM_VERSION = '1.0.0'
UPG_DEFAULT_COUNTRY = 'Kenya'
UPG_DEFAULT_CURRENCY = 'KES'

# Database compatibility settings
import sys
if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
    # Only apply MySQL/MariaDB settings if using MySQL backend
    if DATABASES['default']['ENGINE'] in ['django.db.backends.mysql', 'django.db.backends.mariadb']:
        if 'OPTIONS' not in DATABASES['default']:
            DATABASES['default']['OPTIONS'] = {}
        DATABASES['default']['OPTIONS']['init_command'] = (
            "SET sql_mode='STRICT_TRANS_TABLES'; "
            "SET SESSION innodb_strict_mode=1; "
        )

# Pagination
ITEMS_PER_PAGE = 25

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

---


## File: upg_system\settings_mysql_backup.py

**Location:** `upg_system\settings_mysql_backup.py`

```python
"""
Django settings for UPG System project.

Generated for Village Enterprise Ultra-Poor Graduation Management System.
For local development and testing.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-upg-system-dev-key-change-in-production-123456789'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'households',
    'business_groups',
    'savings_groups',
    'training',
    'surveys',
    'reports',
    'programs',
    'dashboard',
    'grants',
    'upg_grants',  # UPG-specific grant management
    'forms',  # Dynamic forms system
    'settings_module',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'upg_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_permissions',
                'core.context_processors.system_alerts',
            ],
        },
    },
]

WSGI_APPLICATION = 'upg_system.wsgi.application'


# Database - MySQL Configuration (Active)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'upg_management_system',
        'USER': 'root',
        'PASSWORD': '',  # XAMPP default (no password)
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}

# SQLite Configuration (Backup - commented out)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMS Configuration
# Africa's Talking API (Primary SMS provider for Kenya)
AFRICAS_TALKING_API_KEY = ''  # Set in production
AFRICAS_TALKING_USERNAME = 'sandbox'  # Change to production username
SMS_SENDER_ID = 'UPG_SYS'

# Twilio API (Fallback SMS provider)
TWILIO_ACCOUNT_SID = ''  # Set in production
TWILIO_AUTH_TOKEN = ''   # Set in production
TWILIO_PHONE_NUMBER = '' # Set in production

# SMS Settings
SMS_ENABLED = True
SMS_BACKEND = 'core.sms.SMSService'  # Can be changed for testing

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Security Settings for Development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# UPG System Specific Settings
UPG_SYSTEM_VERSION = '1.0.0'
UPG_DEFAULT_COUNTRY = 'Kenya'
UPG_DEFAULT_CURRENCY = 'KES'

# Database compatibility settings
import sys
if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
    # Only apply MySQL/MariaDB settings if using MySQL backend
    if DATABASES['default']['ENGINE'] in ['django.db.backends.mysql', 'django.db.backends.mariadb']:
        if 'OPTIONS' not in DATABASES['default']:
            DATABASES['default']['OPTIONS'] = {}
        DATABASES['default']['OPTIONS']['init_command'] = (
            "SET sql_mode='STRICT_TRANS_TABLES'; "
            "SET SESSION innodb_strict_mode=1; "
        )

# Pagination
ITEMS_PER_PAGE = 25

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

---


## File: upg_system\settings_sqlite_backup.py

**Location:** `upg_system\settings_sqlite_backup.py`

```python
"""
Django settings for UPG System project.

Generated for Village Enterprise Ultra-Poor Graduation Management System.
For local development and testing.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-upg-system-dev-key-change-in-production-123456789'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'households',
    'business_groups',
    'savings_groups',
    'training',
    'surveys',
    'reports',
    'programs',
    'dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'upg_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'upg_system.wsgi.application'


# Database
# For now using SQLite, uncomment MySQL config below when MySQL is properly set up
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MySQL Configuration (uncomment when MySQL is ready)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'upg_management_system',
#         'USER': 'root',
#         'PASSWORD': 'Yimbo001$',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Security Settings for Development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# UPG System Specific Settings
UPG_SYSTEM_VERSION = '1.0.0'
UPG_DEFAULT_COUNTRY = 'Kenya'
UPG_DEFAULT_CURRENCY = 'KES'

# Pagination
ITEMS_PER_PAGE = 25

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

---


## File: upg_system\urls.py

**Location:** `upg_system\urls.py`

```python
"""
URL configuration for UPG System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/', include('accounts.urls')),

    # Main Dashboard
    path('', include('dashboard.urls')),

    # Core modules
    path('households/', include('households.urls')),
    path('business-groups/', include('business_groups.urls')),
    path('savings-groups/', include('savings_groups.urls')),
    path('training/', include('training.urls')),
    path('surveys/', include('surveys.urls')),
    path('reports/', include('reports.urls')),
    path('programs/', include('programs.urls')),
    path('grants/', include('grants.urls')),
    path('upg-grants/', include('upg_grants.urls')),
    path('settings/', include('settings_module.urls')),
    path('core/', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site headers
admin.site.site_header = "UPG Management System"
admin.site.site_title = "UPG Admin"
admin.site.index_title = "Ultra-Poor Graduation Management"
```

---


## File: upg_system\wsgi.py

**Location:** `upg_system\wsgi.py`

```python
"""
WSGI config for upg_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')

application = get_wsgi_application()
```

---

