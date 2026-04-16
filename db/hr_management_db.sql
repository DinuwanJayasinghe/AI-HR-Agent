-- ============================================================
-- AI-Powered HR Management System
-- Database : hr_management_db  (PostgreSQL)
-- Total Tables : 21
-- Compatible with pgAdmin 4 / PostgreSQL 13+
-- ============================================================

-- Enable UUID extension (must be first)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- DROP all tables in reverse dependency order (safe re-run)
-- ============================================================
DROP TABLE IF EXISTS audit_logs                CASCADE;
DROP TABLE IF EXISTS notifications             CASCADE;
DROP TABLE IF EXISTS ai_interviews             CASCADE;
DROP TABLE IF EXISTS candidates                CASCADE;
DROP TABLE IF EXISTS job_postings              CASCADE;
DROP TABLE IF EXISTS performance_scores        CASCADE;
DROP TABLE IF EXISTS performance_evaluations   CASCADE;
DROP TABLE IF EXISTS performance_metrics       CASCADE;
DROP TABLE IF EXISTS payroll_records           CASCADE;
DROP TABLE IF EXISTS payroll_runs              CASCADE;
DROP TABLE IF EXISTS leave_applications        CASCADE;
DROP TABLE IF EXISTS leave_balances            CASCADE;
DROP TABLE IF EXISTS leave_types               CASCADE;
DROP TABLE IF EXISTS overtime_records          CASCADE;
DROP TABLE IF EXISTS attendance_records        CASCADE;
DROP TABLE IF EXISTS face_embeddings           CASCADE;
DROP TABLE IF EXISTS employees                 CASCADE;
DROP TABLE IF EXISTS positions                 CASCADE;
DROP TABLE IF EXISTS departments               CASCADE;
DROP TABLE IF EXISTS sessions                  CASCADE;
DROP TABLE IF EXISTS users                     CASCADE;

-- Drop trigger function if exists
DROP FUNCTION IF EXISTS fn_set_updated_at() CASCADE;

-- ============================================================
-- TABLE 1 : users
-- Stores authentication credentials and roles for all system users.
-- ============================================================
CREATE TABLE users (
    user_id       UUID          NOT NULL DEFAULT gen_random_uuid(),
    email         VARCHAR(255)  NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    role          VARCHAR(50)   NOT NULL
                      CHECK (role IN ('employee', 'hr_manager', 'admin', 'super_admin')),
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE,
    last_login    TIMESTAMP     NULL,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_pkey     PRIMARY KEY (user_id),
    CONSTRAINT users_email_uq UNIQUE (email)
);

-- ============================================================
-- TABLE 2 : sessions
-- Manages active JWT session tokens for authenticated users.
-- ============================================================
CREATE TABLE sessions (
    session_id UUID          NOT NULL DEFAULT gen_random_uuid(),
    user_id    UUID          NOT NULL,
    token_hash VARCHAR(255)  NOT NULL,
    expires_at TIMESTAMP     NOT NULL,
    ip_address INET          NULL,
    user_agent TEXT          NULL,
    created_at TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT sessions_pkey       PRIMARY KEY (session_id),
    CONSTRAINT sessions_user_id_fk FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 3 : departments
-- Organisational departments within the company.
-- NOTE: manager_id FK to employees added after TABLE 5 (employees).
-- ============================================================
CREATE TABLE departments (
    department_id        UUID          NOT NULL DEFAULT gen_random_uuid(),
    department_name      VARCHAR(100)  NOT NULL,
    department_code      VARCHAR(20)   NOT NULL,
    description          TEXT          NULL,
    manager_id           UUID          NULL,
    parent_department_id UUID          NULL,
    is_active            BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT departments_pkey          PRIMARY KEY (department_id),
    CONSTRAINT departments_name_uq       UNIQUE (department_name),
    CONSTRAINT departments_code_uq       UNIQUE (department_code),
    CONSTRAINT departments_parent_fk     FOREIGN KEY (parent_department_id)
        REFERENCES departments (department_id)
);

-- ============================================================
-- TABLE 4 : positions
-- Job positions and salary bands within departments.
-- ============================================================
CREATE TABLE positions (
    position_id    UUID           NOT NULL DEFAULT gen_random_uuid(),
    position_title VARCHAR(100)   NOT NULL,
    position_code  VARCHAR(20)    NOT NULL,
    department_id  UUID           NULL,
    level          VARCHAR(50)    NULL
                       CHECK (level IN ('junior', 'mid', 'senior', 'lead', 'manager', 'director')),
    description    TEXT           NULL,
    min_salary     DECIMAL(12,2)  NULL CHECK (min_salary >= 0),
    max_salary     DECIMAL(12,2)  NULL CHECK (max_salary >= 0),
    is_active      BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positions_pkey          PRIMARY KEY (position_id),
    CONSTRAINT positions_code_uq       UNIQUE (position_code),
    CONSTRAINT positions_dept_fk       FOREIGN KEY (department_id)
        REFERENCES departments (department_id),
    CONSTRAINT positions_salary_check  CHECK (
        min_salary IS NULL OR max_salary IS NULL OR max_salary >= min_salary
    )
);

-- ============================================================
-- TABLE 5 : employees
-- Core employee master data including personal details,
-- employment info, and salary.
-- ============================================================
CREATE TABLE employees (
    employee_id             UUID           NOT NULL DEFAULT gen_random_uuid(),
    user_id                 UUID           NULL,
    employee_number         VARCHAR(50)    NOT NULL,
    first_name              VARCHAR(100)   NOT NULL,
    last_name               VARCHAR(100)   NOT NULL,
    date_of_birth           DATE           NULL,
    gender                  VARCHAR(20)    NULL
                                CHECK (gender IN ('male', 'female', 'other')),
    phone                   VARCHAR(20)    NULL,
    emergency_contact_name  VARCHAR(100)   NULL,
    emergency_contact_phone VARCHAR(20)    NULL,
    address                 TEXT           NULL,
    city                    VARCHAR(100)   NULL,
    country                 VARCHAR(100)   NOT NULL DEFAULT 'Sri Lanka',
    postal_code             VARCHAR(20)    NULL,
    department_id           UUID           NULL,
    position_id             UUID           NULL,
    manager_id              UUID           NULL,
    employment_type         VARCHAR(50)    NULL
                                CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'intern')),
    hire_date               DATE           NOT NULL,
    termination_date        DATE           NULL,
    employment_status       VARCHAR(50)    NOT NULL DEFAULT 'active',
    base_salary             DECIMAL(12,2)  NOT NULL CHECK (base_salary > 0),
    currency                VARCHAR(10)    NOT NULL DEFAULT 'LKR',
    bank_account_number     VARCHAR(50)    NULL,
    bank_name               VARCHAR(100)   NULL,
    created_at              TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              UUID           NULL,

    CONSTRAINT employees_pkey          PRIMARY KEY (employee_id),
    CONSTRAINT employees_number_uq     UNIQUE (employee_number),
    CONSTRAINT employees_user_fk       FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT employees_dept_fk       FOREIGN KEY (department_id)
        REFERENCES departments (department_id),
    CONSTRAINT employees_position_fk   FOREIGN KEY (position_id)
        REFERENCES positions (position_id),
    CONSTRAINT employees_manager_fk    FOREIGN KEY (manager_id)
        REFERENCES employees (employee_id),
    CONSTRAINT employees_created_by_fk FOREIGN KEY (created_by)
        REFERENCES users (user_id)
);

-- Add deferred FK: departments.manager_id -> employees.employee_id
-- (circular reference: departments created before employees)
ALTER TABLE departments
    ADD CONSTRAINT departments_manager_fk
    FOREIGN KEY (manager_id)
    REFERENCES employees (employee_id)
    DEFERRABLE INITIALLY DEFERRED;

-- ============================================================
-- TABLE 6 : face_embeddings
-- Encrypted facial recognition vectors used for attendance
-- biometric verification.
-- ============================================================
CREATE TABLE face_embeddings (
    embedding_id     UUID           NOT NULL DEFAULT gen_random_uuid(),
    employee_id      UUID           NOT NULL,
    embedding_vector BYTEA          NOT NULL,
    encoding_model   VARCHAR(50)    NOT NULL DEFAULT 'facenet',
    quality_score    DECIMAL(5,4)   NULL CHECK (quality_score BETWEEN 0 AND 1),
    is_primary       BOOLEAN        NOT NULL DEFAULT FALSE,
    captured_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at       TIMESTAMP      NULL,
    created_at       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT face_embeddings_pkey        PRIMARY KEY (embedding_id),
    CONSTRAINT face_embeddings_employee_fk FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE
);

-- Only one primary embedding allowed per employee
CREATE UNIQUE INDEX face_embeddings_primary_uq
    ON face_embeddings (employee_id)
    WHERE is_primary = TRUE;

-- ============================================================
-- TABLE 7 : attendance_records
-- Daily attendance events recorded via face recognition,
-- RFID, or manual entry.
-- ============================================================
CREATE TABLE attendance_records (
    attendance_id        UUID           NOT NULL DEFAULT gen_random_uuid(),
    employee_id          UUID           NOT NULL,
    date                 DATE           NOT NULL,
    check_in_time        TIMESTAMP      NOT NULL,
    check_out_time       TIMESTAMP      NULL,
    check_in_method      VARCHAR(50)    NULL
                             CHECK (check_in_method IN
                                 ('face_recognition', 'manual', 'rfid', 'mobile_app')),
    check_in_confidence  DECIMAL(5,4)   NULL CHECK (check_in_confidence  BETWEEN 0 AND 1),
    check_in_location    VARCHAR(100)   NULL,
    check_in_device_id   VARCHAR(100)   NULL,
    check_out_method     VARCHAR(50)    NULL,
    check_out_confidence DECIMAL(5,4)   NULL CHECK (check_out_confidence BETWEEN 0 AND 1),
    check_out_location   VARCHAR(100)   NULL,
    check_out_device_id  VARCHAR(100)   NULL,
    total_hours          DECIMAL(5,2)   GENERATED ALWAYS AS (
                             CASE
                                 WHEN check_out_time IS NOT NULL THEN
                                     ROUND(
                                         CAST(EXTRACT(EPOCH FROM (check_out_time - check_in_time)) AS NUMERIC)
                                         / 3600.0, 2
                                     )
                                 ELSE NULL
                             END
                         ) STORED,
    status               VARCHAR(50)    NULL
                             CHECK (status IN ('present', 'late', 'half_day', 'absent', 'on_leave')),
    is_overtime          BOOLEAN        NOT NULL DEFAULT FALSE,
    approved_by          UUID           NULL,
    approved_at          TIMESTAMP      NULL,
    notes                TEXT           NULL,
    created_at           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT attendance_records_pkey          PRIMARY KEY (attendance_id),
    CONSTRAINT attendance_records_emp_date_uq   UNIQUE (employee_id, date),
    CONSTRAINT attendance_records_employee_fk   FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    CONSTRAINT attendance_records_approved_by_fk FOREIGN KEY (approved_by)
        REFERENCES users (user_id)
);

-- ============================================================
-- TABLE 8 : overtime_records
-- Overtime hours logged against attendance records,
-- with approval workflow.
-- ============================================================
CREATE TABLE overtime_records (
    overtime_id     UUID           NOT NULL DEFAULT gen_random_uuid(),
    employee_id     UUID           NOT NULL,
    attendance_id   UUID           NULL,
    date            DATE           NOT NULL,
    overtime_hours  DECIMAL(5,2)   NOT NULL CHECK (overtime_hours > 0),
    overtime_type   VARCHAR(50)    NULL
                        CHECK (overtime_type IN ('regular', 'weekend', 'holiday')),
    hourly_rate     DECIMAL(10,2)  NOT NULL CHECK (hourly_rate > 0),
    total_amount    DECIMAL(12,2)  GENERATED ALWAYS AS (
                        ROUND(overtime_hours * hourly_rate, 2)
                    ) STORED,
    requested_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_by     UUID           NULL,
    approved_at     TIMESTAMP      NULL,
    approval_status VARCHAR(50)    NOT NULL DEFAULT 'pending',
    notes           TEXT           NULL,
    created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT overtime_records_pkey            PRIMARY KEY (overtime_id),
    CONSTRAINT overtime_records_employee_fk     FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id),
    CONSTRAINT overtime_records_attendance_fk   FOREIGN KEY (attendance_id)
        REFERENCES attendance_records (attendance_id),
    CONSTRAINT overtime_records_approved_by_fk  FOREIGN KEY (approved_by)
        REFERENCES users (user_id)
);

-- ============================================================
-- TABLE 9 : leave_types
-- Master list of leave categories with entitlement rules.
-- ============================================================
CREATE TABLE leave_types (
    leave_type_id        UUID          NOT NULL DEFAULT gen_random_uuid(),
    leave_name           VARCHAR(100)  NOT NULL,
    leave_code           VARCHAR(20)   NOT NULL,
    description          TEXT          NULL,
    default_days_per_year INTEGER      NOT NULL DEFAULT 0,
    is_paid              BOOLEAN       NOT NULL DEFAULT TRUE,
    requires_approval    BOOLEAN       NOT NULL DEFAULT TRUE,
    max_consecutive_days INTEGER       NULL,
    min_notice_days      INTEGER       NOT NULL DEFAULT 0,
    is_active            BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT leave_types_pkey    PRIMARY KEY (leave_type_id),
    CONSTRAINT leave_types_code_uq UNIQUE (leave_code)
);

-- ============================================================
-- TABLE 10 : leave_balances
-- Per-employee annual leave entitlement balances,
-- updated automatically on approval.
-- ============================================================
CREATE TABLE leave_balances (
    balance_id      UUID          NOT NULL DEFAULT gen_random_uuid(),
    employee_id     UUID          NOT NULL,
    leave_type_id   UUID          NOT NULL,
    year            INTEGER       NOT NULL,
    total_allocated DECIMAL(5,2)  NOT NULL CHECK (total_allocated >= 0),
    used            DECIMAL(5,2)  NOT NULL DEFAULT 0 CHECK (used >= 0),
    remaining       DECIMAL(5,2)  GENERATED ALWAYS AS (total_allocated - used) STORED,
    carried_forward DECIMAL(5,2)  NOT NULL DEFAULT 0,
    updated_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT leave_balances_pkey             PRIMARY KEY (balance_id),
    CONSTRAINT leave_balances_emp_type_year_uq UNIQUE (employee_id, leave_type_id, year),
    CONSTRAINT leave_balances_employee_fk      FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    CONSTRAINT leave_balances_leave_type_fk    FOREIGN KEY (leave_type_id)
        REFERENCES leave_types (leave_type_id)
);

-- ============================================================
-- TABLE 11 : leave_applications
-- Employee leave requests with AI-powered approval decisions
-- and human override.
-- ============================================================
CREATE TABLE leave_applications (
    application_id         UUID          NOT NULL DEFAULT gen_random_uuid(),
    employee_id            UUID          NOT NULL,
    leave_type_id          UUID          NOT NULL,
    start_date             DATE          NOT NULL,
    end_date               DATE          NOT NULL,
    total_days             DECIMAL(5,2)  NOT NULL CHECK (total_days > 0),
    reason                 TEXT          NOT NULL,
    emergency_contact      VARCHAR(100)  NULL,
    substitute_employee_id UUID          NULL,
    ai_decision            VARCHAR(50)   NULL
                               CHECK (ai_decision IN ('approved', 'rejected', 'requires_review')),
    ai_reasoning           TEXT          NULL,
    ai_policy_references   JSONB         NULL,
    ai_confidence_score    DECIMAL(5,4)  NULL CHECK (ai_confidence_score BETWEEN 0 AND 1),
    ai_processed_at        TIMESTAMP     NULL,
    reviewed_by            UUID          NULL,
    reviewed_at            TIMESTAMP     NULL,
    final_decision         VARCHAR(50)   NULL
                               CHECK (final_decision IN ('pending', 'approved', 'rejected', 'cancelled')),
    reviewer_notes         TEXT          NULL,
    status                 VARCHAR(50)   NOT NULL DEFAULT 'pending',
    applied_at             TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at             TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT leave_applications_pkey           PRIMARY KEY (application_id),
    CONSTRAINT leave_applications_employee_fk    FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    CONSTRAINT leave_applications_leave_type_fk  FOREIGN KEY (leave_type_id)
        REFERENCES leave_types (leave_type_id),
    CONSTRAINT leave_applications_substitute_fk  FOREIGN KEY (substitute_employee_id)
        REFERENCES employees (employee_id),
    CONSTRAINT leave_applications_reviewed_by_fk FOREIGN KEY (reviewed_by)
        REFERENCES users (user_id),
    CONSTRAINT leave_applications_date_check     CHECK (end_date >= start_date)
);

-- ============================================================
-- TABLE 12 : payroll_runs
-- Payroll batch run header — one record per pay period.
-- ============================================================
CREATE TABLE payroll_runs (
    payroll_run_id     UUID           NOT NULL DEFAULT gen_random_uuid(),
    period_start       DATE           NOT NULL,
    period_end         DATE           NOT NULL,
    payment_date       DATE           NOT NULL,
    status             VARCHAR(50)    NOT NULL DEFAULT 'draft'
                           CHECK (status IN ('draft', 'processing', 'approved', 'paid', 'cancelled')),
    total_employees    INTEGER        NULL,
    total_gross_amount DECIMAL(15,2)  NULL,
    total_deductions   DECIMAL(15,2)  NULL,
    total_net_amount   DECIMAL(15,2)  NULL,
    processed_by       UUID           NULL,
    processed_at       TIMESTAMP      NULL,
    approved_by        UUID           NULL,
    approved_at        TIMESTAMP      NULL,
    notes              TEXT           NULL,
    created_at         TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payroll_runs_pkey            PRIMARY KEY (payroll_run_id),
    CONSTRAINT payroll_runs_processed_by_fk FOREIGN KEY (processed_by)
        REFERENCES users (user_id),
    CONSTRAINT payroll_runs_approved_by_fk  FOREIGN KEY (approved_by)
        REFERENCES users (user_id),
    CONSTRAINT payroll_runs_period_check    CHECK (period_end >= period_start)
);

-- ============================================================
-- TABLE 13 : payroll_records
-- Individual payslip data per employee per payroll run
-- with auto-computed totals.
-- ============================================================
CREATE TABLE payroll_records (
    payroll_id          UUID           NOT NULL DEFAULT gen_random_uuid(),
    payroll_run_id      UUID           NOT NULL,
    employee_id         UUID           NOT NULL,
    base_salary         DECIMAL(12,2)  NOT NULL CHECK (base_salary >= 0),
    overtime_amount     DECIMAL(12,2)  NOT NULL DEFAULT 0,
    bonuses             DECIMAL(12,2)  NOT NULL DEFAULT 0,
    allowances          DECIMAL(12,2)  NOT NULL DEFAULT 0,
    gross_salary        DECIMAL(12,2)  GENERATED ALWAYS AS (
                            base_salary + overtime_amount + bonuses + allowances
                        ) STORED,
    tax_deduction       DECIMAL(12,2)  NOT NULL DEFAULT 0,
    epf_deduction       DECIMAL(12,2)  NOT NULL DEFAULT 0,
    etf_deduction       DECIMAL(12,2)  NOT NULL DEFAULT 0,
    other_deductions    DECIMAL(12,2)  NOT NULL DEFAULT 0,
    total_deductions    DECIMAL(12,2)  GENERATED ALWAYS AS (
                            tax_deduction + epf_deduction + etf_deduction + other_deductions
                        ) STORED,
    net_salary          DECIMAL(12,2)  GENERATED ALWAYS AS (
                            (base_salary + overtime_amount + bonuses + allowances)
                            - (tax_deduction + epf_deduction + etf_deduction + other_deductions)
                        ) STORED,
    working_days        INTEGER        NULL,
    present_days        INTEGER        NULL,
    absent_days         INTEGER        NULL,
    leave_days          INTEGER        NULL,
    overtime_hours      DECIMAL(5,2)   NULL,
    payment_method      VARCHAR(50)    NULL
                            CHECK (payment_method IN ('bank_transfer', 'cash', 'cheque')),
    bank_account_number VARCHAR(50)    NULL,
    payment_status      VARCHAR(50)    NOT NULL DEFAULT 'pending',
    paid_at             TIMESTAMP      NULL,
    payment_reference   VARCHAR(100)   NULL,
    notes               TEXT           NULL,
    created_at          TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payroll_records_pkey        PRIMARY KEY (payroll_id),
    CONSTRAINT payroll_records_run_emp_uq  UNIQUE (payroll_run_id, employee_id),
    CONSTRAINT payroll_records_run_fk      FOREIGN KEY (payroll_run_id)
        REFERENCES payroll_runs (payroll_run_id) ON DELETE CASCADE,
    CONSTRAINT payroll_records_employee_fk FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 14 : performance_metrics
-- Weighted KPI definitions used in performance evaluations.
-- ============================================================
CREATE TABLE performance_metrics (
    metric_id          UUID          NOT NULL DEFAULT gen_random_uuid(),
    metric_name        VARCHAR(100)  NOT NULL,
    metric_code        VARCHAR(20)   NOT NULL,
    description        TEXT          NULL,
    metric_type        VARCHAR(50)   NULL
                           CHECK (metric_type IN
                               ('attendance', 'productivity', 'quality', 'behavior', 'leadership')),
    weight             DECIMAL(5,2)  NULL CHECK (weight BETWEEN 0 AND 100),
    calculation_method TEXT          NULL,
    is_active          BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT performance_metrics_pkey    PRIMARY KEY (metric_id),
    CONSTRAINT performance_metrics_code_uq UNIQUE (metric_code)
);

-- ============================================================
-- TABLE 15 : performance_evaluations
-- Periodic performance review records with AI-generated
-- insights and grade.
-- ============================================================
CREATE TABLE performance_evaluations (
    evaluation_id             UUID          NOT NULL DEFAULT gen_random_uuid(),
    employee_id               UUID          NOT NULL,
    evaluator_id              UUID          NULL,
    evaluation_period_start   DATE          NOT NULL,
    evaluation_period_end     DATE          NOT NULL,
    evaluation_type           VARCHAR(50)   NULL
                                  CHECK (evaluation_type IN
                                      ('monthly', 'quarterly', 'half_yearly', 'annual', 'probation')),
    overall_score             DECIMAL(5,2)  NULL CHECK (overall_score BETWEEN 0 AND 100),
    grade                     VARCHAR(10)   NULL,
    ai_generated_insights     TEXT          NULL,
    ai_recommendations        TEXT          NULL,
    ai_strengths              TEXT          NULL,
    ai_areas_for_improvement  TEXT          NULL,
    ai_processed_at           TIMESTAMP     NULL,
    evaluator_comments        TEXT          NULL,
    employee_comments         TEXT          NULL,
    employee_acknowledged     BOOLEAN       NOT NULL DEFAULT FALSE,
    employee_acknowledged_at  TIMESTAMP     NULL,
    status                    VARCHAR(50)   NOT NULL DEFAULT 'draft'
                                  CHECK (status IN ('draft', 'submitted', 'reviewed', 'finalized')),
    submitted_at              TIMESTAMP     NULL,
    reviewed_at               TIMESTAMP     NULL,
    finalized_at              TIMESTAMP     NULL,
    created_at                TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT performance_evaluations_pkey          PRIMARY KEY (evaluation_id),
    CONSTRAINT performance_evaluations_employee_fk   FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    CONSTRAINT performance_evaluations_evaluator_fk  FOREIGN KEY (evaluator_id)
        REFERENCES employees (employee_id),
    CONSTRAINT performance_evaluations_period_check  CHECK (evaluation_period_end >= evaluation_period_start)
);

-- ============================================================
-- TABLE 16 : performance_scores
-- Individual metric scores contributing to a performance evaluation.
-- ============================================================
CREATE TABLE performance_scores (
    score_id       UUID          NOT NULL DEFAULT gen_random_uuid(),
    evaluation_id  UUID          NOT NULL,
    metric_id      UUID          NOT NULL,
    score          DECIMAL(5,2)  NOT NULL CHECK (score  BETWEEN 0 AND 100),
    weight         DECIMAL(5,2)  NULL     CHECK (weight BETWEEN 0 AND 100),
    weighted_score DECIMAL(5,2)  GENERATED ALWAYS AS (
                       ROUND(score * weight / 100.0, 2)
                   ) STORED,
    evidence       TEXT          NULL,
    comments       TEXT          NULL,
    created_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT performance_scores_pkey            PRIMARY KEY (score_id),
    CONSTRAINT performance_scores_eval_metric_uq  UNIQUE (evaluation_id, metric_id),
    CONSTRAINT performance_scores_evaluation_fk   FOREIGN KEY (evaluation_id)
        REFERENCES performance_evaluations (evaluation_id) ON DELETE CASCADE,
    CONSTRAINT performance_scores_metric_fk       FOREIGN KEY (metric_id)
        REFERENCES performance_metrics (metric_id)
);

-- ============================================================
-- TABLE 17 : job_postings
-- Job vacancy advertisements published for internal and
-- external recruitment.
-- ============================================================
CREATE TABLE job_postings (
    job_id               UUID           NOT NULL DEFAULT gen_random_uuid(),
    position_id          UUID           NULL,
    department_id        UUID           NULL,
    title                VARCHAR(200)   NOT NULL,
    description          TEXT           NOT NULL,
    requirements         TEXT           NULL,
    responsibilities     TEXT           NULL,
    employment_type      VARCHAR(50)    NULL
                             CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'intern')),
    experience_level     VARCHAR(50)    NULL
                             CHECK (experience_level IN ('entry', 'mid', 'senior', 'executive')),
    experience_years_min INTEGER        NULL CHECK (experience_years_min >= 0),
    experience_years_max INTEGER        NULL CHECK (experience_years_max >= 0),
    salary_range_min     DECIMAL(12,2)  NULL,
    salary_range_max     DECIMAL(12,2)  NULL,
    location             VARCHAR(100)   NULL,
    remote_allowed       BOOLEAN        NOT NULL DEFAULT FALSE,
    number_of_positions  INTEGER        NOT NULL DEFAULT 1 CHECK (number_of_positions > 0),
    status               VARCHAR(50)    NOT NULL DEFAULT 'draft'
                             CHECK (status IN ('draft', 'published', 'closed', 'filled')),
    published_at         TIMESTAMP      NULL,
    closing_date         DATE           NULL,
    posted_by            UUID           NULL,
    created_at           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT job_postings_pkey            PRIMARY KEY (job_id),
    CONSTRAINT job_postings_position_fk     FOREIGN KEY (position_id)
        REFERENCES positions (position_id),
    CONSTRAINT job_postings_department_fk   FOREIGN KEY (department_id)
        REFERENCES departments (department_id),
    CONSTRAINT job_postings_posted_by_fk    FOREIGN KEY (posted_by)
        REFERENCES users (user_id),
    CONSTRAINT job_postings_exp_years_check CHECK (
        experience_years_max IS NULL OR experience_years_min IS NULL
        OR experience_years_max >= experience_years_min
    ),
    CONSTRAINT job_postings_salary_check    CHECK (
        salary_range_max IS NULL OR salary_range_min IS NULL
        OR salary_range_max >= salary_range_min
    )
);

-- ============================================================
-- TABLE 18 : candidates
-- Job applicant records with AI screening scores for each vacancy.
-- ============================================================
CREATE TABLE candidates (
    candidate_id           UUID           NOT NULL DEFAULT gen_random_uuid(),
    job_id                 UUID           NOT NULL,
    first_name             VARCHAR(100)   NOT NULL,
    last_name              VARCHAR(100)   NOT NULL,
    email                  VARCHAR(255)   NOT NULL,
    phone                  VARCHAR(20)    NULL,
    address                TEXT           NULL,
    city                   VARCHAR(100)   NULL,
    country                VARCHAR(100)   NULL,
    resume_url             TEXT           NULL,
    cover_letter           TEXT           NULL,
    linkedin_url           VARCHAR(255)   NULL,
    portfolio_url          VARCHAR(255)   NULL,
    current_company        VARCHAR(200)   NULL,
    current_position       VARCHAR(200)   NULL,
    total_experience_years DECIMAL(4,1)   NULL CHECK (total_experience_years >= 0),
    expected_salary        DECIMAL(12,2)  NULL,
    application_status     VARCHAR(50)    NOT NULL DEFAULT 'applied'
                               CHECK (application_status IN
                                   ('applied', 'screening', 'ai_interview', 'offered', 'rejected')),
    ai_screening_score     DECIMAL(5,2)   NULL CHECK (ai_screening_score  BETWEEN 0 AND 100),
    ai_screening_summary   TEXT           NULL,
    ai_match_percentage    DECIMAL(5,2)   NULL CHECK (ai_match_percentage BETWEEN 0 AND 100),
    ai_screening_date      TIMESTAMP      NULL,
    source                 VARCHAR(50)    NULL,
    referrer_employee_id   UUID           NULL,
    applied_at             TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT candidates_pkey        PRIMARY KEY (candidate_id),
    CONSTRAINT candidates_job_fk      FOREIGN KEY (job_id)
        REFERENCES job_postings (job_id),
    CONSTRAINT candidates_referrer_fk FOREIGN KEY (referrer_employee_id)
        REFERENCES employees (employee_id)
);

-- ============================================================
-- TABLE 19 : ai_interviews
-- AI-conducted preliminary interview results stored per
-- candidate per vacancy.
-- ============================================================
CREATE TABLE ai_interviews (
    interview_id          UUID          NOT NULL DEFAULT gen_random_uuid(),
    candidate_id          UUID          NOT NULL,
    job_id                UUID          NOT NULL,
    scheduled_at          TIMESTAMP     NULL,
    started_at            TIMESTAMP     NULL,
    completed_at          TIMESTAMP     NULL,
    duration_minutes      INTEGER       NULL CHECK (duration_minutes >= 0),
    overall_score         DECIMAL(5,2)  NULL CHECK (overall_score         BETWEEN 0 AND 100),
    technical_score       DECIMAL(5,2)  NULL CHECK (technical_score       BETWEEN 0 AND 100),
    communication_score   DECIMAL(5,2)  NULL CHECK (communication_score   BETWEEN 0 AND 100),
    cultural_fit_score    DECIMAL(5,2)  NULL CHECK (cultural_fit_score    BETWEEN 0 AND 100),
    problem_solving_score DECIMAL(5,2)  NULL CHECK (problem_solving_score BETWEEN 0 AND 100),
    ai_summary            TEXT          NULL,
    ai_strengths          TEXT          NULL,
    ai_weaknesses         TEXT          NULL,
    ai_recommendation     VARCHAR(50)   NULL
                              CHECK (ai_recommendation IN ('strong_hire', 'hire', 'maybe', 'no_hire')),
    transcript_reference  VARCHAR(255)  NULL,
    status                VARCHAR(50)   NOT NULL DEFAULT 'scheduled'
                              CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    created_at            TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ai_interviews_pkey         PRIMARY KEY (interview_id),
    CONSTRAINT ai_interviews_candidate_fk FOREIGN KEY (candidate_id)
        REFERENCES candidates (candidate_id) ON DELETE CASCADE,
    CONSTRAINT ai_interviews_job_fk       FOREIGN KEY (job_id)
        REFERENCES job_postings (job_id)
);

-- ============================================================
-- TABLE 20 : notifications
-- In-app and email alerts sent to users for leave, payroll,
-- and system events.
-- ============================================================
CREATE TABLE notifications (
    notification_id     UUID          NOT NULL DEFAULT gen_random_uuid(),
    user_id             UUID          NOT NULL,
    notification_type   VARCHAR(50)   NOT NULL
                            CHECK (notification_type IN (
                                'leave_approval', 'leave_rejection', 'payroll',
                                'performance', 'attendance_alert', 'system',
                                'recruitment', 'policy_update'
                            )),
    title               VARCHAR(200)  NOT NULL,
    message             TEXT          NOT NULL,
    priority            VARCHAR(20)   NOT NULL DEFAULT 'normal'
                            CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    related_entity_type VARCHAR(50)   NULL,
    related_entity_id   UUID          NULL,
    action_url          VARCHAR(500)  NULL,
    action_label        VARCHAR(100)  NULL,
    is_read             BOOLEAN       NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMP     NULL,
    delivery_method     TEXT[]        NOT NULL DEFAULT '{in_app}',
    email_sent          BOOLEAN       NOT NULL DEFAULT FALSE,
    email_sent_at       TIMESTAMP     NULL,
    created_at          TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP     NULL,

    CONSTRAINT notifications_pkey    PRIMARY KEY (notification_id),
    CONSTRAINT notifications_user_fk FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 21 : audit_logs
-- Immutable audit trail of all data changes and user actions
-- for compliance.
-- ============================================================
CREATE TABLE audit_logs (
    log_id          UUID          NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID          NULL,
    action          VARCHAR(100)  NOT NULL,
    entity_type     VARCHAR(100)  NOT NULL,
    entity_id       UUID          NULL,
    old_values      JSONB         NULL,
    new_values      JSONB         NULL,
    changes_summary TEXT          NULL,
    ip_address      INET          NULL,
    user_agent      TEXT          NULL,
    session_id      UUID          NULL,
    request_id      VARCHAR(100)  NULL,
    success         BOOLEAN       NOT NULL DEFAULT TRUE,
    error_message   TEXT          NULL,
    timestamp       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT audit_logs_pkey    PRIMARY KEY (log_id),
    CONSTRAINT audit_logs_user_fk FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- users
CREATE INDEX idx_users_role                      ON users (role);

-- sessions
CREATE INDEX idx_sessions_user_id                ON sessions (user_id);
CREATE INDEX idx_sessions_expires_at             ON sessions (expires_at);

-- departments
CREATE INDEX idx_departments_manager_id          ON departments (manager_id);
CREATE INDEX idx_departments_parent_dept_id      ON departments (parent_department_id);

-- positions
CREATE INDEX idx_positions_department_id         ON positions (department_id);

-- employees
CREATE INDEX idx_employees_user_id               ON employees (user_id);
CREATE INDEX idx_employees_department_id         ON employees (department_id);
CREATE INDEX idx_employees_position_id           ON employees (position_id);
CREATE INDEX idx_employees_manager_id            ON employees (manager_id);
CREATE INDEX idx_employees_employment_status     ON employees (employment_status);

-- face_embeddings
CREATE INDEX idx_face_embeddings_employee_id     ON face_embeddings (employee_id);

-- attendance_records
CREATE INDEX idx_attendance_records_employee_id  ON attendance_records (employee_id);
CREATE INDEX idx_attendance_records_date         ON attendance_records (date);

-- overtime_records
CREATE INDEX idx_overtime_records_employee_id    ON overtime_records (employee_id);
CREATE INDEX idx_overtime_records_date           ON overtime_records (date);

-- leave_balances
CREATE INDEX idx_leave_balances_employee_id      ON leave_balances (employee_id);
CREATE INDEX idx_leave_balances_year             ON leave_balances (year);

-- leave_applications
CREATE INDEX idx_leave_applications_employee_id  ON leave_applications (employee_id);
CREATE INDEX idx_leave_applications_status       ON leave_applications (status);

-- payroll_runs
CREATE INDEX idx_payroll_runs_status             ON payroll_runs (status);
CREATE INDEX idx_payroll_runs_period             ON payroll_runs (period_start, period_end);

-- payroll_records
CREATE INDEX idx_payroll_records_payroll_run_id  ON payroll_records (payroll_run_id);
CREATE INDEX idx_payroll_records_employee_id     ON payroll_records (employee_id);

-- performance_evaluations
CREATE INDEX idx_perf_evals_employee_id          ON performance_evaluations (employee_id);
CREATE INDEX idx_perf_evals_evaluator_id         ON performance_evaluations (evaluator_id);
CREATE INDEX idx_perf_evals_status               ON performance_evaluations (status);

-- performance_scores
CREATE INDEX idx_performance_scores_evaluation_id ON performance_scores (evaluation_id);
CREATE INDEX idx_performance_scores_metric_id     ON performance_scores (metric_id);

-- job_postings
CREATE INDEX idx_job_postings_status             ON job_postings (status);
CREATE INDEX idx_job_postings_department_id      ON job_postings (department_id);

-- candidates
CREATE INDEX idx_candidates_job_id               ON candidates (job_id);
CREATE INDEX idx_candidates_application_status   ON candidates (application_status);
CREATE INDEX idx_candidates_email                ON candidates (email);

-- ai_interviews
CREATE INDEX idx_ai_interviews_candidate_id      ON ai_interviews (candidate_id);
CREATE INDEX idx_ai_interviews_job_id            ON ai_interviews (job_id);

-- notifications
CREATE INDEX idx_notifications_user_id           ON notifications (user_id);
CREATE INDEX idx_notifications_is_read           ON notifications (is_read);
CREATE INDEX idx_notifications_type              ON notifications (notification_type);

-- audit_logs
CREATE INDEX idx_audit_logs_user_id              ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_entity               ON audit_logs (entity_type, entity_id);
CREATE INDEX idx_audit_logs_timestamp            ON audit_logs (timestamp DESC);

-- ============================================================
-- AUTO-UPDATE updated_at TRIGGER FUNCTION
-- ============================================================
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_departments_updated_at
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_attendance_records_updated_at
    BEFORE UPDATE ON attendance_records
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_leave_applications_updated_at
    BEFORE UPDATE ON leave_applications
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_performance_evaluations_updated_at
    BEFORE UPDATE ON performance_evaluations
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_job_postings_updated_at
    BEFORE UPDATE ON job_postings
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_candidates_updated_at
    BEFORE UPDATE ON candidates
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- ============================================================
-- TABLE COMMENTS
-- ============================================================
COMMENT ON TABLE users                   IS 'Stores authentication credentials and roles for all system users.';
COMMENT ON TABLE sessions                IS 'Manages active JWT session tokens for authenticated users.';
COMMENT ON TABLE departments             IS 'Organisational departments within the company.';
COMMENT ON TABLE positions               IS 'Job positions and salary bands within departments.';
COMMENT ON TABLE employees               IS 'Core employee master data including personal details, employment info, and salary.';
COMMENT ON TABLE face_embeddings         IS 'Encrypted facial recognition vectors used for attendance biometric verification.';
COMMENT ON TABLE attendance_records      IS 'Daily attendance events recorded via face recognition, RFID, or manual entry.';
COMMENT ON TABLE overtime_records        IS 'Overtime hours logged against attendance records, with approval workflow.';
COMMENT ON TABLE leave_types             IS 'Master list of leave categories with entitlement rules.';
COMMENT ON TABLE leave_balances          IS 'Per-employee annual leave entitlement balances, updated automatically on approval.';
COMMENT ON TABLE leave_applications      IS 'Employee leave requests with AI-powered approval decisions and human override.';
COMMENT ON TABLE payroll_runs            IS 'Payroll batch run header — one record per pay period.';
COMMENT ON TABLE payroll_records         IS 'Individual payslip data per employee per payroll run with auto-computed totals.';
COMMENT ON TABLE performance_metrics     IS 'Weighted KPI definitions used in performance evaluations.';
COMMENT ON TABLE performance_evaluations IS 'Periodic performance review records with AI-generated insights and grade.';
COMMENT ON TABLE performance_scores      IS 'Individual metric scores contributing to a performance evaluation.';
COMMENT ON TABLE job_postings            IS 'Job vacancy advertisements published for internal and external recruitment.';
COMMENT ON TABLE candidates              IS 'Job applicant records with AI screening scores for each vacancy.';
COMMENT ON TABLE ai_interviews           IS 'AI-conducted preliminary interview results stored per candidate per vacancy.';
COMMENT ON TABLE notifications           IS 'In-app and email alerts sent to users for leave, payroll, and system events.';
COMMENT ON TABLE audit_logs              IS 'Immutable audit trail of all data changes and user actions for compliance.';
