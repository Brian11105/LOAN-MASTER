# generate_crb_data.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
import main
from main import db, User, Loan, Payment

try:
    from main import CRBSimulation, CRBSimulationLog
    print("✅ CRB models imported from main.py")
except ImportError:
    print("❌ CRB models not found in main.py")
    print("   Please ensure CRBSimulation and CRBSimulationLog are defined in main.py")
    sys.exit(1)


try:
    from app.utils.crb_simulator import CRBSimulator
    print("✅ CRBSimulator imported from app.utils")
except ImportError:
   
    import random
    from datetime import datetime
    
    class CRBSimulator:
        @staticmethod
        def generate_score_for_user(user):
            base_score = 500
            
            if user.date_registered:
                days = (datetime.utcnow() - user.date_registered).days
                if days > 730:
                    base_score += 50
                elif days > 365:
                    base_score += 25
            
            past_loans = user.loans
            if past_loans:
                completed = sum(1 for l in past_loans if l.status == 'COMPLETED')
                if completed > 0:
                    base_score += 30 * min(completed, 3)
                defaulted = any(l.status == 'DEFAULTED' for l in past_loans)
                if defaulted:
                    base_score -= 80
            else:
                base_score = random.randint(450, 650)
            
            base_score += random.randint(-20, 20)
            final_score = max(300, min(850, base_score))
            
            rating = 'EXCELLENT' if final_score >= 700 else 'GOOD' if final_score >= 600 else 'FAIR' if final_score >= 500 else 'POOR'
            
            return {
                'credit_score': final_score,
                'credit_rating': rating,
                'npa_count': sum(1 for l in past_loans if l.status == 'DEFAULTED') if past_loans else 0,
                'payment_history': 'GOOD' if final_score >= 550 else 'POOR',
                'default_history': any(l.status == 'DEFAULTED' for l in past_loans) if past_loans else False
            }
        
        @staticmethod
        def get_risk_level(score):
            if score >= 700: return 'LOW'
            if score >= 600: return 'LOW-MEDIUM'
            if score >= 500: return 'MEDIUM'
            if score >= 400: return 'HIGH'
            return 'VERY HIGH'
    
    print("✅ CRBSimulator defined inline")


with main.app.app_context():
    print("=" * 50)
    print("🔄 Generating CRB Reports for All Users")
    print("=" * 50)
    
    users = User.query.all()
    print(f"\n📊 Found {len(users)} users in database\n")
    
    generated = 0
    updated = 0
    
    for user in users:
        print(f"  Processing: {user.username} - {user.full_name}")
        
        report_data = CRBSimulator.generate_score_for_user(user)
        existing = CRBSimulation.query.filter_by(user_id=user.id).first()
        
        if existing:
            existing.credit_score = report_data['credit_score']
            existing.credit_rating = report_data['credit_rating']
            existing.npa_count = report_data['npa_count']
            existing.payment_history = report_data['payment_history']
            existing.default_history = report_data['default_history']
            updated += 1
            print(f"    ✅ Updated: Score {report_data['credit_score']} - {report_data['credit_rating']}")
        else:
            crb = CRBSimulation(
                user_id=user.id,
                national_id=user.id_number,
                full_name=user.full_name,
                phone_number=user.phone_number,
                credit_score=report_data['credit_score'],
                credit_rating=report_data['credit_rating'],
                npa_count=report_data['npa_count'],
                payment_history=report_data['payment_history'],
                default_history=report_data['default_history'],
                simulated_at=datetime.utcnow()
            )
            db.session.add(crb)
            generated += 1
            print(f"    ✅ Generated: Score {report_data['credit_score']} - {report_data['credit_rating']}")
        
        # Create log
        log = CRBSimulationLog(
            user_id=user.id,
            credit_score=report_data['credit_score'],
            risk_level=CRBSimulator.get_risk_level(report_data['credit_score']),
            is_simulated=True
        )
        db.session.add(log)
    
    db.session.commit()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"  ✅ New CRB Reports Created: {generated}")
    print(f"  ✅ Existing Reports Updated: {updated}")
    print(f"  📊 CRB Reports in Database: {CRBSimulation.query.count()}")
    print(f"  📊 CRB Logs in Database: {CRBSimulationLog.query.count()}")
    print("\n🎉 CRB data generation complete!")