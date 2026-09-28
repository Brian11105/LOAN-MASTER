from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from functools import wraps
import json
import random
import os


app = Flask(__name__, template_folder='templates', static_folder='static')


app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/loan_management_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    loans = db.relationship('Loan', backref='borrower', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=10.0)
    loan_period = db.Column(db.Integer, nullable=False)
    monthly_installment = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    loan_purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='PENDING')
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    approval_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    risk_score = db.Column(db.Integer, default=0)
    payments = db.relationship('Payment', backref='loan', lazy=True)

 
    crb_score = db.Column(db.Integer, default=500)
    crb_npa = db.Column(db.Integer, default=0)
    crb_history = db.Column(db.String(20), default='GOOD')
    crb_recommendation = db.Column(db.String(200))
    risk_with_crb = db.Column(db.Integer, default=0)

    def calculate_risk_score(self):
        score = 0
        past_loans = Loan.query.filter_by(user_id=self.user_id).all()
        if past_loans:
            defaulted = any(loan.status == 'DEFAULTED' for loan in past_loans)
            if defaulted:
                score += 30
            late_payments = Payment.query.filter_by(loan_id=self.id, status='LATE').count()
            if late_payments > 0:
                score += min(late_payments * 10, 50)
        if self.loan_amount > 100000:
            score += 20
        return min(score, 100)

    def calculate_risk_with_crb(self, crb_report):
        """Calculate combined risk score using internal + CRB data"""
        internal_score = self.calculate_risk_score()
        crb_score_value = crb_report.get('credit_score', 500)
        crb_percentage = ((crb_score_value - 300) / 550) * 100
        npa_count = crb_report.get('npa_count', 0)
        npa_penalty = min(npa_count * 10, 30)
        default_penalty = 20 if crb_report.get('default_history', False) else 0
        external_score = crb_percentage + npa_penalty + default_penalty
        final_score = (internal_score * 0.6) + (external_score * 0.4)
        
        self.crb_score = crb_score_value
        self.crb_npa = npa_count
        self.crb_history = crb_report.get('payment_history', 'GOOD')
        self.crb_recommendation = crb_report.get('recommendation', 'Review required')
        self.risk_with_crb = min(int(final_score), 100)
        
        return self.risk_with_crb
    
    def get_risk_level(self):
        if self.risk_score >= 70:
            return 'HIGH'
        elif self.risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_risk_color(self):
        if self.risk_score >= 70:
            return 'danger'
        elif self.risk_score >= 40:
            return 'warning'
        else:
            return 'success'


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    payment_method = db.Column(db.String(20), default='MANUAL')
    receipt_number = db.Column(db.String(50))
    
    # M-PESA fields
    mpesa_transaction_id = db.Column(db.String(50), unique=True)
    mpesa_phone_number = db.Column(db.String(20))


class TransactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    reference = db.Column(db.String(50))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))




class CRBSimulation(db.Model):
    """Simulated CRB data for users"""
    __tablename__ = 'crb_simulation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    national_id = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    credit_score = db.Column(db.Integer, default=500)
    credit_rating = db.Column(db.String(20), default='FAIR')
    npa_count = db.Column(db.Integer, default=0)
    payment_history = db.Column(db.String(20), default='GOOD')
    default_history = db.Column(db.Boolean, default=False)
    simulated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('crb_report', uselist=False))
    
    def to_dict(self):
        return {
            'credit_score': self.credit_score,
            'credit_rating': self.credit_rating,
            'npa_count': self.npa_count,
            'payment_history': self.payment_history,
            'default_history': self.default_history
        }
    
    def get_risk_level(self):
        if self.credit_score >= 700:
            return 'LOW'
        elif self.credit_score >= 600:
            return 'LOW-MEDIUM'
        elif self.credit_score >= 500:
            return 'MEDIUM'
        elif self.credit_score >= 400:
            return 'HIGH'
        else:
            return 'VERY HIGH'
    
    def get_recommendation(self):
        if self.default_history:
            return '❌ REJECTED: History of default'
        elif self.npa_count > 2:
            return '❌ REJECTED: Multiple NPA accounts'
        elif self.credit_score >= 700:
            return '✅ APPROVED: Excellent credit history'
        elif self.credit_score >= 600:
            return '✅ APPROVED: Good credit history'
        elif self.credit_score >= 500:
            return '⚠️ APPROVED WITH CONDITIONS: Fair credit history'
        elif self.credit_score >= 400:
            return '⚠️ REVIEW REQUIRED: Poor credit history'
        else:
            return '❌ REJECTED: Very poor credit history'


class CRBSimulationLog(db.Model):
    """Logs all CRB simulation checks"""
    __tablename__ = 'crb_simulation_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=True)
    credit_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(20))
    is_simulated = db.Column(db.Boolean, default=True)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('crb_simulation_logs', lazy=True))




@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            phone_number = request.form['phone_number']
            id_number = request.form['id_number']
            full_name = request.form['full_name']
            
            if not all([username, email, password, phone_number, id_number, full_name]):
                flash('All fields are required', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(id_number=id_number).first():
                flash('ID Number already registered', 'danger')
                return render_template('register.html')
            
            user = User(
                username=username,
                email=email,
                phone_number=phone_number,
                id_number=id_number,
                full_name=full_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
           
            from app.utils.crb_simulator import CRBSimulator
            crb_data = CRBSimulator.generate_score_for_user(user)
            
            crb = CRBSimulation(
                user_id=user.id,
                national_id=user.id_number,
                full_name=user.full_name,
                phone_number=user.phone_number,
                credit_score=crb_data['credit_score'],
                credit_rating=crb_data['credit_rating'],
                npa_count=crb_data['npa_count'],
                payment_history=crb_data['payment_history'],
                default_history=crb_data['default_history']
            )
            db.session.add(crb)
            
            log = CRBSimulationLog(
                user_id=user.id,
                credit_score=crb_data['credit_score'],
                risk_level=CRBSimulator.get_risk_level(crb_data['credit_score']),
                is_simulated=True
            )
            db.session.add(log)
            
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    try:
        loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.application_date.desc()).all()
        
        total_loans = len(loans)
        active_loans = len([l for l in loans if l.status == 'ACTIVE'])
        total_borrowed = sum(l.loan_amount for l in loans if l.status in ['ACTIVE', 'COMPLETED'])
        pending_repayments = sum(l.monthly_installment for l in loans if l.status == 'ACTIVE')
        
        recent_payments = Payment.query.join(Loan).filter(
            Loan.user_id == current_user.id
        ).order_by(Payment.payment_date.desc()).limit(5).all()
        
        risk_score = 0
        active_loans_list = [l for l in loans if l.status == 'ACTIVE']
        if active_loans_list:
            risk_score = sum(l.risk_score for l in active_loans_list) // len(active_loans_list)
        
        crb = CRBSimulation.query.filter_by(user_id=current_user.id).first()
        crb_score = crb.credit_score if crb else 500
        crb_rating = crb.credit_rating if crb else 'N/A'
        
        return render_template('dashboard.html',
                             loans=loans,
                             total_loans=total_loans,
                             active_loans=active_loans,
                             total_borrowed=total_borrowed,
                             pending_repayments=pending_repayments,
                             recent_payments=recent_payments,
                             risk_score=risk_score,
                             crb_score=crb_score,
                             crb_rating=crb_rating)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html')




@app.route('/dashboard/download_loans')
@login_required
def download_my_loans():
    """Download user's loans as PDF"""
    try:
        from app.utils.user_pdf_generator import UserReportGenerator
        
        loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.application_date.desc()).all()
        
        risk_score = 0
        active_loans_list = [l for l in loans if l.status == 'ACTIVE']
        if active_loans_list:
            risk_score = sum(l.risk_score for l in active_loans_list) // len(active_loans_list)
        
        crb = CRBSimulation.query.filter_by(user_id=current_user.id).first()
        crb_score = crb.credit_score if crb else 500
        crb_rating = crb.credit_rating if crb else 'N/A'
        
        payments = Payment.query.join(Loan).filter(
            Loan.user_id == current_user.id
        ).order_by(Payment.payment_date.desc()).limit(10).all()
        
        filename = f"my_loans_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        
        UserReportGenerator.generate_user_report(
            current_user, loans, payments, risk_score, crb_score, crb_rating, filepath
        )
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/dashboard/download_payments')
@login_required
def download_my_payments():
    """Download user's payment history as PDF"""
    try:
        from app.utils.user_pdf_generator import UserReportGenerator
        
        loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.application_date.desc()).all()
        
        payments = Payment.query.join(Loan).filter(
            Loan.user_id == current_user.id
        ).order_by(Payment.payment_date.desc()).all()
        
        risk_score = 0
        active_loans_list = [l for l in loans if l.status == 'ACTIVE']
        if active_loans_list:
            risk_score = sum(l.risk_score for l in active_loans_list) // len(active_loans_list)
        
        crb = CRBSimulation.query.filter_by(user_id=current_user.id).first()
        crb_score = crb.credit_score if crb else 500
        crb_rating = crb.credit_rating if crb else 'N/A'
        
        filename = f"my_payments_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        
        UserReportGenerator.generate_user_report(
            current_user, loans, payments, risk_score, crb_score, crb_rating, filepath
        )
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))



@app.route('/apply_loan', methods=['GET', 'POST'])
@login_required
def apply_loan():
    if request.method == 'POST':
        try:
            loan_amount = float(request.form['loan_amount'])
            loan_period = int(request.form['loan_period'])
            loan_purpose = request.form['loan_purpose']
            
            interest_rate = 10.0
            total_amount = loan_amount * (1 + (interest_rate / 100) * (loan_period / 12))
            monthly_installment = total_amount / loan_period
            
            loan = Loan(
                user_id=current_user.id,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                loan_period=loan_period,
                monthly_installment=monthly_installment,
                total_amount=total_amount,
                loan_purpose=loan_purpose,
                status='PENDING'
            )
            
            crb_report = CRBSimulation.query.filter_by(user_id=current_user.id).first()
            
            if crb_report:
                crb_dict = {
                    'credit_score': crb_report.credit_score,
                    'npa_count': crb_report.npa_count,
                    'default_history': crb_report.default_history,
                    'payment_history': crb_report.payment_history,
                    'recommendation': crb_report.get_recommendation()
                }
                final_score = loan.calculate_risk_with_crb(crb_dict)
            else:
                final_score = loan.calculate_risk_score()
                loan.risk_with_crb = final_score
            
            loan.risk_score = final_score
            
            db.session.add(loan)
            db.session.commit()
            
            flash('Loan application submitted successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error applying for loan: {str(e)}', 'danger')
            return render_template('apply_loan.html')
    
    return render_template('apply_loan.html')


@app.route('/make_payment', methods=['POST'])
@login_required
def make_payment():
    """Manual payment recording (for admin use)"""
    try:
        loan_id = request.form['loan_id']
        amount = float(request.form['amount'])
        
        loan = Loan.query.get(loan_id)
        if not loan or loan.user_id != current_user.id:
            flash('Invalid loan', 'danger')
            return redirect(url_for('dashboard'))
        
        payment = Payment(
            loan_id=loan_id,
            amount=amount,
            due_date=datetime.utcnow() + timedelta(days=30),
            status='COMPLETED',
            payment_method='MANUAL'
        )
        payment.receipt_number = f'RCP{payment.id}'
        
        db.session.add(payment)
        db.session.commit()
        
        payments = Payment.query.filter_by(loan_id=loan_id, status='COMPLETED').all()
        total_paid = sum(p.amount for p in payments)
        
        if total_paid >= loan.total_amount:
            loan.status = 'COMPLETED'
        else:
            loan.status = 'ACTIVE'
        
        db.session.commit()
        
        flash(f'Payment of KSh {amount:,.2f} recorded successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Payment failed: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))



@app.route('/mpesa/initiate', methods=['POST'])
@login_required
def initiate_mpesa_payment():
    """Initiate an M-PESA STK Push payment"""
    try:
        from app.utils.mpesa import MpesaClient
        
        loan_id = request.form.get('loan_id')
        amount = float(request.form.get('amount'))
        phone_number = request.form.get('phone_number')
        
        # Get the loan
        loan = Loan.query.get(loan_id)
        if not loan or loan.user_id != current_user.id:
            flash('Invalid loan', 'danger')
            return redirect(url_for('dashboard'))
        
        if amount <= 0:
            flash('Invalid amount', 'danger')
            return redirect(url_for('dashboard'))
        
  
        phone_exists = User.query.filter_by(phone_number=phone_number).first() is not None
        
    
        mpesa = MpesaClient()
        
 
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=f"LOAN{loan_id}",
            transaction_desc="Loan Payment"
        )
        
        if response.get('error'):
            flash(f'Payment failed: {response.get("error")}', 'danger')
            return redirect(url_for('dashboard'))
        
        if response.get('ResponseCode') == '0':
            checkout_id = response.get('CheckoutRequestID')
            
        
            payment = Payment(
                loan_id=loan_id,
                amount=amount,
                due_date=datetime.utcnow() + timedelta(days=30),
                status='PENDING',
                payment_method='MPESA'
            )
            payment.mpesa_transaction_id = checkout_id
            payment.mpesa_phone_number = phone_number
            
       
            if phone_exists:
                payment.status = 'COMPLETED'
                payment.receipt_number = f'MPESA{checkout_id[-8:]}'
                
               
                existing_payments = Payment.query.filter_by(
                    loan_id=loan_id,
                    status='COMPLETED'
                ).all()
                total_paid = sum(p.amount for p in existing_payments) + amount
                
                if total_paid >= loan.total_amount:
                    loan.status = 'COMPLETED'
                else:
                    loan.status = 'ACTIVE'
                
        
                log = TransactionLog(
                    user_id=current_user.id,
                    transaction_type='PAYMENT',
                    amount=amount,
                    description=f'Payment for loan {loan_id}',
                    reference=payment.receipt_number,
                    status='COMPLETED'
                )
                db.session.add(log)
                
                db.session.add(payment)
                db.session.commit()
                
                flash(f'✅ Payment of KSh {amount:,.2f} completed successfully!', 'success')
            else:

                db.session.add(payment)
                db.session.commit()
                
                flash('⏳ STK Push sent. Payment is PENDING.', 'info')
        else:
            flash(f'Payment initiation failed: {response.get("ResponseDescription", "Unknown error")}', 'danger')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-PESA callback notification"""
    try:
        data = request.json
        print(f"Callback received: {data}")
        
        result = data.get('Body', {}).get('stkCallback', {})
        
        result_code = result.get('ResultCode')
        checkout_request_id = result.get('CheckoutRequestID')
        result_desc = result.get('ResultDesc')
        
        payment = Payment.query.filter_by(mpesa_transaction_id=checkout_request_id).first()
        
        if not payment:
            print(f"Payment not found for CheckoutRequestID: {checkout_request_id}")
            return jsonify({'ResultCode': 1, 'ResultDesc': 'Payment not found'}), 404
        

        if payment.status == 'COMPLETED':
            print(f"Payment {payment.id} already completed. Ignoring callback.")
            return jsonify({'ResultCode': 0, 'ResultDesc': 'Already processed'})
        
        if result_code == 0:

            payment.status = 'COMPLETED'
            
            callback_metadata = result.get('CallbackMetadata', {})
            if callback_metadata and callback_metadata.get('Item'):
                for item in callback_metadata['Item']:
                    if item.get('Name') == 'Amount':
                        payment.amount = item.get('Value')
                    elif item.get('Name') == 'MpesaReceiptNumber':
                        payment.receipt_number = item.get('Value')
            
            loan = Loan.query.get(payment.loan_id)
            if loan:
                total_paid = Payment.query.filter_by(
                    loan_id=loan.id,
                    status='COMPLETED'
                ).with_entities(db.func.sum(Payment.amount)).scalar() or 0
                
                if total_paid >= loan.total_amount:
                    loan.status = 'COMPLETED'
                elif total_paid > 0:
                    loan.status = 'ACTIVE'
                
                log = TransactionLog(
                    user_id=loan.user_id,
                    transaction_type='PAYMENT',
                    amount=payment.amount,
                    description=f'Payment for loan {loan.id}',
                    reference=payment.receipt_number,
                    status='COMPLETED'
                )
                db.session.add(log)
            
            db.session.commit()
            print(f"✅ Payment {payment.id} completed successfully")
            
        else:
           
            print(f"⚠️ Callback failed: {result_desc}")
            print(f"   Payment {payment.id} stays PENDING for manual completion")
            
         
            log = TransactionLog(
                user_id=payment.loan.user_id,
                transaction_type='PAYMENT_FAILED',
                amount=payment.amount,
                description=f'Sandbox callback failed: {result_desc}',
                reference=checkout_request_id,
                status='FAILED'
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing callback: {e}")
        return jsonify({'ResultCode': 1, 'ResultDesc': str(e)}), 500
@app.route('/mpesa/status/<transaction_id>')
@login_required
def check_payment_status(transaction_id):
    """Check the status of a payment"""
    try:
        from app.utils.mpesa import MpesaClient
        
        payment = Payment.query.filter_by(mpesa_transaction_id=transaction_id).first()
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        mpesa = MpesaClient()
        response = mpesa.check_payment_status(transaction_id)
        
        if response.get('error'):
            return jsonify({'status': 'error', 'message': response.get('error')})
        
        if response.get('ResultCode') == '0':
            payment.status = 'COMPLETED'
            db.session.commit()
        
        return jsonify({
            'status': payment.status,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    all_loans = Loan.query.order_by(Loan.application_date.desc()).all()
    pending_loans_list = Loan.query.filter_by(status='PENDING').order_by(Loan.application_date.desc()).all()
    all_users = User.query.all()
    
    total_loans = len(all_loans)
    pending_loans = len(pending_loans_list)
    active_loans = len([l for l in all_loans if l.status == 'ACTIVE'])
    defaulted_loans = len([l for l in all_loans if l.status == 'DEFAULTED'])
    total_lent = sum(l.loan_amount for l in all_loans if l.status in ['ACTIVE', 'COMPLETED'])
    
    return render_template('admin.html',
                         all_loans=all_loans,
                         pending_loans_list=pending_loans_list,
                         all_users=all_users,
                         total_loans=total_loans,
                         pending_loans=pending_loans,
                         active_loans=active_loans,
                         defaulted_loans=defaulted_loans,
                         total_lent=total_lent)


@app.route('/admin/approve_loan/<int:loan_id>')
@login_required
@admin_required
def approve_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        if loan:
            loan.status = 'APPROVED'
            loan.approval_date = datetime.utcnow()
            loan.due_date = datetime.utcnow() + timedelta(days=loan.loan_period * 30)
            db.session.commit()
            flash('Loan approved successfully', 'success')
    except Exception as e:
        flash(f'Error approving loan: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/reject_loan/<int:loan_id>')
@login_required
@admin_required
def reject_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        if loan:
            loan.status = 'REJECTED'
            db.session.commit()
            flash('Loan rejected', 'info')
    except Exception as e:
        flash(f'Error rejecting loan: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/activate_loan/<int:loan_id>')
@login_required
@admin_required
def activate_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        if loan:
            loan.status = 'ACTIVE'
            loan.due_date = datetime.utcnow() + timedelta(days=loan.loan_period * 30)
            db.session.commit()
            flash('Loan activated successfully', 'success')
    except Exception as e:
        flash(f'Error activating loan: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))




@app.route('/reports/risk_assessment')
@login_required
@admin_required
def risk_assessment_report():
    try:
        all_loans = Loan.query.all()
        
        high_risk_loans = [l for l in all_loans if l.risk_score >= 70]
        medium_risk_loans = [l for l in all_loans if 40 <= l.risk_score < 70]
        low_risk_loans = [l for l in all_loans if l.risk_score < 40]
        
        risk_metrics = {
            'total_loans': len(all_loans),
            'high_risk': len(high_risk_loans),
            'medium_risk': len(medium_risk_loans),
            'low_risk': len(low_risk_loans),
            'average_risk': sum(l.risk_score for l in all_loans) / len(all_loans) if all_loans else 0,
            'default_rate': len([l for l in all_loans if l.status == 'DEFAULTED']) / len(all_loans) * 100 if all_loans else 0
        }
        
        return render_template('risk_report.html',
                             risk_metrics=risk_metrics,
                             high_risk_loans=high_risk_loans,
                             medium_risk_loans=medium_risk_loans,
                             low_risk_loans=low_risk_loans)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/reports/download_risk_pdf')
@login_required
@admin_required
def download_risk_pdf():
    """Generate and download risk report as PDF"""
    try:
        from app.utils.pdf_generator import PDFReportGenerator
        
        all_loans = Loan.query.all()
        
        high_risk_loans = [l for l in all_loans if l.risk_score >= 70]
        medium_risk_loans = [l for l in all_loans if 40 <= l.risk_score < 70]
        low_risk_loans = [l for l in all_loans if l.risk_score < 40]
        
        risk_metrics = {
            'total_loans': len(all_loans),
            'high_risk': len(high_risk_loans),
            'medium_risk': len(medium_risk_loans),
            'low_risk': len(low_risk_loans),
            'average_risk': sum(l.risk_score for l in all_loans) / len(all_loans) if all_loans else 0,
            'default_rate': len([l for l in all_loans if l.status == 'DEFAULTED']) / len(all_loans) * 100 if all_loans else 0
        }
        
        filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        
        os.makedirs('temp', exist_ok=True)
        
        PDFReportGenerator.generate_risk_report(
            risk_metrics,
            high_risk_loans,
            medium_risk_loans,
            low_risk_loans,
            filepath
        )
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('risk_assessment_report'))



@app.route('/admin/crb_reports')
@login_required
@admin_required
def crb_reports():
    crb_reports = CRBSimulation.query.all()
    return render_template('crb_report.html', crb_reports=crb_reports)


@app.route('/admin/crb_reports/download')
@login_required
@admin_required
def download_crb_pdf():
    """Generate and download CRB report as PDF"""
    try:
        from app.utils.crb_pdf_generator import CRBReportGenerator
        
        crb_reports = CRBSimulation.query.all()
        
        filename = f"crb_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        
        os.makedirs('temp', exist_ok=True)
        
        CRBReportGenerator.generate_crb_report(crb_reports, filepath)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating CRB PDF: {str(e)}', 'danger')
        return redirect(url_for('crb_reports'))




@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
