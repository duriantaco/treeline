#!/usr/bin/env python3
"""
Test script for treeline code quality checkers.
This script creates sample problematic code files and verifies that 
all quality checkers correctly identify the issues.
"""

import ast
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from treeline.checkers.security import SecurityAnalyzer 
from treeline.checkers.sql_injection import SQLInjectionChecker
from treeline.checkers.duplication import DuplicationDetector
from treeline.checkers.complexity import ComplexityAnalyzer
from treeline.checkers.code_smells import CodeSmellChecker

def create_test_file(content, filename="test_file.py"):
    """Create a temporary file with the given content for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        return Path(f.name)

def run_test(title, file_content, checker_class, expected_category=None, expected_count=None):
    """Run a test using a specific checker on the given file content."""
    print(f"\n{'='*80}")
    print(f"TEST: {title}")
    print(f"{'='*80}")
    
    test_file = create_test_file(file_content)
    print(f"Created test file: {test_file}")
    
    try:
        with open(test_file, 'r') as f:
            tree = ast.parse(f.read())
        
        quality_issues = defaultdict(list)
        
        checker = checker_class()
        
        if isinstance(checker, DuplicationDetector):
            test_dir = tempfile.mkdtemp()
            for i in range(3):
                with open(os.path.join(test_dir, f"file{i}.py"), 'w') as f:
                    f.write(file_content)
            checker.analyze_directory(Path(test_dir), quality_issues)
        else:
            checker.check(tree, test_file, quality_issues)
        
        print("\nQuality Issues Found:")
        for category, issues in quality_issues.items():
            print(f"\n{category.upper()} ({len(issues)} issues):")
            for i, issue in enumerate(issues):
                if isinstance(issue, dict):
                    print(f"  {i+1}. {issue.get('description', 'Unknown issue')} - Line: {issue.get('line', 'N/A')}")
                else:
                    print(f"  {i+1}. {issue}")
        
        if expected_category:
            assert expected_category in quality_issues, f"Expected category '{expected_category}' not found in results"
            if expected_count is not None:
                assert len(quality_issues[expected_category]) >= expected_count, \
                    f"Expected at least {expected_count} issues in '{expected_category}', but found {len(quality_issues[expected_category])}"
            print(f"\n✅ Test passed: Found expected issues in '{expected_category}'")
        
        return quality_issues
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        raise
    finally:
        if test_file.exists():
            os.unlink(test_file)
            print(f"Removed test file: {test_file}")

def test_all_checkers():
    """Run tests for all quality checkers."""
    
    # Test 2: Security Analyzer (Hardcoded Credentials)
    security_code = """
def connect_to_db():
    username = "admin"
    password = "super_secret_password"  # hardcoded credential
    conn = db.connect(username, password)
    return conn

API_KEY = "1a2b3c4d5e6f7g8h"  # hardcoded credential
SECRET_KEY = get_env_var("SECRET_KEY")  # This is good

def get_aws_credentials():
    return {
        "access_key": "AKIAIOSFODNN7EXAMPLE",  # hardcoded credential
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # hardcoded credential
    }
    """
    run_test("Security Issues Detection", security_code, SecurityAnalyzer, "security", 3)
    
    # Test 3: SQL Injection Checker
    sql_injection_code = """
def get_user(user_id):
    cursor = conn.cursor()
    # BAD: SQL injection vulnerability
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    return cursor.fetchone()

def safe_get_user(user_id):
    cursor = conn.cursor()
    # GOOD: Parameterized query
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

def another_bad_query(table_name, condition):
    query = f"SELECT * FROM {table_name} WHERE {condition}"
    # BAD: SQL injection vulnerability
    cursor.execute(query)
    return cursor.fetchall()
    """
    run_test("SQL Injection Detection", sql_injection_code, SQLInjectionChecker, "security", 2)
    
    # Test 4: Duplication Detector
    duplicated_code = """
def process_user_data(user):
    # This code block will be duplicated across multiple files
    if user.is_active:
        user.last_login = datetime.now()
        user.login_count += 1
        user.save()
        log_activity(user, "login")
        notify_user(user, "login_notification")
        return True
    return False

def another_function():
    x = 1 + 2
    y = 3 * 4
    return x + y
    """
    run_test("Code Duplication Detection", duplicated_code, DuplicationDetector, "duplication")
    
    # Test 5: Complexity Analyzer
    complex_code = """
def complex_function(data, threshold=0.5, mode='strict', retry=True, debug=False):
    result = []
    for item in data:
        if item.value > threshold:
            if item.type == 'A':
                if mode == 'strict':
                    if item.quality > 0.8:
                        result.append(item)
                    else:
                        if debug:
                            print(f"Rejected {item} - low quality")
                elif mode == 'lenient':
                    if item.quality > 0.5:
                        result.append(item)
                    else:
                        if retry and item.can_retry:
                            reprocessed = reprocess(item)
                            if reprocessed.quality > 0.5:
                                result.append(reprocessed)
                            else:
                                if debug:
                                    print(f"Rejected {item} - retry failed")
                        else:
                            if debug:
                                print(f"Rejected {item} - no retry")
                else:
                    raise ValueError(f"Unknown mode: {mode}")
            elif item.type == 'B':
                if item.age < 7:
                    if item.processed:
                        if item.verified:
                            result.append(item)
                        else:
                            if verify(item):
                                result.append(item)
                            else:
                                if debug:
                                    print(f"Rejected {item} - verification failed")
                    else:
                        if process(item):
                            if verify(item):
                                result.append(item)
                            else:
                                if debug:
                                    print(f"Rejected {item} - verification failed after processing")
                        else:
                            if debug:
                                print(f"Rejected {item} - processing failed")
                else:
                    if debug:
                        print(f"Rejected {item} - too old")
            else:
                if debug:
                    print(f"Rejected {item} - unknown type")
        else:
            if debug:
                print(f"Rejected {item} - below threshold")
    return result
    """
    run_test("Code Complexity Detection", complex_code, ComplexityAnalyzer, "complexity", 1)
    
    # Test 6: Code Smells
    code_smells_code = """
def process_data(a, b, c, d, e, f, g, h):  # too many parameters
    # Long function with magic numbers
    timeout = 5000  # magic number
    retries = 3     # magic number
    
    if a > 10:      # magic number
        return a * 2.5  # magic number
    
    data = [1, 2, 3, 4, 5]  # magic numbers
    
    return (a + b + c + d + e + f + g + h) / 8  # magic number

class BigClass:
    def __init__(self):
        self.data1 = []
        self.data2 = []
        # ... many more attributes
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    # ... many more methods
    """
    run_test("Code Smells Detection", code_smells_code, CodeSmellChecker, "code_smells", 2)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_all_checkers()