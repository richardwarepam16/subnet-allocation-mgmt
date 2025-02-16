from typing import Dict, Optional
from .cidr_utils import find_available_cidr, hierarchical_split
from db.db_conn import DatabaseConnection

class NormalAllocator:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def allocate(self, project: str, host_vpc: str, required_prefix: int, user: str) -> Dict:
        """Allocate a normal subnet"""
        with self.db.transaction():
            # Find available CIDR
            available_cidrs = self.db.get_available_cidrs('normal')
            parent_cidr = find_available_cidr(available_cidrs, required_prefix)
            
            if not parent_cidr:
                raise ValueError(f"No available CIDR found for /{required_prefix} in {host_vpc}")

            # Split only as much as needed
            split_depth = required_prefix - parent_cidr.prefix
            current_block = parent_cidr
            allocated_cidr = None

            # Remove parent block first
            self.db.remove_available_cidr('normal', parent_cidr)

            # Split hierarchically until we reach required depth
            for _ in range(split_depth):
                subnets = current_block.split()
                # Take first subnet for further splitting or allocation
                candidate = subnets[0]

                if candidate.prefix == required_prefix:
                    allocated_cidr = candidate
                    # Store the other unused subnets as available
                    for unused_subnet in subnets[1:]:
                        self.db.insert_available('normal', unused_subnet, current_block)
                    break
                else:
                    # Store the other unused subnets as available
                    for unused_subnet in subnets[1:]:
                        self.db.insert_available('normal', unused_subnet, current_block)
                    current_block = candidate

            if not allocated_cidr:
                allocated_cidr = current_block

            # Store allocation
            self.db.insert_allocated(
                'normal',
                project,
                host_vpc,
                allocated_cidr,
                'subnet',
                user,
                parent_cidr
            )

            return {
                "project": project,
                "host_vpc": host_vpc,
                "allocated_cidr": allocated_cidr,
                "remaining_subnets": subnets[1:]
            }
