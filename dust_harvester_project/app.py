from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import os
import threading
import time
from datetime import datetime
from src.main import run
from src.config import settings

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Global state for harvester
harvester_running = False
harvester_thread = None
last_run_time = None
candidates_found = 0
transactions_sent = 0

def run_harvester_async():
    """Run the harvester in a separate thread"""
    global harvester_running, last_run_time, candidates_found, transactions_sent
    
    harvester_running = True
    last_run_time = datetime.now()
    
    try:
        # Run the async harvester
        result = asyncio.run(run())
        if result:
            global transactions_sent
            transactions_sent += result
        harvester_running = False
    except Exception as e:
        print(f"Harvester error: {e}")
        harvester_running = False

@app.route('/')
def index():
    """Main dashboard page"""
    global harvester_running, last_run_time, candidates_found, transactions_sent
    
    # Check if candidates.txt exists and count lines
    candidates_count = 0
    if os.path.exists('candidates.txt'):
        try:
            with open('candidates.txt', 'r') as f:
                candidates_count = len(f.readlines())
        except:
            candidates_count = 0
    
    return render_template('index.html', 
                         harvester_running=harvester_running,
                         last_run_time=last_run_time,
                         candidates_found=candidates_count,
                         transactions_sent=transactions_sent,
                         dry_run=settings.DRY_RUN,
                         settings=settings)

@app.route('/config')
def config():
    """Configuration page"""
    return render_template('config.html', settings=settings)

@app.route('/start_harvester', methods=['POST'])
def start_harvester():
    """Start the harvester"""
    global harvester_running, harvester_thread
    
    if not harvester_running:
        harvester_thread = threading.Thread(target=run_harvester_async)
        harvester_thread.daemon = True
        harvester_thread.start()
        return jsonify({'status': 'started'})
    else:
        return jsonify({'status': 'already_running'})

@app.route('/stop_harvester', methods=['POST'])
def stop_harvester():
    """Stop the harvester"""
    global harvester_running
    harvester_running = False
    return jsonify({'status': 'stopped'})

@app.route('/status')
def status():
    """Get harvester status"""
    global harvester_running, last_run_time, candidates_found, transactions_sent
    
    # Check candidates count
    candidates_count = 0
    if os.path.exists('candidates.txt'):
        try:
            with open('candidates.txt', 'r') as f:
                candidates_count = len(f.readlines())
        except:
            candidates_count = 0
    
    return jsonify({
        'running': harvester_running,
        'last_run': last_run_time.isoformat() if last_run_time else None,
        'candidates_found': candidates_count,
        'transactions_sent': transactions_sent,
        'dry_run': settings.DRY_RUN
    })

@app.route('/candidates')
def candidates():
    """Get current candidates"""
    candidates_list = []
    if os.path.exists('candidates.txt'):
        try:
            with open('candidates.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        candidates_list.append({
                            'pair': parts[0],
                            'token': parts[1],
                            'surplus': parts[2]
                        })
        except:
            pass
    
    return jsonify({'candidates': candidates_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
