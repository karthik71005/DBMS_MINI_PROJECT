import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

# Initialize Faker
fake = Faker()

# Create Tables (Reset DB)
print("Resetting database...")
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

def create_users(db: Session):
    print("--- Seeding Users ---")
    # 1. Fixed Users for Login
    fixed_users = [
        {"username": "admin", "role": models.RoleEnum.admin},
        {"username": "officer", "role": models.RoleEnum.loan_officer},
        {"username": "accountant", "role": models.RoleEnum.accountant},
    ]

    for u in fixed_users:
        if not db.query(models.User).filter_by(username=u["username"]).first():
            user = models.User(
                username=u["username"],
                password_hash="fake_hashed_password_123", # In real app, hash this!
                role=u["role"]
            )
            db.add(user)
    
    # 2. Random Users
    for _ in range(5):
        profile = fake.simple_profile()
        if not db.query(models.User).filter_by(username=profile["username"]).first():
            user = models.User(
                username=profile["username"],
                password_hash=fake.sha256(),
                role=random.choice(list(models.RoleEnum))
            )
            db.add(user)
    
    db.commit()

def create_loan_types(db: Session):
    print("--- Seeding Loan Types ---")
    types = [
        {"name": "Personal Loan", "max_amount": 50000, "max_tenure": 36, "base_interest_rate": 12.5},
        {"name": "Gold Loan", "max_amount": 100000, "max_tenure": 24, "base_interest_rate": 10.0},
        {"name": "Vehicle Loan", "max_amount": 500000, "max_tenure": 60, "base_interest_rate": 9.5},
        {"name": "Home Loan", "max_amount": 2000000, "max_tenure": 240, "base_interest_rate": 8.0},
    ]
    for t in types:
        if not db.query(models.LoanType).filter_by(name=t["name"]).first():
            lt = models.LoanType(**t)
            db.add(lt)
    db.commit()

def create_audit_logs(db: Session):
    print("--- Seeding Audit Logs ---")
    users = db.query(models.User).all()
    actions = ["LOGIN", "CREATE_LOAN", "APPROVE_LOAN", "VIEW_REPORT", "UPDATE_BORROWER"]
    
    if not users:
        return

    for _ in range(30): # Create 30 random logs
        user = random.choice(users)
        log = models.AuditLog(
            user_id=user.id,
            action=random.choice(actions),
            details=f"Action performed on {fake.date()}",
            timestamp=fake.date_time_between(start_date='-1y', end_date='now')
        )
        db.add(log)
    db.commit()

def create_borrowers_and_loans(db: Session):
    print("--- Seeding Borrowers, Loans, Repayments, Collateral & Ledger ---")
    
    loan_types = db.query(models.LoanType).all()

    for _ in range(20): # Create 20 Borrowers
        income = random.uniform(3000, 15000)
        borrower = models.Borrower(
            name=fake.name(),
            address=fake.address().replace('\n', ', '),
            income=income,
            monthly_income=income,
            credit_score=random.randint(300, 850)
        )
        db.add(borrower)
        db.flush() # Flush to get borrower ID

        # Create 1-3 loans per borrower
        if random.random() < 0.8: # 80% chance to have loans
            num_loans = random.randint(1, 3)
            for _ in range(num_loans):
                process_loan_logic(db, borrower.id, loan_types)
    
    db.commit()

def process_loan_logic(db: Session, borrower_id: int, loan_types):
    # 1. Random Loan Type
    loan_type = random.choice(loan_types)
    
    # 2. Random Loan Parameters
    principal = round(random.uniform(5000, float(loan_type.max_amount)), 2)
    rate = loan_type.base_interest_rate
    
    # 3. Determine Term (Clamp to max tenure)
    term_options = [12, 24, 36, 48, 60, 120, 180, 240]
    term = random.choice(term_options)
    if term > loan_type.max_tenure:
        term = loan_type.max_tenure

    # 4. Determine Dates and Status (FIXED SECTION)
    created_at = fake.date_time_between(start_date='-2y', end_date='-1M')
    
    # Random status
    status_options = [models.LoanStatus.active, models.LoanStatus.closed, models.LoanStatus.pending, models.LoanStatus.rejected]
    status = random.choice(status_options)

    disbursed_on = None
    
    # Only Active or Closed loans have a disbursement date
    if status in [models.LoanStatus.active, models.LoanStatus.closed]:
        # Disbursed 1-10 days after creation
        disbursed_on = created_at + timedelta(days=random.randint(1, 10))
    
    # Create Loan Object
    loan = models.Loan(
        borrower_id=borrower_id,
        loan_type_id=loan_type.id,
        principal=principal,
        interest_rate=rate,
        term_months=term,
        disbursed_on=disbursed_on,
        status=status,
        outstanding=principal, # Default, will update below
        created_at=created_at
    )
    db.add(loan)
    db.flush()

    # Add Collateral (Randomly)
    if random.random() < 0.5:
        collateral = models.Collateral(
            loan_id=loan.id,
            type=random.choice(["Property", "Vehicle", "Gold", "Deposits"]),
            value=principal * 1.5, # Collateral usually > loan
            description=fake.sentence(),
            submitted_on=created_at
        )
        db.add(collateral)

    # Generate Repayments and Ledger ONLY if the loan was disbursed
    if disbursed_on:
        # Ledger: Disbursement
        ledger_disb = models.Ledger(
            loan_id=loan.id,
            type="disbursement",
            amount=principal,
            date=disbursed_on,
            balance_after=principal
        )
        db.add(ledger_disb)
        
        generate_repayments(db, loan)

def generate_repayments(db: Session, loan: models.Loan):
    # Simple Interest Calculation for installment
    total_interest = float(loan.principal) * (loan.interest_rate / 100) * (loan.term_months / 12)
    total_payable = float(loan.principal) + total_interest
    monthly_installment = round(total_payable / loan.term_months, 2)
    
    # Track how much is paid to update 'outstanding'
    total_paid = 0
    current_balance = float(loan.principal) # For ledger tracking

    for i in range(1, loan.term_months + 1):
        due_date = loan.disbursed_on + timedelta(days=30 * i)
        now = datetime.now()
        
        repayment_status = "due"
        paid_amount = 0
        paid_on = None

        # LOGIC:
        # 1. If Loan is CLOSED, everything is paid.
        # 2. If Loan is ACTIVE, check if due_date is in the past.
        
        is_past_due = due_date < now
        
        should_pay = False

        if loan.status == models.LoanStatus.closed:
            should_pay = True
        elif loan.status == models.LoanStatus.active and is_past_due:
            # Random chance to be paid vs overdue
            if random.random() < 0.9: # 90% chance paid
                should_pay = True
            else:
                repayment_status = "overdue"
        
        if should_pay:
            repayment_status = "paid"
            paid_amount = monthly_installment
            # Paid randomly around due date
            paid_on = due_date + timedelta(days=random.randint(-2, 5))
            
            # Ensure paid_on is not in the future
            if paid_on > now:
                paid_on = now

        # Create Repayment
        repayment = models.Repayment(
            loan_id=loan.id,
            due_date=due_date,
            amount=monthly_installment,
            paid_amount=paid_amount,
            paid_on=paid_on,
            status=repayment_status
        )
        db.add(repayment)
        db.flush()

        # If Paid, Create Receipt and update tracking
        if repayment_status == "paid":
            total_paid += paid_amount
            receipt = models.Receipt(
                repayment_id=repayment.id,
                receipt_number=fake.unique.bothify(text='REC-#####-????')
            )
            db.add(receipt)
            
            # Ledger: Repayment
            current_balance -= float(paid_amount)
            ledger_rep = models.Ledger(
                loan_id=loan.id,
                type="repayment",
                amount=paid_amount,
                date=paid_on,
                balance_after=current_balance
            )
            db.add(ledger_rep)

    # Update Loan Outstanding
    current_outstanding = total_payable - total_paid
    loan.outstanding = max(0, current_outstanding)

def populate():
    db = SessionLocal()
    try:
        create_users(db)
        create_loan_types(db)
        create_audit_logs(db)
        create_borrowers_and_loans(db)
        print("Database population completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        # Optional: Print traceback for debugging
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate()