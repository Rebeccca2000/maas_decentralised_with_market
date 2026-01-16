#!/usr/bin/env python3
"""Check gas metrics data in the database"""

import sqlite3

# Connect to database
conn = sqlite3.connect('maas_bundles.db')
cursor = conn.cursor()

print("\n" + "="*100)
print("📊 GAS METRICS DATA")
print("="*100)

# Get gas metrics
cursor.execute('SELECT * FROM gas_metrics')
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\n🔹 Gas Metrics Record:")
        print(f"   Run ID: {row[1]}")
        print(f"   Tick: {row[2]}")
        print(f"   Total Gas Used: {row[3]}")
        print(f"   Total Gas Cost: {row[4]} wei")
        print(f"   Average Gas Price: {row[5]} wei")
        print(f"   Total Transactions: {row[8]}")
        print(f"   Successful: {row[9]}")
        print(f"   Failed: {row[10]}")
        print(f"   Pending: {row[11]}")
        print(f"   Registration TXs: {row[12]}")
        print(f"   Request TXs: {row[13]}")
        print(f"   Offer TXs: {row[14]}")
        print(f"   Match TXs: {row[15]}")
        print(f"   NFT Mint TXs: {row[16]}")
        print(f"   NFT List TXs: {row[17]}")
        print(f"   NFT Purchase TXs: {row[18]}")
        print(f"   Timestamp: {row[22]}")
else:
    print("\n⚠️  No gas metrics data found")

print("\n" + "="*100)
print("📊 MODE USAGE METRICS")
print("="*100)

# Get mode usage metrics
cursor.execute('SELECT * FROM mode_usage_metrics')
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\n🔹 Mode Usage Record:")
        print(f"   Run ID: {row[1]}")
        print(f"   Mode: {row[2]}")
        print(f"   Total Trips: {row[3]}")
        print(f"   Total Revenue: ${row[4]:.2f}")
        print(f"   Average Price: ${row[5]:.2f}")
        print(f"   Utilization Rate: {row[6]:.2%}")
else:
    print("\n⚠️  No mode usage metrics found")

print("\n" + "="*100)
print("📊 BUNDLE PERFORMANCE METRICS")
print("="*100)

# Get bundle performance metrics
cursor.execute('SELECT * FROM bundle_performance_metrics')
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\n🔹 Bundle Performance Record:")
        print(f"   Run ID: {row[1]}")
        print(f"   Total Bundles Created: {row[2]}")
        print(f"   Total Bundles Reserved: {row[3]}")
        print(f"   Bundle Creation Rate: {row[4]:.2%}")
        print(f"   Average Discount: ${row[5]:.2f}")
        print(f"   Total Discount Given: ${row[6]:.2f}")
else:
    print("\n⚠️  No bundle performance metrics found")

print("\n" + "="*100)

conn.close()

