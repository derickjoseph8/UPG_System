"""
UPG System Simple Workflow - Layman's Version
Visual diagrams with simple language for non-technical stakeholders
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Frame, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from reportlab.graphics import renderPDF
from datetime import datetime
import os

class SimpleWorkflowPDF:
    def __init__(self, filename="UPG_Simple_Workflow_Diagrams.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.width, self.height = A4

        # Define colors
        self.primary_blue = colors.HexColor('#2E86AB')
        self.light_blue = colors.HexColor('#A7C6DA')
        self.success_green = colors.HexColor('#06A77D')
        self.warning_orange = colors.HexColor('#F77F00')
        self.light_gray = colors.HexColor('#F5F5F5')
        self.dark_gray = colors.HexColor('#333333')

        # Custom styles
        self.title_style = ParagraphStyle(
            'SimpleTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.primary_blue,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.heading_style = ParagraphStyle(
            'SimpleHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.primary_blue,
            spaceAfter=15,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )

        self.subheading_style = ParagraphStyle(
            'SimpleSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.dark_gray,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'SimpleNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        )

        self.caption_style = ParagraphStyle(
            'Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
            fontStyle='Italic'
        )

    def create_process_box(self, width, height, x, y, text, color, drawing):
        """Create a rounded rectangle process box"""
        # Box
        box = Rect(x, y, width, height,
                   fillColor=color,
                   strokeColor=self.dark_gray,
                   strokeWidth=1.5,
                   rx=5, ry=5)
        drawing.add(box)

        # Text
        text_obj = String(x + width/2, y + height/2, text,
                         fontSize=10,
                         fillColor=colors.white if color != colors.white else self.dark_gray,
                         textAnchor='middle',
                         fontName='Helvetica-Bold')
        drawing.add(text_obj)

        return drawing

    def create_arrow(self, x1, y1, x2, y2, drawing, label=""):
        """Create an arrow from (x1,y1) to (x2,y2)"""
        # Line
        line = Line(x1, y1, x2, y2,
                   strokeColor=self.dark_gray,
                   strokeWidth=2)
        drawing.add(line)

        # Arrow head
        arrow_size = 5
        if y2 < y1:  # Downward arrow
            arrow = Polygon([x2, y2,
                           x2-arrow_size, y2+arrow_size,
                           x2+arrow_size, y2+arrow_size],
                          fillColor=self.dark_gray,
                          strokeColor=self.dark_gray)
        elif y2 > y1:  # Upward arrow
            arrow = Polygon([x2, y2,
                           x2-arrow_size, y2-arrow_size,
                           x2+arrow_size, y2-arrow_size],
                          fillColor=self.dark_gray,
                          strokeColor=self.dark_gray)
        elif x2 > x1:  # Rightward arrow
            arrow = Polygon([x2, y2,
                           x2-arrow_size, y2-arrow_size,
                           x2-arrow_size, y2+arrow_size],
                          fillColor=self.dark_gray,
                          strokeColor=self.dark_gray)
        else:  # Leftward arrow
            arrow = Polygon([x2, y2,
                           x2+arrow_size, y2-arrow_size,
                           x2+arrow_size, y2+arrow_size],
                          fillColor=self.dark_gray,
                          strokeColor=self.dark_gray)
        drawing.add(arrow)

        # Label if provided
        if label:
            label_obj = String((x1+x2)/2 + 10, (y1+y2)/2, label,
                             fontSize=8,
                             fillColor=self.dark_gray)
            drawing.add(label_obj)

        return drawing

    def create_circle_icon(self, x, y, radius, color, drawing, number=""):
        """Create a circular icon"""
        circle = Circle(x, y, radius,
                       fillColor=color,
                       strokeColor=self.dark_gray,
                       strokeWidth=2)
        drawing.add(circle)

        if number:
            text = String(x, y-3, number,
                        fontSize=14,
                        fillColor=colors.white,
                        textAnchor='middle',
                        fontName='Helvetica-Bold')
            drawing.add(text)

        return drawing

    def add_cover_page(self):
        """Create simple cover page"""
        self.story.append(Spacer(1, 1*inch))

        title = Paragraph("UPG PROGRAM<br/>SIMPLE VISUAL GUIDE", self.title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=self.dark_gray,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        subtitle = Paragraph("How We Help Households Move Out of Poverty<br/>A 12-Month Journey", subtitle_style)
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.5*inch))

        # Simple explanation box
        intro_text = """
        <b>What is the UPG Program?</b><br/><br/>

        The Ultra-Poor Graduation (UPG) program helps the poorest families in Kenya start their own businesses
        and build better lives. Over 12 months, we provide:<br/><br/>

        <b>&#8226; Training</b> - Learn business skills<br/>
        <b>&#8226; Grants</b> - Money to start a business<br/>
        <b>&#8226; Mentoring</b> - Ongoing support and guidance<br/>
        <b>&#8226; Savings Groups</b> - Save money together<br/><br/>

        This guide shows you exactly how the program works, step by step.
        """

        intro_para = Paragraph(intro_text, self.normal_style)

        intro_table = Table([[intro_para]], colWidths=[6*inch])
        intro_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.light_gray),
            ('PADDING', (0, 0), (-1, -1), 20),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 2, self.primary_blue),
        ]))

        self.story.append(intro_table)
        self.story.append(Spacer(1, 0.5*inch))

        date_text = f"Created: {datetime.now().strftime('%B %d, %Y')}"
        date = Paragraph(date_text, self.caption_style)
        self.story.append(date)

        self.story.append(PageBreak())

    def add_overview_diagram(self):
        """Create the big picture overview"""
        self.story.append(Paragraph("THE BIG PICTURE", self.heading_style))

        intro = Paragraph(
            "Here's how the 12-month UPG program works from start to finish:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.2*inch))

        # Create visual overview
        d = Drawing(500, 400)

        # Start - poor household
        self.create_circle_icon(50, 350, 20, self.warning_orange, d, "1")
        self.create_process_box(120, 40, 80, 335, "POOR\nHOUSEHOLD", colors.white, d)

        # Arrow to training
        self.create_arrow(200, 355, 240, 355, d)

        # Training phase
        self.create_circle_icon(250, 350, 20, self.primary_blue, d, "2")
        self.create_process_box(120, 40, 280, 335, "TRAINING\n(3 months)", self.light_blue, d)

        # Arrow down to business group
        self.create_arrow(340, 335, 340, 280, d)

        # Business group formation
        self.create_circle_icon(250, 260, 20, self.primary_blue, d, "3")
        self.create_process_box(180, 40, 280, 245, "FORM BUSINESS GROUP\n(2-3 people)", self.light_blue, d)

        # Arrow down to first grant
        self.create_arrow(370, 245, 370, 190, d)

        # First grant
        self.create_circle_icon(250, 170, 20, self.success_green, d, "4")
        self.create_process_box(180, 40, 280, 155, "SEED GRANT\n(KES 10,000-25,000)", colors.HexColor('#90EE90'), d)

        # Arrow down to business
        self.create_arrow(370, 155, 370, 100, d)

        # Start business
        self.create_circle_icon(250, 80, 20, self.success_green, d, "5")
        self.create_process_box(180, 40, 280, 65, "START BUSINESS\n& SAVE MONEY", colors.HexColor('#90EE90'), d)

        # Arrow to second grant
        self.create_arrow(280, 85, 120, 85, d)

        # Second grant
        self.create_circle_icon(100, 80, 20, self.success_green, d, "6")
        self.create_process_box(180, 40, 10, 65, "SECOND GRANT\n(Performance Bonus)", colors.HexColor('#90EE90'), d)

        # Arrow down to graduation
        self.create_arrow(100, 65, 100, 10, d)

        # Graduation
        self.create_circle_icon(10, -5, 20, colors.HexColor('#FFD700'), d, "7")
        self.create_process_box(180, 40, 40, -20, "GRADUATION!\nOut of Poverty", colors.HexColor('#FFD700'), d)

        self.story.append(d)
        self.story.append(Spacer(1, 0.2*inch))

        # Legend
        steps = [
            ["Step 1", "We identify very poor households who need help"],
            ["Step 2", "Families attend training to learn business skills"],
            ["Step 3", "2-3 families form a business group together"],
            ["Step 4", "The group receives money (grant) to start a business"],
            ["Step 5", "They start their business and join a savings group"],
            ["Step 6", "Good performers get a second grant to grow"],
            ["Step 7", "After 12 months, families graduate out of poverty!"],
        ]

        legend_data = [['Step', 'What Happens']] + steps

        legend_table = Table(legend_data, colWidths=[1*inch, 5.5*inch])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
        ]))

        self.story.append(legend_table)
        self.story.append(PageBreak())

    def add_actors_diagram(self):
        """Show who does what in the program"""
        self.story.append(Paragraph("WHO DOES WHAT?", self.heading_style))

        intro = Paragraph(
            "Different people have different jobs in the UPG program. Here's who you'll meet:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.3*inch))

        # People table
        people_data = [
            ['Person', 'Their Job', 'What They Do For You'],
            ['MENTOR\n(Field Worker)', 'Your main helper',
             'Visits you at home, teaches training, helps with applications, answers questions'],
            ['FIELD ASSOCIATE\n(Supervisor)', 'Manages mentors',
             'Makes sure mentors are doing their job well, organizes training sessions'],
            ['M&E STAFF\n(Monitors)', 'Tracks progress',
             'Checks if the program is working, creates reports, improves the program'],
            ['PROGRAM MANAGER\n(Decision Maker)', 'Approves grants',
             'Reviews grant applications, decides who gets money, ensures fair distribution'],
            ['ICT ADMIN\n(Computer Expert)', 'Runs the system',
             'Manages the computer system, creates user accounts, fixes technical problems'],
        ]

        people_table = Table(people_data, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
        people_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
        ]))

        self.story.append(people_table)
        self.story.append(Spacer(1, 0.3*inch))

        note = Paragraph(
            "<b>IMPORTANT:</b> Your MENTOR is your main contact person. They will guide you through the entire program!",
            self.normal_style
        )
        note_table = Table([[note]], colWidths=[6.5*inch])
        note_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF4E6')),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.warning_orange),
        ]))
        self.story.append(note_table)

        self.story.append(PageBreak())

    def add_enrollment_process(self):
        """Simple enrollment flowchart"""
        self.story.append(Paragraph("HOW DO I JOIN THE PROGRAM?", self.heading_style))

        intro = Paragraph(
            "Here's the step-by-step process to join the UPG program:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.2*inch))

        # Flowchart
        d = Drawing(500, 500)

        y_pos = 480
        x_center = 250
        box_width = 300
        box_height = 50
        step_gap = 80

        # Step 1
        self.create_circle_icon(x_center - box_width/2 - 30, y_pos - 20, 18, self.primary_blue, d, "1")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 40,
                                "MENTOR VISITS YOUR HOME", self.light_blue, d)

        # Arrow
        self.create_arrow(x_center, y_pos - 40, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 2
        self.create_circle_icon(x_center - box_width/2 - 30, y_pos - 20, 18, self.primary_blue, d, "2")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 40,
                                "ASSESSMENT: Are you very poor?", colors.HexColor('#FFE6E6'), d)

        # Arrow
        self.create_arrow(x_center, y_pos - 40, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 3
        self.create_circle_icon(x_center - box_width/2 - 30, y_pos - 20, 18, self.primary_blue, d, "3")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 40,
                                "PPI SURVEY (10 Questions)", self.light_blue, d)

        # Arrow
        self.create_arrow(x_center, y_pos - 40, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 4
        self.create_circle_icon(x_center - box_width/2 - 30, y_pos - 20, 18, self.success_green, d, "4")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 40,
                                "ENROLLED IN PROGRAM!", colors.HexColor('#90EE90'), d)

        # Arrow
        self.create_arrow(x_center, y_pos - 40, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 5
        self.create_circle_icon(x_center - box_width/2 - 30, y_pos - 20, 18, self.success_green, d, "5")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 40,
                                "YOUR 12-MONTH JOURNEY BEGINS", colors.HexColor('#90EE90'), d)

        self.story.append(d)
        self.story.append(Spacer(1, 0.2*inch))

        # What is PPI explanation
        ppi_text = """
        <b>What is PPI (Poverty Probability Index)?</b><br/><br/>

        The PPI is a simple survey with 10 questions about your household, such as:<br/>
        &#8226; How many rooms does your house have?<br/>
        &#8226; What is your roof made of?<br/>
        &#8226; Do you own any livestock?<br/>
        &#8226; How many children go to school?<br/><br/>

        This helps us identify the families who need the most help. A lower score means you qualify for the program.
        """

        ppi_para = Paragraph(ppi_text, self.normal_style)
        ppi_table = Table([[ppi_para]], colWidths=[6.5*inch])
        ppi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F4F8')),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.primary_blue),
        ]))

        self.story.append(ppi_table)
        self.story.append(PageBreak())

    def add_12month_timeline(self):
        """Visual 12-month timeline"""
        self.story.append(Paragraph("YOUR 12-MONTH JOURNEY", self.heading_style))

        intro = Paragraph(
            "Here's what happens each month during your time in the UPG program:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.3*inch))

        # Timeline data
        timeline_data = [
            ['Month', 'What Happens', 'What You Do'],
            ['1', 'Training Starts\nPPI Survey', 'Attend training classes\nLearn business basics'],
            ['2', 'Form Business Group', 'Find 2-3 partners\nChoose a business idea together'],
            ['3', 'Make Business Plan', 'Write down your business idea\nPlan how to spend money'],
            ['4', 'Apply for First Grant', 'Submit application\nWait for approval'],
            ['5', 'GET MONEY!\n(KES 10,000-25,000)', 'Receive grant\nBuy what you need for business'],
            ['6', 'Start Your Business', 'Open your business\nStart earning money'],
            ['7', 'Check-in Survey', 'Answer questions about progress\nGet help if needed'],
            ['8', 'Join Savings Group', 'Save money with 25 people\nHelp each other'],
            ['9', 'Assessment for 2nd Grant', 'Show how well business is doing\nProve you are saving'],
            ['10', 'Apply for 2nd Grant', 'Apply for performance bonus\nGet money to grow business'],
            ['11', 'Final Check', 'Survey about your progress\nPrepare for graduation'],
            ['12', 'GRADUATION DAY!', 'Celebrate success\nYou are out of poverty!'],
        ]

        # Color code by phase
        colors_map = {
            1: colors.HexColor('#E6F3FF'),  # Light blue - training
            2: colors.HexColor('#E6F3FF'),
            3: colors.HexColor('#E6F3FF'),
            4: colors.HexColor('#FFE6E6'),  # Light red - SB grant
            5: colors.HexColor('#FFE6E6'),
            6: colors.HexColor('#E6FFE6'),  # Light green - operations
            7: colors.HexColor('#E6FFE6'),
            8: colors.HexColor('#E6FFE6'),
            9: colors.HexColor('#FFF4E6'),  # Light orange - PR grant
            10: colors.HexColor('#FFF4E6'),
            11: colors.HexColor('#F0E6FF'),  # Light purple - graduation
            12: colors.HexColor('#FFD700'),  # Gold - celebration
        }

        timeline_table = Table(timeline_data, colWidths=[0.7*inch, 2.5*inch, 3.3*inch])

        style_list = [
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]

        # Add row colors
        for i in range(1, 13):
            style_list.append(('BACKGROUND', (0, i), (-1, i), colors_map[i]))

        timeline_table.setStyle(TableStyle(style_list))

        self.story.append(timeline_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Phase legend
        self.story.append(Paragraph("The Journey is Divided into 5 Phases:", self.subheading_style))

        phases_data = [
            ['Phase', 'Months', 'Focus'],
            ['TRAINING', '1-3', 'Learn business skills & form your group'],
            ['FIRST GRANT', '4-5', 'Get seed money to start business'],
            ['BUSINESS LAUNCH', '6-8', 'Open business & join savings group'],
            ['SECOND GRANT', '9-10', 'Grow your business with more money'],
            ['GRADUATION', '11-12', 'Final assessment & celebrate success!'],
        ]

        phases_table = Table(phases_data, colWidths=[1.5*inch, 1*inch, 4*inch])
        phases_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E6F3FF')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFE6E6')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E6FFE6')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#FFF4E6')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#F0E6FF')),
        ]))

        self.story.append(phases_table)
        self.story.append(PageBreak())

    def add_grant_process(self):
        """Simple grant application process"""
        self.story.append(Paragraph("HOW TO GET YOUR GRANT MONEY", self.heading_style))

        intro = Paragraph(
            "Getting grant money is easy! Just follow these steps with your mentor's help:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.3*inch))

        # Grant process flowchart
        d = Drawing(500, 450)

        y_pos = 430
        x_center = 250
        box_width = 280
        box_height = 45
        step_gap = 75

        # Step 1
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.primary_blue, d, "1")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "Write Your Business Plan\n(with mentor's help)", self.light_blue, d)

        self.create_arrow(x_center, y_pos - 35, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 2
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.primary_blue, d, "2")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "Mentor Submits Application\n(for you)", self.light_blue, d)

        self.create_arrow(x_center, y_pos - 35, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 3
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.warning_orange, d, "3")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "Wait for Review & Approval\n(1-2 weeks)", colors.HexColor('#FFF4E6'), d)

        self.create_arrow(x_center, y_pos - 35, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 4
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.success_green, d, "4")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "APPROVED! Get Money\n(M-Pesa or Bank)", colors.HexColor('#90EE90'), d)

        self.create_arrow(x_center, y_pos - 35, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 5
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.success_green, d, "5")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "Buy Business Items\n& Keep Receipts!", colors.HexColor('#90EE90'), d)

        self.create_arrow(x_center, y_pos - 35, x_center, y_pos - step_gap, d)
        y_pos -= step_gap

        # Step 6
        self.create_circle_icon(x_center - box_width/2 - 25, y_pos - 18, 15, self.primary_blue, d, "6")
        self.create_process_box(box_width, box_height, x_center - box_width/2, y_pos - 35,
                                "Report How You Used Money\n(after 1 month)", self.light_blue, d)

        self.story.append(d)
        self.story.append(Spacer(1, 0.2*inch))

        # Grant amounts
        self.story.append(Paragraph("How Much Money Will I Get?", self.subheading_style))

        grant_data = [
            ['Grant Type', 'When', 'Amount', 'What For'],
            ['SEED BUSINESS\nGRANT (SB)', 'Month 4-5', 'KES 10,000 -\nKES 25,000',
             'Start your business\nBuy inventory, tools, equipment'],
            ['PERFORMANCE\nGRANT (PR)', 'Month 10', 'KES 10,000',
             'Grow your business\nExpand or improve your business'],
        ]

        grant_table = Table(grant_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 2.3*inch])
        grant_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.success_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F5E8')),
        ]))

        self.story.append(grant_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Important notes
        notes_text = """
        <b>IMPORTANT THINGS TO REMEMBER:</b><br/><br/>

        &#10004; <b>Keep ALL receipts</b> - You must show how you spent the money<br/>
        &#10004; <b>Use money for business only</b> - Not for personal expenses<br/>
        &#10004; <b>Start business within 1 month</b> - Don't delay!<br/>
        &#10004; <b>Second grant is a bonus</b> - Only if your business is doing well<br/>
        &#10004; <b>Your mentor helps you</b> - Ask questions anytime!<br/>
        """

        notes_para = Paragraph(notes_text, self.normal_style)
        notes_table = Table([[notes_para]], colWidths=[6.5*inch])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF4E6')),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.warning_orange),
        ]))

        self.story.append(notes_table)
        self.story.append(PageBreak())

    def add_business_group_diagram(self):
        """Explain business groups simply"""
        self.story.append(Paragraph("BUSINESS GROUPS: WORKING TOGETHER", self.heading_style))

        intro = Paragraph(
            "In the UPG program, you don't work alone! You form a business group with 2-3 other people. "
            "Here's how it works:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.2*inch))

        # Visual of 3 people forming a group
        d = Drawing(500, 200)

        # Three people circles
        person_radius = 30
        self.create_circle_icon(100, 120, person_radius, self.light_blue, d)
        person1 = String(100, 115, "Person 1", fontSize=9, textAnchor='middle', fontName='Helvetica-Bold')
        d.add(person1)

        self.create_circle_icon(250, 120, person_radius, self.light_blue, d)
        person2 = String(250, 115, "Person 2", fontSize=9, textAnchor='middle', fontName='Helvetica-Bold')
        d.add(person2)

        self.create_circle_icon(400, 120, person_radius, self.light_blue, d)
        person3 = String(400, 115, "Person 3", fontSize=9, textAnchor='middle', fontName='Helvetica-Bold')
        d.add(person3)

        # Lines connecting them
        line1 = Line(130, 120, 220, 120, strokeColor=self.primary_blue, strokeWidth=2)
        d.add(line1)
        line2 = Line(280, 120, 370, 120, strokeColor=self.primary_blue, strokeWidth=2)
        d.add(line2)

        # Plus signs
        plus1 = String(175, 115, "+", fontSize=20, textAnchor='middle', fillColor=self.primary_blue, fontName='Helvetica-Bold')
        d.add(plus1)
        plus2 = String(325, 115, "+", fontSize=20, textAnchor='middle', fillColor=self.primary_blue, fontName='Helvetica-Bold')
        d.add(plus2)

        # Equals sign and result
        equals = String(250, 40, "=", fontSize=24, textAnchor='middle', fillColor=self.primary_blue, fontName='Helvetica-Bold')
        d.add(equals)

        # Business group box
        self.create_process_box(200, 50, 150, 5, "BUSINESS GROUP", self.success_green, d)
        success = String(250, 25, "(Stronger Together!)", fontSize=10, textAnchor='middle', fillColor=colors.white, fontName='Helvetica-Bold')
        d.add(success)

        self.story.append(d)
        self.story.append(Spacer(1, 0.3*inch))

        # Why business groups
        self.story.append(Paragraph("Why Work in a Group?", self.subheading_style))

        benefits = [
            "&#10004; <b>Share Ideas:</b> Three heads are better than one!",
            "&#10004; <b>Share Work:</b> Divide tasks among members",
            "&#10004; <b>Help Each Other:</b> If one person is sick, others can run the business",
            "&#10004; <b>Get More Money:</b> Bigger groups can get up to KES 25,000",
            "&#10004; <b>Learn Together:</b> Support and encourage each other",
        ]

        for benefit in benefits:
            p = Paragraph(benefit, self.normal_style)
            self.story.append(p)

        self.story.append(Spacer(1, 0.2*inch))

        # Group roles
        self.story.append(Paragraph("Each Person Has a Job:", self.subheading_style))

        roles_data = [
            ['Role', 'What They Do'],
            ['LEADER', 'Makes decisions, represents the group, talks to mentor'],
            ['TREASURER', 'Handles money, keeps records, tracks expenses and income'],
            ['SECRETARY', 'Keeps notes, reminds members of meetings, tracks activities'],
        ]

        roles_table = Table(roles_data, colWidths=[1.5*inch, 5*inch])
        roles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), self.light_gray),
        ]))

        self.story.append(roles_table)
        self.story.append(Spacer(1, 0.2*inch))

        # Business types
        self.story.append(Paragraph("What Kind of Business Can We Start?", self.subheading_style))

        business_types = [
            "&#8226; <b>Retail Shop:</b> Sell goods like soap, sugar, cooking oil",
            "&#8226; <b>Farming:</b> Grow vegetables, maize, or other crops",
            "&#8226; <b>Livestock:</b> Raise chickens, goats, or cows",
            "&#8226; <b>Services:</b> Barbershop, tailoring, phone charging",
            "&#8226; <b>Skilled Trade:</b> Carpentry, mechanics, bricklaying",
        ]

        for biz_type in business_types:
            p = Paragraph(biz_type, self.normal_style)
            self.story.append(p)

        self.story.append(PageBreak())

    def add_savings_group(self):
        """Explain savings groups"""
        self.story.append(Paragraph("SAVINGS GROUPS: SAVING TOGETHER", self.heading_style))

        intro = Paragraph(
            "In Month 8, you'll join a Business Savings Group (BSG) with about 25 people from your community. "
            "This helps you save money and support each other!",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.3*inch))

        # How it works
        self.story.append(Paragraph("How Savings Groups Work:", self.subheading_style))

        steps = [
            ["STEP 1", "Everyone in the group saves a small amount each week or month"],
            ["STEP 2", "The group keeps the money in a safe place (like a lock box)"],
            ["STEP 3", "Members can borrow from the group for emergencies or business needs"],
            ["STEP 4", "Borrowed money must be paid back with small interest"],
            ["STEP 5", "At the end of the year, everyone gets their savings back PLUS interest earned!"],
        ]

        steps_data = [['Step', 'What Happens']] + steps

        steps_table = Table(steps_data, colWidths=[1*inch, 5.5*inch])
        steps_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.success_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
        ]))

        self.story.append(steps_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Benefits
        self.story.append(Paragraph("Why Join a Savings Group?", self.subheading_style))

        benefits_text = """
        <b>BENEFITS:</b><br/><br/>

        &#10004; <b>Build Savings Habit:</b> Save small amounts regularly<br/>
        &#10004; <b>Emergency Fund:</b> Money available when you need it<br/>
        &#10004; <b>Earn Interest:</b> Your money grows over time<br/>
        &#10004; <b>Community Support:</b> Help and be helped by neighbors<br/>
        &#10004; <b>Financial Security:</b> Have money for school fees, medical bills, etc.<br/>
        &#10004; <b>Business Growth:</b> Borrow to expand your business<br/><br/>

        <b>EXAMPLE:</b><br/>
        If you save KES 200 per week for one year, you'll have KES 10,400 PLUS interest!
        """

        benefits_para = Paragraph(benefits_text, self.normal_style)
        benefits_table = Table([[benefits_para]], colWidths=[6.5*inch])
        benefits_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F5E8')),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, self.success_green),
        ]))

        self.story.append(benefits_table)
        self.story.append(PageBreak())

    def add_success_criteria(self):
        """What does success look like"""
        self.story.append(Paragraph("HOW DO I KNOW I'M SUCCEEDING?", self.heading_style))

        intro = Paragraph(
            "Success in the UPG program means you're moving out of poverty! Here are the signs:",
            self.normal_style
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.3*inch))

        # Success indicators
        success_data = [
            ['SUCCESS SIGN', 'WHAT IT MEANS', 'TARGET'],
            ['Your Business is Running', 'Open at least 5 days a week, making sales', 'Every week'],
            ['Earning Money', 'Business makes more than it costs to run', 'KES 500+/week profit'],
            ['Regular Savings', 'Saving money every week/month', 'KES 200+/week'],
            ['Can Buy Food', 'Afford 3 meals a day for family', 'Daily'],
            ['Children in School', 'Able to pay school fees', 'Every term'],
            ['Improved Housing', 'Better roof, more rooms, or repairs', 'By month 12'],
            ['Assets Growing', 'Own more than before (tools, inventory, livestock)', 'By month 12'],
            ['Feel Confident', 'Believe you can support your family', 'Always!'],
        ]

        success_table = Table(success_data, colWidths=[2*inch, 2.8*inch, 1.7*inch])
        success_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.success_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8F0')]),
        ]))

        self.story.append(success_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Graduation criteria
        self.story.append(Paragraph("What Happens at Graduation (Month 12)?", self.subheading_style))

        graduation_text = """
        At the end of 12 months, we check if you've successfully graduated out of poverty:<br/><br/>

        <b>WE MEASURE:</b><br/>
        &#8226; Your PPI score improved (comparing Month 1 to Month 12)<br/>
        &#8226; Your business is still running and profitable<br/>
        &#8226; You're saving money regularly<br/>
        &#8226; Your living conditions improved<br/>
        &#8226; You feel less vulnerable and more secure<br/><br/>

        <b>IF YOU PASS:</b><br/>
        You GRADUATE! This means you're no longer ultra-poor. You have the skills and resources
        to continue improving your life. We celebrate your success!<br/><br/>

        <b>IF YOU NEED MORE HELP:</b><br/>
        Don't worry! We'll connect you with other programs or give you extra support to succeed.
        """

        grad_para = Paragraph(graduation_text, self.normal_style)
        grad_table = Table([[grad_para]], colWidths=[6.5*inch])
        grad_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF9E6')),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#FFD700')),
        ]))

        self.story.append(grad_table)
        self.story.append(PageBreak())

    def add_faq(self):
        """Frequently asked questions"""
        self.story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", self.heading_style))

        faqs = [
            ("Do I have to pay back the grant money?",
             "NO! This is a GRANT, not a loan. You do NOT pay it back. It's free money to help you start your business!"),

            ("What if my business fails?",
             "Your mentor will help you avoid failure. But if it happens, we'll help you learn from it and try again. "
             "Don't give up!"),

            ("Can I choose my own business partners?",
             "YES! You choose who you want to work with in your business group. Pick people you trust and work well with."),

            ("What if I can't attend all training sessions?",
             "Try your best to attend! But if you're sick or have an emergency, tell your mentor. Missing too many "
             "sessions may affect your eligibility for grants."),

            ("How do I get the second grant?",
             "You must show that your business is doing well, you're saving money, and you're following the program rules. "
             "Your mentor will help you apply."),

            ("What happens after I graduate?",
             "You continue running your business! You keep all the money you earned. You can stay in your savings group. "
             "We may check on you occasionally to see how you're doing."),

            ("Can my whole family participate?",
             "The program enrolls one person per household, but your whole family benefits! You can include family members "
             "in planning and running the business."),

            ("What if I don't have a phone?",
             "You don't need a phone to participate! Your mentor will visit you in person. But having a phone helps for "
             "quick questions and reminders."),
        ]

        for i, (question, answer) in enumerate(faqs):
            # Question
            q_text = f"<b>Q{i+1}: {question}</b>"
            q_para = Paragraph(q_text, self.normal_style)

            # Answer
            a_text = f"<b>Answer:</b> {answer}"
            a_para = Paragraph(a_text, self.normal_style)

            # Combined in a box
            qa_table = Table([[q_para], [a_para]], colWidths=[6.5*inch])
            qa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E8F4F8')),
                ('BACKGROUND', (0, 1), (0, 1), colors.white),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1.5, self.primary_blue),
                ('LINEBELOW', (0, 0), (0, 0), 1, colors.grey),
            ]))

            self.story.append(qa_table)
            self.story.append(Spacer(1, 0.15*inch))

        self.story.append(PageBreak())

    def add_contact_info(self):
        """Final page with contacts and encouragement"""
        self.story.append(Spacer(1, 1*inch))

        congrats_style = ParagraphStyle(
            'Congrats',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=self.success_green,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )

        congrats = Paragraph("CONGRATULATIONS!", congrats_style)
        self.story.append(congrats)

        message = Paragraph(
            "You are about to begin an exciting 12-month journey out of poverty. "
            "With hard work, dedication, and support from your mentor and business group, "
            "you WILL succeed!",
            self.normal_style
        )

        message_table = Table([[message]], colWidths=[6*inch])
        message_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F5E8')),
            ('PADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, self.success_green),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        self.story.append(message_table)
        self.story.append(Spacer(1, 0.5*inch))

        # Key reminders
        self.story.append(Paragraph("REMEMBER:", self.subheading_style))

        reminders = [
            "&#10004; Your MENTOR is your friend - ask them questions anytime!",
            "&#10004; Attend ALL training sessions - they prepare you for success",
            "&#10004; Work together with your business group - you're stronger together",
            "&#10004; Save money regularly - even small amounts add up",
            "&#10004; Keep receipts and records - this shows you're responsible",
            "&#10004; Be patient - success takes time, but it WILL come!",
            "&#10004; Never give up - challenges are opportunities to learn",
        ]

        for reminder in reminders:
            p = Paragraph(reminder, self.normal_style)
            self.story.append(p)

        self.story.append(Spacer(1, 0.5*inch))

        # Contact section
        contact_style = ParagraphStyle(
            'Contact',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=8
        )

        self.story.append(Paragraph("NEED HELP?", self.subheading_style))
        self.story.append(Paragraph("Contact your mentor first. They are here to help you succeed!", contact_style))
        self.story.append(Spacer(1, 0.3*inch))

        footer_text = f"UPG Program - Village Enterprise<br/>Helping Families Build Better Lives<br/><br/>" \
                     f"Document Created: {datetime.now().strftime('%B %Y')}"
        footer = Paragraph(footer_text, self.caption_style)
        self.story.append(footer)

    def generate(self):
        """Generate the complete simple PDF"""
        print("Generating Simple UPG Workflow Diagrams...")

        # Add all sections
        self.add_cover_page()
        self.add_overview_diagram()
        self.add_actors_diagram()
        self.add_enrollment_process()
        self.add_12month_timeline()
        self.add_grant_process()
        self.add_business_group_diagram()
        self.add_savings_group()
        self.add_success_criteria()
        self.add_faq()
        self.add_contact_info()

        # Build PDF
        self.doc.build(self.story)
        print(f"[SUCCESS] Simple PDF generated: {self.filename}")
        print(f"[SUCCESS] File size: {os.path.getsize(self.filename) / 1024:.2f} KB")

if __name__ == "__main__":
    pdf = SimpleWorkflowPDF("UPG_Simple_Workflow_Diagrams.pdf")
    pdf.generate()
    print("\nDone! Open 'UPG_Simple_Workflow_Diagrams.pdf' to view the simple guide.")
