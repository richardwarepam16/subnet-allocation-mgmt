import argparse
import json
import logging
from typing import Dict, List
from datetime import datetime
from db.db_conn import DatabaseConnection
from logic.cidr_utils import hierarchical_split, validate_cidr_hierarchy

logging.basicConfig(level=logging.INFO)

class CIDRAllocator:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def allocate(self, cidr_type: str, requested_cidr: str, prefixes: Dict[str, int] = None) -> Dict:
        try:
            available_cidr = self._find_available_cidr(requested_cidr, cidr_type)
            if not available_cidr:
                raise ValueError(f"No available CIDR can accommodate {requested_cidr}")

            allocated = []
            if cidr_type == 'kubernetes':
                allocated = self._handle_kubernetes_allocation(available_cidr, prefixes)
            else:
                allocated = self._handle_normal_allocation(available_cidr)

            self._update_database(cidr_type, available_cidr, allocated)
            
            return {
                'status': 'success',
                'allocated_cidrs': allocated,
                'original_cidr': available_cidr,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Allocation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _find_available_cidr(self, requested_cidr: str, cidr_type: str) -> str:
        available_cidrs = self.db.get_available_cidrs(cidr_type)
        required_prefix = int(requested_cidr.split('/')[1])
        for cidr in available_cidrs:
            if validate_cidr_hierarchy(cidr, requested_cidr):
                return cidr
        return None

    def _handle_kubernetes_allocation(self, parent_cidr: str, prefixes: Dict[str, int]) -> List[str]:
        pod_cidr = hierarchical_split(parent_cidr, prefixes['pod'])[0]
        service_cidr = hierarchical_split(pod_cidr, prefixes['service'])[0]
        cluster_cidr = hierarchical_split(service_cidr, prefixes['cluster'])[0]
        return [pod_cidr, service_cidr, cluster_cidr]

    def _handle_normal_allocation(self, parent_cidr: str) -> List[str]:
        return [parent_cidr]

    def _update_database(self, cidr_type: str, original_cidr: str, new_cidrs: List[str]):
        with self.db.transaction() as session:
            # Remove original CIDR from available
            self.db.remove_available_cidr(cidr_type, original_cidr)
            
            # Add new subnets to allocated
            for cidr in new_cidrs:
                self.db.insert_allocated(
                    cidr_type=cidr_type,
                    project=os.getenv('GCP_PROJECT'),
                    host_vpc=os.getenv('HOST_VPC'),
                    cidr=cidr,
                    allocated_to='GKE' if cidr_type == 'kubernetes' else 'VM',
                    user=os.getenv('GITLAB_USER_EMAIL')
                )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Allocate CIDR ranges')
    parser.add_argument('--cidr', required=True)
    parser.add_argument('--type', choices=['kubernetes', 'normal'], required=True)
    parser.add_argument('--pod-prefix', type=int)
    parser.add_argument('--service-prefix', type=int)
    parser.add_argument('--cluster-prefix', type=int)
    
    args = parser.parse_args()
    
    allocator = CIDRAllocator()
    result = allocator.allocate(
        args.type,
        args.cidr,
        prefixes={
            'pod': args.pod_prefix,
            'service': args.service_prefix,
            'cluster': args.cluster_prefix
        } if args.type == 'kubernetes' else None
    )
    
    with open('allocation_results.json', 'w') as f:
        json.dump(result, f)
