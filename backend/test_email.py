# file only to test backend if needed

from dotenv import load_dotenv
load_dotenv() 

from email_service import email_service

email_service.send_project_assignment_email(
    to_email='leexin.tan.2023@scis.smu.edu.sg',  # Change to your actual email
    user_name='Test User',
    project_name='Test Project',
    project_desc='This is a test project',
    creator_name='Admin',
    start_date='2025-01-01',
    end_date='2025-12-31'
)