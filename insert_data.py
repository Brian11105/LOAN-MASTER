from app import app, db, User, Loan
from datetime import datetime, timedelta

with app.app_context():
    print("📝 Inserting sample data...")
    
    # Create users with Kenyan names
    users_data = [
        {'username': 'oketch_j', 'email': 'james.oketch@email.com', 'full_name': 'James Oketch', 'phone_number': '0712345678', 'id_number': '12345678', 'password': 'password123'},
        {'username': 'wambui_m', 'email': 'mary.wambui@email.com', 'full_name': 'Mary Wambui', 'phone_number': '0723456789', 'id_number': '23456789', 'password': 'password123'},
        {'username': 'odhiambo_p', 'email': 'peter.odhiambo@email.com', 'full_name': 'Peter Odhiambo', 'phone_number': '0734567890', 'id_number': '34567890', 'password': 'password123'},
        {'username': 'akinyi_s', 'email': 'sarah.akinyi@email.com', 'full_name': 'Sarah Akinyi', 'phone_number': '0745678901', 'id_number': '45678901', 'password': 'password123'},
        {'username': 'kiprop_d', 'email': 'david.kiprop@email.com', 'full_name': 'David Kiprop', 'phone_number': '0756789012', 'id_number': '56789012', 'password': 'password123'}
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
            print(f"  ✅ Created user: {data['username']}")
    
    db.session.commit()
    print(f"✅ Total users created: {created_users}")

    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@loanmaster.co.ke',
            full_name='System Administrator',
            phone_number='0712345678',
            id_number='00000000',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")

    # Create loans
    loans_data = [
        {'user': 'oketch_j', 'amount': 50000, 'period': 6, 'purpose': 'Business', 'status': 'ACTIVE'},
        {'user': 'wambui_m', 'amount': 30000, 'period': 3, 'purpose': 'Education', 'status': 'APPROVED'},
        {'user': 'odhiambo_p', 'amount': 100000, 'period': 12, 'purpose': 'Medical', 'status': 'PENDING'},
        {'user': 'akinyi_s', 'amount': 75000, 'period': 6, 'purpose': 'Housing', 'status': 'ACTIVE'},
        {'user': 'kiprop_d', 'amount': 25000, 'period': 3, 'purpose': 'Personal', 'status': 'COMPLETED'}
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
                application_date=datetime.utcnow() - timedelta(days=30),
                due_date=datetime.utcnow() + timedelta(days=data['period'] * 30)
            )
            loan.risk_score = loan.calculate_risk_score()
            db.session.add(loan)
            created_loans += 1
            print(f"  ✅ Created loan for: {data['user']}")
    
    db.session.commit()
    print(f"✅ Total loans created: {created_loans}")
    
    # Verify data
    user_count = User.query.count()
    loan_count = Loan.query.count()
    
    print("\n" + "="*50)
    print("🎉 SUCCESS! All data inserted!")
    print("="*50)
    print(f"📊 Users in database: {user_count}")
    print(f"📊 Loans in database: {loan_count}")
    print("\n🔑 LOGIN CREDENTIALS:")
    print("  👤 Regular User: oketch_j / password123")
    print("  👤 Admin User: admin / admin123")
    print("\n🌐 Open browser: http://localhost:5000")
    print("="*50)