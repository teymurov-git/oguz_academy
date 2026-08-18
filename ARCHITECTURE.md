# Oguz Academy — System Architecture v2.0

> **Stack:** Django 5.2 + Django REST Framework + PostgreSQL  
> **Frontend:** Müstəqil (React/Vue/Next) — admin panel üçün Django Admin istifadə edilmir  
> **Auth:** JWT (SimpleJWT)  
> **Docker:** PostgreSQL + Redis (caching, sessions, queue)

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (SPA)                        │
│           React / Next.js / Vue / Nuxt                   │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
                         │ JWT Bearer Token
┌────────────────────────▼────────────────────────────────┐
│              API GATEWAY (Nginx / Traefik)               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 DJANGO REST API                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ accounts  │ │ branches  │ │ courses   │ │ students │  │
│  │ auth      │ │ offices   │ │ groups    │ │ parents  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ teachers  │ │ lessons   │ │ exams     │ │ grades   │  │
│  │          │ │ schedule  │ │ results   │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ payments  │ │ finance   │ │ reports   │ │ hr       │  │
│  │ install   │ │ expenses  │ │ analytics │ │ salary   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ homework  │ │ notifications│ │ files    │ │ audits   │  │
│  │          │ │ sms/email │ │ media    │ │ logs     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   POSTGRESQL                             │
│         Multi-schema (public + per-branch?)              │
└─────────────────────────────────────────────────────────┘
```

Backend yalnız REST API təmin edir. Frontend tam müstəqildir. Django Admin yalnız super-admin üçün ehtiyat qapı kimi qala bilər, əsas panel frontenddədir.

---

## 2. DJANGO APP STRUCTURE

```
oguz/                       # Project settings (settings, urls, wsgi)
├── apps/
│   ├── accounts/           # Auth, User, Profile, RBAC
│   ├── branches/           # Filiallar, sinif otaqları
│   ├── employees/          # İşçilər (HR), maaşlar
│   ├── roles/              # Rollar, icazələr (Permission)
│   ├── students/           # Tələbələr, valideynlər
│   ├── teachers/           # Müəllimlər
│   ├── courses/            # Kurslar, kateqoriyalar, qruplar
│   ├── schedule/           # Dərs cədvəli, dərslər
│   ├── attendance/         # Davamiyyət
│   ├── exams/              # İmtahanlar, qiymətlər
│   ├── homework/           # Ev tapşırıqları
│   ├── payments/           # Ödənişlər, taksit, endirim, kupon
│   ├── finance/            # Mühasibatlıq, gəlir/xərclər
│   ├── notifications/      # Bildirişlər, Email, SMS
│   ├── files/              # Fayl idarəetməsi
│   ├── reports/            # Hesabatlar, analitika
│   ├── audit/              # Audit log, activity log
│   └── settings/           # Sistem ayarları
├── templates/              # (Yalnız frontend olmadıqda)
└── static/
```

Hər app öz `models.py`, `serializers.py`, `views.py`, `urls.py`, `permissions.py`, `filters.py` fayllarını saxlayır. Ortaq funksionallıq `apps/core/` və ya `apps/common/` altında toplanır.

---

## 3. DATABASE SCHEMA (PostgreSQL)

### 3.1 — Core / Shared

```sql
-- ============================================================
-- ACCOUNTS & AUTH
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY,
    email           VARCHAR(254) UNIQUE NOT NULL,
    phone           VARCHAR(50),
    password        VARCHAR(128) NOT NULL,
    first_name      VARCHAR(150),
    last_name       VARCHAR(150),
    avatar          VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    is_superuser    BOOLEAN DEFAULT FALSE,
    last_login      TIMESTAMP,
    date_joined     TIMESTAMP DEFAULT NOW(),
    language        VARCHAR(10) DEFAULT 'az',
    theme           VARCHAR(10) DEFAULT 'light',  -- 'light' | 'dark'
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ROLES & PERMISSIONS (RBAC)
-- ============================================================
CREATE TABLE roles (
    id              UUID PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,  -- super_admin, owner, branch_manager, etc.
    slug            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    is_system       BOOLEAN DEFAULT FALSE,  -- system roles cannot be deleted
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE permissions (
    id              UUID PRIMARY KEY,
    codename        VARCHAR(150) UNIQUE NOT NULL,  -- e.g. 'students.create', 'students.edit'
    name            VARCHAR(255),
    module          VARCHAR(100),  -- e.g. 'students', 'payments'
    action          VARCHAR(50),   -- e.g. 'create', 'read', 'update', 'delete'
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE role_permissions (
    id              UUID PRIMARY KEY,
    role_id         UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   UUID REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);

CREATE TABLE user_roles (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id         UUID REFERENCES roles(id) ON DELETE CASCADE,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,  -- scope to branch
    UNIQUE(user_id, role_id, branch_id)
);

-- ============================================================
-- BRANCHES (Filiallar)
-- ============================================================
CREATE TABLE branches (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(200) UNIQUE NOT NULL,
    logo            VARCHAR(500),
    address         TEXT,
    phone           VARCHAR(50),
    email           VARCHAR(254),
    manager_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    work_hours      JSONB,  -- {"mon": "09:00-18:00", "tue": ...}
    status          VARCHAR(20) DEFAULT 'active',  -- active | inactive | suspended
    max_students    INTEGER DEFAULT 0,  -- 0 = unlimited
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE branch_rooms (  -- Sinif otaqları
    id              UUID PRIMARY KEY,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    name            VARCHAR(100),  -- "Room 101", "Lab 1"
    capacity        INTEGER DEFAULT 20,
    equipment       JSONB,  -- ["projector", "whiteboard", "computer"]
    is_active       BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- EMPLOYEES (İşçilər) — HR modulu
-- ============================================================
CREATE TABLE employees (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    employee_id     VARCHAR(50) UNIQUE,  -- HR kodu, məsələn "EMP-2025-001"
    department      VARCHAR(100),  -- "academic", "finance", "hr", "marketing"
    position        VARCHAR(200),
    hire_date       DATE,
    salary          DECIMAL(10,2),
    salary_currency VARCHAR(3) DEFAULT 'AZN',
    bank_account    VARCHAR(50),
    tax_number      VARCHAR(50),
    emergency_contact JSONB,
    documents       JSONB,  -- ["contract.pdf", "id_copy.pdf"]
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- STUDENTS & PARENTS
-- ============================================================
CREATE TABLE students (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    student_id      VARCHAR(50) UNIQUE,  -- "STU-2025-0001"
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    parent_id       UUID REFERENCES parents(id) ON DELETE SET NULL,
    date_of_birth   DATE,
    gender          VARCHAR(10),  -- male | female
    address         TEXT,
    emergency_phone VARCHAR(50),
    school          VARCHAR(200),  -- hansı məktəbdə oxuyur
    grade_level     VARCHAR(20),  -- 5, 6, 7, 8, 9, 10, 11
    status          VARCHAR(20) DEFAULT 'active',  -- active | frozen | graduated | transferred | dropped
    enrollment_date DATE,
    notes           TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE parents (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    phone           VARCHAR(50),
    occupation      VARCHAR(200),
    address         TEXT,
    is_primary      BOOLEAN DEFAULT TRUE,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TEACHERS
-- ============================================================
CREATE TABLE teachers (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    employee_id     UUID REFERENCES employees(id) ON DELETE SET NULL,
    teacher_id      VARCHAR(50) UNIQUE,  -- "TCH-2025-0001"
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    specialization  VARCHAR(200),
    bio             TEXT,
    education       JSONB,  -- [{"degree": "Bachelor", "field": "Math", "university": "BDU"}]
    certificates    JSONB,
    subjects        JSONB,  -- ["math", "physics", "python"]
    hourly_rate     DECIMAL(10,2),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- COURSES & CATEGORIES
-- ============================================================
CREATE TABLE course_categories (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(200) UNIQUE NOT NULL,
    description     TEXT,
    icon            VARCHAR(100),  -- emoji or icon name
    sort_order      INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE courses (
    id              UUID PRIMARY KEY,
    category_id     UUID REFERENCES course_categories(id) ON DELETE SET NULL,
    name            VARCHAR(300) NOT NULL,
    slug            VARCHAR(300) UNIQUE NOT NULL,
    description     TEXT,
    thumbnail       VARCHAR(500),
    duration_weeks  INTEGER,
    lesson_count    INTEGER,
    price           DECIMAL(10,2),
    installment_allowed BOOLEAN DEFAULT TRUE,
    max_installments    INTEGER DEFAULT 0,
    curriculum      JSONB,  -- [{"week": 1, "topic": "...", "description": "..."}]
    requirements    JSONB,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- GROUPS
-- ============================================================
CREATE TABLE groups (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    course_id       UUID REFERENCES courses(id) ON DELETE CASCADE,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    teacher_id      UUID REFERENCES teachers(id) ON DELETE SET NULL,
    room_id         UUID REFERENCES branch_rooms(id) ON DELETE SET NULL,
    type            VARCHAR(20) DEFAULT 'group',  -- group | individual | intensive
    schedule_text   VARCHAR(200),  -- "Mon-Wed-Fri 14:00-16:00"
    start_date      DATE,
    end_date        DATE,
    max_students    INTEGER DEFAULT 20,
    current_count   INTEGER DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'active',  -- active | completed | cancelled | pending
    price           DECIMAL(10,2),  -- group-specific price override
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE group_students (
    id              UUID PRIMARY KEY,
    group_id        UUID REFERENCES groups(id) ON DELETE CASCADE,
    student_id      UUID REFERENCES students(id) ON DELETE CASCADE,
    status          VARCHAR(20) DEFAULT 'active',  -- active | frozen | dropped | completed
    joined_at       TIMESTAMP DEFAULT NOW(),
    left_at         TIMESTAMP,
    UNIQUE(group_id, student_id)
);

-- ============================================================
-- SCHEDULE & LESSONS
-- ============================================================
CREATE TABLE schedules (  -- Dərs cədvəli (template)
    id              UUID PRIMARY KEY,
    group_id        UUID REFERENCES groups(id) ON DELETE CASCADE,
    day_of_week     INTEGER,  -- 0=Monday, 6=Sunday
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    room_id         UUID REFERENCES branch_rooms(id) ON DELETE SET NULL,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE lessons (  -- Hər bir dərs instance-ı
    id              UUID PRIMARY KEY,
    group_id        UUID REFERENCES groups(id) ON DELETE CASCADE,
    teacher_id      UUID REFERENCES teachers(id) ON DELETE SET NULL,
    room_id         UUID REFERENCES branch_rooms(id) ON DELETE SET NULL,
    topic           VARCHAR(300),
    date            DATE NOT NULL,
    start_time      TIME,
    end_time        TIME,
    status          VARCHAR(20) DEFAULT 'scheduled',  -- scheduled | completed | cancelled | rescheduled
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ATTENDANCE
-- ============================================================
CREATE TABLE attendance (
    id              UUID PRIMARY KEY,
    lesson_id       UUID REFERENCES lessons(id) ON DELETE CASCADE,
    student_id      UUID REFERENCES students(id) ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL,  -- present | absent | late | excused
    late_minutes    INTEGER DEFAULT 0,
    note            TEXT,
    marked_by_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    marked_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE(lesson_id, student_id)
);

-- ============================================================
-- EXAMS & GRADES
-- ============================================================
CREATE TABLE exams (
    id              UUID PRIMARY KEY,
    group_id        UUID REFERENCES groups(id) ON DELETE CASCADE,
    title           VARCHAR(300) NOT NULL,
    type            VARCHAR(50),  -- midterm | final | quiz | mock | placement
    description     TEXT,
    max_score       DECIMAL(5,2) DEFAULT 100,
    passing_score   DECIMAL(5,2) DEFAULT 50,
    weight          DECIMAL(3,2) DEFAULT 1.00,  -- çəki əmsalı
    date            DATE,
    start_time      TIME,
    duration_minutes INTEGER,
    room_id         UUID REFERENCES branch_rooms(id) ON DELETE SET NULL,
    status          VARCHAR(20) DEFAULT 'scheduled',  -- scheduled | ongoing | completed | graded
    created_by_id   UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE exam_results (
    id              UUID PRIMARY KEY,
    exam_id         UUID REFERENCES exams(id) ON DELETE CASCADE,
    student_id      UUID REFERENCES students(id) ON DELETE CASCADE,
    score           DECIMAL(5,2),
    percentage      DECIMAL(5,2),
    grade           VARCHAR(5),  -- A, B, C, D, F
    feedback        TEXT,
    graded_by_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    graded_at       TIMESTAMP,
    UNIQUE(exam_id, student_id)
);

-- ============================================================
-- HOMEWORK
-- ============================================================
CREATE TABLE homework (
    id              UUID PRIMARY KEY,
    group_id        UUID REFERENCES groups(id) ON DELETE CASCADE,
    teacher_id      UUID REFERENCES teachers(id) ON DELETE CASCADE,
    title           VARCHAR(300) NOT NULL,
    description     TEXT,
    attachments     JSONB,
    deadline        TIMESTAMP,
    max_score       DECIMAL(5,2) DEFAULT 100,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE homework_submissions (
    id              UUID PRIMARY KEY,
    homework_id     UUID REFERENCES homework(id) ON DELETE CASCADE,
    student_id      UUID REFERENCES students(id) ON DELETE CASCADE,
    content         TEXT,
    attachments     JSONB,
    submitted_at    TIMESTAMP DEFAULT NOW(),
    score           DECIMAL(5,2),
    feedback        TEXT,
    graded_by_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    graded_at       TIMESTAMP,
    UNIQUE(homework_id, student_id)
);

-- ============================================================
-- PAYMENTS, INSTALLMENTS, DISCOUNTS, COUPONS
-- ============================================================
CREATE TABLE payment_plans (  -- Taksit planı
    id              UUID PRIMARY KEY,
    name            VARCHAR(200),
    installment_count   INTEGER NOT NULL,
    interval_days   INTEGER DEFAULT 30,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE discounts (  -- Endirimlər
    id              UUID PRIMARY KEY,
    name            VARCHAR(200),
    type            VARCHAR(20),  -- percentage | fixed
    value           DECIMAL(10,2),
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    valid_from      DATE,
    valid_until     DATE
);

CREATE TABLE coupons (  -- Kuponlar
    id              UUID PRIMARY KEY,
    code            VARCHAR(50) UNIQUE NOT NULL,
    discount_type   VARCHAR(20),  -- percentage | fixed
    discount_value  DECIMAL(10,2),
    max_uses        INTEGER DEFAULT 0,  -- 0 = unlimited
    current_uses    INTEGER DEFAULT 0,
    valid_from      DATE,
    valid_until     DATE,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE payments (
    id              UUID PRIMARY KEY,
    student_id      UUID REFERENCES students(id) ON DELETE CASCADE,
    group_id        UUID REFERENCES groups(id) ON DELETE SET NULL,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    invoice_no      VARCHAR(50) UNIQUE,
    amount          DECIMAL(10,2) NOT NULL,
    paid_amount     DECIMAL(10,2),  -- endirim tətbiq edildikdən sonra
    discount_id     UUID REFERENCES discounts(id) ON DELETE SET NULL,
    coupon_id       UUID REFERENCES coupons(id) ON DELETE SET NULL,
    payment_method  VARCHAR(50),  -- cash | card | transfer | pos_terminal | e_payment
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | completed | failed | refunded | cancelled
    payment_date    TIMESTAMP DEFAULT NOW(),
    note            TEXT,
    received_by_id  UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE installments (  -- Taksitlər
    id              UUID PRIMARY KEY,
    payment_id      UUID REFERENCES payments(id) ON DELETE CASCADE,
    installment_no  INTEGER NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    due_date        DATE NOT NULL,
    paid_date       DATE,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | paid | overdue | cancelled
    late_fee        DECIMAL(10,2) DEFAULT 0,
    note            TEXT,
    UNIQUE(payment_id, installment_no)
);

-- ============================================================
-- FINANCE (Mühasibatlıq)
-- ============================================================
CREATE TABLE income_categories (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200),
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE expense_categories (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200),
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE expenses (
    id              UUID PRIMARY KEY,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    category_id     UUID REFERENCES expense_categories(id) ON DELETE SET NULL,
    title           VARCHAR(300) NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    tax_amount      DECIMAL(10,2) DEFAULT 0,
    description     TEXT,
    receipt         VARCHAR(500),
    expense_date    DATE NOT NULL,
    payment_method  VARCHAR(50),
    approved_by_id  UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by_id   UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SALARIES (Maaşlar)
-- ============================================================
CREATE TABLE salary_payments (
    id              UUID PRIMARY KEY,
    employee_id     UUID REFERENCES employees(id) ON DELETE CASCADE,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    amount          DECIMAL(10,2) NOT NULL,
    bonus           DECIMAL(10,2) DEFAULT 0,
    penalty         DECIMAL(10,2) DEFAULT 0,
    total           DECIMAL(10,2) NOT NULL,  -- amount + bonus - penalty
    month           INTEGER NOT NULL,  -- 1-12
    year            INTEGER NOT NULL,
    payment_date    DATE,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | paid | cancelled
    note            TEXT,
    paid_by_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE teacher_salary_payments (
    id              UUID PRIMARY KEY,
    teacher_id      UUID REFERENCES teachers(id) ON DELETE CASCADE,
    branch_id       UUID REFERENCES branches(id) ON DELETE CASCADE,
    amount          DECIMAL(10,2) NOT NULL,  -- hourly_rate * hours
    lesson_count    INTEGER DEFAULT 0,
    hourly_rate     DECIMAL(10,2),
    bonus           DECIMAL(10,2) DEFAULT 0,
    total           DECIMAL(10,2) NOT NULL,
    month           INTEGER NOT NULL,
    year            INTEGER NOT NULL,
    payment_date    DATE,
    status          VARCHAR(20) DEFAULT 'pending',
    note            TEXT,
    paid_by_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(50),  -- payment_reminder | exam_reminder | new_lesson | etc.
    title           VARCHAR(300) NOT NULL,
    message         TEXT,
    data            JSONB,  -- additional payload
    is_read         BOOLEAN DEFAULT FALSE,
    read_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sms_logs (
    id              UUID PRIMARY KEY,
    recipient       VARCHAR(50),
    message         TEXT,
    status          VARCHAR(20),  -- sent | failed | pending
    provider        VARCHAR(50),  -- Twilio, etc.
    sent_at         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE email_logs (
    id              UUID PRIMARY KEY,
    recipient       VARCHAR(254),
    subject         VARCHAR(500),
    body            TEXT,
    status          VARCHAR(20),  -- sent | failed | pending
    sent_at         TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FILE MANAGEMENT
-- ============================================================
CREATE TABLE file_uploads (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    original_name   VARCHAR(500),
    file_path       VARCHAR(500),
    file_size       BIGINT,
    mime_type       VARCHAR(100),
    module          VARCHAR(100),  -- homework | exam | student_doc | etc.
    related_id      UUID,  -- polymorphic reference
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- AUDIT & ACTIVITY LOGS
-- ============================================================
CREATE TABLE activity_logs (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(50),  -- created | updated | deleted | viewed | logged_in
    module          VARCHAR(100),  -- students | payments | groups | etc.
    object_id       UUID,
    object_repr     VARCHAR(500),  -- string representation
    details         JSONB,  -- changes, metadata
    ip_address      VARCHAR(50),
    user_agent      TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SYSTEM SETTINGS
-- ============================================================
CREATE TABLE system_settings (
    id              UUID PRIMARY KEY,
    key             VARCHAR(200) UNIQUE NOT NULL,
    value           JSONB NOT NULL,
    description     TEXT,
    is_public       BOOLEAN DEFAULT FALSE,  -- accessible via public API
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 4. RBAC — ROLE & PERMISSION MATRIX

| # | Role | Səviyyə | İcazə Dairəsi |
|---|------|---------|---------------|
| 1 | **super_admin** | Global | Bütün sistemə tam giriş |
| 2 | **owner** | Global | Şirkət sahibi, bütün filialları görür |
| 3 | **branch_manager** | Filial | Öz filialının tam idarəsi |
| 4 | **academic_manager** | Filial | Kurs, qrup, müəllim, dərs cədvəli |
| 5 | **accountant** | Filial | Ödənişlər, maaşlar, gəlir/xərc |
| 6 | **hr** | Filial | İşçi qeydiyyatı, maaş, sənədlər |
| 7 | **marketing** | Filial | Kuponlar, endirimlər, bildirişlər |
| 8 | **reception** | Filial | Tələbə qeydiyyatı, ödəniş qəbulu |
| 9 | **teacher** | Qrup | Öz dərsləri, qiymət, davamiyyət |
| 10 | **student** | Şəxsi | Öz məlumatları, cədvəl, qiymətlər |

Hər permission `{module}.{action}` formatındadır:

```
students.create, students.read, students.update, students.delete
groups.create, groups.read, groups.update, groups.delete
payments.read, payments.create, payments.refund
...
```

Frontend-də hər səhifə, hər button, hər API call permission bazasında göstərilir/gizlədilir.

---

## 5. API URL STRUCTURE (RESTful)

```
# Auth
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/refresh/
POST   /api/v1/auth/password-reset/
POST   /api/v1/auth/password-reset/confirm/
GET    /api/v1/auth/me/
PATCH  /api/v1/auth/me/

# Users
GET    /api/v1/users/
POST   /api/v1/users/
GET    /api/v1/users/{id}/
PATCH  /api/v1/users/{id}/
DELETE /api/v1/users/{id}/

# Roles
GET    /api/v1/roles/
POST   /api/v1/roles/
GET    /api/v1/roles/{id}/
PATCH  /api/v1/roles/{id}/
DELETE /api/v1/roles/{id}/
GET    /api/v1/roles/{id}/permissions/
POST   /api/v1/roles/{id}/permissions/
DELETE /api/v1/roles/{id}/permissions/{permission_id}/

# Permissions
GET    /api/v1/permissions/

# Branches
GET    /api/v1/branches/
POST   /api/v1/branches/
GET    /api/v1/branches/{id}/
PATCH  /api/v1/branches/{id}/
DELETE /api/v1/branches/{id}/
GET    /api/v1/branches/{id}/rooms/
POST   /api/v1/branches/{id}/rooms/
PATCH  /api/v1/branches/{id}/rooms/{room_id}/
DELETE /api/v1/branches/{id}/rooms/{room_id}/
GET    /api/v1/branches/{id}/statistics/

# Employees
GET    /api/v1/employees/
POST   /api/v1/employees/
GET    /api/v1/employees/{id}/
PATCH  /api/v1/employees/{id}/
DELETE /api/v1/employees/{id}/

# Students
GET    /api/v1/students/
POST   /api/v1/students/
GET    /api/v1/students/{id}/
PATCH  /api/v1/students/{id}/
DELETE /api/v1/students/{id}/
GET    /api/v1/students/{id}/payments/
GET    /api/v1/students/{id}/grades/
GET    /api/v1/students/{id}/attendance/
GET    /api/v1/students/{id}/groups/

# Parents
GET    /api/v1/parents/
POST   /api/v1/parents/
GET    /api/v1/parents/{id}/
PATCH  /api/v1/parents/{id}/
DELETE /api/v1/parents/{id}/

# Teachers
GET    /api/v1/teachers/
POST   /api/v1/teachers/
GET    /api/v1/teachers/{id}/
PATCH  /api/v1/teachers/{id}/
DELETE /api/v1/teachers/{id}/
GET    /api/v1/teachers/{id}/groups/
GET    /api/v1/teachers/{id}/schedule/
GET    /api/v1/teachers/{id}/salary/

# Course Categories
GET    /api/v1/course-categories/
POST   /api/v1/course-categories/
GET    /api/v1/course-categories/{id}/
PATCH  /api/v1/course-categories/{id}/
DELETE /api/v1/course-categories/{id}/

# Courses
GET    /api/v1/courses/
POST   /api/v1/courses/
GET    /api/v1/courses/{id}/
PATCH  /api/v1/courses/{id}/
DELETE /api/v1/courses/{id}/

# Groups
GET    /api/v1/groups/
POST   /api/v1/groups/
GET    /api/v1/groups/{id}/
PATCH  /api/v1/groups/{id}/
DELETE /api/v1/groups/{id}/
POST   /api/v1/groups/{id}/students/
DELETE /api/v1/groups/{id}/students/{student_id}/
GET    /api/v1/groups/{id}/schedule/
GET    /api/v1/groups/{id}/lessons/

# Schedule (recurring)
GET    /api/v1/schedules/
POST   /api/v1/schedules/
PATCH  /api/v1/schedules/{id}/
DELETE /api/v1/schedules/{id}/

# Lessons
GET    /api/v1/lessons/
POST   /api/v1/lessons/  (auto-generate from schedule)
GET    /api/v1/lessons/{id}/
PATCH  /api/v1/lessons/{id}/
DELETE /api/v1/lessons/{id}/

# Attendance
GET    /api/v1/attendance/
POST   /api/v1/attendance/  (bulk for a lesson)
PATCH  /api/v1/attendance/{id}/

# Exams
GET    /api/v1/exams/
POST   /api/v1/exams/
GET    /api/v1/exams/{id}/
PATCH  /api/v1/exams/{id}/
DELETE /api/v1/exams/{id}/
POST   /api/v1/exams/{id}/results/ (bulk grade entry)

# Homework
GET    /api/v1/homework/
POST   /api/v1/homework/
GET    /api/v1/homework/{id}/
PATCH  /api/v1/homework/{id}/
DELETE /api/v1/homework/{id}/
POST   /api/v1/homework/{id}/submit/
GET    /api/v1/homework/{id}/submissions/

# Payments
GET    /api/v1/payments/
POST   /api/v1/payments/
GET    /api/v1/payments/{id}/
PATCH  /api/v1/payments/{id}/
DELETE /api/v1/payments/{id}/
POST   /api/v1/payments/{id}/refund/
GET    /api/v1/payments/{id}/installments/
POST   /api/v1/payments/{id}/installments/{installment_id}/pay/

# Discounts
GET    /api/v1/discounts/
POST   /api/v1/discounts/
PATCH  /api/v1/discounts/{id}/
DELETE /api/v1/discounts/{id}/

# Coupons
GET    /api/v1/coupons/
POST   /api/v1/coupons/
PATCH  /api/v1/coupons/{id}/
DELETE /api/v1/coupons/{id}/
POST   /api/v1/coupons/{code}/validate/

# Finance
GET    /api/v1/finance/income-categories/
POST   /api/v1/finance/income-categories/
GET    /api/v1/finance/expense-categories/
POST   /api/v1/finance/expense-categories/
GET    /api/v1/finance/expenses/
POST   /api/v1/finance/expenses/
PATCH  /api/v1/finance/expenses/{id}/
DELETE /api/v1/finance/expenses/{id}/
GET    /api/v1/finance/overview/  (profit/loss summary)
GET    /api/v1/finance/income-vs-expense-chart/

# Salaries
GET    /api/v1/salaries/employees/
POST   /api/v1/salaries/employees/pay/
GET    /api/v1/salaries/teachers/
POST   /api/v1/salaries/teachers/pay/
GET    /api/v1/salaries/summary/

# Notifications
GET    /api/v1/notifications/
POST   /api/v1/notifications/mark-read/
POST   /api/v1/notifications/mark-all-read/
GET    /api/v1/notifications/unread-count/

# SMS / Email
POST   /api/v1/notifications/send-sms/
POST   /api/v1/notifications/send-email/
POST   /api/v1/notifications/send-bulk/

# File Upload
POST   /api/v1/files/upload/
GET    /api/v1/files/{id}/
DELETE /api/v1/files/{id}/

# Reports
GET    /api/v1/reports/student-summary/
GET    /api/v1/reports/financial-summary/
GET    /api/v1/reports/teacher-performance/
GET    /api/v1/reports/attendance-summary/
GET    /api/v1/reports/branch-comparison/

# Activity Log
GET    /api/v1/activity-logs/
GET    /api/v1/activity-logs/{id}/

# Dashboard
GET    /api/v1/dashboard/summary/
GET    /api/v1/dashboard/charts/
GET    /api/v1/dashboard/recent-activity/
GET    /api/v1/dashboard/upcoming-lessons/
GET    /api/v1/dashboard/overdue-payments/

# Settings
GET    /api/v1/settings/
PATCH  /api/v1/settings/
GET    /api/v1/settings/{key}/
PATCH  /api/v1/settings/{key}/
```

Bütün API-lər versiyalanmışdır (`/api/v1/`). Hər response pagination, filtering, sorting dəstəkləyir.

---

## 6. SIDEBAR NAVIGATION STRUCTURE

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Global Search (Cmd+K)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Dashboard                                               │
│                                                             │
│  🏢 Filiallar                                               │
│  ├── Bütün filiallar                                        │
│  ├── Filial əlavə et                                       │
│  └── Sinif otaqları                                         │
│                                                             │
│  👥 İdarəetmə                                               │
│  ├── İşçilər                                                │
│  ├── Rollar & İcazələr                                      │
│  └── İstifadəçilər                                          │
│                                                             │
│  📚 Tədris                                                  │
│  ├── Tələbələr                                              │
│  ├── Valideynlər                                            │
│  ├── Müəllimlər                                             │
│  ├── Kurs kateqoriyaları                                    │
│  ├── Kurslar                                                │
│  └── Qruplar                                                │
│                                                             │
│  📅 Dərslər                                                 │
│  ├── Dərs cədvəli                                           │
│  ├── Dərslər                                                │
│  ├── Davamiyyət                                             │
│  ├── İmtahanlar                                             │
│  ├── Qiymətlər                                              │
│  └── Ev tapşırıqları                                        │
│                                                             │
│  💰 Maliyyə                                                 │
│  ├── Ödənişlər                                              │
│  ├── Taksitlər                                              │
│  ├── Gəlirlər                                               │
│  ├── Xərclər                                                │
│  ├── Endirimlər                                             │
│  ├── Kuponlar                                               │
│  ├── Müəllim maaşları                                       │
│  └── İşçi maaşları                                          │
│                                                             │
│  📊 Hesabatlar                                              │
│  ├── Tələbə hesabatları                                     │
│  ├── Maliyyə hesabatları                                    │
│  ├── Müəllim performansı                                    │
│  ├── Davamiyyət hesabatları                                 │
│  └── Filial müqayisəsi                                      │
│                                                             │
│  🔔 Bildirişlər                                             │
│  ├── Bildirişlər                                            │
│  ├── SMS göndər                                             │
│  └── Email göndər                                           │
│                                                             │
│  📁 Fayllar                                                 │
│                                                             │
│  📋 Audit                                                   │
│  ├── Activity Log                                           │
│  └── Audit Log                                              │
│                                                             │
│  ⚙️ Ayarlar                                                 │
│  ├── Sistem ayarları                                        │
│  └── Profil                                                 │
│                                                             │
│  ─────────────────────────────────────────────────          │
│                                                             │
│  🌙 Dark Mode toggle                                        │
│  👤 User avatar + dropdown                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Sidebar **collapsible** olmalıdır (icon-only mode). Hər bir menu item-i üçün **badge** dəstəyi (bildiriş sayı, gözləyən ödəniş sayı). Alt menu-lar **accordion** şəklində açılır.

---

## 7. DASHBOARD WIDGETS

### 7.1 — Stats Row (4 cards)
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 👥 Tələbələr    │ │ 👨‍🏫 Müəllimlər │ │ 📚 Kurslar      │ │ 👥 Qruplar      │
│ 1,234           │ │ 48              │ │ 12              │ │ 36              │
│ ↑ 12% this month│ │ ↑ 2% this month│ │ —               │ │ ↑ 8% this month│
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 7.2 — Financial Row (3 cards)
```
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ 💰 Bu Ay Gəlir     │ │ 💸 Bu Ay Xərc      │ │ 📈 Mənfəət         │
│ ₼45,230            │ │ ₼18,400            │ │ ₼26,830            │
│ ↑ 15% vs last month│ │ ↑ 5% vs last month │ │ ↑ 22% vs last month│
└────────────────────┘ └────────────────────┘ └────────────────────┘
```

### 7.3 — Charts Row (2 cards)
```
┌──────────────────────────────────────────┐ ┌──────────────────────────────────────────┐
│ 📊 Gəlir vs Xərc (Line Chart)           │ │ 🍩 Ödəniş metodları (Pie Chart)          │
│                                          │ │                                          │
│  ┤     ╱╲     ╱╲                         │ │  ┌─────┐  Nağd: 45%                     │
│  ┤    ╱  ╲   ╱  ╲    ╱╲                 │ │  │  ●  │  Kart: 30%                     │
│  ┤   ╱    ╲ ╱    ╲  ╱  ╲                │ │  └─────┘  Transfer: 15%                 │
│  ┤  ╱      ╲      ╲╱    ╲               │ │            POS: 10%                      │
│  └─┴───┴───┴──────┴──────┴──            │ │                                          │
│     Jan Feb Mar Apr May Jun              │ │                                          │
└──────────────────────────────────────────┘ └──────────────────────────────────────────┘
```

### 7.4 — Activity & Upcoming (2 columns)
```
┌──────────────────────────────────────────┐ ┌──────────────────────────────────────────┐
│ 📅 Bu gün dərslər                        │ │ 🔔 Son fəaliyyətlər                      │
│                                          │ │                                          │
│ 10:00 - Python 101 - Qrup A (Room 1)    │ │ 2 dəq əvvəl - Tələbə qeydiyyatı          │
│ 12:00 - Math - Qrup B (Room 2)          │ │ 15 dəq əvvəl - Ödəniş qəbulu             │
│ 14:00 - English - Qrup C (Room 1)       │ │ 1 saat əvvəl - Yeni qrup yaradıldı       │
│ 16:00 - Physics - Qrup D (Room 3)       │ │ 2 saat əvvəl - Müəllim maaşı ödəndi      │
│                                          │ │                                          │
│ 📌 Gecikən ödənişlər (5)                │ │ 📊 Bu həftə statistika                    │
│ Aliyeva A. - ₼200 - 5 gün gecikmiş      │ │ Yeni qeydiyyat: 12                        │
│ Karimov K. - ₼350 - 12 gün gecikmiş     │ │ Davamiyyət: 94%                           │
│                                          │ │ Orta qiymət: 78.5                         │
└──────────────────────────────────────────┘ └──────────────────────────────────────────┘
```

### 7.5 — Calendar Mini
```
┌───────────────────────────────────────────────────────────────┐
│ 📅 İyul 2026                                                  │
│  B.e  Ç.a  Ç.r  C.a  Cüm  Şən  Baz                           │
│       1    2    3    4    5    6                              │
│  7    8    9   10   11   12   13                              │
│ 14   15   16   17   18   19   20                              │
│ 21   22   23   24   25   26   27                              │
│ 28   29   30   31                                             │
│                                                               │
│ ● Python dərsi - Qrup A (10:00)                               │
│ ● Riyaziyyat - Qrup B (14:00)                                 │
└───────────────────────────────────────────────────────────────┘
```

### 7.6 — Recent Registrations
```
┌───────────────────────────────────────────────────────────────┐
│ 🆕 Son qeydiyyatlar (cədvəl)                                 │
│ ┌──────┬──────────┬──────────┬──────────┬──────────┐         │
│ │ Tarix│ Ad       │ Kurs     │ Filial   │ Status   │         │
│ ├──────┼──────────┼──────────┼──────────┼──────────┤         │
│ │ Bugün│ Əliyev A.│ Python   │ Bakı     │ Təsdiqləndi│       │
│ │ Dünən│ Quliyeva │ İngilis  │ Sumqayıt │ Gözləyir │        │
│ │ Dünən│ Həsənov  │ Riyaz.   │ Bakı     │ Təsdiqləndi│       │
│ └──────┴──────────┴──────────┴──────────┴──────────┘         │
└───────────────────────────────────────────────────────────────┘
```

---

## 8. PAGE INVENTORY (Hər səhifədə nə var)

### 8.1 — Dashboard
- Statistik kartlar (6-8 ədəd)
- Gəlir/Xərc qrafiki (son 12 ay)
- Ödəniş metodları pie chart
- Bu gün dərslərin siyahısı
- Gecikən ödənişlər
- Son fəaliyyətlər feed
- Son qeydiyyatlar cədvəli
- Mini təqvim
- Son bildirişlər

### 8.2 — Branch List / Detail
- **List:** Kart görünüşü (logo, ad, ünvan, status, menecer), aktiv/inactive filtrləri
- **Detail:** Ümumi məlumat, sinif otaqları (CRUD), statistik göstəricilər (tələbə sayı, gəlir, xərc), xəritə
- **Form:** Ad, loqo, ünvan, telefon, email, menecer (select), iş saatları (JSON), status

### 8.3 — Student List / Detail
- **List:** Cədvəl (şəkil, ID, ad, əlaqə, qrup, status, son ödəniş), search, filtrlər (filial, qrup, status), export
- **Detail:** Profil kartı, qruplar, ödəniş tarixçəsi, davamiyyət %, qiymətlər, sənədlər
- **Form:** Şəxsi məlumat, valideyn seçimi, qeydiyyat tarixi, qeydlər

### 8.4 — Payment Management
- **List:** Cədvəl (faktura, tələbə, məbləğ, metod, status, tarix), search, filtrlər (status, metod, tarix aralığı)
- **Create:** Tələbə seçimi, məbləğ, endirim/kupon tətbiqi, taksit planı, ödəniş metodu
- **Detail:** Ödəniş məlumatları, taksit cədvəli (hər taksit: nömrə, məbləğ, son tarix, status, ödəniş tarixi)

### 8.5 — Attendance
- **Guruh seçimi + tarix seçimi** → dərsdəki tələbələrin siyahısı
- Hər tələbə üçün status (present/absent/late/excused) — radio button qrupu
- **Bulk actions:** hamısını present et, hamısını absent et
- **Summary:** bugünkü davamiyyət statistikası

### 8.6 — Exam / Grade
- **List:** İmtahanlar (qrup, ad, tip, tarix, status)
- **Detail:** İmtahan məlumatları, tələbə nəticələri cədvəli (bal, faiz, hərf qiyməti)
- **Grade Entry:** Tələbə siyahısı + bal girişi (bulk input)

### 8.7 — Salary
- **Müəllim maaşı:** Ayda işlədiyi saat * saatlıq tarif
- **İşçi maaşı:** Sabit aylıq + bonus - cərimə
- **Ödəniş:** Ay/il seçimi + hamısını birdən ödə

### 8.8 — Reports
- **Filters:** Tarix aralığı, filial, qrup, müəllim
- **Charts:** Bar chart, line chart, pie chart
- **Export:** PDF, Excel
- **Predefined:** Tələbə sayı, gəlir hesabatı, davamiyyət %, müəllim yükü

---

## 9. UI/UX DESIGN SYSTEM

### 9.1 — Design Tokens

```
Colors:
  Primary:     #6366F1 (Indigo)
  Secondary:   #8B5CF6 (Violet)
  Success:     #10B981 (Emerald)
  Warning:     #F59E0B (Amber)
  Error:       #EF4444 (Red)
  Info:        #3B82F6 (Blue)
  
  Background:  #F9FAFB (light) / #0F172A (dark)
  Surface:     #FFFFFF  (light) / #1E293B (dark)
  Border:      #E2E8F0  (light) / #334155 (dark)
  Text:        #0F172A  (light) / #F1F5F9 (dark)
  
Typography:
  Font:        Inter / Plus Jakarta Sans
  Scale:       12, 14, 16, 18, 20, 24, 30, 36, 48, 60

Spacing:
  Grid:        4px base
  Container:   1200px max

Shadows:
  Card:        0 1px 3px rgba(0,0,0,0.1) 
  Dropdown:    0 10px 15px -3px rgba(0,0,0,0.1)
  Modal:       0 25px 50px -12px rgba(0,0,0,0.25)

Radius:
  Button:      8px
  Card:        12px
  Modal:       16px
  Input:       8px
  Avatar:      Full (50%)
```

### 9.2 — Component Library

```
Atoms:
  Button (Primary, Secondary, Ghost, Danger, Outline)
  Input (Text, Email, Password, Number, Date, Phone)
  Select (Single, Multi, Searchable)
  Checkbox, Radio, Toggle, Switch
  Badge, Tag, StatusDot
  Avatar, AvatarGroup
  Icon (Feather Icons / Lucide)
  Tooltip, Popover
  Skeleton (Loading)
  
Molecules:
  Card (with header, body, footer variants)
  Table (sortable, filterable, selectable rows)
  Modal (with sizes: sm, md, lg, xl, fullscreen)
  Toast (top-right stack, auto-dismiss)
  DropdownMenu
  Tabs (underline, pill, icon)
  Breadcrumb
  Pagination
  EmptyState (with illustration)
  ConfirmDialog
  FileUpload (drag & drop)
  FormGroup (label + input + error + hint)
  
Organisms:
  Sidebar (collapsible, accordion submenu, badge)
  TopNavbar (search, notification bell, user menu)
  DataTable (server-side: search, sort, filter, pagination, export)
  StatsCard (trend indicator, icon, value)
  ChartCard (with date range picker)
  KanbanView (for lessons/events)
  CalendarView (month/week/day)
  FilterBar (multi-select, date range, search)
  ActivityFeed (timeline)
  
Templates:
  ListPage = TopBar + FilterBar + DataTable + Pagination
  DetailPage = Tabs (Overview, History, Related)
  FormPage = Stepper or Single Page Form
  Dashboard = StatsRow + ChartsRow + TablesRow
```

### 9.3 — Dark Mode Strategy

- CSS Custom Properties (design tokens)
- `data-theme="light|dark"` on `<html>`
- Sistem tercihinə avtomatik uyğunlaşma (`prefers-color-scheme`)
- User manual override (localStorage)
- Animations: smooth transition (0.3s)

### 9.4 — Responsive Strategy

| Breakpoint | Device | Layout |
|-----------|--------|--------|
| < 640px | Mobile | Sidebar hidden (hamburger), stacked cards |
| 640-1024 | Tablet | Sidebar collapsed (icons), 2-col grids |
| 1024-1440 | Desktop | Full sidebar, 3-col grids |
| > 1440 | Wide | Max-width container, multi-col |

---

## 10. SCALABILITY & FUTURE PROOFING

### 10.1 — Backend Architecture

```
apps/                    # Modular app structure
├── common/              # Shared utilities
│   ├── models.py        # BaseModel (UUID pk, timestamps)
│   ├── pagination.py    # Custom pagination classes
│   ├── filters.py       # Advanced filtering (django-filter)
│   ├── permissions.py   # Dynamic permission checking
│   ├── mixins.py        # Reusable view mixins
│   ├── choices.py       # Global choice enums
│   └── signals.py       # Common signal handlers
├── ... modules ...

core/                    # Project-level config
├── middlewares/         # Custom middleware
│   ├── audit_middleware.py
│   ├── branch_middleware.py
│   └── timezone_middleware.py
```

### 10.2 — Key Architectural Decisions

1. **UUID Primary Keys** — Bütün modellərdə integer əvəzinə UUID istifadə edilir. Bu, gələcəkdə sharding, merger, data migration üçün vacibdir.

2. **Branch Isolation** — Bütün məlumatlar `branch_id` ilə işarələnir. Middleware avtomatik olaraq cari istifadəçinin filialına uyğun məlumatları filtr edir.

3. **Soft Delete** — Heç bir məlumat birdəfəlik silinmir. Hər modeldə `is_active` və ya `deleted_at` sahəsi var.

4. **JSONB Fields** — Dinamik strukturlar üçün (iş saatları, təhsil məlumatları, kurikulum). Gələcəkdə yeni sahə əlavə etmək üçün migration tələb olunmur.

5. **Service Layer** — View-lər birbaşa model çağırmır. Hər modul üçün `services.py` faylı iş məntiqini özündə saxlayır. View → Service → Model.

6. **Caching** — Redis ilə tez-tez sorğulanan məlumatlar (dashboard stats, tələbə sayı) cache edilir.

7. **Celery / Background Tasks** — Email göndərilməsi, SMS, hesabat yaradılması, bulk əməliyyatlar background queue-da işlənir.

8. **API Versioning** — `/api/v1/`, `/api/v2/`. Köhnə versiyalar dəstəklənir, tədricən deprecated edilir.

9. **Throttling & Rate Limiting** — Hər API endpoint üçün rate limit (Django REST throttling).

10. **Comprehensive Logging** — Hər bir əməliyyat activity_logs cədvəlində qeyd olunur. Audit trail tam şəffafdır.

### 10.3 — Future Expansion Points

- **Multi-language** (az, en, ru) — model-səviyyəsində dil dəstəyi (django-modeltranslation)
- **Multi-currency** — AZN, USD, EUR dəstəyi
- **Online Payment Gateway** — Stripe, PayPal, və yerli provider inteqrasiyası
- **Zoom/Google Meet** — Dərsləri online keçirmək üçün video konfrans inteqrasiyası
- **Mobile App** — Backend hazır olduqda React Native / Flutter app
- **WhatsApp Integration** — Bildirişlər üçün WhatsApp Business API
- **AI/ML** — Tələbə performans proqnozu, davamiyyət analizi, tövsiyə sistemi
- **POS Integration** — Kassa aparatı ilə inteqrasiya
- **1C Integration** — Mühasibat proqramı ilə məlumat mübadiləsi
- **LMS (Learning Management System)** — Online dərs materialı, video, test sistemi

---

## 11. MODULE RELATIONSHIP MAP

```
Branches
  ├── BranchRooms
  ├── Employees (through branch_id)
  │   ├── SalaryPayments
  │   └── Teacher (optional, if employee is teacher)
  ├── Teachers (through branch_id)
  │   ├── TeacherSalaryPayments
  │   ├── Groups (as teacher)
  │   ├── Lessons (as teacher)
  │   └── Homework (as creator)
  ├── Students (through branch_id)
  │   ├── Parents
  │   ├── GroupStudents (through groups)
  │   ├── Attendance
  │   ├── ExamResults
  │   ├── HomeworkSubmissions
  │   └── Payments
  │       └── Installments
  ├── Groups (through branch_id)
  │   ├── GroupStudents
  │   ├── Schedules
  │   └── Lessons
  ├── Courses
  │   └── CourseCategories
  ├── Expenses
  ├── Payments
  └── Exams
      └── ExamResults

Users
  ├── Students (OneToOne)
  ├── Teachers (OneToOne)
  ├── Employees (OneToOne)
  ├── Parents (OneToOne)
  └── UserRoles
      └── Roles
          └── Permissions
```

---

## 12. IMPLEMENTATION ORDER (Təklif olunan sıra)

| Mərhələ | Modullar | Təxmini vaxt |
|---------|----------|-------------|
| **Faza 1** | Auth + RBAC + Users + Branches + System Settings | 5 gün |
| **Faza 2** | Employees + Teachers + Students + Parents | 5 gün |
| **Faza 3** | Course Categories + Courses + Groups + Schedules | 5 gün |
| **Faza 4** | Lessons + Attendance | 3 gün |
| **Faza 5** | Exams + Grades + Homework | 4 gün |
| **Faza 6** | Payments + Installments + Discounts + Coupons | 5 gün |
| **Faza 7** | Finance + Expenses + Salaries | 4 gün |
| **Faza 8** | Notifications (Email/SMS) + File Management | 3 gün |
| **Faza 9** | Reports + Dashboard APIs | 4 gün |
| **Faza 10** | Audit Log + Activity Log + Permissions tuning | 2 gün |
| **Faza 11** | Frontend integration + Testing + Deployment | 10 gün |
| | **Cəmi** | **~50 gün** |

---

*Bu plan təsdiq edildikdən sonra modul-modul implementasiyaya başlayırıq. Hər fazada: Model → Serializer → View → URL → Test → API Documentation.*
