# Quick Start Guide - Process Monitor

Get the Process Monitor system up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- Windows operating system
- Internet connection (for initial package installation)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Django Backend

```bash
python start_backend.py
```

This will:
- Install missing packages automatically
- Set up the database
- Start the server at http://localhost:8000

**Keep this terminal open!**

## Step 3: Build the Agent EXE

Open a **new terminal** and run:

```bash
python build_agent.py
```

This will create:
- `ProcessMonitorAgent.exe` - The main agent executable
- `run_agent.bat` - Easy execution script

## Step 4: Run the Agent

Double-click either:
- `ProcessMonitorAgent.exe` (direct execution)
- `run_agent.bat` (with instructions)

The agent will start collecting process data and sending it to the backend.

## Step 5: View the Interface

Open your browser and go to:
**http://localhost:8000**

You should see the Process Monitor interface with real-time data!

## Troubleshooting

### Backend won't start?
- Check if port 8000 is available
- Try running `python backend/manage.py runserver` manually

### Agent won't connect?
- Make sure the backend is running
- Check the API key in `agent/config.py`
- Verify the backend URL in the config

### No data displayed?
- Ensure the agent is running
- Check the browser console for errors
- Verify the backend API endpoints

## Next Steps

- Customize the agent configuration in `agent/config.py`
- Modify the frontend in `backend/static/`
- Add authentication and security features
- Deploy to production servers

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure the backend is running before starting the agent
4. Check the log files for detailed error information

Happy monitoring! 🚀 