CREATE TABLE available_kubernetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_vpc VARCHAR(255) NOT NULL,
    ip_start INET6 NOT NULL,
    ip_end INET6 NOT NULL,
    cidr_range VARCHAR(18) NOT NULL,
    create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    modify_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_cidr (cidr_range, host_vpc)
);