# My Accountant

Backend for a two-sided marketplace connecting clients with accountants. Clients post services they need and accountants post services they offer; bookings move through an accept/decline flow, and once confirmed the two parties get a private real-time chat with presence and notifications.

## Features

- User accounts with email login, roles (client / accountant), and social login (Google, Facebook)
- Service listings — offered by accountants or requested by clients — with categories and file attachments
- Booking workflow: request → pending → confirmed / declined
- Real-time chat with typing indicators, online presence, and read tracking
- In-app notifications delivered over WebSockets
- Auto-generated API docs

## Tech stack

- **Framework:** Django 5, Django REST Framework
- **Real-time:** Django Channels (ASGI, WebSockets)
- **Database:** PostgreSQL
- **Cache / channel layer:** Redis
- **Auth:** JWT (SimpleJWT), allauth + dj-rest-auth

## Getting started

Requires Python 3.11+, PostgreSQL, and Redis.

```bash
python -m venv venv
source venv/bin/activate            # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                # then fill in the values
python manage.py migrate
python manage.py createsuperuser
```

Run the server (ASGI — required for WebSockets):

```bash
daphne my_accountant_project.asgi:application
```

API documentation is available at `/swagger/` and `/redoc/`.

## Project structure

```
accounts/       Users, authentication, OTP flows
profiles/       Extended user profiles
services/       Marketplace listings
bookings/       Booking workflow
chat/           Chat rooms and message history
realtime/       WebSocket consumer, presence, live delivery
notifications/  Notifications
learning/       Course content
```
