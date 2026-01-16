#!/usr/bin/env python3
"""
Demo script showing the difference between development and mainnet modes
"""

import os
import subprocess
import sys

def run_development_mode():
    """Run simulation in development mode (synchronous)"""
    print("🧪 RUNNING DEVELOPMENT MODE")
    print("=" * 50)
    print("• Uses synchronous blockchain calls")
    print("• Waits for each transaction to confirm")
    print("• Works on local testnets (Hardhat, Ganache)")
    print("• NOT suitable for mainnet")
    print("=" * 50)
    
    # Set environment variable for development mode
    env = os.environ.copy()
    env['MAINNET_MODE'] = 'false'
    
    # Run the simulation
    cmd = [sys.executable, 'abm/agents/run_decentralized_model.py', '--steps', '10', '--commuters', '3', '--providers', '2']
    subprocess.run(cmd, env=env)

def run_mainnet_mode():
    """Run simulation in mainnet mode (event-based)"""
    print("\n🌐 RUNNING MAINNET MODE")
    print("=" * 50)
    print("• Uses event-based blockchain interface")
    print("• Fire-and-forget transaction submission")
    print("• Event-driven confirmation tracking")
    print("• Suitable for mainnet deployment")
    print("=" * 50)
    
    # Set environment variable for mainnet mode
    env = os.environ.copy()
    env['MAINNET_MODE'] = 'true'
    
    # Run the simulation
    cmd = [sys.executable, 'abm/agents/run_decentralized_model.py', '--steps', '10', '--commuters', '3', '--providers', '2']
    subprocess.run(cmd, env=env)

def main():
    print("🚀 MaaS BLOCKCHAIN SIMULATION DEMO")
    print("=" * 60)
    print("This demo shows the difference between:")
    print("1. Development Mode: Synchronous (works on testnet)")
    print("2. Mainnet Mode: Event-based (works on mainnet)")
    print("=" * 60)
    
    choice = input("\nChoose mode:\n1. Development (sync)\n2. Mainnet (async)\n3. Both\nEnter choice (1/2/3): ")
    
    if choice == '1':
        run_development_mode()
    elif choice == '2':
        run_mainnet_mode()
    elif choice == '3':
        run_development_mode()
        run_mainnet_mode()
    else:
        print("Invalid choice. Running development mode by default.")
        run_development_mode()

if __name__ == "__main__":
    main()
