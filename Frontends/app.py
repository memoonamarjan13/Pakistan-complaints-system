import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Pakistan Public Complaint System",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:Inter,sans-serif;}
.stApp {background:#f5f7fb;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0b3d2e,#082d23);}
[data-testid="stSidebar"] * {color:white !important;}
.brand {padding:8px 0 20px;border-bottom:1px solid #ffffff2b;margin-bottom:18px;}
.brand-title {font-size:21px;font-weight:800;line-height:1.25;}
.brand-sub {font-size:12px;opacity:.75;margin-top:5px;}
.hero {padding:30px;border-radius:20px;background:linear-gradient(135deg,#0b3d2e,#167457);
color:white;margin-bottom:24px;box-shadow:0 10px 30px #0b3d2e22;}
.hero h1 {margin:0;font-size:35px;font-weight:800;}
.hero p {margin:8px 0 0;opacity:.88;}
.section-title {font-size:24px;font-weight:800;color:#17251f;}
.section-sub {color:#68756f;margin-bottom:18px;}
.card {background:white;border:1px solid #e2e8e5;border-radius:16px;padding:20px;
box-shadow:0 5px 18px #1e322a0d;margin-bottom:16px;}
.metric {background:white;border:1px solid #e2e8e5;border-radius:16px;padding:18px;min-height:120px;}
.metric-label {color:#718078;font-size:13px;font-weight:600;}
.metric-value {color:#0b3d2e;font-size:30px;font-weight:800;margin-top:8px;}
.metric-note {color:#8a958f;font-size:12px;margin-top:4px;}
.chat-user {background:#e9f4ef;border:1px solid #d3e7dd;border-radius:15px;
padding:13px 16px;margin:8px 0 8px 18%;}
.chat-bot {background:white;border:1px solid #e1e8e4;border-radius:15px;
padding:15px 17px;margin:8px 18% 8px 0;box-shadow:0 4px 14px #1e322a0b;}
.footer {text-align:center;color:#89958f;font-size:12px;padding:28px 0 10px;}
div.stButton > button {border-radius:10px;font-weight:700;min-height:42px;}
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_question" not in st.session_state:
    st.session_state.chat_question = ""


def api_get(path, timeout=20):
    try:
        return requests.get(f"{API_URL}{path}", timeout=timeout)
    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


def api_post(path, payload, timeout=30):
    try:
        return requests.post(f"{API_URL}{path}", json=payload, timeout=timeout)
    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


def api_patch(path, payload, timeout=20):
    try:
        return requests.patch(f"{API_URL}{path}", json=payload, timeout=timeout)
    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


@st.cache_data(ttl=60, show_spinner=False)
def get_departments():
    r = api_get("/departments")
    if r is not None and r.status_code == 200:
        try:
            data = r.json()
            return data if isinstance(data, list) else []
        except ValueError:
            st.error("Backend returned invalid department data.")
    elif r is not None:
        st.error(f"Could not load departments: {r.text}")
    return []


def did(d):
    return d.get("department_info_id") or d.get("id")


def dname(d):
    return d.get("department_name") or d.get("name") or d.get("department") or "Unknown"


def field(d, *names):
    for name in names:
        if d.get(name) not in (None, ""):
            return d[name]
    return "N/A"


def error_detail(r, title):
    try:
        detail = r.json().get("detail", r.json())
    except Exception:
        detail = r.text
    st.error(f"{title}: {detail}")


def ccategory(c):
    return c.get("complaint_category") or c.get("category") or "N/A"


def cdepartment(c):
    return c.get("department_name") or c.get("department") or "N/A"


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-title">🇵🇰 Pakistan Public<br>Complaint System</div>
      <div class="brand-sub">Citizen complaint management portal</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠 Home", "📝 Submit Complaint", "🏢 Departments",
         "📊 Department Dashboard", "🤖 Complaint Chatbot"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Backend: {API_URL}")


# ---------------- HOME ----------------
if page == "🏠 Home":
    departments = get_departments()

    st.markdown("""
    <div class="hero">
      <h1>Pakistan Public Complaint System</h1>
      <p>A centralized platform for submitting, reviewing and managing public complaints.</p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    metrics = [
        (a, "Departments", len(departments), "Available departments"),
        (b, "Submission", "24/7", "Complaint submission portal"),
        (c, "Tracking", "Live", "Department status updates"),
        (d, "Assistant", "AI", "Complaint data chatbot"),
    ]
    for col, label, value, note in metrics:
        with col:
            st.markdown(
                f'<div class="metric"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    x, y = st.columns([1.2, 1])
    with x:
        st.markdown("""
        <div class="card">
          <h3>How the system works</h3>
          <p><b>1. Submit</b> — Citizen enters complaint information.</p>
          <p><b>2. Register</b> — Backend stores the complaint.</p>
          <p><b>3. Review</b> — Responsible department views assigned complaints.</p>
          <p><b>4. Action</b> — Department records response, priority and status.</p>
          <p><b>5. Query</b> — Chatbot answers supported complaint questions.</p>
        </div>
        """, unsafe_allow_html=True)
    with y:
        st.markdown("""
        <div class="card">
          <h3>Available services</h3>
          <p>📝 Submit a public complaint</p>
          <p>🏢 View department information</p>
          <p>📊 Review assigned complaints</p>
          <p>⚙️ Update status and priority</p>
          <p>🤖 Ask the complaint chatbot</p>
        </div>
        """, unsafe_allow_html=True)


# ---------------- SUBMIT ----------------
elif page == "📝 Submit Complaint":
    st.markdown('<div class="section-title">Submit a Complaint</div>'
                '<div class="section-sub">Provide accurate information so your complaint can be forwarded correctly.</div>',
                unsafe_allow_html=True)

    departments = get_departments()
    if not departments:
        st.warning("No departments available. Check that FastAPI and Supabase are working.")
    else:
        with st.form("complaint_form"):
            st.markdown("### Citizen Information")
            c1, c2 = st.columns(2)
            with c1:
                citizen_name = st.text_input("Citizen Name *", placeholder="Full name")
                phone = st.text_input("Phone Number *", placeholder="03XXXXXXXXX")
                city = st.text_input("City", placeholder="Peshawar")
            with c2:
                cnic = st.text_input("CNIC *", placeholder="XXXXX-XXXXXXX-X")
                province = st.text_input("Province", placeholder="Khyber Pakhtunkhwa")
                address = st.text_area("Address *", height=100)

            st.markdown("### Complaint Information")
            options = {}
            for dep in departments:
                label = dname(dep)
                office = field(dep, "office_section", "section")
                if office != "N/A":
                    label += f" — {office}"
                if did(dep) is not None:
                    label += f" (ID: {did(dep)})"
                options[label] = did(dep)

            selected = st.selectbox("Responsible Department *", list(options))
            selected_id = options[selected]

            c3, c4 = st.columns(2)
            with c3:
                category = st.text_input("Complaint Category",
                                          placeholder="e.g. Fraud Detection")
            with c4:
                priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])

            complaint_text = st.text_area(
                "Complaint Details *",
                height=180,
                placeholder="Clearly describe the complaint and the issue requiring departmental review.",
            )
            submitted = st.form_submit_button(
                "Submit Complaint", type="primary", use_container_width=True
            )

        if submitted:
            required = [
                (citizen_name, "Citizen name"),
                (cnic, "CNIC"),
                (phone, "Phone number"),
                (address, "Address"),
                (complaint_text, "Complaint details"),
            ]
            errors = [f"{name} is required." for value, name in required if not value.strip()]
            if selected_id is None:
                errors.append("Please select a valid department.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                payload = {
                    "citizen_name": citizen_name.strip(),
                    "cnic": cnic.strip(),
                    "phone": phone.strip(),
                    "address": address.strip(),
                    "city": city.strip() or None,
                    "province": province.strip() or None,
                    "department_info_id": selected_id,
                    "complaint_category": category.strip() or None,
                    "complaint_text": complaint_text.strip(),
                    "priority": priority,
                }
                with st.spinner("Registering complaint..."):
                    r = api_post("/complaints", payload, 30)

                if r is not None and r.status_code in (200, 201):
                    try:
                        data = r.json()
                    except ValueError:
                        data = {}
                    st.success("Complaint submitted successfully.")
                    x, y, z = st.columns(3)
                    x.metric("Complaint ID", data.get("id", "N/A"))
                    y.metric("Complaint Number", data.get("complaint_number", "N/A"))
                    z.metric("Status", data.get("status", "Pending"))
                    st.info("Your complaint has been registered and forwarded to the selected department.")
                elif r is not None:
                    error_detail(r, "Complaint submission failed")


# ---------------- DEPARTMENTS ----------------
elif page == "🏢 Departments":
    st.markdown('<div class="section-title">Government Departments</div>'
                '<div class="section-sub">Explore departments available in the complaint system.</div>',
                unsafe_allow_html=True)

    departments = get_departments()
    if not departments:
        st.warning("No departments found.")
    else:
        search = st.text_input("Search departments", placeholder="Search by name...").lower().strip()
        shown = [d for d in departments if search in dname(d).lower()]
        st.caption(f"Showing {len(shown)} of {len(departments)} departments")

        for dep in shown:
            with st.expander(dname(dep)):
                x, y = st.columns(2)
                with x:
                    st.write(f"**Department ID:** {did(dep) or 'N/A'}")
                    st.write(f"**Office Section:** {field(dep, 'office_section', 'section')}")
                    st.write(f"**Department Head:** {field(dep, 'department_head', 'head')}")
                    st.write(f"**Section Officer:** {field(dep, 'section_officer', 'officer')}")
                with y:
                    st.write(f"**Officer Phone:** {field(dep, 'officer_phone', 'phone')}")
                    st.write(f"**Officer Email:** {field(dep, 'officer_email', 'email')}")
                    st.write(f"**Office Location:** {field(dep, 'office_location', 'location')}")
                    st.write(f"**Working Hours:** {field(dep, 'working_hours', 'hours')}")
                st.write(f"**Department Work:** {field(dep, 'department_work', 'work')}")
                st.write(f"**Services:** {field(dep, 'services')}")


# ---------------- DASHBOARD ----------------
elif page == "📊 Department Dashboard":
    st.markdown('<div class="section-title">Department Dashboard</div>'
                '<div class="section-sub">Review assigned complaints and record department action.</div>',
                unsafe_allow_html=True)

    departments = get_departments()
    if not departments:
        st.warning("No departments available.")
    else:
        opts = {}
        for dep in departments:
            label = dname(dep)
            if did(dep) is not None:
                label += f" (ID: {did(dep)})"
            opts[label] = did(dep)

        selected = st.selectbox("Select Department", list(opts), key="dashboard_department")
        dep_id = opts[selected]
        r = api_get(f"/departments/{dep_id}/complaints", 25)

        if r is None:
            st.stop()
        if r.status_code != 200:
            error_detail(r, "Loading complaints failed")
        else:
            try:
                complaints = r.json()
                complaints = complaints if isinstance(complaints, list) else []
            except ValueError:
                complaints = []

            total = len(complaints)
            pending = sum(str(c.get("status", "")).lower() == "pending" for c in complaints)
            progress = sum(str(c.get("status", "")).lower() == "in progress" for c in complaints)
            resolved = sum(str(c.get("status", "")).lower() in ("resolved", "closed") for c in complaints)

            a, b, c, d = st.columns(4)
            for col, label, value, note in [
                (a, "Total Complaints", total, "Assigned records"),
                (b, "Pending", pending, "Awaiting action"),
                (c, "In Progress", progress, "Under review"),
                (d, "Resolved", resolved, "Completed records"),
            ]:
                with col:
                    st.markdown(
                        f'<div class="metric"><div class="metric-label">{label}</div>'
                        f'<div class="metric-value">{value}</div>'
                        f'<div class="metric-note">{note}</div></div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            if not complaints:
                st.success("No complaints are currently assigned to this department.")
            else:
                status_filter = st.selectbox(
                    "Filter by status",
                    ["All", "Pending", "In Progress", "Resolved", "Closed", "Rejected"],
                )
                visible = complaints if status_filter == "All" else [
                    c for c in complaints
                    if str(c.get("status", "")).lower() == status_filter.lower()
                ]

                for complaint in visible:
                    cid = complaint.get("id", "N/A")
                    number = complaint.get("complaint_number") or f"#{cid}"
                    status = complaint.get("status") or "Pending"
                    priority = complaint.get("priority") or "Normal"

                    with st.expander(f"{number}  •  {status}  •  {priority}"):
                        x, y = st.columns(2)
                        with x:
                            st.write(f"**Complaint ID:** {cid}")
                            st.write(f"**Complaint Number:** {complaint.get('complaint_number') or 'N/A'}")
                            st.write(f"**Citizen Name:** {complaint.get('citizen_name') or 'N/A'}")
                            st.write(f"**CNIC:** {complaint.get('cnic') or 'N/A'}")
                            st.write(f"**Phone:** {complaint.get('phone') or 'N/A'}")
                            st.write(f"**City:** {complaint.get('city') or 'N/A'}")
                        with y:
                            st.write(f"**Department:** {cdepartment(complaint)}")
                            st.write(f"**Category:** {ccategory(complaint)}")
                            st.write(f"**Priority:** {priority}")
                            st.write(f"**Status:** {status}")
                            st.write(f"**Created At:** {complaint.get('created_at') or 'N/A'}")
                            st.write(f"**Updated At:** {complaint.get('updated_at') or 'N/A'}")

                        st.write("**Address:**")
                        st.info(complaint.get("address") or "N/A")
                        st.write("**Complaint Details:**")
                        st.info(complaint.get("complaint_text") or complaint.get("complaint") or "N/A")

                        st.markdown("---")
                        st.markdown("### Department Action")
                        response_text = st.text_area(
                            "Department Response",
                            value=complaint.get("department_response") or "",
                            height=130,
                            key=f"response_{cid}",
                            placeholder="Write the department review, action taken, or response.",
                        )
                        statuses = ["Pending", "In Progress", "Resolved", "Closed", "Rejected"]
                        priorities = ["Low", "Normal", "High", "Urgent"]
                        new_status = st.selectbox(
                            "Update Status",
                            statuses,
                            index=statuses.index(status) if status in statuses else 0,
                            key=f"status_{cid}",
                        )
                        new_priority = st.selectbox(
                            "Update Priority",
                            priorities,
                            index=priorities.index(priority) if priority in priorities else 1,
                            key=f"priority_{cid}",
                        )

                        if st.button("Save Department Action", type="primary",
                                     key=f"update_{cid}", use_container_width=True):
                            payload = {
                                "department_response": response_text.strip(),
                                "status": new_status,
                                "priority": new_priority,
                            }
                            with st.spinner("Saving department action..."):
                                ur = api_patch(f"/complaints/{cid}", payload)
                            if ur is not None and ur.status_code == 200:
                                st.success("Complaint updated successfully.")
                                st.rerun()
                            elif ur is not None:
                                error_detail(ur, "Complaint update failed")


# ---------------- CHATBOT ----------------
elif page == "🤖 Complaint Chatbot":
    st.markdown('<div class="section-title">Complaint Chatbot</div>'
                '<div class="section-sub">Ask specific questions about complaint records.</div>',
                unsafe_allow_html=True)

    examples = [
        "How many complaints are registered?",
        "How many complaints are in Police?",
        "How many complaints are pending?",
        "Which department has the most complaints?",
        "Show the details of complaint ID 7.",
    ]

    st.markdown("**Example questions:**")
    cols = st.columns(len(examples))
    for col, example in zip(cols, examples):
        with col:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.chat_question = example

    question = st.text_area(
        "Your question",
        value=st.session_state.chat_question,
        placeholder="Ask a specific question about complaints...",
        height=110,
    )

    a, b = st.columns([1, 5])
    with a:
        ask = st.button("Ask Chatbot", type="primary", use_container_width=True)
    with b:
        clear = st.button("Clear Chat", use_container_width=True)

    if clear:
        st.session_state.chat_history = []
        st.session_state.chat_question = ""
        st.rerun()

    if ask:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Finding the answer..."):
                r = api_post("/chat", {"question": question.strip(), "history": st.session_state.chat_history[-6:]}, 40)
            if r is not None and r.status_code == 200:
                try:
                    answer = r.json().get("answer", "No answer returned.")
                except ValueError:
                    answer = r.text
                st.session_state.chat_history.append(
                    {"question": question.strip(), "answer": answer}
                )
                st.session_state.chat_question = ""
            elif r is not None:
                error_detail(r, "Chatbot request failed")

    for item in st.session_state.chat_history:
        st.markdown(
            f'<div class="chat-user"><b>You</b><br>{item["question"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="chat-bot"><b>🤖 Complaint Assistant</b><br>{item["answer"]}</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer">Pakistan Public Complaint System • Streamlit Frontend</div>',
    unsafe_allow_html=True,
)
