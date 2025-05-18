"""
User Management Script for TranspoSystem with MongoDB Atlas
This script helps with creating admin users and managing user accounts.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transporsystem.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

def create_admin():
    """Create a superuser account"""
    try:
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists.")
            return
        
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Admin user '{username}' created successfully!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

def list_users():
    """List all users in the database"""
    try:
        users = User.objects.all()
        print("\nUser List:")
        print("-" * 50)
        print(f"{'Username':<20} {'Email':<30} {'Admin':<10}")
        print("-" * 50)
        for user in users:
            print(f"{user.username:<20} {user.email:<30} {'Yes' if user.is_superuser else 'No':<10}")
    except Exception as e:
        print(f"Error listing users: {e}")

def reset_password():
    """Reset a user's password"""
    try:
        username = input("Enter username to reset password: ")
        try:
            user = User.objects.get(username=username)
            new_password = input("Enter new password: ")
            user.set_password(new_password)
            user.save()
            print(f"Password for user '{username}' has been reset.")
        except User.DoesNotExist:
            print(f"User '{username}' not found.")
    except Exception as e:
        print(f"Error resetting password: {e}")

def delete_user():
    """Delete a user"""
    try:
        username = input("Enter username to delete: ")
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"User '{username}' has been deleted.")
        except User.DoesNotExist:
            print(f"User '{username}' not found.")
    except Exception as e:
        print(f"Error deleting user: {e}")

def main():
    """Main function to run the script"""
    while True:
        print("\nTranspoSystem User Management")
        print("1. Create admin user")
        print("2. List all users")
        print("3. Reset user password")
        print("4. Delete user")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            create_admin()
        elif choice == '2':
            list_users()
        elif choice == '3':
            reset_password()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            print("Exiting user management. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()