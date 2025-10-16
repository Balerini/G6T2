import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        # Get credentials from environment variables
        self.smtp_user = os.getenv('GMAIL_USER')  # Your Gmail address
        self.smtp_password = os.getenv('GMAIL_APP_PASSWORD')  # Gmail App Password
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
    
    # ===================== SEND EMAIL NOTIF TO USER(S) WHEN HE IS BEING ASSIGNED A PROJECT =====================
    def send_project_assignment_email(self, to_email, user_name, project_name, project_desc, creator_name, start_date, end_date):
        """Send email notification for project assignment"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = f'New Project Assignment: {project_name}'
            
            # Email body
            html = """
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">New Project Assignment</h2>
                        <p>Hi {user_name},</p>
                        <p>You have been assigned as a collaborator to a new project:</p>
                        
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #1e40af;">{project_name}</h3>
                            <p style="margin: 10px 0;"><strong>Description:</strong> {project_desc or 'No description provided'}</p>
                            <p style="margin: 10px 0;"><strong>Created by:</strong> {creator_name}</p>
                            <p style="margin: 10px 0;"><strong>Start Date:</strong> {start_date}</p>
                            <p style="margin: 10px 0;"><strong>End Date:</strong> {end_date}</p>
                        </div>
                        
                        <p>Please log in to the system to view more details and start working on your tasks.</p>
                        
                        <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                            This is an automated notification. Please do not reply to this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
        
    # ===================== SEND EMAIL NOTIF TO USER(S) WHEN HE IS BEING ASSIGNED A TASK =====================
    def send_task_assignment_email(self, to_email, user_name, task_name, task_desc, project_name, creator_name, start_date, end_date, priority_level):
        """Send email notification for task assignment"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = f'New Task Assignment: {task_name}'
            
            # # Set priority badge color
            # priority_colors = {
            #     'High': '#ef4444',
            #     'Medium': '#f59e0b',
            #     'Low': '#10b981'
            # }
            # priority_color = priority_colors.get(priority_level, '#6b7280')
            
            # Email body
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">New Task Assignment</h2>
                        <p>Hi {user_name},</p>
                        <p>You have been assigned to a new task:</p>
                        
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #1e40af;">{task_name}</h3>
                            <p style="margin: 10px 0;"><strong>Description:</strong> {task_desc or 'No description provided'}</p>
                            {f'<p style="margin: 10px 0;"><strong>Project:</strong> {project_name}</p>' if project_name else ''}
                            <p style="margin: 10px 0;"><strong>Created by:</strong> {creator_name}</p>
                            <p style="margin: 10px 0;"><strong>Start Date:</strong> {start_date}</p>
                            {f'<p style="margin: 10px 0;"><strong>End Date:</strong> {end_date}</p>' if end_date else ''}
                        </div>
                        
                        <p>Please log in to the system to view more details and start working on this task.</p>
                        
                        <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                            This is an automated notification. Please do not reply to this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False

# Create singleton instance
email_service = EmailService()