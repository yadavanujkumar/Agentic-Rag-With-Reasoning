"""
Sample Data Loader for Financial Fraud Detection Graph

This script creates realistic sample data in Neo4j to demonstrate
the Agentic GraphRAG system's capabilities.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from datetime import datetime, timedelta
import random

load_dotenv()


class FraudDataLoader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def create_constraints(self):
        """Create uniqueness constraints"""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.company_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transaction_id IS UNIQUE",
            ]
            for constraint in constraints:
                session.run(constraint)
            print("✓ Constraints created")
    
    def load_sample_data(self):
        """Load sample fraud detection data"""
        with self.driver.session() as session:
            # Create Persons
            persons = [
                {"person_id": "P001", "name": "Alice Johnson", "ssn": "XXX-XX-1234", "risk_level": "low"},
                {"person_id": "P002", "name": "Bob Smith", "ssn": "XXX-XX-2345", "risk_level": "medium"},
                {"person_id": "P003", "name": "Charlie Brown", "ssn": "XXX-XX-3456", "risk_level": "high"},
                {"person_id": "P004", "name": "Diana Prince", "ssn": "XXX-XX-4567", "risk_level": "low"},
                {"person_id": "P005", "name": "Eve Chen", "ssn": "XXX-XX-5678", "risk_level": "high"},
                {"person_id": "P006", "name": "Frank Miller", "ssn": "XXX-XX-6789", "risk_level": "medium"},
            ]
            
            for person in persons:
                session.run("""
                    CREATE (p:Person {
                        person_id: $person_id,
                        name: $name,
                        ssn: $ssn,
                        risk_level: $risk_level
                    })
                """, person)
            print(f"✓ Created {len(persons)} persons")
            
            # Create Companies
            companies = [
                {"company_id": "C001", "name": "TechCorp Inc", "ein": "12-3456789", "industry": "Technology", "is_suspicious": False},
                {"company_id": "C002", "name": "ShellCo LLC", "ein": "98-7654321", "industry": "Financial Services", "is_suspicious": True},
            ]
            
            for company in companies:
                session.run("""
                    CREATE (c:Company {
                        company_id: $company_id,
                        name: $name,
                        ein: $ein,
                        industry: $industry,
                        is_suspicious: $is_suspicious
                    })
                """, company)
            print(f"✓ Created {len(companies)} companies")
            
            # Create Accounts
            accounts = [
                {"account_id": "ACC001", "account_type": "checking", "balance": 15000.00, "risk_score": 0.2},
                {"account_id": "ACC002", "account_type": "savings", "balance": 50000.00, "risk_score": 0.1},
                {"account_id": "ACC003", "account_type": "checking", "balance": 5000.00, "risk_score": 0.8},
                {"account_id": "ACC004", "account_type": "checking", "balance": 2000.00, "risk_score": 0.9},
                {"account_id": "ACC005", "account_type": "business", "balance": 100000.00, "risk_score": 0.3},
                {"account_id": "ACC006", "account_type": "checking", "balance": 8000.00, "risk_score": 0.7},
                {"account_id": "ACC007", "account_type": "savings", "balance": 25000.00, "risk_score": 0.4},
                {"account_id": "ACC008", "account_type": "checking", "balance": 3000.00, "risk_score": 0.85},
            ]
            
            for account in accounts:
                session.run("""
                    CREATE (a:Account {
                        account_id: $account_id,
                        account_type: $account_type,
                        balance: $balance,
                        risk_score: $risk_score,
                        created_at: datetime()
                    })
                """, account)
            print(f"✓ Created {len(accounts)} accounts")
            
            # Create Addresses
            addresses = [
                {"address_id": "ADDR001", "street": "123 Main St", "city": "New York", "state": "NY", "zip_code": "10001"},
                {"address_id": "ADDR002", "street": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "zip_code": "90001"},
                {"address_id": "ADDR003", "street": "789 Pine Rd", "city": "Chicago", "state": "IL", "zip_code": "60601"},
                {"address_id": "ADDR004", "street": "321 Elm St", "city": "Houston", "state": "TX", "zip_code": "77001"},
            ]
            
            for address in addresses:
                session.run("""
                    CREATE (addr:Address {
                        address_id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip_code: $zip_code
                    })
                """, address)
            print(f"✓ Created {len(addresses)} addresses")
            
            # Create Phone Numbers
            phones = [
                {"phone_id": "PH001", "number": "+1-555-0101", "verified": True},
                {"phone_id": "PH002", "number": "+1-555-0102", "verified": True},
                {"phone_id": "PH003", "number": "+1-555-0103", "verified": False},
                {"phone_id": "PH004", "number": "+1-555-0104", "verified": True},
            ]
            
            for phone in phones:
                session.run("""
                    CREATE (ph:PhoneNumber {
                        phone_id: $phone_id,
                        number: $number,
                        verified: $verified
                    })
                """, phone)
            print(f"✓ Created {len(phones)} phone numbers")
            
            # Create OWNS relationships (Person -> Account)
            ownerships = [
                ("P001", "ACC001", 100.0),
                ("P001", "ACC002", 100.0),  # Alice owns 2 accounts
                ("P002", "ACC003", 100.0),
                ("P003", "ACC004", 100.0),
                ("P003", "ACC006", 100.0),  # Charlie owns 2 accounts (suspicious)
                ("P004", "ACC007", 100.0),
                ("P005", "ACC008", 100.0),
                ("C002", "ACC005", 100.0),  # Suspicious company owns account
            ]
            
            for owner_id, account_id, percentage in ownerships:
                session.run("""
                    MATCH (owner) WHERE owner.person_id = $owner_id OR owner.company_id = $owner_id
                    MATCH (a:Account {account_id: $account_id})
                    CREATE (owner)-[:OWNS {ownership_percentage: $percentage, since: datetime()}]->(a)
                """, {"owner_id": owner_id, "account_id": account_id, "percentage": percentage})
            print(f"✓ Created {len(ownerships)} ownership relationships")
            
            # Create SENT_MONEY relationships (demonstrating suspicious patterns)
            transactions = [
                # Normal transactions
                ("ACC001", "ACC002", "TXN001", 1000.00, "transfer"),
                ("ACC007", "ACC001", "TXN002", 500.00, "payment"),
                
                # Circular flow (SUSPICIOUS): ACC003 -> ACC004 -> ACC006 -> ACC003
                ("ACC003", "ACC004", "TXN003", 5000.00, "wire"),
                ("ACC004", "ACC006", "TXN004", 4800.00, "transfer"),
                ("ACC006", "ACC003", "TXN005", 4500.00, "wire"),
                
                # Money mule pattern: Multiple small transactions
                ("ACC008", "ACC003", "TXN006", 2000.00, "transfer"),
                ("ACC008", "ACC004", "TXN007", 1500.00, "transfer"),
                
                # Large transaction from suspicious company
                ("ACC005", "ACC006", "TXN008", 50000.00, "business_payment"),
            ]
            
            for from_acc, to_acc, txn_id, amount, purpose in transactions:
                session.run("""
                    MATCH (from:Account {account_id: $from_acc})
                    MATCH (to:Account {account_id: $to_acc})
                    CREATE (from)-[:SENT_MONEY {
                        transaction_id: $txn_id,
                        amount: $amount,
                        timestamp: datetime(),
                        purpose: $purpose
                    }]->(to)
                """, {
                    "from_acc": from_acc,
                    "to_acc": to_acc,
                    "txn_id": txn_id,
                    "amount": amount,
                    "purpose": purpose
                })
            print(f"✓ Created {len(transactions)} transaction relationships")
            
            # Create LOCATED_AT relationships
            locations = [
                ("P001", "ADDR001", "home"),
                ("P002", "ADDR002", "home"),
                ("P003", "ADDR003", "home"),
                ("P004", "ADDR003", "home"),  # Same address as P003 (SUSPICIOUS)
                ("P005", "ADDR004", "home"),
                ("P006", "ADDR003", "home"),  # Same address (SUSPICIOUS - 3 people)
                ("C002", "ADDR004", "business"),  # Suspicious company
            ]
            
            for entity_id, addr_id, addr_type in locations:
                session.run("""
                    MATCH (entity) WHERE entity.person_id = $entity_id OR entity.company_id = $entity_id
                    MATCH (addr:Address {address_id: $addr_id})
                    CREATE (entity)-[:LOCATED_AT {address_type: $addr_type, since: datetime()}]->(addr)
                """, {"entity_id": entity_id, "addr_id": addr_id, "addr_type": addr_type})
            print(f"✓ Created {len(locations)} location relationships")
            
            # Create HAS_PHONE relationships
            phone_links = [
                ("P001", "PH001", "mobile"),
                ("P002", "PH002", "mobile"),
                ("P003", "PH003", "mobile"),
                ("P005", "PH003", "mobile"),  # Same phone as P003 (SUSPICIOUS)
                ("P004", "PH004", "mobile"),
            ]
            
            for entity_id, phone_id, phone_type in phone_links:
                session.run("""
                    MATCH (entity) WHERE entity.person_id = $entity_id OR entity.company_id = $entity_id
                    MATCH (ph:PhoneNumber {phone_id: $phone_id})
                    CREATE (entity)-[:HAS_PHONE {phone_type: $phone_type, since: datetime()}]->(ph)
                """, {"entity_id": entity_id, "phone_id": phone_id, "phone_type": phone_type})
            print(f"✓ Created {len(phone_links)} phone relationships")
            
            # Create ASSOCIATED_WITH relationships
            associations = [
                ("P003", "P005", "known_associates", 0.8),
                ("P003", "P006", "family", 0.9),
            ]
            
            for p1, p2, rel_type, confidence in associations:
                session.run("""
                    MATCH (p1:Person {person_id: $p1})
                    MATCH (p2:Person {person_id: $p2})
                    CREATE (p1)-[:ASSOCIATED_WITH {relationship_type: $rel_type, confidence: $confidence}]->(p2)
                """, {"p1": p1, "p2": p2, "rel_type": rel_type, "confidence": confidence})
            print(f"✓ Created {len(associations)} association relationships")
    
    def print_statistics(self):
        """Print database statistics"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(*) as count
                ORDER BY count DESC
            """)
            
            print("\n" + "="*60)
            print("DATABASE STATISTICS")
            print("="*60)
            for record in result:
                print(f"  {record['type']}: {record['count']}")
            
            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            
            print("\nRelationships:")
            for record in rel_result:
                print(f"  {record['type']}: {record['count']}")
            print("="*60 + "\n")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FRAUD DETECTION DATA LOADER")
    print("="*60 + "\n")
    
    # Get Neo4j credentials
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not password:
        print("ERROR: NEO4J_PASSWORD not set in .env file")
        return
    
    print(f"Connecting to Neo4j at {uri}...")
    
    try:
        loader = FraudDataLoader(uri, user, password)
        
        # Clear and load data
        print("\nClearing existing data...")
        loader.clear_database()
        
        print("\nCreating constraints...")
        loader.create_constraints()
        
        print("\nLoading sample data...")
        loader.load_sample_data()
        
        print("\nData loading complete!")
        loader.print_statistics()
        
        print("\n✓ Sample fraud detection data loaded successfully!")
        print("\nSuspicious patterns in the data:")
        print("  1. Circular money flow: ACC003 -> ACC004 -> ACC006 -> ACC003")
        print("  2. Multiple accounts owned by same person (P003)")
        print("  3. Multiple persons sharing same address (ADDR003)")
        print("  4. Multiple persons sharing same phone (PH003)")
        print("  5. High-risk accounts (ACC003, ACC004, ACC006, ACC008)")
        print("\nYou can now run agent.py to query this data!\n")
        
        loader.close()
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Neo4j is running and credentials are correct in .env file")


if __name__ == "__main__":
    main()
