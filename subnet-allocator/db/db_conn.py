import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import List

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine(
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
            f"{os.getenv('DB_PRIVATE_IP')}:{os.getenv('DB_PORT')}/ccoe_subnets?"
            f"unix_socket=/cloudsql/{os.getenv('INSTANCE_CONNECTION_NAME')}&"
            f"ssl_ca={os.getenv('SSL_CA')}&ssl_cert={os.getenv('SSL_CERT')}&ssl_key={os.getenv('SSL_KEY')}",
            pool_size=10,
            pool_recycle=3600,
            echo_pool=True
        )
        self.session_factory = sessionmaker(bind=self.engine)
        
    @contextmanager
    def transaction(self):
        session = scoped_session(self.session_factory)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            session.remove()

    def get_available_cidrs(self, cidr_type: str) -> List[str]:
        with self.transaction() as session:
            table = 'available_kubernetes' if cidr_type == 'kubernetes' else 'available_normal'
            result = session.execute(text(f"SELECT cidr_range FROM {table}"))
            return [row[0] for row in result.fetchall()]

    def insert_allocated(self, cidr_type: str, project: str, host_vpc: str, 
                       cidr: str, allocated_to: str, user: str):
        table = 'allocated_kubernetes' if cidr_type == 'kubernetes' else 'allocated_normal'
        with self.transaction() as session:
            session.execute(text(f"""
                INSERT INTO {table} 
                (gcp_project, host_vpc, cidr_range, subnet_allocated_to, created_by)
                VALUES (:project, :host_vpc, :cidr, :allocated_to, :user)
            """), {'project': project, 'host_vpc': host_vpc, 'cidr': cidr, 
                  'allocated_to': allocated_to, 'user': user})

    def remove_available_cidr(self, cidr_type: str, cidr: str):
        table = 'available_kubernetes' if cidr_type == 'kubernetes' else 'available_normal'
        with self.transaction() as session:
            session.execute(text(f"""
                DELETE FROM {table} 
                WHERE cidr_range = :cidr
            """), {'cidr': cidr})

    def insert_available(self, cidr_type: str, cidr: str):
        table = 'available_kubernetes' if cidr_type == 'kubernetes' else 'available_normal'
        with self.transaction() as session:
            session.execute(text(f"""
                INSERT INTO {table} (cidr_range)
                VALUES (:cidr)
                ON DUPLICATE KEY UPDATE modify_date=NOW()
            """), {'cidr': cidr})
