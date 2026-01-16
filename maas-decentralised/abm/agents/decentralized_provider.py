# File: abm/agents/decentralized_provider.py
# SIMPLIFIED VERSION - Uses marketplace API for all operations

import logging
import random
import math
from contextlib import nullcontext
from mesa import Agent

class DecentralizedProvider(Agent):
    """
    Simplified provider agent that uses marketplace API

    Now supports proactive NFT segment creation for bundle routing
    """

    def __init__(self, unique_id, model, pos, company_name, mode_type,
                 capacity, base_price, blockchain_interface=None):
        super().__init__(unique_id, model)

        # Agent type identifier for database export
        self.is_provider = True
        # Basic attributes
        self.pos = pos
        self.company_name = company_name
        self.mode_type = mode_type
        self.capacity = capacity
        self.available_capacity = capacity
        self.base_price = base_price

        # Marketplace interface
        self.marketplace = blockchain_interface  # This is actually the marketplace API

        # Service tracking
        self.active_offers = {}
        self.completed_services = 0
        self.total_revenue = 0

        # Quality metrics
        self.quality_score = random.randint(60, 90)
        self.reliability = random.randint(70, 95)
        self.service_center = list(pos)

        # Bundle segment tracking
        self.active_segments = {}  # Track created NFT segments
        self.segment_creation_interval = 10  # Create segments every N steps
        self.last_segment_creation = 0

        # Logging
        self.logger = logging.getLogger(f"Provider-{unique_id}-{company_name}")
        
    def step(self):
        """Main step function - simplified flow"""
        # Register with marketplace if not registered
        if not hasattr(self, 'registered'):
            success, address = self.marketplace.register_provider(self)
            if success:
                self.registered = True
                self.address = address

                # Store detailed provider profile for booking analysis
                profile_data = {
                    'provider_id': self.unique_id,
                    'name': f"{self.company_name}-{self.unique_id}",
                    'mode': self.mode_type,
                    'capacity': self.capacity,
                    'base_price': self.base_price,
                    'quality_score': self.quality_score,
                    'reliability': self.reliability,
                    'service_center': self.service_center,
                    'company_name': self.company_name
                }
                self.marketplace.store_provider_profile(self.unique_id, profile_data)

        # Check for notifications from marketplace
        if hasattr(self, 'registered') and self.registered:
            self.check_marketplace_notifications()

            # Arbitrage scan every 3 steps to add liquidity
            if self.model.current_step % 3 == 0:
                self._run_arbitrage_logic()

    def accept_booking(self, commuter_id, request_id, price, start_time, route=None):
        """
        Handle a direct booking request and record it with explicit mode information.
        """
        # Basic capacity check
        if self.available_capacity <= 0:
            self.logger.warning(f"Provider {self.unique_id} has no capacity for request {request_id}")
            return False

        # Derive duration from route distance and mode speed
        origin = route[0] if route else self.service_center
        destination = route[-1] if route else self.service_center
        trip_distance = self._calculate_distance(origin, destination)
        if self.mode_type == 'car':
            speed = 2.0
        elif self.mode_type == 'bike':
            speed = 0.8
        else:
            speed = 1.0
        duration = max(1, int(trip_distance / speed)) if trip_distance else 1
        end_time = start_time + duration

        match_id = f"direct_{self.unique_id}_{request_id}"
        match_data = {
            'match_id': match_id,
            'request_id': request_id,
            'commuter_id': commuter_id,
            'provider_id': self.unique_id,
            'price': price,
            'timestamp': self.model.schedule.time,
            'status': 'completed',
            'source': 'direct',
            'mode': self.mode_type,
            'provider_type': self.mode_type,
            'origin': origin,
            'destination': destination,
            'route_details': {'route': route or [origin, destination], 'duration': duration},
            'start_time': start_time,
            'end_time': end_time,
        }

        # Record match details and transaction with explicit mode
        if hasattr(self.blockchain_interface, "store_match_details"):
            self.blockchain_interface.store_match_details(match_id, match_data)
        if hasattr(self.blockchain_interface, "_record_transaction"):
            self.blockchain_interface._record_transaction(
                offer_id=f"direct_{request_id}",
                buyer_id=commuter_id,
                price=price,
                tx_type="direct_booking",
                explicit_tick=self.model.current_step,
                source_override='direct',
                start_time=start_time,
                duration=duration,
                mode_override=self.mode_type
            )

        # Reduce capacity until service completion
        self.available_capacity = max(0, self.available_capacity - 1)
        self.active_offers[request_id] = {
            'price': price,
            'details': {
                'route': [origin, destination],
                'time': duration,
                'mode': self.mode_type
            },
            'submitted_at': self.model.schedule.time
        }

        self.logger.info(f"Direct booking accepted by {self.unique_id} ({self.mode_type}) for request {request_id}")
        return True
    
    def check_marketplace_notifications(self):
        """Check for request notifications from marketplace"""
        notifications = self.marketplace.get_provider_notifications(self.unique_id)
        
        for notification in notifications[-5:]:  # Process last 5 notifications
            request_id = notification['request_id']
            if request_id not in self.active_offers:
                self.submit_offer_for_request(request_id)
    
    def submit_offer_for_request(self, request_id):
        """Submit an offer through marketplace API"""
        # Get request details from marketplace
        requests = self.marketplace.get_marketplace_requests()
        request = next((r for r in requests if r['request_id'] == request_id), None)
        
        if not request:
            return False

        # Calculate trip distance origin->destination for pricing/time
        trip_distance = self._calculate_distance(request['origin'], request['destination'])
        # Use requested start_time when available so downstream logging has a real depart_time
        depart_time = request.get('start_time', self.model.current_step)

        # Utilization for dynamic pricing
        utilization = 1.0 - (self.available_capacity / max(1, self.capacity))

        if self.mode_type == 'car':
            speed = 2.4 * random.uniform(0.85, 1.15)  # slightly slower to reduce dominance
            base_rate = 1.4  # slightly higher to reduce dominance
            if utilization > 0.8:
                surge = 2.5
            elif utilization < 0.2:
                surge = 0.4  # even deeper discount when idle
            else:
                surge = 1.0
            price = (self.base_price * 0.5 + trip_distance * base_rate) * surge
        elif self.mode_type == 'bike':
            speed = 0.6 * random.uniform(0.85, 1.1)   # faster to revive bike share
            price = 0.8 + trip_distance * 0.4        # cheaper to encourage bikes
            price *= random.uniform(0.9, 1.1)
        else:
            speed = 1.0 * random.uniform(0.8, 1.2)
            price = self.base_price + trip_distance * 2.0

        # Add randomness and floor
        price *= random.uniform(0.9, 1.1)
        price = max(1.0, round(price, 2))

        # Estimated travel time (in ticks)
        travel_time = max(1, int(trip_distance / speed))
        arrive_time = depart_time + travel_time

        # Prepare offer details
        offer_details = {
            'route': [request['origin'], request['destination']],
            'time': travel_time,
            'mode': self.mode_type,
            'depart_time': depart_time,
            'start_time': depart_time,
            'estimated_time': travel_time,
            'arrive_time': arrive_time,
        }
        
        # Submit offer through marketplace API (not blockchain directly!)
        success = self.marketplace.submit_offer(
            self,
            request_id,
            price,
            offer_details
        )
        
        if success:
            self.active_offers[request_id] = {
                'price': price,
                'details': offer_details,
                'submitted_at': self.model.schedule.time
            }

            # Store detailed offer information for booking analysis
            offer_id = f"{request_id}{self.unique_id}"  # Create unique offer ID
            offer_data = {
                'offer_id': offer_id,
                'provider_id': self.unique_id,
                'request_id': request_id,
                'price': price,
                'estimated_time': offer_details['time'],
                'mode': self.mode_type,
                'route': offer_details['route'],
                'depart_time': depart_time,
                'start_time': depart_time,
                'arrive_time': arrive_time,
                'distance': trip_distance,
                'submitted_at': self.model.schedule.time,
                'provider_location': self.service_center
            }
            self.marketplace.store_offer_details(offer_id, offer_data)

            self.logger.info(f"Submitted offer for request {request_id} at price {price:.2f}")
        
        return success
    
    def complete_service(self, request_id, price):
        """Complete a service, update metrics, and relocate provider"""
        self.completed_services += 1
        self.total_revenue += price

        # Relocate to destination of the served trip
        if request_id in self.active_offers:
            details = self.active_offers[request_id]['details']
            dest = details.get('route', [])[-1] if details.get('route') else None
            if dest:
                try:
                    self.model.grid.move_agent(self, dest)
                except Exception:
                    pass
                self.pos = dest
                self.service_center = list(dest)
            del self.active_offers[request_id]

        # Update capacity
        self.available_capacity = self.capacity

        self.logger.info(f"Completed service for request {request_id}, relocated to {self.pos}")
        return True

    def _run_arbitrage_logic(self):
        """Market making: force scan and buy active listings."""
        try:
            # Read listings from marketplace_db
            db = getattr(self.marketplace, 'marketplace_db', {})
            all_listings = db.get('listings', {})

            # DEBUG: how many listings does this provider see?
            if len(all_listings) > 0:
                self.logger.info(f"DEBUG: Provider {self.unique_id} sees {len(all_listings)} listings.")

            # Active listings, exclude own sales
            listings = [
                l for l in all_listings.values()
                if l.get('status') == 'active' and str(l.get('seller_id')) != str(self.unique_id)
            ]
        except Exception as e:
            self.logger.error(f"Arbitrage logic error: {e}")
            return

        for listing in listings:
            details = listing.get('details', {})
            origin = details.get('origin', self.service_center)
            dest = details.get('destination', self.service_center)
            dist = self._calculate_distance(origin, dest)
            base_value = dist * self.base_price

            service_time = details.get('service_time', self.model.current_step)
            time_premium = 1.5 if self.model.check_is_peak(service_time) else 1.0
            fair_value = base_value * time_premium
            time_left = service_time - self.model.current_step

            ask = listing.get('current_price', listing.get('price', 1e9))
            nft_id = listing.get('nft_id')

            # Rational buy: require at least ~10% discount vs fair value
            if ask < fair_value * 0.90 and time_left > 0:
                self.logger.info(f"💰 Arbitrage! Buying NFT {nft_id} at {ask:.2f} (FV: {fair_value:.2f})")
                success = self.marketplace.purchase_nft(nft_id, self.unique_id)

                if success:
                    new_price = ask * 1.2  # relist at 20% premium
                    time_params = {
                        'initial_price': new_price,
                        'final_price': new_price * 0.8,
                        'decay_rate': 0.05
                    }
                    self.marketplace.list_nft_for_sale(nft_id, new_price, time_params)
                    self.logger.info(f"📈 Re-listed NFT {nft_id} at {new_price:.2f}")
                    break  # buy one and stop to avoid spam
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def get_service_offers(self, origin, destination, start_time):
        """Get service offers for a route - used by marketplace"""
        distance = self._calculate_distance(origin, destination)
        price = self.base_price + (distance * 2)

        return [{
            'provider_id': self.unique_id,
            'price': price,
            'time': int(distance * 3),
            'mode': self.mode_type,
            'quality': self.quality_score
        }]

    def _should_create_segments(self):
        """Check if provider should create new route segments"""
        # Only create segments if bundle system is enabled
        if not hasattr(self.model, 'enable_proactive_segments'):
            return False

        if not self.model.enable_proactive_segments:
            return False

        # Create segments periodically
        current_step = self.model.current_step
        if current_step - self.last_segment_creation >= self.segment_creation_interval:
            return True

        return False


class PublicTransportProvider(DecentralizedProvider):
    """
    Public transport provider that publishes fixed-schedule segment offers (no NFT mint until purchase).
    """

    def __init__(self, unique_id, model, pos, route_stations, schedule_interval=20,
                 capacity_per_trip=6, company_name="PublicTransport", base_fare=2.0,
                 blockchain_interface=None, mode_type="bus", speed_modifier=1.5):
        # Use model.blockchain_interface by default to retain register_provider/register_commuter APIs
        bc_if = blockchain_interface or getattr(model, "blockchain_interface", None)
        super().__init__(
            unique_id=unique_id,
            model=model,
            pos=pos,
            company_name=company_name,
            mode_type=mode_type,
            capacity=capacity_per_trip,
            base_price=base_fare,
            blockchain_interface=bc_if
        )
        self.route_stations = route_stations
        self.schedule_interval = schedule_interval
        self.capacity_per_trip = capacity_per_trip
        self.base_fare = base_fare
        self.last_publish_step = -1
        self.mode_type = mode_type
        # speed_modifier >1 -> slower than straight-line, <1 -> faster (express/rail)
        self.speed_modifier = speed_modifier

    def step(self):
        # Run base provider logic (registration, bookkeeping)
        super().step()

        # Publish future schedules periodically
        # Avoid re-publishing at t=0 if bootstrapped already; publish thereafter on interval
        if self.model.current_step > 0 and self.model.current_step % self.schedule_interval == 0:
            self.publish_future_schedules()

    def publish_future_schedules(self, horizon=60):
        """Publish segment offers for the next `horizon` minutes."""
        current = self.model.current_step
        # Snapshot existing offers to preserve sold_count/status
        existing_offers = {}
        if hasattr(self.marketplace, 'marketplace_db'):
            with self.marketplace.marketplace_db_lock:
                existing_offers = self.marketplace.marketplace_db.get('offers', {}).copy()
        for time_offset in range(0, horizon, self.schedule_interval):
            depart_time = current + time_offset
            # Peak-aware surge with softer off-peak pricing
            is_peak = False
            if hasattr(self.model, 'check_is_peak'):
                try:
                    is_peak = self.model.check_is_peak(depart_time)
                except Exception:
                    is_peak = False
            surge_multiplier = random.uniform(1.6, 2.1) if is_peak else random.uniform(0.8, 0.9)
            for i in range(len(self.route_stations) - 1):
                origin = self.route_stations[i]
                dest = self.route_stations[i + 1]
                segment_id = f"BUS_{self.unique_id}_{depart_time}_{i}" if self.mode_type == "bus" else f"TRAIN_{self.unique_id}_{depart_time}_{i}"
                dist = self._calculate_distance(origin, dest)
                duration = max(1, int(dist * self.speed_modifier))
                # Distance-based dynamic pricing with time-of-day surge and volatility
                time_of_day = depart_time % 144
                if (30 <= time_of_day <= 60) or (90 <= time_of_day <= 120):
                    predicted_utilization = random.uniform(0.8, 1.0)
                else:
                    predicted_utilization = random.uniform(0.1, 0.4)
                surge_pred = 1.0 + (predicted_utilization - 0.5) * 0.5  # slightly softer

                dist_rate = 0.18 if self.mode_type == 'bus' else 0.2
                base_component = 1.2 if self.mode_type == 'bus' else 1.8
                noise = random.uniform(-0.3, 0.6)
                dynamic_price = (base_component + dist * dist_rate) * surge_multiplier * surge_pred + noise
                dynamic_price = max(1.0, round(dynamic_price, 2))
                # Preserve sold_count/status if offer already exists
                current_sold = 0
                current_status = 'available'
                if segment_id in existing_offers:
                    old_offer = existing_offers[segment_id]
                    current_sold = old_offer.get('sold_count', 0)
                    if current_sold >= self.capacity_per_trip:
                        current_status = 'sold_out'
                    else:
                        current_status = old_offer.get('status', 'available')

                offer = {
                    'offer_id': segment_id,
                    'type': 'segment',
                    'provider_id': self.unique_id,
                    'mode': self.mode_type,
                    'origin': origin,
                    'destination': dest,
                    'depart_time': depart_time,
                    'start_time': depart_time,
                    'estimated_time': duration,
                    'arrive_time': depart_time + duration,
                    'price': dynamic_price,
                    'capacity': self.capacity_per_trip,
                    'sold_count': current_sold,
                    'status': current_status
                }
                if hasattr(self.marketplace, "broadcast_offer"):
                    self.marketplace.broadcast_offer(offer)
        self.logger.info(f"Provider {self.unique_id} published schedules from t={current} to {current + horizon}")

    def create_route_segments(self):
        """
        Create proactive NFT segments for bundle routing

        This creates intermediate route segments that can be combined
        into multi-modal bundles by the bundle router.
        """
        try:
            current_step = self.model.current_step
            self.last_segment_creation = current_step

            # Generate route segments based on provider's service area
            segments = self._generate_route_segments()

            if not segments:
                return

            # Create offers for each segment
            for segment in segments:
                segment_id = f"{self.unique_id}_{segment['origin']}_{segment['destination']}_{current_step}"

                # Create offer in marketplace database
                offer = {
                    'offer_id': segment_id,
                    'segment_id': segment_id,
                    'type': 'segment',  # Mark as proactive segment
                    'provider_id': self.unique_id,
                    'mode': self.mode_type,
                    'origin': segment['origin'],
                    'destination': segment['destination'],
                    'depart_time': segment['start_time'],
                    'arrive_time': segment['start_time'] + segment['duration'],
                    'estimated_time': segment['duration'],
                    'price': segment['price'],
                    'capacity': 1,
                    'status': 'available',  # Available for bundle routing
                    'created_at': current_step,
                    'route': [segment['origin'], segment['destination']]
                }

                # Store in marketplace database
                with self.marketplace.marketplace_db_lock:
                    self.marketplace.marketplace_db['offers'][segment_id] = offer

                # Track locally
                self.active_segments[segment_id] = offer

            self.logger.info(f"Created {len(segments)} route segments for bundle routing")

        except Exception as e:
            self.logger.error(f"Error creating route segments: {e}")
            import traceback
            traceback.print_exc()

    def _generate_route_segments(self):
        """
        Generate intermediate route segments based on provider's service area

        Creates segments that can connect with other providers' segments
        to form multi-modal bundles.

        Strategy: Create segments along grid lines to increase connectivity
        """
        segments = []
        current_step = self.model.current_step

        # Get grid dimensions
        grid_width = self.model.grid.width
        grid_height = self.model.grid.height

        # Create segments along major grid points for better connectivity
        # Use grid step size to align segments
        grid_step = 3  # Align to 3-unit grid for denser coverage

        # Generate 5-8 route segments for better network density
        num_segments = random.randint(5, 8)

        for i in range(num_segments):
            # Start from service center (rounded to grid)
            origin_x = round(self.service_center[0] / grid_step) * grid_step
            origin_y = round(self.service_center[1] / grid_step) * grid_step
            origin = [origin_x, origin_y]

            # Create destination along cardinal or diagonal directions
            # This creates a network of connecting segments
            direction = random.choice([
                (1, 0),   # East
                (0, 1),   # North
                (-1, 0),  # West
                (0, -1),  # South
                (1, 1),   # Northeast
                (1, -1),  # Southeast
                (-1, 1),  # Northwest
                (-1, -1)  # Southwest
            ])

            # Distance: widen to 1-10 grid steps for broader length/pricing spread
            steps = random.randint(1, 10)
            dest_x = origin_x + (direction[0] * grid_step * steps)
            dest_y = origin_y + (direction[1] * grid_step * steps)

            # Clamp to grid boundaries
            dest_x = max(0, min(grid_width - 1, dest_x))
            dest_y = max(0, min(grid_height - 1, dest_y))

            destination = [dest_x, dest_y]

            # Skip if origin and destination are the same
            if origin == destination:
                continue

            # Calculate segment properties
            segment_distance = self._calculate_distance(origin, destination)
            if segment_distance < 1:  # Skip very short segments
                continue

            duration = int(segment_distance * 3)  # Time based on distance

            # Start time: stagger across a wide range to enable chaining
            # Some segments depart now, some in near future, some later
            # This allows segments to connect: segment1 arrives -> segment2 departs
            time_offset = i * 10  # Stagger by segment index
            start_time = current_step + time_offset + random.randint(-5, 10)

            # Dynamic pricing for PT segments with surge and noise
            if self.mode_type == "bus":
                dist_rate = 0.18
                base = 1.2
            else:
                dist_rate = 0.2
                base = 1.8
            time_of_day = start_time % 144
            is_peak = (30 <= time_of_day <= 60) or (90 <= time_of_day <= 120)
            surge = random.uniform(1.3, 1.7) if is_peak else 1.0
            raw_price = base + (segment_distance * dist_rate)
            price = raw_price * surge + random.uniform(-0.2, 0.8)
            price = max(1.0, round(price, 2))

            segment = {
                'origin': origin,
                'destination': destination,
                'start_time': start_time,
                'duration': duration,
                'price': price,
                'distance': segment_distance
            }

            segments.append(segment)

        return segments
