"""
Data Exporter for MaaS Simulation
Exports simulation results to SQLite database
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Try to import SQLite models first, fallback to PostgreSQL models
try:
    from .models_sqlite import (
        Base,
        SimulationRun,
        SimulationTick,
        Commuter,
        Provider,
        TravelRequest,
        Bundle,
        BundleSegment,
        Reservation,
        SegmentReservation,
        ModeUsageMetrics,
        BundlePerformanceMetrics,
        PriceTrend,
        BlockchainTransaction,
        NFTToken,
        NFTListing,
        SmartContractCall,
        BlockchainEvent,
        GasMetrics,
        MarketplaceMetrics
    )
    USE_SQLITE = True
except ImportError:
    from .models import (
        DatabaseManager,
        SimulationRun,
        SimulationTick,
        Commuter,
        Provider,
        TravelRequest,
        Bundle,
        BundleSegment,
        Reservation,
        SegmentReservation
    )
    USE_SQLITE = False


class SimulationExporter:
    """Exports simulation data to SQLite database"""

    def __init__(self, connection_string: Optional[str] = None, logger=None):
        """
        Initialize exporter

        Args:
            connection_string: Database connection string (SQLite or PostgreSQL)
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

        if USE_SQLITE:
            # Use SQLite database
            if connection_string is None:
                # Default to maas_bundles.db in project root
                db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'maas_bundles.db')
                connection_string = f"sqlite:///{db_path}"

            self.engine = create_engine(connection_string)
            Base.metadata.create_all(self.engine)
            # Ensure schema evolutions (like income_level) are present
            self._ensure_commuter_income_column()
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info(f"Using SQLite database: {connection_string}")
        else:
            # Use PostgreSQL database manager
            self.db_manager = DatabaseManager(connection_string)
            try:
                self.db_manager.create_tables()
                self.logger.info("Database tables ready")
            except Exception as e:
                self.logger.error(f"Error creating tables: {e}")
    
    def export_simulation(
        self,
        run_id: str,
        model,
        blockchain_interface,
        advanced_metrics: Dict,
        config: Dict
    ) -> bool:
        """
        Export complete simulation to database
        
        Args:
            run_id: Unique simulation run identifier
            model: DecentralizedABMModel instance
            blockchain_interface: BlockchainInterface instance
            advanced_metrics: Dictionary of calculated metrics
            config: Simulation configuration
            
        Returns:
            True if export successful, False otherwise
        """
        if USE_SQLITE:
            session = self.Session()
        else:
            session = self.db_manager.get_session()

        try:
            self.logger.info(f"Starting export for run {run_id}")
            
            # 1. Create simulation run record
            sim_run = self._export_run_metadata(session, run_id, model, config)
            
            # 2. Export agents (commuters and providers)
            commuter_map = self._export_commuters(session, run_id, model)
            provider_map = self._export_providers(session, run_id, model)
            
            # 3. Export requests
            request_map = self._export_requests(session, run_id, blockchain_interface, commuter_map)
            
            # 4. Export bundles and segments
            bundle_map = self._export_bundles(session, run_id, blockchain_interface, request_map, provider_map)
            
            # 5. Export reservations
            self._export_reservations(session, run_id, blockchain_interface, bundle_map, commuter_map)
            
            # 6. Export time-series tick data
            self._export_tick_data(session, run_id, model)

            # 7. Export mode usage metrics
            self._export_mode_usage_metrics(session, run_id, blockchain_interface, provider_map)

            # 8. Export bundle performance metrics
            self._export_bundle_performance_metrics(session, run_id, blockchain_interface)

            # 9. Export blockchain data
            self._export_blockchain_transactions(session, run_id, blockchain_interface, model)
            self._export_nft_data(session, run_id, blockchain_interface)
            self._export_gas_metrics(session, run_id, blockchain_interface, model)
            self._export_marketplace_metrics(session, run_id, blockchain_interface, model)

            # 10. Mark run as completed
            sim_run.status = 'completed'
            sim_run.end_time = datetime.utcnow()
            
            # Commit all changes
            session.commit()
            self.logger.info(f"Successfully exported simulation {run_id}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error during export: {e}")
            return False
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error during export: {e}")
            return False
        finally:
            session.close()

    def _ensure_commuter_income_column(self):
        """Add income_level column to commuters table if it does not exist (SQLite only)."""
        if not USE_SQLITE:
            return
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(commuters);"))
                cols = [row[1] for row in result.fetchall()]
                if 'income_level' not in cols:
                    conn.execute(text("ALTER TABLE commuters ADD COLUMN income_level VARCHAR(20) DEFAULT 'unknown';"))
                    self.logger.info("Added income_level column to commuters table")
        except Exception as e:
            self.logger.warning(f"Could not ensure income_level column: {e}")
    
    def _export_run_metadata(self, session, run_id: str, model, config: Dict) -> SimulationRun:
        """Export simulation run metadata"""
        sim_run = SimulationRun(
            run_id=run_id,
            start_time=datetime.utcnow(),
            total_steps=config.get('steps', 0),
            num_commuters=config.get('commuters', 0),
            num_providers=config.get('providers', 0),
            network_type=config.get('network', 'localhost'),
            blockchain_rpc=config.get('rpc_url', ''),
            config=config,
            status='running'
        )
        session.add(sim_run)
        session.flush()  # Get ID without committing
        return sim_run
    
    def _export_commuters(self, session, run_id: str, model) -> Dict[int, int]:
        """
        Export commuter agents
        
        Returns:
            Mapping of agent_id -> database_id
        """
        commuter_map = {}
        
        for agent in model.schedule.agents:
            if hasattr(agent, 'is_commuter') and agent.is_commuter:
                income_level = getattr(agent, 'income_level', 'unknown')
                commuter = Commuter(
                    run_id=run_id,
                    agent_id=str(agent.unique_id),
                    wallet_address=getattr(agent, 'blockchain_address', None),
                    total_requests=len(getattr(agent, 'requests', {})),
                    successful_trips=getattr(agent, 'completed_trips', 0),
                    total_spent=sum(trip.get('price', 0) for trip in getattr(agent, 'trip_history', [])),
                    avg_wait_time=None,  # Calculate if needed
                    income_level=income_level
                )
                session.add(commuter)
                session.flush()
                commuter_map[agent.unique_id] = commuter.id
        
        # Simple income distribution summary
        try:
            from collections import Counter
            income_counts = Counter(getattr(agent, 'income_level', 'unknown') for agent in model.schedule.agents if getattr(agent, 'is_commuter', False))
            self.logger.info(f"Exported {len(commuter_map)} commuters | Income distribution: {dict(income_counts)}")
        except Exception:
            self.logger.info(f"Exported {len(commuter_map)} commuters")

        return commuter_map
    
    def _export_providers(self, session, run_id: str, model) -> Dict[int, int]:
        """
        Export provider agents
        
        Returns:
            Mapping of agent_id -> database_id
        """
        provider_map = {}
        
        for agent in model.schedule.agents:
            if hasattr(agent, 'is_provider') and agent.is_provider:
                provider = Provider(
                    run_id=run_id,
                    agent_id=str(agent.unique_id),
                    wallet_address=getattr(agent, 'blockchain_address', None) or getattr(agent, 'address', None),
                    mode=getattr(agent, 'mode_type', getattr(agent, 'mode', 'unknown')),
                    total_offers=len(getattr(agent, 'active_offers', {})),
                    successful_matches=getattr(agent, 'completed_services', 0),
                    total_revenue=getattr(agent, 'total_revenue', 0.0),
                    avg_price=getattr(agent, 'base_price', 0.0),
                    utilization_rate=None  # Calculate if needed
                )
                session.add(provider)
                session.flush()
                provider_map[agent.unique_id] = provider.id
        
        self.logger.info(f"Exported {len(provider_map)} providers")
        return provider_map
    
    def _export_requests(self, session, run_id: str, blockchain, commuter_map: Dict) -> Dict[int, int]:
        """
        Export travel requests
        
        Returns:
            Mapping of request_id -> database_id
        """
        request_map = {}
        
        with blockchain.marketplace_db_lock:
            requests = blockchain.marketplace_db.get('requests', {})
            
            for req_id, req_data in requests.items():
                # Find commuter database ID
                commuter_agent_id = req_data.get('commuter_id')
                commuter_db_id = commuter_map.get(commuter_agent_id)
                
                if not commuter_db_id:
                    continue
                
                origin = req_data.get('origin', [0, 0])
                destination = req_data.get('destination', [0, 0])

                request = TravelRequest(
                    run_id=run_id,
                    request_id=str(req_id),
                    commuter_id=str(commuter_agent_id),
                    origin_x=float(origin[0]) if len(origin) > 0 else 0.0,
                    origin_y=float(origin[1]) if len(origin) > 1 else 0.0,
                    dest_x=float(destination[0]) if len(destination) > 0 else 0.0,
                    dest_y=float(destination[1]) if len(destination) > 1 else 0.0,
                    created_at_tick=req_data.get('start_time', 0),
                    matched=req_data.get('status') == 'matched',
                    matched_at_tick=req_data.get('matched_at_tick'),
                    final_price=req_data.get('final_price'),
                    num_bids_received=len(req_data.get('offers', []))
                )
                session.add(request)
                session.flush()
                request_map[req_id] = request.id
        
        self.logger.info(f"Exported {len(request_map)} requests")
        return request_map
    
    def _generate_bundle_description(self, bundle_data: Dict, segments: List[Dict]) -> str:
        """
        Generate a human-readable description for a bundle

        Args:
            bundle_data: Bundle information dictionary
            segments: List of segment dictionaries

        Returns:
            Human-readable description string
        """
        if not segments:
            return "Empty bundle"

        # Get transport modes
        modes = [seg.get('mode', 'unknown') for seg in segments]
        unique_modes = list(dict.fromkeys(modes))  # Preserve order, remove duplicates

        # Format mode names
        mode_names = {
            'bike': '🚲 Bike',
            'train': '🚆 Train',
            'bus': '🚌 Bus',
            'car': '🚗 Car',
            'walk': '🚶 Walk'
        }
        formatted_modes = [mode_names.get(m, m.capitalize()) for m in unique_modes]

        # Build description
        num_segments = len(segments)
        if num_segments == 1:
            desc = f"Direct trip via {formatted_modes[0]}"
        else:
            mode_str = " → ".join(formatted_modes)
            desc = f"Multi-modal journey: {mode_str}"

        # Add price and discount info
        total_price = bundle_data.get('total_price', 0)
        discount = bundle_data.get('bundle_discount', 0)

        if discount > 0:
            desc += f" (${total_price:.2f} with ${discount:.2f} multi-modal discount)"
        else:
            desc += f" (${total_price:.2f})"

        # Add duration if available
        duration = bundle_data.get('total_duration')
        if duration:
            desc += f" • {duration} min"

        return desc

    def _export_bundles(
        self,
        session,
        run_id: str,
        blockchain,
        request_map: Dict,
        provider_map: Dict
    ) -> Dict[str, str]:
        """
        Export bundles and their segments

        Returns:
            Mapping of bundle_id -> database_bundle_id
        """
        bundle_map = {}

        # Get bundles from blockchain marketplace
        with blockchain.marketplace_db_lock:
            matches = blockchain.marketplace_db.get('matches', {})
            
            for match_id, match_data in matches.items():
                # Extract bundle information from match
                bundle_data = match_data.get('bundle', {})
                if not bundle_data:
                    continue
                
                bundle_id = bundle_data.get('bundle_id', f"bundle_{match_id}")
                # Skip duplicates to avoid UNIQUE constraint errors
                if bundle_id in bundle_map:
                    continue

                existing = session.query(Bundle).filter_by(bundle_id=bundle_id).first()
                if existing:
                    bundle_map[bundle_id] = existing.bundle_id
                    continue

                request_id = match_data.get('request_id')
                request_db_id = request_map.get(request_id)
                
                if not request_db_id:
                    continue

                # Generate bundle description
                segments = bundle_data.get('segments', [])
                description = self._generate_bundle_description(bundle_data, segments)

                # Get origin and destination from bundle data or first/last segment
                origin_x = bundle_data.get('origin_x', segments[0].get('from_x', 0) if segments else 0)
                origin_y = bundle_data.get('origin_y', segments[0].get('from_y', 0) if segments else 0)
                dest_x = bundle_data.get('dest_x', segments[-1].get('to_x', 0) if segments else 0)
                dest_y = bundle_data.get('dest_y', segments[-1].get('to_y', 0) if segments else 0)

                total_price = bundle_data.get('total_price', 0)
                bundle_discount = bundle_data.get('bundle_discount', 0)

                # Create bundle record (compatible with both SQLite and PostgreSQL models)
                if USE_SQLITE:
                    bundle = Bundle(
                        run_id=run_id,
                        bundle_id=bundle_id,
                        origin_x=origin_x,
                        origin_y=origin_y,
                        dest_x=dest_x,
                        dest_y=dest_y,
                        base_price=total_price + bundle_discount,  # Original price before discount
                        discount_amount=bundle_discount,
                        final_price=total_price,
                        num_segments=len(segments),
                        total_duration=bundle_data.get('total_duration', 0),
                        description=description,
                        created_at_tick=bundle_data.get('expected_depart_time', 0)
                    )
                else:
                    bundle = Bundle(
                        run_id=run_id,
                        bundle_id=bundle_id,
                        request_id=request_db_id,
                        expected_depart_time=bundle_data.get('expected_depart_time', 0),
                        expected_arrive_time=bundle_data.get('expected_arrive_time', 0),
                        total_price=total_price,
                        total_duration=bundle_data.get('total_duration', 0),
                        num_segments=len(segments),
                        bundle_discount=bundle_discount,
                        utility_score=bundle_data.get('utility_score', 0),
                        description=description,
                        status='completed'
                    )

                session.add(bundle)
                session.flush()
                bundle_map[bundle_id] = bundle.bundle_id

                # Export segments for this bundle
                self._export_bundle_segments(
                    session,
                    bundle_id,
                    segments,
                    provider_map
                )
        
        self.logger.info(f"Exported {len(bundle_map)} bundles")
        return bundle_map
    
    def _export_bundle_segments(self, session, bundle_id: str, segments: List[Dict], provider_map: Dict):
        """Export individual segments within a bundle"""
        for idx, seg_data in enumerate(segments):
            provider_agent_id = seg_data.get('provider_id')
            provider_db_id = provider_map.get(provider_agent_id)
            
            if not provider_db_id:
                continue
            
            segment = BundleSegment(
                bundle_id=bundle_id,
                segment_id=seg_data.get('segment_id', f"{bundle_id}_seg_{idx}"),
                sequence=idx + 1,
                provider_id=provider_db_id,
                mode=seg_data.get('mode', 'unknown'),
                origin=list(seg_data.get('origin', [0, 0])),
                destination=list(seg_data.get('destination', [0, 0])),
                depart_time=seg_data.get('depart_time', 0),
                arrive_time=seg_data.get('arrive_time', 0),
                price=seg_data.get('price', 0),
                nft_token_id=seg_data.get('nft_token_id'),
                blockchain_tx_hash=seg_data.get('blockchain_tx_hash'),
                status='consumed'
            )
            session.add(segment)
    
    def _export_reservations(self, session, run_id: str, blockchain, bundle_map: Dict, commuter_map: Dict):
        """Export reservations and segment reservations"""
        # This would be populated from actual reservation data
        # For now, we'll create reservations from completed matches
        pass
    
    def _export_tick_data(self, session, run_id: str, model):
        """Export comprehensive time-series data for each simulation tick"""
        if hasattr(model, 'datacollector') and model.datacollector:
            df = model.datacollector.get_model_vars_dataframe()

            # Note: The datacollector only has limited metrics. For now, we'll export what's available.
            # Future enhancement: Add more metrics to the model's datacollector
            for tick, row in df.iterrows():
                # Extract execution time (it's a dict, so get the average)
                exec_time = row.get('Execution Time', {})
                avg_exec_time = 0.0
                if isinstance(exec_time, dict) and exec_time:
                    avg_exec_time = sum(exec_time.values()) / len(exec_time)
                elif isinstance(exec_time, (int, float)):
                    avg_exec_time = float(exec_time)

                tick_data = SimulationTick(
                    run_id=run_id,
                    tick=tick,
                    active_commuters=row.get('Active Commuters', 0),
                    active_providers=row.get('Active Providers', 0),
                    total_transactions=row.get('Total Transactions', 0),
                    active_nft_listings=row.get('Active NFT Listings', 0),
                    completed_trips=row.get('Completed Trips', 0),
                    average_nft_price=row.get('Average NFT Price', 0.0),
                    execution_time=avg_exec_time,
                    # Other fields will use default values (0) for now
                    # Future: Enhance datacollector to track these metrics
                )
                session.add(tick_data)

        self.logger.info(f"Exported {len(df) if hasattr(model, 'datacollector') and model.datacollector else 0} tick records")

    def _export_mode_usage_metrics(self, session, run_id: str, blockchain, provider_map: Dict):
        """Export transport mode usage statistics"""
        if not USE_SQLITE:
            return  # Only for SQLite models

        from .models_sqlite import ModeUsageMetrics

        mode_stats = {}

        # Aggregate data from matches/trips
        with blockchain.marketplace_db_lock:
            matches = blockchain.marketplace_db.get('matches', {})

            for match_data in matches.values():
                bundle_data = match_data.get('bundle', {})
                segments = bundle_data.get('segments', [])

                for seg in segments:
                    mode = seg.get('mode', 'unknown')
                    if mode not in mode_stats:
                        mode_stats[mode] = {
                            'trips': 0,
                            'segments': 0,
                            'revenue': 0.0,
                            'distance': 0.0
                        }

                    mode_stats[mode]['segments'] += 1
                    mode_stats[mode]['revenue'] += seg.get('price', 0.0)
                    mode_stats[mode]['distance'] += seg.get('distance', 0.0)

                # Count as trip if single-mode
                if len(segments) == 1:
                    mode = segments[0].get('mode', 'unknown')
                    mode_stats[mode]['trips'] += 1

        # Create records
        for mode, stats in mode_stats.items():
            metrics = ModeUsageMetrics(
                run_id=run_id,
                mode=mode,
                total_trips=stats['trips'],
                total_segments=stats['segments'],
                total_revenue=stats['revenue'],
                total_distance=stats['distance'],
                average_price=stats['revenue'] / stats['segments'] if stats['segments'] > 0 else 0.0
            )
            session.add(metrics)

        self.logger.info(f"Exported mode usage metrics for {len(mode_stats)} modes")

    def _export_bundle_performance_metrics(self, session, run_id: str, blockchain):
        """Export bundle system performance metrics"""
        if not USE_SQLITE:
            return  # Only for SQLite models

        from .models_sqlite import BundlePerformanceMetrics

        total_bundles = 0
        total_segments = 0
        total_revenue = 0.0
        total_discount = 0.0
        segment_counts = []
        mode_combinations = {}

        with blockchain.marketplace_db_lock:
            matches = blockchain.marketplace_db.get('matches', {})

            for match_data in matches.values():
                bundle_data = match_data.get('bundle', {})
                if not bundle_data:
                    continue

                total_bundles += 1
                segments = bundle_data.get('segments', [])
                num_segments = len(segments)
                total_segments += num_segments
                segment_counts.append(num_segments)

                total_revenue += bundle_data.get('total_price', 0.0)
                total_discount += bundle_data.get('bundle_discount', 0.0)

                # Track mode combinations
                if num_segments > 1:
                    modes = tuple(sorted([seg.get('mode', 'unknown') for seg in segments]))
                    mode_combinations[modes] = mode_combinations.get(modes, 0) + 1

        # Calculate metrics
        avg_segments = sum(segment_counts) / len(segment_counts) if segment_counts else 0.0
        max_segments = max(segment_counts) if segment_counts else 0
        avg_price = total_revenue / total_bundles if total_bundles > 0 else 0.0
        avg_discount_pct = (total_discount / (total_revenue + total_discount) * 100) if (total_revenue + total_discount) > 0 else 0.0

        # Format popular combinations
        popular_combos = [
            {"modes": list(modes), "count": count}
            for modes, count in sorted(mode_combinations.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        metrics = BundlePerformanceMetrics(
            run_id=run_id,
            total_bundles_created=total_bundles,
            total_bundles_reserved=total_bundles,  # Assume all created bundles are reserved
            bundle_reservation_rate=100.0 if total_bundles > 0 else 0.0,
            total_segments_created=total_segments,
            average_segments_per_bundle=avg_segments,
            max_segments_in_bundle=max_segments,
            total_bundle_revenue=total_revenue,
            total_discount_given=total_discount,
            average_bundle_price=avg_price,
            average_discount_percentage=avg_discount_pct,
            popular_mode_combinations=popular_combos
        )
        session.add(metrics)

        self.logger.info(f"Exported bundle performance metrics: {total_bundles} bundles")

    def _export_blockchain_transactions(self, session, run_id: str, blockchain_interface, model):
        """Export blockchain transaction data"""
        try:
            # Get blockchain stats
            stats = blockchain_interface.blockchain_stats

            # Export transaction summary from blockchain stats
            # Note: Individual transaction details would require tracking in blockchain_interface
            # For now, we'll create aggregate records based on available stats

            self.logger.info(f"Blockchain transactions tracked in stats: {stats.get('total_transactions', 0)}")

            # If blockchain interface has transaction history, export it
            if hasattr(blockchain_interface, 'transaction_history'):
                for tx_data in blockchain_interface.transaction_history:
                    tx = BlockchainTransaction(
                        run_id=run_id,
                        tx_hash=tx_data.get('tx_hash', ''),
                        tx_type=tx_data.get('tx_type', 'unknown'),
                        function_name=tx_data.get('function_name', ''),
                        sender_id=tx_data.get('sender_id', ''),
                        status=tx_data.get('status', 'confirmed'),
                        tick=tx_data.get('tick', 0),
                        params=tx_data.get('params', {}),
                        result=tx_data.get('result', {})
                    )
                    session.add(tx)

            self.logger.info("Exported blockchain transaction data")

        except Exception as e:
            self.logger.error(f"Error exporting blockchain transactions: {e}")

    def _export_nft_data(self, session, run_id: str, blockchain_interface):
        """Export NFT token and listing data"""
        try:
            # Get NFT data from marketplace
            if hasattr(blockchain_interface, 'marketplace'):
                marketplace = blockchain_interface.marketplace

                # Export NFT listings
                if hasattr(marketplace, 'listings'):
                    for nft_id, listing in marketplace.listings.items():
                        # Create NFT token record
                        nft_token = NFTToken(
                            run_id=run_id,
                            token_id=str(nft_id),
                            owner_id=listing.get('owner_id', ''),
                            service_type=listing.get('details', {}).get('service_type', ''),
                            origin_x=listing.get('details', {}).get('origin', [0, 0])[0],
                            origin_y=listing.get('details', {}).get('origin', [0, 0])[1],
                            dest_x=listing.get('details', {}).get('destination', [0, 0])[0],
                            dest_y=listing.get('details', {}).get('destination', [0, 0])[1],
                            base_price=listing.get('initial_price', 0.0),
                            current_price=listing.get('current_price', 0.0),
                            status=listing.get('status', 'active'),
                            minted_at_tick=listing.get('listing_time', 0)
                        )
                        session.add(nft_token)

                        # Create NFT listing record
                        nft_listing = NFTListing(
                            run_id=run_id,
                            listing_id=str(nft_id),
                            token_id=str(nft_id),
                            seller_id=listing.get('owner_id', ''),
                            initial_price=listing.get('initial_price', 0.0),
                            current_price=listing.get('current_price', 0.0),
                            min_price=listing.get('min_price', 0.0),
                            dynamic_pricing=listing.get('dynamic_pricing', False),
                            decay_rate=listing.get('decay_rate', 0.0),
                            status=listing.get('status', 'active'),
                            listed_at_tick=listing.get('listing_time', 0)
                        )
                        session.add(nft_listing)

                self.logger.info(f"Exported NFT data: {len(marketplace.listings)} listings")
            else:
                self.logger.info("No marketplace data available for NFT export")

        except Exception as e:
            self.logger.error(f"Error exporting NFT data: {e}")

    def _export_gas_metrics(self, session, run_id: str, blockchain_interface, model):
        """Export gas usage metrics"""
        try:
            stats = blockchain_interface.blockchain_stats

            # Calculate gas metrics from blockchain stats
            total_txs = stats.get('total_transactions', 0)
            successful_txs = stats.get('successful_transactions', 0)
            failed_txs = stats.get('failed_transactions', 0)

            # Create gas metrics record (aggregate for entire run)
            gas_metrics = GasMetrics(
                run_id=run_id,
                tick=model.schedule.steps if hasattr(model, 'schedule') else 0,
                total_gas_used=stats.get('total_gas_used', 0),
                total_transactions=total_txs,
                successful_transactions=successful_txs,
                failed_transactions=failed_txs,
                registration_txs=stats.get('commuter_registrations', 0) + stats.get('provider_registrations', 0),
                request_txs=stats.get('travel_requests', 0),
                offer_txs=stats.get('service_offers', 0),
                match_txs=stats.get('completed_matches', 0)
            )
            session.add(gas_metrics)

            self.logger.info(f"Exported gas metrics: {total_txs} total transactions")

        except Exception as e:
            self.logger.error(f"Error exporting gas metrics: {e}")

    def _export_marketplace_metrics(self, session, run_id: str, blockchain_interface, model):
        """Export NFT marketplace metrics"""
        try:
            if hasattr(blockchain_interface, 'marketplace'):
                marketplace = blockchain_interface.marketplace

                # Calculate marketplace metrics
                total_listings = len(marketplace.listings) if hasattr(marketplace, 'listings') else 0
                active_listings = sum(1 for l in marketplace.listings.values() if l.get('status') == 'active') if hasattr(marketplace, 'listings') else 0
                sold_listings = sum(1 for l in marketplace.listings.values() if l.get('status') == 'sold') if hasattr(marketplace, 'listings') else 0

                # Calculate trading volume
                total_volume = 0.0
                sale_prices = []
                if hasattr(marketplace, 'transaction_history'):
                    for tx in marketplace.transaction_history:
                        price = tx.get('price', 0.0)
                        total_volume += price
                        sale_prices.append(price)

                avg_sale_price = sum(sale_prices) / len(sale_prices) if sale_prices else 0.0
                min_sale_price = min(sale_prices) if sale_prices else 0.0
                max_sale_price = max(sale_prices) if sale_prices else 0.0

                # Create marketplace metrics record
                marketplace_metrics = MarketplaceMetrics(
                    run_id=run_id,
                    tick=model.schedule.steps if hasattr(model, 'schedule') else 0,
                    total_listings=total_listings,
                    active_listings=active_listings,
                    sold_listings=sold_listings,
                    total_nfts_minted=total_listings,
                    total_nfts_sold=sold_listings,
                    total_volume=total_volume,
                    average_sale_price=avg_sale_price,
                    min_sale_price=min_sale_price,
                    max_sale_price=max_sale_price,
                    transactions_count=len(marketplace.transaction_history) if hasattr(marketplace, 'transaction_history') else 0
                )
                session.add(marketplace_metrics)

                self.logger.info(f"Exported marketplace metrics: {total_listings} listings, {sold_listings} sold")
            else:
                self.logger.info("No marketplace data available for metrics export")

        except Exception as e:
            self.logger.error(f"Error exporting marketplace metrics: {e}")
