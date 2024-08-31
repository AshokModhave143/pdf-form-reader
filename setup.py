import os
import subprocess
import sys
import platform
import signal

# Global variable to store the Flask process
flask_process = None

def create_and_activate_venv(venv_dir="venv"):
    """Create and activate a virtual environment."""
    try:
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        print(f"Virtual environment created at {venv_dir}.")
        
        # Activate the virtual environment
        activate_script = os.path.join(venv_dir, "Scripts", "activate") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "activate")
        
        if platform.system() == "Windows":
            print(f"Activating virtual environment... (on Windows)")
            activate_command = f"{venv_dir}\\Scripts\\activate"
            subprocess.call(activate_command, shell=True)
        else:
            print(f"Activating virtual environment... (on Unix/Mac)")
            activate_command = f"source {activate_script}"
            subprocess.call(activate_command, shell=True)
        
        print("Virtual environment activated.")
        
    except subprocess.CalledProcessError:
        print("Failed to create or activate the virtual environment.")
        sys.exit(1)

def install_dependencies():
    """Install dependencies from requirements.txt."""
    try:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies.")
        sys.exit(1)

def set_env_variables():
    """Set environment variables."""
    try:
        print("Setting environment variables...")
        os.environ["FLASK_APP"] = "project/web/app.py"  # Set this to your Flask app entry point
        os.environ["FLASK_ENV"] = "development"  # Set environment to development or production
        print("Environment variables set successfully.")
    except Exception as e:
        print(f"Failed to set environment variables: {e}")
        sys.exit(1)

def run_flask_app():
    """Run the Flask application."""
    global flask_process
    try:
        print("Running Flask application...")
        
        if platform.system() == "Windows":
            flask_process = subprocess.Popen([sys.executable, "-m", "flask", "run"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            flask_process = subprocess.Popen([sys.executable, "-m", "flask", "run"], preexec_fn=os.setsid)
        
        flask_process.wait()
        
    except subprocess.CalledProcessError:
        print("Failed to run Flask application.")
        sys.exit(1)

def stop_flask_app(signal_received, frame):
    """Gracefully stop the Flask application."""
    global flask_process
    if flask_process:
        print("Stopping Flask application...")
        
        if platform.system() == "Windows":
            flask_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)
        
        flask_process.wait()
        print("Flask application stopped gracefully.")
        sys.exit(0)
    else:
        print("No Flask application running.")
        sys.exit(1)


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, stop_flask_app)
    signal.signal(signal.SIGTERM, stop_flask_app)

    create_and_activate_venv()
    install_dependencies()
    set_env_variables()
    run_flask_app()
