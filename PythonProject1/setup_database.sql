-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS process_monitor;

-- Use the database
USE process_monitor;

-- Create the STATUS_PROCESS table
CREATE TABLE IF NOT EXISTS STATUS_PROCESS (
    process_id INT PRIMARY KEY,
    alarma TINYINT NOT NULL DEFAULT 0,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes VARCHAR(255)
);

-- Create the PROCESE table
CREATE TABLE IF NOT EXISTS PROCESE (
    process_id INT PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES STATUS_PROCESS(process_id)
);

-- Insert sample data for testing
-- Sample processes that might exist on a Linux system
INSERT INTO STATUS_PROCESS (process_id, alarma, notes) VALUES
(1, 0, 'Apache web server'),
(2, 1, 'MySQL database server'),
(3, 0, 'SSH server'),
(4, 1, 'Nginx web server'),
(5, 0, 'Cron service');

INSERT INTO PROCESE (process_id, process_name, description) VALUES
(1, 'apache2', 'Apache HTTP Server'),
(2, 'mysqld', 'MySQL Database Server'),
(3, 'sshd', 'OpenSSH Server'),
(4, 'nginx', 'Nginx Web Server'),
(5, 'cron', 'Cron Job Scheduler');

-- Add an index for faster queries
CREATE INDEX idx_alarma ON STATUS_PROCESS(alarma);

-- Show the created tables
SHOW TABLES;

-- Display sample data
SELECT sp.process_id, sp.alarma, p.process_name 
FROM STATUS_PROCESS sp
JOIN PROCESE p ON sp.process_id = p.process_id
ORDER BY sp.process_id;

-- Display processes in alarm state (for testing)
SELECT sp.process_id, p.process_name, sp.notes
FROM STATUS_PROCESS sp
JOIN PROCESE p ON sp.process_id = p.process_id
WHERE sp.alarma = 1
ORDER BY sp.process_id;