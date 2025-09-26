# My Accountant Platform - Complete API Documentation

## Overview

This documentation covers all APIs for the My Accountant platform, including authentication, user management, profile management, services marketplace, and booking system. The platform uses JWT (JSON Web Tokens) for authentication and supports email-based registration with OTP verification, social login (Google/Facebook), password reset, and comprehensive role-based service management.

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

The platform supports role-based profile management for different user types. Each user type has its own profile structure and endpoints. Profiles are **automatically created** when a user registers using Django signals, so there's no need for explicit profile creation endpoints.

#### Update/Retrieve Accountant Profile 🔒

**Endpoint:** `GET/PUT/PATCH /profiles/accountant/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieve or update the authenticated user's accountant profile. Only users with `user_type: "accountant"` can access this endpoint. The profile is automatically created when the user registers.

**Request Body (PUT/PATCH):**

For regular profile updates (JSON):

```json
{
  "profile_picture": "image_file",
  "phone": "+1234567890",
  "location": "Algiers, Algeria",
  "bio": "Experienced CPA with 10+ years in tax preparation and financial consulting...",
  "working_hours": {
    "monday": { "start": "09:00", "end": "17:00" },
    "tuesday": { "start": "09:00", "end": "17:00" },
    "wednesday": { "start": "09:00", "end": "17:00" },
    "thursday": { "start": "09:00", "end": "17:00" },
    "friday": { "start": "09:00", "end": "17:00" },
    "saturday": "closed",
    "sunday": "closed"
  },
  "is_available": true
}
```

For multiple file uploads (form-data):

```
Content-Type: multipart/form-data

phone: "+1234567890"
location: "Algiers, Algeria"
bio: "Experienced CPA with 10+ years in tax preparation..."
working_hours: {"monday": {"start": "09:00", "end": "17:00"}, ...}
is_available: true
upload_files: [file1.pdf, file2.pdf, file3.pdf]  // Multiple files
profile_picture: profile_image.jpg
```

**Response (Success - 200):**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant",
    "phone": "+1234567890",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/profile.jpg",
  "phone": "+1234567890",
  "location": "Algiers, Algeria",
  "bio": "Experienced CPA with 10+ years...",
  "working_hours": {
    "monday": { "start": "09:00", "end": "17:00" },
    "tuesday": { "start": "09:00", "end": "17:00" },
    "wednesday": { "start": "09:00", "end": "17:00" },
    "thursday": { "start": "09:00", "end": "17:00" },
    "friday": { "start": "09:00", "end": "17:00" },
    "saturday": "closed",
    "sunday": "closed"
  },
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/profile_attachments/certification.pdf",
      "filename": "شهادة الخبرة المحاسبية.pdf",
      "size": 245760,
      "uploaded_at": "2025-01-01T12:00:00Z"
    },
    {
      "id": "uuid-here",
      "url": "/media/profile_attachments/license.pdf",
      "filename": "ترخيص مزاولة المهنة.pdf",
      "size": 134567,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 2,
  "all_services": [
    {
      "id": "uuid-here",
      "service_type": "offered",
      "title": "Tax Declaration Preparation",
      "description": "Professional tax filing services...",
      "categories": [...],
      "price": "8000.00",
      "location": "16",
      "delivery_method": "online",
      "is_featured": false,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "is_available": true,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### Retrieve/Update Client Profile 🔒

**Endpoint:** `GET/PUT/PATCH /profiles/client/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieve or update the authenticated user's client profile. Only users with `user_type: "client"` can access this endpoint. The profile is automatically created when the user registers.

**Request Body (PUT/PATCH):**

For regular profile updates (JSON):

```json
{
  "profile_picture": "image_file",
  "phone": "+1234567890",
  "location": "Oran, Algeria",
  "activity_type": "Food Distribution Company"
}
```

For multiple file uploads (form-data):

```
Content-Type: multipart/form-data

phone: "+1234567890"
location: "Oran, Algeria"
activity_type: "Food Distribution Company"
upload_files: [file1.pdf, file2.pdf]  // Multiple files
profile_picture: profile_image.jpg
```

**Response (Success - 200):**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "Company Name",
    "user_type": "client",
    "phone": "+1234567890",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/profile.jpg",
  "phone": "+1234567890",
  "location": "Oran, Algeria",
  "activity_type": "Food Distribution Company",
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/profile_attachments/company_registration.pdf",
      "filename": "شهادة التسجيل التجاري.pdf",
      "size": 512000,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 1,
  "all_services": [
    {
      "id": "uuid-here",
      "service_type": "needed",
      "title": "Need Tax Declaration Help",
      "description": "Looking for professional accountant...",
      "categories": [...],
      "price": "5000.00",
      "location": "31",
      "delivery_method": "online",
      "is_featured": false,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### Retrieve/Update Academic Profile 🔒

**Endpoint:** `GET/PUT/PATCH /profiles/academic/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieve or update the authenticated user's academic profile. Only users with `user_type: "academic"` can access this endpoint. The profile is automatically created when the user registers.

**Request Body (PUT/PATCH):**

For regular profile updates (JSON):

```json
{
  "profile_picture": "image_file",
  "phone": "+1234567890",
  "bio": "Professor of Accounting at University..."
}
```

For multiple file uploads (form-data):

```
Content-Type: multipart/form-data

phone: "+1234567890"
bio: "Professor of Accounting at University..."
upload_files: [file1.pdf, file2.pdf]  // Multiple files
profile_picture: profile_image.jpg
```

**Response (Success - 200):**

```json
{
  "profile_id": "uuid-here",
  "user": {
    "pk": "uuid-here",
    "email": "academic@example.com",
    "full_name": "Dr. Academic Name",
    "user_type": "academic",
    "phone": "+1234567890",
    "is_email_verified": true,
    "account_status": "active",
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  },
  "profile_picture": "https://example.com/profile.jpg",
  "phone": "+1234567890",
  "bio": "Professor of Accounting at University...",
  "all_attachments": [
    {
      "id": "uuid-here",
      "url": "/media/profile_attachments/phd_certificate.pdf",
      "filename": "شهادة الدكتوراه في المحاسبة.pdf",
      "size": 345678,
      "uploaded_at": "2025-01-01T12:00:00Z"
    },
    {
      "id": "uuid-here",
      "url": "/media/profile_attachments/research_papers.pdf",
      "filename": "الأوراق البحثية المنشورة.pdf",
      "size": 1024000,
      "uploaded_at": "2025-01-01T12:00:00Z"
    }
  ],
  "attachments_count": 2,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Key Features:**

- **Automatic Profile Creation**: Profiles are created automatically via Django signals when users register
- **Role-Based Access**: Each user type can only access their corresponding profile endpoint
- **Service Integration**: Accountant and Client profiles include an `all_services` field showing all active services created by the user
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

**Example for Accountants (Offering Services):**

```json
{
  "title": "Tax Declaration Preparation (IRG, TVA, IBS)",
  "description": "I offer monthly tax declaration preparation services for companies and traders including:\n• Individual Income Tax (IRG)\n• Value Added Tax (TVA)\n• Corporate Income Tax (IBS)\nI analyze documents, calculate due amounts, and fill declarations according to Algerian tax laws.",
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

- **Clients**: See "offered" services (services provided by accountants)
- **Accountants**: See "needed" services (services requested by clients)

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

The booking system enables clients and accountants to create, manage, and interact with service bookings. The system supports two main booking flows based on service types:

- **Offered Services**: Clients book accountants' offered services
- **Needed Services**: Accountants propose to fulfill clients' needed services

### 1. Booking Creation

#### Create Booking 🔒

**Endpoint:** `POST /bookings/create/`

**Headers:** `Authorization: Bearer <access_token>`

**Content-Type:** `multipart/form-data` (supports file uploads)

**Description:** Creates a new booking with role-specific behavior:

**Role-Based Booking Types:**

- **Clients booking Offered Services**: Only clients can book services offered by accountants
- **Accountants proposing to Needed Services**: Only accountants can propose to fulfill services needed by clients
- **Validation**: Users cannot book/propose to their own services

**Request Body:**

```json
{
  "service": "uuid-of-service",
  "full_name": "John Doe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "cv_file": "file_upload",
  "additional_notes": "I have experience in tax preparation and would like to discuss my requirements in detail..."
}
```

**Fields:**

- **service** (required): UUID of the service to book/propose
- **full_name** (required): Full name of the person booking
- **linkedin_url** (optional): LinkedIn profile URL
- **cv_file** (optional): CV/resume file upload
- **additional_notes** (optional): Any additional information or requirements

**Response (Success - 201):**

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

**Response (Error - 400):**

```json
{
  "service": ["This field is required."],
  "full_name": ["This field is required."],
  "non_field_errors": ["Only a client can book an offered service."]
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

**Description:** Retrieves all bookings for the authenticated user (as client or accountant). Results are filtered based on user type:

- **Clients**: See bookings where they are the client
- **Accountants**: See bookings where they are the accountant

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

The Chat System provides real-time messaging capabilities between users with role-based access control. The system supports both group chat rooms and direct messaging (DM) with WebSocket connections for real-time communication.

### 1. Chat System Overview

#### System Features

- **Real-time messaging** via WebSocket connections
- **Role-based communication** with strict permission controls
- **Group chat rooms** for multi-user conversations
- **Direct messaging (DM)** for one-on-one conversations
- **File sharing** support (images, documents, etc.)
- **Message editing and deletion** capabilities
- **Typing indicators** for real-time interaction feedback
- **Online presence tracking** using Redis
- **Unread message counts** and notification system
- **Message history** with pagination
- **Search functionality** across messages and users

#### Role-Based Communication Rules

**Communication Matrix:**

| User Type      | Can Message Clients | Can Message Accountants | Can Message Academics | Can Create Group Rooms | Can Access Group Rooms |
| -------------- | :-----------------: | :---------------------: | :-------------------: | :--------------------: | :--------------------: |
| **Client**     |         ❌          |           ✅            |          ❌           |           ❌           |           ❌           |
| **Accountant** |         ✅          |           ✅            |          ✅           |           ✅           |           ✅           |
| **Academic**   |         ❌          |           ✅            |          ✅           |           ❌           |           ✅           |

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

### 3. WebSocket Connection

#### Connect to Chat Room

**WebSocket URL:** `wss://my-accountant-j02f.onrender.com/ws/chat/{room_id}/`

**Authentication:** JWT token required via Authorization header only

**Connection Headers:**

```
Authorization: Bearer <access_token>
```

**Note:** Query parameter authentication is NOT supported. The JWT token must be provided in the Authorization header with "Bearer " prefix.

**Connection Process:**

1. **Authentication Check**: User must be authenticated via JWT
2. **Room Membership Verification**: User must be a member of the specified room
3. **Role-Based Access**: User's role must allow chat room access
4. **Real-time Presence**: User is added to Redis presence tracking
5. **Message History**: Last 50 messages are sent upon connection
6. **User List**: Current online users in the room are broadcast

**Connection Close Codes:**

- **4000**: Room not found
- **4001**: Unauthorized (invalid/missing JWT token)
- **4003**: Forbidden access (not a room member or role restrictions)

#### WebSocket Message Types

**Sending Messages:**

You can send the following message types to the WebSocket:

**Text Message:**

```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

**Typing Indicator:**

```json
{
  "type": "typing",
  "is_typing": true
}
```

**Receiving Messages:**

The WebSocket will send you the following message types:

**Chat Message:**

```json
{
  "type": "chat_message",
  "message": {
    "message_id": "uuid-here",
    "content": "Hello everyone!",
    "sender": {
      "id": "uuid-here",
      "full_name": "John Doe"
    },
    "sent_at": "2025-01-01T12:00:00Z",
    "edited_at": null,
    "is_deleted": false,
    "is_edited": false,
    "message_type": "text",
    "file": null
  }
}
```

**Note:** This new format applies to newly sent messages. Historical messages and other events maintain their original format.

**User Join Event:**

```json
{
  "type": "user_join",
  "user_id": "uuid-here",
  "full_name": "Jane Smith"
}
```

**User Leave Event:**

```json
{
  "type": "user_leave",
  "user_id": "uuid-here",
  "user_full_name": "Jane Smith"
}
```

**Typing Indicator:**

```json
{
  "type": "typing_indicator",
  "user": "Jane Smith",
  "user_id": "uuid-here",
  "room": "General Discussion",
  "is_typing": true
}
```

**Message Edited:**

```json
{
  "type": "message_edited",
  "message_id": "uuid-here",
  "new_content": "Updated message content",
  "edited_at": "2025-01-01T12:05:00Z",
  "room_id": "uuid-here",
  "sender_id": "uuid-here",
  "sender_full_name": "John Doe"
}
```

**Message Deleted:**

```json
{
  "type": "message_deleted",
  "message_id": "uuid-here",
  "room_id": "uuid-here",
  "edited_at": "2025-01-01T12:05:00Z"
}
```

**Room Users List:**

```json
{
  "type": "room_users_list",
  "users": [
    {
      "id": "uuid-here",
      "full_name": "John Doe"
    },
    {
      "id": "uuid-here",
      "full_name": "Jane Smith"
    }
  ]
}
```

#### File Messages

When a file is uploaded via the REST API, it's automatically broadcast to all room members via WebSocket as:

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
    "sent_at": "2025-01-01T12:00:00Z",
    "edited_at": null,
    "is_deleted": false,
    "is_edited": false,
    "message_type": "file",
    "file": "/media/chat_files/uploaded_image.jpg"
  }
}
```

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

- **Accountants**: Update via `PUT/PATCH /profiles/accountant/`
- **Clients**: Update via `PUT/PATCH /profiles/client/`
- **Academics**: Update via `PUT/PATCH /profiles/academic/`

**Profile Features:**

- **Service Integration**: Accountant and Client profiles include `all_services` field showing user's active services
- **File Handling**: Profile pictures and attachments return full URLs
- **Role-Based Access**: Users can only access their own profile type endpoint

### Service Management Flow

**Category Selection Flow:**

1. **Get Categories**: Call `GET /services/categories/` to get all categories for dropdown
2. **User Selects**: User picks one or more categories from the list (shows `name`, uses `id`)
3. **Create Service**: Use the selected category IDs in the `categories` field (array of UUIDs)

**Role-Based Service Creation:**

1. **Clients**: Create "needed" services (requesting help) → `POST /services/create/`
2. **Accountants**: Create "offered" services (providing help) → `POST /services/create/`
3. **Academic users**: Limited access to service marketplace

**Service Discovery:**

1. **Clients**: Browse "offered" services → `GET /services/browse/` (see accountant services)
2. **Accountants**: Browse "needed" services → `GET /services/browse/` (see client requests)

**Service Management:**

1. **All Users**: View own services → `GET /services/my/`
2. **All Users**: Update own services → `PUT/PATCH /services/{service_id}/update/`
3. **All Users**: Delete own services → `DELETE /services/{service_id}/delete/`
4. **All Users**: Update own services → `PUT/PATCH /services/{service_id}/update/`
5. **All Users**: Delete own services → `DELETE /services/{service_id}/delete/`

### Booking Flow

#### For Offered Services (Client books Accountant's service)

1. **Accountant** creates offered service: `POST /services/create/` (service_type: "offered")
2. **Client** browses offered services: `GET /services/browse/`
3. **Client** books service: `POST /bookings/create/` with service details (status: "pending")
4. **Accountant** (service owner) accepts: `POST /bookings/{booking_id}/accept/` (status: "confirmed")
   - OR **Accountant** declines: `POST /bookings/{booking_id}/decline/` (status: "declined")
   - OR **Accountant** updates status: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")

#### For Needed Services (Accountant proposes to Client's request)

1. **Client** creates needed service: `POST /services/create/` (service_type: "needed")
2. **Accountant** browses needed services: `GET /services/browse/`
3. **Accountant** proposes to fulfill: `POST /bookings/create/` with proposal details (status: "pending")
4. **Client** (service owner) accepts: `POST /bookings/{booking_id}/accept/` (status: "confirmed")
   - OR **Client** declines: `POST /bookings/{booking_id}/decline/` (status: "declined")
   - OR **Client** updates status: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")

#### Booking Information Flow

**During Booking Creation:**

- **Full Name**: Contact person's name
- **LinkedIn URL**: Optional professional profile link
- **CV File**: Optional resume/CV upload (supports file uploads)
- **Additional Notes**: Optional requirements, questions, or additional information

**Status Flow:**

- **pending**: Initial status after booking creation
- **confirmed**: Service owner accepted the booking (final state)
- **declined**: Service owner declined the booking (final state)

**Permissions:**

- Only the **service owner** can accept/decline bookings
- Both **client** and **accountant** can view booking details if they are participants
- Both participants can update booking information (name, LinkedIn, CV, notes)

**Note**: Academic users cannot participate in the booking system as they don't have access to the service marketplace.

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

- **client**: Can create "needed" services, book offered services, create client profile, search for accountants
- **accountant**: Can create "offered" services, propose to needed services, create accountant profile, search for clients
- **academic**: Can create academic profile, limited access to service marketplace
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
- Time slot conflicts are automatically prevented for confirmed bookings
- Service types are automatically assigned based on user type (clients create "needed", accountants create "offered")
- Academic users are restricted from service marketplace access
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

_Last Updated: September 13, 2025_
_API Version: v1_
