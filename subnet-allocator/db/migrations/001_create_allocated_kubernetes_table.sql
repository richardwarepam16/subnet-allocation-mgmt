CREATE TABLE allocated_kubernetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gcp_project VARCHAR(255) NOT NULL,
    host_vpc VARCHAR(255) NOT NULL,
    ip_start INET6 NOT NULL,
    ip_end INET6 NOT NULL,
    cidr_range VARCHAR(18) NOT NULL,
    subnet_allocated_to ENUM('GKE', 'vm_nodes', 'clusters', 'networks', 'composer') NOT NULL,
    create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    UNIQUE KEY unique_cidr (cidr_range, host_vpc)
);