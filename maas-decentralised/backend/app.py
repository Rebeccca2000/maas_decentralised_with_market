#!/usr/bin/env python3
"""
Flask backend server for MaaS Decentralized Platform
Bridges React frontend with Python simulation engine
"""

import os
import sys
import json
import threading
import subprocess
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import io
import contextlib

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from abm.utils.blockchain_interface import BlockchainInterface
# NOTE: Lazy-imported in run_real_simulation to allow setting a headless Matplotlib backend
# from abm.agents.run_decentralized_model import run_simulation as run_full_model

# Import database and blockchain export modules
from backend.database_api import register_database_routes
from backend.blockchain_export import register_blockchain_export_routes

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
current_simulation = None
simulation_process = None
simulation_status = {
    'running': False,
    'progress': 0,
    'current_step': 0,
    'total_steps': 0,
    'start_time': None,
    'estimated_completion': None
}

# Latest research results cache
latest_results = {
    'advanced_metrics': None,
    'plots_dir': None,
    'raw_log': '',
    'finished_at': None
}

# Blockchain interface
blockchain_interface = None

def init_blockchain():
    """Initialize blockchain connection"""
    global blockchain_interface
    try:
        blockchain_interface = BlockchainInterface()
        logger.info("Blockchain interface initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize blockchain: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    blockchain_connected = False
    if blockchain_interface:
        try:
            blockchain_connected = blockchain_interface.w3.is_connected()
        except:
            blockchain_connected = False

    return jsonify({
        'backend_connected': True,
        'blockchain_connected': blockchain_connected,
        'simulation_running': simulation_status['running']
    })

@app.route('/api/simulation/start', methods=['POST', 'GET'])
def start_simulation():
    """Start a new simulation"""
    global current_simulation, simulation_process, simulation_status

    print("=== SIMULATION START REQUEST RECEIVED ===")
    logger.info("=== SIMULATION START REQUEST RECEIVED ===")

    if simulation_status['running']:
        return jsonify({'error': 'Simulation already running'}), 400

    # Merge JSON and querystring for flexibility
    config = request.get_json(silent=True) or {}
    for k in ['steps', 'commuters', 'providers', 'no_plots', 'export_db', 'enable_proactive_segments']:
        if request.args.get(k) is not None:
            v = request.args.get(k)
            if k in ['steps','commuters','providers']:
                config[k] = int(v)
            else:
                config[k] = str(v).lower() in ('1','true','yes','on')

    # Validate configuration
    required_fields = ['steps', 'commuters', 'providers']
    for field in required_fields:
        if field not in config:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        steps = int(config['steps'])
        commuters = int(config['commuters'])
        providers = int(config['providers'])
        no_plots = bool(config.get('no_plots', False))
        export_db = bool(config.get('export_db', False))
        enable_proactive_segments = bool(config.get('enable_proactive_segments', True))

        # Update status
        simulation_status.update({
            'running': True,
            'progress': 0,
            'current_step': 0,
            'total_steps': steps,
            'start_time': datetime.now().isoformat()
        })

        current_simulation = {
            'id': f"sim_{int(time.time())}",
            'config': {
                'steps': steps, 'commuters': commuters, 'providers': providers,
                'no_plots': no_plots, 'export_db': export_db,
                'enable_proactive_segments': enable_proactive_segments
            },
            'start_time': simulation_status['start_time']
        }

        # Extract network configuration
        network = config.get('network', 'localhost')
        rpc_url = config.get('rpc_url', '')
        chain_id = config.get('chain_id', None)

        # Start real simulation in background thread and capture outputs
        sim_thread = threading.Thread(
            target=run_real_simulation,
            args=(steps, commuters, providers, no_plots, export_db, network, rpc_url, chain_id, enable_proactive_segments),
            daemon=True
        )
        sim_thread.start()
        # Start a naive progress ticker to update current_step while running
        ticker_thread = threading.Thread(target=_tick_progress, args=(steps,), daemon=True)
        ticker_thread.start()

        logger.info(f"Started simulation with config: {current_simulation['config']}")

        return jsonify({
            'success': True,
            'simulation_id': current_simulation['id'],
            'message': 'Simulation started successfully'
        })

    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the current simulation"""
    global simulation_process, simulation_status, current_simulation

    if not simulation_status['running']:
        # If simulation is not running, just return success (idempotent operation)
        return jsonify({
            'success': True,
            'message': 'No simulation was running'
        })

    try:
        if simulation_process:
            simulation_process.terminate()
            simulation_process.wait(timeout=10)

        simulation_status.update({
            'running': False,
            'progress': 0,
            'current_step': 0,
            'total_steps': 0
        })

        current_simulation = None

        logger.info("Simulation stopped")

        return jsonify({
            'success': True,
            'message': 'Simulation stopped successfully'
        })

    except Exception as e:
        logger.error(f"Failed to stop simulation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/status', methods=['GET'])
def get_simulation_status():
    """Get current simulation status"""
    return jsonify({
        'simulation': current_simulation,
        'status': simulation_status
    })

@app.route('/api/simulation/progress', methods=['GET'])
def get_simulation_progress():
    """Get detailed simulation progress"""
    total = simulation_status.get('total_steps', 0) or 0
    current = simulation_status.get('current_step', 0) or 0

    if simulation_status.get('running'):
        progress_percentage = int((current / total) * 100) if total > 0 else 0
        return jsonify({
            'current_step': current,
            'total_steps': total,
            'progress_percentage': progress_percentage,
            'estimated_time_remaining': 0,
            'status': 'running'
        })

    # Not running: if we have a finished run, report completed
    if latest_results.get('finished_at') and total > 0 and current >= total:
        return jsonify({
            'current_step': total,
            'total_steps': total,
            'progress_percentage': 100,
            'estimated_time_remaining': 0,
            'status': 'completed'
        })

    # Default stopped when nothing has run yet
    return jsonify({
        'current_step': 0,
        'total_steps': 0,
        'progress_percentage': 0,
        'estimated_time_remaining': 0,
        'status': 'stopped'
    })


def _tick_progress(total_steps, interval_sec=1):
    """Naive progress ticker to update current_step while simulation runs."""
    global simulation_status
    try:
        while simulation_status.get('running', False):
            # Let the completion handler set the final step exactly
            if simulation_status.get('current_step', 0) >= max(0, total_steps - 1):
                time.sleep(interval_sec)
                continue
            simulation_status['current_step'] = min(
                total_steps - 1,
                simulation_status.get('current_step', 0) + 1
            )
            time.sleep(interval_sec)
    except Exception:
        # Best-effort ticker; ignore errors
        pass



def run_real_simulation(total_steps, commuters, providers, no_plots=False, export_db=False, network='localhost', rpc_url='', chain_id=None, enable_proactive_segments=True):
    """Run the real ABM simulation and capture outputs for research."""
    global simulation_status, latest_results
    buf = io.StringIO()
    try:
        # Force headless Matplotlib to avoid Tkinter/Tcl issues in background thread
        try:
            os.environ['MPLBACKEND'] = 'Agg'
            import matplotlib
            matplotlib.use('Agg', force=True)
        except Exception:
            pass

        with contextlib.redirect_stdout(buf):
            # Lazy import after backend is set to Agg
            from abm.agents.run_decentralized_model import run_simulation as run_full_model
            model, advanced_metrics, plots_dir = run_full_model(
                steps=total_steps,
                num_commuters=commuters,
                num_providers=providers,
                no_plots=no_plots,
                export_db=export_db,
                network=network,
                rpc_url=rpc_url if rpc_url else None,
                chain_id=chain_id,
                enable_proactive_segments=enable_proactive_segments
            )
        latest_results.update({
            'advanced_metrics': advanced_metrics or {},
            'plots_dir': os.path.abspath(plots_dir) if plots_dir else None,
            'raw_log': buf.getvalue(),
            'finished_at': datetime.now().isoformat()
        })
    except Exception as e:
        latest_results.update({
            'advanced_metrics': None,
            'plots_dir': None,
            'raw_log': buf.getvalue() + f"\nERROR: {e}\n",
            'finished_at': datetime.now().isoformat()
        })
    finally:
        simulation_status['current_step'] = simulation_status.get('total_steps', total_steps)
        simulation_status['running'] = False



@app.route('/api/analytics/metrics', methods=['GET'])
def get_simulation_metrics():
    """Get simulation metrics and analytics."""
    adv = latest_results.get('advanced_metrics') if isinstance(latest_results, dict) else None
    if adv:
        try:
            total_requests = int(adv.get('total_requests', 0))
            total_matches = int(adv.get('total_matches', 0))
            match_rate = float(adv.get('match_rate', 0.0))

            # Calculate active requests (pending, not yet matched)
            # Note: total_matches can be > total_requests if requests are matched multiple times
            active_requests = max(0, total_requests - total_matches)

            # Total agents = commuters + providers (not requests + matches)
            # We'll use a better calculation based on provider and mode market share
            num_providers = len(adv.get('provider_market_share', {}))
            num_modes = len(adv.get('mode_market_share', {}))
            # Estimate: assume average 2 commuters per request
            estimated_commuters = max(10, total_requests // 2)
            total_agents = estimated_commuters + num_providers

            # Success rate should be 0-100%, not match_rate which can exceed 100%
            # Calculate as: (matches / requests) * 100, capped at 100%
            success_rate = min(100.0, match_rate)

            # Estimate avg response time from cost components if available
            avg_response_time = 0
            cost_components = adv.get('cost_components', [])
            if cost_components:
                # Extract time costs and convert to milliseconds
                time_costs = [c.get('time_cost', 0) for c in cost_components]
                if time_costs:
                    avg_time_hours = sum(time_costs) / len(time_costs) / 15  # Divide by value_of_time
                    avg_response_time = int(avg_time_hours * 3600 * 1000)  # Convert to ms

            kpis = {
                'total_agents': total_agents,
                'active_requests': active_requests,
                'completed_matches': total_matches,
                'blockchain_transactions': total_matches,
                'success_rate': round(success_rate, 2),
                'avg_response_time': avg_response_time
            }
            return jsonify({ **kpis, 'advanced': adv })
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            pass
    # Fallback placeholders
    return jsonify({
        'total_agents': 0,
        'active_requests': 0,
        'completed_matches': 0,
        'blockchain_transactions': 0,
        'success_rate': 0,
        'avg_response_time': 0
    })

@app.route('/api/results/log', methods=['GET'])
def get_results_log():
    """Return raw console output from the latest real simulation run."""
    return jsonify({
        'log': latest_results.get('raw_log', ''),
        'finished_at': latest_results.get('finished_at')
    })

@app.route('/api/files/results', methods=['GET'])
def list_results_files():
    """List generated plot files from the latest simulation."""
    plots_dir = latest_results.get('plots_dir')
    if not plots_dir or not os.path.isdir(plots_dir):
        return jsonify({'plots': [], 'dir': None})
    try:
        files = [f for f in os.listdir(plots_dir) if os.path.isfile(os.path.join(plots_dir, f))]
        return jsonify({'plots': files, 'dir': os.path.basename(plots_dir)})
    except Exception as e:
        return jsonify({'plots': [], 'dir': None, 'error': str(e)}), 500

@app.route('/api/files/download/<path:filename>', methods=['GET'])
def download_result_file(filename):
    plots_dir = latest_results.get('plots_dir')
    if not plots_dir or not os.path.isdir(plots_dir):
        return jsonify({'error': 'No results available'}), 404
    # Inline by default so images render in the UI; add ?download=1 to force download
    as_attachment = str(request.args.get('download', '0')).lower() in ('1','true','yes','on')
    return send_from_directory(plots_dir, filename, as_attachment=as_attachment)

@app.route('/api/analytics/transactions', methods=['GET'])
def get_transaction_history():
    """Get recent transaction history"""
    # TODO: Implement actual transaction history from blockchain
    sample_transactions = [
        {
            'type': 'registration',
            'description': 'New commuter registered',
            'details': 'Commuter ID: 123',
            'timestamp': datetime.now().isoformat()
        },
        {
            'type': 'request',
            'description': 'Travel request created',
            'details': 'From [1,1] to [10,10]',
            'timestamp': datetime.now().isoformat()
        },
        {
            'type': 'match',
            'description': 'Service matched',
            'details': 'Provider: BikeShare1, Price: 15 tokens',
            'timestamp': datetime.now().isoformat()
        }
    ]
    return jsonify(sample_transactions)

@app.route('/api/blockchain/status', methods=['GET'])
def get_blockchain_status():
    """Get detailed blockchain status"""
    if not blockchain_interface:
        return jsonify({'error': 'Blockchain not initialized'}), 500

    try:
        connected = blockchain_interface.w3.is_connected()
        if connected:
            latest_block = blockchain_interface.w3.eth.block_number
            network_id = blockchain_interface.w3.net.version
        else:
            latest_block = 0
            network_id = 'unknown'

        return jsonify({
            'connected': connected,
            'latest_block': latest_block,
            'network_id': network_id,
            'node_url': 'http://127.0.0.1:8545'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/contracts', methods=['GET'])
def get_contract_addresses():
    """Get deployed contract addresses"""
    try:
        with open('deployment-info.json', 'r') as f:
            contracts = json.load(f)
        return jsonify(contracts)
    except FileNotFoundError:
        return jsonify({'error': 'Contracts not deployed'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/transactions/recent', methods=['GET'])
def get_recent_transactions():
    """Get recent blockchain transactions"""
    try:
        # For now, return sample data since we don't have transaction monitoring yet
        sample_transactions = [
            {
                'hash': '0x1234567890abcdef',
                'type': 'Service Request',
                'status': 'confirmed',
                'timestamp': datetime.now().isoformat(),
                'value': '0.1 ETH'
            },
            {
                'hash': '0xabcdef1234567890',
                'type': 'Provider Registration',
                'status': 'confirmed',
                'timestamp': datetime.now().isoformat(),
                'value': '0.05 ETH'
            }
        ]
        return jsonify(sample_transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# BUNDLE API ENDPOINTS
# ============================================================================

@app.route('/api/bundles/stats', methods=['GET'])
def get_bundles_stats():
    """Get bundle statistics from database"""
    try:
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker

        # Use SQLite database
        import os
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'maas_bundles.db')
        DATABASE_URL = f"sqlite:///{sqlite_path}"

        # Import SQLite models
        from abm.database.models_sqlite import Bundle, BundleSegment, Reservation

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Total bundles
            total_bundles = session.query(func.count(Bundle.id)).scalar() or 0

            # Average segments per bundle
            avg_segments = session.query(func.avg(Bundle.num_segments)).scalar() or 0

            # Total discount savings
            total_savings = session.query(func.sum(Bundle.discount_amount)).scalar() or 0

            # Bundle type distribution (by number of segments)
            bundle_types = session.query(
                Bundle.num_segments,
                func.count(Bundle.id)
            ).group_by(Bundle.num_segments).all()

            # Bundle match rate (reserved bundles / total bundles)
            reserved_bundles = session.query(func.count(Reservation.id)).scalar() or 0
            bundle_match_rate = (reserved_bundles / total_bundles * 100) if total_bundles > 0 else 0

            return jsonify({
                'total_bundles': total_bundles,
                'avg_segments': float(avg_segments) if avg_segments else 0,
                'total_savings': float(total_savings) if total_savings else 0,
                'bundle_match_rate': float(bundle_match_rate),
                'bundle_types': {str(num_seg): count for num_seg, count in bundle_types}
            })

        finally:
            session.close()

    except ImportError:
        return jsonify({
            'error': 'Database dependencies not installed',
            'message': 'Install: pip install sqlalchemy psycopg2-binary'
        }), 500
    except Exception as e:
        logger.error(f"Error fetching bundle stats: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Database connection failed. Run: python setup_database.py'
        }), 500


@app.route('/api/bundles/list', methods=['GET'])
def get_bundles_list():
    """List all bundles with pagination"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from abm.database.models import Bundle, BundleSegment

        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Use SQLite database
        import os
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'maas_bundles.db')
        DATABASE_URL = f"sqlite:///{sqlite_path}"

        from abm.database.models_sqlite import Bundle, BundleSegment

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Query bundles with segments
            bundles = session.query(Bundle).order_by(Bundle.created_at.desc()).limit(limit).offset(offset).all()

            bundle_list = []
            for bundle in bundles:
                # Get segments for this bundle
                segments = session.query(BundleSegment).filter(
                    BundleSegment.bundle_id == bundle.bundle_id
                ).order_by(BundleSegment.segment_order).all()

                bundle_list.append({
                    'bundle_id': bundle.bundle_id,
                    'origin': f"[{bundle.origin_x}, {bundle.origin_y}]",
                    'destination': f"[{bundle.dest_x}, {bundle.dest_y}]",
                    'num_segments': bundle.num_segments,
                    'total_price': float(bundle.final_price),
                    'base_price': float(bundle.base_price),
                    'discount_amount': float(bundle.discount_amount),
                    'total_duration': bundle.total_duration,
                    'created_at': bundle.created_at.isoformat() if bundle.created_at else None,
                    'segments': [{
                        'mode': seg.mode,
                        'origin': f"[{seg.from_x}, {seg.from_y}]",
                        'destination': f"[{seg.to_x}, {seg.to_y}]",
                        'price': float(seg.price),
                        'duration': seg.duration,
                        'segment_order': seg.segment_order
                    } for seg in segments]
                })

            return jsonify({
                'bundles': bundle_list,
                'total': len(bundle_list),
                'limit': limit,
                'offset': offset
            })

        finally:
            session.close()

    except ImportError:
        return jsonify({
            'error': 'Database dependencies not installed',
            'message': 'Install: pip install sqlalchemy psycopg2-binary'
        }), 500
    except Exception as e:
        logger.error(f"Error fetching bundles list: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Database connection failed. Run: python setup_database.py'
        }), 500


@app.route('/api/bundles/details/<bundle_id>', methods=['GET'])
def get_bundle_details_api(bundle_id):
    """Get detailed bundle information"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Use SQLite database
        import os
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'maas_bundles.db')
        DATABASE_URL = f"sqlite:///{sqlite_path}"

        from abm.database.models_sqlite import Bundle, BundleSegment, Reservation, SegmentReservation

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Query bundle
            bundle = session.query(Bundle).filter(Bundle.bundle_id == bundle_id).first()

            if not bundle:
                return jsonify({'error': 'Bundle not found'}), 404

            # Get segments
            segments = session.query(BundleSegment).filter(
                BundleSegment.bundle_id == bundle.bundle_id
            ).order_by(BundleSegment.segment_order).all()

            # Get reservation info
            reservation = session.query(Reservation).filter(
                Reservation.bundle_id == bundle.bundle_id
            ).first()

            reservation_info = None
            if reservation:
                # Get segment reservations
                seg_reservations = session.query(SegmentReservation).filter(
                    SegmentReservation.reservation_id == reservation.id
                ).all()

                reservation_info = {
                    'reservation_id': reservation.reservation_id,
                    'commuter_id': reservation.commuter_id,
                    'request_id': reservation.request_id,
                    'status': reservation.status,
                    'reserved_at': reservation.reserved_at.isoformat() if reservation.reserved_at else None,
                    'segment_reservations': [{
                        'segment_id': sr.segment_id,
                        'provider_id': sr.provider_id,
                        'nft_token_id': sr.nft_token_id
                    } for sr in seg_reservations]
                }

            return jsonify({
                'bundle_id': bundle.bundle_id,
                'origin': bundle.origin,
                'destination': bundle.destination,
                'num_segments': bundle.num_segments,
                'total_price': float(bundle.total_price),
                'base_price': float(bundle.base_price),
                'discount_percentage': float(bundle.discount_percentage),
                'discount_amount': float(bundle.discount_amount),
                'total_duration': bundle.total_duration,
                'utility_score': float(bundle.utility_score) if bundle.utility_score else None,
                'created_at': bundle.created_at.isoformat() if bundle.created_at else None,
                'segments': [{
                    'segment_id': seg.segment_id,
                    'mode': seg.mode,
                    'origin': seg.origin,
                    'destination': seg.destination,
                    'price': float(seg.price),
                    'duration': seg.duration,
                    'sequence_order': seg.sequence_order,
                    'provider_id': seg.provider_id,
                    'nft_token_id': seg.nft_token_id
                } for seg in segments],
                'reservation': reservation_info
            })

        finally:
            session.close()

    except ImportError:
        return jsonify({
            'error': 'Database dependencies not installed',
            'message': 'Install: pip install sqlalchemy psycopg2-binary'
        }), 500
    except Exception as e:
        logger.error(f"Error fetching bundle details: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Database connection failed. Run: python setup_database.py'
        }), 500


@app.route('/api/bundles/recent', methods=['GET'])
def get_recent_bundles():
    """Get recent bundle reservations"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Use SQLite database
        import os
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'maas_bundles.db')
        DATABASE_URL = f"sqlite:///{sqlite_path}"

        from abm.database.models_sqlite import Bundle, Reservation

        # Get limit parameter
        limit = int(request.args.get('limit', 10))

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Query recent reservations with bundles
            reservations = session.query(Reservation).join(
                Bundle, Reservation.bundle_id == Bundle.bundle_id
            ).order_by(Reservation.reserved_at.desc()).limit(limit).all()

            recent_list = []
            for res in reservations:
                bundle = session.query(Bundle).filter(Bundle.bundle_id == res.bundle_id).first()
                if bundle:
                    recent_list.append({
                        'bundle_id': bundle.bundle_id,
                        'commuter_id': res.commuter_id,
                        'origin': f"[{bundle.origin_x}, {bundle.origin_y}]",
                        'destination': f"[{bundle.dest_x}, {bundle.dest_y}]",
                        'num_segments': bundle.num_segments,
                        'total_price': float(bundle.final_price),
                        'discount_amount': float(bundle.discount_amount),
                        'reserved_at': res.reserved_at.isoformat() if res.reserved_at else None,
                        'status': res.status
                    })

            return jsonify({
                'recent_bundles': recent_list,
                'total': len(recent_list)
            })

        finally:
            session.close()

    except ImportError:
        return jsonify({
            'error': 'Database dependencies not installed',
            'message': 'Install: pip install sqlalchemy psycopg2-binary'
        }), 500
    except Exception as e:
        logger.error(f"Error fetching recent bundles: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Database connection failed. Run: python setup_database.py'
        }), 500


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/api/config/default', methods=['GET'])
def get_default_config():
    """Get default simulation configuration"""
    return jsonify({
        'steps': 50,
        'commuters': 10,
        'providers': 5,
        'debug': False,
        'no_plots': False,
        'seed': None
    })

if __name__ == '__main__':
    # Initialize blockchain connection
    init_blockchain()

    # Register database routes
    register_database_routes(app)

    # Register blockchain export routes
    register_blockchain_export_routes(app, blockchain_interface)

    # Start Flask server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
