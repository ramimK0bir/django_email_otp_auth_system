# BD-Pay

A Django-based payment web application with user authentication, OTP verification, and password reset functionality.

## Features

- User Signup & Login
- OTP-based email verification
- Password reset via OTP
- Role-based access control
- SMTP email support

## Setup

1. Clone the repository
```
git clone https://github.com/userAnonymous/bdpay.git
cd bdpay
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory
```
SECRET_KEY=your-secret-key
SMTP_SENDER_EMAIL=your-email
SMPT_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_MAIL_SERVER=your-smtp-server
```

4. Run migrations
```
python manage.py migrate
```
> Default site settings will be created automatically after migration.

5. Start the server
```
python manage.py runserver
```

## License

MIT License — see [LICENSE.txt](LICENSE.txt)
