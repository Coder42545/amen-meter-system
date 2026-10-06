import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
import shutil
import os

# Page Configuration
st.set_page_config(page_title="အိမ်မဲမြို့နယ် လျှပ်စစ်ရုံး - မီတာခစနစ်", page_icon="⚡", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #1b4332;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2d6a4f;
        color: white;
    }
    h1, h2, h3 {
        color: #1b4332;
    }
    </style>
""", unsafe_allow_html=True)

# Database ဖန်တီးခြင်းနှင့် အလိုအလျောက် Backup ယူခြင်း
def init_db():
    db_file = "meter_data.db"
    backup_file = "backup_meter_data.db"
    
    # အကယ်၍ Database ဖိုင် ရှိပြီးသားဆိုရင် အရန်ဖိုင် (Backup) တစ်ခု အမြဲလုပ်ထားမည်
    if os.path.exists(db_file):
        try:
            shutil.copyfile(db_file, backup_file)
        except:
            pass

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # ဇယားမရှိသေးရင် အသစ်ဆောက်မည်
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meter_no TEXT,
            name TEXT,
            unit INTEGER,
            total_bill REAL,
            status TEXT
        )
    """)
    
    # month_year column ရှိမရှိ စစ်ဆေးပြီး မရှိပါက အသစ်ထည့်မည် (Data ဟောင်းများ မပျက်စေရန်)
    cursor.execute("PRAGMA table_info(meters)")
    columns = [col[1] for col in cursor.fetchall()]
    if "month_year" not in columns:
        current_month_year = datetime.now().strftime("%B %Y")
        cursor.execute(f"ALTER TABLE meters ADD COLUMN month_year TEXT DEFAULT '{current_month_year}'")
    
    conn.commit()
    conn.close()

init_db()

# Header / Title
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("logo.png", width=90)
    except:
        st.write("⚡")

with col_title:
    st.markdown("<h1 style='margin-bottom: 0px; font-size: 28px;'>အိမ်မဲမြို့နယ် လျှပ်စစ်ရုံး</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 16px; margin-top: 0px;'>မီတာစာရင်းနှင့် ကျသင့်ငွေများ စီမံခန့်ခွဲမှုစနစ် (ဒေတာလုံခြုံရေး အပြည့်အဝပါဝင်သည်)</p>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# မီတာခ တွက်ချက်ပေးမည့် နှုန်းထား (100 ယူနစ်အထိ ၃၅ကျပ်၊ ကျော်လွန်ပါက ၅၀ကျပ်)
def calculate_bill(unit):
    if unit <= 100:
        return unit * 35
    else:
        return (100 * 35) + ((unit - 100) * 50)

# Sidebar (စာရင်းသွင်းရန် Form)
st.sidebar.markdown("### 📝 မီတာစာရင်း အသစ်သွင်းရန်")

try:
    st.sidebar.image("logo.png", width=70)
except:
    pass

meter_no = st.sidebar.text_input("မီတာနံပါတ်")
name = st.sidebar.text_input("သုံးစွဲသူအမည်")
unit_input = st.sidebar.text_input("သုံးစွဲသည့်ယူနစ် (Units)")

current_month_year = datetime.now().strftime("%B %Y")
month_year = st.sidebar.text_input("စာရင်းသွင်းမည့် လ/နှစ်", value=current_month_year)

status = st.sidebar.selectbox("ငွေပေးချေမှု အခြေအနေ", ["ပေးဆောင်ရန်ရှိ", "ပေးချေပြီး"])

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("စာရင်းသိမ်းမည်", use_container_width=True):
    if meter_no == "" or name == "" or unit_input == "":
        st.sidebar.error("⚠️ အချက်အလက်များကို အစုံအလင် ဖြည့်ပါ။")
    else:
        try:
            unit = int(unit_input)
            bill = calculate_bill(unit)
            
            conn = sqlite3.connect("meter_data.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meters (meter_no, name, unit, total_bill, status, month_year) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (meter_no, name, unit, bill, status, month_year))
            conn.commit()
            conn.close()
            
            # သိမ်းလိုက်တိုင်း Backup ထပ်လုပ်ပေးခြင်း
            try:
                shutil.copyfile("meter_data.db", "backup_meter_data.db")
            except:
                pass
            
            st.sidebar.success(f"✅ မီတာစာရင်း သိမ်းဆည်းပြီးပါပြီ။\n\n**ကျသင့်ငွေ: {bill:,.0f} ကျပ်**")
        except ValueError:
            st.sidebar.error("⚠️ ယူနစ် နေရာတွင် ဂဏန်းသာ ထည့်ပါ။")

# Sidebar အောက်ဆုံးတွင် Database တစ်ခုလုံးကို Backup Download ဆွဲနိုင်သည့် ခလုတ်ထည့်ပေးခြင်း
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 ဒေတာ လုံခြုံရေး Backup")
if os.path.exists("meter_data.db"):
    with open("meter_data.db", "rb") as f:
        st.sidebar.download_button(
            label="📥 Database တစ်ခုလုံး Backup ထုတ်မည်",
            data=f,
            file_name="meter_data_backup.db",
            mime="application/octet-stream"
        )

# ပင်မစာမျက်နှာ - ရှာဖွေရန်နှင့် လအလိုက်စစ်ထုတ်ရန်
col_search, col_filter = st.columns([2, 1])

with col_search:
    st.markdown("### 📊 လက်ရှိ မီတာစာရင်းများနှင့် ကျသင့်ငွေများ")
    search_query = st.text_input("🔍 မီတာနံပါတ် သို့မဟုတ် အမည်ဖြင့် ရှာဖွေရန်", placeholder="ဥပမာ - 003 သို့မဟုတ် ဦးညီ")

with col_filter:
    conn = sqlite3.connect("meter_data.db")
    try:
        months_df = pd.read_sql("SELECT DISTINCT month_year FROM meters", conn)
        available_months = months_df['month_year'].tolist() if not months_df.empty else [current_month_year]
    except:
        available_months = [current_month_year]
    
    selected_month = st.selectbox("📅 လအလိုက် စစ်ထုတ်ရန်", available_months)

# Database ထဲက အချက်အလက်များ ထုတ်ယူခြင်း
if search_query:
    query = f"SELECT * FROM meters WHERE (month_year = '{selected_month}') AND (meter_no LIKE '%{search_query}%' OR name LIKE '%{search_query}%')"
else:
    query = f"SELECT * FROM meters WHERE month_year = '{selected_month}'"

df = pd.read_sql(query, conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 {selected_month} အတွက် Report Download ဆွဲမည်",
        data=csv,
        file_name=f'meter_report_{selected_month}.csv',
        mime='text/csv',
    )
else:
    st.info(f"ℹ️ {selected_month} အတွက် ရှာဖွေတွေ့ရှိသော စာရင်း မရှိသေးပါ။")
