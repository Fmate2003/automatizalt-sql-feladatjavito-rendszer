-- Run ONCE by an administrator in the disposable sql_grader_demo database.
-- Demo credentials only; never reuse in any other environment.
CREATE ROLE sql_student NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE sql_runner LOGIN PASSWORD 'local_runner_demo_only'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT sql_student TO sql_runner;
REVOKE ALL ON DATABASE sql_grader_demo FROM PUBLIC;
GRANT CONNECT, CREATE ON DATABASE sql_grader_demo TO sql_runner;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
