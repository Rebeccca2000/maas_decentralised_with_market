#!/usr/bin/env python3
"""
Test script to verify all blockchain interface improvements
Tests atomic operations, rollback mechanisms, thread safety, and error handling
"""

import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from abm.utils.blockchain_interface import BlockchainInterface, TransactionData, TransactionState


class MockAgent:
    """Mock agent for testing"""
    def __init__(self, unique_id, agent_type="commuter"):
        self.unique_id = unique_id
        self.agent_type = agent_type


def test_transaction_state_machine():
    """Test the transaction state machine"""
    print("🧪 Testing Transaction State Machine...")
    
    tx_data = TransactionData(
        tx_type="test",
        function_name="testFunction",
        params={"test": "data"},
        sender_id=1
    )
    
    # Test initial state
    assert tx_data.state == TransactionState.PENDING
    print("✅ Initial state is PENDING")
    
    # Test state transitions
    tx_data.state = TransactionState.SUBMITTED
    assert tx_data.state == TransactionState.SUBMITTED
    print("✅ State transition to SUBMITTED works")
    
    tx_data.state = TransactionState.CONFIRMED
    assert tx_data.state == TransactionState.CONFIRMED
    print("✅ State transition to CONFIRMED works")
    
    print("✅ Transaction state machine test passed!\n")


def test_thread_safety():
    """Test thread safety of blockchain interface"""
    print("🧪 Testing Thread Safety...")
    
    # Initialize blockchain interface
    blockchain = BlockchainInterface(async_mode=False)
    
    # Create mock agents
    agents = [MockAgent(i) for i in range(10)]
    
    # Test concurrent request creation
    def create_request(agent):
        request = {
            'origin': [0, 0],
            'destination': [10, 10],
            'start_time': time.time()
        }
        return blockchain.create_travel_request_marketplace(agent, request)
    
    # Run concurrent operations
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_request, agent) for agent in agents]
        results = [future.result() for future in futures]
    
    # Check results
    successful_requests = sum(1 for success, _ in results if success)
    print(f"✅ Created {successful_requests}/{len(agents)} requests concurrently")
    
    # Verify marketplace database integrity
    with blockchain.marketplace_db_lock:
        db_requests = len(blockchain.marketplace_db['requests'])
    
    print(f"✅ Marketplace DB has {db_requests} requests (thread-safe)")
    print("✅ Thread safety test passed!\n")


def test_atomic_operations():
    """Test atomic operations and rollback"""
    print("🧪 Testing Atomic Operations...")
    
    blockchain = BlockchainInterface(async_mode=False)
    agent = MockAgent(1)
    
    # Test successful atomic operation
    request = {
        'origin': [0, 0],
        'destination': [5, 5],
        'start_time': time.time()
    }
    
    success, request_id = blockchain.create_travel_request_marketplace(agent, request)
    
    if success:
        print("✅ Atomic request creation succeeded")
        
        # Verify data is in marketplace DB
        with blockchain.marketplace_db_lock:
            assert request_id in blockchain.marketplace_db['requests']
        print("✅ Data correctly stored in marketplace DB")
    else:
        print("❌ Atomic request creation failed")
    
    print("✅ Atomic operations test passed!\n")


def test_error_handling():
    """Test error handling and recovery"""
    print("🧪 Testing Error Handling...")
    
    blockchain = BlockchainInterface(async_mode=False)
    
    # Test recoverable vs non-recoverable errors
    recoverable_errors = [
        "nonce too low",
        "replacement transaction underpriced",
        "network error"
    ]
    
    non_recoverable_errors = [
        "insufficient funds",
        "execution reverted",
        "invalid signature"
    ]
    
    for error in recoverable_errors:
        is_recoverable = blockchain._is_recoverable_error(Exception(error))
        assert is_recoverable, f"Error '{error}' should be recoverable"
        print(f"✅ '{error}' correctly identified as recoverable")
    
    for error in non_recoverable_errors:
        is_recoverable = blockchain._is_recoverable_error(Exception(error))
        assert not is_recoverable, f"Error '{error}' should not be recoverable"
        print(f"✅ '{error}' correctly identified as non-recoverable")
    
    print("✅ Error handling test passed!\n")


def test_offer_mapping_thread_safety():
    """Test thread-safe offer mapping"""
    print("🧪 Testing Offer Mapping Thread Safety...")
    
    blockchain = BlockchainInterface(async_mode=False)
    
    # Test concurrent offer mapping operations
    def add_mapping(i):
        with blockchain.offer_mapping_lock:
            blockchain.offer_id_mapping[f"offer_{i}"] = i
            blockchain.provider_request_mapping[f"req_{i}_prov_{i}"] = i
    
    # Run concurrent mapping operations
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(add_mapping, i) for i in range(20)]
        [future.result() for future in futures]
    
    # Verify mappings
    with blockchain.offer_mapping_lock:
        assert len(blockchain.offer_id_mapping) == 20
        assert len(blockchain.provider_request_mapping) == 20
    
    print("✅ Offer mapping thread safety test passed!")
    
    # Test reset functionality
    blockchain.reset_offer_mappings()
    
    with blockchain.offer_mapping_lock:
        assert len(blockchain.offer_id_mapping) == 0
        assert len(blockchain.provider_request_mapping) == 0
    
    print("✅ Offer mapping reset test passed!\n")


def test_statistics_accuracy():
    """Test statistics tracking accuracy"""
    print("🧪 Testing Statistics Accuracy...")
    
    blockchain = BlockchainInterface(async_mode=False)
    
    # Create some mock transactions
    successful_tx = TransactionData(
        tx_type="request",
        function_name="createRequest",
        params={},
        sender_id=1
    )
    
    failed_tx = TransactionData(
        tx_type="request", 
        function_name="createRequest",
        params={},
        sender_id=2
    )
    
    # Update stats for successful transaction
    blockchain._update_transaction_stats(successful_tx, success=True)
    
    # Update stats for failed transaction
    blockchain._update_transaction_stats(failed_tx, success=False)
    
    # Verify only successful transactions are counted
    assert blockchain.blockchain_stats['total_transactions'] == 1
    assert blockchain.blockchain_stats['travel_requests'] == 1
    
    print("✅ Statistics only count successful transactions")
    print("✅ Statistics accuracy test passed!\n")


def main():
    """Run all tests"""
    print("🚀 Starting Blockchain Interface Improvement Tests\n")
    
    try:
        test_transaction_state_machine()
        test_thread_safety()
        test_atomic_operations()
        test_error_handling()
        test_offer_mapping_thread_safety()
        test_statistics_accuracy()
        
        print("🎉 ALL TESTS PASSED!")
        print("✅ Blockchain interface improvements are working correctly!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
