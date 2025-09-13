# My Accountant Platform - Complete API Documentation

## Overview

This documentation covers all APIs for the My Accountant platform, including authentication, user management, services, and bookings. The platform uses JWT (JSON Web Tokens) for authentication and supports email-based registration with OTP verification, social login (Google/Facebook), password reset, user profile management, service marketplace, and booking system.

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
- `academic` - Academic/instructor providing educational content
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

### 8. Accountant Profile Management

#### Create Accountant Profile 🔒

**Endpoint:** `POST /profiles/accountant/create/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Creates a professional profile for accountants. Only users with `user_type: "accountant"` can access this.

**Request Body:**

```json
{
  "bio": "Experienced CPA with 10+ years...",
  "profile_picture_url": "https://example.com/profile.jpg",
  "specializations": ["Tax Planning", "Financial Consulting", "Audit"],
  "certifications": ["CPA", "CMA", "CIA"],
  "years_of_experience": 10,
  "working_hours": {
    "monday": { "start": "09:00", "end": "17:00" },
    "tuesday": { "start": "09:00", "end": "17:00" },
    "wednesday": { "start": "09:00", "end": "17:00" },
    "thursday": { "start": "09:00", "end": "17:00" },
    "friday": { "start": "09:00", "end": "17:00" },
    "saturday": "closed",
    "sunday": "closed"
  },
  "contact_preferences": {
    "email": true,
    "phone": true,
    "video_call": true,
    "in_person": false
  }
}
```

**Response (Success - 201):**

```json
{
  "profile_id": "uuid-here",
  "bio": "Experienced CPA with 10+ years...",
  "profile_picture_url": "https://example.com/profile.jpg",
  "specializations": ["Tax Planning", "Financial Consulting", "Audit"],
  "certifications": ["CPA", "CMA", "CIA"],
  "years_of_experience": 10,
  "working_hours": {...},
  "contact_preferences": {...},
  "is_verified": false,
  "overall_rating": 0.0,
  "total_completed_sessions": 0,
  "total_reviews_count": 0,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### Get/Update Accountant Profile 🔒

**Endpoint:** `GET/PUT/PATCH /profiles/accountant/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves or updates the current user's accountant profile.

**Response (GET - 200):** Same as create response
**Request/Response (PUT/PATCH):** Same as create

---

## 9. Services Management

The Services Management system allows clients to post service requests and accountants to offer their services. The system is role-based where:

- **Clients** create "needed" services (service requests)
- **Accountants** create "offered" services (service offerings)

### 1. Service Categories

#### Get Service Categories 🔒

**Endpoint:** `GET /services/categories/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves a list of all active predefined service categories for dropdown/selection lists. These categories are managed by administrators and users cannot create custom categories.

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
```

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

**Description:** Creates a new service. The service type is automatically determined based on user role:

- **Clients** create `service_type: "needed"` (service requests)
- **Accountants** create `service_type: "offered"` (service offerings)

**Request Body (Form Data):**

**Example for Accountants (Offering Services):**

```json
{
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "أوفر خدمة إعداد وتقديم التصريحات الجبائية الشهرية للشركات والتجار بما في ذلك:\n• تصريح الضريبة على الدخل الإجمالي (IRG)\n• الضريبة على القيمة المضافة (TVA)\n• الضريبة على أرباح الشركات (IBS)\nأقوم بتحليل الوثائق، حساب القيم المستحقة، وملء التصاريح وفقاً للقوانين الجبائية الجزائرية.",
  "categories": ["uuid1", "uuid2"],
  "location": "16",
  "estimated_duration": 2,
  "duration_unit": "days",
  "estimated_duration_description": "من 2 إلى 4 أيام حسب حجم النشاط والوثائق المتوفرة",
  "price": 8000,
  "price_description": "ابتداء من 8000 دج - السعر قابل للتفاوض حسب حجم الملف",
  "delivery_method": "online",
  "attachments": "tax_declaration_sample.pdf"
}
```

**Example for Clients (Requesting Services):**

```json
{
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "نحن شركة توزيع مواد غذائية مقرها في ولاية وهران نبحث عن محاسب معتمد للقيام بإعداد وتقديم التصريحات الجبائية الخاصة بنا (IRG, TVA, IBS) بشكل دوري",
  "categories": ["uuid1"],
  "location": "31",
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
  "price": 8000,
  "price_description": "ابتداء من 8000 دج - السعر قابل للتفاوض حسب حجم الملف",
  "delivery_method": "online",
  "attachments": "company_documents.pdf"
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
    "full_name": "الأستاذ عبد القادر بن يوسف",
    "user_type": "accountant"
  },
  "service_type": "offered",
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "أوفر خدمة إعداد وتقديم التصريحات الجبائية الشهرية للشركات والتجار بما في ذلك:\n• تصريح الضريبة على الدخل الإجمالي (IRG)\n• الضريبة على القيمة المضافة (TVA)\n• الضريبة على أرباح الشركات (IBS)\nأقوم بتحليل الوثائق، حساب القيم المستحقة، وملء التصاريح وفقاً للقوانين الجبائية الجزائرية.",
  "categories": [
    {
      "id": "uuid-here",
      "name": "التصريحات الجبائية"
    },
    {
      "id": "uuid-here",
      "name": "الامتثال الجبائي والقانوني"
    }
  ],
  "location": "16",
  "estimated_duration": 2,
  "duration_unit": "days",
  "estimated_duration_description": "من 2 إلى 4 أيام حسب حجم النشاط والوثائق المتوفرة",
  "price": "8000.00",
  "price_description": "ابتداء من 8000 دج - السعر قابل للتفاوض حسب حجم الملف",
  "delivery_method": "online",
  "attachments": {
    "url": "https://example.com/tax_declaration_sample.pdf",
    "filename": "نموذج تصريح جبائي سابق.pdf"
  },
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
    "full_name": "اسم الشركة",
    "user_type": "client"
  },
  "service_type": "needed",
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "نحن شركة توزيع مواد غذائية مقرها في ولاية وهران نبحث عن محاسب معتمد للقيام بإعداد وتقديم التصريحات الجبائية الخاصة بنا (IRG, TVA, IBS) بشكل دوري",
  "categories": [
    {
      "id": "uuid-here",
      "name": "التصريحات الجبائية"
    }
  ],
  "location": "31",
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
  "delivery_method": "online",
  "attachments": {
    "url": "https://example.com/company_documents.pdf",
    "filename": "نسخة من دفتري كمحاسب معتمد.pdf"
  },
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z"
}
```

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
    "category": {
      "id": "uuid-here",
      "name": "Tax Preparation"
    },
    "price": "500.00",
    "price_negotiable": true,
    "location_preference": "online",
    "urgency_level": "medium",
    "is_featured": false,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### Get Service Details 🔒

**Endpoint:** `GET /services/my/{service_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves detailed information about a specific service owned by the user. The response fields are customized based on the service type:

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
  "attachments": {
    "url": "https://example.com/tax_declaration_sample.pdf",
    "filename": "نموذج تصريح جبائي سابق.pdf"
  },
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
  "attachments": {
    "url": "https://example.com/company_documents.pdf",
    "filename": "نسخة من دفتري كمحاسب معتمد.pdf"
  },
  "is_active": true,
  "is_featured": false,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Key Differences:**

- **"offered" services** (AccountantServiceDetailSerializer): Show `price`, `price_description`, `estimated_duration` fields (focus on service offering details)
- **"needed" services** (ClientServiceDetailSerializer): Show `tasks_and_responsibilities`, `conditions_requirements` fields (focus on service requirements)
- Both show common fields: `title`, `description`, `categories`, `location`, `delivery_method`, `attachments`

#### Update Service 🔒

**Endpoint:** `PUT/PATCH /services/{service_id}/update/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Updates a service owned by the user. Only active services can be updated.

**Request Body (PATCH example):**

**Accountant Update Example:**

```json
{
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "خدمة محدثة: أوفر خدمة إعداد وتقديم التصريحات الجبائية الشهرية مع متابعة إضافية",
  "estimated_duration": 3,
  "estimated_duration_description": "من 2 إلى 5 أيام حسب حجم النشاط والوثائق المتوفرة",
  "price": 9000,
  "price_description": "ابتداء من 9000 دج - السعر محدث ويشمل خدمات إضافية",
  "delivery_method": "online"
}
```

**Client Update Example:**

````json
{
  "title": "إعداد التصريح الجبائي الشهري (IRG, TVA, IBS)",
  "description": "تحديث: نحن شركة توزيع مواد غذائية نبحث عن محاسب معتمد مع خبرة إضافية في النظام الجبائي الجديد",
  "tasks_and_responsibilities": [
    "جمع وتحليل الوثائق المالية",
    "إعداد التصريحات الضريبية",
    "تقديم الاستشارة حول النظام الجبائي الجديد"
  ],
  "conditions_requirements": [
    "محاسب معتمد أو خبير محاسبي",
    "خبرة في النظام الجبائي الجديد",
    "الالتزام بالسرية والحذر المهني"
  ],
  "estimated_duration": 2,
  "duration_unit": "weeks",
  "price": 9500,
  "price_description": "ابتداء من 9500 دج - السعر محدث يشمل الاستشارة الإضافية",
  "delivery_method": "online"
}
```**Response (Success - 200):** Updated service object

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

````

?search=tax filing
&category=uuid-here
&location_preference=online,flexible
&experience_level_required=intermediate,expert
&urgency_level=high,urgent
&min_price=100
&max_price=1000
&price_negotiable=true
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

| Filter                      | Type       | Description                                                            | Options                                                               |
| --------------------------- | ---------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `search`                    | String     | Search across title, description, skills, user name, company, category | Free text                                                             |
| `category`                  | UUID Array | Filter by service categories                                           | Category UUIDs                                                        |
| `location_preference`       | Array      | Meeting location preferences                                           | `online`, `client_office`, `my_office`, `flexible`, `to_be_discussed` |
| `experience_level_required` | Array      | Required experience levels                                             | `beginner`, `intermediate`, `expert`, `any`                           |
| `urgency_level`             | Array      | Service urgency levels                                                 | `low`, `medium`, `high`, `urgent`                                     |
| `min_price`                 | Number     | Minimum price filter                                                   | Decimal value                                                         |
| `max_price`                 | Number     | Maximum price filter                                                   | Decimal value                                                         |
| `price_negotiable`          | Boolean    | Show only negotiable prices                                            | `true`, `false`                                                       |
| `duration_unit`             | Array      | Time unit for estimated duration                                       | `hours`, `days`, `weeks`, `months`                                    |
| `min_duration`              | Number     | Minimum estimated duration                                             | Integer value                                                         |
| `max_duration`              | Number     | Maximum estimated duration                                             | Integer value                                                         |
| `is_featured`               | Boolean    | Show only featured services                                            | `true`, `false`                                                       |
| `created_after`             | Date       | Services created after date                                            | YYYY-MM-DD                                                            |
| `created_before`            | Date       | Services created before date                                           | YYYY-MM-DD                                                            |

**Search Fields:** The search parameter searches across:

- Service title and description
- Skills keywords and requirements notes
- Service provider's full name and company name
- Service category name

**Ordering Options:**

- `created_at` (default: `-created_at` for newest first)
- `price`
- `urgency_level`
- `estimated_duration`

**Role-Based Examples:**

**For Clients (sees offered services):**

```

GET /services/browse/?search=tax&urgency_level=high&max_price=500

```

**For Accountants (sees needed services):**

```

GET /services/browse/?search=bookkeeping&location_preference=online&min_price=200

````

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
      "category": {
        "id": "uuid-here",
        "name": "Tax Preparation"
      },
      "price": "400.00",
      "price_negotiable": false,
      "location_preference": "online",
      "urgency_level": "medium",
      "is_featured": true,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
````

#### View Service Details 🔒

**Endpoint:** `GET /services/browse/{service_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** View detailed information about any active service. The response fields are customized based on the service type being viewed:

- **"offered" services** (accountant services): Show service details like price, duration, delivery method
- **"needed" services** (client requests): Show request details like tasks, conditions, requirements

This means:

- Anyone viewing an accountant's offered service sees the service details format
- Anyone viewing a client's needed service sees the request details format

**Response (Success - 200):** Role-specific service object (same format as "Get Service Details" above)

---

## Bookings Management

### 1. Booking Creation

#### Create Booking 🔒

**Endpoint:** `POST /bookings/create/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Creates a new booking with role-specific behavior:

**Role-Based Booking Types:**

- **Clients booking Offered Services**: Direct booking (status: "pending") - requires schedule and price
- **Accountants proposing to Needed Services**: Service proposal (status: "proposed") - optional schedule

**Request Body (Booking Offered Service):**

```json
{
  "service": "uuid-of-offered-service",
  "scheduled_start": "2025-02-01T10:00:00Z",
  "scheduled_end": "2025-02-01T12:00:00Z",
  "meeting_type": "online",
  "agreed_price": 400.0
}
```

**Request Body (Proposing to Needed Service):**

```json
{
  "service": "uuid-of-needed-service",
  "proposal_message": "I can help you with your tax filing. I have 10+ years experience...",
  "scheduled_start": "2025-02-01T10:00:00Z",
  "scheduled_end": "2025-02-01T12:00:00Z",
  "meeting_type": "online",
  "agreed_price": 500.0
}
```

**Field Options:**

- **meeting_type**: `online`, `in_person`, `phone`

**Response (Success - 201):**

```json
{
  "booking_id": "uuid-here",
  "client": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "John Doe",
    "user_type": "client"
  },
  "accountant": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant"
  },
  "service": {
    "id": "uuid-here",
    "title": "Professional Tax Filing Service",
    "service_type": "offered"
  },
  "proposal_message": null,
  "scheduled_start": "2025-02-01T10:00:00Z",
  "scheduled_end": "2025-02-01T12:00:00Z",
  "meeting_type": "online",
  "status": "pending",
  "agreed_price": "400.00",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### 2. Booking Management

#### Get My Bookings 🔒

**Endpoint:** `GET /bookings/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves all bookings for the authenticated user (as client or accountant).

**Response (Success - 200):**

```json
[
  {
    "booking_id": "uuid-here",
    "service": {
      "id": "uuid-here",
      "title": "Professional Tax Filing Service",
      "service_type": "offered"
    },
    "scheduled_start": "2025-02-01T10:00:00Z",
    "scheduled_end": "2025-02-01T12:00:00Z",
    "status": "confirmed",
    "meeting_type": "online",
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### Get Booking Details 🔒

**Endpoint:** `GET /bookings/{booking_id}/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Retrieves detailed information about a specific booking where the user is a participant.

**Response (Success - 200):**

```json
{
  "booking_id": "uuid-here",
  "client": {
    "pk": "uuid-here",
    "email": "client@example.com",
    "full_name": "John Doe",
    "user_type": "client"
  },
  "accountant": {
    "pk": "uuid-here",
    "email": "accountant@example.com",
    "full_name": "Jane Smith",
    "user_type": "accountant"
  },
  "service": {
    "id": "uuid-here",
    "title": "Professional Tax Filing Service",
    "description": "Comprehensive tax filing services...",
    "service_type": "offered",
    "category": {
      "id": "uuid-here",
      "name": "Tax Preparation"
    }
  },
  "proposal_message": "I can help you with your tax filing...",
  "scheduled_start": "2025-02-01T10:00:00Z",
  "scheduled_end": "2025-02-01T12:00:00Z",
  "meeting_type": "online",
  "status": "confirmed",
  "agreed_price": "400.00",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:30:00Z"
}
```

#### Update Booking 🔒

**Endpoint:** `PUT/PATCH /bookings/{booking_id}/update/`

**Headers:** `Authorization: Bearer <access_token>`

**Description:** Updates a booking. Available actions depend on current status and user role.

**Status Transitions:**

- **proposed** → `confirmed`, `declined`, `cancelled` (by service owner)
- **pending** → `confirmed`, `cancelled` (by service owner)
- **confirmed** → `in_progress`, `cancelled` (provider can mark in_progress)
- **in_progress** → `completed`, `cancelled` (client can mark completed)

**Request Body (Confirm Proposal):**

```json
{
  "status": "confirmed",
  "agreed_price": 450.0
}
```

**Request Body (Update Schedule - only before confirmation):**

```json
{
  "scheduled_start": "2025-02-02T10:00:00Z",
  "scheduled_end": "2025-02-02T12:00:00Z",
  "meeting_type": "phone"
}
```

**Response (Success - 200):** Updated booking object

**Response (Error - 400):**

```json
{
  "status": ["Cannot transition from confirmed to declined."],
  "scheduled_start": ["Schedule cannot be changed after confirmation."]
}
```

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
2. User calls `/auth/send-email-otp/` → OTP sent to email
3. User calls `/auth/verify-email-otp/` with OTP → Account activated
4. User can now login

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

### Accountant Profile Flow

1. User with `user_type: "accountant"` logs in successfully
2. Check if profile exists: `GET /profiles/accountant/`
3. If no profile exists:
   - Show profile creation form
   - Call `POST /profiles/accountant/create/`
4. If profile exists:
   - Allow updates via `PUT/PATCH /profiles/accountant/`

### Service Management Flow

**Category Selection Flow:**

1. **Get Categories**: Call `GET /services/categories/` to get all categories for dropdown
2. **User Selects**: User picks a category from the list (shows `name`, uses `id`)
3. **Create Service**: Use the selected category's `id` in the `category` field

**Creating New Categories:**

If the user needs a category that doesn't exist:

1. **Skip Category Selection**: Don't provide the `category` field
2. **Provide New Category**: Include `new_category_name` (required) and optionally `new_category_description`
3. **Create Service**: The API will automatically create the new category and link it to the service

**Example for New Category Creation:**

```json
{
  "title": "Custom Accounting Service",
  "description": "Special accounting service...",
  "new_category_name": "Custom Financial Analysis",
  "new_category_description": "Specialized financial analysis services",
  "price": 600.0
  // ... other service fields
}
```

**Role-Based Service Creation:**

1. **Clients**: Create "needed" services (requesting help) → `POST /services/create/`
2. **Accountants**: Create "offered" services (providing help) → `POST /services/create/`

**Service Discovery:**

1. **Clients**: Browse "offered" services → `GET /services/browse/` (see accountant services)
2. **Accountants**: Browse "needed" services → `GET /services/browse/` (see client requests)

**Service Management:**

1. **All Users**: View own services → `GET /services/my/`
2. **All Users**: Update own services → `PUT/PATCH /services/{service_id}/update/`
3. **All Users**: Delete own services → `DELETE /services/{service_id}/delete/`

### Booking Flow

#### For Offered Services (Accountant → Client)

1. **Accountant** creates service: `POST /services/create/` (service_type: "offered")
2. **Client** browses services: `GET /services/browse/`
3. **Client** books service: `POST /bookings/create/` (status: "pending")
4. **Accountant** confirms/declines: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")
5. **Accountant** starts session: `PATCH /bookings/{booking_id}/update/` (status: "in_progress")
6. **Client** marks complete: `PATCH /bookings/{booking_id}/update/` (status: "completed")

#### For Needed Services (Client → Accountant)

1. **Client** creates service: `POST /services/create/` (service_type: "needed")
2. **Accountant** browses services: `GET /services/browse/`
3. **Accountant** makes proposal: `POST /bookings/create/` (status: "proposed")
4. **Client** confirms/declines: `PATCH /bookings/{booking_id}/update/` (status: "confirmed"/"declined")
5. **Accountant** starts session: `PATCH /bookings/{booking_id}/update/` (status: "in_progress")
6. **Client** marks complete: `PATCH /bookings/{booking_id}/update/` (status: "completed")

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

- **client**: Can book services, create "needed" services, search for offered services
- **accountant**: Can create "offered" services, search for needed services, respond to "needed" services
- **academic**: Limited access (future features planned)
- **admin**: Full platform access and management capabilities
- **admin**: Administrative access to all platform features

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

---

_Last Updated: August 25, 2025_
_API Version: v1_
