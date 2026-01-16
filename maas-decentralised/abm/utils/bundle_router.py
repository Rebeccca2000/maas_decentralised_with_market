"""
Decentralized Bundle Router for MaaS
Implements peer-to-peer bundle discovery and distributed route assembly
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import math
import hashlib
import json


class DecentralizedBundleRouter:
    """
    Decentralized bundle routing using peer-to-peer discovery
    
    Instead of a central router, this implements:
    1. Distributed segment discovery via blockchain event logs
    2. Peer-to-peer route assembly using graph traversal
    3. Auction-driven path formation for competitive pricing
    
    This avoids centralization by having each commuter independently:
    - Query blockchain for available segments (NFTs)
    - Assemble routes locally using graph algorithms
    - Participate in auctions for contested segments
    """
    
    def __init__(self, blockchain_interface, logger=None):
        self.blockchain = blockchain_interface
        self.logger = logger or logging.getLogger(__name__)
        
        # Local cache of segment graph (built from blockchain events)
        self.segment_graph = defaultdict(list)  # origin -> [(destination, segment_data)]
        self.segment_index = {}  # segment_id -> segment_data
        
        # Auction tracking for contested segments
        self.active_auctions = {}  # segment_id -> auction_data
        
    def get_active_segments(self, time_window: Tuple[int, int] = None) -> List[Dict]:
        """
        DECENTRALIZED: Query blockchain for active segments via event logs
        
        Instead of querying a central database, this reads NFT mint events
        and offer submissions directly from the blockchain.
        
        Args:
            time_window: (start_tick, end_tick) for filtering segments
            
        Returns:
            List of active segment dictionaries
        """
        try:
            # Query blockchain marketplace for active NFTs/offers
            # This is decentralized - reading from blockchain state
            active_segments = []
            
            # Get all active NFT listings from blockchain
            nfts = self.blockchain.search_nfts(
                origin_area=None,  # Get all
                destination_area=None,
                time_window=time_window,
                max_price=None
            )
            
            # Get all active offers from marketplace
            # Include both regular offers ('submitted') and proactive segments ('available')
            with self.blockchain.marketplace_db_lock:
                offers = [
                    offer for offer in self.blockchain.marketplace_db.get('offers', {}).values()
                    if offer.get('status') in ['submitted', 'available']
                ]
            
            # Convert NFTs to segment format
            for nft in nfts:
                segment = {
                    'segment_id': f"nft_{nft.get('token_id', '')}",
                    'type': 'nft',
                    'provider_id': nft.get('provider_id'),
                    'mode': nft.get('mode', 'unknown'),
                    'origin': nft.get('origin', []),
                    'destination': nft.get('destination', []),
                    'depart_time': nft.get('start_time', 0),
                    'arrive_time': nft.get('start_time', 0) + nft.get('estimated_time', 0),
                    'price': nft.get('price', 0),
                    'capacity': nft.get('capacity', 1),
                    'status': 'available',
                    'nft_token_id': nft.get('token_id')
                }
                active_segments.append(segment)
            
            # Convert offers to segment format
            for offer in offers:
                # Handle both regular offers (start_time) and proactive segments (depart_time)
                origin = offer.get('origin')
                destination = offer.get('destination')
                if not origin or not destination:
                    continue
                if not isinstance(origin, (list, tuple)) or not isinstance(destination, (list, tuple)):
                    continue
                depart_time = offer.get('depart_time', offer.get('start_time', 0))
                arrive_time = offer.get('arrive_time', depart_time + offer.get('estimated_time', 0))

                segment = {
                    'segment_id': f"offer_{offer.get('offer_id', '')}",
                    'type': offer.get('type', 'offer'),  # Preserve 'segment' type for proactive segments
                    'provider_id': offer.get('provider_id'),
                    'mode': offer.get('mode', 'unknown'),
                    'origin': origin,
                    'destination': destination,
                    'depart_time': depart_time,
                    'arrive_time': arrive_time,
                    'price': offer.get('price', 0),
                    'capacity': offer.get('capacity', 1),
                    'status': 'available',
                    'offer_signature': offer.get('signature')
                }
                active_segments.append(segment)
            
            self.logger.info(f"Retrieved {len(active_segments)} active segments from blockchain")
            return active_segments
            
        except Exception as e:
            self.logger.error(f"Error getting active segments: {e}")
            return []
    
    def build_segment_graph(self, segments: List[Dict]):
        """
        Build a directed graph of segments for route finding with robust coordinate parsing.
        Graph structure: origin_location -> [(destination_location, segment_data)]
        """
        self.segment_graph.clear()
        self.segment_index.clear()

        skipped = 0
        success_count = 0

        # Debug: show sample raw origin type to diagnose format issues
        if segments:
            first_seg = segments[0]
            self.logger.info(f"DEBUG: Sample Raw Segment Origin: {first_seg.get('origin')} (Type: {type(first_seg.get('origin'))})")

        for segment in segments:
            origin = self._parse_coordinate(segment.get('origin'))
            destination = self._parse_coordinate(segment.get('destination'))

            if not origin or not destination:
                skipped += 1
                continue

            try:
                segment_id = segment.get('segment_id', 'unknown')
                self.segment_graph[origin].append((destination, segment))
                self.segment_index[segment_id] = segment
                success_count += 1
            except Exception as e:
                self.logger.warning(f"Skipping segment due to unexpected error: {e}")
                skipped += 1
                continue

        self.logger.info(f"Built segment graph: {len(self.segment_graph)} nodes, {success_count} edges loaded. (Skipped {skipped} invalid/malformed)")
    
    def build_bundles(
        self,
        origin: List[float],
        destination: List[float],
        active_segments: List[Dict],
        start_time: int,
        max_transfers: int = 3,
        time_tolerance: int = 5
    ) -> List[Dict]:
        """
        DECENTRALIZED: Build bundle options using distributed graph traversal
        
        Each commuter independently assembles routes from available segments.
        No central coordinator - pure peer-to-peer discovery.
        
        Args:
            origin: Starting location [x, y]
            destination: Target location [x, y]
            active_segments: Available segments from blockchain
            start_time: Desired departure tick
            max_transfers: Maximum number of segments in bundle
            time_tolerance: Acceptable time deviation (ticks)
            
        Returns:
            List of bundle options, each containing:
                - bundle_id: Unique identifier
                - segments: List of segment dictionaries
                - total_price: Sum of segment prices
                - total_duration: Total travel time
                - num_transfers: Number of mode changes
                - utility_score: Calculated utility
        """
        # Build graph from available segments
        self.build_segment_graph(active_segments)

        # Inject virtual walk edges for first/last mile to connect origins/destinations to network
        origin_tuple = (round(origin[0]), round(origin[1]))
        destination_tuple = (round(destination[0]), round(destination[1]))
        self._inject_walk_edges(origin_tuple, destination_tuple, start_time)

        # Find all possible paths using depth-first search
        self.logger.info(f"🔍 Searching for paths from {origin_tuple} to {destination_tuple}")
        self.logger.info(f"   Graph has {len(self.segment_graph)} origin nodes")
        self.logger.info(f"   Start time: {start_time}, Max transfers: {max_transfers}, Time tolerance: {time_tolerance}")

        # Log sample graph nodes
        if self.segment_graph:
            sample_nodes = list(self.segment_graph.items())[:5]
            self.logger.info(f"   Sample graph nodes:")
            for node_origin, edges in sample_nodes:
                self.logger.info(f"     {node_origin} -> {len(edges)} edges to {[dest for dest, _ in edges]}")

        # Check if origin is in graph or nearby
        nearby_origins = [node for node in self.segment_graph.keys()
                         if self._is_close_enough(origin_tuple, node, threshold=4.0)]
        self.logger.info(f"   Found {len(nearby_origins)} nodes near origin: {nearby_origins[:5]}")

        all_paths = self._find_all_paths(
            origin_tuple,
            destination_tuple,
            start_time,
            max_transfers,
            time_tolerance
        )

        self.logger.info(f"   Found {len(all_paths)} valid paths")
        
        # Convert paths to bundle format
        bundles = []
        for path_segments in all_paths:
            bundle = self._create_bundle_from_path(path_segments, origin, destination, start_time)
            if bundle:
                bundles.append(bundle)
        
        # Sort by utility score (highest first)
        bundles.sort(key=lambda b: b.get('utility_score', 0), reverse=True)
        
        self.logger.info(f"Built {len(bundles)} bundle options for {origin} -> {destination}")
        return bundles
    
    def _find_all_paths(
        self,
        current: Tuple[float, float],
        destination: Tuple[float, float],
        current_time: int,
        max_depth: int,
        time_tolerance: int,
        current_path: List[Dict] = None,
        visited: Set[Tuple] = None
    ) -> List[List[Dict]]:
        """
        Recursive depth-first search to find all valid paths
        
        This is the core decentralized routing algorithm - no central coordinator needed
        """
        if current_path is None:
            current_path = []
        if visited is None:
            visited = set()
        
        # Base case: reached destination
        # Use larger threshold to account for grid-aligned segments (3-unit grid)
        if self._is_close_enough(current, destination, threshold=4.0):
            return [current_path] if current_path else []
        
        # Base case: max depth reached
        if len(current_path) >= max_depth:
            return []
        
        # Mark current location as visited
        visited.add(current)
        
        all_paths = []

        # Explore all outgoing segments from current location AND nearby locations
        # This allows matching even when origin/destination don't exactly align with grid
        nearby_segments = []

        # Check exact location first
        nearby_segments.extend(self.segment_graph.get(current, []))

        # For first segment only, also check nearby grid points
        if len(current_path) == 0:
            # Check nearby grid points (within 4 units) for starting segments (3-unit grid)
            for node_loc in self.segment_graph.keys():
                if node_loc != current and self._is_close_enough(current, node_loc, threshold=4.0):
                    nearby_segments.extend(self.segment_graph.get(node_loc, []))

        # Track rejections for debugging (only for first call)
        rejections = {'visited': 0, 'time_early': 0, 'time_late': 0, 'status': 0, 'explored': 0}

        # Explore all found segments
        for next_location, segment in nearby_segments:
            # Skip if already visited (avoid cycles)
            if next_location in visited:
                rejections['visited'] += 1
                continue

            # Check time compatibility
            # For first segment: must depart at or after start time
            # For subsequent segments: must depart after previous arrival (with tolerance for waiting)
            # Walk segments: allow immediate departure; set arrival based on duration
            if segment.get('mode') == 'walk':
                walk_duration = segment.get('duration', 1)
                segment_depart = current_time
                segment_arrive = current_time + walk_duration
            else:
                segment_depart = segment.get('depart_time', 0)
                segment_arrive = segment.get('arrive_time', segment_depart)

            if len(current_path) == 0:
                # First segment: can depart at or after start time (allow early departure within tolerance)
                if segment_depart < current_time - time_tolerance:
                    rejections['time_early'] += 1
                    continue
                # Don't depart too far in the future
                if segment_depart > current_time + time_tolerance * 2:
                    rejections['time_late'] += 1
                    continue
            else:
                # Subsequent segments: must depart after we arrive from previous segment
                # Allow waiting between segments (up to time_tolerance * 5)
                if segment_depart < current_time:
                    rejections['time_early'] += 1
                    continue
                if segment_depart > current_time + time_tolerance * 5:  # Allow longer wait for transfers
                    rejections['time_late'] += 1
                    continue

            # Check if segment is still available
            if segment.get('status') != 'available':
                rejections['status'] += 1
                continue

            rejections['explored'] += 1

            # Recursively explore from next location
            # Next time is when we ARRIVE at the next location (not current_time + duration)
            next_time = segment_arrive
            
            paths_from_here = self._find_all_paths(
                next_location,
                destination,
                next_time,
                max_depth,
                time_tolerance,
                current_path + [segment],
                visited.copy()
            )

            all_paths.extend(paths_from_here)

        # Log rejections for first-level search only
        if len(current_path) == 0 and len(nearby_segments) > 0:
            self.logger.info(f"   First-level search: {len(nearby_segments)} segments found, "
                           f"{rejections['explored']} explored, "
                           f"{rejections['visited']} visited, "
                           f"{rejections['time_early']} too early, "
                           f"{rejections['time_late']} too late, "
                           f"{rejections['status']} wrong status")

        return all_paths
    
    def _is_close_enough(self, loc1: Tuple[float, float], loc2: Tuple[float, float], threshold: float = 0.5) -> bool:
        """Check if two locations are within threshold distance"""
        distance = math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
        return distance <= threshold

    def _inject_walk_edges(self, origin: Tuple[float, float], destination: Tuple[float, float], start_time: int, radius: float = 10.0):
        """
        Add virtual walk segments to connect origin/destination to nearby network nodes.
        """
        nodes = list(self.segment_graph.keys())
        for node in nodes:
            # First mile: origin -> node
            dist_o = self._distance(origin, node)
            if dist_o <= radius:
                duration = max(1, int(dist_o * 3))
                walk_seg = {
                    'segment_id': f"walk_{origin}_{node}",
                    'type': 'walk',
                    'provider_id': 'walk',
                    'mode': 'walk',
                    'origin': origin,
                    'destination': node,
                    'depart_time': start_time,
                    'arrive_time': start_time + duration,
                    'duration': duration,
                    'price': 0,
                    'capacity': 9999,
                    'status': 'available'
                }
                self.segment_graph[origin].append((node, walk_seg))

            # Last mile: node -> destination
            dist_d = self._distance(node, destination)
            if dist_d <= radius:
                duration = max(1, int(dist_d * 3))
                walk_seg = {
                    'segment_id': f"walk_{node}_{destination}",
                    'type': 'walk',
                    'provider_id': 'walk',
                    'mode': 'walk',
                    'origin': node,
                    'destination': destination,
                    'depart_time': start_time,  # will be overridden by DFS timing logic for walk
                    'arrive_time': start_time + duration,
                    'duration': duration,
                    'price': 0,
                    'capacity': 9999,
                    'status': 'available'
                }
                self.segment_graph[node].append((destination, walk_seg))

    def _distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    
    def _create_bundle_from_path(self, segments: List[Dict], origin: List[float], destination: List[float], start_time: int) -> Optional[Dict]:
        """
        Create a bundle dictionary from a path of segments
        """
        if not segments:
            return None
        
        # Calculate bundle metrics with walk/wait disutility
        total_price = sum(seg.get('price', 0) for seg in segments)
        total_duration = segments[-1].get('arrive_time', 0) - segments[0].get('depart_time', 0)
        num_transfers = len(segments) - 1

        walk_time = 0
        wait_time = 0
        in_vehicle_time = 0

        # First wait: ready at start_time
        first_depart = segments[0].get('depart_time', 0)
        wait_time += max(0, first_depart - start_time)

        for i, seg in enumerate(segments):
            duration = seg.get('duration', 0)
            if seg.get('mode') == 'walk':
                walk_time += duration
            else:
                in_vehicle_time += duration

            if i > 0:
                prev_arrive = segments[i - 1].get('arrive_time', 0)
                curr_depart = seg.get('depart_time', 0)
                wait_time += max(0, curr_depart - prev_arrive)

        # Apply multi-modal discount (5% per additional segment, max 15%)
        discount_rate = min(0.15, num_transfers * 0.05)
        discounted_price = total_price * (1 - discount_rate)

        # Calculate utility score (lower is better: price + time penalty)
        weighted_time = in_vehicle_time + (walk_time * 2.5) + (wait_time * 2.0)
        time_penalty = weighted_time * 0.5  # Value of time proxy
        utility_score = -(discounted_price + time_penalty)  # Negative for sorting

        # Generate unique bundle ID
        bundle_id = self._generate_bundle_id(segments)

        return {
            'bundle_id': bundle_id,
            'segments': segments,
            'total_price': discounted_price,
            'original_price': total_price,
            'bundle_discount': total_price - discounted_price,
            'total_duration': total_duration,
            'num_transfers': num_transfers,
            'num_segments': len(segments),
            'utility_score': utility_score,
            'expected_depart_time': segments[0].get('depart_time', 0),
            'expected_arrive_time': segments[-1].get('arrive_time', 0),
            'modes': [seg.get('mode') for seg in segments],
            'walk_time': walk_time,
            'wait_time': wait_time,
            'in_vehicle_time': in_vehicle_time
        }
    
    def _generate_bundle_id(self, segments: List[Dict]) -> str:
        """Generate unique bundle ID from segment composition"""
        segment_ids = [seg.get('segment_id', '') for seg in segments]
        bundle_str = '_'.join(sorted(segment_ids))
        return hashlib.md5(bundle_str.encode()).hexdigest()[:16]

    def _parse_coordinate(self, coord) -> Optional[Tuple[int, int]]:
        """
        Robust coordinate parser handling lists, tuples, and string representations.
        Returns a rounded (x, y) tuple or None if parsing fails.
        """
        if coord is None:
            return None

        try:
            # Already list/tuple
            if isinstance(coord, (list, tuple)):
                if len(coord) >= 2:
                    return (round(float(coord[0])), round(float(coord[1])))

            # String representation: "[10, 20]" or "10,20" etc.
            if isinstance(coord, str):
                clean = coord.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                parts = [float(x.strip()) for x in clean.split(',') if x.strip() != '']
                if len(parts) >= 2:
                    return (round(parts[0]), round(parts[1]))
        except (ValueError, TypeError, AttributeError):
            return None

        return None
