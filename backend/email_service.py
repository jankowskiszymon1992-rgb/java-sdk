import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
import base64
from typing import List, Dict, Optional
import logging
import html
import re

logger = logging.getLogger(__name__)

# Popularne serwery email - automatyczne wykrywanie
EMAIL_PROVIDERS = {
    'wp.pl': {
        'imap_server': 'imap.wp.pl',
        'imap_port': 993,
        'smtp_server': 'smtp.wp.pl',
        'smtp_port': 465,
        'smtp_use_ssl': True
    },
    'gmail.com': {
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 465,
        'smtp_use_ssl': True
    },
    'o2.pl': {
        'imap_server': 'poczta.o2.pl',
        'imap_port': 993,
        'smtp_server': 'poczta.o2.pl',
        'smtp_port': 465,
        'smtp_use_ssl': True
    },
    'onet.pl': {
        'imap_server': 'imap.poczta.onet.pl',
        'imap_port': 993,
        'smtp_server': 'smtp.poczta.onet.pl',
        'smtp_port': 465,
        'smtp_use_ssl': True
    },
    'interia.pl': {
        'imap_server': 'poczta.interia.pl',
        'imap_port': 993,
        'smtp_server': 'poczta.interia.pl',
        'smtp_port': 465,
        'smtp_use_ssl': True
    },
    'outlook.com': {
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'smtp_use_ssl': False
    },
    'hotmail.com': {
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'smtp_use_ssl': False
    }



def html_to_text(html_content: str) -> str:
    """Konwertuj HTML na czytelny plain text"""
    try:
        # Usuń tagi HTML
        text = re.sub('<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        text = re.sub('<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        
        # Zamień <br> i <p> na nowe linie
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'</p>', '\n\n', text)
        text = re.sub(r'<p[^>]*>', '', text)
        
        # Usuń pozostałe tagi
        text = re.sub('<[^>]+>', '', text)
        
        # Dekoduj HTML entities
        text = html.unescape(text)
        
        # Usuń nadmiar białych znaków
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    except Exception as e:
        logger.error(f"Error converting HTML to text: {e}")
        return html_content


def get_available_folders(email_address: str, password: str, imap_server: str, imap_port: int) -> List[str]:
    """Pobierz listę dostępnych folderów"""
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        
        # Pobierz listę folderów
        status, folders = mail.list()
        
        folder_names = []
        if status == 'OK':
            for folder in folders:
                # Dekoduj nazwę folderu
                folder_str = folder.decode() if isinstance(folder, bytes) else folder
                # Wyciągnij nazwę folderu (ostatnia część po spacji)
                parts = folder_str.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folder_names.append(folder_name)
        
        mail.logout()
        return folder_names
    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        # Fallback do standardowych folderów
        return ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']

}


def detect_email_provider(email_address: str) -> Optional[Dict]:
    """Automatyczne wykrywanie providera na podstawie adresu email"""
    try:
        domain = email_address.split('@')[1].lower()
        return EMAIL_PROVIDERS.get(domain)
    except:
        return None


def test_imap_connection(email_address: str, password: str, imap_server: str, imap_port: int) -> bool:
    """Test połączenia IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.logout()
        return True
    except Exception as e:
        logger.error(f"IMAP connection test failed: {e}")
        return False


def test_smtp_connection(email_address: str, password: str, smtp_server: str, smtp_port: int, use_ssl: bool) -> bool:
    """Test połączenia SMTP"""
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(email_address, password)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"SMTP connection test failed: {e}")
        return False


def fetch_emails(email_address: str, password: str, imap_server: str, imap_port: int, 
                 folder: str = 'INBOX', limit: int = 50) -> List[Dict]:
    """Pobierz emaile z serwera IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select(folder)
        
        # Wyszukaj wszystkie emaile
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        # Pobierz ostatnie N emaili
        email_ids = email_ids[-limit:]
        email_ids.reverse()  # Najnowsze pierwsze
        
        emails = []
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Dekoduj subject
                        subject = decode_header(msg['Subject'])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        # Dekoduj from
                        from_header = decode_header(msg['From'])[0][0]
                        if isinstance(from_header, bytes):
                            from_header = from_header.decode()
                        
                        # Pobierz treść
                        body = ""
                        attachments = []
                        
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                
                                if "attachment" in content_disposition:
                                    # Załącznik
                                    filename = part.get_filename()
                                    if filename:
                                        attachments.append({
                                            'filename': filename,
                                            'size': len(part.get_payload(decode=True) or b'')
                                        })
                                elif content_type == "text/plain" and not body:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        body = str(part.get_payload())
                                elif content_type == "text/html" and not body:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        body = str(part.get_payload())
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                            except:
                                body = str(msg.get_payload())
                        
                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject or '(Brak tematu)',
                            'from': from_header,
                            'date': msg['Date'],
                            'body': body[:500],  # Pierwsze 500 znaków
                            'has_attachments': len(attachments) > 0,
                            'attachments': attachments
                        })
            except Exception as e:
                logger.error(f"Error parsing email {email_id}: {e}")
                continue
        
        mail.logout()
        return emails
        
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        raise Exception(f"Nie udało się pobrać emaili: {str(e)}")


def send_email(from_address: str, password: str, to_address: str, subject: str, 
               body: str, smtp_server: str, smtp_port: int, use_ssl: bool,
               attachments: List[Dict] = None) -> bool:
    """Wyślij email przez SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Załączniki
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {attachment["filename"]}')
                msg.attach(part)
        
        # Połącz i wyślij
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise Exception(f"Nie udało się wysłać emaila: {str(e)}")


def get_email_body(email_address: str, password: str, imap_server: str, 
                   imap_port: int, email_id: str, folder: str = 'INBOX') -> Dict:
    """Pobierz pełną treść emaila wraz z załącznikami"""
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select(folder)
        
        status, msg_data = mail.fetch(email_id.encode(), '(RFC822)')
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Dekoduj headers
                subject = decode_header(msg['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_header = decode_header(msg['From'])[0][0]
                if isinstance(from_header, bytes):
                    from_header = from_header.decode()
                
                # Pobierz treść
                body_text = ""
                body_html = ""
                attachments = []
                
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                file_data = part.get_payload(decode=True)
                                attachments.append({
                                    'filename': filename,
                                    'size': len(file_data),
                                    'data': base64.b64encode(file_data).decode()
                                })
                        elif content_type == "text/plain":
                            try:
                                body_text = part.get_payload(decode=True).decode()
                            except:
                                body_text = str(part.get_payload())
                        elif content_type == "text/html":
                            try:
                                body_html = part.get_payload(decode=True).decode()
                            except:
                                body_html = str(part.get_payload())
                else:
                    try:
                        body_text = msg.get_payload(decode=True).decode()
                    except:
                        body_text = str(msg.get_payload())
                
                mail.logout()
                
                return {
                    'id': email_id,
                    'subject': subject,
                    'from': from_header,
                    'to': msg['To'],
                    'date': msg['Date'],
                    'body_text': body_text,
                    'body_html': body_html,
                    'attachments': attachments
                }
        
        mail.logout()
        return None
        
    except Exception as e:
        logger.error(f"Error fetching email body: {e}")
        raise Exception(f"Nie udało się pobrać treści emaila: {str(e)}")
