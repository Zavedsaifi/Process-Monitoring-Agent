"""
Configuration settings for the Process Monitoring Agent.
"""

# Backend API configuration
BACKEND_URL = "http://localhost:8000/api/processes/"
API_KEY = "zaved-secret-key-2024"

# System Information Display
DISPLAY_SYSTEM_INFO = True
SYSTEM_INFO_INTERVAL = 10  # seconds between system info display

# Data collection settings
COLLECTION_INTERVAL = 30  # seconds between collections
MAX_RETRIES = 3  # maximum retry attempts for failed API calls
RETRY_DELAY = 5  # seconds to wait between retries

# Process filtering
INCLUDE_SYSTEM_PROCESSES = True
MIN_CPU_THRESHOLD = 0.1  # minimum CPU usage to include process
MIN_MEMORY_THRESHOLD = 1.0  # minimum memory usage in MB to include process

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "agent.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Network configuration
REQUEST_TIMEOUT = 30  # seconds
USER_AGENT = "ProcessMonitorAgent/1.0"

# Data retention
MAX_PROCESSES_PER_SNAPSHOT = 1000  # maximum processes to collect per snapshot
ENABLE_PROCESS_HIERARCHY = True  # collect parent-child relationships

# Performance settings
ENABLE_CPU_MONITORING = True
ENABLE_MEMORY_MONITORING = True
ENABLE_COMMAND_LINE_COLLECTION = False  # may contain sensitive information
ENABLE_PROCESS_STATUS = True

# Error handling
CONTINUE_ON_ERROR = True  # continue running even if some processes fail to collect
LOG_ERRORS_TO_FILE = True
MAX_ERROR_LOG_SIZE = 1024 * 1024  # 1MB 