from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    budgets = db.relationship('Budget', backref='user', cascade='all, delete')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Budget(db.Model):
    __table_args__ = (db.UniqueConstraint(
                        'user_id', 
                        'name', 
                        name='unique_budget_name_per_user'),
                     )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    month_duration = db.Column(db.Integer, nullable=False) # 1 = monthly, 12 = yearly
    gross_income = db.Column(db.Numeric(11,2), nullable=False)
    items = db.relationship('BudgetItem', backref='budget', cascade='all, delete')

    def __repr__(self):
        return f'<Budget {self.name}>'

class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    total = db.Column(db.Numeric(11,2), nullable=False)