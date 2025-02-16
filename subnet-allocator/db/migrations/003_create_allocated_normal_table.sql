CREATE TABLE allocated_normal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `GCP_Project` VARCHAR(255) NOT NULL,
    `Host_VPC` VARCHAR(255) NOT NULL,
    `IP_start` INET6 NOT NULL,
    `IP_End` INET6 NOT NULL,
    `CIDR_Range` VARCHAR(18) NOT NULL,
    `Subnet_Allocated_To` ENUM('GKE', 'vm_nodes', 'clusters', 'networks', 'composer') NOT NULL,
    `Create_Date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `Modify_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `Created_by` VARCHAR(255) NOT NULL,
    UNIQUE KEY unique_cidr (`CIDR_Range`, `Host_VPC`)
