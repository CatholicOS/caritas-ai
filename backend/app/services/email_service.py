
"""
Email Service with SMTP and Calendar Invitations
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict
from icalendar import Calendar, Event as ICalEvent, vText
from dotenv import load_dotenv

load_dotenv()


def generate_calendar_invite(
    event_title: str,
    event_date: datetime,
    event_description: str,
    location: str,
    organizer_email: str,
    organizer_name: str
) -> bytes:
    """
    Generate iCalendar (.ics) file content.
    
    Returns: Bytes content of .ics file
    """
    cal = Calendar()
    cal.add('prodid', '-//CaritasAI//Volunteer Event//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')
    
    event = ICalEvent()
    event.add('summary', event_title)
    event.add('description', event_description)
    event.add('location', location)
    event.add('dtstart', event_date)
    event.add('dtend', event_date.replace(hour=event_date.hour + 2))  # 2 hour duration
    event.add('dtstamp', datetime.now())
    
    # Organizer
    organizer = vText(f'MAILTO:{organizer_email}')
    organizer.params['cn'] = vText(organizer_name)
    event['organizer'] = organizer
    
    # Status
    event.add('status', 'CONFIRMED')
    event.add('sequence', 0)
    event.add('priority', 5)
    
    # Add to calendar
    cal.add_component(event)
    
    return cal.to_ical()


def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = None,
    from_name: str = None,
    reply_to: str = None,
    attachment_data: bytes = None,
    attachment_filename: str = None
) -> Dict:
    """
    Send email via SMTP with optional attachment.
    
    Uses Gmail SMTP by default, but can be configured for any SMTP server.
    """
    
    try:
        # Get SMTP credentials from environment
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_username or not smtp_password:
            return {
                "success": False,
                "message": "SMTP credentials not configured"
            }
        
        # Create message
        msg = MIMEMultipart('mixed')
        msg['From'] = f"{from_name} <{from_email or smtp_username}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Attach HTML body
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        html_part = MIMEText(html_content, 'html')
        msg_alternative.attach(html_part)
        
        # Attach file if provided
        if attachment_data and attachment_filename:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(attachment_data)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_filename}'
            )
            msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


def send_registration_confirmation(
    volunteer_name: str,
    volunteer_email: str,
    event_title: str,
    event_date: datetime,
    event_description: str,
    parish_name: str,
    parish_email: str,
    parish_address: str,
    event_id: int
) -> Dict:
    """
    Send registration confirmation email with calendar invite.
    
    Email appears to come from parish (or CaritasAI), with reply-to set to parish.
    """
    
    try:
        # Format date
        event_date_formatted = event_date.strftime("%A, %B %d, %Y at %I:%M %p")
        
        # Generate calendar invite
        calendar_content = generate_calendar_invite(
            event_title=event_title,
            event_date=event_date,
            event_description=event_description or "Volunteer opportunity",
            location=f"{parish_name}, {parish_address}",
            organizer_email=parish_email or "volunteer@caritasai.org",
            organizer_name=parish_name
        )
        
        # Create HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #DC2626, #991B1B); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .event-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #DC2626; }}
                .event-details h3 {{ margin-top: 0; color: #DC2626; }}
                .detail-row {{ margin: 10px 0; }}
                .detail-label {{ font-weight: bold; color: #666; }}
                .button {{ display: inline-block; background: #DC2626; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🙏 Registration Confirmed!</h1>
                    <p>Thank you for serving your community</p>
                </div>
                
                <div class="content">
                    <p>Dear {volunteer_name},</p>
                    
                    <p>Your registration has been confirmed! We're grateful for your commitment to serve.</p>
                    
                    <div class="event-details">
                        <h3>📅 Event Details</h3>
                        
                        <div class="detail-row">
                            <span class="detail-label">Event:</span> {event_title}
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Date & Time:</span> {event_date_formatted}
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Location:</span> {parish_name}<br>
                            {parish_address}
                        </div>
                        
                        {f'<div class="detail-row"><span class="detail-label">Description:</span> {event_description}</div>' if event_description else ''}
                    </div>
                    
                    <p><strong>📎 Calendar Invitation:</strong> A calendar invitation (.ics file) is attached to this email. Click it to add this event to your calendar!</p>
                    
                    <p><strong>📧 Questions?</strong> Reply to this email to contact {parish_name}</p>
                    
                    <div style="text-align: center;">
                        <a href="https://caritasai.wanjohichristopher.com/volunteer" class="button">
                            View More Opportunities
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; font-style: italic; color: #666;">
                        "Whoever is generous to the poor lends to the Lord, and he will repay him for his deed." - Proverbs 19:17
                    </p>
                </div>
                
                <div class="footer">
                    <p>CaritasAI - Serving the Church's Mission of Evangelization Through Service</p>
                    <p>Reply to this email to contact {parish_name}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        result = send_email_smtp(
            to_email=volunteer_email,
            subject=f"✅ Confirmed: {event_title} - {parish_name}",
            html_content=html_content,
            from_email=None,  # Uses SMTP_USERNAME
            from_name=f"CaritasAI - {parish_name}",
            reply_to=parish_email,
            attachment_data=calendar_content,
            attachment_filename="event.ics"
        )
        
        return result
        
    except Exception as e:
        print(f"Error sending confirmation: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


def send_parish_notification(
    parish_name: str,
    parish_email: str,
    volunteer_name: str,
    volunteer_email: str,
    event_title: str,
    event_date: datetime
) -> Dict:
    """
    Notify parish of new volunteer registration.
    """
    
    try:
        event_date_formatted = event_date.strftime("%A, %B %d, %Y at %I:%M %p")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .volunteer-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-row {{ margin: 10px 0; padding: 10px; border-bottom: 1px solid #eee; }}
                .label {{ font-weight: bold; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎉 New Volunteer Registration</h2>
                </div>
                
                <div class="content">
                    <p>Dear {parish_name} Team,</p>
                    
                    <p>Great news! A volunteer has registered for your event.</p>
                    
                    <div class="volunteer-info">
                        <div class="info-row">
                            <span class="label">Volunteer:</span> {volunteer_name}
                        </div>
                        <div class="info-row">
                            <span class="label">Email:</span> <a href="mailto:{volunteer_email}">{volunteer_email}</a>
                        </div>
                        <div class="info-row">
                            <span class="label">Event:</span> {event_title}
                        </div>
                        <div class="info-row">
                            <span class="label">Date:</span> {event_date_formatted}
                        </div>
                    </div>
                    
                    <p>Please reach out to {volunteer_name} to confirm attendance and provide any additional details.</p>
                    
                    <p>God bless,<br>The CaritasAI Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        result = send_email_smtp(
            to_email=parish_email,
            subject=f"New Volunteer: {volunteer_name} - {event_title}",
            html_content=html_content,
            from_name="CaritasAI",
            reply_to=volunteer_email
        )
        
        return result
        
    except Exception as e:
        print(f"Error sending parish notification: {e}")
        return {
            "success": False,
            "message": str(e)
        }
