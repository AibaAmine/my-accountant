# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"My Accountant" — Django + DRF backend connecting clients with accountants. Marketplace of services, bookings, real-time chat, and notifications. Backend-only (API + WebSockets); frontend is separate. Target market is Algeria (services carry `wilaya` location codes).

## Commands

Windows, PowerShell. Activate venv first: `.\venv\Scripts\Activate.ps1`

```powershell
python manage.py runserver              # HTTP dev server (WSGI, no WebSockets)
daphne my_accountant_project.asgi:application   # ASGI server — needed for WebSockets/chat
python manage.py makemigrations <app>   # create migrations after model change
python manage.py migrate
python manage.py createsuperuser
python manage.py test                   # all tests
python manage.py test bookings          # one app
python manage.py test bookings.tests.TestClass.test_method   # single test
python manage.py collectstatic          # whitenoise static build (deploy)
```

WebSocket features require a running **Redis** (channel layer + presence), default `redis://127.0.0.1:6379/1`. `runserver` won't serve WebSockets — use `daphne` for anything touching chat/notifications/presence.

## External dependencies

- **PostgreSQL** — main DB. Config via `DATABASE_URL` (takes priority) or discrete `DB_*` env vars.
- **Redis** — Channels layer, presence tracking, online status.
- **Brevo** (via `django-anymail`) — production email. In `DEBUG` mode email prints to console.
- **Google + Facebook OAuth** — social login via allauth.
- Env loaded from `.env` (gitignored, not committed). Requires: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, DB vars, `ACCESS_TOKEN_LIFETIME_MINUTES`, `REFRESH_TOKEN_LIFETIME_DAYS`, OAuth keys, `BREVO_API_KEY`. Missing `ACCESS_TOKEN_LIFETIME_MINUTES`/`REFRESH_TOKEN_LIFETIME_DAYS` crashes at settings load (`int()` on `None`).

## Architecture

Django apps under project root, wired in `my_accountant_project/`.

- **accounts** — custom `User` model (`AUTH_USER_MODEL = accounts.User`, table `users`). UUID PK, email is login (no username), `user_type` (client/accountant/academic/admin), OTP models for email verify + password reset. Auth via `dj-rest-auth` + `allauth` + custom serializers/adapters.
- **profiles** — extended user profile data.
- **services** — `Service` marketplace listing. `service_type` is `needed` (client asks) or `offered` (accountant provides). M2M categories, JSON fields for tasks/conditions, `wilaya` location codes, attachments in separate model.
- **bookings** — `Booking` links client + accountant + service. Flow: `pending` → `confirmed`/`declined`. Accepting a booking auto-creates a DM chat room. See `BOOKING_FLOW_SUMMARY.md`.
- **chat** — `ChatRooms`, `ChatMembers`, `ChatMessages`, `UserRoomLastSeen`. REST views for room/message history; live messaging is in `realtime`.
- **notifications** — `Notification` model + `utils.send_notification_to_user()` which pushes over the channel layer to group `user_<id>`.
- **realtime** — WebSocket layer. This is where live chat, presence, and notifications actually run.
- **learning** — course/learning content (`Service.is_course` ties in).

### Authentication

- **REST**: JWT (`simplejwt`) is the default DRF auth class. Default permission is `IsAuthenticatedOrReadOnly`. Tokens at `/api/token/` + `/api/token/refresh/`; dj-rest-auth flows under `/auth/`.
- **WebSocket**: custom `my_accountant_project/auth_middleware.py` (`JWTAuthMiddlewareStack`) reads JWT from the `Authorization: Bearer` header or `?token=` query param, sets `scope["user"]`. Anonymous connections are closed with code `4001`.

### Real-time (important)

Single WebSocket endpoint: **`ws/global/`** → `realtime/consumers.py::GlobalConsumer`. One connection per user carries everything (chat across all rooms, presence, notifications) — the client joins/leaves rooms with in-band messages, not separate sockets.

`GlobalConsumer` is composed from mixins — behavior is split across files, not all in `consumers.py`:
- `realtime/chat_handlers.py` — `ChatHandlers`: join/leave/send/typing message handlers.
- `realtime/event_handlers.py` — `EventHandlers`: channel-layer event fan-out (`user.status.changed`, `new.notification`, etc.).
- `realtime/db.py` — `DatabaseOperations`: `@database_sync_to_async` DB access.

Inbound message dispatch is by `type` field in `receive()`: `join_room`, `leave_room`, `send_message`, `typing`. On connect, user is added to group `user_<id>`, marked online in Redis (`global_user_status` hash), and shared rooms are notified. Presence uses raw Redis sets/hashes via `channel_layer.connection(0)`.

Note: `chat/consumers.py` and `chat/routing.py` also exist but the active/registered WebSocket route (`asgi.py` → `realtime.routing`) uses only `realtime`'s `GlobalConsumer`. Treat `realtime` as the source of truth for live features.

### API docs

Swagger/ReDoc auto-generated (`drf-yasg`) at `/swagger/`, `/redoc/`, and `/` (root). Hand-written reference in `API_DOCUMENTATION.md`.

## Conventions

- Models use **UUID primary keys** and explicit `db_table` names (e.g. `users`, `services`, `booking`). Match this for new models.
- `created_at`/`updated_at` timestamps on most models.
- App URLs are included per-app; note `bookings.urls` is mounted at root (`""`), not under a prefix.
- `CORS_ALLOW_ALL_ORIGINS = True` currently (dev-permissive).
