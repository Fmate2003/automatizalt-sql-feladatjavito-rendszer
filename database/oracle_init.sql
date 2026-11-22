-- DBA: run once in a DEDICATED teaching PDB. Replace the placeholder password.
-- Change USERS here and oracle_tablespace in the config if needed.
CREATE USER SQLGRADER_ADMIN IDENTIFIED BY "REPLACE_WITH_UNIQUE_PASSWORD"
    DEFAULT TABLESPACE USERS;
GRANT CREATE USER, DROP USER TO SQLGRADER_ADMIN;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO SQLGRADER_ADMIN WITH ADMIN OPTION;
-- Do not grant DBA, SYSDBA or access to existing class/business data.
