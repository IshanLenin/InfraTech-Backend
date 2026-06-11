import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_date_past_90_days():
    return datetime.now() - timedelta(days=random.randint(0, 90))

def seed_database():
    db: Session = SessionLocal()
    
    print("Starting database seeding process...")

    try:
        print("Clearing old data from the database...")
        db.query(models.Notification).delete()
        db.query(models.Ticket).delete()
        db.query(models.Reward).delete()
        db.query(models.Deal).delete()
        db.query(models.Brand).delete()
        db.query(models.User).delete()
        db.commit()
        print("Old data cleared.")

        # 1. Create Brands and Deals
        brands_data = [("Amazon", "E-commerce"), ("Myntra", "Fashion"), ("HDFC", "Finance")]
        brands = []
        for name, category in brands_data:
            b = models.Brand(name=name, category=category)
            db.add(b)
            brands.append(b)
        db.commit()

        deals = []
        for i in range(15):
            d = models.Deal(
                brand_id=random.choice(brands).id,
                title=f"Mega Sale {i+1}",
                status=random.choices(['active', 'inactive'], weights=[0.7, 0.3])[0],
                payout_percentage=random.choice([70.00, 75.00, 80.00]),
                has_seo_metadata=random.choice([True, False])
            )
            db.add(d)
            deals.append(d)
        db.commit()
        print("Brands and Deals created.")

        # 2. Create Users (spanning 3 months for MoM growth)
        users = []
        for i in range(500):
            created = random_date_past_90_days()
            u = models.User(
                name=f"Test User {i}",
                email=f"user{i}@example.com",
                status=random.choices(['active', 'inactive'], weights=[0.9, 0.1])[0],
                is_verified=random.choice([True, False]),
                refer_code=generate_random_string(),
                pp_points=random.randint(0, 5000),
                created_at=created
            )
            db.add(u)
            users.append(u)
        db.commit()
        
        # Link some referrers
        for u in users:
            if random.random() > 0.8: # 20% of users were referred
                u.referrer_id = random.choice(users).refer_code
        db.commit()
        print(f"500 Users created.")

        # 3. Create the Unified Ledger (Rewards Funnel)
        reward_types = ['redirect_reward', 'pending_reward', 'final_reward', 'redeem_cash_back', 'rejected_reward']
        # Weights simulate a funnel drop-off
        weights = [0.4, 0.3, 0.2, 0.05, 0.05] 
        
        for i in range(2000):
            r_type = random.choices(reward_types, weights=weights)[0]
            r = models.Reward(
                user_id=random.choice(users).id,
                deal_id=random.choice(deals).id,
                type=r_type,
                amount=random.randint(10, 500),
                receipt_uploaded=True if r_type in ['final_reward', 'redeem_cash_back'] else False,
                created_at=random_date_past_90_days()
            )
            db.add(r)
        db.commit()
        print("2000 Reward Ledger entries created.")

        # 4. Create Operations Data (Tickets & Notifications)
        for i in range(150):
            t = models.Ticket(
                user_id=random.choice(users).id,
                status=random.choices(['unresolved_backlog', 'resolved_cleanly'], weights=[0.8, 0.2])[0],
                created_at=random_date_past_90_days()
            )
            db.add(t)

        for i in range(1000):
            n = models.Notification(
                user_id=random.choice(users).id,
                is_read=random.choices([True, False], weights=[0.1, 0.9])[0],
                created_at=random_date_past_90_days()
            )
            db.add(n)
        db.commit()
        print("Support Tickets and Notifications created.")

        print("Database successfully seeded! Your dashboard is now alive.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()