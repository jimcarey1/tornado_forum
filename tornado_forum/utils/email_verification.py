import aiosmtplib
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from email.mime.text import MIMEText

from settings import SECRET_KEY, SECURITY_PASSWORD_SALT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, MAIL_SERVER, MAIL_PORT

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

async def send_verification_email(recipient_email, verification_link):
    msg = MIMEText(f"Please click on the following link to verify your email: {verification_link}")
    msg['Subject'] = "Email Verification"
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = recipient_email

    try:
        async with aiosmtplib.SMTP(hostname=MAIL_SERVER, port=MAIL_PORT, use_tls=True) as server:
            await server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            await server.send_message(msg)
        print(f'Verification email sent to {recipient_email}')
        return True
    except Exception as exc:
        print(f'Error sending the email: {str(exc)}')
        return False

def confirm_verification_token(token, expiration=600):
    serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=expiration)
        return email
    except SignatureExpired:
        print('Verification link expired')
        return None
    except BadTimeSignature:
        print('Invalid verification link')
        return None
