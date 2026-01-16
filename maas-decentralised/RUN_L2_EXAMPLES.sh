#!/bin/bash
# L2 Blockchain Simulation Examples
# Run any of these commands to test the MaaS simulation on different networks

echo "🚀 MaaS Simulation - L2 Blockchain Examples"
echo "==========================================="
echo ""
echo "Choose an example to run:"
echo ""
echo "LOCALHOST (Development)"
echo "  1. Quick test (debug mode)"
echo "  2. Medium test (big-test mode)"
echo "  3. Full simulation"
echo ""
echo "OPTIMISM SEPOLIA"
echo "  4. Quick test on Optimism"
echo "  5. Full simulation on Optimism"
echo ""
echo "BASE SEPOLIA"
echo "  6. Quick test on Base"
echo "  7. Full simulation on Base"
echo ""
echo "ARBITRUM SEPOLIA"
echo "  8. Quick test on Arbitrum"
echo "  9. Full simulation on Arbitrum"
echo ""
echo "CUSTOM"
echo "  10. Custom RPC URL"
echo ""

# Example commands (uncomment to run)

# ============================================
# LOCALHOST EXAMPLES
# ============================================

# 1. Quick test on localhost (debug mode)
# python abm/agents/run_decentralized_model.py --debug

# 2. Medium test on localhost (big-test mode)
# python abm/agents/run_decentralized_model.py --big-test

# 3. Full simulation on localhost
# python abm/agents/run_decentralized_model.py --steps 100 --commuters 20 --providers 10

# ============================================
# OPTIMISM SEPOLIA EXAMPLES
# ============================================

# 4. Quick test on Optimism Sepolia
# python abm/agents/run_decentralized_model.py --network optimism-sepolia --debug

# 5. Full simulation on Optimism Sepolia
# python abm/agents/run_decentralized_model.py --network optimism-sepolia --steps 100 --commuters 20 --providers 10

# ============================================
# BASE SEPOLIA EXAMPLES
# ============================================

# 6. Quick test on Base Sepolia
# python abm/agents/run_decentralized_model.py --network base-sepolia --debug

# 7. Full simulation on Base Sepolia
# python abm/agents/run_decentralized_model.py --network base-sepolia --steps 100 --commuters 20 --providers 10

# ============================================
# ARBITRUM SEPOLIA EXAMPLES
# ============================================

# 8. Quick test on Arbitrum Sepolia
# python abm/agents/run_decentralized_model.py --network arbitrum-sepolia --debug

# 9. Full simulation on Arbitrum Sepolia
# python abm/agents/run_decentralized_model.py --network arbitrum-sepolia --steps 100 --commuters 20 --providers 10

# ============================================
# CUSTOM RPC EXAMPLES
# ============================================

# 10. Custom RPC URL for Optimism
# python abm/agents/run_decentralized_model.py \
#   --network optimism-sepolia \
#   --rpc-url https://opt-sepolia.g.alchemy.com/v2/YOUR_API_KEY \
#   --steps 50 --commuters 10 --providers 5

# 11. Custom RPC URL for Base
# python abm/agents/run_decentralized_model.py \
#   --network base-sepolia \
#   --rpc-url https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY \
#   --steps 50 --commuters 10 --providers 5

# 12. Custom RPC URL for Arbitrum
# python abm/agents/run_decentralized_model.py \
#   --network arbitrum-sepolia \
#   --rpc-url https://arb-sepolia.g.alchemy.com/v2/YOUR_API_KEY \
#   --steps 50 --commuters 10 --providers 5

# ============================================
# ADVANCED EXAMPLES
# ============================================

# 13. Skip plots for faster execution
# python abm/agents/run_decentralized_model.py --network optimism-sepolia --no-plots --steps 50

# 14. Large scale simulation on L2
# python abm/agents/run_decentralized_model.py \
#   --network base-sepolia \
#   --steps 200 \
#   --commuters 50 \
#   --providers 20

# 15. Compare networks (run sequentially)
# echo "Testing Localhost..."
# python abm/agents/run_decentralized_model.py --debug
# echo "Testing Optimism Sepolia..."
# python abm/agents/run_decentralized_model.py --network optimism-sepolia --debug
# echo "Testing Base Sepolia..."
# python abm/agents/run_decentralized_model.py --network base-sepolia --debug

# ============================================
# COMMAND LINE REFERENCE
# ============================================

# Network options:
#   --network localhost              (default)
#   --network optimism-sepolia
#   --network base-sepolia
#   --network arbitrum-sepolia

# Simulation parameters:
#   --steps <N>                      (default: 100)
#   --commuters <N>                  (default: 20)
#   --providers <N>                  (default: 10)

# Flags:
#   --debug                          (5 commuters, 3 providers, 20 steps)
#   --big-test                       (15 commuters, 8 providers, 50 steps)
#   --no-plots                       (skip visualization generation)

# Custom RPC:
#   --rpc-url <URL>                  (override default RPC)
#   --chain-id <ID>                  (override default chain ID)

# ============================================
# QUICK START
# ============================================

# To run a quick test on Optimism Sepolia:
# python abm/agents/run_decentralized_model.py --network optimism-sepolia --debug

# To run a full simulation on Base Sepolia:
# python abm/agents/run_decentralized_model.py --network base-sepolia --steps 100 --commuters 20 --providers 10

# To use a custom RPC endpoint:
# python abm/agents/run_decentralized_model.py \
#   --network optimism-sepolia \
#   --rpc-url https://your-custom-rpc.com \
#   --steps 50

echo ""
echo "📖 For more information, see:"
echo "   - L2_BLOCKCHAIN_GUIDE.md (detailed guide)"
echo "   - L2_SETUP_SUMMARY.md (implementation overview)"
echo ""
echo "🚀 Ready to run! Uncomment any example above and execute."

