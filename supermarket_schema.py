import sys
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# 1. جدول المخزن (Inventory)
class InventoryItem(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)           # الاسم
    quantity = Column(Integer, default=0)                # الكمية
    cost_price = Column(Float, nullable=False)           # سعر التكلفة
    selling_price = Column(Float, nullable=False)        # سعر البيع
    
    # علاقة مع جدول المبيعات
    sales = relationship('Sale', back_populates='item')

# 2. جدول المبيعات (Sales)
class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.datetime.utcnow) # التاريخ
    item_id = Column(Integer, ForeignKey('inventory.id'))     # الصنف (مربوط بالمخزن)
    quantity = Column(Integer, nullable=False)                # الكمية
    total = Column(Float, nullable=False)                     # الإجمالي
    
    item = relationship('InventoryItem', back_populates='sales')

# 3. جدول الديون (Debts)
class Debt(Base):
    __tablename__ = 'debts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)       # اسم العميل
    current_debt = Column(Float, default=0.0)                 # المديونية الحالية
    last_payment_date = Column(DateTime, nullable=True)       # تاريخ آخر دفع
    expected_payment_date = Column(DateTime, nullable=True)    # تاريخ السداد المتوقع
    notes = Column(String(500), nullable=True)                 # ملاحظات

# 4. جدول المستخدمين (Users)
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default='Agency') # Admin or Agency

# ==========================================
# إعداد الاتصال بقاعدة بيانات Google Cloud SQL
# ==========================================

def get_engine(db_user, db_pass, db_name, db_host=None, connection_name=None, db_type='postgresql'):
    """
    تقوم هذه الدالة بإنشاء محرك الاتصال بقاعدة البيانات.
    يمكن استخدامها للاتصال بـ Google Cloud SQL (سواء PostgreSQL أو MySQL).
    """
    if db_type == 'postgresql':
        if connection_name:
            # استخدام Unix Socket للاتصال الآمن (مفضل في بيئة GCP)
            db_url = f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock=/cloudsql/{connection_name}/.s.PGSQL.5432"
        else:
            db_url = f"postgresql+pg8000://{db_user}:{db_pass}@{db_host}/{db_name}"
            
    elif db_type == 'mysql':
        if connection_name:
            db_url = f"mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket=/cloudsql/{connection_name}"
        else:
            db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
    else:
        # اتصال محلي للتجربة
        db_url = "sqlite:///supermarket.db"

    return create_engine(db_url)

def create_tables(engine):
    """إنشاء جميع الجداول في قاعدة البيانات"""
    Base.metadata.create_all(engine)
    
    # إضافة مدير افتراضي إذا لم يكن موجوداً
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # البحث عن مستخدم باسم 'admin'
        admin_exists = session.query(User).filter_by(username='admin').first()
        if not admin_exists:
            admin_user = User(username='admin', password='123', role='Admin')
            session.add(admin_user)
            session.commit()
            print("Admin user created (admin / 123)")
    except Exception as e:
        print(f"Error checking/creating admin user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # مثال للتجربة محلياً باستخدام SQLite
    engine = get_engine('', '', '', db_type='sqlite')
    create_tables(engine)
