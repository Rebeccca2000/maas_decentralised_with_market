#!/usr/bin/env python3
"""
Comprehensive Simulation Data Analysis Script
Demonstrates how to query and analyze all database tables
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def connect_db():
    """Connect to the database"""
    return sqlite3.connect('maas_bundles.db')

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*100)
    print(f"📊 {title}")
    print("="*100)

def analyze_simulation_runs(conn):
    """Analyze simulation runs"""
    print_section("SIMULATION RUNS OVERVIEW")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT run_id, start_time, end_time, total_steps, 
               num_commuters, num_providers, network_type, status
        FROM runs
        ORDER BY start_time DESC
    ''')
    
    runs = cursor.fetchall()
    for run in runs:
        print(f"\n🔹 Run: {run[0]}")
        print(f"   Started: {run[1]}")
        print(f"   Ended: {run[2]}")
        print(f"   Steps: {run[3]}")
        print(f"   Commuters: {run[4]}")
        print(f"   Providers: {run[5]}")
        print(f"   Network: {run[6]}")
        print(f"   Status: {run[7]}")
    
    return [run[0] for run in runs]

def analyze_mode_usage(conn, run_id):
    """Analyze mode usage metrics"""
    print_section(f"MODE USAGE ANALYSIS - {run_id}")

    cursor = conn.cursor()
    cursor.execute('''
        SELECT mode, total_trips, total_revenue, average_price,
               utilization_rate, peak_demand_tick, peak_demand_count
        FROM mode_usage_metrics
        WHERE run_id = ?
        ORDER BY total_revenue DESC
    ''', (run_id,))
    
    modes = cursor.fetchall()
    
    if modes:
        total_trips = sum(m[1] for m in modes)
        total_revenue = sum(m[2] for m in modes)
        
        print(f"\n📈 Total Trips: {total_trips}")
        print(f"💰 Total Revenue: ${total_revenue:.2f}")
        print(f"\n{'Mode':<15} {'Trips':<10} {'Revenue':<15} {'Avg Price':<15} {'Market Share':<15}")
        print("-" * 70)
        
        for mode in modes:
            market_share = (mode[1] / total_trips * 100) if total_trips > 0 else 0
            print(f"{mode[0]:<15} {mode[1]:<10} ${mode[2]:<14.2f} ${mode[3]:<14.2f} {market_share:<14.1f}%")
    else:
        print("\n⚠️  No mode usage data available")

def analyze_bundle_performance(conn, run_id):
    """Analyze bundle performance metrics"""
    print_section(f"BUNDLE PERFORMANCE ANALYSIS - {run_id}")

    cursor = conn.cursor()
    cursor.execute('''
        SELECT total_bundles_created, total_bundles_reserved,
               bundle_reservation_rate, average_discount_percentage, total_discount_given,
               popular_mode_combinations, average_segments_per_bundle,
               total_bundle_revenue, average_bundle_price
        FROM bundle_performance_metrics
        WHERE run_id = ?
    ''', (run_id,))

    bundle_data = cursor.fetchone()

    if bundle_data:
        print(f"\n🎫 Total Bundles Created: {bundle_data[0]}")
        print(f"✅ Total Bundles Reserved: {bundle_data[1]}")
        print(f"📊 Bundle Reservation Rate: {bundle_data[2]:.2f}%")
        print(f"💵 Average Discount Percentage: {bundle_data[3]:.2f}%")
        print(f"💰 Total Discount Given: ${bundle_data[4]:.2f}")
        print(f"🌟 Popular Mode Combinations: {bundle_data[5]}")
        print(f"📈 Average Segments per Bundle: {bundle_data[6]:.2f}")
        print(f"💵 Total Bundle Revenue: ${bundle_data[7]:.2f}")
        print(f"💵 Average Bundle Price: ${bundle_data[8]:.2f}")
        
        # Get actual bundles
        cursor.execute('''
            SELECT bundle_id, final_price, discount_amount, num_segments
            FROM bundles
            WHERE run_id = ?
        ''', (run_id,))

        bundles = cursor.fetchall()
        if bundles:
            print(f"\n📦 Bundle Details:")
            for bundle in bundles:
                print(f"   • Bundle {bundle[0]}: ${bundle[1]:.2f} (discount: ${bundle[2]:.2f}, segments: {bundle[3]})")
    else:
        print("\n⚠️  No bundle performance data available")

def analyze_gas_metrics(conn, run_id):
    """Analyze gas usage metrics"""
    print_section(f"GAS METRICS ANALYSIS - {run_id}")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tick, total_gas_used, total_gas_cost, average_gas_price,
               total_transactions, successful_transactions, failed_transactions,
               registration_txs, request_txs, offer_txs, match_txs,
               nft_mint_txs, nft_list_txs, nft_purchase_txs
        FROM gas_metrics
        WHERE run_id = ?
        ORDER BY tick
    ''', (run_id,))
    
    gas_data = cursor.fetchall()
    
    if gas_data:
        for data in gas_data:
            print(f"\n⛽ Tick {data[0]}:")
            print(f"   Total Gas Used: {data[1]:,}")
            print(f"   Total Gas Cost: {data[2]:,} wei")
            print(f"   Average Gas Price: {data[3]:,} wei")
            print(f"   Total Transactions: {data[4]}")
            print(f"   Successful: {data[5]} | Failed: {data[6]}")
            print(f"   Transaction Breakdown:")
            print(f"      - Registrations: {data[7]}")
            print(f"      - Requests: {data[8]}")
            print(f"      - Offers: {data[9]}")
            print(f"      - Matches: {data[10]}")
            print(f"      - NFT Mints: {data[11]}")
            print(f"      - NFT Lists: {data[12]}")
            print(f"      - NFT Purchases: {data[13]}")
    else:
        print("\n⚠️  No gas metrics data available (blockchain stats not tracked)")

def analyze_requests(conn, run_id):
    """Analyze travel requests"""
    print_section(f"TRAVEL REQUESTS ANALYSIS - {run_id}")

    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total,
               AVG(final_price) as avg_price,
               MIN(final_price) as min_price,
               MAX(final_price) as max_price
        FROM requests
        WHERE run_id = ? AND final_price IS NOT NULL
    ''', (run_id,))

    stats = cursor.fetchone()

    if stats and stats[0] > 0:
        print(f"\n📊 Request Statistics:")
        print(f"   Total Matched Requests: {stats[0]}")
        print(f"   Average Price: ${stats[1]:.2f}")
        print(f"   Min Price: ${stats[2]:.2f}")
        print(f"   Max Price: ${stats[3]:.2f}")
        
        # Get request status breakdown
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM requests
            WHERE run_id = ?
            GROUP BY status
        ''', (run_id,))
        
        status_breakdown = cursor.fetchall()
        print(f"\n📋 Request Status Breakdown:")
        for status, count in status_breakdown:
            print(f"   {status}: {count}")
    else:
        print("\n⚠️  No request data available")

def analyze_providers(conn, run_id):
    """Analyze provider performance"""
    print_section(f"PROVIDER PERFORMANCE ANALYSIS - {run_id}")

    cursor = conn.cursor()
    cursor.execute('''
        SELECT agent_id, mode,
               total_revenue, successful_matches, avg_price, utilization_rate
        FROM providers
        WHERE run_id = ?
        ORDER BY total_revenue DESC
    ''', (run_id,))

    providers = cursor.fetchall()

    if providers:
        print(f"\n{'Agent ID':<15} {'Mode':<10} {'Revenue':<15} {'Matches':<10} {'Avg Price':<15} {'Utilization':<15}")
        print("-" * 80)

        for provider in providers:
            util_rate = f"{provider[5]:.1f}%" if provider[5] is not None else "N/A"
            avg_price = f"${provider[4]:.2f}" if provider[4] is not None else "N/A"
            print(f"{provider[0]:<15} {provider[1]:<10} ${provider[2]:<14.2f} {provider[3]:<10} {avg_price:<15} {util_rate:<15}")
    else:
        print("\n⚠️  No provider data available")

def analyze_commuters(conn, run_id):
    """Analyze commuter behavior"""
    print_section(f"COMMUTER BEHAVIOR ANALYSIS - {run_id}")

    cursor = conn.cursor()
    cursor.execute('''
        SELECT agent_id, total_spent, successful_trips, total_requests, avg_wait_time
        FROM commuters
        WHERE run_id = ?
        ORDER BY total_spent DESC
        LIMIT 10
    ''', (run_id,))

    commuters = cursor.fetchall()

    if commuters:
        print(f"\n{'Agent ID':<15} {'Total Spent':<15} {'Trips':<10} {'Requests':<10} {'Avg Wait':<15}")
        print("-" * 65)

        for commuter in commuters:
            wait_time = f"{commuter[4]:.2f}s" if commuter[4] is not None else "N/A"
            print(f"{commuter[0]:<15} ${commuter[1]:<14.2f} {commuter[2]:<10} {commuter[3]:<10} {wait_time:<15}")
    else:
        print("\n⚠️  No commuter data available")

def generate_summary_report(conn):
    """Generate a comprehensive summary report"""
    print_section("COMPREHENSIVE SUMMARY REPORT")
    
    cursor = conn.cursor()
    
    # Get latest run
    cursor.execute('SELECT run_id FROM runs ORDER BY start_time DESC LIMIT 1')
    latest_run = cursor.fetchone()
    
    if not latest_run:
        print("\n⚠️  No simulation data available")
        return
    
    run_id = latest_run[0]
    
    print(f"\n📊 Analysis for Run: {run_id}")
    
    # Analyze all aspects
    analyze_mode_usage(conn, run_id)
    analyze_bundle_performance(conn, run_id)
    analyze_gas_metrics(conn, run_id)
    analyze_requests(conn, run_id)
    analyze_providers(conn, run_id)
    analyze_commuters(conn, run_id)

def main():
    """Main analysis function"""
    print("\n" + "="*100)
    print("🔬 MAAS DECENTRALIZED SIMULATION - COMPREHENSIVE DATA ANALYSIS")
    print("="*100)
    
    conn = connect_db()
    
    try:
        # Analyze all runs
        run_ids = analyze_simulation_runs(conn)
        
        if run_ids:
            # Generate detailed report for latest run
            generate_summary_report(conn)
            
            print("\n" + "="*100)
            print("✅ ANALYSIS COMPLETE")
            print("="*100)
            print("\n💡 Tips:")
            print("   • Run more simulations to collect more data")
            print("   • Use SQL queries to create custom analyses")
            print("   • Export data to CSV for visualization in Excel/Python")
            print("   • Check blockchain tables for transaction data")
            print("\n")
        else:
            print("\n⚠️  No simulation runs found in database")
            print("   Run a simulation first: python abm/agents/run_decentralized_model.py --export-db")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()

