# UPG Mentoring System User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [User Roles and Permissions](#user-roles-and-permissions)
4. [Getting Started](#getting-started)
5. [Mentoring Dashboard](#mentoring-dashboard)
6. [Logging Mentoring Activities](#logging-mentoring-activities)
7. [Managing Training Sessions](#managing-training-sessions)
8. [Creating Mentoring Reports](#creating-mentoring-reports)
9. [Analytics and Reporting](#analytics-and-reporting)
10. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

The UPG (Ultra Poor Graduation) Mentoring System is a comprehensive platform designed to track, manage, and report on mentoring activities for households participating in poverty graduation programs. This system enables mentors, field associates, and administrators to efficiently coordinate training sessions, document household visits, track phone communications, and generate detailed performance reports.

### Key Features
- **Mentoring Visit Tracking**: Log and monitor on-site, phone, and virtual visits to households
- **Phone Nudge Management**: Record and analyze phone communications with program participants
- **Training Coordination**: Manage training sessions, track attendance, and monitor household enrollments
- **Comprehensive Reporting**: Create periodic mentoring reports with automated statistics
- **Performance Analytics**: View detailed analytics on mentor performance and program effectiveness
- **Multi-role Access**: Different permissions for mentors, field associates, M&E staff, and administrators

---

## 2. System Overview

### System Architecture
The UPG Mentoring System is built on Django framework and consists of the following core components:

**Data Models:**
- **MentoringVisit**: Records of household visits (on-site, phone, virtual)
- **PhoneNudge**: Phone call records with duration tracking
- **MentoringReport**: Periodic reports submitted by mentors
- **Training**: Training modules linked to Business Mentor Cycles
- **TrainingAttendance**: Attendance tracking for each training session
- **HouseholdTrainingEnrollment**: Household enrollment in training programs

**Access URL:**
```
http://127.0.0.1:8000/training/mentoring/
```

---

## 3. User Roles and Permissions

### Mentor
**Permissions:**
- View own mentoring activities only
- Log household visits and phone nudges
- Create and view own mentoring reports
- Mark attendance for assigned trainings
- View households in assigned villages only
- Apply for grants on behalf of households

**Restrictions:**
- Cannot view other mentors' activities
- Cannot export system-wide reports
- Cannot access analytics dashboard

### Field Associate
**Permissions:**
- Log visits and phone nudges
- View mentoring activities across all mentors
- Access full mentoring dashboard
- Manage training sessions
- View comprehensive reports

**Restrictions:**
- Cannot export reports
- Limited analytics access

### M&E Staff (Monitoring & Evaluation)
**Permissions:**
- Full read access to all mentoring data
- Export reports to CSV
- Access advanced analytics
- View mentor performance metrics
- Generate custom filtered reports

**Restrictions:**
- Cannot create or modify mentoring activities
- Cannot log visits or phone nudges

### ICT Admin / Superuser
**Permissions:**
- Full system access
- All data management capabilities
- System configuration
- User management
- Complete analytics access
- Export all data

---

## 4. Getting Started

### Logging In
1. Navigate to `http://127.0.0.1:8000`
2. Enter your username and password
3. Click "Login"

### First-Time Access
Upon first login, you will be directed to the main dashboard based on your role.

**For Mentors:**
- Ensure your profile has assigned villages configured
- Verify you can see your assigned households
- Review the quick start guide on the dashboard

**For Administrators:**
- Verify user roles are correctly assigned
- Confirm mentor profiles have village assignments
- Review system health indicators

### Accessing the Mentoring System
From any page in the system:
1. Navigate to the main menu
2. Click on "Training & Mentoring"
3. Select "Mentoring Dashboard"

Or directly access: `http://127.0.0.1:8000/training/mentoring/dashboard/`

---

## 5. Mentoring Dashboard

The Mentoring Dashboard is the central hub for all mentoring activities.

### Dashboard Components

#### Monthly Statistics Card
Displays current month metrics:
- **Visits This Month**: Total household visits logged
- **Phone Nudges This Month**: Total calls made
- **Trainings This Month**: Number of trainings scheduled/conducted
- **Active Households**: Unique households receiving mentoring support

#### Recent Activities Section
Shows the 10 most recently logged activities:
- **Recent Visits**: Latest household visits with date, household name, and topic
- **Recent Phone Nudges**: Latest calls with duration and contact status
- **Recent Reports**: Latest submitted mentoring reports

#### Mentor Performance Overview (Admin/M&E Only)
Displays performance metrics for all mentors:
- Visit counts per mentor
- Phone nudge activity
- Active households per mentor
- Average call duration

#### Activity Distribution Charts
- **Visit Type Distribution**: Breakdown of on-site, phone, and virtual visits
- **Phone Nudge Type Distribution**: Categories of calls made (reminder, follow-up, support, check-in, business advice)

#### Quick Actions
- **Log Visit**: Record a new household visit
- **Log Phone Nudge**: Record a new phone call
- **Create Report**: Generate a new mentoring report
- **View All Activities**: Access complete visit and phone nudge lists

### Filtering Dashboard Data
The dashboard automatically filters data based on:
- Current month
- User role (mentors see only their own data)
- Assigned villages (for mentors)

---

## 6. Logging Mentoring Activities

### 6.1 Logging a Household Visit

**Access:** Dashboard → "Log Visit" button

**Step-by-Step Process:**

1. **Click "Log Visit"** from the mentoring dashboard
2. **Fill in the Visit Information:**
   - **Visit Name**: Short descriptive title (e.g., "Business Progress Check", "Financial Training Follow-up")
   - **Household**: Select from dropdown (shows only households in your assigned villages)
   - **Visit Topic**: Detailed description of what was discussed
   - **Visit Type**: Choose one:
     - **On-site**: Physical visit to household
     - **Phone**: Phone-based check-in (for short interactions)
     - **Virtual**: Video call or online meeting
   - **Visit Date**: Date the visit occurred
   - **Notes**: Additional details, observations, or action items

3. **Click "Submit"**

**Success Confirmation:**
You will see a message: "Visit '{name}' to {household name} logged successfully on {date}."

**Best Practices:**
- Log visits promptly while details are fresh
- Include specific, actionable notes
- Reference any challenges or support needs identified
- Note any follow-up actions required

### 6.2 Logging a Phone Nudge

**Access:** Dashboard → "Log Phone Nudge" button

**Step-by-Step Process:**

1. **Click "Log Phone Nudge"** from the mentoring dashboard
2. **Fill in the Call Information:**
   - **Household**: Select the household contacted
   - **Nudge Type**: Select call purpose:
     - **Training Reminder**: Upcoming training notification
     - **Follow-up Call**: Post-training or post-visit follow-up
     - **Support Call**: Addressing specific household needs
     - **Regular Check-in**: Routine check on household status
     - **Business Advice**: Specific business guidance
   - **Call Date**: Date of the call
   - **Call Time**: Time the call was made
   - **Duration (Minutes)**: Length of the call
   - **Notes**: Key discussion points and outcomes
   - **Successful Contact**: Check if household was reached

3. **Click "Submit"**

**Success Confirmation:**
"Phone nudge to {household name} logged successfully."

**Best Practices:**
- Log all phone interactions, even unsuccessful attempts
- Record actual duration for accurate metrics
- Uncheck "Successful Contact" if household didn't answer
- Note any changed contact information
- Document action items from the conversation

### 6.3 Viewing Logged Activities

#### View All Visits
**Access:** Dashboard → "View All Visits" or navigate to `/training/mentoring/visits/`

**Features:**
- **Pagination**: 20 visits per page
- **Sorting**: Automatically sorted by most recent first
- **Filtering Options:**
  - Household
  - Mentor (if admin/M&E)
  - Visit Type
  - Date Range (From/To)

**How to Filter:**
1. Use the filter form at the top of the page
2. Select desired filters
3. Click "Filter"
4. Click "Clear" to reset all filters

#### View All Phone Nudges
**Access:** Dashboard → "View All Phone Nudges" or navigate to `/training/mentoring/phone-nudges/`

**Features:**
- **Pagination**: 20 phone nudges per page
- **Statistics Display:**
  - Total Calls
  - Successful Calls
  - Average Duration
- **Filtering Options:**
  - Household
  - Mentor (if admin/M&E)
  - Nudge Type
  - Date Range
  - Contact Status (Successful/Unsuccessful)

**Understanding Phone Nudge Statistics:**
- **Success Rate**: Percentage of calls where contact was made
- **Average Duration**: Mean call length across all selected nudges
- **Type Distribution**: Visual breakdown of call purposes

---

## 7. Managing Training Sessions

### 7.1 Training Overview

Training sessions are organized around Business Mentor (BM) Cycles and consist of multiple modules delivered over time.

**Training Statuses:**
- **Planned**: Training scheduled but not yet started
- **Active**: Currently running training
- **Completed**: Training has concluded
- **Cancelled**: Training was cancelled

### 7.2 Viewing Trainings

**Access:** Navigate to `/training/trainings/` or through the main menu

**Training List Features:**
- Module number and name
- Assigned mentor
- Status badge
- Date range
- Participant count
- Quick action buttons

### 7.3 Managing Training Attendance

**Access:** Training List → Select Training → "Manage Attendance"

**Marking Attendance:**

1. **Navigate to the training details**
2. **Click "Manage Attendance"**
3. **Select the training date** from the available session dates
4. **Mark attendance for each enrolled household:**
   - Check box = Present
   - Uncheck box = Absent
5. **Click "Save Attendance"**

**Attendance Features:**
- Bulk mark all present/absent
- Individual household attendance tracking
- Automatic timestamp recording
- Tracks who marked the attendance

**Attendance Reports:**
- View attendance history by household
- Generate attendance summaries
- Track attendance rates per training module

### 7.4 Household Training Enrollment

**Enrollment Rules:**
- Each household can be enrolled in only ONE training at a time
- Enrollment must be in "enrolled" status to be active
- Households can be marked as:
  - **Enrolled**: Currently participating
  - **Completed**: Successfully finished training
  - **Dropped Out**: Discontinued participation
  - **Transferred**: Moved to different training

**Checking Enrollment:**
1. View household profile
2. Check "Current Training Enrollment" section
3. See training name, enrollment date, and status

**Managing Enrollments (Admin only):**
- Enrollments are typically managed through the household or training detail pages
- Completion dates are automatically recorded when status changes to "completed"

---

## 8. Creating Mentoring Reports

### 8.1 Report Overview

Mentoring reports are periodic summaries of mentor activities, including automated statistics and narrative sections.

**Report Types:**
- **Weekly Reports**: 7-day activity summaries
- **Monthly Reports**: Full month activity summaries
- **Quarterly Reports**: 3-month comprehensive reports

**Who Can Create Reports:**
- Only users with the "Mentor" role can create mentoring reports

### 8.2 Creating a New Report

**Access:** Dashboard → "Create Report" or navigate to `/training/mentoring/reports/create/`

**Step-by-Step Process:**

1. **Click "Create Report"**

2. **Select Report Details:**
   - **Reporting Period**: Choose Weekly, Monthly, or Quarterly
   - **Period Start Date**: First day of the reporting period
   - **Period End Date**: Last day of the reporting period

3. **The System Automatically Calculates:**
   - Number of households visited during the period
   - Total phone nudges made
   - Number of trainings conducted
   - Unique households reached

4. **Fill in Narrative Sections:**

   **Key Activities** (Required):
   - Describe main mentoring activities during the period
   - Include specific training sessions delivered
   - Mention significant household progress
   - Note any special initiatives or programs

   **Challenges Faced** (Optional):
   - Identify barriers encountered
   - Describe difficult situations
   - Note resource constraints
   - Mention weather or access issues

   **Successes Achieved** (Optional):
   - Highlight household improvements
   - Note milestone achievements
   - Describe breakthrough moments
   - Report positive outcomes

   **Next Period Plans** (Optional):
   - Outline upcoming activities
   - Set goals for next reporting period
   - Identify households needing special attention
   - Plan training schedule

5. **Click "Submit Report"**

**Success Confirmation:**
You will be redirected to the report detail page showing your complete report.

### 8.3 Viewing Mentoring Reports

**Access:** Navigate to `/training/mentoring/reports/`

**Features:**

**For Mentors:**
- View only your own reports
- Create new reports
- Filter by period type and date range

**For Admin/M&E Staff:**
- View all mentor reports
- Filter by mentor, period type, and date range
- Export reports to CSV

**Report List Display:**
- Mentor name and email
- Reporting period dates
- Period type badge
- Quick statistics (visits, nudges, trainings, enrollments)
- Submission date
- View detail button

**Filtering Reports:**
1. Use the filter form at the top
2. Select filters:
   - Mentor (admin/M&E only)
   - Period Type
   - Date From/To
3. Click "Filter"
4. Click "Clear" to reset

### 8.4 Viewing Report Details

**Access:** Report List → Click "View" on any report

**Report Detail Page Displays:**

**Header Section:**
- Mentor name
- Reporting period
- Period type badge
- Submission timestamp

**Statistics Dashboard:**
- Households Visited
- Phone Nudges Made
- Trainings Conducted
- New Households Enrolled

**Narrative Sections:**
- Key Activities
- Challenges Faced
- Successes Achieved
- Next Period Plans

**Related Activities:**
- List of all visits during the report period
- List of all phone nudges made
- List of trainings conducted

**Actions:**
- Back to Reports List
- Print Report (browser print function)

---

## 9. Analytics and Reporting

### 9.1 Mentoring Analytics Dashboard

**Access:** Main Menu → "Mentoring Analytics" or `/training/mentoring/analytics/`

**Who Can Access:**
- Superusers
- ICT Admins
- M&E Staff
- Field Associates

### 9.2 Analytics Components

#### Overall Statistics Panel
- **Total Mentors**: Active mentor count
- **Total Visits**: Visits in selected time period
- **Total Phone Nudges**: Calls in selected time period
- **Total Households Reached**: Unique households with interactions

#### Time Period Selector
Choose data range:
- Last 7 days
- Last 30 days (default)
- Last 60 days
- Last 90 days
- Custom date range

#### Mentor Performance Ranking
Top 10 mentors by performance score:
- Performance score calculated as: (visits × 2) + nudges + (households × 3)
- Shows visit counts
- Shows phone nudge counts
- Shows unique households reached
- Ranked from highest to lowest score

#### Monthly Trend Analysis
6-month trend chart showing:
- Visit volume per month
- Phone nudge volume per month
- Comparative monthly performance

#### Visit Type Analysis
Pie chart breaking down visits by type:
- On-site visits
- Phone checks
- Virtual meetings

#### Phone Nudge Analysis
Average call duration by nudge type:
- Training Reminders
- Follow-up Calls
- Support Calls
- Regular Check-ins
- Business Advice

### 9.3 Exporting Data

**Export Mentoring Reports:**

**Access:** Reports List → "Export CSV" button (admin/M&E only)

**Features:**
- Exports all reports matching current filters
- Includes all report fields
- CSV format compatible with Excel
- Filename includes export date

**CSV Contents:**
- Mentor Name
- Reporting Period
- Period Start/End
- All statistics (visits, nudges, trainings, enrollments)
- All narrative sections
- Submission date

**How to Export:**
1. Apply any desired filters to the report list
2. Click "Export CSV" button
3. File downloads automatically
4. Open in Excel or other spreadsheet application

**Export Use Cases:**
- Monthly performance reviews
- Program evaluation reports
- Donor reporting
- Trend analysis
- Performance comparisons

---

## 10. Troubleshooting

### Common Issues and Solutions

#### Issue: Cannot See Any Households
**Possible Causes:**
- No villages assigned to mentor profile
- Households not linked to assigned villages

**Solution:**
1. Contact system administrator
2. Request village assignment to your profile
3. Verify households exist in assigned villages

#### Issue: Cannot Create Mentoring Report
**Possible Cause:**
- User role is not set to "Mentor"

**Solution:**
1. Verify your role with system administrator
2. Only mentors can create reports
3. M&E staff and admins can view but not create

#### Issue: Reports Page Shows No Data
**Possible Cause:**
- No reports have been created yet
- Template issue (previously fixed)

**Solution:**
- Create your first report
- If reports exist but don't display, contact ICT admin
- Check filters are not excluding all reports

#### Issue: Statistics Show Zero Despite Logged Activities
**Possible Causes:**
- Activities logged outside of report date range
- Activities assigned to different mentor

**Solution:**
- Verify activity dates fall within report period
- Check activities are assigned to your user account
- Review activity logs for date accuracy

#### Issue: Cannot Access Analytics Dashboard
**Possible Cause:**
- Insufficient permissions for your role

**Solution:**
- Verify you have M&E staff, field associate, or admin role
- Contact administrator to adjust permissions
- Mentors do not have analytics access by design

#### Issue: Phone Nudge Duration Not Recording
**Possible Cause:**
- Duration field left empty

**Solution:**
- Always fill in the duration field in minutes
- Round up to nearest minute for short calls
- If using auto-tracked duration, ensure seconds field is populated

#### Issue: Training Attendance Not Saving
**Possible Causes:**
- JavaScript error
- Network connectivity issue
- Missing training date selection

**Solution:**
1. Ensure you selected a training date
2. Check browser console for errors
3. Refresh page and try again
4. Contact ICT support if persists

### Getting Help

**For Technical Issues:**
- Contact ICT Administrator
- Email: [system-admin@organization.org]
- Include screenshots and error messages

**For Training and Usage Questions:**
- Contact M&E Staff
- Refer to this user manual
- Request additional training sessions

**For Data Issues:**
- Contact Field Associate supervisor
- Report discrepancies immediately
- Provide specific details (dates, household names, activities)

### System Maintenance

**Regular Maintenance Schedule:**
- Weekly database backups
- Monthly system updates
- Quarterly data audits

**Planned Downtime Notifications:**
- Announced 48 hours in advance
- Typically scheduled during off-hours
- Posted on system login page

---

## Appendix A: Quick Reference Guide

### Common URLs
- **Mentoring Dashboard**: `/training/mentoring/dashboard/`
- **Mentoring Reports**: `/training/mentoring/reports/`
- **Create Report**: `/training/mentoring/reports/create/`
- **Log Visit**: `/training/mentoring/log-visit/`
- **Log Phone Nudge**: `/training/mentoring/log-phone-nudge/`
- **Visit List**: `/training/mentoring/visits/`
- **Phone Nudge List**: `/training/mentoring/phone-nudges/`
- **Analytics**: `/training/mentoring/analytics/`

### Visit Types
- **On-site**: Physical household visit
- **Phone**: Phone-based check-in
- **Virtual**: Video call or online meeting

### Phone Nudge Types
- **Reminder**: Training reminder
- **Follow-up**: Follow-up call
- **Support**: Support call
- **Check-in**: Regular check-in
- **Business Advice**: Business advice

### Reporting Periods
- **Weekly**: 7-day period
- **Monthly**: Calendar month
- **Quarterly**: 3-month period

### Training Statuses
- **Planned**: Not yet started
- **Active**: Currently running
- **Completed**: Finished
- **Cancelled**: Not proceeding

### User Roles
- **Mentor**: Field mentors
- **Field Associate**: Field supervisors
- **M&E Staff**: Monitoring & evaluation team
- **ICT Admin**: Technical administrators
- **Superuser**: Full system access

---

## Appendix B: Best Practices

### Data Entry Guidelines
1. **Log activities within 24 hours** for accuracy
2. **Use consistent terminology** in notes and descriptions
3. **Be specific** in activity descriptions
4. **Include actionable items** in notes
5. **Verify dates** before submitting

### Reporting Best Practices
1. **Submit reports on time** at end of each period
2. **Include quantitative and qualitative information**
3. **Be honest about challenges** for proper support
4. **Highlight successes** for program learning
5. **Set realistic plans** for next period

### Phone Communication Guidelines
1. **Schedule calls** when households are available
2. **Keep records** of all communication attempts
3. **Follow up** on action items from previous calls
4. **Respect household time** - be concise
5. **Document unsuccessful attempts** for tracking

### Household Visit Best Practices
1. **Plan visits in advance** with household
2. **Come prepared** with relevant materials
3. **Listen actively** to household concerns
4. **Take notes** during or immediately after visits
5. **Set clear next steps** before leaving

---

## Document Information

**Document Title**: UPG Mentoring System User Manual

**Version**: 1.0

**Last Updated**: 2025-10-03

**Author**: UPG System Development Team

**For Questions or Feedback**: Contact your system administrator

---

**End of User Manual**
