"""
Database API endpoints for MaaS Platform
Provides data retrieval and export functionality
"""

import os
import io
import pandas as pd
from datetime import datetime
from flask import jsonify, send_file, request
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Database configuration
SQLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'maas_bundles.db')
DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

def get_database_session():
    """Create and return a database session"""
    try:
        from abm.database.models_sqlite import (
            Base, SimulationRun, SimulationTick, Commuter, Provider,
            TravelRequest, Bundle, BundleSegment, Reservation, SegmentReservation
        )
        
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session(), {
            'SimulationRun': SimulationRun,
            'SimulationTick': SimulationTick,
            'Commuter': Commuter,
            'Provider': Provider,
            'TravelRequest': TravelRequest,
            'Bundle': Bundle,
            'BundleSegment': BundleSegment,
            'Reservation': Reservation,
            'SegmentReservation': SegmentReservation
        }
    except Exception as e:
        print(f"Database session error: {e}")
        return None, None

def register_database_routes(app):
    """Register all database-related routes"""
    
    @app.route('/api/database/stats', methods=['GET'])
    def get_database_stats():
        """Get overall database statistics"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            stats = {
                'total_runs': session.query(func.count(models['SimulationRun'].run_id)).scalar() or 0,
                'total_bundles': session.query(func.count(models['Bundle'].id)).scalar() or 0,
                'total_commuters': session.query(func.count(models['Commuter'].id)).scalar() or 0,
                'total_providers': session.query(func.count(models['Provider'].id)).scalar() or 0,
                'total_requests': session.query(func.count(models['TravelRequest'].id)).scalar() or 0,
                'total_reservations': session.query(func.count(models['Reservation'].id)).scalar() or 0,
                'last_updated': datetime.now().isoformat()
            }
            return jsonify(stats)
        except Exception as e:
            print(f"Database stats error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/overview', methods=['GET'])
    def get_database_overview():
        """Get database overview with stats"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            stats = {
                'total_runs': session.query(func.count(models['SimulationRun'].run_id)).scalar() or 0,
                'total_bundles': session.query(func.count(models['Bundle'].id)).scalar() or 0,
                'total_commuters': session.query(func.count(models['Commuter'].id)).scalar() or 0,
                'total_providers': session.query(func.count(models['Provider'].id)).scalar() or 0,
                'total_requests': session.query(func.count(models['TravelRequest'].id)).scalar() or 0,
                'total_reservations': session.query(func.count(models['Reservation'].id)).scalar() or 0
            }

            return jsonify({
                'data': [],
                'stats': stats
            })
        except Exception as e:
            print(f"Database overview error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/runs', methods=['GET'])
    def get_simulation_runs():
        """Get all simulation runs"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            runs = session.query(models['SimulationRun']).order_by(
                models['SimulationRun'].start_time.desc()
            ).all()

            run_list = []
            for run in runs:
                config = run.config if isinstance(run.config, dict) else {}
                run_list.append({
                    'run_id': run.run_id,
                    'start_time': run.start_time.isoformat() if run.start_time else None,
                    'end_time': run.end_time.isoformat() if run.end_time else None,
                    'total_steps': run.total_steps,
                    'num_commuters': run.num_commuters,
                    'num_providers': run.num_providers,
                    'network_type': run.network_type,
                    'status': run.status
                })

            return jsonify({
                'data': run_list,
                'stats': {'total_runs': len(run_list)}
            })
        except Exception as e:
            print(f"Database runs error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/bundles', methods=['GET'])
    def get_all_bundles():
        """Get all bundles from database"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            bundles = session.query(models['Bundle']).order_by(
                models['Bundle'].created_at.desc()
            ).limit(100).all()
            
            bundle_list = []
            for bundle in bundles:
                bundle_list.append({
                    'bundle_id': bundle.bundle_id,
                    'origin': f"[{bundle.origin_x}, {bundle.origin_y}]",
                    'destination': f"[{bundle.dest_x}, {bundle.dest_y}]",
                    'num_segments': bundle.num_segments,
                    'total_price': float(bundle.final_price),
                    'discount_amount': float(bundle.discount_amount),
                    'created_at': bundle.created_at.isoformat() if bundle.created_at else None
                })
            
            return jsonify({
                'data': bundle_list,
                'stats': {'total_bundles': len(bundle_list)}
            })
        except Exception as e:
            print(f"Database bundles error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/commuters', methods=['GET'])
    def get_all_commuters():
        """Get all commuters from database"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            commuters = session.query(models['Commuter']).all()

            commuter_list = []
            for commuter in commuters:
                commuter_list.append({
                    'id': commuter.id,
                    'run_id': commuter.run_id,
                    'agent_id': commuter.agent_id,
                    'wallet_address': commuter.wallet_address,
                    'total_requests': commuter.total_requests,
                    'successful_trips': commuter.successful_trips,
                    'total_spent': float(commuter.total_spent) if commuter.total_spent else 0.0,
                    'avg_wait_time': float(commuter.avg_wait_time) if commuter.avg_wait_time else None
                })

            return jsonify({
                'data': commuter_list,
                'stats': {'total_commuters': len(commuter_list)}
            })
        except Exception as e:
            print(f"Database commuters error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/providers', methods=['GET'])
    def get_all_providers():
        """Get all providers from database"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            providers = session.query(models['Provider']).all()

            provider_list = []
            for provider in providers:
                provider_list.append({
                    'id': provider.id,
                    'run_id': provider.run_id,
                    'agent_id': provider.agent_id,
                    'wallet_address': provider.wallet_address,
                    'mode': provider.mode,
                    'total_offers': provider.total_offers,
                    'successful_matches': provider.successful_matches,
                    'total_revenue': float(provider.total_revenue) if provider.total_revenue else 0.0,
                    'avg_price': float(provider.avg_price) if provider.avg_price else None,
                    'utilization_rate': float(provider.utilization_rate) if provider.utilization_rate else None
                })

            return jsonify({
                'data': provider_list,
                'stats': {'total_providers': len(provider_list)}
            })
        except Exception as e:
            print(f"Database providers error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/requests', methods=['GET'])
    def get_all_requests():
        """Get all travel requests from database"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            requests = session.query(models['TravelRequest']).order_by(
                models['TravelRequest'].created_at_tick.desc()
            ).limit(100).all()

            request_list = []
            for req in requests:
                request_list.append({
                    'id': req.id,
                    'run_id': req.run_id,
                    'request_id': req.request_id,
                    'commuter_id': req.commuter_id,
                    'origin': f"[{req.origin_x}, {req.origin_y}]",
                    'destination': f"[{req.dest_x}, {req.dest_y}]",
                    'created_at_tick': req.created_at_tick,
                    'matched': req.matched,
                    'matched_at_tick': req.matched_at_tick,
                    'final_price': float(req.final_price) if req.final_price else None,
                    'num_bids_received': req.num_bids_received
                })

            return jsonify({
                'data': request_list,
                'stats': {'total_requests': len(request_list)}
            })
        except Exception as e:
            print(f"Database requests error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/reservations', methods=['GET'])
    def get_all_reservations():
        """Get all reservations from database"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            reservations = session.query(models['Reservation']).order_by(
                models['Reservation'].reserved_at.desc()
            ).limit(100).all()

            reservation_list = []
            for res in reservations:
                reservation_list.append({
                    'id': res.id,
                    'run_id': res.run_id,
                    'bundle_id': res.bundle_id,
                    'commuter_id': res.commuter_id,
                    'reserved_at': res.reserved_at.isoformat() if res.reserved_at else None,
                    'reserved_at_tick': res.reserved_at_tick,
                    'transaction_hash': res.transaction_hash,
                    'status': res.status
                })

            return jsonify({
                'data': reservation_list,
                'stats': {'total_reservations': len(reservation_list)}
            })
        except Exception as e:
            print(f"Database reservations error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/database/export/<table>/<format>', methods=['GET'])
    def export_table(table, format):
        """Export database table to Excel or CSV"""
        session, models = get_database_session()
        if not session:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            # Map table names to models
            table_map = {
                'runs': 'SimulationRun',
                'bundles': 'Bundle',
                'commuters': 'Commuter',
                'providers': 'Provider',
                'requests': 'TravelRequest',
                'reservations': 'Reservation',
                'all': None
            }
            
            if table not in table_map:
                return jsonify({'error': 'Invalid table name'}), 400
            
            # Create DataFrame based on table
            if table == 'all':
                # Export all tables to separate sheets
                return export_all_tables(session, models, format)
            else:
                model = models[table_map[table]]
                data = session.query(model).all()
                
                # Convert to DataFrame
                df = pd.DataFrame([{
                    col.name: getattr(row, col.name)
                    for col in model.__table__.columns
                } for row in data])
            
            # Generate file
            output = io.BytesIO()
            
            if format == 'excel':
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=table.capitalize(), index=False)
                output.seek(0)
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = f'{table}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            else:  # CSV
                df.to_csv(output, index=False)
                output.seek(0)
                mimetype = 'text/csv'
                filename = f'{table}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    def export_all_tables(session, models, format):
        """Export all tables to a single file"""
        try:
            output = io.BytesIO()
            
            if format == 'excel':
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for table_name, model_name in [
                        ('Runs', 'SimulationRun'),
                        ('Bundles', 'Bundle'),
                        ('Commuters', 'Commuter'),
                        ('Providers', 'Provider'),
                        ('Requests', 'TravelRequest'),
                        ('Reservations', 'Reservation')
                    ]:
                        model = models[model_name]
                        data = session.query(model).all()
                        df = pd.DataFrame([{
                            col.name: getattr(row, col.name)
                            for col in model.__table__.columns
                        } for row in data])
                        df.to_excel(writer, sheet_name=table_name, index=False)
                
                output.seek(0)
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = f'maas_database_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            else:
                return jsonify({'error': 'CSV format not supported for all tables export'}), 400
            
            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            raise e

