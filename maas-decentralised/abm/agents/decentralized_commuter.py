from mesa import Agent
import numpy as np
import math
import uuid
import logging
import random
from datetime import datetime, timedelta

class DecentralizedCommuter(Agent):
    """
    A commuter agent with blockchain identity capable of requesting, purchasing, 
    and trading mobility services through the blockchain.
    
    This agent makes decisions based on utility calculations and learns from past 
    experiences to adapt its strategy over time.
    """
    def __init__(self, unique_id, model, location, age, income_level,
                 has_disability, tech_access, health_status, payment_scheme,
                 blockchain_interface):
        """
        Initialize a new decentralized commuter agent.
        
        Args:
            unique_id: Unique identifier for the agent
            model: The model containing the agent
            location: Current location coordinates (x, y)
            age: Age of the commuter
            income_level: Income level ('low', 'middle', 'high')
            has_disability: Whether the commuter has a disability
            tech_access: Whether the commuter has access to technology
            health_status: Health status ('good', 'poor')
            payment_scheme: Payment scheme ('PAYG', 'subscription')
            blockchain_interface: Interface to the blockchain
        """
        super().__init__(unique_id, model)
        # Agent type identifier for database export
        self.is_commuter = True
        # Basic attributes
        self.location = location
        self.age = age
        self.income_level = income_level
        self.has_disability = has_disability
        self.tech_access = tech_access
        self.health_status = health_status
        self.payment_scheme = payment_scheme
        # Socio-economic/urgency parameters
        self.base_vot = {'high': 0.50, 'middle': 0.25, 'low': 0.13}.get(income_level, 0.25)
        self.current_urgency = 0.0  # refreshed whenever a new trip is generated
        
        # Travel patterns
        self.home_location = location
        self.work_location = None
        self.regular_destinations = {}  
        self.current_destination = None
        self.current_path = []
        self.current_mode = None
        self.next_trip_time = None
        self.next_destination = None
        
        # Blockchain-specific attributes
        self.blockchain_interface = blockchain_interface
        self.blockchain_address = None
        self.owned_nfts = {}  # NFTs owned by this commuter
        self.requests = {}  # All requests created by this commuter
        self.active_trips = {}  # Currently active trips
        self.trip_history = []  # History of completed trips
        self.transaction_history = []  # History of blockchain transactions
        # Request/trip tracking
        self.active_request_id = None
        self.completed_trips = 0
        self.pending_outgoing_requests = []  # Requests queued until registration confirmed
        
        # Decision-making parameters
        self.utility_coefficients = self._initialize_utility_coefficients()
        self.risk_aversion = self._initialize_risk_aversion()
        self.time_flexibility = self._initialize_time_flexibility()
        self.price_sensitivity = self._initialize_price_sensitivity()
        self.comfort_preference = self._initialize_comfort_preference()
        self.reliability_preference = self._initialize_reliability_preference()
        
        # Learning parameters
        self.market_experience = {}  # Provider ID -> satisfaction level
        self.mode_preference = self._initialize_mode_preference()
        self.strategy_weights = {
            'direct_booking': 0.4,   # Book directly with provider
            'market_purchase': 0.25, # Purchase from NFT marketplace
            'bundled_service': 0.35  # Prefer bundles slightly more to increase encounter rate
        }
        
        # Track requests that need attention
        self.pending_requests = []
        
        # Set up logging
        self.logger = logging.getLogger(f"Commuter-{unique_id}")
        self.logger.setLevel(logging.INFO)
        self.marketplace = blockchain_interface
        # Register with blockchain
        self._register_with_blockchain()

    def _initialize_utility_coefficients(self):
        """Utility coefficients inspired by agent_commuter_03.py"""
        self.vot = {'low': 0.15, 'middle': 0.3, 'high': 0.6}.get(self.income_level, 0.3)
        # Extreme test: drive all demand to Bus/Train by crushing car/bike preference
        base_beta_c = -0.35
        base_beta_t = -0.5
        if self.income_level == 'high':
            beta_cost = -0.005
            beta_time = -1.5
            beta_walk = -3.0
            beta_wait = -3.0
            beta_reliability = 0.7
            asc_car = -1000000.0
        elif self.income_level == 'middle':
            beta_cost = base_beta_c * 1.0
            beta_time = base_beta_t * 1.0
            beta_walk = -1.5
            beta_wait = -2.0
            beta_reliability = 0.5
            asc_car = -1000000.0
        else:  # low
            beta_cost = -2.0
            beta_time = -0.1
            beta_walk = -0.5
            beta_wait = -0.5
            beta_reliability = 0.3
            asc_car = -1000000.0

        # Additional sensitivity: disability/poor health increases walk aversion
        if self.has_disability or self.health_status == 'poor':
            beta_walk = beta_walk * 2.0
        # Increase waiting disutility globally to penalize long waits/bundle transfers
        beta_wait = beta_wait * 1.5

        return {
            # Increase variance to create stronger heterogeneity across agents
            'beta_cost': random.gauss(beta_cost, abs(beta_cost * 0.8)),
            'beta_time': random.gauss(beta_time, abs(beta_time * 0.8)),
            'beta_reliability': beta_reliability,
            'beta_walk': random.gauss(beta_walk, 0.5),
            'beta_wait': random.gauss(beta_wait, 0.5),
            # Strongly heterogeneous car preference: some love cars, some hate them
            'asc_car': random.gauss(asc_car, 0.1),     # extremely negative
            'asc_bike': random.gauss(-1000000.0, 0.1), # extremely negative
            'asc_bus': random.gauss(2000000.0, 0.1),   # even more positive for bus
            'asc_train': random.gauss(2000000.0, 0.1), # even more positive for train
            'asc_bundle': -2.0,                        # discourage bundle vs direct PT
            'asc_nft': 0.0
        }

    def _initialize_risk_aversion(self):
        """
        Initialize risk aversion parameter based on the commuter's attributes.
        
        Returns:
            Float between 0 and 1, higher means more risk-averse
        """
        # Base risk aversion
        risk_aversion = 0.5
        
        # Adjust based on age (older people tend to be more risk-averse)
        if self.age > 60:
            risk_aversion += 0.2
        elif self.age < 30:
            risk_aversion -= 0.1
        
        # Adjust based on income (higher income can afford more risk)
        if self.income_level == 'high':
            risk_aversion -= 0.1
        elif self.income_level == 'low':
            risk_aversion += 0.1
        
        # Adjust based on health status
        if self.health_status == 'poor':
            risk_aversion += 0.15
        
        # Adjust for tech access (less tech access means more risk-averse with digital platforms)
        if not self.tech_access:
            risk_aversion += 0.15
        
        # Add randomness
        risk_aversion += random.uniform(-0.1, 0.1)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, risk_aversion))

    def _initialize_time_flexibility(self):
        """
        Initialize time flexibility parameter based on the commuter's attributes.
        
        Returns:
            Float between 0 and 1, higher means more flexible with time
        """
        # Base time flexibility
        flexibility = 0.5
        
        # Adjust based on age
        if self.age > 60:
            flexibility += 0.2  # Retired, more flexible
        elif 30 <= self.age <= 50:
            flexibility -= 0.2  # Working age, less flexible
        
        # Adjust based on income
        if self.income_level == 'high':
            flexibility -= 0.1  # Higher value of time
        
        # Adjust based on payment scheme
        if self.payment_scheme == 'subscription':
            flexibility += 0.1  # Subscription users might be more flexible
        
        # Add randomness
        flexibility += random.uniform(-0.1, 0.1)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, flexibility))

    def _initialize_price_sensitivity(self):
        """
        Initialize price sensitivity parameter based on the commuter's attributes.
        
        Returns:
            Float between 0 and 1, higher means more sensitive to price
        """
        # Base price sensitivity
        sensitivity = 0.5
        
        # Adjust based on income level
        if self.income_level == 'low':
            sensitivity += 0.3
        elif self.income_level == 'high':
            sensitivity -= 0.3
        
        # Adjust based on payment scheme
        if self.payment_scheme == 'subscription':
            sensitivity -= 0.1  # Subscription users might be less price-sensitive
        
        # Add randomness
        sensitivity += random.uniform(-0.1, 0.1)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, sensitivity))

    def _initialize_comfort_preference(self):
        """
        Initialize comfort preference parameter based on the commuter's attributes.
        
        Returns:
            Float between 0 and 1, higher means more preference for comfort
        """
        # Base comfort preference
        preference = 0.5
        
        # Adjust based on age
        if self.age > 60:
            preference += 0.2
        
        # Adjust based on income level
        if self.income_level == 'high':
            preference += 0.2
        elif self.income_level == 'low':
            preference -= 0.1
        
        # Adjust based on disability and health
        if self.has_disability:
            preference += 0.3
        if self.health_status == 'poor':
            preference += 0.2
        
        # Add randomness
        preference += random.uniform(-0.1, 0.1)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, preference))

    def _initialize_reliability_preference(self):
        """
        Initialize reliability preference parameter based on the commuter's attributes.
        
        Returns:
            Float between 0 and 1, higher means more preference for reliability
        """
        # Base reliability preference
        preference = 0.5
        
        # Adjust based on purpose (would depend on typical travel purposes)
        # Will be adjusted dynamically based on purpose
        
        # Adjust based on tech access
        if not self.tech_access:
            preference += 0.1  # Less tech-savvy users may value reliability more
        
        # Add randomness
        preference += random.uniform(-0.1, 0.1)
        
        # Ensure value is between 0 and 1
        return max(0, min(1, preference))

    def _initialize_mode_preference(self):
        """
        Initialize mode preference based on the commuter's attributes.
        
        Returns:
            Dictionary of mode preferences
        """
        # Base preferences
        preferences = {
            'car': 0.2,
            'bike': 0.2, 
            'bus': 0.2,
            'train': 0.2,
            'walk': 0.2
        }
        
        # Adjust based on age
        if self.age > 60:
            preferences['car'] += 0.1
            preferences['walk'] -= 0.1
        elif self.age < 30:
            preferences['bike'] += 0.1
            preferences['car'] -= 0.05
        
        # Adjust based on disability
        if self.has_disability:
            preferences['car'] += 0.2
            preferences['bike'] -= 0.1
            preferences['walk'] -= 0.1
        
        # Adjust based on health status
        if self.health_status == 'poor':
            preferences['car'] += 0.1
            preferences['walk'] -= 0.1
            preferences['bike'] -= 0.1
        
        # Add randomness
        for mode in preferences:
            preferences[mode] += random.uniform(-0.05, 0.05)
        
        # Normalize preferences
        total = sum(preferences.values())
        for mode in preferences:
            preferences[mode] /= total
        
        return preferences

    def _register_with_blockchain(self):
        """Register the commuter on the blockchain."""
        self.logger.info(f"Registering commuter {self.unique_id} with blockchain")
        success, self.blockchain_address = self.blockchain_interface.register_commuter(self)

        if success:
            self.logger.info(f"Commuter {self.unique_id} registered at address {self.blockchain_address}")
            # Don't create requests until registration is confirmed
            self.registration_confirmed = False

            # Store detailed commuter profile for booking analysis
            profile_data = {
                'commuter_id': self.unique_id,
                'age': self.age,
                'income_level': self.income_level,
                'has_disability': self.has_disability,
                'tech_access': self.tech_access,
                'health_status': self.health_status,
                'payment_scheme': self.payment_scheme,
                'home_location': self.home_location,
                'preferences': self._initialize_mode_preference(),
                'utility_coefficients': {
                    'cost': getattr(self, 'cost_coefficient', 0),
                    'time': getattr(self, 'time_coefficient', 0),
                    'comfort': getattr(self, 'comfort_coefficient', 0),
                    'reliability': getattr(self, 'reliability_coefficient', 0),
                    'environmental': getattr(self, 'environmental_coefficient', 0)
                }
            }
            self.blockchain_interface.store_commuter_profile(self.unique_id, profile_data)
        else:
            self.logger.error(f"Failed to register commuter {self.unique_id} with blockchain")
            self.registration_confirmed = False
            
    def has_active_request(self):
        """Check if the commuter has any active requests"""
        for request_id, request in self.requests.items():
            if request['status'] in ['active', 'seeking_offers', 'service_selected']:
                return True
        return False
    
    def get_personal_requirements(self):
        """
        Get the personal requirements of the commuter.
        
        Returns:
            Dictionary of personal requirements
        """
        requirements = {
            'wheelchair': self.has_disability,
            'assistance': self.has_disability or (self.age > 70),
            'child_seat': False,  # Default, can be updated based on trip purpose
            'pet_friendly': False  # Default, can be updated based on trip purpose
        }
        
        # Could add more complex logic based on commuter attributes
        
        return requirements

    def determine_schedule_flexibility(self, travel_purpose):
        """
        Determine the schedule flexibility based on travel purpose and commuter attributes.
        
        Args:
            travel_purpose: Purpose of travel
            
        Returns:
            String indicating flexibility level
        """
        # Base flexibility based on commuter's time flexibility parameter
        if self.time_flexibility < 0.3:
            base_flexibility = "low"
        elif self.time_flexibility < 0.7:
            base_flexibility = "medium"
        else:
            base_flexibility = "high"
        
        # Adjust based on travel purpose
        if travel_purpose == 'work':
            # Work trips usually have less flexibility
            if base_flexibility == "high":
                return "medium"
            elif base_flexibility == "medium":
                return "low"
            else:
                return "very_low"
        elif travel_purpose == 'medical':
            # Medical appointments usually have less flexibility
            if base_flexibility == "high":
                return "medium"
            elif base_flexibility == "medium":
                return "low"
            else:
                return "very_low"
        elif travel_purpose == 'leisure':
            # Leisure trips usually have more flexibility
            if base_flexibility == "low":
                return "medium"
            elif base_flexibility == "medium":
                return "high"
            else:
                return "very_high"
        
        # Default to base flexibility for other purposes
        return base_flexibility

    def create_request(self, origin, destination, start_time, travel_purpose='work', requirements=None):
        """
        Create a travel request and submit it to the blockchain.
        
        Args:
            origin: Origin coordinates [x, y]
            destination: Destination coordinates [x, y]
            start_time: Start time for the trip
            travel_purpose: Purpose of travel
            requirements: Optional custom requirements
            
        Returns:
            Request ID
        """
        # Check if registration is confirmed
        if not self.blockchain_interface.is_commuter_registered(self.unique_id):
            self.logger.info(f"Commuter {self.unique_id} not yet registered. Queueing request.")
            # Store the request to process later
            if not hasattr(self, 'pending_outgoing_requests'):
                self.pending_outgoing_requests = []
            
            self.pending_outgoing_requests.append({
                'origin': origin,
                'destination': destination,
                'start_time': start_time,
                'travel_purpose': travel_purpose,
                'requirements': requirements,
                'queued_at': self.model.schedule.time
            })
            
            return None  # Return None to indicate request is queued
        # Generate a unique numeric request ID (64-bit)
        request_id = int(uuid.uuid4().int & (2**64 - 1))
        
        # Get personal requirements
        personal_reqs = self.get_personal_requirements()
        if requirements:
            # Override with custom requirements if provided
            for key, value in requirements.items():
                personal_reqs[key] = value
        
        # Determine schedule flexibility
        flexibility = self.determine_schedule_flexibility(travel_purpose)
        
        # Map purpose to enum value (matching blockchain expectations)
        purpose_map = {
            'work': 0,
            'school': 1,
            'shopping': 2,
            'medical': 3,
            'trip': 4,
            'leisure': 6,
            'other': 7
        }
        
        # Use default if purpose not in map
        purpose_value = purpose_map.get(travel_purpose, 7)
        
        # Convert requirements to format expected by blockchain
        requirement_keys = list(personal_reqs.keys())
        requirement_values = [personal_reqs[key] for key in requirement_keys]
        
        # Create request structure
        request = {
            'request_id': request_id,
            'commuter_id': self.unique_id,
            'origin': origin,
            'destination': destination,
            'start_time': start_time,
            'travel_purpose': purpose_value,
            'flexible_time': flexibility,
            'requirement_keys': requirement_keys,
            'requirement_values': requirement_values,
            'status': 'active',
            'blockchain_status': 'pending',  # Track blockchain state
            'created_at': self.model.schedule.time,
            'selected_strategy': None,  # Will be updated when strategy is selected
            'selected_option': None     # Will be updated when option is selected
        }
        
        self.logger.info(f"Creating request {request_id} from {origin} to {destination} at time {start_time}")
        
        # Store request locally
        self.requests[request_id] = request
        self.pending_requests.append(request_id)

        # Store detailed request information for booking analysis
        distance = math.sqrt((destination[0] - origin[0])**2 + (destination[1] - origin[1])**2)
        request_details = {
            'request_id': request_id,
            'commuter_id': self.unique_id,
            'origin': origin,
            'destination': destination,
            'distance': distance,
            'travel_purpose': travel_purpose,
            'start_time': start_time,
            'flexibility': flexibility,
            'requirements': personal_reqs,
            'created_at': self.model.schedule.time
        }
        self.blockchain_interface.store_request_details(request_id, request_details)

        # Create request on blockchain asynchronously
        result = self.blockchain_interface.create_travel_request(self, request)

        self.logger.info(f"Request {request_id} created with blockchain result: {result}")

        return request_id

    def step(self):
        """Main step function - integrated with bundle system"""
        # Register with marketplace if not registered
        if not hasattr(self, 'registered'):
            success, address = self.marketplace.register_commuter(self)
            if success:
                self.registered = True
                self.address = address

        # Critical: maintain state only (no self-initiated demand)
        self._check_trip_completion()
        if self.active_request_id:
            self.check_request_status()
        self._process_pending_requests()

    def _check_trip_completion(self):
        """
        Safely delegate to active-trip updater.
        """
        self._update_active_trips()

    def _attempt_decentralized_trip(self):
        """
        Decentralized client-side routing + purchase using available offers/listings.
        """
        try:
            origin = list(self.location) if isinstance(self.location, (list, tuple)) else [0, 0]
            destination = self._generate_destination(origin)
            segments = self.blockchain_interface.get_all_available_segments()
            bundles = self.blockchain_interface.build_bundles(
                origin=origin,
                destination=destination,
                start_time=int(self.model.schedule.time),
                max_transfers=4,
                time_tolerance=20,
                segments_override=segments
            )
            if not bundles:
                return False

            choice = bundles[0]
            self.logger.info(f"Decentralized choice: bundle {choice.get('bundle_id')} with {len(choice.get('segments', []))} segments")

            # Derive trip timing from bundle segments
            segment_starts = [s.get('depart_time') or s.get('start_time') for s in choice.get('segments', []) if s.get('depart_time') or s.get('start_time')]
            start_time = min(segment_starts) if segment_starts else self.model.schedule.time
            # If per-segment durations exist, use sum; else fallback to bundle total_duration
            seg_durations = [s.get('estimated_time') or s.get('duration') for s in choice.get('segments', []) if s.get('estimated_time') or s.get('duration')]
            total_duration = sum(seg_durations) if seg_durations else choice.get('total_duration', 30)
            end_time = start_time + total_duration

            for seg in choice.get('segments', []):
                seg_type = seg.get('type')
                if seg_type in ['offer', 'segment']:
                    offer_id = seg.get('offer_id') or seg.get('segment_id', '').replace('offer_', '')
                    success, nft_id = self.blockchain_interface.mint_and_buy(
                        offer_id,
                        self.unique_id,
                        start_time=start_time,
                        duration=seg.get('estimated_time') or seg.get('duration') or total_duration,
                        source_override='jit_mint'
                    )
                    if not success:
                        return False
                    self.owned_nfts[nft_id] = seg
                elif seg_type in ['listing', 'nft']:
                    nft_id = seg.get('nft_id')
                    if not self.blockchain_interface.buy_secondary_nft(nft_id, self.unique_id):
                        return False
                    self.owned_nfts[nft_id] = seg

            # Lock trip in progress to avoid immediate re-booking
            self.active_trips['jit_trip'] = {
                'status': 'in_progress',
                'start_time': start_time,
                'end_time': end_time,
                'option': choice,
                'request': {'origin': origin, 'destination': destination}
            }
            if hasattr(self.model, "log_booking"):
                modes = choice.get('modes', ['bundle'])
                mode_val = modes[0] if modes else choice.get('mode') or 'bundle'
                mode_detailed = "_".join(modes) if modes else (choice.get('mode') or "bundle")
                self.model.log_booking(
                    tick=self.model.schedule.time,
                    request_id=f"jit_bundle_{self.unique_id}",
                    commuter_id=self.unique_id,
                    provider_id=choice.get('provider_id'),
                    mode=mode_val,
                    price=choice.get('total_price', 0),
                    duration=total_duration,
                    is_bundle=True,
                    mode_detailed=mode_detailed,
                    start_time=start_time,
                    end_tick=end_time
                )
            self.logger.info(f"🚀 Trip Started! Locked for {total_duration} ticks (start {start_time}).")
            return True
        except Exception as e:
            self.logger.warning(f"Decentralized trip attempt failed: {e}")
            return False

    def create_travel_request(self):
        """Create a simple travel request using current location and a random destination."""
        origin = list(self.location) if isinstance(self.location, (list, tuple)) else [0, 0]
        destination = self._generate_destination(origin)
        # Use simulation time to stay consistent with utility computations
        # Allow booking further in the future to create a resale window
        start_time = int(self.model.schedule.time + random.randint(20, 100))
        req_id = self.create_request(origin, destination, start_time, travel_purpose='work')
        if req_id:
            self.active_request_id = req_id
        return req_id

    def create_travel_request_with_bundles(self):
        """
        Create a travel request and attempt to find bundle options using the decentralized router.
        This is the NEW integrated method that uses the bundle system.
        """
        # Generate origin and destination
        origin = list(self.location) if isinstance(self.location, (list, tuple)) else [0, 0]
        destination = self._generate_destination(origin)
        # Allow booking further in the future to create a resale window
        start_time = int(self.model.schedule.time + random.randint(20, 100))

        # Create the request
        req_id = self.create_request(origin, destination, start_time, travel_purpose='work')
        if not req_id:
            return None

        self.active_request_id = req_id

        # NEW: Use decentralized bundle router to find multi-modal options
        try:
            # Get active segments from blockchain (decentralized discovery)
            active_segments = self.marketplace.get_active_segments()

            if active_segments:
                self.logger.info(f"Found {len(active_segments)} active segments for bundle routing")

            # Build bundle options using decentralized routing
            bundle_options = self.marketplace.build_bundles(
                origin=origin,
                destination=destination,
                start_time=start_time,
                max_transfers=4,  # Allow up to 4 segments (3 transfers)
                time_tolerance=20  # 20 ticks tolerance for better matching
            )

            if bundle_options:
                self.logger.info(f"Found {len(bundle_options)} bundle options for request {req_id}")

                # Select best bundle based on utility
                best_bundle = bundle_options[0]  # Already sorted by utility score

                # Store bundle options for this request
                if not hasattr(self, 'bundle_options'):
                    self.bundle_options = {}
                self.bundle_options[req_id] = bundle_options

                # Attempt to reserve the best bundle
                success, reservation_id = self.marketplace.reserve_bundle(
                    commuter_id=self.unique_id,
                    request_id=req_id,
                    bundle=best_bundle
                )

                if success:
                    self.logger.info(f"Successfully reserved bundle {best_bundle.get('bundle_id')} "
                                   f"with reservation ID: {reservation_id}")
                    self.logger.info(f"Bundle details: {best_bundle.get('num_segments')} segments, "
                                   f"${best_bundle.get('total_price'):.2f}, "
                                   f"discount: ${best_bundle.get('bundle_discount', 0):.2f}")

                    # Store reservation info
                    if not hasattr(self, 'bundle_reservations'):
                        self.bundle_reservations = {}
                    self.bundle_reservations[req_id] = {
                        'reservation_id': reservation_id,
                        'bundle': best_bundle,
                        'timestamp': self.model.schedule.time
                    }
                else:
                    self.logger.warning(f"Failed to reserve bundle for request {req_id}")
                    # Fall back to triggering direct segment minting
                    self._trigger_direct_segment_minting(req_id, origin, destination, start_time)
            else:
                self.logger.info(f"No bundle options found for request {req_id}")
                # Trigger direct segment minting for unmatched request
                self._trigger_direct_segment_minting(req_id, origin, destination, start_time)

        except Exception as e:
            self.logger.error(f"Error in bundle routing: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to old behavior
            pass

        return req_id

    def _trigger_direct_segment_minting(self, req_id, origin, destination, start_time):
        """
        Trigger direct segment minting when no bundles are available.
        This broadcasts the request to providers who can mint segments.
        """
        request_data = {
            'request_id': req_id,
            'origin': origin,
            'destination': destination,
            'start_time': start_time,
            'max_price': self._calculate_max_price()
        }

        success = self.marketplace.mint_direct_segment_for(request_data)

        if success:
            self.logger.info(f"Broadcasted unmatched request {req_id} to providers for direct segment minting")
        else:
            self.logger.warning(f"Failed to broadcast request {req_id} for direct segment minting")

    def check_request_status(self):
        """Check marketplace for match on the active request and finalize locally."""
        rid = self.active_request_id
        if not rid:
            return

        # Check if matched
        match = self.marketplace.marketplace_db['matches'].get(rid)
        
        if match:
            # Ensure the commuter receives an NFT representing the trip
            offer_id = match.get('winning_offer_id')
            offer = self.marketplace.marketplace_db['offers'].get(offer_id, {})
            request = self.requests.get(rid, {})

            nft_id = f"nft_{rid}_{self.unique_id}"
            service_time = request.get('start_time', self.model.schedule.time + 50)

            nft_details = {
                'nft_id': nft_id,
                'request_id': rid,
                'price': match.get('final_price', 10.0),
                'service_time': service_time,
                'duration': offer.get('estimated_time', 30),
                'provider_id': match.get('provider_id'),
                'mode': offer.get('mode', 'car'),
                'status': 'active',
                'purchase_time': self.model.schedule.time
            }

            # Store in commuter wallet
            self.owned_nfts[nft_id] = nft_details

            # Sync ownership to marketplace DB
            try:
                lock = getattr(self.marketplace, 'marketplace_db_lock', None)
                acquired = False
                if lock:
                    lock.acquire()
                    acquired = True
                if 'nfts' not in self.marketplace.marketplace_db:
                    self.marketplace.marketplace_db['nfts'] = {}
                self.marketplace.marketplace_db['nfts'][nft_id] = {
                    'owner_id': self.unique_id,
                    'status': 'active',
                    'details': nft_details
                }
            finally:
                if lock and acquired:
                    lock.release()

            self.logger.info(f"✅ Trip Matched & NFT Minted: {nft_id}")

            # Track the booked trip
            self.active_trips[rid] = {
                'status': 'booked',
                'start_time': service_time,
                'option': offer,
                'request': request
            }

            # Log booking for downstream analysis
            if hasattr(self.model, "log_booking"):
                end_time = service_time + offer.get('estimated_time', 30)
                offer_id_str = str(offer.get('offer_id') or offer.get('segment_id') or "")
                mode_val = offer.get('mode') or offer.get('provider_type')
                if not mode_val:
                    upper_id = offer_id_str.upper()
                    if "BUS" in upper_id:
                        mode_val = "bus"
                    elif "TRAIN" in upper_id:
                        mode_val = "train"
                mode_val = mode_val or "unknown"
                self.model.log_booking(
                    tick=self.model.schedule.time,
                    start_time=service_time,
                    end_tick=end_time,
                    request_id=rid,
                    commuter_id=self.unique_id,
                    provider_id=offer.get('provider_id'),
                    mode=mode_val,
                    price=match.get('final_price', 0),
                    duration=offer.get('estimated_time', 30),
                    is_bundle=False,
                    mode_detailed=mode_val
                )

            # Clear active request to allow new ones
            self.active_request_id = None
        else:
            # Timeout and retry if request has been waiting too long
            request = self.requests.get(rid)
            if request and (self.model.current_step - request.get('created_at', 0) > 5):
                self.logger.info(f"Request {rid} timed out. Retrying...")
                self.active_request_id = None  # drop and allow retry


    def calculate_option_utility(self, option, request_id):
        request = self.requests[request_id]
        coeffs = self.utility_coefficients

        cost = option.get('price', 0)
        mode = option.get('mode', 'car')
        # Estimate walk/wait/ride times (prefer router-provided values)
        if option.get('type') == 'bundle':
            ride_time = option.get('in_vehicle_time', option.get('total_duration', 0))
            walk_time = option.get('walk_time', 5)   # reduce walk penalty defaults
            wait_time = option.get('wait_time', 3)   # reduce wait penalty defaults
        elif mode in ['car', 'bike', 'taxi']:
            ride_time = option.get('duration') or option.get('time', 0)
            walk_time = 0.5  # minimal walk out the door
            wait_time = random.uniform(1, 3)  # quick dispatch
        else:
            ride_time = option.get('in_vehicle_time', option.get('duration', option.get('time', 0)))
            walk_time = option.get('walk_time', 15)
            wait_time = option.get('wait_time', 10)

        origin = option.get('origin') or request.get('origin')
        dest = option.get('dest') or request.get('destination')

        # Apply congestion for car; other modes use base time
        if hasattr(self.model, "calculate_bpr_time") and mode == 'car':
            real_time = self.model.calculate_bpr_time(origin, dest, ride_time)
        else:
            real_time = ride_time

        reliability = option.get('reliability', 1.0)

        beta_walk = coeffs.get('beta_walk', coeffs['beta_time'] * 2.0)
        beta_wait = coeffs.get('beta_wait', coeffs['beta_time'] * 1.5)

        # Urgency adjustment: high urgency -> time matters more, cost matters less
        urgency_factor = 1.0 + self.current_urgency * 2.0  # 1.0 ~ 3.0
        effective_beta_time = coeffs['beta_time'] * urgency_factor
        effective_beta_cost = coeffs['beta_cost'] / max(0.5, urgency_factor)
        effective_beta_wait = beta_wait * urgency_factor

        asc = coeffs.get(f"asc_{mode}", 0)
        utility = (
            asc +
            effective_beta_cost * cost +
            effective_beta_time * real_time +
            beta_walk * walk_time +
            effective_beta_wait * wait_time +
            coeffs['beta_reliability'] * reliability
        )

        # Add random unobserved preference shock to diversify choices
        utility += random.gauss(0, 1.0)

        # Speculative boost for deeply discounted NFTs
        if option.get('type') == 'nft_market':
            original = option.get('original_price', cost)
            if original > 0:
                discount = 1 - (cost / original)
                if discount > 0.5:
                    utility += 5.0

        return utility

    def _calculate_max_price(self, request=None):
        """
        Calculate the maximum price the commuter is willing to pay.
        
        Args:
            request: Optional request to calculate max price for
            
        Returns:
            Maximum price
        """
        # Base price depends on income level
        if self.income_level == 'low':
            base_max = 50
        elif self.income_level == 'middle':
            base_max = 100
        else:  # high
            base_max = 200
        
        # Adjust based on trip distance if request provided
        if request:
            origin = request['origin']
            destination = request['destination']
            distance = math.sqrt((destination[0] - origin[0])**2 + (destination[1] - origin[1])**2)
            
            # Simple linear adjustment based on distance
            distance_factor = 1 + (distance / 100)  # Adjust scale as needed
            base_max *= distance_factor
        
        # Adjust based on purpose if provided
        if request and 'travel_purpose' in request:
            purpose = request['travel_purpose']
            
            # Business/work trips might have higher willingness to pay
            if purpose == 0:  # work
                base_max *= 1.2
            # Medical trips might have higher urgency
            elif purpose == 3:  # medical
                base_max *= 1.3
        
        # Adjust based on time flexibility
        if request and 'flexible_time' in request:
            if request['flexible_time'] == 'low':
                base_max *= 1.2  # Less flexible = willing to pay more
            elif request['flexible_time'] == 'high':
                base_max *= 0.8  # More flexible = willing to pay less
        
        # Add some randomness
        base_max *= random.uniform(0.9, 1.1)

        # Peak willingness to pay: during peak windows, commuters may pay much more
        current_time = getattr(self.model, "current_step", 0)
        if 30 <= (current_time % 144) <= 90:
            base_max *= 5.0  # desperation multiplier to accept secondary premiums
        
        return base_max
    

    def evaluate_bundle_options(self, bundle_id):
        """
        Evaluate different bundle options.
        
        Args:
            bundle_id: Bundle request ID
            
        Returns:
            List of (utility, option) tuples, sorted by utility
        """
        if not hasattr(self, 'bundle_requests') or bundle_id not in self.bundle_requests:
            self.logger.error(f"Bundle request {bundle_id} not found")
            return []
        
        bundle_request = self.bundle_requests[bundle_id]
        
        # Generate all possible combinations of offers
        bundle_options = []
        
        # This is a simplified approach - in a full implementation, 
        # you would need to handle combinatorial complexity with heuristics
        
        # For each segment, select the best offer based on utility
        selected_offers = {}
        
        for segment_id, offers in bundle_request['components'].items():
            best_offer = None
            best_utility = float('-inf')
            
            for offer in offers:
                # Calculate utility for this offer
                utility = self._calculate_bundle_offer_utility(offer, segment_id)
                
                if utility > best_utility:
                    best_utility = utility
                    best_offer = offer
            
            if best_offer:
                selected_offers[segment_id] = best_offer
        
        # Check if we have offers for all segments
        if len(selected_offers) == len(bundle_request['segments']):
            # Calculate total price and utility
            total_price = sum(offer['price'] for offer in selected_offers.values())
            
            # Apply bundle discount
            discounted_price = total_price * 0.95  # 5% discount for the whole bundle
            
            total_utility = sum(self._calculate_bundle_offer_utility(offer, segment_id) 
                            for segment_id, offer in selected_offers.items())
            
            # Create bundle option
            bundle_option = {
                'bundle_id': bundle_id,
                'selected_offers': selected_offers,
                'total_price': discounted_price,
                'total_utility': total_utility,
                'components': {
                    segment_id: {
                        'provider_id': offer['provider_id'],
                        'price': offer['price'],
                        'start_time': offer['start_time'],
                        'duration': offer['estimated_time'],
                        'route': offer['route'],
                        'mode': offer['mode'],
                        'offer_signature': offer.get('signature')
                    }
                    for segment_id, offer in selected_offers.items()
                }
            }
            
            bundle_options.append((total_utility, bundle_option))
        
        # Sort by utility (highest first)
        bundle_options.sort(reverse=True, key=lambda x: x[0])
        
        return bundle_options

    def _calculate_bundle_offer_utility(self, offer, segment_id):
        """
        Calculate utility of a bundle component offer.
        
        Args:
            offer: Offer for a bundle component
            segment_id: Segment ID
            
        Returns:
            Utility value
        """
        # Extract offer details
        price = offer['price']
        duration = offer['estimated_time']
        mode = offer['mode']
        reliability = offer.get('reliability', 0.7)
        comfort = offer.get('quality_score', 70) / 100
        
        # Basic utility calculation
        price_utility = self.utility_coefficients['price'] * price * self.price_sensitivity
        time_utility = self.utility_coefficients['time'] * duration
        comfort_utility = self.utility_coefficients['comfort'] * comfort * self.comfort_preference
        reliability_utility = self.utility_coefficients['reliability'] * reliability * self.reliability_preference
        
        # Mode preference
        mode_utility = 0
        if mode in self.mode_preference:
            mode_utility = self.mode_preference[mode] * 0.5
        
        # Calculate total utility
        total_utility = (
            price_utility + 
            time_utility + 
            comfort_utility + 
            reliability_utility + 
            mode_utility
        )
        
        # Small random component for variety
        total_utility += random.uniform(-0.05, 0.05)
        
        return total_utility

    def purchase_bundle(self, bundle_id):
        """
        Purchase a selected bundle.
        
        Args:
            bundle_id: Bundle ID to purchase
            
        Returns:
            Success status
        """
        if not hasattr(self, 'bundle_requests') or bundle_id not in self.bundle_requests:
            self.logger.error(f"Bundle request {bundle_id} not found")
            return False
        
        bundle_request = self.bundle_requests[bundle_id]
        
        # Get bundle options
        bundle_options = self.evaluate_bundle_options(bundle_id)
        
        if not bundle_options:
            self.logger.error(f"No viable options for bundle {bundle_id}")
            return False
        
        # Select best option
        best_utility, best_option = bundle_options[0]
        
        # Execute bundle purchase via blockchain
        success, bundle_id = self.blockchain_interface.execute_bundle_purchase(
            best_option, self.unique_id)
        
        if success:
            self.logger.info(f"Successfully purchased bundle {bundle_id}")
            
            # Update bundle status
            bundle_request['status'] = 'purchased'

            # Mint a tradable NFT representing this bundle purchase
            component_data = best_option.get('components', {})
            start_times = [comp.get('start_time') for comp in component_data.values() if comp.get('start_time') is not None]
            service_time = min(start_times) if start_times else self.model.schedule.time
            total_duration = sum(comp.get('duration', 0) for comp in component_data.values())

            representative_provider = next((comp.get('provider_id') for comp in component_data.values() if comp.get('provider_id') is not None), 0)
            representative_mode = next((comp.get('mode') for comp in component_data.values() if comp.get('mode')), 'bundle')

            combined_route = []
            for comp in component_data.values():
                route = comp.get('route', [])
                if route:
                    if combined_route and combined_route[-1] == route[0]:
                        combined_route.extend(route[1:])
                    else:
                        combined_route.extend(route)

            bundle_nft_id = f"bundle_nft_{bundle_id}_{self.unique_id}"
            bundle_nft_details = {
                'request_id': bundle_request.get('request_id', bundle_id),
                'price': best_option.get('total_price', 0),
                'service_time': service_time,
                'duration': total_duration,
                'provider_id': representative_provider,
                'mode': representative_mode,
                'route': combined_route,
                'status': 'active',
                'purchase_time': self.model.schedule.time,
                'valid_until': service_time,
                'components': component_data
            }
            self.owned_nfts[bundle_nft_id] = bundle_nft_details

            try:
                with self.marketplace.marketplace_db_lock:
                    self.marketplace.marketplace_db.setdefault('nfts', {})[bundle_nft_id] = {
                        'owner_id': self.unique_id,
                        'status': 'active',
                        'details': bundle_nft_details
                    }
            except Exception:
                self.logger.debug(f"Could not register bundle NFT {bundle_nft_id} in marketplace DB")

            self.logger.info(f"Minted bundle NFT {bundle_nft_id} for commuter {self.unique_id}")
            
            # Add bundle to active trips
            if not hasattr(self, 'active_bundles'):
                self.active_bundles = {}
            
            self.active_bundles[bundle_id] = {
                'bundle_id': bundle_id,
                'components': best_option['components'],
                'total_price': best_option['total_price'],
                'purchase_time': self.model.schedule.time,
                'status': 'active',
                'nft_id': bundle_nft_id
            }
            
            return True
        else:
            self.logger.error(f"Failed to purchase bundle {bundle_id}")
            return False

    def select_and_purchase_option(self, ranked_options, request_id, strategy=None):
        """
        Select and purchase the best mobility option.
        
        Args:
            request_id: The request ID
            strategy: Optional strategy to use ('direct_booking', 'market_purchase', 'bundled_service')
            
        Returns:
            True if successful, False otherwise
        """
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False
        
        # Select strategy if not provided based on weights
        if not strategy:
            strategies = list(self.strategy_weights.keys())
            weights = [self.strategy_weights[s] for s in strategies]
            strategy = random.choices(strategies, weights=weights, k=1)[0]
        
        self.logger.info(f"Using strategy: {strategy} for request {request_id}")
        self.requests[request_id]['selected_strategy'] = strategy
        
        if not ranked_options:
            self.logger.warning(f"No options found for request {request_id}")
            return False
        
        # Filter options based on strategy
        filtered_options = []
        if strategy == 'direct_booking':
            filtered_options = [(u, opt) for u, opt in ranked_options if opt['type'] == 'direct_booking']
        elif strategy == 'market_purchase':
            filtered_options = [(u, opt) for u, opt in ranked_options if opt['type'] == 'nft_market']
        elif strategy == 'bundled_service':
            # For bundled service, we would need to get bundle options
            # This is a placeholder - implementation would depend on how bundles are represented
            # For now, just use all options
            filtered_options = ranked_options
        
        # If no options match the strategy, fall back to all options
        if not filtered_options:
            self.logger.warning(f"No options match strategy {strategy}, using all options")
            filtered_options = ranked_options
        
        # Select best option (highest utility)
        best_utility, best_option = filtered_options[0]
        
        self.logger.info(f"Selected option: {best_option['type']} with utility {best_utility}")
        self.requests[request_id]['selected_option'] = best_option
        
        # Execute purchase based on option type
        success = False
        if best_option['type'] == 'direct_booking':
            # Call the appropriate provider method to book directly
            for provider in self.model.schedule.agents:
                if provider.unique_id == best_option['provider_id'] and hasattr(provider, 'accept_booking'):
                    success = provider.accept_booking(
                        self.unique_id,
                        request_id,
                        best_option['price'],
                        best_option.get('departure_time', self.requests[request_id]['start_time']),
                        best_option.get('route', [])
                    )
                    break
        elif best_option['type'] == 'nft_market':
            # Purchase from NFT marketplace
            success = self.blockchain_interface.purchase_nft(best_option['nft_id'], self.unique_id)
            
            if success:
                # Record the NFT as owned
                self.owned_nfts[best_option['nft_id']] = {
                    'request_id': request_id,
                    'price': best_option['price'],
                    'service_time': best_option.get('service_time', self.requests[request_id]['start_time']),
                    'duration': best_option.get('time', 0),
                    'provider_id': best_option.get('provider_id', 0),
                    'mode': best_option.get('mode', 'unknown'),
                    'route': best_option.get('route', []),
                    'status': 'active',
                    'purchase_time': self.model.schedule.time
                }
        
        # Update request status
        if success:
            self.requests[request_id]['status'] = 'service_selected'
            self.requests[request_id]['blockchain_status'] = 'confirmed'

            # If the booking was direct (not bought from the market), mint a tradable NFT for resale
            if best_option['type'] == 'direct_booking':
                dummy_nft_id = f"nft_{request_id}_{self.unique_id}"
                departure_time = best_option.get('departure_time', self.requests[request_id]['start_time'])
                nft_details = {
                    'request_id': request_id,
                    'price': best_option['price'],
                    'service_time': departure_time,
                    'duration': best_option.get('time', 0),
                    'provider_id': best_option.get('provider_id', 0),
                    'mode': best_option.get('mode', 'unknown'),
                    'route': best_option.get('route', []),
                    'status': 'active',
                    'purchase_time': self.model.schedule.time,
                    'valid_until': departure_time
                }
                self.owned_nfts[dummy_nft_id] = nft_details

                # Mirror ownership in the marketplace DB so listings have the right owner
                try:
                    with self.marketplace.marketplace_db_lock:
                        self.marketplace.marketplace_db.setdefault('nfts', {})[dummy_nft_id] = {
                            'owner_id': self.unique_id,
                            'status': 'active',
                            'details': nft_details
                        }
                except Exception:
                    self.logger.debug(f"Could not register minted NFT {dummy_nft_id} in marketplace DB")

                self.logger.info(f"Minted NFT {dummy_nft_id} for booked trip {request_id}")
            
            # Add to active trips
            self.active_trips[request_id] = {
                'request': self.requests[request_id],
                'option': best_option,
                'start_time': best_option.get('departure_time', self.requests[request_id]['start_time']),
                'status': 'booked'
            }
            
            # Remove from pending requests
            if request_id in self.pending_requests:
                self.pending_requests.remove(request_id)
            
            # Update experience with this provider
            provider_id = best_option.get('provider_id', None)
            if provider_id:
                if provider_id not in self.market_experience:
                    self.market_experience[provider_id] = 0
                # Small positive update for successful booking
                self.market_experience[provider_id] += 0.05
            
            self.logger.info(f"Successfully purchased option for request {request_id}")
        else:
            self.logger.warning(f"Failed to purchase option for request {request_id}")
        
        return success

    def evaluate_owned_nfts_for_resale(self):
        """
        Evaluate each owned NFT to decide whether to keep or sell.
        """
        current_time = self.model.schedule.time
        
        # Evaluate each owned NFT
        for nft_id, nft_details in list(self.owned_nfts.items()):
            # Skip if service already used or sold
            if nft_details['status'] != 'active':
                continue
            
            # Skip if service time has passed
            if nft_details['service_time'] < current_time:
                # Mark as expired
                nft_details['status'] = 'expired'
                self.logger.info(f"NFT {nft_id} has expired")
                continue
            
            # Calculate continued utility value (CUV)
            cuv = self._calculate_continued_utility(nft_id)
            
            # Estimate current market value
            market_value = self._estimate_market_value(nft_id)
            
            # Lower threshold to encourage resale during simulations
            threshold = 0.05
            sudden_need_to_sell = random.random() < 0.05
            
            self.logger.debug(f"NFT {nft_id} - CUV: {cuv}, Market value: {market_value}")
            
            # If market value exceeds utility by threshold or an urgent sale is triggered
            if market_value > cuv * (1 + threshold) or sudden_need_to_sell:
                # Calculate optimal listing price
                listing_price = market_value * 0.95  # Slight discount for quicker sale
                
                # Decide on dynamic pricing parameters
                time_to_service = nft_details['service_time'] - current_time
                
                # Longer time to service = more aggressive price decay
                if time_to_service > 24 * 3600:  # More than 24 hours
                    decay_rate = 0.1  # Faster decay
                    min_price = cuv * 0.8  # Lower minimum price
                else:
                    decay_rate = 0.05  # Slower decay
                    min_price = cuv * 0.9  # Higher minimum price
                
                # List for sale with dynamic pricing
                time_parameters = {
                    'initial_price': listing_price,
                    'final_price': min_price,
                    'decay_duration': int(time_to_service * 0.7),  # Use 70% of remaining time
                    'decay_rate': decay_rate
                }
                
                success = self.blockchain_interface.list_nft_for_sale(nft_id, listing_price, time_parameters)
                
                if success:
                    # Update NFT status
                    nft_details['status'] = 'listed'
                    self.logger.info(f"Listed NFT {nft_id} for sale at {listing_price}")
                else:
                    self.logger.warning(f"Failed to list NFT {nft_id} for sale")

    def _calculate_continued_utility(self, nft_id):
        """
        Calculate the utility of keeping and using the NFT.
        
        Args:
            nft_id: The NFT ID
            
        Returns:
            Utility value
        """
        nft = self.owned_nfts[nft_id]
        current_time = self.model.schedule.time
        price_weight = self.utility_coefficients.get('price', 0.1)
        time_weight = self.utility_coefficients.get('time', 0.05)
        
        # Base utility calculation
        base_utility = -1 * (
            price_weight * nft.get('price', 0) +
            time_weight * nft.get('duration', 0)
        )
        
        # Adjust for time proximity
        time_to_service = nft['service_time'] - current_time
        
        # If service time is very close, utility increases (harder to replace)
        if time_to_service < 3600:  # Within 1 hour
            urgency_factor = 2.0 - (time_to_service / 3600)  # From 1.0 to 2.0
            base_utility *= urgency_factor
        # If somewhat close, still increase utility
        elif time_to_service < 24 * 3600:  # Within 24 hours
            urgency_factor = 1.0 + (24 * 3600 - time_to_service) / (24 * 3600)
            base_utility *= urgency_factor
        # If very far in future, utility might decrease (easier to replace)
        elif time_to_service > 7 * 24 * 3600:  # More than 7 days away
            flexibility_factor = 0.8
            base_utility *= flexibility_factor
        
        # Adjust for upcoming needs
        # Check if we have upcoming requests that might need this service
        for req_id, req in self.requests.items():
            if req['status'] == 'active' and req_id != nft.get('request_id'):
                req_origin = req['origin']
                req_dest = req['destination']
                req_time = req['start_time']
                
                # Check if NFT route is similar
                route_match = False
                nft_route = nft.get('route', [])
                
                if nft_route:
                    # Simple check: does route start near request origin and end near request destination?
                    if (len(nft_route) >= 2 and
                        self._calculate_distance(nft_route[0], req_origin) < 10 and
                        self._calculate_distance(nft_route[-1], req_dest) < 10):
                        route_match = True
                
                # Check if time is close
                time_match = abs(nft['service_time'] - req_time) < 3600  # Within 1 hour
                
                if route_match and time_match:
                    # This NFT could be useful for an upcoming request
                    base_utility *= 1.5
                    break
        
        return base_utility

    def _estimate_market_value(self, nft_id):
        """
        Estimate the current market value of an NFT.
        
        Args:
            nft_id: The NFT ID
            
        Returns:
            Estimated market value
        """
        nft = self.owned_nfts[nft_id]
        current_time = self.model.schedule.time
        
        # Original price as baseline
        base_price = nft['price']
        
        # Time-based adjustment
        time_to_service = nft['service_time'] - current_time
        
        if time_to_service < 3600:  # Within 1 hour
            # Price drops rapidly near service time (less than 20% of original value)
            time_factor = max(0.2, time_to_service / 3600)
        elif time_to_service < 24 * 3600:  # Within 24 hours
            # Linear decrease from 80% to 60% value
            time_factor = 0.6 + (0.2 * time_to_service / (24 * 3600))
        elif time_to_service < 7 * 24 * 3600:  # Within 7 days
            # Stable pricing in medium range (80% of value)
            time_factor = 0.8
        else:  # Far future
            # Premium for advance booking (up to 120% of value)
            time_factor = min(1.2, 0.8 + (time_to_service - 7 * 24 * 3600) / (30 * 24 * 3600))
        
        # Market demand adjustment based on similar recent transactions
        # For simplicity, use a random factor, but in a real implementation,
        # would check actual market demand
        demand_factor = random.uniform(0.9, 1.1)
        
        estimated_value = base_price * time_factor * demand_factor
        
        return estimated_value

    def update(self):
        """
        Main update method called on each simulation step.
        """
        # Process pending blockchain operations
        self._update_request_status()
        
        # Process active trips
        self._update_active_trips()
        
        # Evaluate owned NFTs for potential resale
        self.evaluate_owned_nfts_for_resale()

        # Sudden shock: occasionally force a preference shift that triggers resale
        # This simulates unexpected schedule changes that push commuters to offload holdings.
        if random.random() < 0.1:
            self._trigger_sudden_resale_event()
        
        # Check pending requests and take action if needed
        self._process_pending_requests()        
        
        # Generate new trips if needed (optional, based on model design)
        self._generate_new_trips()

        # Exogenous shock forcing resale (more realistic, rarer)
        if random.random() < 0.05:
            self._handle_exogenous_shock()

    def _trigger_sudden_resale_event(self):
        """
        Force a quick resale attempt for all active NFTs to create secondary market volume.
        """
        current_time = self.model.schedule.time
        for nft_id, nft_details in list(self.owned_nfts.items()):
            if nft_details.get('status') != 'active':
                continue

            # Steepen risk aversion temporarily to encourage sale
            self.risk_aversion = min(1.0, self.risk_aversion + 0.3)

            # Discount the estimated market value to move inventory fast
            market_value = self._estimate_market_value(nft_id)
            listing_price = max(1.0, market_value * random.uniform(0.6, 0.85))

            time_to_service = nft_details.get('service_time', current_time) - current_time
            time_parameters = {
                'initial_price': listing_price,
                'final_price': max(0.5, listing_price * 0.7),
                'decay_duration': max(1, int(time_to_service * 0.7))
            }

            success = self.blockchain_interface.list_nft_for_sale(nft_id, listing_price, time_parameters)
            if success:
                nft_details['status'] = 'listed'
                self.logger.info(f"Sudden event: listed NFT {nft_id} at {listing_price}")

    def _handle_exogenous_shock(self):
        """Handle life-event shocks that trigger fire-sale listings."""
        if not self.owned_nfts:
            return
        current_time = self.model.schedule.time
        for nft_id, nft in list(self.owned_nfts.items()):
            if nft.get('status') != 'active':
                continue
            if nft.get('service_time', 0) <= current_time:
                continue
            fire_price = nft.get('price', 1.0) * 0.6
            time_params = {
                'initial_price': fire_price,
                'final_price': 0.0,
                'decay_rate': 0.05,
                'decay_duration': 20
            }
            success = self.blockchain_interface.list_nft_for_sale(nft_id, fire_price, time_params)
            if success:
                nft['status'] = 'listed'
                self.logger.info(f"⚠️ Exogenous shock: dumping {nft_id} at {fire_price}")

    def _check_speculative_opportunities(self):
        """Risk-seeking commuters grab cheap nearby listings."""
        # More conservative risk appetite: only lower risk aversion commuters speculate
        if self.risk_aversion >= 0.4:
            return False
        try:
            listings = list(self.marketplace.marketplace_db.get('listings', {}).values())
        except Exception:
            listings = []
        if not listings:
            return False
        for listing in listings:
            details = listing.get('details', {})
            dest = details.get('destination') or details.get('dest') or details.get('destination', [0, 0])
            dist_to_cbd = 0
            if hasattr(self.model, 'hubs') and 'CBD' in getattr(self.model, 'hubs', {}):
                dist_to_cbd = self._calculate_distance(dest, self.model.hubs['CBD'])
            price = listing.get('current_price', listing.get('price', 1e9))
            is_affordable = price < 25.0
            is_strategic = dist_to_cbd <= 10
            if is_strategic and is_affordable:
                self.logger.info(f"🤑 Speculative buy by {self.unique_id} for listing {listing.get('listing_id')} @ ${price:.2f}")
                if self.marketplace.purchase_nft(listing.get('nft_id', listing.get('token_id', '')), self.unique_id):
                    return True
        return False

    def _update_request_status(self):
        """
        Update local status based on blockchain status.
        """
        for request_id, request in self.requests.items():
            status = request.get('blockchain_status', 'pending')
            request['blockchain_status'] = status  # ensure key exists
            if status == 'pending':
                # Check blockchain status
                updated_status = self.blockchain_interface.check_request_status(request_id)
                if updated_status:
                    request['blockchain_status'] = updated_status
                    self.logger.info(f"Request {request_id} blockchain status updated to {updated_status}")

    def _update_active_trips(self):
        """
        Check active trips and transition statuses; release provider capacity and log completion.
        """
        current_time = self.model.schedule.time

        for trip_id, trip in list(self.active_trips.items()):
            if trip.get('status') == 'completed':
                continue

            # Booked -> in_progress
            if trip.get('status') == 'booked' and current_time >= trip.get('start_time', 0):
                trip['status'] = 'in_progress'
                self.logger.info(f"Trip {trip_id} is now in progress")

            if trip.get('status') == 'in_progress':
                option = trip.get('option', {})
                duration = option.get('time', option.get('duration', 30))
                if current_time >= trip.get('start_time', 0) + duration:
                    trip['status'] = 'completed'
                    self.logger.info(f"Trip {trip_id} completed")

                    # Move commuter to destination
                    dest = trip.get('request', {}).get('destination')
                    if dest:
                        try:
                            self.model.grid.move_agent(self, dest)
                        except Exception:
                            pass
                        self.location = dest

                    # Add to trip history
                    self.trip_history.append({
                        'trip_id': trip_id,
                        'request': trip.get('request', {}),
                        'option': option,
                        'start_time': trip.get('start_time'),
                        'end_time': current_time,
                        'duration': current_time - trip.get('start_time'),
                        'satisfaction': self._calculate_trip_satisfaction(trip)
                    })

                    # Update experience with provider and release capacity
                    provider_id = option.get('provider_id')
                    if provider_id:
                        satisfaction = self._calculate_trip_satisfaction(trip)
                        self._update_provider_experience(provider_id, satisfaction)
                        provider = self.model.providers.get(provider_id) if hasattr(self.model, 'providers') else None
                        if provider and hasattr(provider, 'complete_service'):
                            try:
                                provider.complete_service(trip_id, option.get('price', 0))
                                self.logger.info(f"Released provider {provider_id}")
                            except Exception:
                                pass

                    # Mark NFT used if applicable
                    if option.get('type') == 'nft_market' and 'nft_id' in option:
                        nft_id = option['nft_id']
                        if nft_id in self.owned_nfts:
                            self.owned_nfts[nft_id]['status'] = 'used'
                            self.logger.info(f"NFT {nft_id} marked as used")

                    # Detailed duration-based logging
                    if hasattr(self.model, "log_booking_detailed"):
                        self.model.log_booking_detailed(
                            tick=trip.get('start_time', current_time),
                            duration=duration,
                            mode=option.get('mode') or option.get('provider_type') or 'unknown',
                            price=option.get('price', 0),
                            commuter_id=self.unique_id,
                            is_bundle=(option.get('type') == 'bundle'),
                            provider_id=provider_id
                        )

                    # Schedule return/next trip
                    if random.random() < 0.6:
                        self.next_trip_time = current_time + random.randint(20, 40)
                        self.next_destination = trip.get('request', {}).get('origin') or self.home_location

                    # Clear active trip to allow new demand
                    del self.active_trips[trip_id]
                    self.active_request_id = None
                    self.last_trip_end_time = current_time

    def _calculate_trip_satisfaction(self, trip):
        """
        Calculate satisfaction with a completed trip.
        
        Args:
            trip: Trip data
            
        Returns:
            Satisfaction score between -1 and 1
        """
        # Base satisfaction is neutral
        satisfaction = 0.0
        option = trip.get('option', {})
        request = trip.get('request', {})
        
        # Factors that affect satisfaction
        
        # 1. Timeliness - was the service on time?
        expected_start = request.get('start_time') or trip.get('start_time') or option.get('start_time') or getattr(self.model.schedule, "time", 0)
        actual_start = trip.get('start_time') or option.get('start_time') or getattr(self.model.schedule, "time", 0)
        time_diff = abs(actual_start - expected_start)
        
        if time_diff < 300:  # Within 5 minutes
            timeliness = 0.2
        elif time_diff < 900:  # Within 15 minutes
            timeliness = 0.1
        elif time_diff < 1800:  # Within 30 minutes
            timeliness = 0
        else:  # More than 30 minutes
            timeliness = -0.2
        
        # 2. Price - was it good value?
        price = option.get('price', 0)
        max_price = self._calculate_max_price(request) if request else self._calculate_max_price({})
        
        if price < 0.5 * max_price:
            price_satisfaction = 0.2
        elif price < 0.8 * max_price:
            price_satisfaction = 0.1
        elif price < max_price:
            price_satisfaction = 0
        else:
            price_satisfaction = -0.1
        
        # 3. Comfort and quality (from option data)
        comfort = option.get('comfort', 0.5)
        comfort_satisfaction = (comfort - 0.5) * 0.4  # Scale from -0.2 to 0.2
        
        # 4. Mode preference
        mode = option.get('mode', 'car')
        mode_preference = self.mode_preference.get(mode, 0.2)
        mode_satisfaction = (mode_preference - 0.2) * 0.5  # Scale from -0.1 to 0.3
        
        # Combine factors
        satisfaction = timeliness + price_satisfaction + comfort_satisfaction + mode_satisfaction
        
        # Add random component for variation
        satisfaction += random.uniform(-0.1, 0.1)
        
        # Clamp to [-1, 1] range
        satisfaction = max(-1, min(1, satisfaction))
        
        return satisfaction

    def _update_provider_experience(self, provider_id, satisfaction):
        """
        Update experience with a provider based on trip satisfaction.
        
        Args:
            provider_id: Provider ID
            satisfaction: Satisfaction score between -1 and 1
        """
        if provider_id not in self.market_experience:
            self.market_experience[provider_id] = 0
        
        # Map satisfaction [-1, 1] to experience update [-0.2, 0.2]
        experience_update = satisfaction * 0.2
        
        # Apply update with some damping (80% new, 20% old)
        self.market_experience[provider_id] = (
            0.8 * self.market_experience[provider_id] + 
            0.2 * experience_update
        )
        
        # Ensure value is between -1 and 1
        self.market_experience[provider_id] = max(-1, min(1, self.market_experience[provider_id]))
        
        self.logger.debug(f"Updated experience with provider {provider_id} to {self.market_experience[provider_id]}")

    def _process_pending_requests(self):
        """
        Process pending requests and take action if needed.
        """
        # Make a copy to avoid modifying during iteration
        for request_id in list(self.pending_requests):
            if request_id not in self.requests:
                self.pending_requests.remove(request_id)
                continue

            request = self.requests[request_id]

            if request.get('blockchain_status', 'pending') == 'confirmed' and request.get('status') == 'active':
                self.logger.info(f"Processing pending request {request_id}")
                success = self.select_and_purchase_option(request_id)
                if not success:
                    self.logger.warning(f"Failed to process request {request_id}")
                # remove from pending regardless; model-level generator can create new demand later
                self.pending_requests.remove(request_id)

    

    def _generate_new_trips(self):
        """
        Generate new trips based on commuter's travel patterns.
        This is model-specific and depends on how the simulation is structured.
        """
        # This is a placeholder - implementation depends on the model design
        # In many models, trip generation would be controlled at the model level
        # rather than by individual agents
        pass

    def _generate_destination(self, origin):
        """Generate clustered destinations around hubs when available."""
        if random.random() < 0.8 and hasattr(self.model, 'hubs'):
            hub_name, coords = random.choice(list(self.model.hubs.items()))
            x = int(coords[0] + random.gauss(0, 2))
            y = int(coords[1] + random.gauss(0, 2))
            x = max(0, min(self.model.grid_width - 1, x))
            y = max(0, min(self.model.grid_height - 1, y))
            return [x, y]
        # Fallback random nearby destination
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        return [origin[0] + dx, origin[1] + dy]

    def _calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1: First point [x, y]
            point2: Second point [x, y]
            
        Returns:
            Euclidean distance
        """
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

    def get_position(self):
        """
        Get current position for visualization.
        
        Returns:
            Current position (x, y)
        """
        # If on an active trip, position might be along the route
        for trip_id, trip in self.active_trips.items():
            if trip['status'] == 'in_progress':
                # Calculate position along route
                route = trip['option'].get('route', [])
                if len(route) >= 2:
                    start_time = trip['start_time']
                    duration = trip['option'].get('time', 1800)  # Default 30 minutes
                    current_time = self.model.schedule.time
                    
                    # Calculate progress along route (0 to 1)
                    progress = min(1.0, (current_time - start_time) / duration)
                    
                    # Interpolate position along route
                    if progress <= 0:
                        return route[0]
                    elif progress >= 1:
                        return route[-1]
                    else:
                        # Find appropriate segment
                        segment_count = len(route) - 1
                        segment_idx = min(int(progress * segment_count), segment_count - 1)
                        segment_progress = (progress * segment_count) - segment_idx
                        
                        # Interpolate within segment
                        start = route[segment_idx]
                        end = route[segment_idx + 1]
                        
                        return [
                            start[0] + segment_progress * (end[0] - start[0]),
                            start[1] + segment_progress * (end[1] - start[1])
                        ]
        
        # If not on a trip, return home location
        return self.location
    
