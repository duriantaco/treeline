#!/usr/bin/env python3
"""
Deliberately problematic Python file for testing code quality analyzers.
This file contains many code quality issues:
- Magic numbers
- SQL injection vulnerabilities
- Hardcoded credentials
- Complex methods
- Methods with too many parameters
- Code duplication
"""

import json
import os
import sqlite3
from datetime import datetime


# ---- Magic numbers throughout the file ----
def calculate_area(radius):
    return 3.14159 * radius * radius  

def calculate_timeout(factor):
    base_timeout = 30000  
    return factor * base_timeout

def set_default_batch_size():
    return 1000  

def calculate_discount(price):
    if price > 100:  
        return price * 0.15  
    else:
        return price * 0.05  


# ---- Hardcoded credentials ----
API_KEY = "1a2b3c4d5e6f7g8h9i0j"  
SECRET_KEY = "super_secret_token_value_do_not_share"  

def get_database_connection():
    connection_string = "postgresql://admin:password123@localhost:5432/mydb"  
    return connection_string
    
def authenticate_user(username, password):  
    admin_password = "admin123"  
    if username == "admin" and password == admin_password:
        return True
    return False


# ---- SQL Injection vulnerabilities ----
def unsafe_get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    return cursor.fetchone()

def unsafe_search_orders(conn, customer_name, date_range):
    cursor = conn.cursor()
    query = f"SELECT * FROM orders WHERE customer_name LIKE '%{customer_name}%' AND order_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    cursor.execute(query)
    return cursor.fetchall()

def unsafe_update_status(conn, table, id_value, new_status):
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table} SET status = '{new_status}' WHERE id = {id_value}")
    conn.commit()


# ---- Extremely complex function with deep nesting ----
def process_data(data, options=None):
    if options is None:
        options = {"max_items": 1000, "min_value": 10, "mode": "normal"}
    
    results = []
    for i, item in enumerate(data):
        if i < options["max_items"]:
            if item["value"] > options["min_value"]:
                if item["type"] == "A":
                    if options["mode"] == "normal":
                        if item["quality"] > 0.8:
                            if item["status"] == "active":
                                processed = {"id": item["id"], "result": item["value"] * 2}
                                if processed["result"] > 100:
                                    if item["priority"] == "high":
                                        processed["category"] = "important"
                                    else:
                                        processed["category"] = "standard"
                                else:
                                    processed["category"] = "low"
                                results.append(processed)
                            else:
                                if options.get("include_inactive", False):
                                    results.append({"id": item["id"], "result": 0, "category": "inactive"})
                        else:
                            if options.get("include_low_quality", False):
                                results.append({"id": item["id"], "result": item["value"], "category": "low_quality"})
                    elif options["mode"] == "aggressive":
                        if item["age"] < 30:
                            results.append({"id": item["id"], "result": item["value"] * 3, "category": "aggressive"})
                        else:
                            if item["usage"] > 10:
                                results.append({"id": item["id"], "result": item["value"] * 2, "category": "aggressive_medium"})
                            else:
                                results.append({"id": item["id"], "result": item["value"] * 1.5, "category": "aggressive_low"})
                elif item["type"] == "B":
                    if item["flag"]:
                        if item["region"] == "EU":
                            if datetime.now().year - item["year"] < 5:
                                results.append({"id": item["id"], "result": item["value"] / 1.2, "category": "EU_recent"})
                            else:
                                results.append({"id": item["id"], "result": item["value"] / 1.5, "category": "EU_old"})
                        else:
                            if item["special"]:
                                results.append({"id": item["id"], "result": item["value"] / 1.1, "category": "special"})
                            else:
                                results.append({"id": item["id"], "result": item["value"], "category": "normal"})
    return results


# ---- Function with too many parameters ----
def create_user_profile(user_id, username, email, first_name, last_name, 
                       date_of_birth, address, city, state, country, 
                       postal_code, phone, bio, avatar_url, is_public,
                       newsletter_opt_in, email_verified, account_type,
                       security_question, security_answer, language_preference):
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
        "account_type": account_type,
        "security_question": security_question,
        "security_answer": security_answer,
        "language_preference": language_preference
    }
    return profile


# ---- Duplicated code blocks ----
def process_user_data(user):
    if user.is_active:
        user.last_login = datetime.now()
        user.login_count += 1
        user.save()
        
        log_entry = {
            "user_id": user.id,
            "action": "login",
            "timestamp": datetime.now().isoformat(),
            "ip_address": user.last_ip,
            "user_agent": user.user_agent,
            "session_id": user.session_id
        }
        
        with open("user_logs.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        if user.notifications_enabled:
            send_notification(user.email, "New login detected", {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": user.last_ip,
                "location": get_location_from_ip(user.last_ip)
            })
            
        return True
    return False

def process_admin_login(admin):
    if admin.is_active:
        admin.last_login = datetime.now()
        admin.login_count += 1
        admin.save()
        
        log_entry = {
            "user_id": admin.id,
            "action": "login",
            "timestamp": datetime.now().isoformat(),
            "ip_address": admin.last_ip,
            "user_agent": admin.user_agent,
            "session_id": admin.session_id
        }
        
        with open("admin_logs.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        if admin.notifications_enabled:
            send_notification(admin.email, "New admin login detected", {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": admin.last_ip,
                "location": get_location_from_ip(admin.last_ip)
            })
            
        return True
    return False

def log_system_access(system_user):
    if system_user.is_active:
        system_user.last_login = datetime.now()
        system_user.login_count += 1
        system_user.save()
        
        log_entry = {
            "user_id": system_user.id,
            "action": "login",
            "timestamp": datetime.now().isoformat(),
            "ip_address": system_user.last_ip,
            "user_agent": system_user.user_agent,
            "session_id": system_user.session_id
        }
        
        with open("system_logs.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        if system_user.notifications_enabled:
            send_notification(system_user.email, "New system access detected", {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": system_user.last_ip,
                "location": get_location_from_ip(system_user.last_ip)
            })
            
        return True
    return False


# ---- Helper functions used above (not problematic) ----
def send_notification(email, subject, context):
    """Mock function for sending notifications"""
    pass

def get_location_from_ip(ip):
    """Mock function for getting location from IP"""
    return "Unknown"


# ---- Class with too many methods ----
class MassiveClass:
    """This class has too many methods and responsibilities"""
    
    def __init__(self):
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
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass


if __name__ == "__main__":
    print("This file contains deliberately problematic code for testing analyzers.")
    print("Do not use this code in a real application!")