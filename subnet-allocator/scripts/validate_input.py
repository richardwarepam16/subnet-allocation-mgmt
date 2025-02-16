import argparse
import json
import sys
import ipaddress
from datetime import datetime
from logic.cidr_utils import validate_cidr_hierarchy, validate_cidr_format

def main():
    parser = argparse.ArgumentParser(description='Validate CIDR allocation input')
    parser.add_argument('--cidr', required=True, help='CIDR range requested')
    parser.add_argument('--type', choices=['kubernetes', 'normal'], required=True)
    
    args = parser.parse_args()
    
    try:
        # Basic CIDR format validation
        if not validate_cidr_format(args.cidr):
            raise ValueError(f"Invalid CIDR format: {args.cidr}")
            
        result = {
            'status': 'success',
            'cidr': args.cidr,
            'type': args.type,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        result = {'status': 'error', 'message': str(e)}
        sys.exit(1)
        
    with open('input_params.json', 'w') as f:
        json.dump(result, f)

def validate_cidr_format(cidr: str) -> bool:
    try:
        ipaddress.ip_network(cidr)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()
