# Process Monitor API Documentation

Complete API reference for the Process Monitor system.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses simple API key authentication for agent communication.

**Header**: `Content-Type: application/json`

**API Key**: Included in request body for agent endpoints

## Endpoints

### 1. Submit Process Data (Agent)

**POST** `/processes/`

Submit process monitoring data from the agent.

**Request Body:**
```json
{
    "hostname": "DESKTOP-ABC123",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "api_key": "your-secret-api-key-here",
    "processes": [
        {
            "pid": 1234,
            "name": "chrome.exe",
            "cpu_percent": 15.2,
            "memory_mb": 256.5,
            "parent_pid": 1000,
            "command_line": "chrome.exe --new-window",
            "status": "running",
            "create_time": 1705312200
        }
    ]
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Processed 45 processes",
    "snapshot_id": 123
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid data format
- `401` - Invalid API key
- `500` - Server error

### 2. Get Process Data (Frontend)

**GET** `/processes/get/`

Retrieve the latest process data for all hosts.

**Response:**
```json
{
    "message": "Success",
    "data": [
        {
            "id": 123,
            "timestamp": "2024-01-15T10:30:00.000Z",
            "total_processes": 45,
            "total_cpu_percent": 125.6,
            "total_memory_mb": 2048.3,
            "hostname": "DESKTOP-ABC123",
            "processes": [
                {
                    "id": 456,
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 15.2,
                    "memory_mb": 256.5,
                    "parent_pid": 1000,
                    "command_line": "chrome.exe --new-window",
                    "status": "running",
                    "create_time": 1705312200,
                    "children": [],
                    "has_children": false
                }
            ]
        }
    ],
    "total_hosts": 1
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

### 3. Get Hosts List

**GET** `/hosts/`

Get a list of all monitored hosts.

**Response:**
```json
{
    "message": "Success",
    "data": [
        {
            "id": 1,
            "hostname": "DESKTOP-ABC123",
            "ip_address": "192.168.1.100",
            "first_seen": "2024-01-15T09:00:00.000Z",
            "last_seen": "2024-01-15T10:30:00.000Z",
            "is_active": true,
            "latest_snapshot": {
                "id": 123,
                "timestamp": "2024-01-15T10:30:00.000Z",
                "total_processes": 45,
                "total_cpu_percent": 125.6,
                "total_memory_mb": 2048.3,
                "hostname": "DESKTOP-ABC123",
                "processes": []
            },
            "process_count": 45
        }
    ],
    "total_hosts": 1
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

### 4. Get Host-Specific Processes

**GET** `/hosts/{hostname}/processes/`

Get process data for a specific host.

**Parameters:**
- `hostname` (string) - The hostname to query

**Response:**
```json
{
    "message": "Success",
    "data": {
        "id": 123,
        "timestamp": "2024-01-15T10:30:00.000Z",
        "total_processes": 45,
        "total_cpu_percent": 125.6,
        "total_memory_mb": 2048.3,
        "hostname": "DESKTOP-ABC123",
        "processes": [
            {
                "id": 456,
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 15.2,
                "memory_mb": 256.5,
                "parent_pid": 1000,
                "command_line": "chrome.exe --new-window",
                "status": "running",
                "create_time": 1705312200,
                "children": [],
                "has_children": false
            }
        ]
    }
}
```

**Status Codes:**
- `200` - Success
- `404` - Host not found
- `500` - Server error

### 5. Clear Old Data

**DELETE** `/clear-old-data/`

Remove old process snapshots (older than 24 hours).

**Response:**
```json
{
    "message": "Cleared 15 old snapshots",
    "deleted_count": 15
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

## Data Models

### Process

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `pid` | integer | Process ID |
| `name` | string | Process name |
| `cpu_percent` | float | CPU usage percentage |
| `memory_mb` | float | Memory usage in MB |
| `parent_pid` | integer/null | Parent process ID |
| `command_line` | string | Command line arguments |
| `status` | string | Process status |
| `create_time` | integer/null | Process creation timestamp |
| `children` | array | Child processes |
| `has_children` | boolean | Whether process has children |

### ProcessSnapshot

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `timestamp` | datetime | Snapshot timestamp |
| `total_processes` | integer | Total process count |
| `total_cpu_percent` | float | Total CPU usage |
| `total_memory_mb` | float | Total memory usage |
| `hostname` | string | Host identifier |
| `processes` | array | List of processes |

### Host

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `hostname` | string | Hostname |
| `ip_address` | string/null | IP address |
| `first_seen` | datetime | First detection time |
| `last_seen` | datetime | Last detection time |
| `is_active` | boolean | Active status |
| `latest_snapshot` | object/null | Latest snapshot data |
| `process_count` | integer | Process count in latest snapshot |

## Error Handling

### Error Response Format

```json
{
    "error": "Error message description",
    "details": {
        "field_name": ["Specific error details"]
    }
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations

1. **API Key**: Change the default API key in production
2. **HTTPS**: Use HTTPS in production environments
3. **Input Validation**: All inputs are validated and sanitized
4. **CORS**: CORS is enabled for development; restrict in production

## Example Usage

### Python Client

```python
import requests
import json

# Submit process data
data = {
    "hostname": "my-computer",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "api_key": "your-api-key",
    "processes": [...]
}

response = requests.post(
    "http://localhost:8000/api/processes/",
    json=data
)

if response.status_code == 200:
    print("Data submitted successfully")
else:
    print(f"Error: {response.json()}")
```

### JavaScript Client

```javascript
// Get process data
fetch('/api/processes/get/')
    .then(response => response.json())
    .then(data => {
        console.log('Process data:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

### cURL Examples

```bash
# Submit process data
curl -X POST http://localhost:8000/api/processes/ \
  -H "Content-Type: application/json" \
  -d '{"hostname":"test","timestamp":"2024-01-15T10:30:00.000Z","api_key":"key","processes":[]}'

# Get process data
curl http://localhost:8000/api/processes/get/

# Get hosts
curl http://localhost:8000/api/hosts/

# Clear old data
curl -X DELETE http://localhost:8000/api/clear-old-data/
```

## Versioning

Current API version: v1

No versioning scheme is currently implemented. Consider adding versioning for future updates.

## Support

For API support or questions:
1. Check the console logs for detailed error information
2. Verify the API endpoint URLs
3. Ensure proper authentication
4. Check the database connection and migrations 