import os
import subprocess
import sys
import time

# Add Scripts to PATH for this session
scripts_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts")
os.environ["PATH"] += os.pathsep + scripts_path

print("🚀 Starting Flet with Hot Reload...")
print(f"📂 Project: {os.getcwd()}")

# Kill any existing flet processes to prevent conflicts
if sys.platform == "win32":
    try:
        subprocess.run(["taskkill", "/f", "/im", "flet.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "windowtitle eq Flet*"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# Run flet command
try:
    # Use --recursive to watch subdirectories
    cmd = ["flet", "run", "main.py", "--web", "--port", "8552", "--recursive"]
    print(f"▶️  Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
except FileNotFoundError:
    print("❌ 'flet' command not found. Trying python -m flet...")
    subprocess.run([sys.executable, "-m", "flet", "run", "main.py", "--web", "--port", "8552", "--recursive"])
except KeyboardInterrupt:
    print("\n👋 Stopped.")
except Exception as e:
    print(f"\n❌ Error: {e}")
