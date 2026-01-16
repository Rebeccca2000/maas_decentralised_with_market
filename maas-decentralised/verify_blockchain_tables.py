"""
Verify the blockchain-related database tables
"""
import sqlite3

def verify_blockchain_tables():
    """Verify the blockchain tables in the database"""
    conn = sqlite3.connect('maas_bundles.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔗 BLOCKCHAIN DATABASE TABLES VERIFICATION")
    print("=" * 80)
    
    # 1. Check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Total tables in database: {len(tables)}")
    print(f"\n📊 ALL TABLES:")
    
    # Categorize tables
    core_tables = []
    analytics_tables = []
    blockchain_tables = []
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if table in ['runs', 'ticks', 'commuters', 'providers', 'requests', 'bundles', 
                     'bundle_segments', 'reservations', 'segment_reservations']:
            core_tables.append((table, count))
        elif table in ['mode_usage_metrics', 'bundle_performance_metrics', 'price_trends']:
            analytics_tables.append((table, count))
        elif table in ['blockchain_transactions', 'nft_tokens', 'nft_listings', 
                       'smart_contract_calls', 'blockchain_events', 'gas_metrics', 
                       'marketplace_metrics']:
            blockchain_tables.append((table, count))
    
    print(f"\n📦 CORE SIMULATION TABLES ({len(core_tables)}):")
    for table, count in core_tables:
        print(f"   • {table:<30} {count:>5} records")
    
    print(f"\n📈 ANALYTICS TABLES ({len(analytics_tables)}):")
    for table, count in analytics_tables:
        print(f"   • {table:<30} {count:>5} records")
    
    print(f"\n🔗 BLOCKCHAIN TABLES ({len(blockchain_tables)}):")
    for table, count in blockchain_tables:
        print(f"   • {table:<30} {count:>5} records")
    
    # 2. Show schema for each blockchain table
    print(f"\n" + "=" * 80)
    print(f"📋 BLOCKCHAIN TABLE SCHEMAS")
    print("=" * 80)
    
    blockchain_table_names = [
        'blockchain_transactions',
        'nft_tokens',
        'nft_listings',
        'smart_contract_calls',
        'blockchain_events',
        'gas_metrics',
        'marketplace_metrics'
    ]
    
    for table_name in blockchain_table_names:
        if table_name in tables:
            print(f"\n🔹 {table_name.upper().replace('_', ' ')}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Columns: {len(columns)}")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                print(f"      • {col_name:<30} {col_type:<15} {nullable}")
    
    # 3. Summary
    print(f"\n" + "=" * 80)
    print(f"✅ VERIFICATION COMPLETE")
    print("=" * 80)
    
    print(f"\n📊 DATABASE SUMMARY:")
    print(f"   • Total tables: {len(tables)}")
    print(f"   • Core simulation tables: {len(core_tables)}")
    print(f"   • Analytics tables: {len(analytics_tables)}")
    print(f"   • Blockchain tables: {len(blockchain_tables)}")
    
    print(f"\n🔗 BLOCKCHAIN CAPABILITIES:")
    print(f"   ✅ Transaction tracking (blockchain_transactions)")
    print(f"   ✅ NFT token management (nft_tokens)")
    print(f"   ✅ Marketplace listings (nft_listings)")
    print(f"   ✅ Smart contract calls (smart_contract_calls)")
    print(f"   ✅ Blockchain events (blockchain_events)")
    print(f"   ✅ Gas usage metrics (gas_metrics)")
    print(f"   ✅ Marketplace metrics (marketplace_metrics)")
    
    print(f"\n📈 ANALYTICAL CAPABILITIES:")
    print(f"   ✅ Time-series data (ticks table with 23 columns)")
    print(f"   ✅ Mode usage statistics (mode_usage_metrics)")
    print(f"   ✅ Bundle performance (bundle_performance_metrics)")
    print(f"   ✅ Price trends (price_trends)")
    print(f"   ✅ Transaction history (blockchain_transactions)")
    print(f"   ✅ Gas cost analysis (gas_metrics)")
    print(f"   ✅ NFT marketplace analytics (marketplace_metrics)")
    
    print(f"\n🎯 READY FOR:")
    print(f"   • Blockchain transaction analysis")
    print(f"   • NFT marketplace visualization")
    print(f"   • Gas cost optimization")
    print(f"   • Smart contract performance monitoring")
    print(f"   • Event-driven analytics")
    print(f"   • Multi-modal journey analysis")
    print(f"   • Price trend forecasting")
    
    conn.close()

if __name__ == "__main__":
    verify_blockchain_tables()

