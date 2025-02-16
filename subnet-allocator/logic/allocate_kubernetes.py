from typing import Dict, List
from .cidr_utils import hierarchical_split, validate_cidr_hierarchy
from db.db_conn import DatabaseConnection
import ipaddress

class KubernetesAllocator:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        
    def allocate(self, project: str, host_vpc: str, requirements: Dict, user: str) -> Dict:
        """Allocate Kubernetes subnets with 3 required ranges"""
        with self.db.transaction():
            # Get required prefixes from user input
            primary_prefix = requirements['primary']
            services_prefix = requirements['services']
            pods_prefix = requirements['pods']
            
            # Find parent CIDR that can accommodate largest required prefix
            available_cidrs = self.db.get_available_cidrs('kubernetes')
            parent_cidr = self._find_parent_cidr(available_cidrs, max(primary_prefix, services_prefix, pods_prefix))
            
            if not parent_cidr:
                raise ValueError(f"No available CIDR in {host_vpc} for Kubernetes requirements")

            # Split parent CIDR hierarchically
            primary_subnets = hierarchical_split(parent_cidr, primary_prefix)
            primary_cidr = primary_subnets[0]
            
            services_subnets = hierarchical_split(primary_cidr, services_prefix)
            services_cidr = services_subnets[0]
            
            pods_subnets = hierarchical_split(primary_cidr, pods_prefix)
            pods_cidr = pods_subnets[0]

            # Validate hierarchy
            if not all([
                validate_cidr_hierarchy(parent_cidr, primary_cidr),
                validate_cidr_hierarchy(primary_cidr, services_cidr),
                validate_cidr_hierarchy(primary_cidr, pods_cidr)
            ]):
                raise ValueError("CIDR hierarchy validation failed")

            # Update database
            self.db.remove_available_cidr('kubernetes', parent_cidr)
            self._update_allocations(project, host_vpc, primary_cidr, services_cidr, pods_cidr, user)
            self._update_available_subnets(primary_subnets, services_subnets, pods_subnets)

            return {
                "primary": primary_cidr,
                "services": services_cidr,
                "pods": pods_cidr,
                "host_vpc": host_vpc
            }

    def _find_parent_cidr(self, available_cidrs: List[str], min_prefix: int) -> str:
        for cidr in sorted(available_cidrs, key=lambda x: ipaddress.ip_network(x).prefixlen):
            if ipaddress.ip_network(cidr).prefixlen <= min_prefix:
                return cidr
        return ""

    def _update_allocations(self, project: str, host_vpc: str, 
                          primary: str, services: str, pods: str, user: str):
        # Store all allocated ranges
        self.db.insert_allocated('kubernetes', project, host_vpc, primary, 'primary', user)
        self.db.insert_allocated('kubernetes', project, host_vpc, services, 'services', user)
        self.db.insert_allocated('kubernetes', project, host_vpc, pods, 'pods', user)

    def _update_available_subnets(self, primary_subnets: List[str],
                                services_subnets: List[str], pods_subnets: List[str]):
        # Add unused subnets back to available pool
        for subnet in primary_subnets[1:]:
            self.db.insert_available('kubernetes', subnet)
        for subnet in services_subnets[1:]:
            self.db.insert_available('kubernetes', subnet)
        for subnet in pods_subnets[1:]:
            self.db.insert_available('kubernetes', subnet)