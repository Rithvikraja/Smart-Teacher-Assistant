import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import bcrypt
import qrcode
from io import BytesIO
from datetime import date
import re
import uuid

def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Teacher Assistant", layout="wide")

# ---------------- UI STYLING ----------------
st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #eef2f3, #ffffff);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(#1f4037, #99f2c8);
    color: white;
}

h1 {
    color: #1f4037;
    text-align: center;
    font-weight: bold;
}

h2, h3 {
    color: #2c3e50;
    font-weight: bold;
}

.stButton > button {
    background-color: #1f4037;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #145a32;
}

input {
    border-radius: 6px !important;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid #ddd;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
/* Bigger Sidebar Menu */
section[data-testid="stSidebar"] label {
    font-size: 18px !important;
    font-weight: bold;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 7px 10px !important;
    margin-bottom: 8px !important;
    border-radius: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.2);
    cursor: pointer;

}

</style>
""", unsafe_allow_html=True)

# ---------------- FILES ----------------
USER_FILE = "users.csv"
ATT_FILE = "attendance.csv"
MARKS_FILE = "marks.csv"
ASSIGN_FILE = "assignments.csv"
SLIP_FILE = "slip_tests.csv"


# ---------------- CREATE FILES ----------------
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["Username", "Password"]).to_csv(USER_FILE, index=False)

if not os.path.exists(ATT_FILE):
    pd.DataFrame(
        columns=["Username", "Roll", "Name", "Date", "Status", "DeviceID"]
    ).to_csv(ATT_FILE, index=False)


if not os.path.exists(MARKS_FILE):
    pd.DataFrame(columns=["Username", "Roll", "Name", "Subject", "Marks"]).to_csv(MARKS_FILE, index=False)

if not os.path.exists(ASSIGN_FILE):
    pd.DataFrame(columns=["Username", "Roll", "Name", "Assignment", "File"]).to_csv(ASSIGN_FILE, index=False)
if not os.path.exists(SLIP_FILE):
    pd.DataFrame(
        columns=["Username","Roll","Name","SlipTest","File","Marks"]
    ).to_csv(SLIP_FILE, index=False)



# ---------------- PASSWORD ----------------
def hash_pass(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def check_pass(p, h):
    return bcrypt.checkpw(p.encode(), h.encode())


# ---------------- SIGNUP ----------------
def signup():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Create Account")

    user = st.text_input("Username", key="signup_user")
    pwd = st.text_input("Password", type="password", key="signup_pwd")
    cpwd = st.text_input("Confirm Password", type="password", key="signup_cpwd")

    if st.button("Signup", key="signup_btn"):

        if pwd != cpwd:
            st.error("Passwords not match")
            return

        df = pd.read_csv(USER_FILE)

        if user in df["Username"].values:
            st.warning("User Exists")
            return

        df.loc[len(df)] = [user, hash_pass(pwd)]
        df.to_csv(USER_FILE, index=False)

        st.success("Account Created! Login Now")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- LOGIN ----------------
def login():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    user = st.text_input("Username", key="login_user")
    pwd = st.text_input("Password", type="password", key="login_pwd")

    if st.button("Login", key="login_btn"):

        df = pd.read_csv(USER_FILE)

        if user not in df["Username"].values:
            st.error("User Not Found")
            return

        h = df[df["Username"] == user]["Password"].values[0]

        if check_pass(pwd, h):

            st.session_state.login = True
            st.session_state.user = user

            st.success("Login Success")
            st.rerun()

        else:
            st.error("Wrong Password")

    st.markdown('</div>', unsafe_allow_html=True)

from datetime import timedelta

# ---------------- WORKING DAYS FUNCTION ----------------
def get_working_days(start_date, end_date, holidays=None):
    if holidays is None:
        holidays = []

    count = 0
    current = start_date

    while current <= end_date:
        # weekday(): Monday=0 ... Sunday=6
        if current.weekday() != 6 and current not in holidays:
            count += 1
        current += timedelta(days=1)

    return count

# ---------------- ATTENDANCE ----------------
def attendance():
    # -------- QR CODE ATTENDANCE --------
    st.subheader("📸 QR Attendance (Today)")

    qr_date = st.date_input(
    "Select Date for QR Attendance",
    value=date.today(),
    key="qr_date"
)

    app_url = f"https://smart-teacher-assistant.streamlit.app/?page=student&date={qr_date}"


    

    qr = qrcode.make(app_url)

    buf = BytesIO()
    qr.save(buf)

    st.image(buf.getvalue(), width=200)

    st.caption("Students scan this QR to mark attendance")

    st.divider()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📋 Day-Wise Attendance System")

    user = st.session_state.user

    # -------- MARK ATTENDANCE --------
    # -------- MARK ATTENDANCE --------
with st.expander("📝 Manual Attendance (Click to Open)"):

    selected_date = st.date_input("Select Attendance Date", key="att_date")

    roll = st.text_input("Roll No", key="att_roll")
    name = st.text_input("Student Name", key="att_name")

    status = st.selectbox("Status", ["Present", "Absent"], key="att_status")

    if st.button("Save Attendance", key="att_btn"):


        df = pd.read_csv(ATT_FILE)

        already = df[
            (df["Username"] == user) &
            (df["Roll"] == roll) &
            (df["Date"] == str(selected_date))
            ]

        if len(already) > 0:
            st.warning("Attendance already marked for this day!")
    return

        df.loc[len(df)] = [user, roll, name, selected_date, status]
        df.to_csv(ATT_FILE, index=False)

        st.success("Attendance Saved Successfully")

    st.divider()

    # -------- VIEW BY DATE --------
    st.subheader("📅 View Attendance (By Date)")

    view_date = st.date_input("Choose Date to View", key="att_view_date")

    df = pd.read_csv(ATT_FILE)

    day_data = df[
    ((df["Username"] == user) | (df["Username"] == "QR-STUDENT")) &
    (df["Date"] == str(view_date))
]


    if len(day_data) == 0:
        st.info("No records for this date")
    else:
        st.dataframe(day_data)

    st.divider()
    # Get all dates for this user
    # Get attendance dates only for this teacher
    user_dates = df[
    (df["Username"] == user) | (df["Username"] == "QR-STUDENT")
    ]["Date"]

# Convert to datetime
    all_dates = pd.to_datetime(user_dates, errors="coerce").dropna()

# Find start and end date
    if len(all_dates) > 0:
     start_date = all_dates.min().date()
     end_date = all_dates.max().date()
    else:
     start_date = date.today()
     end_date = date.today()



    # -------- PRESENT COUNT --------
    st.subheader("📊 Student Attendance Summary")

    search_roll = st.text_input("Enter Roll No", key="att_search")

    if search_roll.strip() != "":

        student_data = df[
    ((df["Username"] == user) | (df["Username"] == "QR-STUDENT")) &
    (df["Roll"] == search_roll)
]


        if len(student_data) == 0:
            st.warning("No attendance found for this Roll No")

        else:
            present_days = student_data[student_data["Status"] == "Present"]["Date"].nunique()


            # Calculate working days between start and end date
            total_days = get_working_days(start_date, end_date)
            percentage = round((present_days / total_days) * 100, 2)
            col1, col2 = st.columns(2)

            with col1:
              st.metric("✅ Present Days", present_days)

            with col2:
              st.metric("📊 Attendance %", f"{percentage}%")
                            


          

    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # -------- REGULAR / NON-REGULAR STUDENTS --------
    st.subheader("📈 Regular & Non-Regular Students (50% Criteria)")

    df = pd.read_csv(ATT_FILE)

    user_data = df[
    (df["Username"] == user) | (df["Username"] == "QR-STUDENT")
]

    if len(user_data) == 0:
        st.info("No attendance data available")
        return

    # Group by student
    # Convert Date column to datetime
    user_data["Date"] = pd.to_datetime(user_data["Date"], errors="coerce")

# Get academic range
    all_dates = user_data["Date"].dropna()

    if len(all_dates) > 0:
     start_date = all_dates.min().date()
     end_date = all_dates.max().date()
    else:
     start_date = date.today()
     end_date = date.today()

# Calculate total working days
    total_working_days = get_working_days(start_date, end_date)

# Group by student (only Present count)
    summary = user_data.groupby(
    ["Roll", "Name"]
).agg(
    Present_Days=("Status", lambda x: (x == "Present").sum())
).reset_index()

# Add Total Days column (same for all students)
    summary["Total_Days"] = total_working_days

# Calculate Percentage
    summary["Percentage"] = round(
    (summary["Present_Days"] / summary["Total_Days"]) * 100, 2
)


    # Calculate Percentage
    summary["Percentage"] = round(
        (summary["Present_Days"] / summary["Total_Days"]) * 100, 2
    )

    # Regular / Non-Regular
    summary["Status"] = summary["Percentage"].apply(
        lambda x: "Regular" if x >= 50 else "Non-Regular"
    )

    # Separate tables
    regular = summary[summary["Status"] == "Regular"]
    non_regular = summary[summary["Status"] == "Non-Regular"]

    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ Regular Students (≥ 50%)")

        if len(regular) == 0:
            st.info("No regular students found")
        else:
            st.dataframe(regular)

    with col2:
        st.error("⚠️ Non-Regular Students (< 50%)")

        if len(non_regular) == 0:
            st.info("No non-regular students found")
        else:
            st.dataframe(non_regular)


# ---------------- STUDENT QR ATTENDANCE ----------------
def student_attendance():

    # Load attendance file
    df = pd.read_csv(ATT_FILE)

    # Add DeviceID column if missing (old file fix)
    if "DeviceID" not in df.columns:
        df["DeviceID"] = ""
        df.to_csv(ATT_FILE, index=False)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📱 Student Attendance (QR Scan)")

    query = st.query_params

    if "date" not in query:
        st.error("Invalid QR Code")
        return

    att_date = query["date"]

    st.write(f"📅 Date: **{att_date}**")

    roll = st.text_input("Roll No")
    name = st.text_input("Student Name")

    pattern = r"^\d{5}-[A-Za-z]{3}-\d{3}$"

    # ✅ Create device id BEFORE button
    device_id = get_device_id()

    if st.button("✅ Mark Present"):

        if roll.strip() == "" or name.strip() == "":
            st.warning("Please fill all fields")
            return

        if not re.match(pattern, roll):
            st.error("❌ Invalid Roll No format.")
            return

        # ❌ Check same phone
        phone_used = df[
            (df["DeviceID"] == device_id) &
            (df["Date"] == str(att_date))
        ]

        if len(phone_used) > 0:
            st.error("❌ This phone already marked attendance today")
            return

        # ❌ Check same student
        already = df[
            (df["Roll"] == roll) &
            (df["Date"] == str(att_date))
        ]

        if len(already) > 0:
            st.info("Attendance already marked")
            return

        # ✅ Save
        df.loc[len(df)] = [
            "QR-STUDENT",
            roll,
            name,
            att_date,
            "Present",
            device_id
        ]

        df.to_csv(ATT_FILE, index=False)

        st.success("✅ Attendance Marked Successfully")

    st.markdown('</div>', unsafe_allow_html=True)





# ---------------- ASSIGNMENTS ----------------
def assignments():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📝 Assignments")

    user = st.session_state.user

    # ---------------- SUBMIT SECTION ----------------
    st.subheader("📤 Submission Details")



    roll = st.text_input("Roll No", key="ass_roll")
    name = st.text_input("Student Name", key="ass_name")
    ass = st.text_input("Assignment Name", key="ass_title")

    file = st.file_uploader(
        "Upload File (Optional - Drag & Drop Supported)",
        key="ass_file"
    )
    ass_marks = st.selectbox(
    "Assignment Marks (0 - 10)",
    options=list(range(0, 11)),
    key="ass_marks"
)

    # Fix assignments file if Marks column missing
    df = pd.read_csv(ASSIGN_FILE)

    if "Marks" not in df.columns:
        df["Marks"] = 0
        df.to_csv(ASSIGN_FILE, index=False)

    if st.button("Submit Assignment", key="ass_btn"):

    # Validate marks
     if ass_marks < 0 or ass_marks > 10:
        st.error("❌ Marks must be between 0 and 10")
        return

     if roll.strip() == "" or name.strip() == "" or ass.strip() == "":
        st.warning("Please fill all fields")
        return

     df = pd.read_csv(ASSIGN_FILE)

    # Optional file
     if file is None:
        filename = "No File"
     else:
        filename = file.name

     df.loc[len(df)] = [user, roll, name, ass, filename, ass_marks]
     df.to_csv(ASSIGN_FILE, index=False)

     st.success("✅ Assignment Submitted Successfully")

         


    st.divider()

    # ---------------- MY SUBMISSIONS ----------------
    st.subheader("📂 My Submissions")

    df = pd.read_csv(ASSIGN_FILE)
    mydata = df[df["Username"] == user]

    if len(mydata) == 0:
        st.info("No submissions yet")
    else:
        st.dataframe(mydata)

    st.divider()

    # ---------------- SEARCH BY ROLL ----------------
    st.subheader("🔍 View Completed Assignments (By Roll No)")

    search_roll = st.text_input("Enter Roll No", key="ass_search")

    if search_roll.strip() != "":

        result = mydata[mydata["Roll"] == search_roll]

        if len(result) == 0:
            st.warning("No assignments found for this Roll No")
        else:
            st.success(f"Found {len(result)} assignment(s)")
            st.dataframe(result)

    else:
        st.info("Enter Roll No to search student assignments")


    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SLIP TEST ----------------
def slip_test():

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📝 Slip-Test")

    user = st.session_state.user

    # -------- SUBMIT SLIP TEST --------
    st.subheader("📤 Slip-Test Submission")

    st_roll = st.text_input("Roll No", key="slip_roll_page")
    st_name = st.text_input("Student Name", key="slip_name_page")
    st_title = st.text_input("Slip-Test Title", key="slip_title_page")

    st_marks = st.selectbox(
    "Slip-Test Marks (0 - 10)",
    options=list(range(0, 11)),
    key="slip_marks_page"
)


    st_file = st.file_uploader(
        "Upload Slip-Test File (Optional)",
        key="slip_file_page"
    )

    if st.button("Submit Slip-Test", key="slip_btn_page"):

    # Validate marks
      if st_marks < 0 or st_marks > 10:
        st.error("❌ Marks must be between 0 and 10")
        return

      if st_roll.strip() == "" or st_name.strip() == "" or st_title.strip() == "":
        st.warning("Please fill all fields")
        return

      df = pd.read_csv(SLIP_FILE)

      if st_file is None:
        filename = "No File"
      else:
        filename = st_file.name

      df.loc[len(df)] = [
        user,
        st_roll,
        st_name,
        st_title,
        filename,
        st_marks
    ]

      df.to_csv(SLIP_FILE, index=False)

      st.success("✅ Slip-Test Submitted Successfully")


    st.divider()

    # -------- VIEW RECORDS --------
    st.subheader("📂 My Slip-Test Records")

    df = pd.read_csv(SLIP_FILE)

    my_slips = df[df["Username"] == user]

    if len(my_slips) == 0:
        st.info("No Slip-Test records yet")
    else:
        st.dataframe(my_slips)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MARKS ----------------
def marks():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Student Marks Management")

    user = st.session_state.user

    # ---------------- ENTER MARKS ----------------
    st.subheader("📝 Enter / Update Marks")

    col1, col2 = st.columns(2)

    with col1:
        roll = st.text_input("Roll No", key="marks_roll")
        name = st.text_input("Student Name", key="marks_name")

    with col2:
        subject = st.text_input("Subject", key="marks_subject")
        mark = st.number_input("Marks (0 - 100)", 0, 100, key="marks_value")

    if st.button("💾 Save Marks", key="marks_save"):

        df = pd.read_csv(MARKS_FILE)

        # Check if already exists (Update marks)
        existing = df[
            (df["Username"] == user) &
            (df["Roll"] == roll) &
            (df["Subject"] == subject)
            ]

        if len(existing) > 0:
            df.loc[existing.index, "Marks"] = mark
            st.success("Marks Updated Successfully")
        else:
            df.loc[len(df)] = [user, roll, name, subject, mark]
            st.success("Marks Saved Successfully")

        df.to_csv(MARKS_FILE, index=False)

    st.divider()

    # ---------------- STUDENT SEARCH ----------------
    st.subheader("🔍 View Student Marks")

    search_roll = st.text_input("Enter Roll No to Search", key="marks_search")

    df = pd.read_csv(MARKS_FILE)
    mydata = df[df["Username"] == user]

    if search_roll.strip() != "":

        student_data = mydata[mydata["Roll"] == search_roll]

        if len(student_data) == 0:
            st.warning("No records found for this student")
        else:
            st.dataframe(student_data)

            avg = student_data["Marks"].mean()
            st.info(f"📌 Average Marks: {round(avg, 2)}")

    else:
        st.info("Enter Roll No to view marks")

    st.divider()

    # ---------------- ALL RECORDS ----------------
    st.subheader("📋 My Marks Records")

    if len(mydata) == 0:
        st.warning("No marks data available")
    else:
        st.dataframe(mydata)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- ANALYTICS ----------------
def analytics():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📈 Academic Performance Analytics")

    user = st.session_state.user

    # Load data
    df = pd.read_csv(MARKS_FILE)
    df = df[df["Username"] == user]

    if len(df) == 0:
        st.warning("No marks data available for analysis")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ---------------- SUMMARY METRICS ----------------
    st.subheader("📊 Performance Overview")

    class_avg = round(df["Marks"].mean(), 2)
    highest = df["Marks"].max()
    lowest = df["Marks"].min()
    total_students = df["Roll"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📌 Class Average", class_avg)
    col2.metric("🏆 Highest Marks", highest)
    col3.metric("⚠️ Lowest Marks", lowest)
    col4.metric("👨‍🎓 Students", total_students)

    st.divider()

    # ---------------- SUBJECT FILTER ----------------
    st.subheader("🎯 Subject-wise Analysis")

    subjects = ["All"] + list(df["Subject"].unique())

    selected_sub = st.selectbox(
        "Select Subject",
        subjects,
        key="ana_subject"
    )

    if selected_sub != "All":
        data = df[df["Subject"] == selected_sub]
    else:
        data = df.copy()

    st.write(f"Showing data for: **{selected_sub}**")

    st.dataframe(data)

    st.divider()

    # ---------------- TOP & WEAK STUDENTS ----------------
    st.subheader("🏅 Student Performance Ranking")

    avg_student = data.groupby(["Roll", "Name"])["Marks"].mean().reset_index()

    top5 = avg_student.sort_values("Marks", ascending=False).head(5)
    weak5 = avg_student.sort_values("Marks").head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.write("🌟 Top Performers")
        st.dataframe(top5)

    with col2:
        st.write("⚠️ Weak Performers")
        st.dataframe(weak5)

    st.divider()

    # ---------------- PASS / FAIL ----------------
    st.subheader("✅ Pass / Fail Distribution")

    # Create fresh copy (important for updating)
    temp_data = data.copy()

    PASS_MARK = 35  # Fixed pass mark

    temp_data["Result"] = temp_data["Marks"].apply(
        lambda x: "Pass" if x >= PASS_MARK else "Fail"
    )

    result_count = temp_data["Result"].value_counts()

    fig1, ax1 = plt.subplots()
    result_count.plot(kind="pie", autopct='%1.1f%%', ax=ax1)
    ax1.set_ylabel("")

    st.pyplot(fig1)

    st.divider()

    # ---------------- SUBJECT AVERAGE ----------------
    st.subheader("📚 Subject-wise Average Marks")

    sub_avg = data.groupby("Subject")["Marks"].mean()

    try:
        if len(sub_avg) > 0:

            fig2, ax2 = plt.subplots()
            sub_avg.plot(kind="bar", ax=ax2)
            ax2.set_ylabel("Average Marks")

            st.pyplot(fig2)

        else:
            st.info("Not enough data to show subject-wise chart")

    except Exception:
        st.warning("Subject-wise chart cannot be generated (insufficient data)")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- CHATBOT ----------------
def chatbot():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🤖 AI Assistant")

    st.subheader("Need Advanced Help?")

    st.write("Click the button below to open ChatGPT:")

    # Main redirect button
    st.link_button(
        "💬 Open ChatGPT",
        "https://chat.openai.com",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- DASHBOARD ----------------
def dashboard():
    st.markdown(f"""
    <div>
    <h2 style="color:gold;">👋 Welcome {st.session_state.user}</h2>
    <p>Smart Classroom Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    menu = ["Attendance", "Assignments", "Slip Test", "Marks", "Analytics", "Chatbot", "Logout"]


    choice = st.sidebar.radio("Menu", menu)

    if choice == "Attendance":
        attendance()

    elif choice == "Assignments":
        assignments()
    elif choice == "Slip Test":
        slip_test()

    elif choice == "Marks":
        marks()

    elif choice == "Analytics":
        analytics()

    elif choice == "Chatbot":
        chatbot()

    elif choice == "Logout":

        st.session_state.login = False
        st.rerun()


# ---------------- MAIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

st.markdown("""
<div class="card">
<h1 style="color:green;">🏫 Smart Teacher Assistant</h1>
<p style="text-align:center;font-size:18px;color:black;">
AI + Digital Management System for Teachers
</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Login", "Signup"])
# -------- QR ROUTING --------
query = st.query_params

if "page" in query:

    if query["page"] == "student":
        student_attendance()
        st.stop()

if not st.session_state.login:

    with tab1:
        login()

    with tab2:
        signup()

else:
    dashboard()




































