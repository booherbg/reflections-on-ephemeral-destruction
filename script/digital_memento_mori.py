import sqlite3
import os
import time
import random
import hashlib
import json
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import numpy as np
from PIL import Image, ImageDraw
import shutil
from pathlib import Path
import threading
import signal
import sys

class DatabaseWatcher(FileSystemEventHandler):
    def __init__(self, db_path, output_dir, expiration_date):
        self.db_path = db_path
        self.output_dir = output_dir
        self.expiration_date = expiration_date
        self.last_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        self.operation_count = 0
        self.last_visualization = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the event log
        self.event_log = os.path.join(output_dir, "event_log.json")
        if not os.path.exists(self.event_log):
            with open(self.event_log, "w") as f:
                json.dump({"events": []}, f)
    
    def on_modified(self, event):
        if event.src_path == self.db_path:
            current_size = os.path.getsize(self.db_path)
            if current_size != self.last_size:
                self.operation_count += 1
                self.last_size = current_size
                self.log_event("database_modified", current_size)
                
                # Random chance to generate visualization
                if random.random() < 0.1:  # 10% chance
                    self.create_visualization()
    
    def log_event(self, event_type, size):
        try:
            with open(self.event_log, "r") as f:
                log = json.load(f)
        except:
            log = {"events": []}
            
        log["events"].append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "size": size,
            "operation_count": self.operation_count
        })
        
        with open(self.event_log, "w") as f:
            json.dump(log, f, indent=2)
    
    def create_visualization(self):
        """Create a visual representation of the database state"""
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Create image
            img_size = 1000
            img = Image.new('RGB', (img_size, img_size), color='black')
            draw = ImageDraw.Draw(img)
            
            # Calculate visualization parameters
            center_x = img_size // 2
            center_y = img_size // 2
            max_radius = min(center_x, center_y) - 50
            
            # Draw circular representation of database
            angle_per_table = 360 / len(tables)
            for i, (table_name,) in enumerate(tables):
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Calculate segment parameters
                start_angle = i * angle_per_table
                end_angle = (i + 1) * angle_per_table
                radius = max_radius * (0.3 + (0.7 * (row_count / 1000)))  # Scale based on row count
                
                # Draw segment
                draw.arc([center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius],
                        start_angle, end_angle,
                        fill=self.get_color(table_name, row_count))
            
            # Save visualization
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_path = os.path.join(self.output_dir, f"db_viz_{timestamp}.png")
            img.save(viz_path)
            
            self.last_visualization = viz_path
            self.log_event("visualization_created", os.path.getsize(viz_path))
            
            conn.close()
            
        except Exception as e:
            self.log_event("visualization_error", str(e))
    
    def get_color(self, table_name, row_count):
        """Generate a color based on table name and row count"""
        color_hash = hashlib.md5(table_name.encode()).hexdigest()
        r = int(color_hash[:2], 16)
        g = int(color_hash[2:4], 16)
        b = int(color_hash[4:6], 16)
        
        # Adjust brightness based on row count
        factor = 0.5 + min(row_count / 1000, 0.5)
        return (int(r * factor), int(g * factor), int(b * factor))
    
    def check_expiration(self):
        """Check if the script should self-destruct"""
        if datetime.now() > self.expiration_date:
            self.self_destruct()
            return True
        return False
    
    def self_destruct(self):
        """Remove all traces of the script and its outputs"""
        try:
            # Log final event
            self.log_event("self_destruct_initiated", 0)
            
            # Remove output directory
            shutil.rmtree(self.output_dir)
            
            # Remove this script
            script_path = os.path.abspath(__file__)
            os.remove(script_path)
            
        except Exception as e:
            # If we can't remove everything, at least try to corrupt the files
            with open(script_path, 'w') as f:
                f.write('# This script has expired')
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    with open(os.path.join(self.output_dir, file), 'w') as f:
                        f.write('# Expired')

def main():
    # Set expiration date (30 days from now)
    expiration_date = datetime.now() + timedelta(days=30)
    
    # Initialize watcher
    db_path = "samples.db"  # Path to your database
    output_dir = "justice/script/memento"
    watcher = DatabaseWatcher(db_path, output_dir, expiration_date)
    
    # Set up file system observer
    observer = Observer()
    observer.schedule(watcher, path=os.path.dirname(db_path), recursive=False)
    observer.start()
    
    try:
        while True:
            if watcher.check_expiration():
                break
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main() 