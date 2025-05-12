# Process Monitor and Restart Tool

A Python application that monitors processes on a Linux system by querying a MySQL database for processes in alarm state and automatically restarts them when necessary.

## Overview

This tool is designed for Linux systems without internet access. It periodically checks a MySQL database for processes that are in an alarm state, retrieves their names, and attempts to restart them using various methods. After a successful restart, it updates the alarm status in the database.

## Features

- Monitors processes in alarm state from a MySQL database
- Automatically restarts processes using multiple methods (systemctl, service, or direct kill and restart)
- Configurable monitoring interval and restart attempts
- Comprehensive logging of all actions and errors
- Works on Linux systems without internet access
- Minimal dependencies

## Requirements

- Python 3.6 or higher
- MySQL database
- mysql-connector-python package

## Database Schema

The application expects the following database tables:

### STATUS_PROCESS Table
- `process_id`: Identifier for the process
- `alarma`: Alarm status (1 = in alarm, 0 = normal)

### PROCESE Table
- `process_id`: Identifier for the process (matches STATUS_PROCESS.process_id)
- `process_name`: Name of the process or service to restart

## Installation

1. Copy the `process_monitor.py` script, `config.ini` file, and `setup_database.sql` to your Linux system
2. Make the script executable:
   ```
   chmod +x process_monitor.py
   ```
3. Install the required Python package:
   ```
   pip install mysql-connector-python
   ```
4. Set up the database schema:
   ```
   mysql -u root -p < setup_database.sql
   ```
   This will create the necessary database, tables, and sample data for testing.

## Configuration

Edit the `config.ini` file to match your environment:

```ini
[DATABASE]
host = localhost
database = process_monitor
user = root
password = password

[MONITOR]
interval = 300
max_restart_attempts = 3
```

- `host`: MySQL server hostname or IP address
- `database`: Name of the database containing the required tables
- `user`: MySQL username
- `password`: MySQL password
- `interval`: Time in seconds between checks for processes in alarm state
- `max_restart_attempts`: Maximum number of restart attempts for each process

## Usage

### Running the Monitor

Start the process monitor:

```
./process_monitor.py
```

For production use, you might want to run it as a service or using a tool like `screen` or `tmux` to keep it running in the background.

### Testing with Simulated Alarms

The repository includes a test script (`test_alarm.py`) that can be used to simulate process alarms by updating the database:

```
# List all processes and their current alarm status
python test_alarm.py list

# Set alarm ON for a specific process (e.g., process_id = 1)
python test_alarm.py on 1

# Set alarm OFF for a specific process (e.g., process_id = 1)
python test_alarm.py off 1

# Set sample alarms for testing (Apache and SSH to ON, MySQL to OFF)
python test_alarm.py test

# Show usage information
python test_alarm.py help
```

This script is useful for testing the process monitor without having to manually update the database.

### Running as a Systemd Service

1. Create a systemd service file:

```
sudo nano /etc/systemd/system/process-monitor.service
```

2. Add the following content:

```
[Unit]
Description=Process Monitor and Restart Tool
After=network.target mysql.service

[Service]
ExecStart=/path/to/process_monitor.py
WorkingDirectory=/path/to/directory
Restart=always
User=your_user
Group=your_group

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```
sudo systemctl enable process-monitor.service
sudo systemctl start process-monitor.service
```

## Logging

The application logs all activities to both the console and a file named `process_monitor.log` in the same directory as the script. The log includes information about:

- Processes found in alarm state
- Restart attempts and their results
- Database connection issues
- Any errors encountered

## Troubleshooting

### Database Connection Issues

If the application cannot connect to the database, it will log an error and retry after 60 seconds. Check:
- Database server is running
- Credentials in config.ini are correct
- Network connectivity to the database server

### Process Restart Failures

If a process cannot be restarted, the application will try different methods and make multiple attempts. If all attempts fail, it will log an error. Check:
- The process name in the PROCESE table is correct
- The user running the script has sufficient permissions to restart the process
- The process or service exists on the system

## License

This project is licensed under the MIT License - see the LICENSE file for details.
