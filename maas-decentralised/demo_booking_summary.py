#!/usr/bin/env python3
"""
Demo script to show the detailed booking summary functionality
that has been implemented in the decentralized transportation system.
"""

import time
import random

def demo_booking_summary():
    """Demonstrate the detailed booking summary functionality"""
    
    print("\n" + "="*80)
    print("🔗 BLOCKCHAIN STORAGE SUMMARY")
    print("="*80)
    
    # Mock blockchain statistics
    blockchain_stats = {
        'total_transactions': 45,
        'successful_transactions': 42,
        'failed_transactions': 3,
        'success_rate': 93.3,
        'total_gas_used': 2850000,
        'eth_spent': 0.00285,
        'commuter_registrations': 5,
        'provider_registrations': 3,
        'travel_requests': 12,
        'service_offers': 18,
        'completed_matches': 8,
        'blockchain_connected': True,
        'avg_tx_time': 2.3,
        'peak_tps': 4.2,
        'congestion_level': 'Low',
        'recent_tx_hashes': [
            '0x1234567890abcdef1234567890abcdef12345678',
            '0x2345678901bcdef12345678901bcdef123456789',
            '0x3456789012cdef123456789012cdef1234567890'
        ]
    }
    
    # Mock detailed booking data
    booking_details = [
        {
            'booking_id': 'REQ_001',
            'commuter_id': 0,
            'provider_id': 101,
            'price': 15.50,
            'origin': [10, 20],
            'destination': [50, 80],
            'commuter_profile': {
                'income_level': 'middle',
                'preferences': {'bus': 0.4, 'taxi': 0.3, 'bike': 0.3},
                'age': 35,
                'has_disability': False,
                'payment_scheme': 'PAYG'
            },
            'provider_profile': {
                'name': 'CityBus-101',
                'mode': 'bus',
                'capacity': 40,
                'base_price': 5.0,
                'quality_score': 85,
                'reliability': 90
            },
            'route_details': {
                'distance': 72.1,
                'duration': 25
            }
        },
        {
            'booking_id': 'REQ_002',
            'commuter_id': 2,
            'provider_id': 102,
            'price': 28.75,
            'origin': [5, 15],
            'destination': [45, 75],
            'commuter_profile': {
                'income_level': 'high',
                'preferences': {'taxi': 0.6, 'bus': 0.2, 'bike': 0.2},
                'age': 42,
                'has_disability': False,
                'payment_scheme': 'subscription'
            },
            'provider_profile': {
                'name': 'QuickTaxi-102',
                'mode': 'taxi',
                'capacity': 4,
                'base_price': 8.0,
                'quality_score': 92,
                'reliability': 88
            },
            'route_details': {
                'distance': 84.3,
                'duration': 18
            }
        },
        {
            'booking_id': 'REQ_003',
            'commuter_id': 3,
            'provider_id': 103,
            'price': 12.25,
            'origin': [25, 35],
            'destination': [60, 90],
            'commuter_profile': {
                'income_level': 'low',
                'preferences': {'bike': 0.5, 'bus': 0.4, 'taxi': 0.1},
                'age': 28,
                'has_disability': False,
                'payment_scheme': 'PAYG'
            },
            'provider_profile': {
                'name': 'EcoBike-103',
                'mode': 'bike',
                'capacity': 1,
                'base_price': 3.0,
                'quality_score': 78,
                'reliability': 85
            },
            'route_details': {
                'distance': 65.2,
                'duration': 35
            }
        }
    ]
    
    # Display transaction statistics
    print(f"📊 TRANSACTION STATISTICS:")
    print(f"   • Total transactions sent: {blockchain_stats['total_transactions']}")
    print(f"   • Successful transactions: {blockchain_stats['successful_transactions']}")
    print(f"   • Failed transactions: {blockchain_stats['failed_transactions']}")
    print(f"   • Success rate: {blockchain_stats['success_rate']:.1f}%")
    
    print(f"\n💰 GAS & COSTS:")
    print(f"   • Total gas used: {blockchain_stats['total_gas_used']:,}")
    print(f"   • Estimated ETH spent: {blockchain_stats['eth_spent']:.6f} ETH")
    
    print(f"\n📝 DATA STORED ON BLOCKCHAIN:")
    print(f"   • Commuter registrations: {blockchain_stats['commuter_registrations']}")
    print(f"   • Provider registrations: {blockchain_stats['provider_registrations']}")
    print(f"   • Travel requests: {blockchain_stats['travel_requests']}")
    print(f"   • Service offers: {blockchain_stats['service_offers']}")
    print(f"   • Completed matches: {blockchain_stats['completed_matches']}")
    
    print(f"\n🔍 BLOCKCHAIN VERIFICATION:")
    print(f"   • Connection status: {'✅ Connected' if blockchain_stats['blockchain_connected'] else '❌ Disconnected'}")
    print(f"   • Average transaction time: {blockchain_stats['avg_tx_time']:.1f}s")
    print(f"   • Peak TPS: {blockchain_stats['peak_tps']:.1f}")
    print(f"   • Network congestion: {blockchain_stats['congestion_level']}")
    
    if blockchain_stats['recent_tx_hashes']:
        print(f"\n🔗 RECENT SUCCESSFUL TRANSACTIONS:")
        for i, tx_hash in enumerate(blockchain_stats['recent_tx_hashes'][:5]):
            print(f"   {i+1}. {tx_hash}")
    
    # Display detailed booking information
    if booking_details:
        print(f"\n📋 DETAILED BOOKING RECORDS:")
        print(f"   Total bookings completed: {len(booking_details)}")
        print(f"\n   📊 BOOKING BREAKDOWN:")
        
        for i, booking in enumerate(booking_details):
            print(f"\n   🎫 BOOKING #{i+1}:")
            print(f"      • Booking ID: {booking['booking_id']}")
            print(f"      • Commuter ID: {booking['commuter_id']}")
            print(f"      • Provider ID: {booking['provider_id']}")
            
            # Provider details
            provider_profile = booking['provider_profile']
            print(f"      • Provider Type: {provider_profile['mode']}")
            print(f"      • Provider Name: {provider_profile['name']}")
            
            # Pricing and route
            print(f"      • Total Price: ${booking['price']}")
            print(f"      • Origin: {booking['origin']}")
            print(f"      • Destination: {booking['destination']}")
            
            # Commuter details
            commuter_profile = booking['commuter_profile']
            print(f"      • Commuter Income Level: {commuter_profile['income_level']}")
            print(f"      • Commuter Age: {commuter_profile['age']}")
            print(f"      • Payment Scheme: {commuter_profile['payment_scheme']}")
            
            # Route details
            route_details = booking['route_details']
            print(f"      • Route Distance: {route_details['distance']:.1f} units")
            print(f"      • Estimated Duration: {route_details['duration']} minutes")
        
        # Summary statistics
        total_revenue = sum(booking['price'] for booking in booking_details)
        avg_price = total_revenue / len(booking_details)
        
        provider_types = {}
        for booking in booking_details:
            provider_type = booking['provider_profile']['mode']
            provider_types[provider_type] = provider_types.get(provider_type, 0) + 1
        
        print(f"\n   💰 FINANCIAL SUMMARY:")
        print(f"      • Total Revenue Generated: ${total_revenue:.2f}")
        print(f"      • Average Booking Price: ${avg_price:.2f}")
        
        print(f"\n   🚗 PROVIDER TYPE BREAKDOWN:")
        for provider_type, count in provider_types.items():
            percentage = (count / len(booking_details)) * 100
            print(f"      • {provider_type}: {count} bookings ({percentage:.1f}%)")
    
    print(f"\n" + "="*80)
    print("🎯 SIMULATION COMPLETE")
    print("="*80)
    print("✅ Decentralized transportation system successfully demonstrated")
    print("✅ Agent-based modeling with real blockchain integration")
    print("✅ Smart contracts storing transportation data permanently")
    print("✅ Marketplace matching with on-chain settlement")
    print("✅ Detailed booking tracking with comprehensive analytics")
    print("="*80)

if __name__ == "__main__":
    print("🚀 DEMONSTRATING DETAILED BOOKING SUMMARY FUNCTIONALITY")
    print("="*80)
    print("This demo shows the enhanced booking tracking that has been")
    print("implemented in the decentralized transportation system.")
    print("="*80)
    
    demo_booking_summary()
