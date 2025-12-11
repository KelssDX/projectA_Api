#!/usr/bin/env python3
"""
Development runner with auto-reload for Flet application.
This script will automatically restart the app when Python files change.
"""

import flet as ft
import os
import sys
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FletReloadHandler(FileSystemEventHandler):
    def __init__(self, app_process):
        self.app_process = app_process
        self.last_restart = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only restart on Python file changes
        if event.src_path.endswith('.py'):
            current_time = time.time()
            # Prevent multiple restarts in quick succession
            if current_time - self.last_restart < 2:
                return
                
            self.last_restart = current_time
            print(f"\n🔄 File changed: {event.src_path}")
            print("🔄 Restarting Flet application...")
            
            # Kill the current app process
            if self.app_process and self.app_process.poll() is None:
                self.app_process.terminate()
                self.app_process.wait()
            
            # Start the app again
            start_flet_app()

def start_flet_app():
    """Start the Flet application"""
    try:
        # Import and run the main function
        from main import main
        
        print("🚀 Starting Flet application with auto-reload...")
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP,
            assets_dir="assets" if os.path.exists("assets") else None,
        )
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

def main():
    """Main development runner"""
    print("🔧 Development mode with auto-reload enabled")
    print("📁 Watching for changes in Python files...")
    print("🛑 Press Ctrl+C to stop")
    
    # Start the app initially
    app_process = subprocess.Popen([sys.executable, "-c", """
import flet as ft
from main import main
ft.app(target=main, view=ft.AppView.FLET_APP)
"""])
    
    # Set up file watcher
    event_handler = FletReloadHandler(app_process)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
        observer.stop()
        if app_process and app_process.poll() is None:
            app_process.terminate()
            app_process.wait()
    
    observer.join()

if __name__ == "__main__":
    main()
