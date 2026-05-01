import tasks.create_login_table as create_login_table
import tasks.load_users as load_users

if __name__ == "__main__":
    print("Running Task 1...")
    create_login_table.create_login_table()
    load_users.load_users()