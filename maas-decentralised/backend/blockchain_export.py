"""
Blockchain data export functionality
Exports blockchain transaction data to Excel/CSV
"""

import os
import io
import json
import pandas as pd
from datetime import datetime
from flask import jsonify, send_file

def register_blockchain_export_routes(app, blockchain_interface):
    """Register blockchain export routes"""
    
    @app.route('/api/blockchain/export/<format>', methods=['GET'])
    def export_blockchain_data(format):
        """Export blockchain data to Excel or CSV"""
        try:
            if not blockchain_interface:
                return jsonify({'error': 'Blockchain not initialized'}), 500
            
            # Check if connected
            if not blockchain_interface.w3.is_connected():
                return jsonify({'error': 'Blockchain not connected'}), 500
            
            # Collect blockchain data
            blockchain_data = collect_blockchain_data(blockchain_interface)
            
            # Create DataFrames
            dfs = {
                'Overview': pd.DataFrame([blockchain_data['overview']]),
                'Contracts': pd.DataFrame(blockchain_data['contracts']),
                'Recent_Blocks': pd.DataFrame(blockchain_data['recent_blocks']),
                'Transaction_Summary': pd.DataFrame([blockchain_data['transaction_summary']])
            }
            
            # Generate file
            output = io.BytesIO()
            
            if format == 'excel':
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, df in dfs.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output.seek(0)
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = f'blockchain_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            else:  # CSV - combine all data
                combined_df = pd.concat([
                    df.assign(Source=name) for name, df in dfs.items()
                ], ignore_index=True)
                combined_df.to_csv(output, index=False)
                output.seek(0)
                mimetype = 'text/csv'
                filename = f'blockchain_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/blockchain/data/detailed', methods=['GET'])
    def get_detailed_blockchain_data():
        """Get detailed blockchain data for display"""
        try:
            if not blockchain_interface:
                return jsonify({'error': 'Blockchain not initialized'}), 500
            
            data = collect_blockchain_data(blockchain_interface)
            return jsonify(data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def collect_blockchain_data(blockchain_interface):
    """Collect comprehensive blockchain data"""
    try:
        w3 = blockchain_interface.w3
        
        # Basic blockchain info
        latest_block_number = w3.eth.block_number
        network_id = w3.net.version
        
        # Overview data
        overview = {
            'Network ID': network_id,
            'Latest Block': latest_block_number,
            'Chain ID': w3.eth.chain_id,
            'Gas Price (Gwei)': w3.from_wei(w3.eth.gas_price, 'gwei'),
            'Syncing': w3.eth.syncing,
            'Peer Count': w3.net.peer_count if hasattr(w3.net, 'peer_count') else 'N/A',
            'Timestamp': datetime.now().isoformat()
        }
        
        # Contract addresses
        contracts = []
        try:
            with open('deployment-info.json', 'r') as f:
                deployment_info = json.load(f)
                for contract_name, address in deployment_info.items():
                    if isinstance(address, str) and address.startswith('0x'):
                        contracts.append({
                            'Contract Name': contract_name,
                            'Address': address,
                            'Code Size': len(w3.eth.get_code(address)),
                            'Balance (ETH)': w3.from_wei(w3.eth.get_balance(address), 'ether')
                        })
        except FileNotFoundError:
            contracts.append({
                'Contract Name': 'No contracts deployed',
                'Address': 'N/A',
                'Code Size': 0,
                'Balance (ETH)': 0
            })
        
        # Recent blocks
        recent_blocks = []
        for i in range(min(10, latest_block_number + 1)):
            block_number = latest_block_number - i
            try:
                block = w3.eth.get_block(block_number)
                recent_blocks.append({
                    'Block Number': block_number,
                    'Timestamp': datetime.fromtimestamp(block['timestamp']).isoformat(),
                    'Transactions': len(block['transactions']),
                    'Gas Used': block['gasUsed'],
                    'Gas Limit': block['gasLimit'],
                    'Miner': block.get('miner', 'N/A')
                })
            except Exception as e:
                print(f"Error fetching block {block_number}: {e}")
                break
        
        # Transaction summary (from blockchain interface if available)
        transaction_summary = {
            'Total Transactions Sent': getattr(blockchain_interface, 'total_transactions', 0),
            'Successful Transactions': getattr(blockchain_interface, 'successful_transactions', 0),
            'Failed Transactions': getattr(blockchain_interface, 'failed_transactions', 0),
            'Total Gas Used': getattr(blockchain_interface, 'total_gas_used', 0),
            'Average Gas Price (Gwei)': w3.from_wei(w3.eth.gas_price, 'gwei')
        }
        
        return {
            'overview': overview,
            'contracts': contracts,
            'recent_blocks': recent_blocks,
            'transaction_summary': transaction_summary
        }
        
    except Exception as e:
        print(f"Error collecting blockchain data: {e}")
        return {
            'overview': {'Error': str(e)},
            'contracts': [],
            'recent_blocks': [],
            'transaction_summary': {}
        }

