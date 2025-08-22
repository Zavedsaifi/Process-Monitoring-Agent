"""
Process Monitoring Agent
Collects system process information and sends it to the Django backend.
"""

import psutil
import socket
import json
import time
import logging
import requests
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class ProcessMonitorAgent:
    """Main agent class for monitoring system processes."""
    
    def __init__(self):
        """Initialize the process monitoring agent."""
        self.setup_logging()
        # Use custom hostname "Zaved PC" instead of system hostname
        self.hostname = "Zaved PC"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Content-Type': 'application/json'
        })
        
        self.logger.info(f"Process Monitor Agent started on {self.hostname}")
        self.logger.info(f"Backend URL: {config.BACKEND_URL}")
        
        # Display initial system information
        if getattr(config, 'DISPLAY_SYSTEM_INFO', True):
            self.display_system_info()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def collect_process_data(self) -> List[Dict[str, Any]]:
        """Collect information about all running processes."""
        processes = []
        total_checked = 0
        skipped_low_usage = 0
        
        try:
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 
                                           'ppid', 'cmdline', 'status', 'create_time']):
                total_checked += 1
                try:
                    proc_info = proc.info
                    
                    # Collect ALL processes without filtering
                    # Skip processes that don't meet thresholds (only skip if both are very low)
                    # if (proc_info['cpu_percent'] < 0.01 and 
                    #     proc_info['memory_info'].rss / (1024 * 1024) < 0.1):
                    #     skipped_low_usage += 1
                    #     continue
                    
                    # Calculate memory usage in MB
                    memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                    
                    process_data = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'] or 'Unknown',
                        'cpu_percent': round(proc_info['cpu_percent'], 2),
                        'memory_mb': round(memory_mb, 2),
                        'parent_pid': proc_info['ppid'] if proc_info['ppid'] != 0 else None,
                        'status': proc_info['status'],
                        'create_time': proc_info['create_time']
                    }
                    
                    # Add command line if enabled and available
                    if config.ENABLE_COMMAND_LINE_COLLECTION and proc_info['cmdline']:
                        process_data['command_line'] = ' '.join(proc_info['cmdline'])
                    else:
                        process_data['command_line'] = ''
                    
                    processes.append(process_data)
                    
                    # Log some process details for debugging
                    if len(processes) <= 10:  # Log first 10 processes
                        self.logger.info(f"Added process: {proc_info['name']} (PID: {proc_info['pid']}) - "
                                       f"CPU: {proc_info['cpu_percent']}%, Memory: {memory_mb:.2f} MB")
                    elif len(processes) % 50 == 0:  # Log every 50th process
                        self.logger.info(f"Added process #{len(processes)}: {proc_info['name']} (PID: {proc_info['pid']})")
                    
                    # Limit the number of processes if configured
                    if len(processes) >= config.MAX_PROCESSES_PER_SNAPSHOT:
                        self.logger.warning(f"Reached maximum process limit ({config.MAX_PROCESSES_PER_SNAPSHOT})")
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    if config.CONTINUE_ON_ERROR:
                        self.logger.debug(f"Could not collect info for process: {e}")
                        continue
                    else:
                        raise
                        
        except Exception as e:
            self.logger.error(f"Error collecting process data: {e}")
            if not config.CONTINUE_ON_ERROR:
                raise
                
        self.logger.info(f"Process collection summary: Checked {total_checked} processes, "
                        f"Skipped {skipped_low_usage} low-usage processes, "
                        f"Collected {len(processes)} processes")
        return processes
        
    def build_process_hierarchy(self, processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build parent-child relationships between processes."""
        if not config.ENABLE_PROCESS_HIERARCHY:
            return processes
            
        # Create a map of PID to process
        process_map = {proc['pid']: proc for proc in processes}
        
        # Mark processes that have children
        for proc in processes:
            proc['has_children'] = any(
                p['parent_pid'] == proc['pid'] for p in processes
            )
            
        # Return root processes (those without parents or with parent PID 0)
        root_processes = [
            proc for proc in processes 
            if proc['parent_pid'] is None or proc['parent_pid'] == 0
        ]
        
        return root_processes
        
    def send_data_to_backend(self, processes: List[Dict[str, Any]]) -> bool:
        """Send collected process data to the backend API."""
        payload = {
            'hostname': self.hostname,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'processes': processes,
            'api_key': config.API_KEY
        }
        
        for attempt in range(config.MAX_RETRIES):
            try:
                self.logger.info(f"Sending data to backend (attempt {attempt + 1}/{config.MAX_RETRIES})")
                
                response = self.session.post(
                    config.BACKEND_URL,
                    json=payload,
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.logger.info(f"Data sent successfully: {result.get('message', 'OK')}")
                    return True
                else:
                    self.logger.warning(f"Backend returned status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                
            # Wait before retrying
            if attempt < config.MAX_RETRIES - 1:
                self.logger.info(f"Waiting {config.RETRY_DELAY} seconds before retry...")
                time.sleep(config.RETRY_DELAY)
                
        self.logger.error("Failed to send data to backend after all retry attempts")
        return False
        
    def run_single_collection(self) -> bool:
        """Run a single collection cycle."""
        try:
            self.logger.info("Starting process data collection...")
            
            # Collect process data
            processes = self.collect_process_data()
            
            if not processes:
                self.logger.warning("No processes collected")
                return False
                
            # Build process hierarchy
            if config.ENABLE_PROCESS_HIERARCHY:
                processes = self.build_process_hierarchy(processes)
                self.logger.info(f"After hierarchy building: {len(processes)} processes remain")
            else:
                self.logger.info(f"Process hierarchy disabled, keeping all {len(processes)} processes")
                
            # Send data to backend
            success = self.send_data_to_backend(processes)
            
            if success:
                self.logger.info("Collection cycle completed successfully")
            else:
                self.logger.error("Collection cycle failed")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error in collection cycle: {e}")
            return False
            
    def run_continuous(self):
        """Run the agent continuously, collecting data at regular intervals."""
        self.logger.info(f"Starting continuous monitoring with {config.COLLECTION_INTERVAL}s intervals")
        
        try:
            while True:
                start_time = time.time()
                
                # Run collection cycle
                self.run_single_collection()
                
                # Display system info periodically
                self.display_system_info_periodic()
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, config.COLLECTION_INTERVAL - elapsed)
                
                if sleep_time > 0:
                    self.logger.info(f"Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error in continuous mode: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Cleanup resources before shutdown."""
        self.logger.info("Cleaning up...")
        self.session.close()
        self.logger.info("Agent shutdown complete")
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')  # Windows C: drive
            
            return {
                'cpu_percent': cpu_percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_percent': memory.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 2)
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def display_system_info(self):
        """Display system information in a formatted way."""
        try:
            system_info = self.get_system_info()
            platform_info = platform.platform()
            cpu_info = platform.processor()
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            print("\n" + "="*60)
            print(f"🖥️  SYSTEM INFORMATION - {self.hostname}")
            print("="*60)
            print(f"📋 Name: {self.hostname}")
            print(f"💻 Operating System: {platform_info}")
            print(f"🔧 Processor: {cpu_info}")
            print(f"⚡ Number of Cores: {cpu_count}")
            print(f"🧵 Number of Threads: {cpu_count_logical}")
            print(f"💾 RAM (GB): {system_info.get('memory_total_gb', 0)}")
            print(f"📊 Used RAM (GB): {round(system_info.get('memory_total_gb', 0) - system_info.get('memory_available_gb', 0), 2)}")
            print(f"🆓 Available RAM (GB): {system_info.get('memory_available_gb', 0)}")
            print(f"💿 Storage Free (GB): {system_info.get('disk_free_gb', 0)}")
            print(f"💾 Storage Total (GB): {system_info.get('disk_total_gb', 0)}")
            print(f"📈 Storage Used (GB): {round(system_info.get('disk_total_gb', 0) - system_info.get('disk_free_gb', 0), 2)}")
            print("="*60 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error displaying system info: {e}")
    
    def display_system_info_periodic(self):
        """Display system information periodically."""
        if getattr(config, 'DISPLAY_SYSTEM_INFO', True):
            self.display_system_info()


def main():
    """Main entry point for the agent."""
    agent = ProcessMonitorAgent()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single collection
        success = agent.run_single_collection()
        sys.exit(0 if success else 1)
    else:
        # Run continuously
        agent.run_continuous()


if __name__ == "__main__":
    main() 