import ipaddress
from typing import List, Optional

def split_cidr(parent_cidr: str, new_prefix: int) -> List[str]:
    """Split a parent CIDR into subnets of specified prefix length"""
    network = ipaddress.ip_network(parent_cidr)
    return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)]

def find_available_cidr(available_cidrs: List[str], required_prefix: int) -> Optional[str]:
    """Find first available CIDR that can accommodate the required prefix"""
    for cidr in available_cidrs:
        network = ipaddress.ip_network(cidr)
        if network.prefixlen <= required_prefix:
            return cidr
    return None

def hierarchical_split(parent_cidr: str, target_prefix: int) -> List[str]:
    """Hierarchically split CIDR until target prefix is achieved using binary division"""
    network = ipaddress.ip_network(parent_cidr)
    
    if network.prefixlen > target_prefix:
        raise ValueError("Target prefix must be larger than parent prefix")
    
    all_subnets = []
    current_subnets = [str(network)]
    current_prefix = network.prefixlen
    
    while current_prefix < target_prefix:
        # Split each subnet in current level and collect all new subnets
        new_subnets = []
        for subnet in current_subnets:
            new_subnets.extend(split_cidr(subnet, current_prefix + 1))
        
        all_subnets.extend(current_subnets)
        current_subnets = new_subnets
        current_prefix += 1
    
    # Add final level subnets
    all_subnets.extend(current_subnets)
    
    return all_subnets



# import ipaddress
# from typing import List, Optional

# def split_cidr(parent_cidr: str, new_prefix: int) -> List[str]:
#     """Split a parent CIDR into subnets of specified prefix length"""
#     network = ipaddress.ip_network(parent_cidr)
#     return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)]

# def find_available_cidr(available_cidrs: List[str], required_prefix: int) -> Optional[str]:
#     """Find first available CIDR that can accommodate the required prefix"""
#     for cidr in available_cidrs:
#         network = ipaddress.ip_network(cidr)
#         if network.prefixlen <= required_prefix:
#             return cidr
#     return None

# def hierarchical_split(parent_cidr: str, target_prefix: int) -> List[str]:
#     """Hierarchically split CIDR until target prefix is achieved using binary division"""
#     network = ipaddress.ip_network(parent_cidr)
    
#     if network.prefixlen > target_prefix:
#         raise ValueError("Target prefix must be larger than parent prefix")
    
#     subnets = [str(network)]
    
#     # Split binary hierarchically (each split creates exactly two subnets)
#     current_prefix = network.prefixlen
#     while current_prefix < target_prefix:
#         subnets = split_cidr(subnets[0], current_prefix + 1)
#         current_prefix += 1
        
#     return subnets

# def validate_cidr_hierarchy(parent_cidr: str, child_cidr: str) -> bool:
#     """Verify if child CIDR is properly contained within parent"""
#     parent_net = ipaddress.ip_network(parent_cidr)
#     child_net = ipaddress.ip_network(child_cidr)
#     return child_net.subnet_of(parent_net)
