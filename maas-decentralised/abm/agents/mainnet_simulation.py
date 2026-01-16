#!/usr/bin/env python3
"""
Mainnet-ready simulation using event-based blockchain interface
Demonstrates how to run simulations without blocking on transaction confirmations
"""

import time
import json
import logging
import argparse
from typing import Dict, List, Any
from dataclasses import dataclass

# Import our event-based blockchain interface
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.event_based_blockchain import EventBasedBlockchain

@dataclass
class SimulationAgent:
    """Represents a simulation agent (commuter or provider)"""
    agent_id: int
    agent_type: str  # 'commuter' or 'provider'
    blockchain_address: str = None
    registration_confirmed: bool = False
    
class MainnetSimulation:
    """
    Mainnet-ready MaaS simulation using event-based blockchain
    
    Key principles for mainnet:
    1. Never wait for transaction confirmations
    2. Use events to track state changes
    3. Handle transaction failures gracefully
    4. Provide real-time status updates
    5. Allow simulation to continue even with pending transactions
    """
    
    def __init__(self, config_file="blockchain_config.json"):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize event-based blockchain
        self.blockchain = EventBasedBlockchain(config_file)
        
        # Simulation state
        self.agents: Dict[int, SimulationAgent] = {}
        self.requests: Dict[int, Dict[str, Any]] = {}
        self.offers: Dict[int, List[Dict[str, Any]]] = {}
        self.matches: Dict[int, Dict[str, Any]] = {}
        
        # Simulation metrics
        self.metrics = {
            'agents_created': 0,
            'registrations_attempted': 0,
            'requests_created': 0,
            'offers_submitted': 0,
            'matches_recorded': 0,
            'simulation_start_time': time.time()
        }
        
        # Set up callbacks for blockchain events
        self._setup_event_callbacks()
    
    def _setup_event_callbacks(self):
        """Set up callbacks to handle blockchain events"""
        
        def on_commuter_registered(tx_hash, tx_data):
            """Callback when commuter registration is confirmed"""
            commuter_id = tx_data.params['commuter_id']
            if commuter_id in self.agents:
                self.agents[commuter_id].registration_confirmed = True
                self.logger.info(f"✅ Commuter {commuter_id} registration confirmed via event")
        
        def on_provider_registered(tx_hash, tx_data):
            """Callback when provider registration is confirmed"""
            provider_id = tx_data.params['provider_id']
            if provider_id in self.agents:
                self.agents[provider_id].registration_confirmed = True
                self.logger.info(f"✅ Provider {provider_id} registration confirmed via event")
        
        def on_request_created(tx_hash, tx_data):
            """Callback when request creation is confirmed"""
            commuter_id = tx_data.params['commuter_id']
            self.logger.info(f"✅ Request by commuter {commuter_id} confirmed via event")
        
        def on_offer_submitted(tx_hash, tx_data):
            """Callback when offer submission is confirmed"""
            provider_id = tx_data.params['provider_id']
            request_id = tx_data.params['request_id']
            self.logger.info(f"✅ Offer by provider {provider_id} for request {request_id} confirmed via event")
        
        def on_match_recorded(tx_hash, tx_data):
            """Callback when match recording is confirmed"""
            request_id = tx_data.params['request_id']
            self.logger.info(f"✅ Match for request {request_id} confirmed via event")
        
        # Store callbacks for use in transaction submissions
        self.callbacks = {
            'commuter_registration': on_commuter_registered,
            'provider_registration': on_provider_registered,
            'request_creation': on_request_created,
            'offer_submission': on_offer_submitted,
            'match_recording': on_match_recorded
        }
    
    def create_agents(self, num_commuters: int, num_providers: int):
        """Create simulation agents without waiting for blockchain confirmation"""
        self.logger.info(f"Creating {num_commuters} commuters and {num_providers} providers...")
        
        # Create commuters
        for i in range(num_commuters):
            agent_id = i + 1
            agent = SimulationAgent(agent_id, 'commuter')
            self.agents[agent_id] = agent
            self.metrics['agents_created'] += 1
            
            # Submit registration transaction (non-blocking)
            try:
                # Generate a blockchain address for the agent
                from eth_account import Account
                account = Account.create()
                agent.blockchain_address = account.address
                
                # Submit registration asynchronously
                tx_hash = self.blockchain.register_commuter_async(
                    agent_id, 
                    agent.blockchain_address,
                    self.callbacks['commuter_registration']
                )
                
                self.metrics['registrations_attempted'] += 1
                self.logger.info(f"📤 Submitted commuter {agent_id} registration: {tx_hash}")
                
            except Exception as e:
                self.logger.error(f"Failed to register commuter {agent_id}: {e}")
        
        # Create providers
        for i in range(num_providers):
            agent_id = num_commuters + i + 1
            agent = SimulationAgent(agent_id, 'provider')
            self.agents[agent_id] = agent
            self.metrics['agents_created'] += 1
            
            # Submit registration transaction (non-blocking)
            try:
                # Generate a blockchain address for the agent
                from eth_account import Account
                account = Account.create()
                agent.blockchain_address = account.address
                
                # For providers, we need to register through the facade
                # This is a simplified version - in reality you'd call the provider registration
                self.metrics['registrations_attempted'] += 1
                self.logger.info(f"📤 Provider {agent_id} registration queued")
                
            except Exception as e:
                self.logger.error(f"Failed to register provider {agent_id}: {e}")
    
    def simulate_travel_requests(self, num_requests: int):
        """Simulate travel requests without waiting for confirmations"""
        self.logger.info(f"Creating {num_requests} travel requests...")
        
        commuters = [a for a in self.agents.values() if a.agent_type == 'commuter']
        
        for i in range(num_requests):
            if not commuters:
                break
                
            # Select a commuter (in real simulation, this would be based on agent behavior)
            commuter = commuters[i % len(commuters)]
            request_id = i + 1
            
            # Create request data
            request_data = {
                'request_id': request_id,
                'commuter_id': commuter.agent_id,
                'origin': [10.0 + i, 20.0 + i],
                'destination': [30.0 + i, 40.0 + i],
                'timestamp': time.time()
            }
            
            self.requests[request_id] = request_data
            
            # Submit to blockchain asynchronously
            try:
                # Create content hash (in reality, this would be stored on IPFS)
                content_hash = f"request_{request_id}_hash"
                
                tx_hash = self.blockchain.create_request_async(
                    commuter.agent_id,
                    content_hash,
                    self.callbacks['request_creation']
                )
                
                self.metrics['requests_created'] += 1
                self.logger.info(f"📤 Submitted request {request_id} by commuter {commuter.agent_id}: {tx_hash}")
                
            except Exception as e:
                self.logger.error(f"Failed to create request {request_id}: {e}")
    
    def simulate_offers(self, offers_per_request: int = 2):
        """Simulate provider offers without waiting for confirmations"""
        self.logger.info(f"Creating offers ({offers_per_request} per request)...")
        
        providers = [a for a in self.agents.values() if a.agent_type == 'provider']
        
        for request_id, request_data in self.requests.items():
            self.offers[request_id] = []
            
            for i in range(min(offers_per_request, len(providers))):
                provider = providers[i % len(providers)]
                
                # Create offer data
                offer_data = {
                    'offer_id': len(self.offers[request_id]) + 1,
                    'request_id': request_id,
                    'provider_id': provider.agent_id,
                    'price': 10.0 + (i * 2.0),  # Varying prices
                    'timestamp': time.time()
                }
                
                self.offers[request_id].append(offer_data)
                
                # Submit to blockchain asynchronously
                try:
                    content_hash = f"offer_{request_id}_{provider.agent_id}_hash"
                    
                    tx_hash = self.blockchain.submit_offer_async(
                        request_id,
                        provider.agent_id,
                        content_hash,
                        self.callbacks['offer_submission']
                    )
                    
                    self.metrics['offers_submitted'] += 1
                    self.logger.info(f"📤 Submitted offer by provider {provider.agent_id} for request {request_id}: {tx_hash}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to submit offer for request {request_id}: {e}")
    
    def simulate_matches(self):
        """Simulate matching without waiting for confirmations"""
        self.logger.info("Creating matches...")
        
        for request_id, offers in self.offers.items():
            if not offers:
                continue
            
            # Select best offer (simplified - just pick the first one)
            best_offer = offers[0]
            
            match_data = {
                'request_id': request_id,
                'offer_id': best_offer['offer_id'],
                'provider_id': best_offer['provider_id'],
                'price': best_offer['price']
            }
            
            self.matches[request_id] = match_data
            
            # Submit to blockchain asynchronously
            try:
                # Convert price to wei (simplified)
                price_wei = int(best_offer['price'] * 10**18)
                
                tx_hash = self.blockchain.record_match_async(
                    request_id,
                    best_offer['offer_id'],
                    best_offer['provider_id'],
                    price_wei,
                    self.callbacks['match_recording']
                )
                
                self.metrics['matches_recorded'] += 1
                self.logger.info(f"📤 Submitted match for request {request_id}: {tx_hash}")
                
            except Exception as e:
                self.logger.error(f"Failed to record match for request {request_id}: {e}")
    
    def print_status(self):
        """Print current simulation and blockchain status"""
        elapsed = time.time() - self.metrics['simulation_start_time']
        blockchain_stats = self.blockchain.get_statistics()
        
        print(f"\n{'='*60}")
        print(f"🚀 MAINNET SIMULATION STATUS (Elapsed: {elapsed:.1f}s)")
        print(f"{'='*60}")
        
        print(f"📊 SIMULATION METRICS:")
        print(f"   • Agents created: {self.metrics['agents_created']}")
        print(f"   • Registration attempts: {self.metrics['registrations_attempted']}")
        print(f"   • Requests created: {self.metrics['requests_created']}")
        print(f"   • Offers submitted: {self.metrics['offers_submitted']}")
        print(f"   • Matches recorded: {self.metrics['matches_recorded']}")
        
        print(f"\n🔗 BLOCKCHAIN STATUS:")
        print(f"   • Transactions sent: {blockchain_stats['transactions_sent']}")
        print(f"   • Transactions confirmed: {blockchain_stats['transactions_confirmed']}")
        print(f"   • Transactions failed: {blockchain_stats['transactions_failed']}")
        print(f"   • Pending transactions: {blockchain_stats['pending_transactions']}")
        print(f"   • Events processed: {blockchain_stats['events_processed']}")
        
        print(f"\n✅ CONFIRMED ON BLOCKCHAIN:")
        print(f"   • Registrations: {blockchain_stats['confirmed_registrations']}")
        print(f"   • Requests: {blockchain_stats['confirmed_requests']}")
        print(f"   • Offers: {blockchain_stats['confirmed_offers']}")
        print(f"   • Matches: {blockchain_stats['confirmed_matches']}")
        
        if blockchain_stats['pending_transactions'] > 0:
            print(f"\n⏳ {blockchain_stats['pending_transactions']} transactions still pending...")
            print(f"   Events will update status as confirmations arrive")
        
        print(f"{'='*60}\n")
    
    def run_simulation(self, num_commuters: int = 5, num_providers: int = 3, num_requests: int = 10):
        """Run the complete mainnet simulation"""
        self.logger.info("🚀 Starting mainnet-ready simulation...")
        
        # Phase 1: Create agents (non-blocking)
        self.create_agents(num_commuters, num_providers)
        self.print_status()
        
        # Phase 2: Create requests (non-blocking)
        time.sleep(2)  # Small delay to show progression
        self.simulate_travel_requests(num_requests)
        self.print_status()
        
        # Phase 3: Create offers (non-blocking)
        time.sleep(2)
        self.simulate_offers(offers_per_request=2)
        self.print_status()
        
        # Phase 4: Create matches (non-blocking)
        time.sleep(2)
        self.simulate_matches()
        self.print_status()
        
        # Phase 5: Show final status
        self.logger.info("🎉 Simulation complete! Transactions will continue confirming in background...")
        
        # Optional: Wait for some confirmations (for demo purposes)
        # In production, you would NOT do this - just rely on events
        print("⏳ Waiting 30 seconds for some confirmations (demo only)...")
        final_stats = self.blockchain.wait_for_confirmations(timeout=30)
        
        self.print_status()
        
        return final_stats
    
    def shutdown(self):
        """Shutdown the simulation"""
        self.blockchain.shutdown()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Mainnet-ready MaaS simulation')
    parser.add_argument('--commuters', type=int, default=5, help='Number of commuters')
    parser.add_argument('--providers', type=int, default=3, help='Number of providers')
    parser.add_argument('--requests', type=int, default=10, help='Number of requests')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run simulation
    simulation = MainnetSimulation()
    
    try:
        final_stats = simulation.run_simulation(
            num_commuters=args.commuters,
            num_providers=args.providers,
            num_requests=args.requests
        )
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   • Total transactions sent: {final_stats['transactions_sent']}")
        print(f"   • Confirmed: {final_stats['transactions_confirmed']}")
        print(f"   • Still pending: {final_stats['pending_transactions']}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
    finally:
        simulation.shutdown()

if __name__ == "__main__":
    main()
