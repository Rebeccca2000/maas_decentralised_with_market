#!/usr/bin/env python3
"""
Export simulation data to CSV files for analysis in Excel, Python, R, etc.
"""

import sqlite3
import csv
import os
from datetime import datetime

def export_table_to_csv(conn, table_name, output_dir='exports'):
    """Export a database table to CSV"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    cursor = conn.cursor()
    
    # Get table data
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    
    if not rows:
        print(f"⚠️  Table '{table_name}' is empty, skipping...")
        return
    
    # Get column names
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = [col[1] for col in cursor.fetchall()]
    
    # Write to CSV
    filename = os.path.join(output_dir, f'{table_name}.csv')
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    
    print(f"✅ Exported {len(rows)} rows from '{table_name}' to {filename}")

def export_all_tables(conn, output_dir='exports'):
    """Export all tables to CSV files"""
    
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Exporting {len(tables)} tables to CSV...")
    print("="*80)
    
    for table in tables:
        export_table_to_csv(conn, table, output_dir)
    
    print("="*80)
    print(f"✅ Export complete! Files saved to '{output_dir}/' directory")

def export_custom_query(conn, query, filename, output_dir='exports'):
    """Export results of a custom SQL query to CSV"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print(f"⚠️  Query returned no results")
        return
    
    # Get column names from cursor description
    columns = [desc[0] for desc in cursor.description]
    
    # Write to CSV
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    
    print(f"✅ Exported {len(rows)} rows to {filepath}")

def export_analysis_reports(conn, output_dir='exports'):
    """Export pre-built analysis reports"""
    
    print(f"\n📈 Exporting analysis reports...")
    print("="*80)
    
    # Report 1: Mode usage summary
    export_custom_query(conn, '''
        SELECT 
            m.run_id,
            m.mode,
            m.total_trips,
            m.total_revenue,
            m.average_price,
            m.utilization_rate,
            r.start_time,
            r.total_steps,
            r.num_commuters,
            r.num_providers
        FROM mode_usage_metrics m
        JOIN runs r ON m.run_id = r.run_id
        ORDER BY m.run_id, m.total_revenue DESC
    ''', 'report_mode_usage.csv', output_dir)
    
    # Report 2: Bundle performance summary
    export_custom_query(conn, '''
        SELECT 
            b.run_id,
            b.total_bundles_created,
            b.total_bundles_reserved,
            b.bundle_reservation_rate,
            b.total_bundle_revenue,
            b.average_bundle_price,
            b.total_discount_given,
            b.average_discount_percentage,
            b.average_segments_per_bundle,
            r.start_time,
            r.total_steps
        FROM bundle_performance_metrics b
        JOIN runs r ON b.run_id = r.run_id
        ORDER BY b.run_id
    ''', 'report_bundle_performance.csv', output_dir)
    
    # Report 3: Provider performance
    export_custom_query(conn, '''
        SELECT 
            p.run_id,
            p.agent_id,
            p.mode,
            p.total_offers,
            p.successful_matches,
            p.total_revenue,
            p.avg_price,
            p.utilization_rate,
            r.start_time,
            r.total_steps
        FROM providers p
        JOIN runs r ON p.run_id = r.run_id
        ORDER BY p.run_id, p.total_revenue DESC
    ''', 'report_provider_performance.csv', output_dir)
    
    # Report 4: Commuter behavior
    export_custom_query(conn, '''
        SELECT 
            c.run_id,
            c.agent_id,
            c.total_requests,
            c.successful_trips,
            c.total_spent,
            c.avg_wait_time,
            r.start_time,
            r.total_steps
        FROM commuters c
        JOIN runs r ON c.run_id = r.run_id
        ORDER BY c.run_id, c.total_spent DESC
    ''', 'report_commuter_behavior.csv', output_dir)
    
    # Report 5: Gas metrics
    export_custom_query(conn, '''
        SELECT 
            g.run_id,
            g.tick,
            g.total_gas_used,
            g.total_gas_cost,
            g.average_gas_price,
            g.total_transactions,
            g.successful_transactions,
            g.failed_transactions,
            g.registration_txs,
            g.request_txs,
            g.offer_txs,
            g.match_txs,
            g.nft_mint_txs,
            g.nft_list_txs,
            g.nft_purchase_txs
        FROM gas_metrics g
        ORDER BY g.run_id, g.tick
    ''', 'report_gas_metrics.csv', output_dir)
    
    # Report 6: Bundle details
    export_custom_query(conn, '''
        SELECT 
            b.run_id,
            b.bundle_id,
            b.origin_x,
            b.origin_y,
            b.dest_x,
            b.dest_y,
            b.base_price,
            b.discount_amount,
            b.final_price,
            b.num_segments,
            b.total_duration,
            b.created_at_tick,
            b.description
        FROM bundles b
        ORDER BY b.run_id, b.created_at_tick
    ''', 'report_bundle_details.csv', output_dir)
    
    print("="*80)
    print(f"✅ Analysis reports exported!")

def main():
    """Main export function"""
    
    print("\n" + "="*80)
    print("📤 MAAS DECENTRALIZED SIMULATION - DATA EXPORT TO CSV")
    print("="*80)
    
    # Connect to database
    conn = sqlite3.connect('maas_bundles.db')
    
    try:
        # Create timestamp for this export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'exports_{timestamp}'
        
        print(f"\n📁 Export directory: {output_dir}/")
        
        # Export all tables
        export_all_tables(conn, output_dir)
        
        # Export analysis reports
        export_analysis_reports(conn, output_dir)
        
        print("\n" + "="*80)
        print("✅ EXPORT COMPLETE")
        print("="*80)
        print(f"\n💡 Next steps:")
        print(f"   • Open CSV files in Excel for visualization")
        print(f"   • Import into Python/Pandas for advanced analysis")
        print(f"   • Use R or other statistical tools")
        print(f"   • Create charts and graphs from the data")
        print(f"\n📂 All files are in: {output_dir}/\n")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()

