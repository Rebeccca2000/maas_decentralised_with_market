# L2 Blockchain Support Guide

## Overview
The MaaS simulation now supports running on L2 blockchains (Optimism, Base, Arbitrum) in addition to the local Hardhat node.

## Quick Start

### Run on Localhost (Default)
```bash
python abm/agents/run_decentralized_model.py --steps 50 --commuters 10 --providers 5
```

### Run on Optimism Sepolia
```bash
python abm/agents/run_decentralized_model.py --network optimism-sepolia --steps 50 --commuters 10 --providers 5
```

### Run on Base Sepolia
```bash
python abm/agents/run_decentralized_model.py --network base-sepolia --steps 50 --commuters 10 --providers 5
```

### Run on Arbitrum Sepolia
```bash
python abm/agents/run_decentralized_model.py --network arbitrum-sepolia --steps 50 --commuters 10 --providers 5
```

## Command Line Options

### Network Selection
```
--network {localhost|optimism-sepolia|base-sepolia|arbitrum-sepolia}
```
Default: `localhost`

### Custom RPC URL
```
--rpc-url <URL>
```
Example: `--rpc-url https://opt-sepolia.g.alchemy.com/v2/YOUR_API_KEY`

### Custom Chain ID
```
--chain-id <ID>
```
Example: `--chain-id 11155420`

### Simulation Parameters
- `--steps <N>` - Number of simulation steps (default: 100)
- `--commuters <N>` - Number of commuter agents (default: 20)
- `--providers <N>` - Number of provider agents (default: 10)
- `--no-plots` - Skip plot generation for faster execution
- `--debug` - Run with minimal agents (5 commuters, 3 providers, 20 steps)
- `--big-test` - Run with extended parameters (15 commuters, 8 providers, 50 steps)

## Network Details

### Localhost (Hardhat)
- **RPC URL**: http://127.0.0.1:8545
- **Chain ID**: 31337
- **Status**: Local development, instant finality
- **Use Case**: Development and testing

### Optimism Sepolia
- **RPC URL**: https://sepolia.optimism.io
- **Chain ID**: 11155420
- **Status**: Testnet, ~2 second block time
- **Use Case**: Testing on Optimism L2

### Base Sepolia
- **RPC URL**: https://sepolia.base.org
- **Chain ID**: 84532
- **Status**: Testnet, ~2 second block time
- **Use Case**: Testing on Base L2

### Arbitrum Sepolia
- **RPC URL**: https://sepolia-rollup.arbitrum.io:443
- **Chain ID**: 421614
- **Status**: Testnet, ~0.25 second block time
- **Use Case**: Testing on Arbitrum L2

## Configuration

The script automatically updates `blockchain_config.json` with the selected network settings:

```json
{
  "rpc_url": "https://sepolia.optimism.io",
  "chain_id": 11155420,
  "deployment_info": "./deployed/simplified.json",
  "max_batch_size": 5,
  "tx_confirmation_blocks": 1,
  "gas_price_strategy": "medium",
  "gas_limit": 1500000,
  "provider_gas_limit": 5000000,
  "retry_count": 3,
  "retry_delay": 2,
  "real_blockchain_mode": true,
  "api_private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}
```

## Example Commands

### Development Testing
```bash
# Quick test on localhost
python abm/agents/run_decentralized_model.py --debug

# Medium test on localhost
python abm/agents/run_decentralized_model.py --big-test

# Full simulation on localhost
python abm/agents/run_decentralized_model.py --steps 100 --commuters 20 --providers 10
```

### L2 Testing
```bash
# Quick test on Optimism Sepolia
python abm/agents/run_decentralized_model.py --network optimism-sepolia --debug

# Full simulation on Base Sepolia
python abm/agents/run_decentralized_model.py --network base-sepolia --steps 100 --commuters 20 --providers 10

# Custom RPC on Arbitrum
python abm/agents/run_decentralized_model.py --network arbitrum-sepolia --rpc-url https://your-custom-rpc.com
```

## Output

The simulation generates:
1. **Console Output**: Real-time progress, metrics, and blockchain statistics
2. **Plots**: Performance dashboard and cost analysis (saved to `simulation_plots_TIMESTAMP/`)
3. **Blockchain Config**: Updated `blockchain_config.json` with network settings

## Troubleshooting

### RPC Connection Issues
- Verify the RPC URL is correct and accessible
- Check network connectivity
- Use `--rpc-url` to specify a custom RPC endpoint

### Transaction Failures
- Ensure sufficient gas limits in config
- Check blockchain network status
- Verify contract deployment on target network

### Slow Performance
- Use `--no-plots` to skip visualization generation
- Reduce `--steps` or agent counts for testing
- Use `--debug` mode for quick validation

## Notes

- The script automatically configures the blockchain connection based on the selected network
- All simulation results are saved with timestamps
- The blockchain configuration persists in `blockchain_config.json`
- For L2 networks, ensure contracts are deployed before running simulations

