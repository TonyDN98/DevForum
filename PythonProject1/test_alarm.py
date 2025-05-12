#!/usr/bin/env python3
"""
Test Alarm Script

This script simulates process alarms by updating the STATUS_PROCESS table in the database.
It can be used to test the process_monitor.py script without having to manually update the database.
"""

import sys
import mysql.connector
from configparser import ConfigParser

def load_config(config_file='config.ini'):
    """Load configuration from config file."""
    config = ConfigParser()
    config.read(config_file)
    return config

def connect_to_database(config):
    """Connect to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=config['DATABASE']['host'],
            database=config['DATABASE']['database'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password']
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None

def list_processes(connection):
    """List all processes in the database."""
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT sp.process_id, p.process_name, sp.alarma, sp.notes
        FROM STATUS_PROCESS sp
        JOIN PROCESE p ON sp.process_id = p.process_id
        ORDER BY sp.process_id
        """
        cursor.execute(query)
        processes = cursor.fetchall()
        cursor.close()
        
        print("\nCurrent processes in database:")
        print("-" * 70)
        print(f"{'ID':<5} {'Process Name':<20} {'Alarm':<10} {'Notes':<30}")
        print("-" * 70)
        
        for process in processes:
            alarm_status = "YES" if process['alarma'] == 1 else "NO"
            print(f"{process['process_id']:<5} {process['process_name']:<20} {alarm_status:<10} {process['notes']:<30}")
        
        print("-" * 70)
        return processes
    except mysql.connector.Error as err:
        print(f"Error querying database: {err}")
        return []

def set_alarm(connection, process_id, alarm_value):
    """Set the alarm status for a process."""
    try:
        cursor = connection.cursor()
        query = "UPDATE STATUS_PROCESS SET alarma = %s WHERE process_id = %s"
        cursor.execute(query, (alarm_value, process_id))
        connection.commit()
        cursor.close()
        
        status = "ON" if alarm_value == 1 else "OFF"
        print(f"Alarm for process ID {process_id} set to {status}")
        return True
    except mysql.connector.Error as err:
        print(f"Error updating alarm status: {err}")
        return False

def print_usage():
    """Print usage information."""
    print("\nUsage:")
    print("  python test_alarm.py list                  - List all processes")
    print("  python test_alarm.py on <process_id>       - Set alarm ON for process")
    print("  python test_alarm.py off <process_id>      - Set alarm OFF for process")
    print("  python test_alarm.py test                  - Set sample alarms for testing")
    print("  python test_alarm.py help                  - Show this help message")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    config = load_config()
    connection = connect_to_database(config)
    
    if not connection:
        print("Failed to connect to database. Check your configuration.")
        return
    
    try:
        if command == "list":
            list_processes(connection)
        
        elif command == "on" and len(sys.argv) == 3:
            process_id = int(sys.argv[2])
            set_alarm(connection, process_id, 1)
            list_processes(connection)
        
        elif command == "off" and len(sys.argv) == 3:
            process_id = int(sys.argv[2])
            set_alarm(connection, process_id, 0)
            list_processes(connection)
        
        elif command == "test":
            # Set some sample alarms for testing
            print("Setting sample alarms for testing...")
            set_alarm(connection, 1, 1)  # Set Apache to alarm
            set_alarm(connection, 3, 1)  # Set SSH to alarm
            set_alarm(connection, 2, 0)  # Clear MySQL alarm
            list_processes(connection)
        
        elif command == "help":
            print_usage()
        
        else:
            print("Invalid command or missing arguments.")
            print_usage()
    
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()