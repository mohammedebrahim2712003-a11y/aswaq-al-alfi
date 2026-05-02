import sys
import streamlit as st
import pandas as pd
from sqlalchemy import func, text
from sqlalchemy.orm import sessionmaker
from supermarket_schema import get_engine, InventoryItem, Debt, User, Sale, create_tables
import datetime
import io

# 1. إعداد الصفحة وتنسيق اللغة العربية
st.set_page_config(page_title="أسواق الألفي - نظام الإدارة المتكامل", layout="wide", page_icon="🛒")

# تطبيق التنسيق الجمالي المتطور (Aesthetics)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* التنسيق العام والخطوط */
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    /* الخلفية الدافئة والمتميزة (Warm Background) */
    .stApp {
        background: linear-gradient(135deg, #FDF5E6 0%, #FFF5EE 100%) !important;
        background-attachment: fixed !important;
    }

    /* تأثيرات الصور الخلفية اللطيفة */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        opacity: 0.03;
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 86c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm66 3c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM37 7c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm92 12c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23000' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E");
        pointer-events: none;
    }

    /* جعل جميع النصوص عريضة وواضحة (Bold Text) */
    .stApp, .stMarkdown, p, span, h1, h2, h3, h4, h5, h6, label, .stMetric, .stDataFrame, .stTable, [data-testid="stSidebar"], div[data-testid="stForm"] {
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }

    h1, h2, h3 {
        color: #004d66 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* تنسيق الحاويات والنماذج (Glassmorphism Effect) */
    div[data-testid="stForm"], .stExpander {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 20px;
    }

    /* تحسين مظهر الأزرار (Premium Buttons) */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #004d66, #007a99) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        width: 100%;
        height: 50px;
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
        background: linear-gradient(45deg, #005d7a, #008eb3) !important;
    }

    /* تنسيق المربعات الإحصائية (Metrics) */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 900 !important;
        color: #004d66 !important;
    }

    /* تحسين الجداول */
    .stDataFrame {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }

    /* الوضع الليلي */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(10px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. الوضع الليلي (Night Mode)
night_mode = st.sidebar.toggle('الوضع الليلي 🌙')
if night_mode:
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%) !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, label, .stMetric, [data-testid="stMetricValue"] {
            color: #ecf0f1 !important;
        }
        div[data-testid="stForm"], .stExpander {
            background: rgba(44, 62, 80, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.7) !important;
        }
        </style>
        """, unsafe_allow_html=True)

# 3. إعداد قاعدة البيانات (مع التحديث التلقائي للجداول)
def init_db():
    engine = get_engine('', '', '', db_type='sqlite')
    create_tables(engine)
    
    # تحديث تلقائي للأعمدة الناقصة (Migration) لتجنب الـ OperationalError
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if 'debts' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('debts')]
        with engine.connect() as conn:
            if 'expected_payment_date' not in columns:
                conn.execute(text("ALTER TABLE debts ADD COLUMN expected_payment_date DATETIME"))
            if 'notes' not in columns:
                conn.execute(text("ALTER TABLE debts ADD COLUMN notes VARCHAR(500)"))
            conn.commit()
    return engine

# 4. إدارة الجلسة (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = ''

# 5. شاشة تسجيل الدخول
def login_screen(Session):
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'><b>🛒 أسواق الألفي</b></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; opacity: 0.8;'>مرحباً بكم في نظام الإدارة الذكي</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### **تسجيل الدخول**")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submit_login = st.form_submit_button("دخول آمن")
            
            if submit_login:
                # 1. الدخول الطارئ (Emergency Bypass) لضمان العمل دائماً
                if username == 'admin' and password == '123':
                    st.session_state.logged_in = True
                    st.session_state.username = 'admin'
                    st.session_state.role = 'Admin'
                    st.success("تم تسجيل الدخول (دخول طارئ)")
                    st.rerun()
                
                # 2. التحقق العادي من قاعدة البيانات
                session = Session()
                user = session.query(User).filter_by(username=username, password=password).first()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user.username
                    st.session_state.role = user.role
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
                session.close()
                
    st.markdown("<p style='text-align: center; font-size: 0.9rem; opacity: 0.6;'>في حال نسيان كلمة المرور، يرجى مراجعة الإدارة</p>", unsafe_allow_html=True)

# 6. دالة لتصدير البيانات إلى إكسيل
def export_to_excel(df, sheet_name, filename):
    buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"خطأ في تصدير الإكسيل: {e}")
        return None
    return buffer.getvalue()

# 7. التطبيق الرئيسي (بعد تسجيل الدخول)
def main_app(Session):
    # الهيدر الاحترافي
    st.markdown("""
        <div style="background: linear-gradient(90deg, #004d66, #007a99); padding: 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h1 style="color: white !important; margin: 0; text-align: center;"><b>أسواق الألفي - لوحة التحكم</b></h1>
        </div>
    """, unsafe_allow_html=True)
    
    session = Session()
    
    # حساب الإحصائيات السريعة
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_sales_today = session.query(func.sum(Sale.total)).filter(Sale.date >= today).scalar() or 0
    transaction_count = session.query(func.count(Sale.id)).filter(Sale.date >= today).scalar() or 0
    top_sale = session.query(Sale.item_id, func.sum(Sale.quantity).label('qty'))\
                      .group_by(Sale.item_id).order_by(text('qty DESC')).first()
    
    top_item_name = "لا يوجد"
    if top_sale:
        item = session.query(InventoryItem).filter_by(id=top_sale[0]).first()
        if item: top_item_name = item.name

    # عرض البطاقات الإحصائية بتصميم مودرن
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("أكثر صنف مبيعاً 🏆", top_item_name)
    with c2:
        st.metric("مبيعات اليوم 💰", f"{total_sales_today:,.2f} ج.م")
    with c3:
        st.metric("عدد العمليات 🛒", transaction_count)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # السايد بار
    st.sidebar.markdown(f"### **مرحباً: {st.session_state.username}**")
    st.sidebar.markdown(f"**الصلاحية:** `{st.session_state.role}`")
    st.sidebar.markdown("---")
    
    pages = ["🛒 نظام البيع", "📦 إدارة المخزن", "💵 نوتة الديون (Ledger)", "📈 التقارير الشاملة", "⚙️ إعدادات الحساب"]
    if st.session_state.role == "Admin":
        pages.insert(4, "🛡️ إدارة المستخدمين")
        
    page = st.sidebar.radio("القائمة الرئيسية:", pages)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("تسجيل الخروج 📤"):
        st.session_state.logged_in = False
        st.rerun()

    # ======================================================
    # نظام البيع (POS)
    # ======================================================
    if page == "🛒 نظام البيع":
        st.header("**🛒 واجهة البيع السريع**")
        
        items = session.query(InventoryItem).filter(InventoryItem.quantity > 0).all()
        if not items:
            st.warning("المخزن فارغ! يرجى إضافة أصناف في صفحة المخزن.")
        else:
            with st.form("sales_form"):
                col_item, col_qty = st.columns([3, 1])
                item_options = {f"{i.name} (متوفر: {i.quantity}) - {i.selling_price} ج.م": i for i in items}
                selected_item_str = col_item.selectbox("اختر الصنف 🍎", list(item_options.keys()))
                sell_qty = col_qty.number_input("الكمية 🔢", min_value=1, step=1)
                
                submit_sale = st.form_submit_button("إتمام العملية وتحديث المخزن ✅")
                
                if submit_sale:
                    item = item_options[selected_item_str]
                    if sell_qty > item.quantity:
                        st.error("الكمية المطلوبة أكبر من المتوفر!")
                    else:
                        total_price = sell_qty * item.selling_price
                        new_sale = Sale(item_id=item.id, quantity=sell_qty, total=total_price)
                        item.quantity -= sell_qty
                        session.add(new_sale)
                        session.commit()
                        st.balloons()
                        st.success(f"تمت العملية بنجاح! الإجمالي: {total_price:,.2f} ج.م")
                        st.rerun()

    # ======================================================
    # إدارة المخزن
    # ======================================================
    elif page == "📦 إدارة المخزن":
        st.header("**📦 إدارة المخزون والأصناف**")
        
        with st.expander("➕ إضافة أو تحديث صنف"):
            with st.form("inventory_form"):
                name = st.text_input("اسم الصنف")
                col_a, col_b, col_c = st.columns(3)
                quantity = col_a.number_input("الكمية المضافة", min_value=0, step=1)
                cost_price = col_b.number_input("سعر التكلفة (ج.م)", min_value=0.0)
                selling_price = col_c.number_input("سعر البيع (ج.م)", min_value=0.0)
                
                submit = st.form_submit_button("حفظ البيانات")
                
                if submit:
                    if name:
                        item = session.query(InventoryItem).filter_by(name=name).first()
                        if item:
                            item.quantity += quantity
                            item.cost_price = cost_price if cost_price > 0 else item.cost_price
                            item.selling_price = selling_price if selling_price > 0 else item.selling_price
                            st.success(f"تم تحديث {name}")
                        else:
                            new_item = InventoryItem(name=name, quantity=quantity, cost_price=cost_price, selling_price=selling_price)
                            session.add(new_item)
                            st.success(f"تمت إضافة {name}")
                        session.commit()
                        st.rerun()

        st.subheader("**📋 قائمة الأصناف**")
        items = session.query(InventoryItem).all()
        if items:
            df_items = pd.DataFrame([{
                "م": i.id,
                "الصنف": i.name,
                "الكمية": i.quantity,
                "سعر التكلفة": i.cost_price,
                "سعر البيع": i.selling_price,
                "القيمة الإجمالية": i.quantity * i.cost_price
            } for i in items])
            
            # تمييز الكميات القليلة
            def highlight_low_stock(val):
                color = 'red' if val < 5 else 'black'
                return f'color: {color}'
            
            st.dataframe(df_items.style.applymap(highlight_low_stock, subset=['الكمية']), use_container_width=True)
            
            # تصدير إكسيل للمخزن
            excel_data = export_to_excel(df_items, "المخزن", "inventory.xlsx")
            if excel_data:
                st.download_button("📥 تحميل المخزن (Excel)", excel_data, "inventory_alalfi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ======================================================
    # نوتة الديون (Ledger)
    # ======================================================
    elif page == "💵 نوتة الديون (Ledger)":
        st.header("**👥 نوتة ديون العملاء (Ledger)**")
        
        c_add, c_pay = st.columns(2)
        
        with c_add:
            with st.expander("📝 تسجيل مديونية"):
                with st.form("debt_form"):
                    c_name = st.text_input("اسم العميل")
                    amount = st.number_input("المبلغ", min_value=0.0)
                    expected_date = st.date_input("تاريخ السداد المتوقع")
                    notes = st.text_area("ملاحظات")
                    if st.form_submit_button("تسجيل"):
                        if c_name:
                            debt = session.query(Debt).filter_by(customer_name=c_name).first()
                            if debt:
                                debt.current_debt += amount
                                debt.expected_payment_date = datetime.datetime.combine(expected_date, datetime.time())
                                debt.notes = notes
                            else:
                                session.add(Debt(customer_name=c_name, current_debt=amount, 
                                               expected_payment_date=datetime.datetime.combine(expected_date, datetime.time()), 
                                               notes=notes))
                            session.commit()
                            st.success("تم التسجيل")
                            st.rerun()

        with c_pay:
            with st.expander("💰 تحصيل مديونية"):
                with st.form("payment_form"):
                    debts_list = session.query(Debt).filter(Debt.current_debt > 0).all()
                    p_name = st.selectbox("اختر العميل", [d.customer_name for d in debts_list]) if debts_list else st.text_input("اسم العميل")
                    p_amount = st.number_input("المبلغ المحصل", min_value=0.0)
                    if st.form_submit_button("تأكيد التحصيل"):
                        debt = session.query(Debt).filter_by(customer_name=p_name).first()
                        if debt:
                            debt.current_debt -= p_amount
                            debt.last_payment_date = datetime.datetime.now()
                            session.commit()
                            st.success("تم التحصيل")
                            st.rerun()

        st.subheader("**📑 سجل المديونيات الحالية**")
        all_debts = session.query(Debt).all()
        if all_debts:
            df_debts = pd.DataFrame([{
                "العميل": d.customer_name,
                "المبلغ المتبقي": d.current_debt,
                "تاريخ السداد": d.expected_payment_date.strftime("%Y-%m-%d") if d.expected_payment_date else "-",
                "آخر دفعة": d.last_payment_date.strftime("%Y-%m-%d") if d.last_payment_date else "-",
                "ملاحظات": d.notes
            } for d in all_debts])
            
            st.dataframe(df_debts, use_container_width=True)
            
            # إجمالي الديون في الخارج
            total_out = sum(d.current_debt for d in all_debts)
            st.error(f"### **إجمالي الديون في الخارج: {total_out:,.2f} ج.م**")
            
            # تصدير إكسيل للديون
            excel_debts = export_to_excel(df_debts, "الديون", "debts.xlsx")
            if excel_debts:
                st.download_button("📥 تحميل سجل الديون (Excel)", excel_debts, "debts_alalfi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ======================================================
    # التقارير الشاملة
    # ======================================================
    elif page == "📈 التقارير الشاملة":
        st.header("**📊 الإحصائيات والتقارير المالية**")
        
        items = session.query(InventoryItem).all()
        debts = session.query(Debt).all()
        
        v_inv = sum(i.quantity * i.selling_price for i in items)
        v_cost = sum(i.quantity * i.cost_price for i in items)
        v_debt = sum(d.current_debt for d in debts)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("قيمة البضاعة (بيع)", f"{v_inv:,.2f} ج.م")
        col2.metric("قيمة البضاعة (تكلفة)", f"{v_cost:,.2f} ج.م")
        col3.metric("إجمالي الديون لنا", f"{v_debt:,.2f} ج.م")
        
        # رسم بياني بسيط (إذا رغبت في إضافة Plotly مستقبلاً)
        st.info("💡 نصيحة: حافظ على توازن قيمة المخزن مع السيولة النقدية.")

    # ======================================================
    # إدارة المستخدمين (Admin)
    # ======================================================
    elif page == "🛡️ إدارة المستخدمين" and st.session_state.role == "Admin":
        st.header("**🛡️ نظام إدارة الصلاحيات**")
        
        with st.form("user_mgmt"):
            u_name = st.text_input("اسم المستخدم الجديد")
            u_pass = st.text_input("كلمة المرور", type="password")
            u_role = st.selectbox("الصلاحية", ["Agency", "Admin"])
            if st.form_submit_button("إضافة مستخدم"):
                if u_name and u_pass:
                    session.add(User(username=u_name, password=u_pass, role=u_role))
                    session.commit()
                    st.success("تمت الإضافة")
                    st.rerun()
        
        users = session.query(User).all()
        st.table(pd.DataFrame([{"المعرف": u.id, "المستخدم": u.username, "الصلاحية": u.role} for u in users]))

    # ======================================================
    # إعدادات الحساب
    # ======================================================
    elif page == "⚙️ إعدادات الحساب":
        st.header("**⚙️ إعدادات الحساب الشخصي**")
        with st.form("pwd_change"):
            old_p = st.text_input("كلمة المرور الحالية", type="password")
            new_p = st.text_input("كلمة المرور الجديدة", type="password")
            if st.form_submit_button("تحديث كلمة المرور"):
                user = session.query(User).filter_by(username=st.session_state.username).first()
                if user and user.password == old_p:
                    user.password = new_p
                    session.commit()
                    st.success("تم التحديث")
                else:
                    st.error("البيانات غير صحيحة")

    session.close()

def main():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    
    if not st.session_state.logged_in:
        login_screen(Session)
    else:
        main_app(Session)

if __name__ == "__main__":
    main()
