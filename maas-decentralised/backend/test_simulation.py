#!/usr/bin/env python3
"""
Simple test simulation script for debugging backend integration
"""

import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Test simulation')
    parser.add_argument('--steps', type=int, default=10, help='Number of steps')
    parser.add_argument('--commuters', type=int, default=5, help='Number of commuters')
    parser.add_argument('--providers', type=int, default=3, help='Number of providers')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting test simulation with {args.commuters} commuters, {args.providers} providers, {args.steps} steps")
    
    for step in range(args.steps):
        print(f"Step {step + 1}/{args.steps} - Progress: {((step + 1) / args.steps) * 100:.1f}%")
        time.sleep(1)  # Simulate work
        
        # Flush output to ensure it's captured
        sys.stdout.flush()
    
    print("Simulation completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
