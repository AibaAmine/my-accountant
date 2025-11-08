# My Accountant Platform - Complete API Documentation

## Overview

This documentation covers all APIs for the My Accountant platform, including authentication, user management, profile management, services marketplace, booking system, and course management. The platform uses JWT (JSON Web Tokens) for authentication and supports email-based registration with OTP verification, social login (Google/Facebook), password reset, and comprehensive role-based service management.

### Platform Features

- **Service Marketplace**: Clients request services, accountants offer services
- **Course System**: Accountants create courses, academics book and enroll in courses
- **Booking System**: Role-based booking flows for services and courses
- **Real-time Chat**: WebSocket-based messaging with role-based access
- **Notifications**: Real-time notifications for bookings and messages

### User Roles

- **Client**: Books regular services from accountants
- **Accountant**: Offers services and courses, manages bookings
- **Academic**: Browses and books courses, participates in course chat groups
- **Admin**: Full platform management

## Base URL

```
https://my-accountant-j02f.onrender.com
```

## Authentication Method

- **Primary**: JWT (JSON Web Tokens)
- **Token Format**: Bearer Token
- **Header**: `Authorization: Bearer <access_token>`

**Note**: All endpoints marked with 🔒 require authentication.

## Token Lifecycle

- **Access Token**: Configurable lifetime (default: set in environment)
- **Refresh Token**: Configurable lifetime (default: set in environment)
- **Refresh Rotation**: Configurable (set in environment)

---

## API Endpoints

### 1. User Registration

#### Register New User

**Endpoint:** `POST /auth/registration/`

**Description:** Creates a new user account. The account will be inactive until email verification is completed using the OTP endpoints.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password1": "securepassword123",
  "password2": "securepassword123",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "user_type": "client"
}
```

**User Types:**

- `client` - Regular client user seeking accounting services
- `accountant` - Professional accountant offering services
- `academic` - Academic/instructor for educational content (limited access to marketplace)
- `admin` - Administrator with full platform access

**Response (Success - 201):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "pk": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "client",
    "phone": "+1234567890",
    "is_email_verified": false,
    "account_status": "inactive"
  }
}
```

**Response (Error - 400):**

```json
{
  "email": ["A user with that email address already exists."],
  "password1": ["This password is too common."]
}
```

**Important Note:** No verification email is sent automatically during registration. Users must call the `/auth/send-email-otp/` endpoint to receive an OTP for email verification.

---

### 2. Email Verification

#### Send Email OTP

**Endpoint:** `POST /auth/send-email-otp/`

**Description:** Sends a 6-digit OTP code to the user's email for verification.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (Success - 200):**

```json
{
  "detail": "OTP sent to your email"
}
```

**Response (Error - 400):**

```json
{
  "email": ["User not found."]
}
```

**Note:** OTP expires in 10 minutes.

#### Verify Email OTP

**Endpoint:** `POST /auth/verify-email-otp/`

**Description:** Verifies the OTP code and activates the user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

**Response (Success - 200):**

```json
{
  "detail": "Email verified successfully"
}
```

**Response (Error - 400):**

```json
{
  "otp_code": ["Invalid OTP."]
}
```

---

### 3. User Login

#### Email/Password Login

**Endpoint:** `POST /auth/login/`

**Description:** Authenticates user with email and password.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (Success - 200):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "pk": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "client",
    "company_name": "",
    "job_title": "",
    "phone": "+1234567890",
    "bio": "",
    "profile_picture_url": null,
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
}
```

**Response (Error - 400):**

```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

### 4. Social Authentication

#### Google Login

**Endpoint:** `POST /auth/google/`

**Description:** Authenticates user with Google OAuth2.

**Request Body:**

```json
{
  "access_token": "google_access_token_here"
}
```

#### Facebook Login

**Endpoint:** `POST /auth/facebook/`

**Description:** Authenticates user with Facebook OAuth2.

**Request Body:**

```json
{
  "access_token": "facebook_access_token_here"
}
```

**Response (Success - 200):** Same as email/password login

---

### 5. Token Management

#### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Description:** Gets a new access token using the refresh token.

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Success - 200):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Token Pair

**Endpoint:** `POST /api/token/`

**Description:** Alternative endpoint for getting tokens with email/password.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

---

### 6. Password Reset

#### Request Password Reset

**Endpoint:** `POST /auth/password-reset/request/`

**Description:** Sends a password reset OTP to user's email.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (Success - 200):**

```json
{
  "message": "OTP sent to email."
}
```

#### Verify Password Reset

**Endpoint:** `POST /auth/password-reset/verify/`

**Description:** Verifies OTP and sets new password.

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "newsecurepassword123"
}
```

**Response (Success - 200):**

```json
{
  "detail": "Password reset successfully."
}
```

---

**Response (Success - 200):** Updated user object

#### Logout 🔒

**Endpoint:** `POST /auth/logout/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Logs out the user by blacklisting the refresh token. The access token remains valid until its natural expiration.

**Request Body (Optional):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Success - 200):**

```json
{
  "detail": "Successfully logged out."
}
```

**Important Notes:**

- **Refresh Token**: Immediately blacklisted and cannot be used to obtain new access tokens
- **Access Token**: Continues to work until its configured expiration time
- **Security**: This is standard JWT behavior - refresh tokens are stateful (can be blacklisted), access tokens are stateless (expire naturally)
- **Best Practice**: Frontend should clear all stored tokens and redirect to login after successful logout

#### Change Password 🔒

**Endpoint:** `POST /auth/password/change/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Changes the authenticated user's password.

**Request Body:**

```json
{
  "old_password": "currentpassword123",
  "new_password1": "newsecurepassword123",
  "new_password2": "newsecurepassword123"
}
```

**Response (Success - 200):**

```json
{
  "detail": "New password has been saved."
}
```

**Response (Error - 400):**

```json
{
  "old_password": ["Invalid password."],
  "new_password2": ["The two password fields didn't match."]
}
```

---

### 8. Profile Management

The platform supports role-based profile management for different user types. Each user type has its own profile structure. Profiles are **automatically created** when a user registers using Django signals, so there's no need for explicit profile creation endpoints.

#### Get/Update My Profile 🔒

**Endpoint:** `GET/PUT/PATCH /profiles/me/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Unified endpoint to retrieve or update the authenticated user's profile. The endpoint automatically detects the user type (accountant, client, or academic) and returns the appropriate profile. The profile is automatically created when the user registers.

**Request Body (PUT/PATCH) - Accountant:**

Available fields to update:

- `profile_picture` - Profile image file
- `phone` - Phone number (e.g., "+213796269301")
- `location` - Location/city (e.g., "Alger")
- `bio` - Biography/description text
- `upload_files` - Multiple files (certifications, documents) - send this field multiple times, once per file

Example JSON request:

```json
{
  "phone": "+213796269301",
  "location": "Alger",
  "bio": "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر"
}
```

Example form-data request with files:

```
Content-Type: multipart/form-data

phone: "+213796269301"
location: "Alger"
bio: "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر"
profile_picture: image.jpg
upload_files: file1.pdf
upload_files: file2.pdf
```

---

**Request Body (PUT/PATCH) - Client (Economic Operator):**

Available fields to update:

- `profile_picture` - Profile image file
- `phone` - Phone number (e.g., "+213796269301")
- `location` - Location/city (e.g., "Alger")
- `activity_type` - Type of business/activity (e.g., "عمل اقتصادي")
- `upload_files` - Multiple files (business documents, registrations) - send this field multiple times, once per file

Example JSON request:

```json
{
  "phone": "+213796269301",
  "location": "Alger",
  "activity_type": "عمل اقتصادي"
}
```

Example form-data request with files:

```
Content-Type: multipart/form-data

phone: "+213796269301"
location: "Alger"
activity_type: "عمل اقتصادي"
profile_picture: image.jpg
upload_files: file1.pdf
upload_files: file2.pdf
```

> **Note:** To upload multiple files, send the `upload_files` field multiple times (once per file), not as an array.

---

**Request Body (PUT/PATCH) - Academic:**

Available fields to update:

- `profile_picture` - Profile image file
- `phone` - Phone number (e.g., "+213796269301")
- `location` - Location/city (e.g., "Alger")
- `bio` - Biography/description text
- `upload_files` - Multiple files (academic credentials, certificates) - send this field multiple times, once per file

Example JSON request:

```json
{
  "phone": "+213796269301",
  "location": "Alger",
  "bio": "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر"
}
```

Example form-data request with files:

```
Content-Type: multipart/form-data

phone: "+213796269301"
location: "Alger"
bio: "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر"
profile_picture: image.jpg
upload_files: file1.pdf
upload_files: file2.pdf
```

> **Note:** To upload multiple files, send the `upload_files` field multiple times (once per file), not as an array.

---

**Response (Success - 200) - Accountant Example:**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "abdou8@gmail.com",
    "full_name": "عبد الرحمن القيّم",
    "user_type": "accountant",
    "phone": "+213796269301",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/media/profile_pictures/accountants/image.jpg",
  "phone": "+213796269301",
  "location": "Alger",
  "bio": "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر",
  "all_attachments": [
    {
      "attachment_id": "uuid-here",
      "url": "https://example.com/media/profile_attachments/cert.pdf",
      "filename": "شهادة خبرة مكتب محاسبي.pdf",
      "size": 245760,
      "uploaded_at": "2025-01-01T12:00:00Z"
    },
    {
      "attachment_id": "uuid-here",
      "url": "https://example.com/media/profile_attachments/license.pdf",
      "filename": "نسخة من رخصتي كمكتب محاسبي معتمد.pdf",
      "size": 134567,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 2,
  "all_services": [
    {
      "id": "uuid-here",
      "service_type": "offered",
      "title": "الضمانة",
      "description": "اسم الشركة او الصيل المتوقع...",
      "price": "14.02",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

---

**Response (Success - 200) - Client (Economic Operator) Example:**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "algerietelecom@gmail.com",
    "full_name": "اتصالات الجزائر",
    "user_type": "client",
    "phone": "+213796269301",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/media/profile_pictures/clients/image.jpg",
  "phone": "+213796269301",
  "location": "Alger",
  "activity_type": "عمل اقتصادي",
  "all_attachments": [
    {
      "attachment_id": "uuid-here",
      "url": "https://example.com/media/profile_attachments/doc.pdf",
      "filename": "شهادة تجارية بالعربي.pdf",
      "size": 512000,
      "uploaded_at": "2025-01-01T12:00:00Z"
    },
    {
      "attachment_id": "uuid-here",
      "url": "https://example.com/media/profile_attachments/doc2.pdf",
      "filename": "نسخة من رخصتني كعمتب محاسبي معتمد.pdf",
      "size": 245000,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 2,
  "all_services": [
    {
      "id": "uuid-here",
      "service_type": "needed",
      "title": "الخدمة",
      "description": "اسم الشركة او الصيل المتوقع...",
      "price": "14.02",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

---

**Response (Success - 200) - Academic Example:**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "algerietelecom@gmail.com",
    "full_name": "الاسم الكامل",
    "user_type": "academic",
    "phone": "+213796269301",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/media/profile_pictures/academics/image.jpg",
  "phone": "+213796269301",
  "location": "Alger",
  "bio": "أنا محمم وأجهة مستخدم تجربة مستخدم مبدع ومقيم في الجزائر",
  "all_attachments": [
    {
      "attachment_id": "uuid-here",
      "url": "https://example.com/media/profile_attachments/cert.pdf",
      "filename": "الدورة",
      "size": 345678,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 1,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Key Features:**

- **Unified Endpoint**: One endpoint (`/profiles/me/`) for all user types - no need to know the user type in advance
- **Automatic Detection**: The API automatically detects the user type and returns the appropriate profile
- **Automatic Profile Creation**: Profiles are created automatically via Django signals when users register
- **Service Integration**: Accountant and Client profiles include an `all_services` field showing all active services created by the user (Academic profiles do not have services)
- **Multiple File Attachments**: Profiles support multiple file uploads using the `upload_files` field with form-data
- **File Downloads**: All attachment files are directly downloadable via their URL paths
- **File Metadata**: Each attachment includes filename, size, upload timestamp, and unique ID
- **Attachment Count**: `attachments_count` field shows total number of files attached to profile
- **File Handling**: Profile pictures and attachments are properly handled with full URLs in responses
- **Read-Only Fields**: `profile_id`, `user`, `all_attachments`, `attachments_count`, `created_at`, and `updated_at` are automatically managed

````

---

## 9. Services Management

The Services Management system allows clients to post service requests and accountants to offer their services. The system is role-based where:

- **Clients** create "needed" services (service requests)
- **Accountants** create "offered" services (service offerings)

### 1. Service Categories

#### Get Service Categories 🔒

**Endpoint:** `GET /services/categories/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves a list of all active service categories for dropdown/selection lists. These categories are managed by administrators.

**Response (Success - 200):**

```json
[
  {
    "id": "uuid-here",
    "name": "Tax Preparation",
    "is_active": true,
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  {
    "id": "uuid-here",
    "name": "Bookkeeping",
    "is_active": true,
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
]
````

#### Get Category Details 🔒

**Endpoint:** `GET /services/categories/{category_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get detailed information about a specific category.

**Response (Success - 200):**

```json
{
  "id": "uuid-here",
  "name": "Tax Preparation",
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### 2. Service Creation

#### Create New Service 🔒

**Endpoint:** `POST /services/create/`

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Description:** Creates a new service with support for multiple file attachments. The service type is automatically determined based on user role:

- **Clients** create `service_type: "needed"` (service requests)
- **Accountants** create `service_type: "offered"` (service offerings)

**Request Body (Form Data):**

**Example for Accountants (Offering Regular Services):**

```json
{
  "title": "Tax Declaration Preparation (IRG, TVA, IBS)",
  "description": "I offer monthly tax declaration preparation services for companies and traders including:\n• Individual Income Tax (IRG)\n• Value Added Tax (TVA)\n• Corporate Income Tax (IBS)\nI analyze documents, calculate due amounts, and fill declarations according to Algerian tax laws.",
  "is_course": false,
  "categories": ["uuid1", "uuid2"],
  "location": "16",
  "estimated_duration": 2,
  "duration_unit": "days",
  "estimated_duration_description": "2 to 4 days depending on business size and available documents",
  "price": 8000,
  "price_description": "Starting from 8000 DZD - Price negotiable based on file size",
  "delivery_method": "online",
  "upload_files": [file1, file2, file3]
}
```

**Example for Accountants (Creating Courses):**

```json
{
  "title": "Accounting Fundamentals Course",
  "description": "Learn the basics of accounting in 8 weeks. This comprehensive course covers bookkeeping, financial statements, tax preparation, and practical exercises. Perfect for beginners wanting to start a career in accounting.",
  "is_course": true,
  "categories": ["uuid1"],
  "location": "online",
  "estimated_duration": 8,
  "duration_unit": "weeks",
  "estimated_duration_description": "8 weeks with weekly 2-hour sessions",
  "price": 15000,
  "price_description": "15000 DZD for the complete 8-week course",
  "delivery_method": "online"
}
```

**Important Note for Accountants:**

- **Regular Services**: Set `is_course: false` or omit the field (defaults to false)
- **Courses**: **Must** set `is_course: true` to create a course for academics
- Courses will only be visible to academic users, regular services only to clients

**Multiple File Upload:**

- Use `upload_files` field with multiple files
- In Postman: Add multiple `upload_files` fields of type "File"
- In form-data: Use the same key `upload_files` multiple times
- Supported formats: PDF, DOC, DOCX, images, etc.

**Example for Clients (Requesting Services):**

```json
{
  "title": "Need Tax Declaration Preparation (IRG, TVA, IBS)",
  "description": "We are a food distribution company based in Oran looking for a certified accountant to prepare and submit our monthly tax declarations (IRG, TVA, IBS) on a regular basis",
  "categories": ["uuid1"],
  "location": "31",
  "tasks_and_responsibilities": [
    "Collect and analyze financial documents",
    "Prepare tax declarations"
  ],
  "conditions_requirements": [
    "Certified accountant or accounting expert",
    "Commitment to confidentiality and professional care"
  ],
  "estimated_duration": 1,
  "duration_unit": "weeks",
  "estimated_duration_description": "2 to 4 days depending on business size and available documents",
  "price": 8000,
  "price_description": "Starting from 8000 DZD - Price negotiable based on file size",
  "delivery_method": "online",
  "upload_files": [company_docs.pdf, business_license.jpg]
}
```

**Response (Success - 201):**

**Accountant Service Example:**

```json
{
  "id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Mr. Abdelkader Ben Youssef",
    "user_type": "accountant"
  },
  "service_type": "offered",
  "title": "Tax Declaration Preparation (IRG, TVA, IBS)",
  "description": "I offer monthly tax declaration preparation services...",
  "categories": [
    {
      "id": "uuid-here",
      "name": "Tax Declarations"
    },
    {
      "id": "uuid-here",
      "name": "Tax and Legal Compliance"
    }
  ],
  "location": "16",
  "estimated_duration": 2,
  "duration_unit": "days",
  "estimated_duration_description": "2 to 4 days depending on business size and available documents",
  "price": "8000.00",
  "price_description": "Starting from 8000 DZD - Price negotiable based on file size",
  "delivery_method": "online",
  "all_attachments": [
    {
      "id": "485213c3-de3d-4cc1-95f0-9da5b83ea5dc",
      "url": "/media/service_attachments/Database_Schema_Documentation.pdf",
      "filename": "Database Schema Documentation.pdf",
      "size": 53440,
      "uploaded_at": "2025-09-18T09:10:54.461274Z"
    },
    {
      "id": "ed499537-fcf4-4c34-9b81-5b7799f9838a",
      "url": "/media/service_attachments/Not_named_yet.pdf",
      "filename": "Not_named_yet.pdf",
      "size": 106172,
      "uploaded_at": "2025-09-18T09:10:54.461274Z"
    }
  ],
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Client Service Request Example:**

```json
{
  "id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "Company Name",
    "user_type": "client"
  },
  "service_type": "needed",
  "title": "Need Tax Declaration Preparation (IRG, TVA, IBS)",
  "description": "We are a food distribution company based in Oran...",
  "categories": [
    {
      "id": "uuid-here",
      "name": "Tax Declarations"
    }
  ],
  "location": "31",
  "tasks_and_responsibilities": [
    "Collect and analyze financial documents",
    "Prepare tax declarations"
  ],
  "conditions_requirements": [
    "Certified accountant or accounting expert",
    "Commitment to confidentiality and professional care"
  ],
  "estimated_duration": 1,
  "duration_unit": "weeks",
  "estimated_duration_description": "2 to 4 days depending on business size and available documents",
  "price": "8000.00",
  "price_description": "Starting from 8000 DZD - Price negotiable based on file size",
  "delivery_method": "online",
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/service_attachments/company_documents.pdf",
      "filename": "Company Registration Documents.pdf",
      "size": 245760,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z"
}
```

**New Attachment System Features:**

- ✅ **Multiple Files**: Upload multiple files per service using `upload_files` field
- ✅ **File Metadata**: Each attachment includes `id`, `url`, `filename`, `size`, and `uploaded_at`
- ✅ **Direct Downloads**: Files can be downloaded directly via their URLs
- ✅ **Automatic Management**: Files are automatically linked to services and cleaned up on deletion

### 3. Service Management

#### Get My Services 🔒

**Endpoint:** `GET /services/my/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves all services created by the authenticated user.

**Response (Success - 200):**

```json
[
  {
    "id": "uuid-here",
    "user": {
      "pk": "uuid-here",
      "email": "user@example.com",
      "full_name": "John Doe",
      "user_type": "client"
    },
    "service_type": "needed",
    "title": "Tax Filing for Small Business",
    "description": "Need help with annual tax filing...",
    "categories": [
      {
        "id": "uuid-here",
        "name": "Tax Preparation"
      }
    ],
    "price": "500.00",
    "location": "16",
    "delivery_method": "online",
    "is_featured": false,
    "attachments_count": 3,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

**New Fields:**

- `attachments_count`: Total number of files attached to the service

#### Get Service Details 🔒

**Endpoint:** `GET /services/my/{service_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves detailed information about a specific service owned by the user. The response fields are customized based on the service type and user role:

- **"offered" services**: Show service details (price, duration, delivery method)
- **"needed" services**: Show request details (tasks, conditions, requirements)

**Response (Success - 200):**

**Accountant Viewing Service Details:**

```json
{
  "id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "الأستاذ عبد القادر بن يوسف",
    "user_type": "accountant"
  },
  "service_type": "offered",
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "أوفر خدمة إعداد وتقديم التصريحات الجبائية الشهرية للشركات والتجار...",
  "categories": [
    {
      "id": "uuid-here",
      "name": "التصريحات الجبائية"
    }
  ],
  "price": "8000.00",
  "price_description": "ابتداء من 8000 دج - السعر قابل للتفاوض حسب حجم الملف",
  "estimated_duration": 2,
  "duration_unit": "days",
  "estimated_duration_description": "من 2 إلى 4 أيام حسب حجم النشاط والوثائق المتوفرة",
  "location": "16",
  "delivery_method": "online",
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/service_attachments/tax_declaration_sample.pdf",
      "filename": "نموذج تصريح جبائي سابق.pdf",
      "size": 245760,
      "uploaded_at": "2025-01-01T12:00:00Z"
    },
    {
      "id": "uuid-here",
      "url": "/media/service_attachments/certificate.pdf",
      "filename": "شهادة الخبرة المحاسبية.pdf",
      "size": 134567,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Client Viewing Service Details:**

```json
{
  "id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "اسم الشركة",
    "user_type": "client"
  },
  "service_type": "needed",
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "نحن شركة توزيع مواد غذائية مقرها في ولاية وهران نبحث عن محاسب معتمد...",
  "categories": [
    {
      "id": "uuid-here",
      "name": "التصريحات الجبائية"
    }
  ],
  "tasks_and_responsibilities": [
    "جمع وتحليل الوثائق المالية",
    "إعداد التصريحات الضريبية"
  ],
  "conditions_requirements": [
    "محاسب معتمد أو خبير محاسبي",
    "الالتزام بالسرية والحذر المهني"
  ],
  "estimated_duration": 1,
  "duration_unit": "weeks",
  "estimated_duration_description": "من 2 إلى 4 أيام حسب حجم النشاط والوثائق المتوفرة",
  "price": "8000.00",
  "price_description": "ابتداء من 8000 دج - السعر قابل للتفاوض حسب حجم الملف",
  "location": "31",
  "delivery_method": "online",
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/service_attachments/company_documents.pdf",
      "filename": "نسخة من دفتري كمحاسب معتمد.pdf",
      "size": 512000,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Key Differences:**

- **"offered" services** : Show `price`, `price_description`, `estimated_duration` fields (focus on service offering details)
- **"needed" services** : Show `tasks_and_responsibilities`, `conditions_requirements` fields (focus on service requirements)
- Both show common fields: `title`, `description`, `categories`, `location`, `delivery_method`, `all_attachments`

#### Update Service 🔒

**Endpoint:** `PUT/PATCH /services/{service_id}/update/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Updates a service owned by the user. Only active services can be updated.

**Important Note:** The `is_course` field is **read-only** after creation. You cannot change a regular service to a course or vice versa.

**Request Body (PATCH example):**

For regular updates (JSON):

```json
{
  "title": "Updated Tax Declaration Preparation",
  "description": "Updated service description...",
  "price": 9000,
  "price_description": "Updated pricing starting from 9000 DZD"
}
```

For multiple file updates (form-data):

```
Content-Type: multipart/form-data

title: "Updated Tax Declaration Preparation"
description: "Updated service description..."
price: 9000
upload_files: [file1.pdf, file2.pdf]  // Replace all existing files with these new files
```

**Response (Success - 200):** Updated service object

#### Delete Service 🔒

**Endpoint:** `DELETE /services/{service_id}/delete/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Soft deletes a service (sets is_active to false) owned by the user.

**Response (Success - 204):** No content

### 4. Service Discovery

#### Browse Available Services 🔒

**Endpoint:** `GET /services/browse/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Browse services available to the authenticated user based on their role:

- **Clients**: See "offered" services where `is_course: false` (regular services provided by accountants)
- **Accountants**: See "needed" services (services requested by clients)
- **Academics**: See "offered" services where `is_course: true` (courses provided by accountants)

**Query Parameters:**

```
?search=tax filing
&categories=uuid-here
&location=16,31
&min_price=100
&max_price=1000
&duration_unit=days,weeks
&min_duration=1
&max_duration=30
&is_featured=true
&created_after=2025-01-01
&created_before=2025-12-31
&ordering=-created_at
&page=1
```

**Available Filters:**

| Filter           | Type       | Description                                 | Options                            |
| ---------------- | ---------- | ------------------------------------------- | ---------------------------------- |
| `search`         | String     | Search across title, description, user name | Free text                          |
| `categories`     | UUID Array | Filter by service categories                | Category UUIDs                     |
| `location`       | Array      | Filter by Algerian wilaya (state)           | Wilaya codes (01-58)               |
| `min_price`      | Number     | Minimum price filter                        | Decimal value                      |
| `max_price`      | Number     | Maximum price filter                        | Decimal value                      |
| `duration_unit`  | Array      | Time unit for estimated duration            | `hours`, `days`, `weeks`, `months` |
| `min_duration`   | Number     | Minimum estimated duration                  | Integer value                      |
| `max_duration`   | Number     | Maximum estimated duration                  | Integer value                      |
| `is_featured`    | Boolean    | Show only featured services                 | `true`, `false`                    |
| `created_after`  | Date       | Services created after date                 | YYYY-MM-DD                         |
| `created_before` | Date       | Services created before date                | YYYY-MM-DD                         |

**Search Fields:** The search parameter searches across:

- Service title and description
- Service provider's full name
- Location
- Category names

**Ordering Options:**

- `created_at` (default: `-created_at` for newest first)
- `price`
- `estimated_duration`

**Response (Success - 200):**

```json
{
  "count": 25,
  "next": "https://api.example.com/services/browse/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "user": {
        "pk": "uuid-here",
        "email": "accountant@example.com",
        "full_name": "Jane Smith",
        "user_type": "accountant"
      },
      "service_type": "offered",
      "title": "Professional Tax Filing Service",
      "description": "I offer comprehensive tax filing services...",
      "categories": [
        {
          "id": "uuid-here",
          "name": "Tax Preparation"
        }
      ],
      "price": "400.00",
      "location": "16",
      "delivery_method": "online",
      "is_featured": true,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

#### View Service Details 🔒

**Endpoint:** `GET /services/browse/{service_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** View detailed information about any active service. The response fields are customized based on the service type being viewed:

- **"offered" services** (accountant services): Show service details like price, duration, delivery method
- **"needed" services** (client requests): Show request details like tasks, conditions, requirements

**Response (Success - 200):** Role-specific service object (same format as "Get Service Details" above)

---

## 10. Bookings Management

The booking system enables clients, academics, and accountants to create, manage, and interact with service bookings. The system supports three main booking flows based on service types and user roles:

- **Offered Services (Regular)**: Clients book accountants' regular services
- **Offered Services (Courses)**: Academics book accountants' courses
- **Needed Services**: Accountants propose to fulfill clients' needed services

### 1. Booking Creation

#### Create Booking 🔒

**Endpoint:** `POST /bookings/create/`

**Headers:** `Authorization: Bearer <access_token>`

**Content-Type:** `multipart/form-data` (supports file uploads)

**Description:** Creates a new booking with role-specific behavior:

**Role-Based Booking Types:**

- **Clients booking Regular Services**: Only clients can book regular services (`is_course: false`) offered by accountants
- **Academics booking Courses**: Only academics can book courses (`is_course: true`) offered by accountants
- **Accountants proposing to Needed Services**: Only accountants can propose to fulfill services needed by clients
- **Validation**: Users cannot book/propose to their own services

**Request Body for Clients (Regular Service Booking):**

```json
{
  "service": "uuid-of-regular-service",
  "full_name": "John Doe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "cv_file": "file_upload",
  "additional_notes": "I have experience in tax preparation and would like to discuss my requirements in detail..."
}
```

**Request Body for Academics (Course Booking):**

```json
{
  "service": "uuid-of-course",
  "full_name": "Sarah Academic",
  "additional_notes": "I'm excited to learn accounting fundamentals. I have basic math knowledge and available for all sessions.",
  "cv_file": "file_upload"
}
```

**Fields:**

- **service** (required): UUID of the service/course to book
- **full_name** (required): Full name of the person booking
- **linkedin_url** (optional): LinkedIn profile URL
- **cv_file** (optional for courses, optional for services): CV/resume file upload
  - **For course bookings**: CV is optional (academics don't need to provide CV)
  - **For service bookings**: CV is optional but recommended
- **additional_notes** (optional): Any additional information or requirements

**Key Differences:**

| Field              | Client Booking Service | Academic Booking Course |
| ------------------ | ---------------------- | ----------------------- |
| `service`          | Required               | Required                |
| `full_name`        | Required               | Required                |
| `linkedin_url`     | Optional               | Optional                |
| `cv_file`          | Optional               | Optional                |
| `additional_notes` | Optional               | Optional                |

**Response (Success - 201):**

**Example for Client Booking Service:**

```json
{
  "booking_id": "uuid-here",
  "client": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "John Doe",
    "user_type": "client",
    "phone": "+1234567890",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "accountant": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant",
    "phone": "+1234567891",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "service": {
    "id": "uuid-here",
    "user": {
      "pk": "uuid-here",
      "email": "accountant@example.com",
      "full_name": "Jane Smith",
      "user_type": "accountant"
    },
    "service_type": "offered",
    "is_course": false,
    "title": "Professional Tax Filing Service",
    "description": "Comprehensive tax filing services for individuals and small businesses...",
    "categories": [
      {
        "id": "uuid-here",
        "name": "Tax Preparation"
      }
    ],
    "price": "500.00",
    "estimated_duration": 5,
    "duration_unit": "days",
    "delivery_method": "online",
    "location": "16",
    "is_active": true,
    "is_featured": false,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  },
  "full_name": "John Doe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "cv_file": "/media/booking_cvs/john_doe_cv.pdf",
  "additional_notes": "I have experience in tax preparation and would like to discuss my requirements...",
  "status": "pending",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Example for Academic Booking Course:**

```json
{
  "booking_id": "uuid-here",
  "client": {
    "pk": "uuid-here",
    "email": "academic@example.com",
    "full_name": "Sarah Academic",
    "user_type": "academic",
    "phone": "+1234567892",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "accountant": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant",
    "phone": "+1234567891",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "service": {
    "id": "uuid-here",
    "user": {
      "pk": "uuid-here",
      "email": "accountant@example.com",
      "full_name": "Jane Smith",
      "user_type": "accountant"
    },
    "service_type": "offered",
    "is_course": true,
    "title": "Accounting Fundamentals Course",
    "description": "Learn the basics of accounting in 8 weeks...",
    "categories": [
      {
        "id": "uuid-here",
        "name": "Education"
      }
    ],
    "price": "15000.00",
    "estimated_duration": 8,
    "duration_unit": "weeks",
    "delivery_method": "online",
    "location": "online",
    "is_active": true,
    "is_featured": false,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  },
  "full_name": "Sarah Academic",
  "linkedin_url": "https://linkedin.com/in/sarahacademic",
  "cv_file": null,
  "additional_notes": "I'm excited to learn accounting fundamentals. I have basic math knowledge...",
  "status": "pending",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Response (Error - 400):**

```json
{
  "service": ["This field is required."],
  "full_name": ["This field is required."],
  "non_field_errors": ["Only a client can book an offered service."]
}
```

```json
{
  "non_field_errors": ["Only academics can book courses."]
}
```

**Response (Error - 403):**

```json
{
  "detail": "You cannot propose to your own needed service."
}
```

### 2. Booking Management

#### Get My Bookings 🔒

**Endpoint:** `GET /bookings/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves all bookings for the authenticated user. Results are filtered based on user type:

- **Clients**: See bookings where they are the client (regular service bookings)
- **Academics**: See bookings where they are the client and service is a course (course bookings only)
- **Accountants**: See bookings where they are the accountant (both service and course bookings)

**Response (Success - 200):**

```json
[
  {
    "booking_id": "uuid-here",
    "service": {
      "id": "uuid-here",
      "user": {
        "pk": "uuid-here",
        "email": "accountant@example.com",
        "full_name": "Jane Smith",
        "user_type": "accountant"
      },
      "service_type": "offered",
      "title": "Professional Tax Filing Service",
      "description": "Comprehensive tax filing services...",
      "categories": [
        {
          "id": "uuid-here",
          "name": "Tax Preparation"
        }
      ],
      "price": "500.00",
      "estimated_duration": 5,
      "duration_unit": "days",
      "delivery_method": "online",
      "location": "16",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z"
    },
    "status": "pending",
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### Get Booking Details 🔒

**Endpoint:** `GET /bookings/{booking_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves detailed information about a specific booking where the user is a participant (either client or accountant).

**Response (Success - 200):**

```json
{
  "booking_id": "uuid-here",
  "client": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "John Doe",
    "user_type": "client",
    "phone": "+1234567890",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "accountant": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant",
    "phone": "+1234567891",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "service": {
    "id": "uuid-here",
    "user": {
      "pk": "uuid-here",
      "email": "accountant@example.com",
      "full_name": "Jane Smith",
      "user_type": "accountant"
    },
    "service_type": "offered",
    "title": "Professional Tax Filing Service",
    "description": "Comprehensive tax filing services for individuals and small businesses...",
    "categories": [
      {
        "id": "uuid-here",
        "name": "Tax Preparation"
      }
    ],
    "price": "500.00",
    "estimated_duration": 5,
    "duration_unit": "days",
    "delivery_method": "online",
    "location": "16",
    "is_active": true,
    "is_featured": false,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  },
  "full_name": "John Doe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "cv_file": "/media/booking_cvs/john_doe_cv.pdf",
  "additional_notes": "I have experience in tax preparation and would like to discuss my requirements...",
  "status": "pending",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Response (Error - 404):**

```json
{
  "detail": "Not found."
}
```

#### Update Booking 🔒

**Endpoint:** `PUT/PATCH /bookings/{booking_id}/update/`

**Headers:** `Authorization: Bearer <access_token>`

**Content-Type:** `multipart/form-data` (supports file uploads)

**Description:** Updates a booking's information or status. Only participants (client or accountant) can update a booking.

**Status Transitions:**

- **pending** → `confirmed`, `declined` (only by service owner)
- **confirmed** → No further transitions allowed (final state)
- **declined** → No further transitions allowed (final state)

**Request Body:**

```json
{
  "status": "confirmed",
  "full_name": "John Doe Updated",
  "linkedin_url": "https://linkedin.com/in/johndoe-updated",
  "cv_file": "new_cv_file",
  "additional_notes": "Updated requirements and additional information..."
}
```

**Fields:**

- **status** (optional): New status (`confirmed`, `declined`) - only service owner can change
- **full_name** (optional): Updated full name
- **linkedin_url** (optional): Updated LinkedIn profile URL
- **cv_file** (optional): Updated CV/resume file
- **additional_notes** (optional): Updated additional information

**Permission Rules:**

- **Service Owner**: Can confirm or decline bookings (`confirmed`, `declined`)
- **Participants**: Can update booking information (name, LinkedIn, CV, notes)
- **Non-participants**: Cannot access or update

**Response (Success - 200):** Updated booking object (same structure as booking details)

**Response (Error - 400):**

```json
{
  "status": ["Cannot transition from confirmed to declined."],
  "non_field_errors": ["Only the service owner can confirm or decline."]
}
```

**Response (Error - 403):**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 3. Booking Status Management

#### Accept Booking 🔒

**Endpoint:** `POST /bookings/{booking_id}/accept/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Accept a pending booking. Only the service owner can accept bookings.

**Request Body:** Empty (no body required)

**Response (Success - 200):**

```json
{
  "message": "Booking accepted successfully",
  "booking_id": "uuid-here",
  "status": "confirmed",
  "client_id": "uuid-here",
  "accountant_id": "uuid-here"
}
```

**Response (Error - 403):**

```json
{
  "error": "Only the service owner can accept this booking"
}
```

**Response (Error - 400):**

```json
{
  "error": "Cannot accept booking with status: confirmed"
}
```

**Response (Error - 404):**

```json
{
  "error": "Booking not found"
}
```

#### Decline Booking 🔒

**Endpoint:** `POST /bookings/{booking_id}/decline/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Decline a pending booking. Only the service owner can decline bookings.

**Request Body:** Empty (no body required)

**Response (Success - 200):**

```json
{
  "message": "Booking declined successfully",
  "booking_id": "uuid-here",
  "status": "declined"
}
```

**Response (Error - 403):**

```json
{
  "error": "Only the service owner can decline this booking"
}
```

**Response (Error - 400):**

```json
{
  "error": "Cannot decline booking with status: confirmed"
}
```

**Response (Error - 404):**

```json
{
  "error": "Booking not found"
}
```

---

## 11. Chat System

The Chat System provides real-time messaging capabilities with a **global WebSocket connection** architecture. Users maintain a single WebSocket connection for all chat features including messaging, presence tracking, typing indicators, and room list updates.

### 1. Chat System Overview

#### System Features

- **Global WebSocket connection** - One connection per user for all real-time features
- **Real-time messaging** across multiple rooms simultaneously
- **Global presence system** - Online/offline status visible across all shared rooms
- **Role-based communication** with strict permission controls
- **Group chat rooms** for multi-user conversations
- **Direct messaging (DM)** for one-on-one conversations
- **File sharing** support (images, documents, etc.)
- **Typing indicators** for real-time interaction feedback
- **Room list updates** - Automatic reordering and message previews
- **Member management** - Real-time add/remove notifications
- **Unread message tracking** - Badge counts and read status
- **Message history** with pagination via REST API
- **Search functionality** across messages and users

#### Role-Based Communication Rules

**Communication Matrix:**

| User Type      | Can Message Clients | Can Message Accountants | Can Message Academics | Can Create Group Rooms | Can Access Group Rooms |
| -------------- | :-----------------: | :---------------------: | :-------------------: | :--------------------: | :--------------------: |
| **Client**     |         âŒ          |           âœ…           |          âŒ           |           âŒ           |           âŒ           |
| **Accountant** |         âœ…         |           âœ…           |          âœ…          |          âœ…           |          âœ…           |
| **Academic**   |         âŒ          |           âœ…           |          âœ…          |           âŒ           |          âœ…           |

**Key Rules:**

- **Clients**: Can only message accountants via direct messaging (no group room access)
- **Accountants**: Full access to all chat features and can communicate with everyone
- **Academics**: Can message accountants and other academics, access group rooms but cannot create them

### 2. REST API Endpoints

#### Available Users

**Endpoint:** `GET /chat/available_users/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get list of users that the authenticated user can message based on role permissions.

**Query Parameters:**

- `search`: Search by full name or email
- `page`: Page number for pagination (20 users per page)

**Response (Success - 200):**

```json
{
  "count": 15,
  "next": "https://api.example.com/chat/available_users/?page=2",
  "previous": null,
  "results": [
    {
      "pk": "uuid-here",
      "email": "accountant@example.com",
      "full_name": "Jane Smith",
      "user_type": "accountant",
      "is_email_verified": true,
      "account_status": "active"
    },
    {
      "pk": "uuid-here",
      "email": "academic@example.com",
      "full_name": "Dr. Academic Name",
      "user_type": "academic",
      "is_email_verified": true,
      "account_status": "active"
    }
  ]
}
```

#### Group Chat Rooms

**Get Group Chat Rooms:**

**Endpoint:** `GET /chat/chatrooms/group/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get all group chat rooms that the authenticated user is a member of.

**Response (Success - 200):**

```json
[
  {
    "room_id": "uuid-here",
    "creator": {
      "pk": "uuid-here",
      "email": "accountant@example.com",
      "full_name": "Jane Smith",
      "user_type": "accountant"
    },
    "room_name": "General Discussion",
    "created_at": "2025-01-01T12:00:00Z",
    "description": "General discussion room for all accountants",
    "is_private": false,
    "is_dm": false,
    "members_count": 5,
    "message_count": 42,
    "has_unread_messages": true
  }
]
```

**Create Group Chat Room:**

**Endpoint:** `POST /chat/chatrooms/group/create/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Create a new group chat room. Only accountants can create group rooms.

**Request Body:**

```json
{
  "room_name": "Tax Preparation Discussion",
  "description": "Discussion room for tax preparation topics",
  "is_private": true
}
```

**Response (Success - 201):**

```json
{
  "room_id": "uuid-here",
  "creator": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant"
  },
  "room_name": "Tax Preparation Discussion",
  "created_at": "2025-01-01T12:00:00Z",
  "description": "Discussion room for tax preparation topics",
  "is_private": true,
  "is_dm": false,
  "members_count": 1,
  "message_count": 0,
  "has_unread_messages": false
}
```

**Group Chat Room Details:**

**Endpoint:** `GET/PUT/DELETE /chat/chatrooms/{room_id}/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieve, update, or delete a specific group chat room.

**Update Request Body (PUT):**

```json
{
  "room_name": "Updated Room Name",
  "description": "Updated room description",
  "is_private": false
}
```

#### Direct Message Rooms

**Get Direct Message Rooms:**

**Endpoint:** `GET /chat/chatrooms/direct/me/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get all direct message rooms for the authenticated user.

**Response (Success - 200):**

```json
[
  {
    "room_id": "uuid-here",
    "creator": {
      "pk": "uuid-here",
      "email": "client@example.com",
      "full_name": "John Doe",
      "user_type": "client"
    },
    "room_name": "dm_uuid1_uuid2",
    "created_at": "2025-01-01T12:00:00Z",
    "description": "Direct message between John Doe and Jane Smith",
    "is_private": true,
    "is_dm": true,
    "members_count": 2,
    "message_count": 8,
    "has_unread_messages": false
  }
]
```

**Create/Get Direct Message Room:**

**Endpoint:** `POST /chat/chatrooms/direct/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Create or retrieve an existing direct message room between two users.

**Request Body:**

```json
{
  "target_user_id": "uuid-of-target-user"
}
```

**Response (Success - 200):**

```json
{
  "room_id": "uuid-here",
  "creator": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "John Doe",
    "user_type": "client"
  },
  "room_name": "dm_uuid1_uuid2",
  "created_at": "2025-01-01T12:00:00Z",
  "description": "Direct message between John Doe and Jane Smith",
  "is_private": true,
  "is_dm": true,
  "members_count": 2,
  "message_count": 8,
  "has_unread_messages": false
}
```

#### Room Management

**Add Member to Group Room:**

**Endpoint:** `POST /chat/chatrooms/group/{room_id}/add_member/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Add a new member to a group chat room. Only room creators can add members.

**Request Body:**

```json
{
  "user_id": "uuid-of-user-to-add"
}
```

**Response (Success - 200):**

```json
"User added successfully"
```

**Remove Member from Group Room:**

**Endpoint:** `DELETE /chat/chatrooms/group/{room_id}/remove_member/{user_id_to_remove}/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Remove a member from a group chat room. Only room creators can remove members.

**Response (Success - 200):**

```json
{
  "room_id": "uuid-here",
  "room_name": "Updated Room Name",
  "members_count": 4,
  "message_count": 15
}
```

**Note:** Only room creators can add/remove members. Clients cannot be added to group rooms.

#### Messages

**Get Room Messages:**

**Endpoint:** `GET /chat/chatrooms/{room_id}/messages/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get messages from a specific chat room with pagination and search.

**Query Parameters:**

- `search`: Search message content
- `page`: Page number (20 messages per page)

**Response (Success - 200):**

```json
{
  "count": 50,
  "next": "https://api.example.com/chat/chatrooms/uuid/messages/?page=2",
  "previous": null,
  "results": [
    {
      "message_id": "uuid-here",
      "room": {
        "room_id": "uuid-here",
        "room_name": "General Discussion"
      },
      "sender": {
        "pk": "uuid-here",
        "email": "user@example.com",
        "full_name": "John Doe",
        "user_type": "client"
      },
      "content": "Hello everyone!",
      "timestamp": "2025-01-01T12:00:00Z",
      "edited_at": null,
      "is_deleted": false
    }
  ]
}
```

**Update Message:**

**Endpoint:** `PUT /chat/chatrooms/messages/{message_id}/update/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Update a message content. Only the message sender can edit their messages.

**Request Body:**

```json
{
  "content": "Updated message content"
}
```

**Response (Success - 200):**

```json
{
  "message_id": "uuid-here",
  "content": "Updated message content",
  "edited_at": "2025-01-01T12:05:00Z"
}
```

**Delete Message:**

**Endpoint:** `DELETE /chat/chatrooms/messages/{message_id}/delete/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Delete a message. Only the message sender can delete their messages. The message is soft-deleted and content becomes "This message has been deleted".

**Response (Success - 204):** No content

**Note:** Users can only edit/delete their own messages.

#### File Upload

**Endpoint:** `POST /chat/rooms/{room_id}/upload_file/` 🔒

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Description:** Upload a file to a chat room. The file will be broadcast to all room members via WebSocket.

**Request Body (Form Data):**

```
file: [selected_file.jpg]
```

**Response (Success - 201):**

```json
{
  "file_url": "/media/chat_files/uploaded_image.jpg"
}
```

**Supported File Types:**

- **Images**: JPG, PNG, GIF, WebP
- **Documents**: PDF, DOC, DOCX, TXT
- **Archives**: ZIP, RAR
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, AVI, MOV

#### Room Members

**Get Room Members:**

**Endpoint:** `GET /chat/chatrooms/{room_id}/members/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get list of all members in a chat room.

**Query Parameters:**

- `search`: Search by full name
- `page`: Page number (20 members per page)

**Response (Success - 200):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "pk": "uuid-here",
      "email": "user@example.com",
      "full_name": "John Doe",
      "user_type": "accountant",
      "is_email_verified": true,
      "account_status": "active"
    }
  ]
}
```

**Get Members Count:**

**Endpoint:** `GET /chat/rooms/{room_id}/members/count/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get the total count of members in a chat room.

**Response (Success - 200):**

```json
{
  "members_count": 5
}
```

#### Notification Features

**Get Unread Message Count:**

**Endpoint:** `GET /chat/unread-count/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get the total count of unread messages across all chat rooms for the authenticated user.

**Response (Success - 200):**

```json
{
  "unread_count": 12
}
```

**Mark Room as Read:**

**Endpoint:** `POST /chat/rooms/{room_id}/mark-read/` 🔒

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Mark all messages in a room as read by updating the user's last seen timestamp.

**Response (Success - 200):**

```json
{
  "message": "Last seen updated successfully"
}
```

### 3. WebSocket Real-Time Communication

#### Overview

The platform uses a **global WebSocket connection** for all real-time features. Each user maintains a single WebSocket connection that handles:

- Real-time messaging across all rooms
- Global presence tracking (online/offline status)
- Typing indicators
- Room list updates
- Member management notifications

#### Connect to WebSocket

**WebSocket URL:**

```
Production: wss://my-accountant-j02f.onrender.com/ws/global/
```

**Authentication:** Include JWT token in connection URL

```
ws://localhost:8000/ws/global/?token=<your_jwt_token>
```

**Connection Flow:**

1. **Connect**: User establishes WebSocket connection with JWT token
2. **Global Presence**: User automatically goes online globally
3. **Presence Broadcast**: All users in shared rooms receive online status
4. **Ready**: User can now join rooms and send/receive messages

**Connection Close Codes:**

- **4001**: Unauthorized (invalid/missing JWT token)

---

#### Client to Server Messages

Messages you send TO the server:

##### 1. Join Room

Join a chat room to send/receive messages in that room.

**Request:**

```json
{
  "type": "join_room",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365"
}
```

**Success Response:**

```json
{
  "type": "room_joined",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "room_name": "General Chat"
}
```

**Error Responses:**

```json
{"error": "room_id is required"}
{"error": "Room not found"}
{"error": "Not authorized to join this room"}
```

---

##### 2. Leave Room

Leave a chat room.

**Request:**

```json
{
  "type": "leave_room",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365"
}
```

**Success Response:**

```json
{
  "type": "room_left",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365"
}
```

**Error Responses:**

```json
{"error": "room_id is required"}
{"error": "You are not in this room"}
```

---

##### 3. Send Message

Send a message to a room. **You must join the room first.**

**Request:**

```json
{
  "type": "send_message",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "content": "Hello everyone!"
}
```

**Success Response (Delivery Confirmation):**

```json
{
  "type": "message_sent",
  "message_id": "cd4f5823-4cfc-421d-8743-516e7d5853bb",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "status": "delivered"
}
```

**Error Responses:**

```json
{"error": "You must join the room first"}
{"error": "room_id and content are required"}
```

---

##### 4. Typing Indicator

Notify others when you're typing in a room.

**Start Typing:**

```json
{
  "type": "typing",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "is_typing": true
}
```

**Stop Typing:**

```json
{
  "type": "typing",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "is_typing": false
}
```

**Error Responses:**

```json
{"error": "room_id is required"}
{"error": "You must join the room first"}
```

---

#### Server to Client Events

Events you receive FROM the server:

##### 1. Chat Message

Received when a new message is sent to a room you're in.

**Event:**

```json
{
  "type": "chat_message",
  "message": {
    "message_id": "cd4f5823-4cfc-421d-8743-516e7d5853bb",
    "content": "Hello everyone!",
    "sender": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "full_name": "John Doe"
    },
    "sent_at": "2025-01-10T22:30:00.000Z",
    "edited_at": null,
    "is_deleted": false,
    "is_edited": false,
    "message_type": "text",
    "file": null,
    "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365"
  }
}
```

**Message Types:**

- `text` - Regular text message
- `file` - File attachment (check `file` field for URL)

---

##### 2. User Status Changed

Received when a user in your shared rooms goes online/offline.

**Event:**

```json
{
  "type": "user_status_changed",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "John Doe",
  "status": "online"
}
```

**Status Values:**

- `online` - User is connected
- `offline` - User has disconnected

**Note:** This event is sent for all users who share at least one room with you.

---

##### 3. Typing Indicator

Received when another user starts/stops typing in a room you're in.

**Event:**

```json
{
  "type": "typing_indicator",
  "user": "John Doe",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_typing": true,
  "room": "General Chat",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365"
}
```

---

##### 4. Room List Update â­ NEW

Received when a message is sent to ANY room you're a member of. Use this to update your room list.

**Event:**

```json
{
  "type": "room_list_update",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "room_name": "General Chat",
  "is_dm": false,
  "has_unread": true,
  "latest_message": {
    "message_id": "cd4f5823-4cfc-421d-8743-516e7d5853bb",
    "content": "Hello everyone!",
    "sender": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "full_name": "John Doe"
    },
    "sent_at": "2025-01-10T22:30:00.000Z",
    "edited_at": null,
    "is_deleted": false,
    "is_edited": false,
    "message_type": "text",
    "file": null
  }
}
```

**Field Descriptions:**

- `has_unread`: `true` if this is an unread message for you (false if you're the sender)
- `is_dm`: `true` if this is a direct message room
- `latest_message`: Complete message object for preview

**Usage:**

1. Move room to top of your room list
2. Update message preview text
3. Show/hide unread indicator (red badge, bold text)
4. Display message timestamp

---

##### 5. Member Added

Received when a new member is added to a room you're in.

**Event:**

```json
{
  "type": "member_added",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "John Doe",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "added_by": "456e7890-e89b-12d3-a456-426614174001",
  "added_by_name": "Admin User"
}
```

---

##### 6. Member Removed

Received when a member is removed from a room you're in.

**Event:**

```json
{
  "type": "member_removed",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "John Doe",
  "room_id": "6a8df2c9-dc5b-4aee-81c6-a4b126683365",
  "removed_by": "456e7890-e89b-12d3-a456-426614174001",
  "removed_by_name": "Admin User"
}
```

---

#### File Messages

When a file is uploaded via the REST API (`POST /chat/rooms/{room_id}/upload_file/`), it's automatically broadcast to all room members:

```json
{
  "type": "chat_message",
  "message": {
    "message_id": "uuid-here",
    "content": "/media/chat_files/uploaded_image.jpg",
    "sender": {
      "id": "uuid-here",
      "full_name": "John Doe"
    },
    "sent_at": "2025-01-10T22:30:00.000Z",
    "edited_at": null,
    "is_deleted": false,
    "is_edited": false,
    "message_type": "file",
    "file": "/media/chat_files/uploaded_image.jpg",
    "room_id": "room-uuid-here"
  }
}
```

---

#### Implementation Best Practices

**Connection Management:**

- Maintain single WebSocket connection per user
- Implement automatic reconnection on disconnect
- Handle connection state changes gracefully
- Clean up resources on disconnect

**Message Handling:**

- Join room before sending messages
- Handle delivery confirmations
- Display messages immediately on send
- Show loading state until delivery confirmed

**Presence Updates:**

- User goes online on WebSocket connect
- User goes offline on WebSocket disconnect
- No manual presence updates needed
- Presence is global, not per-room

**Room List Management:**

- Move rooms to top on new messages
- Update message previews immediately
- Show unread badges for recipients only
- Sender doesn't see unread badge on own messages
- Sort room list by latest activity

**Error Handling:**

- Handle all error messages from server
- Display user-friendly error messages
- Retry failed operations when appropriate
- Log errors for debugging

### 4. Error Handling

#### REST API Errors

**Permission Denied:**

```json
{
  "detail": "You do not have permission to access this room."
}
```

**Role Restrictions:**

```json
{
  "error": "You cannot message this user"
}
```

**Room Creation Limits:**

```json
{
  "detail": "You cannot add a client to this room."
}
```

**Message Not Found:**

```json
{
  "detail": "Message not found or already deleted."
}
```

#### WebSocket Error Handling

**Connection Errors:**

- **Code 4000**: Room not found - check if room_id exists
- **Code 4001**: Unauthorized - verify JWT token is valid
- **Code 4003**: Forbidden access - check room membership and user permissions

**Runtime Errors:**

```json
{
  "error": "Unauthorized to send messages."
}
```

```json
{
  "error": "Message content is missing"
}
```

```json
{
  "error": "Invalid JSON format received"
}
```

---

## 11. Notifications System

The platform provides a real-time notification system for important events like booking updates. Notifications are delivered via both REST APIs and WebSocket for instant updates.

### Notification Types

| Type               | Description                        | Triggered When                      |
| ------------------ | ---------------------------------- | ----------------------------------- |
| `booking_created`  | New booking request received       | Someone books your service          |
| `booking_accepted` | Booking confirmed by service owner | Service owner accepts your booking  |
| `booking_declined` | Booking declined by service owner  | Service owner declines your booking |
| `message`          | New message received               | Someone sends you a chat message    |

### REST API Endpoints

#### Get Notifications List 🔒

**Endpoint:** `GET /notifications/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves paginated list of all notifications for the authenticated user, ordered by newest first.

**Query Parameters:**

- `page`: Page number (default: 1, page size: 20)

**Response (Success - 200):**

```json
{
  "count": 45,
  "next": "https://api.example.com/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "notification_id": "uuid-here",
      "notification_type": "booking_created",
      "title": "New Booking Request",
      "message": "John Doe booked your Tax Preparation service",
      "is_read": false,
      "related_object_id": "booking-uuid-here",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "notification_id": "uuid-here",
      "notification_type": "booking_accepted",
      "title": "Booking Confirmed",
      "message": "Your booking for Tax Preparation has been confirmed",
      "is_read": true,
      "related_object_id": "booking-uuid-here",
      "created_at": "2025-01-14T14:20:00Z"
    },
    {
      "notification_id": "uuid-here",
      "notification_type": "booking_declined",
      "title": "Booking Declined",
      "message": "Your booking for Tax Preparation has been declined",
      "is_read": false,
      "related_object_id": "booking-uuid-here",
      "created_at": "2025-01-14T09:15:00Z"
    },
    {
      "notification_id": "uuid-here",
      "notification_type": "message",
      "title": "New message from Jane Smith",
      "message": "Jane Smith in Tax Discussion: Can we schedule a call tomorrow?",
      "is_read": false,
      "related_object_id": "room-uuid-here",
      "created_at": "2025-01-13T16:45:00Z"
    }
  ]
}
```

---

#### Get Notification Details 🔒

**Endpoint:** `GET /notifications/{notification_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieve detailed information about a specific notification. Only the notification owner can access it.

**Response Examples:**

**Booking Created Notification:**

```json
{
  "notification_id": "uuid-here",
  "notification_type": "booking_created",
  "title": "New Booking Request",
  "message": "John Doe booked your Tax Preparation service",
  "is_read": false,
  "related_object_id": "booking-uuid-here",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Booking Accepted Notification:**

```json
{
  "notification_id": "uuid-here",
  "notification_type": "booking_accepted",
  "title": "Booking Confirmed",
  "message": "Your booking for Tax Preparation has been confirmed",
  "is_read": true,
  "related_object_id": "booking-uuid-here",
  "created_at": "2025-01-14T14:20:00Z"
}
```

**Booking Declined Notification:**

```json
{
  "notification_id": "uuid-here",
  "notification_type": "booking_declined",
  "title": "Booking Declined",
  "message": "Your booking for Tax Preparation has been declined",
  "is_read": false,
  "related_object_id": "booking-uuid-here",
  "created_at": "2025-01-14T09:15:00Z"
}
```

**Message Notification:**

```json
{
  "notification_id": "uuid-here",
  "notification_type": "message",
  "title": "New message from Jane Smith",
  "message": "Jane Smith in Tax Discussion: Can we schedule a call tomorrow?",
  "is_read": false,
  "related_object_id": "room-uuid-here",
  "created_at": "2025-01-13T16:45:00Z"
}
```

**Response (Error - 404):**

```json
{
  "detail": "Not found."
}
```

---

#### Get Unread Count 🔒

**Endpoint:** `GET /notifications/unread-count/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Get the count of unread notifications for displaying badges.

**Response (Success - 200):**

```json
{
  "unread_count": 5
}
```

---

#### Mark Notification as Read 🔒

**Endpoint:** `POST /notifications/{notification_id}/mark-read/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Mark a specific notification as read. Only the notification owner can mark it as read.

**Response (Success - 200):**

```json
{
  "notification_id": "uuid-here",
  "is_read": true,
  "message": "Notification marked as read successfully"
}
```

**Response (Already Read - 200):**

```json
{
  "notification_id": "uuid-here",
  "is_read": true,
  "message": "Notification was already marked as read"
}
```

---

#### Mark All as Read 🔒

**Endpoint:** `POST /notifications/mark-all-read/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Mark all unread notifications as read for the authenticated user.

**Response (Success - 200):**

```json
{
  "message": "12 notification marked as read",
  "marked_count": 12,
  "unread_count": 0
}
```

---

### Real-time Notifications via WebSocket

Notifications are sent in real-time through the **Global WebSocket** connection (`ws://your-domain/ws/global/`). The same WebSocket connection used for chat also delivers notifications.

#### New Notification Event

Received when a new notification is created for you.

**Event Examples:**

**Booking Created Event:**

```json
{
  "type": "new_notification",
  "notification_id": "d0020a19-09bf-4550-b960-bbe13ad16316",
  "notification_type": "booking_created",
  "title": "New Booking Request",
  "message": "John Doe booked your Tax Preparation service",
  "related_object_id": "89797ee0-94f7-4cc6-9c15-a17a292c1a1b",
  "created_at": "2025-10-12T17:08:57.743228+00:00",
  "is_read": false
}
```

**Booking Accepted Event:**

```json
{
  "type": "new_notification",
  "notification_id": "uuid-here",
  "notification_type": "booking_accepted",
  "title": "Booking Confirmed",
  "message": "Your booking for Tax Preparation has been confirmed",
  "related_object_id": "booking-uuid-here",
  "created_at": "2025-10-12T18:30:00.000000+00:00",
  "is_read": false
}
```

**Booking Declined Event:**

```json
{
  "type": "new_notification",
  "notification_id": "uuid-here",
  "notification_type": "booking_declined",
  "title": "Booking Declined",
  "message": "Your booking for Tax Preparation has been declined",
  "related_object_id": "booking-uuid-here",
  "created_at": "2025-10-12T19:15:00.000000+00:00",
  "is_read": false
}
```

**Message Event:**

```json
{
  "type": "new_notification",
  "notification_id": "uuid-here",
  "notification_type": "message",
  "title": "New message from Jane Smith",
  "message": "Jane Smith in Tax Discussion: Can we schedule a call tomorrow?",
  "related_object_id": "room-uuid-here",
  "created_at": "2025-10-12T20:45:00.000000+00:00",
  "is_read": false
}
```

**Field Descriptions:**

- `notification_id`: Unique identifier for the notification
- `notification_type`: Type of notification (see Notification Types table)
- `title`: Short notification title
- `message`: Detailed notification message
- `related_object_id`: ID of the related object (booking_id, message_id, etc.)
- `created_at`: Timestamp when notification was created
- `is_read`: Always `false` for new notifications

---

### Implementation Flow

**1. On App Start:**

- Fetch existing notifications: `GET /notifications/list/`
- Get unread count: `GET /notifications/unread-count/`
- Connect to WebSocket: `ws://your-domain/ws/global/`

**2. On New Notification (WebSocket):**

- Receive `new_notification` event
- Add notification to local list at the top
- Increment unread count by 1
- Display notification banner/toast to user
- Update notification badge

**3. On User Taps Notification:**

- Call: `POST /notifications/{notification_id}/mark-read/`
- Update local notification: `is_read = true`
- Decrement unread count by 1
- Navigate to related object (booking, message, etc.)

**4. On Mark All as Read:**

- Call: `POST /notifications/mark-all-read/`
- Update all local notifications: `is_read = true`
- Set unread count to 0

**Best Practice:** Update local state after API calls instead of refetching the entire notification list for better performance.

---

## Error Codes and Messages

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Common Error Response Format

```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

### Authentication Errors

```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

---

## User States and Flow

### Registration Flow

1. User registers → Account created (inactive, no email sent automatically)
   - **Profile automatically created** based on `user_type` via Django signals
   - AccountantProfile for accountants, ClientProfile for clients, AcademicProfile for academics
2. User calls `/auth/send-email-otp/` → OTP sent to email
3. User calls `/auth/verify-email-otp/` with OTP → Account activated
4. User can now login and access their profile endpoint

### Social Authentication Flow

#### Google OAuth Flow

1. User taps "Continue with Google" button
2. Mobile app integrates Google Sign-In SDK
3. Google SDK handles authentication and returns access token
4. Send Google access token to `POST /auth/google/`
5. API validates token with Google and creates/logs in user
6. Receive JWT tokens and user data
7. User is automatically logged in (no email verification needed)

#### Facebook OAuth Flow

1. User taps "Continue with Facebook" button
2. Mobile app integrates Facebook SDK
3. Facebook SDK handles authentication and returns access token
4. Send Facebook access token to `POST /auth/facebook/`
5. API validates token with Facebook and creates/logs in user
6. Receive JWT tokens and user data
7. User is automatically logged in (no email verification needed)

### Password Reset Flow

1. User taps "Forgot Password" on login screen
2. User enters email address
3. Call `POST /auth/password-reset/request/` → OTP sent to email
4. User enters OTP and new password
5. Call `POST /auth/password-reset/verify/` → Password updated
6. User can login with new password

### Token Management Flow

1. Store access_token and refresh_token securely after login or register
2. Include access_token in Authorization header for API calls
3. When API returns 401 (token expired):
   - Call `POST /api/token/refresh/` with refresh_token
   - Update stored access_token
   - Retry original API call
4. If refresh fails, redirect user to login

### Profile Management Flow

**Automatic Profile Creation:**

- Profiles are **automatically created** when users register using Django signals
- No explicit profile creation endpoints needed
- Profile type matches the user's `user_type` (accountant → AccountantProfile, client → ClientProfile, academic → AcademicProfile)

**Profile Updates:**

- **All user types**: Use unified endpoint `GET/PUT/PATCH /profiles/me/`
- The endpoint automatically detects user type and returns/updates the appropriate profile

**Profile Features:**

- **Unified Endpoint**: One endpoint for all user types - no need to know user type in advance
- **Service Integration**: Accountant and Client profiles include `all_services` field showing user's active services
- **File Handling**: Profile pictures and attachments return full URLs
- **Automatic Detection**: API automatically determines profile type based on authenticated user

### Service Management Flow

**Category Selection Flow:**

1. **Get Categories**: Call `GET /services/categories/` to get all categories for dropdown
2. **User Selects**: User picks one or more categories from the list (shows `name`, uses `id`)
3. **Create Service**: Use the selected category IDs in the `categories` field (array of UUIDs)

**Role-Based Service Creation:**

1. **Clients**: Create "needed" services (requesting help) → `POST /services/create/` with `is_course: false` or omit field
2. **Accountants**:
   - Create "offered" regular services → `POST /services/create/` with `is_course: false` or omit field
   - Create "offered" courses → `POST /services/create/` with **`is_course: true`** (required)
3. **Academic users**: Cannot create services, can only browse and book courses

**Service Discovery:**

1. **Clients**: Browse "offered" regular services → `GET /services/browse/` (see accountant services)
2. **Academics**: Browse "offered" courses → `GET /services/browse/` (see accountant courses)
3. **Accountants**: Browse "needed" services → `GET /services/browse/` (see client requests)

**Service Management:**

1. **All Users**: View own services → `GET /services/my/`
2. **All Users**: Update own services → `PUT/PATCH /services/{service_id}/update/`
3. **All Users**: Delete own services → `DELETE /services/{service_id}/delete/`
4. **All Users**: Update own services → `PUT/PATCH /services/{service_id}/update/`
5. **All Users**: Delete own services → `DELETE /services/{service_id}/delete/`

### Booking Flow

#### For Offered Regular Services (Client books Accountant's service)

1. **Accountant** creates offered service: `POST /services/create/` with `is_course: false` or omit field
2. **Client** browses offered services: `GET /services/browse/` (sees services where `is_course: false`)
3. **Client** books service: `POST /bookings/create/` with service details (status: "pending")
   - Required fields: `service`, `full_name`
   - Optional fields: `linkedin_url`, `cv_file`, `additional_notes`
4. **Accountant** (service owner) accepts: `POST /bookings/{booking_id}/accept/` (status: "confirmed")
   - OR **Accountant** declines: `POST /bookings/{booking_id}/decline/` (status: "declined")
   - OR **Accountant** updates status: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")

#### For Offered Courses (Academic books Accountant's course)

1. **Accountant** creates course: `POST /services/create/` with **`is_course: true`** (required)
2. **Academic** browses courses: `GET /services/browse/` (sees services where `is_course: true`)
3. **Academic** books course: `POST /bookings/create/` with minimal details (status: "pending")
   - Required fields: `service`, `full_name`
   - Optional fields: `linkedin_url`, `cv_file`, `additional_notes`
   - **Note**: CV and LinkedIn are optional for course bookings
4. **Accountant** (course instructor) accepts: `POST /bookings/{booking_id}/accept/` (status: "confirmed")
   - Academic receives notification that booking is confirmed
   - Accountant manually adds academic to course chat group
   - OR **Accountant** declines: `POST /bookings/{booking_id}/decline/` (status: "declined")

#### For Needed Services (Accountant proposes to Client's request)

1. **Client** creates needed service: `POST /services/create/` (service_type: "needed")
2. **Accountant** browses needed services: `GET /services/browse/`
3. **Accountant** proposes to fulfill: `POST /bookings/create/` with proposal details (status: "pending")
4. **Client** (service owner) accepts: `POST /bookings/{booking_id}/accept/` (status: "confirmed")
   - OR **Client** declines: `POST /bookings/{booking_id}/decline/` (status: "declined")
   - OR **Client** updates status: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")

#### Booking Information Flow

**During Booking Creation (Regular Services):**

- **Full Name** (required): Contact person's name
- **LinkedIn URL** (optional): Professional profile link
- **CV File** (optional): Resume/CV upload (supports file uploads)
- **Additional Notes** (optional): Requirements, questions, or additional information

**During Booking Creation (Courses):**

- **Full Name** (required): Academic's name
- **LinkedIn URL** (optional): Professional profile link
- **CV File** (optional): Not typically required for courses
- **Additional Notes** (optional): Questions about the course, availability, learning goals

**Status Flow:**

- **pending**: Initial status after booking creation
- **confirmed**: Service owner accepted the booking (final state)
- **declined**: Service owner declined the booking (final state)

**Permissions:**

- Only the **service owner** (accountant/course instructor) can accept/decline bookings
- **Clients** and **academics** can view their own booking details
- **Accountants** can view bookings for their services/courses
- All participants can update booking information (name, LinkedIn, CV, notes)

**Chat Room Integration (Courses Only):**

- After accepting a course booking, the accountant **manually** adds the academic to the course chat group
- Academics receive a notification informing them they'll be added to the course chat
- Chat room management is done through the chat system (not automated)

---

### Logout Flow

1. User taps "Logout" button
2. Call `POST /auth/logout/` with access_token (and optionally refresh_token in body)
3. **Server side**: Refresh token gets blacklisted immediately
4. **Client side**: Clear all stored tokens from device secure storage
5. Clear any cached user data
6. Redirect to login/welcome screen

**Important**: Access token continues working until expiration, but refresh token is immediately blacklisted preventing new token generation.

### User Account States

- **inactive**: Newly registered, email not verified
- **active**: Email verified, can use platform
- **suspended**: Account temporarily disabled

### User Types and Permissions

- **client**: Can create "needed" services, book regular offered services (`is_course: false`), create client profile, search for accountants
- **accountant**: Can create "offered" services (regular or courses by setting `is_course`), propose to needed services, create accountant profile, search for clients and academics, manage course bookings
- **academic**: Can browse and book courses (`is_course: true`), create academic profile, cannot create services, can be added to course chat groups
- **admin**: Full platform access and management capabilities

---

## Security Considerations

### Token Security

- Store tokens securely (encrypted storage recommended)
- Implement automatic token refresh
- Clear tokens on logout
- Handle token expiration gracefully
- Users should change passwords regularly using `/auth/password/change/`

### Password Requirements

- Minimum 8 characters
- Cannot be too common
- Cannot be entirely numeric
- Cannot be too similar to user information

### OTP Security

- OTP codes expire in 10 minutes
- Each OTP can only be used once
- New OTP invalidates previous ones

### Service and Booking Security

- Users can only manage their own services and bookings
- Users can only view/update bookings they participate in
- Service types are automatically assigned based on user type:
  - Clients create "needed" services
  - Accountants create "offered" services (regular or courses)
  - Academics cannot create services
- **Course Creation**: Accountants must explicitly set `is_course: true` to create a course
- **Course Access**: Only academics can browse and book courses
- **Service Access**: Only clients can browse and book regular services

- Role-based filtering ensures users only see relevant services

---

## Testing Endpoints

### Development Base URL

```
http://localhost:8000/
```

### Production Base URL

```
https://my-accountant-j02f.onrender.com/
```

### API Documentation

- **Swagger UI**: `http://localhost:8000/swagger/` (dev) | `https://my-accountant-j02f.onrender.com/swagger/` (prod)
- **ReDoc**: `http://localhost:8000/redoc/` (dev) | `https://my-accountant-j02f.onrender.com/redoc/` (prod)
- **Default API Docs**: `http://localhost:8000/` (dev) | `https://my-accountant-j02f.onrender.com/` (prod) - redirects to Swagger UI

---

_Last Updated: January 10, 2025_
_API Version: v1_
_WebSocket Protocol: v1_
