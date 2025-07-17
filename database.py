import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_file="fitgym.db"):
        """Initialize database connection"""
        self.db_file = db_file
        self.conn = None
        self.create_connection()
        self.create_tables()
    
    def create_connection(self):
        """Create a database connection to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Create members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    membership_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create membership_types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS membership_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    price REAL NOT NULL,
                    description TEXT
                )
            ''')
            
            # Insert default membership types if table is empty
            cursor.execute("SELECT COUNT(*) FROM membership_types")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO membership_types (name, duration, price, description)
                    VALUES 
                    ('Monthly', 30, 50.00, 'Standard monthly membership'),
                    ('Quarterly', 90, 130.00, 'Three month membership'),
                    ('Annual', 365, 450.00, 'Full year membership')
                ''')
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
            return False
    
    def add_member(self, name, phone, email, membership_type):
        """Add a new member to the database"""
        try:
            cursor = self.conn.cursor()
            
            # Get membership duration
            cursor.execute("SELECT duration FROM membership_types WHERE name = ?", (membership_type,))
            result = cursor.fetchone()
            if not result:
                return False, "Invalid membership type"
            
            duration = result[0]
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=duration)).strftime("%Y-%m-%d")
            
            cursor.execute('''
                INSERT INTO members (name, phone, email, start_date, end_date, membership_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, start_date, end_date, membership_type))
            
            self.conn.commit()
            return True, cursor.lastrowid
        except sqlite3.Error as e:
            return False, str(e)
    
    def update_member(self, member_id, name, phone, email, membership_type=None, extend_days=0):
        """Update member information and optionally extend membership"""
        try:
            cursor = self.conn.cursor()
            
            # Get current member data
            cursor.execute("SELECT end_date, membership_type FROM members WHERE id = ?", (member_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Member not found"
            
            current_end_date = datetime.strptime(result[0], "%Y-%m-%d")
            current_membership_type = result[1]
            
            # Update membership type and end date if specified
            if membership_type and membership_type != current_membership_type:
                cursor.execute("SELECT duration FROM membership_types WHERE name = ?", (membership_type,))
                duration_result = cursor.fetchone()
                if not duration_result:
                    return False, "Invalid membership type"
                
                # Reset end date based on new membership type
                duration = duration_result[0]
                new_end_date = (datetime.now() + timedelta(days=duration)).strftime("%Y-%m-%d")
            else:
                # Extend current end date if requested
                new_end_date = (current_end_date + timedelta(days=extend_days)).strftime("%Y-%m-%d") if extend_days > 0 else result[0]
                membership_type = current_membership_type
            
            cursor.execute('''
                UPDATE members 
                SET name = ?, phone = ?, email = ?, end_date = ?, membership_type = ?
                WHERE id = ?
            ''', (name, phone, email, new_end_date, membership_type, member_id))
            
            self.conn.commit()
            return True, "Member updated successfully"
        except sqlite3.Error as e:
            return False, str(e)
    
    def update_member_dates(self, member_id, name, phone, email, membership_type, start_date, end_date, extend_days=0):
        """Update member information including start and end dates"""
        try:
            cursor = self.conn.cursor()
            
            # Get current member data
            cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Member not found"
            
            # Update end date if extension is requested
            if extend_days > 0:
                # Parse the end date
                current_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Add extension days
                new_end_date = (current_end_date + timedelta(days=extend_days)).strftime("%Y-%m-%d")
            else:
                new_end_date = end_date
            
            cursor.execute('''
                UPDATE members 
                SET name = ?, phone = ?, email = ?, start_date = ?, end_date = ?, membership_type = ?
                WHERE id = ?
            ''', (name, phone, email, start_date, new_end_date, membership_type, member_id))
            
            self.conn.commit()
            return True, "Member updated successfully"
        except sqlite3.Error as e:
            return False, str(e)
    
    def delete_member(self, member_id):
        """Delete a member from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            self.conn.commit()
            
            if cursor.rowcount == 0:
                return False, "Member not found"
            return True, "Member deleted successfully"
        except sqlite3.Error as e:
            return False, str(e)
    
    def get_all_members(self):
        """Get all members from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, phone, email, start_date, end_date, membership_type, status
                FROM members
                ORDER BY name
            ''')
            
            columns = [col[0] for col in cursor.description]
            members = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Calculate days remaining for each member
            for member in members:
                end_date = datetime.strptime(member['end_date'], "%Y-%m-%d")
                days_remaining = (end_date - datetime.now()).days
                member['days_remaining'] = max(0, days_remaining)
                
                # Update status if membership has expired
                if days_remaining <= 0 and member['status'] == 'active':
                    cursor.execute("UPDATE members SET status = 'expired' WHERE id = ?", (member['id'],))
                    member['status'] = 'expired'
            
            self.conn.commit()
            return members
        except sqlite3.Error as e:
            print(f"Error getting members: {e}")
            return []
    
    def get_member(self, member_id):
        """Get a specific member by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, phone, email, start_date, end_date, membership_type, status
                FROM members
                WHERE id = ?
            ''', (member_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            columns = [col[0] for col in cursor.description]
            member = dict(zip(columns, result))
            
            # Calculate days remaining
            end_date = datetime.strptime(member['end_date'], "%Y-%m-%d")
            days_remaining = (end_date - datetime.now()).days
            member['days_remaining'] = max(0, days_remaining)
            
            return member
        except sqlite3.Error as e:
            print(f"Error getting member: {e}")
            return None
    
    def search_members(self, search_term):
        """Search members by name, phone, or email"""
        try:
            cursor = self.conn.cursor()
            search_pattern = f"%{search_term}%"
            
            cursor.execute('''
                SELECT id, name, phone, email, start_date, end_date, membership_type, status
                FROM members
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY name
            ''', (search_pattern, search_pattern, search_pattern))
            
            columns = [col[0] for col in cursor.description]
            members = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Calculate days remaining for each member
            for member in members:
                end_date = datetime.strptime(member['end_date'], "%Y-%m-%d")
                days_remaining = (end_date - datetime.now()).days
                member['days_remaining'] = max(0, days_remaining)
            
            return members
        except sqlite3.Error as e:
            print(f"Error searching members: {e}")
            return []
    
    def get_membership_types(self):
        """Get all membership types"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, duration, price, description FROM membership_types")
            
            columns = [col[0] for col in cursor.description]
            types = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return types
        except sqlite3.Error as e:
            print(f"Error getting membership types: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()