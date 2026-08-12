-- Job Portal Database Schema
-- MySQL 8.x

CREATE DATABASE IF NOT EXISTS job_portal
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE job_portal;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
  id             INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  email          VARCHAR(255)      NOT NULL,
  hashed_password VARCHAR(255)     NOT NULL,
  role           ENUM('candidate','recruiter','admin') NOT NULL DEFAULT 'candidate',
  is_active      BOOLEAN           NOT NULL DEFAULT TRUE,
  created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  INDEX ix_users_role (role)
) ENGINE=InnoDB;

-- ============================================================
-- CANDIDATE PROFILES  (1-to-1 with users)
-- ============================================================
CREATE TABLE candidate_profiles (
  id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
  user_id     INT UNSIGNED   NOT NULL,
  full_name   VARCHAR(150)   NOT NULL,
  phone       VARCHAR(20)    DEFAULT NULL,
  resume_url  VARCHAR(500)   DEFAULT NULL,
  skills      TEXT           DEFAULT NULL,
  created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_candidate_profiles_user_id (user_id),
  CONSTRAINT fk_candidate_profiles_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- COMPANIES  (owned by a recruiter user)
-- ============================================================
CREATE TABLE companies (
  id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
  owner_id    INT UNSIGNED   NOT NULL,
  name        VARCHAR(200)   NOT NULL,
  description TEXT           DEFAULT NULL,
  website     VARCHAR(300)   DEFAULT NULL,
  logo_url    VARCHAR(500)   DEFAULT NULL,
  created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_companies_name (name),
  INDEX ix_companies_owner_id (owner_id),
  CONSTRAINT fk_companies_owner
    FOREIGN KEY (owner_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- JOBS  (posted by a company)
-- ============================================================
CREATE TABLE jobs (
  id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
  company_id  INT UNSIGNED   NOT NULL,
  title       VARCHAR(200)   NOT NULL,
  description TEXT           NOT NULL,
  location    VARCHAR(200)   DEFAULT NULL,
  salary_min  DECIMAL(10,2)  DEFAULT NULL,
  salary_max  DECIMAL(10,2)  DEFAULT NULL,
  job_type    ENUM('full_time','part_time','contract','internship') NOT NULL,
  is_active   BOOLEAN        NOT NULL DEFAULT TRUE,
  created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  INDEX ix_jobs_company_id (company_id),
  INDEX ix_jobs_is_active (is_active),
  CONSTRAINT fk_jobs_company
    FOREIGN KEY (company_id) REFERENCES companies(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- APPLICATIONS  (candidate applies to a job)
-- ============================================================
CREATE TABLE applications (
  id           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  candidate_id INT UNSIGNED  NOT NULL,
  job_id       INT UNSIGNED  NOT NULL,
  cover_letter TEXT          DEFAULT NULL,
  status       ENUM('pending','reviewed','shortlisted','rejected','accepted') NOT NULL DEFAULT 'pending',
  applied_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE KEY uq_applications_candidate_job (candidate_id, job_id),
  INDEX ix_applications_candidate_id (candidate_id),
  INDEX ix_applications_job_id (job_id),
  INDEX ix_applications_status (status),
  CONSTRAINT fk_applications_candidate
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_applications_job
    FOREIGN KEY (job_id) REFERENCES jobs(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
