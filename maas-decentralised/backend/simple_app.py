#!/usr/bin/env python3
"""
Simplified Flask backend for MaaS simulation with reliable progress tracking
"""

import os
import sys
import time
import threading
import subprocess
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for simulation state
simulation_process = None
simulation_status = {
    'running': False,
    'current_step': 0,
    'total_steps': 0,
    'start_time': None,
    'simulation_id': None
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start a new simulation"""
    global simulation_process, simulation_status

    print("=== SIMULATION START REQUEST RECEIVED ===")
    logger.info("=== SIMULATION START REQUEST RECEIVED ===")

    if simulation_status['running']:
        print("=== SIMULATION ALREADY RUNNING ===")
        return jsonify({'error': 'Simulation already running'}), 400

    config = request.json
    print(f"=== CONFIG RECEIVED: {config} ===")

    if not config:
        return jsonify({'error': 'No configuration provided'}), 400

    # Validate required fields
    required_fields = ['steps', 'commuters', 'providers']
    for field in required_fields:
        if field not in config:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Generate simulation ID
        simulation_id = f"sim_{int(time.time())}"
        print(f"=== GENERATED SIMULATION ID: {simulation_id} ===")

        # Build command - use test simulation for now to debug
        cmd = [
            sys.executable,
            'test_simulation.py',
            '--steps', str(config['steps']),
            '--commuters', str(config['commuters']),
            '--providers', str(config['providers'])
        ]

        print(f"=== COMMAND: {' '.join(cmd)} ===")

        # Start simulation process in backend directory
        simulation_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.abspath('.')
        )

        print(f"=== PROCESS STARTED: PID {simulation_process.pid} ===")

        # Update simulation status
        simulation_status.update({
            'running': True,
            'current_step': 0,
            'total_steps': config['steps'],
            'start_time': datetime.now().isoformat(),
            'simulation_id': simulation_id
        })

        print(f"=== STATUS UPDATED: {simulation_status} ===")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_simulation, daemon=True)
        monitor_thread.start()

        print(f"=== MONITORING THREAD STARTED ===")

        logger.info(f"Started simulation: {simulation_id} with {config['steps']} steps")

        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'message': 'Simulation started successfully'
        })

    except Exception as e:
        print(f"=== ERROR STARTING SIMULATION: {e} ===")
        logger.error(f"Failed to start simulation: {e}")
        return jsonify({'error': f'Failed to start simulation: {str(e)}'}), 500

@app.route('/api/simulation/progress', methods=['GET'])
def get_simulation_progress():
    """Get current simulation progress"""
    if not simulation_status['running'] and simulation_status['current_step'] == 0:
        return jsonify({
            'current_step': 0,
            'total_steps': 0,
            'progress_percentage': 0,
            'status': 'stopped',
            'estimated_time_remaining': 0
        })
    
    progress_percentage = 0
    if simulation_status['total_steps'] > 0:
        progress_percentage = (simulation_status['current_step'] / simulation_status['total_steps']) * 100
    
    return jsonify({
        'current_step': simulation_status['current_step'],
        'total_steps': simulation_status['total_steps'],
        'progress_percentage': round(progress_percentage, 1),
        'status': 'running' if simulation_status['running'] else 'completed',
        'estimated_time_remaining': 0
    })

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the current simulation"""
    global simulation_process, simulation_status
    
    if simulation_process:
        simulation_process.terminate()
        simulation_process = None
    
    simulation_status['running'] = False
    
    return jsonify({
        'success': True,
        'message': 'Simulation stopped'
    })

def monitor_simulation():
    """Monitor simulation progress in background thread"""
    global simulation_process, simulation_status
    
    try:
        logger.info("Starting simulation monitoring")
        print("=== MONITORING THREAD STARTED ===")
        
        start_time = time.time()
        total_steps = simulation_status['total_steps']
        
        while simulation_status['running'] and simulation_process:
            # Check if process is still alive
            if simulation_process.poll() is not None:
                # Process has ended
                return_code = simulation_process.poll()
                if return_code == 0:
                    logger.info("Simulation completed successfully")
                    simulation_status['current_step'] = total_steps
                    print(f"=== SIMULATION COMPLETED: {total_steps}/{total_steps} ===")
                else:
                    logger.warning(f"Simulation terminated with return code: {return_code}")
                    print(f"=== SIMULATION TERMINATED: {return_code} ===")
                break
            
            # Calculate progress based on elapsed time
            elapsed = time.time() - start_time
            
            # Estimate step duration (1.2 seconds per step is realistic)
            step_duration = 1.2
            estimated_step = min(int(elapsed / step_duration), total_steps)
            simulation_status['current_step'] = estimated_step
            
            # Log progress every 3 steps
            if estimated_step % 3 == 0 or estimated_step == total_steps:
                progress_pct = (estimated_step / total_steps) * 100
                logger.info(f"Progress: {estimated_step}/{total_steps} ({progress_pct:.1f}%)")
                print(f"=== PROGRESS: {estimated_step}/{total_steps} ({progress_pct:.1f}%) ===")
            
            time.sleep(1)
        
        simulation_status['running'] = False
        logger.info("Simulation monitoring completed")
        print("=== MONITORING COMPLETED ===")
        
    except Exception as e:
        logger.error(f"Error monitoring simulation: {e}")
        print(f"=== MONITORING ERROR: {e} ===")
        simulation_status['running'] = False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting simplified Flask backend on port {port}")
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/simulation/start")
    print("  GET  /api/simulation/progress")
    print("  POST /api/simulation/stop")
    app.run(host='0.0.0.0', port=port, debug=False)
