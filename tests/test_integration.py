#!/usr/bin/env python3
"""
Integration test script for treeline code quality checkers.
This script tests that the results from quality checkers are properly
integrated into the visualization.
"""

import ast
import json
import tempfile
from collections import defaultdict
from pathlib import Path

from treeline.enhanced_analyzer import EnhancedCodeAnalyzer
from treeline.dependency_analyzer import ModuleDependencyAnalyzer

def create_test_files():
    """Create sample Python files with various quality issues."""
    test_dir = Path(tempfile.mkdtemp())
    print(f"Created test directory: {test_dir}")
    
    complex_file = test_dir / "complex_module.py"
    with open(complex_file, "w") as f:
        f.write("""
# This file has complex functions and magic numbers
def complex_algorithm(data, threshold=0.5):
    result = []
    for i in range(100):  # Magic number
        if data[i] > threshold:
            for j in range(50):  # Magic number
                if i % 2 == 0:
                    if j % 3 == 0:
                        if (i + j) % 5 == 0:
                            result.append(data[i] * 1.5)  # Magic number
                        else:
                            result.append(data[i] * 2.5)  # Magic number
                    else:
                        if (i - j) % 7 == 0:  # Magic number
                            result.append(data[i] / 3.0)  # Magic number
                        else:
                            result.append(data[i] / 2.0)  # Magic number
                else:
                    result.append(data[i])
    return result

def another_complex_function(items, config=None):
    if config is None:
        config = {"max_items": 1000}  # Magic number
    
    results = []
    for idx, item in enumerate(items):
        if idx < config["max_items"]:
            if item.is_valid():
                if item.priority > 5:  # Magic number
                    if item.category == "important":
                        results.append(item.process())
                    else:
                        if item.age < 30:  # Magic number
                            results.append(item.process_with_options())
                        else:
                            results.append(item.quick_process())
                else:
                    if item.size > 500:  # Magic number
                        results.append(item.partial_process())
                    else:
                        results.append(item)
    return results
""")

    security_file = test_dir / "database_module.py"
    with open(security_file, "w") as f:
        f.write("""
# This file has SQL injection and security issues
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.connection_string = "data.db"
        self.password = "admin123"  # Hardcoded credential
        self.api_key = "1a2b3c4d5e6f7g8h9i0j"  # Hardcoded credential
        
    def connect(self):
        return sqlite3.connect(self.connection_string)
    
    def get_user(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        # SQL injection vulnerability
        cursor.execute("SELECT * FROM users WHERE id = " + user_id)
        return cursor.fetchone()
    
    def get_orders(self, customer_id, date_range):
        conn = self.connect()
        cursor = conn.cursor()
        # Another SQL injection vulnerability
        query = f"SELECT * FROM orders WHERE customer_id = {customer_id} AND date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
        cursor.execute(query)
        return cursor.fetchall()
    
    def authenticate(self, username, password):
        conn = self.connect()
        cursor = conn.cursor()
        # Bad password handling and SQL injection
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        return cursor.fetchone() is not None
""")

    for i in range(1, 4):
        duplication_file = test_dir / f"util_module_{i}.py"
        with open(duplication_file, "w") as f:
            f.write("""
# This file contains duplicated code blocks
def format_user_data(user):
    # This code block is duplicated across files
    result = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "is_active": user.is_active,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "date_joined": user.date_joined.isoformat(),
        "groups": [g.name for g in user.groups.all()],
    }
    return result

def process_payment(payment):
    # Some unique code in each file
    return payment.amount * 1.{i}
""")

    smell_file = test_dir / "service_module.py"
    with open(smell_file, "w") as f:
        f.write("""
# This file has code smells like long parameter lists
def create_user_profile(user_id, username, email, first_name, last_name, 
                       date_of_birth, address, city, state, country, 
                       postal_code, phone, bio, avatar_url, is_public,
                       newsletter_opt_in, email_verified, account_type):
    # Too many parameters
    profile = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
        "postal_code": postal_code,
        "phone": phone,
        "bio": bio,
        "avatar_url": avatar_url,
        "is_public": is_public,
        "newsletter_opt_in": newsletter_opt_in,
        "email_verified": email_verified,
        "account_type": account_type
    }
    return profile

class MassiveClass:
    def __init__(self):
        # Class with too many methods and responsibilities
        self.data = {}
        
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
""")

    module_file = test_dir / "__init__.py"
    with open(module_file, "w") as f:
        f.write("""
from .complex_module import complex_algorithm, another_complex_function
from .database_module import DatabaseManager
from .service_module import create_user_profile, MassiveClass

# Import all utils
from .util_module_1 import format_user_data
""")

    return test_dir

def run_integration_test():
    """Run an integration test for all quality checkers."""
    print("\n" + "="*80)
    print("RUNNING INTEGRATION TEST FOR QUALITY CHECKERS")
    print("="*80)
    
    # Create test files
    test_dir = create_test_files()
    
    try:
        # Create enhanced analyzer and analyze files
        analyzer = EnhancedCodeAnalyzer()
        
        print("\nAnalyzing individual files...")
        all_results = []
        
        for py_file in test_dir.glob("**/*.py"):
            print(f"Analyzing {py_file.relative_to(test_dir)}...")
            results = analyzer.analyze_file(py_file)
            all_results.extend(results)
            
            quality_issues = analyzer.quality_issues
            print(f"  Found issues: ", end="")
            for category, issues in quality_issues.items():
                if issues:
                    print(f"{category}({len(issues)}) ", end="")
            print()
        
        print("\nAnalyzing directory for duplication...")
        analyzer.analyze_directory(test_dir)
        
        print("\nAnalyzing module dependencies...")
        dep_analyzer = ModuleDependencyAnalyzer()
        dep_analyzer.analyze_directory(test_dir)
        
        nodes, links = dep_analyzer.get_graph_data()
        
        print("\nVerifying quality issues in graph data nodes...")
        issues_count = 0
        for node in nodes:
            if node.get('code_smells'):
                issues_count += len(node.get('code_smells'))
                print(f"Node '{node['name']}' has {len(node.get('code_smells'))} issues")
                for issue in node.get('code_smells')[:3]:  
                    if isinstance(issue, dict):
                        print(f"  - {issue.get('description')}")
                    else:
                        print(f"  - {issue}")
                
                if len(node.get('code_smells')) > 3:
                    print(f"  - ... and {len(node.get('code_smells')) - 3} more issues")
        
        print(f"\nTotal issues found in graph data: {issues_count}")
        
        visualization_data = {
            "nodes": nodes,
            "links": links
        }
        
        with open(test_dir / "visualization_data.json", "w") as f:
            json.dump(visualization_data, f, indent=2)
        
        print(f"\nSaved visualization data to: {test_dir / 'visualization_data.json'}")
        print("This file can be used to test the visualization display.")
        
        if issues_count > 0:
            print("\n✅ Integration test passed: Quality issues are captured in visualization data")
        else:
            print("\n❌ Integration test failed: No quality issues captured in visualization data")
        
        return test_dir, visualization_data
    
    except Exception as e:
        print(f"\n❌ Error during integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return test_dir, None

def simulate_visualization(visualization_data):
    """Simulate how issues would be displayed in the visualization."""
    print("\n" + "="*80)
    print("SIMULATING VISUALIZATION DISPLAY")
    print("="*80)
    
    nodes_with_issues = [n for n in visualization_data["nodes"] if n.get("code_smells")]
    
    if not nodes_with_issues:
        print("No nodes with quality issues found.")
        return
    
    print(f"Found {len(nodes_with_issues)} nodes with quality issues.\n")
    
    sample_node = nodes_with_issues[0]
    print(f"HOVER SIMULATION FOR NODE: {sample_node['name']}")
    print("-" * 40)
    
    security_issues = []
    complexity_issues = []
    other_issues = []
    
    if sample_node.get("code_smells"):
        for issue in sample_node.get("code_smells"):
            description = issue.get("description") if isinstance(issue, dict) else str(issue)
            
            if any(keyword in description.lower() for keyword in ["sql injection", "credential", "security"]):
                security_issues.append(description)
            elif any(keyword in description.lower() for keyword in ["complex", "too many", "too long"]):
                complexity_issues.append(description)
            else:
                other_issues.append(description)
    
    print(f"{sample_node['name']} ({sample_node['type']})")
    
    if sample_node.get("docstring"):
        print(f"Documentation: {sample_node['docstring']}")
    
    if security_issues:
        print("\n⚠️ SECURITY ISSUES DETECTED:")
        for issue in security_issues[:2]:
            print(f"  • {issue}")
        if len(security_issues) > 2:
            print(f"  • ...and {len(security_issues) - 2} more security issues")
    
    if complexity_issues:
        print("\n⚠️ COMPLEXITY ISSUES DETECTED:")
        for issue in complexity_issues[:2]:
            print(f"  • {issue}")
        if len(complexity_issues) > 2:
            print(f"  • ...and {len(complexity_issues) - 2} more complexity issues")
    
    if other_issues:
        print("\n⚠️ OTHER ISSUES DETECTED:")
        for issue in other_issues[:2]:
            print(f"  • {issue}")
        if len(other_issues) > 2:
            print(f"  • ...and {len(other_issues) - 2} more issues")
    
    if sample_node.get("metrics"):
        print("\nMetrics Summary:")
        for key, value in list(sample_node["metrics"].items())[:3]:
            print(f"  • {key}: {value}")
    
    print("\n\nCLICK SIMULATION FOR NODE: {sample_node['name']}")
    print("-" * 40)
    print("DETAILED VIEW:\n")
    
    print(f"# {sample_node['name']}")
    print(f"Type: {sample_node['type']}")
    
    if sample_node.get("docstring"):
        print(f"\nDocumentation: {sample_node['docstring']}")
    
    print("\n## Quality Issues")
    
    if security_issues:
        print("\n### Security Issues")
        for i, issue in enumerate(security_issues):
            print(f"{i+1}. {issue}")
    
    if complexity_issues:
        print("\n### Complexity Issues")
        for i, issue in enumerate(complexity_issues):
            print(f"{i+1}. {issue}")
    
    if other_issues:
        print("\n### Other Issues")
        for i, issue in enumerate(other_issues):
            print(f"{i+1}. {issue}")
    
    if sample_node.get("metrics"):
        print("\n## Detailed Metrics")
        for key, value in sample_node["metrics"].items():
            print(f"* {key}: {value}")
    
    incoming_links = [l for l in visualization_data["links"] if l["target"] == sample_node["id"]]
    outgoing_links = [l for l in visualization_data["links"] if l["source"] == sample_node["id"]]
    
    if incoming_links or outgoing_links:
        print("\n## Dependencies")
        
        if incoming_links:
            print(f"\n### Incoming ({len(incoming_links)})")
            for i, link in enumerate(incoming_links[:3]):
                source_node = next((n for n in visualization_data["nodes"] if n["id"] == link["source"]), None)
                if source_node:
                    print(f"{i+1}. {link['type']} from {source_node['name']}")
            if len(incoming_links) > 3:
                print(f"...and {len(incoming_links) - 3} more")
        
        if outgoing_links:
            print(f"\n### Outgoing ({len(outgoing_links)})")
            for i, link in enumerate(outgoing_links[:3]):
                target_node = next((n for n in visualization_data["nodes"] if n["id"] == link["target"]), None)
                if target_node:
                    print(f"{i+1}. {link['type']} to {target_node['name']}")
            if len(outgoing_links) > 3:
                print(f"...and {len(outgoing_links) - 3} more")

if __name__ == "__main__":
    test_dir, visualization_data = run_integration_test()
    
    if visualization_data:
        simulate_visualization(visualization_data)
        
        print("\n" + "="*80)
        print(f"Test files are available for inspection at: {test_dir}")
        print("You can use the visualization_data.json file to test the actual visualization.")
        print("="*80)