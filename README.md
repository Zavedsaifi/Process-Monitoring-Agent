# Process Monitoring Agent with Django Backend

A comprehensive system for monitoring running processes on Windows machines with a web-based interface.

## Architecture Overview

The system consists of three main components:

1. **Agent (EXE)**: A standalone executable that collects process information and sends it to the backend
2. **Django Backend**: REST API server that receives and stores process data
3. **Frontend**: Web interface displaying process hierarchy with interactive features

## Features

- Real-time process monitoring
- Process hierarchy visualization (parent-child relationships)
- CPU and memory usage tracking
- Hostname identification
- Interactive tree-like display
- Expandable/collapsible subprocesses
- Responsive web interface

## Project Structure

```
procmon/
├── agent/                 # Process monitoring agent
│   ├── process_monitor.py
│   └── config.py
├── backend/               # Django backend
│   ├── manage.py
│   ├── procmon/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── static/
│       ├── css/
│       └── js/
├── frontend/              # HTML/JS frontend
│   ├── index.html
│   ├── css/
│   └── js/
├── requirements.txt
├── build_agent.py         # Script to build EXE
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Django Backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 3. Build Agent EXE

```bash
python build_agent.py
```

This will create `agent.exe` in the `dist/` folder.

### 4. Configure and Run Agent

1. Double-click `agent.exe` to run
2. The agent will automatically collect process data and send it to the backend
3. Data will appear in the web interface

### 5. Access Frontend

Open `http://localhost:8000` in your browser to view the process monitoring interface.

## API Specifications

### Endpoints

- `POST /api/processes/` - Receive process data from agent
- `GET /api/processes/` - Retrieve process data for frontend
- `GET /api/hosts/` - Get list of monitored hosts

### Authentication

Simple API key authentication is implemented for agent communication.

## Configuration

The agent can be configured by modifying `agent/config.py`:
- Backend endpoint URL
- API key
- Collection interval
- Data retention settings

## Assumptions

- Windows operating system (for process monitoring)
- Python 3.8+ installed
- Network connectivity between agent and backend
- Administrative privileges may be required for some process information

## Troubleshooting

1. **Agent won't start**: Check if Python and required packages are installed
2. **Backend connection failed**: Verify Django server is running and endpoint is correct
3. **No data displayed**: Ensure agent is running and sending data successfully

## Development

To modify the system:
1. Edit Django models in `backend/api/models.py`
2. Update API views in `backend/api/views.py`
3. Modify frontend in `frontend/` directory
4. Update agent logic in `agent/process_monitor.py`

## License

This project is provided as-is for educational and development purposes. 