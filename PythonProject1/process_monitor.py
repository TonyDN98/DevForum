#!/usr/bin/env python3
"""
Process Monitor and Restart Tool

This script monitors processes by querying a MySQL database for processes in alarm state
and restarts them when necessary. It's designed to work on Linux systems without internet access.
"""

import os
import sys
import time
import logging
import subprocess
import mysql.connector
from datetime import datetime
from configparser import ConfigParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("process_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_file='config.ini'):
    """Load configuration from config file."""
    if not os.path.exists(config_file):
        logger.error(f"Configuration file {config_file} not found.")
        create_default_config(config_file)
        logger.info(f"Created default configuration file at {config_file}")
        
    config = ConfigParser()
    config.read(config_file)
    return config

def create_default_config(config_file):
    """Create a default configuration file."""
    config = ConfigParser()
    config['DATABASE'] = {
        'host': 'localhost',
        'database': 'process_monitor',
        'user': 'root',
        'password': 'password'
    }
    config['MONITOR'] = {
        'interval': '300',  # 5 minutes
        'max_restart_attempts': '3'
    }
    
    with open(config_file, 'w') as f:
        config.write(f)

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
        logger.error(f"Database connection failed: {err}")
        return None

def get_processes_in_alarm(connection):
    """Query the STATUS_PROCESS table to find processes in alarm state."""
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT process_id, alarma FROM STATUS_PROCESS WHERE alarma = 1"
        cursor.execute(query)
        processes = cursor.fetchall()
        cursor.close()
        return processes
    except mysql.connector.Error as err:
        logger.error(f"Error querying STATUS_PROCESS table: {err}")
        return []

def get_process_name(connection, process_id):
    """Query the PROCESE table to get the process name for a given process_id."""
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT process_name FROM PROCESE WHERE process_id = %s"
        cursor.execute(query, (process_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return result['process_name']
        else:
            logger.warning(f"No process name found for process_id {process_id}")
            return None
    except mysql.connector.Error as err:
        logger.error(f"Error querying PROCESE table: {err}")
        return None

def restart_process(process_name, max_attempts=3):
    """Restart a process using systemctl or service command."""
    logger.info(f"Attempting to restart process: {process_name}")
    
    # Try different methods to restart the process
    methods = [
        # systemctl method
        lambda: subprocess.run(['systemctl', 'restart', process_name], 
                              check=True, capture_output=True, text=True),
        # service method
        lambda: subprocess.run(['service', process_name, 'restart'], 
                              check=True, capture_output=True, text=True),
        # direct kill and start (if it's a regular process, not a service)
        lambda: restart_by_kill(process_name)
    ]
    
    for attempt in range(max_attempts):
        for method_index, method in enumerate(methods):
            try:
                result = method()
                logger.info(f"Successfully restarted {process_name} using method {method_index+1}")
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"Method {method_index+1} failed to restart {process_name}: {e.stderr}")
            except Exception as e:
                logger.warning(f"Error with method {method_index+1} for {process_name}: {str(e)}")
        
        logger.warning(f"Attempt {attempt+1}/{max_attempts} to restart {process_name} failed. Retrying...")
        time.sleep(2)  # Wait before retrying
    
    logger.error(f"Failed to restart {process_name} after {max_attempts} attempts")
    return False

def restart_by_kill(process_name):
    """Restart a process by killing it and starting it again."""
    # Find process PID
    ps_result = subprocess.run(['pgrep', '-f', process_name], 
                              capture_output=True, text=True)
    
    if ps_result.returncode != 0:
        raise Exception(f"Process {process_name} not found")
    
    pid = ps_result.stdout.strip()
    if not pid:
        raise Exception(f"No PID found for {process_name}")
    
    # Kill the process
    kill_result = subprocess.run(['kill', '-9', pid], 
                                check=True, capture_output=True, text=True)
    
    # Start the process again
    # Note: This is a simplified approach and might not work for all processes
    # In a real environment, you would need to know how to properly start each process
    start_result = subprocess.run([process_name], 
                                 check=True, capture_output=True, text=True)
    
    return True

def update_alarm_status(connection, process_id):
    """Update the alarm status in the STATUS_PROCESS table after restart."""
    try:
        cursor = connection.cursor()
        query = "UPDATE STATUS_PROCESS SET alarma = 0 WHERE process_id = %s"
        cursor.execute(query, (process_id,))
        connection.commit()
        cursor.close()
        logger.info(f"Updated alarm status for process_id {process_id}")
        return True
    except mysql.connector.Error as err:
        logger.error(f"Error updating alarm status: {err}")
        return False

def main():
    """Main function to monitor and restart processes."""
    logger.info("Starting Process Monitor")
    
    config = load_config()
    interval = int(config['MONITOR']['interval'])
    max_restart_attempts = int(config['MONITOR']['max_restart_attempts'])
    
    while True:
        connection = connect_to_database(config)
        if not connection:
            logger.error("Failed to connect to database. Retrying in 60 seconds...")
            time.sleep(60)
            continue
        
        try:
            # Get processes in alarm state
            alarm_processes = get_processes_in_alarm(connection)
            logger.info(f"Found {len(alarm_processes)} processes in alarm state")
            
            # Process each alarm
            for process in alarm_processes:
                process_id = process['process_id']
                process_name = get_process_name(connection, process_id)
                
                if process_name:
                    logger.info(f"Process {process_id} ({process_name}) is in alarm state")
                    
                    # Attempt to restart the process
                    if restart_process(process_name, max_restart_attempts):
                        # Update alarm status in database
                        update_alarm_status(connection, process_id)
                    else:
                        logger.error(f"Failed to restart process {process_name}")
                else:
                    logger.warning(f"Could not find name for process_id {process_id}")
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        finally:
            if connection:
                connection.close()
        
        logger.info(f"Sleeping for {interval} seconds before next check")
        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process Monitor stopped by user")
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        sys.exit(1)