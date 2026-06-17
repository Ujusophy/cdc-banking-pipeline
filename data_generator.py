import psycopg2
import random
import time
from faker import Faker
from datetime import datetime
import uuid

fake = Faker()

conn = psycopg2.connect(
    host="localhost",
    database="banking",
    user="admin",
    password="****",
    port=5432
)
cursor = conn.cursor()

def create_user():
    cursor.execute("""
        INSERT INTO users (first_name, last_name, email, phone_number, date_of_birth)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id
    """, (
        fake.first_name(),
        fake.last_name(),
        fake.unique.email(),
        fake.phone_number()[:20],
        fake.date_of_birth(minimum_age=18, maximum_age=70)
    ))
    conn.commit()
    return cursor.fetchone()[0]

def create_account(user_id):
    cursor.execute("""
        INSERT INTO accounts (user_id, account_type, balance, status)
        VALUES (%s, %s, %s, %s)
        RETURNING account_id
    """, (
        user_id,
        random.choice(['savings', 'current']),
        round(random.uniform(1000, 100000), 2),
        'active'
    ))
    conn.commit()
    return cursor.fetchone()[0]

def create_transaction(sender_id, receiver_id):
    amount = round(random.uniform(100, 10000), 2)
    cursor.execute("""
        INSERT INTO transactions (sender_account_id, receiver_account_id, amount, transaction_type, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        sender_id,
        receiver_id,
        amount,
        random.choice(['transfer', 'deposit', 'withdrawal']),
        random.choice(['completed', 'pending', 'failed'])
    ))
    # Update sender balance
    cursor.execute("""
        UPDATE accounts SET balance = balance - %s, updated_at = NOW()
        WHERE account_id = %s
    """, (amount, sender_id))
    # Update receiver balance
    cursor.execute("""
        UPDATE accounts SET balance = balance + %s, updated_at = NOW()
        WHERE account_id = %s
    """, (amount, receiver_id))
    conn.commit()

def main():
    print("Starting data generator...")
    account_ids = []

    # Seed initial data
    print("Seeding initial users and accounts...")
    for _ in range(10):
        user_id = create_user()
        account_id = create_account(user_id)
        account_ids.append(account_id)
        print(f"Created user {user_id} with account {account_id}")

    # Continuously generate transactions
    print("Generating continuous transactions...")
    while True:
        sender = random.choice(account_ids)
        receiver = random.choice([a for a in account_ids if a != sender])
        create_transaction(sender, receiver)
        print(f"Transaction: {sender} → {receiver}")
        time.sleep(2)

if __name__ == "__main__":
    main()