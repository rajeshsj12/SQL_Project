@echo off
REM Change to MySQL bin directory
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

REM Run the restore command
mysql -u root -p customersdb < "D:\customersdb_backup.sql"

pause
