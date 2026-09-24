# generate_full_data.py
from main import app, db
from main import User, Loan, Payment, CRBSimulation, CRBSimulationLog
from datetime import datetime, timedelta
import random

with app.app_context():
    print("=" * 60)
    print("🔄 GENERATING  DATA FOR RISK REPORTS")
    print("=" * 60)
    
   
    users_data = [
        {'username': 'oketch_j', 'email': 'james.oketch@email.com', 'full_name': 'James Oketch', 'phone_number': '0712345678', 'id_number': '12345678', 'password': 'password123'},
        {'username': 'wambui_m', 'email': 'mary.wambui@email.com', 'full_name': 'Mary Wambui', 'phone_number': '0723456789', 'id_number': '23456789', 'password': 'password123'},
        {'username': 'odhiambo_p', 'email': 'peter.odhiambo@email.com', 'full_name': 'Peter Odhiambo', 'phone_number': '0734567890', 'id_number': '34567890', 'password': 'password123'},
        {'username': 'akinyi_s', 'email': 'sarah.akinyi@email.com', 'full_name': 'Sarah Akinyi', 'phone_number': '0745678901', 'id_number': '45678901', 'password': 'password123'},
        {'username': 'kiprop_d', 'email': 'david.kiprop@email.com', 'full_name': 'David Kiprop', 'phone_number': '0756789012', 'id_number': '56789012', 'password': 'password123'},
        {'username': 'mbugua_j', 'email': 'john.mbugua@email.com', 'full_name': 'John Mbugua', 'phone_number': '0767890123', 'id_number': '67890123', 'password': 'password123'},
        {'username': 'kamau_p', 'email': 'peter.kamau@email.com', 'full_name': 'Peter Kamau', 'phone_number': '0778901234', 'id_number': '78901234', 'password': 'password123'},
        {'username': 'otieno_m', 'email': 'mary.otieno@email.com', 'full_name': 'Mary Otieno', 'phone_number': '0789012345', 'id_number': '89012345', 'password': 'password123'},
        {'username': 'nyambura_g', 'email': 'grace.nyambura@email.com', 'full_name': 'Grace Nyambura', 'phone_number': '0790123456', 'id_number': '90123456', 'password': 'password123'},
        {'username': 'kariuki_j', 'email': 'james.kariuki@email.com', 'full_name': 'James Kariuki', 'phone_number': '0701234567', 'id_number': '01234567', 'password': 'password123'},
        {'username': 'chege_m', 'email': 'martin.chege@email.com', 'full_name': 'Martin Chege', 'phone_number': '0712345670', 'id_number': '11223344', 'password': 'password123'},
        {'username': 'njeri_e', 'email': 'esther.njeri@email.com', 'full_name': 'Esther Njeri', 'phone_number': '0723456780', 'id_number': '22334455', 'password': 'password123'},
    ]
    
    created_users = 0
    for data in users_data:
        existing = User.query.filter_by(username=data['username']).first()
        if not existing:
            user = User(
                username=data['username'],
                email=data['email'],
                full_name=data['full_name'],
                phone_number=data['phone_number'],
                id_number=data['id_number']
            )
            user.set_password(data['password'])
            db.session.add(user)
            created_users += 1
    db.session.commit()
    print(f"✅ Created {created_users} users")
    

    print("\n🔄 Clearing existing loans and payments...")
    
   
    payment_count = Payment.query.count()
    Payment.query.delete()
    db.session.commit()
    print(f"   ✅ Cleared {payment_count} payments")
    
 
    loan_count = Loan.query.count()
    Loan.query.delete()
    db.session.commit()
    print(f"   ✅ Cleared {loan_count} loans")
    
    print("   ✅ Existing data cleared")
    

    print("\n🔄 Creating loans with varying risk levels...")
    
    loans_data = [
       
        {'user': 'oketch_j', 'amount': 50000, 'period': 6, 'purpose': 'Business', 'status': 'COMPLETED', 'risk': 25},
        {'user': 'kiprop_d', 'amount': 25000, 'period': 3, 'purpose': 'Personal', 'status': 'COMPLETED', 'risk': 10},
        {'user': 'nyambura_g', 'amount': 30000, 'period': 3, 'purpose': 'Education', 'status': 'ACTIVE', 'risk': 15},
        {'user': 'kariuki_j', 'amount': 40000, 'period': 6, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 20},
        {'user': 'otieno_m', 'amount': 20000, 'period': 3, 'purpose': 'Personal', 'status': 'ACTIVE', 'risk': 30},
        {'user': 'oketch_j', 'amount': 35000, 'period': 4, 'purpose': 'Medical', 'status': 'ACTIVE', 'risk': 35},
        {'user': 'chege_m', 'amount': 45000, 'period': 5, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 28},
        {'user': 'njeri_e', 'amount': 50000, 'period': 4, 'purpose': 'Education', 'status': 'ACTIVE', 'risk': 22},
        {'user': 'kariuki_j', 'amount': 30000, 'period': 3, 'purpose': 'Personal', 'status': 'ACTIVE', 'risk': 18},
        {'user': 'nyambura_g', 'amount': 40000, 'period': 5, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 32},
        {'user': 'otieno_m', 'amount': 25000, 'period': 3, 'purpose': 'Education', 'status': 'ACTIVE', 'risk': 12},
        
        
        {'user': 'wambui_m', 'amount': 60000, 'period': 8, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 45},
        {'user': 'kamau_p', 'amount': 50000, 'period': 6, 'purpose': 'Education', 'status': 'ACTIVE', 'risk': 50},
        {'user': 'akinyi_s', 'amount': 80000, 'period': 9, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 55},
        {'user': 'mbugua_j', 'amount': 100000, 'period': 12, 'purpose': 'Housing', 'status': 'ACTIVE', 'risk': 60},
        {'user': 'otieno_m', 'amount': 70000, 'period': 7, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 48},
        {'user': 'odhiambo_p', 'amount': 90000, 'period': 10, 'purpose': 'Medical', 'status': 'APPROVED', 'risk': 52},
        {'user': 'chege_m', 'amount': 75000, 'period': 9, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 58},
        {'user': 'njeri_e', 'amount': 80000, 'period': 10, 'purpose': 'Housing', 'status': 'ACTIVE', 'risk': 42},
 
        {'user': 'mbugua_j', 'amount': 150000, 'period': 18, 'purpose': 'Business', 'status': 'DEFAULTED', 'risk': 85},
        {'user': 'kamau_p', 'amount': 200000, 'period': 24, 'purpose': 'Business', 'status': 'DEFAULTED', 'risk': 90},
        {'user': 'odhiambo_p', 'amount': 120000, 'period': 15, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 75},
        {'user': 'akinyi_s', 'amount': 100000, 'period': 12, 'purpose': 'Business', 'status': 'ACTIVE', 'risk': 80},
        {'user': 'wambui_m', 'amount': 180000, 'period': 20, 'purpose': 'Housing', 'status': 'PENDING', 'risk': 70},
    ]
    
    created_loans = 0
    for data in loans_data:
        user = User.query.filter_by(username=data['user']).first()
        if user:
            interest_rate = 10.0
            total_amount = data['amount'] * (1 + (interest_rate / 100) * (data['period'] / 12))
            monthly_installment = total_amount / data['period']
            
            loan = Loan(
                user_id=user.id,
                loan_amount=data['amount'],
                interest_rate=interest_rate,
                loan_period=data['period'],
                monthly_installment=monthly_installment,
                total_amount=total_amount,
                loan_purpose=data['purpose'],
                status=data['status'],
                application_date=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                due_date=datetime.utcnow() + timedelta(days=data['period'] * 30),
                risk_score=data['risk']
            )
            db.session.add(loan)
            created_loans += 1
    
    db.session.commit()
    print(f"✅ Created {created_loans} loans with varying risk levels")
    print(f"   🟢 Low Risk (<40%):   11 loans")
    print(f"   🟡 Medium Risk (40-69%): 8 loans")
    print(f"   🔴 High Risk (≥70%):   5 loans")
    

    print("\n🔄 Creating payments...")
    
    payments_data = [
        # LOW RISK LOANS - Full payment history
        {'user': 'oketch_j', 'loan_amount': 50000, 'payments': [8750, 8750, 8750, 8750, 8750, 8750]},
        {'user': 'kiprop_d', 'loan_amount': 25000, 'payments': [9027, 9027, 9027]},
        {'user': 'nyambura_g', 'loan_amount': 30000, 'payments': [10833, 10833, 10833]},
        
        # MEDIUM RISK LOANS - Some late payments
        {'user': 'wambui_m', 'loan_amount': 60000, 'payments': [7500, 7500, 7500, 7500]},
        {'user': 'akinyi_s', 'loan_amount': 80000, 'payments': [8889, 8889, 8889]},
        {'user': 'kamau_p', 'loan_amount': 50000, 'payments': [8333, 8333, 8333]},
        
        # HIGH RISK LOANS - Few payments
        {'user': 'mbugua_j', 'loan_amount': 150000, 'payments': [8333, 8333]},
        {'user': 'kamau_p', 'loan_amount': 200000, 'payments': [8333]},
        {'user': 'odhiambo_p', 'loan_amount': 120000, 'payments': [10000, 10000]},
    ]
    
    created_payments = 0
    for data in payments_data:
        user = User.query.filter_by(username=data['user']).first()
        if user:
            loan = Loan.query.filter_by(user_id=user.id, loan_amount=data['loan_amount']).first()
            if loan:
                for idx, amount in enumerate(data['payments']):
                    is_late = random.random() > 0.7
                    payment = Payment(
                        loan_id=loan.id,
                        amount=amount,
                        payment_date=datetime.utcnow() - timedelta(days=idx * 30 + random.randint(1, 10)),
                        due_date=datetime.utcnow() + timedelta(days=30),
                        status='LATE' if is_late and idx > 0 else 'COMPLETED'
                    )
                    db.session.add(payment)
                    created_payments += 1
    
    db.session.commit()
    print(f"✅ Created {created_payments} payment records")
    

    print("\n🔄 Updating CRB data...")
    
    for user in User.query.all():
        crb = CRBSimulation.query.filter_by(user_id=user.id).first()
        loans = Loan.query.filter_by(user_id=user.id).all()
        
        if loans:
            avg_risk = sum(l.risk_score for l in loans) / len(loans)
            
            if avg_risk < 40:
                score = random.randint(650, 750)
                rating = 'GOOD'
            elif avg_risk < 70:
                score = random.randint(500, 649)
                rating = 'FAIR'
            else:
                score = random.randint(300, 499)
                rating = 'POOR'
            
            if crb:
                crb.credit_score = score
                crb.credit_rating = rating
                crb.default_history = any(l.status == 'DEFAULTED' for l in loans)
                crb.npa_count = sum(1 for l in loans if l.status == 'DEFAULTED')
            else:
                crb = CRBSimulation(
                    user_id=user.id,
                    national_id=user.id_number,
                    full_name=user.full_name,
                    phone_number=user.phone_number,
                    credit_score=score,
                    credit_rating=rating,
                    default_history=any(l.status == 'DEFAULTED' for l in loans),
                    npa_count=sum(1 for l in loans if l.status == 'DEFAULTED')
                )
                db.session.add(crb)
            
            db.session.add(crb)
    
    db.session.commit()
    print("✅ CRB data updated")
    
 
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    
    total_users = User.query.count()
    total_loans = Loan.query.count()
    total_payments = Payment.query.count()
    
    low_risk = Loan.query.filter(Loan.risk_score < 40).count()
    medium_risk = Loan.query.filter(Loan.risk_score >= 40, Loan.risk_score < 70).count()
    high_risk = Loan.query.filter(Loan.risk_score >= 70).count()
    
    active = Loan.query.filter_by(status='ACTIVE').count()
    pending = Loan.query.filter_by(status='PENDING').count()
    approved = Loan.query.filter_by(status='APPROVED').count()
    completed = Loan.query.filter_by(status='COMPLETED').count()
    defaulted = Loan.query.filter_by(status='DEFAULTED').count()
    
    print(f"\n👤 Users: {total_users}")
    print(f"📊 Total Loans: {total_loans}")
    print(f"💳 Total Payments: {total_payments}")
    
    print("\n📊 Risk Distribution:")
    print(f"  🟢 Low Risk (<40%):   {low_risk}  ({(low_risk/total_loans*100):.1f}%)")
    print(f"  🟡 Medium Risk (40-69%): {medium_risk}  ({(medium_risk/total_loans*100):.1f}%)")
    print(f"  🔴 High Risk (≥70%):   {high_risk}  ({(high_risk/total_loans*100):.1f}%)")
    
    print("\n📊 Status Distribution:")
    print(f"  ✅ Active:    {active}  ({(active/total_loans*100):.1f}%)")
    print(f"  ⏳ Pending:   {pending}  ({(pending/total_loans*100):.1f}%)")
    print(f"  📋 Approved:  {approved}  ({(approved/total_loans*100):.1f}%)")
    print(f"  ✔️ Completed: {completed}  ({(completed/total_loans*100):.1f}%)")
    print(f"  ❌ Defaulted: {defaulted}  ({(defaulted/total_loans*100):.1f}%)")
    
    print("\n" + "=" * 60)
    print("🎉 Adequate data generation complete!")
    print("=" * 60)