# app/utils/crb_simulator.py
import random
from datetime import datetime


class CRBSimulator:
    """
    Simulates CRB credit reports for users with and without payment history
    """
    
    @staticmethod
    def generate_score_for_user(user):
        """
        Generate a realistic CRB score and report based on user data
        """
        base_score = 500
        
        # 1. Factor: User age
        if user.date_registered:
            days_since_reg = (datetime.utcnow() - user.date_registered).days
            if days_since_reg > 730:
                base_score += 50
            elif days_since_reg > 365:
                base_score += 25
            elif days_since_reg > 180:
                base_score += 10
        
        # 2. Factor: Payment history
        past_loans = user.loans
        if past_loans:
            completed = sum(1 for l in past_loans if l.status == 'COMPLETED')
            if completed > 0:
                base_score += 30 * min(completed, 3)
            
            defaulted = any(l.status == 'DEFAULTED' for l in past_loans)
            if defaulted:
                base_score -= 80
            
            active = sum(1 for l in past_loans if l.status == 'ACTIVE')
            if active > 0:
                base_score += 10 * min(active, 2)
            
            # Check for late payments
            late_count = 0
            for loan in past_loans:
                from main import Payment
                late_payments = Payment.query.filter_by(loan_id=loan.id, status='LATE').count()
                late_count += late_payments
            
            if late_count > 0:
                base_score -= min(late_count * 5, 30)
        
        # 3. Factor: New users
        if not past_loans:
            base_score = random.randint(450, 650)
            base_score += random.randint(-20, 20)
        
        # 4. Random variation
        base_score += random.randint(-20, 20)
        
        # 5. Ensure score is within range
        final_score = max(300, min(850, base_score))
        
        # Determine rating
        if final_score >= 700:
            rating = 'EXCELLENT'
        elif final_score >= 600:
            rating = 'GOOD'
        elif final_score >= 500:
            rating = 'FAIR'
        elif final_score >= 400:
            rating = 'POOR'
        else:
            rating = 'VERY POOR'
        
        return {
            'credit_score': final_score,
            'credit_rating': rating,
            'total_loan_accounts': len(past_loans) if past_loans else random.randint(0, 3),
            'active_loan_accounts': sum(1 for l in past_loans if l.status == 'ACTIVE') if past_loans else 0,
            'settled_loan_accounts': sum(1 for l in past_loans if l.status == 'COMPLETED') if past_loans else 0,
            'npa_count': sum(1 for l in past_loans if l.status == 'DEFAULTED') if past_loans else 0,
            'payment_history': 'GOOD' if final_score >= 550 else 'POOR',
            'months_positive': random.randint(6, 60) if past_loans else random.randint(1, 12),
            'months_negative': random.randint(0, 3) if past_loans else 0,
            'default_history': any(l.status == 'DEFAULTED' for l in past_loans) if past_loans else False,
            'legal_suits': random.randint(0, 1) if final_score < 400 else 0,
            'bounced_cheques': random.randint(0, 1) if final_score < 450 else 0,
            'is_new_user': not past_loans
        }
    
    @staticmethod
    def get_risk_level(score):
        """Get risk level from credit score"""
        if score >= 700:
            return 'LOW'
        elif score >= 600:
            return 'LOW-MEDIUM'
        elif score >= 500:
            return 'MEDIUM'
        elif score >= 400:
            return 'HIGH'
        else:
            return 'VERY HIGH'
    
    @staticmethod
    def get_recommendation(score, npa_count=0, default_history=False, is_new_user=False):
        """Get loan recommendation based on CRB data"""
        if default_history:
            return '❌ REJECTED: History of default'
        elif npa_count > 2:
            return '❌ REJECTED: Multiple NPA accounts'
        elif is_new_user and score >= 550:
            return '✅ APPROVED: Good profile for new user'
        elif is_new_user and score >= 450:
            return '⚠️ APPROVED WITH CONDITIONS: New user, higher interest may apply'
        elif score >= 700:
            return '✅ APPROVED: Excellent credit history'
        elif score >= 600:
            return '✅ APPROVED: Good credit history'
        elif score >= 500:
            return '⚠️ APPROVED WITH CONDITIONS: Fair credit history'
        elif score >= 400:
            return '⚠️ REVIEW REQUIRED: Poor credit history'
        else:
            return '❌ REJECTED: Very poor credit history'