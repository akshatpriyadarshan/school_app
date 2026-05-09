import streamlit as st
from datetime import datetime, date
from database import (add_student, get_student_by_admission, update_student,
                      search_students, get_fee_for_class, get_fee_payments,
                      add_fee_payment, get_list_of_classes)
import io


# ─── helpers ─────────────────────────────────────────────────────────────────

def _photo_bytes(uploaded_file):
    """Return raw bytes from an UploadedFile, or None."""
    if uploaded_file is not None:
        return uploaded_file.read()
    return None


def _show_photo(photo_bytes, caption="Photo", width=140):
    if photo_bytes:
        st.image(io.BytesIO(photo_bytes), caption=caption, width=width)
    else:
        st.markdown(
            f"<div style='width:{width}px;height:{width}px;background:#f1f5f9;"
            "border-radius:8px;display:flex;align-items:center;justify-content:center;"
            "color:#94a3b8;font-size:13px;border:1px dashed #cbd5e1;'>No Photo</div>",
            unsafe_allow_html=True)


# ─── public entry point ──────────────────────────────────────────────────────

def render_students(user):
    role = user['role']
    can_edit = role in ('Admin', 'Manager', 'Teacher')

    tabs = st.tabs(["🔍 Search", "➕ Add Student", "✏️ Edit Student", "💰 Fees"])

    with tabs[0]:
        _student_search()
    with tabs[1]:
        _student_add() if can_edit else st.info("You don't have permission to add students.")
    with tabs[2]:
        _student_edit() if can_edit else st.info("You don't have permission to edit students.")
    with tabs[3]:
        _student_fees(user)


# ─── Search ──────────────────────────────────────────────────────────────────

def _student_search():
    st.subheader("Search Student")
    st.caption("Search by student name or enrolment number.")

    query = st.text_input("Name or Enrolment Number", key="s_search_query",
                          placeholder="e.g. Ravi Sharma  or  ENR-2024-001")

    if st.button("🔍 Search", key="btn_search_student"):
        if not query.strip():
            st.warning("Please enter a name or enrolment number to search.")
        else:
            results = search_students(query.strip())
            if results:
                st.session_state['s_search_results'] = results
            else:
                st.session_state.pop('s_search_results', None)
                st.error("No students found matching your search.")

    results = st.session_state.get('s_search_results', [])
    if results:
        st.success(f"{len(results)} student(s) found.")
        for s in results:
            with st.expander(
                f"**{s['first_name']} {s['last_name']}** — {s['enrolment_number']} | {s['class_name']}",
                expanded=len(results) == 1
            ):
                _display_student_card(s)


def _display_student_card(s):
    photo_col, info_col = st.columns([1, 3])
    with photo_col:
        _show_photo(s.get('photo'), caption=f"{s['first_name']} {s['last_name']}")
    with info_col:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Admission No:** {s['admission_number']}")
            st.markdown(f"**Enrolment No:** {s['enrolment_number']}")
            st.markdown(f"**Name:** {s['first_name']} {s['last_name']}")
            st.markdown(f"**Gender:** {s['gender']}")
            st.markdown(f"**Date of Birth:** {s['date_of_birth']}")
            st.markdown(f"**Blood Group:** {s.get('blood_group') or '-'}")
            st.markdown(f"**Email:** {s.get('email') or '-'}")
            st.markdown(f"**Phone:** {s['phone']}")
        with col2:
            st.markdown(f"**Class:** {s['class_name']}")
            st.markdown(f"**Section:** {s.get('section') or '-'}")
            st.markdown(f"**Roll Number:** {s['roll_number']}")
            st.markdown(f"**Father's Name:** {s['father_name']}")
            st.markdown(f"**Mother's Name:** {s.get('mother_name') or '-'}")
            st.markdown(f"**Guardian:** {s.get('guardian_name') or '-'}")
            st.markdown(f"**Guardian Phone:** {s['guardian_phone']}")
            st.markdown(f"**Address:** {s['address']}")
    if s.get('health_issues'):
        st.markdown(f"**Health Issues:** {s['health_issues']}")


# ─── Add ─────────────────────────────────────────────────────────────────────

def _student_add():
    st.subheader("Add New Student")

    # form_key increments on success to force a fresh form (all fields reset)
    form_key = st.session_state.get('add_student_form_key', 0)

    # Show persistent success banner between renders
    if st.session_state.get('add_student_success'):
        st.success(st.session_state.pop('add_student_success'))

    with st.form(f"add_student_form_{form_key}"):
        # Photo upload at top
        st.markdown("**Student Photo**")
        photo_file = st.file_uploader("Upload Photo (JPG/PNG, max 2 MB)",
                                      type=["jpg", "jpeg", "png"],
                                      key=f"add_s_photo_{form_key}")

        admission_number = st.text_input(
            "Admission Number (Auto-generated)",
            value=f"ADM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            disabled=True)

        enrolment_number = st.text_input("Enrolment Number *", key=f"add_s_enrol_{form_key}")

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", key=f"add_s_fn_{form_key}")
        with col2:
            last_name = st.text_input("Last Name *", key=f"add_s_ln_{form_key}")

        email = st.text_input("Email", key=f"add_s_email_{form_key}")

        col3, col4 = st.columns(2)
        with col3:
            date_of_birth = st.date_input("Date of Birth *", key=f"add_s_dob_{form_key}",
                                          min_value=date(1990, 1, 1), max_value=date.today())
        with col4:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"],
                                  key=f"add_s_gender_{form_key}")

        col5, col6 = st.columns(2)
        with col5:
            father_name = st.text_input("Father's Name *", key=f"add_s_father_{form_key}")
        with col6:
            mother_name = st.text_input("Mother's Name", key=f"add_s_mother_{form_key}")

        col7, col8 = st.columns(2)
        with col7:
            guardian_name = st.text_input("Guardian Name (if applicable)",
                                          key=f"add_s_guardian_{form_key}")
        with col8:
            guardian_phone = st.text_input("Guardian Phone *", key=f"add_s_gphone_{form_key}")

        address = st.text_area("Address *", key=f"add_s_address_{form_key}", height=100)

        col9, col10 = st.columns(2)
        with col9:
            phone = st.text_input("Phone Number *", key=f"add_s_phone_{form_key}")
        with col10:
            class_name = st.selectbox("Class *", get_list_of_classes(),
                                      key=f"add_s_class_{form_key}")

        col11, col12 = st.columns(2)
        with col11:
            section = st.text_input("Section", key=f"add_s_section_{form_key}")
        with col12:
            roll_number = st.text_input("Roll Number *", key=f"add_s_roll_{form_key}")

        col13, _ = st.columns(2)
        with col13:
            blood_group = st.selectbox("Blood Group",
                ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                key=f"add_s_blood_{form_key}")

        health_issues = st.text_area("Health Issues / Allergies",
                                     key=f"add_s_health_{form_key}", height=80)

        submitted = st.form_submit_button("➕ Add Student", width='content')

    if submitted:
        # Validate — errors keep the form as-is (no rerun)
        errors = []
        if not enrolment_number.strip():  errors.append("**Enrolment Number** is required.")
        if not first_name.strip():         errors.append("**First Name** is required.")
        if not last_name.strip():          errors.append("**Last Name** is required.")
        if not father_name.strip():        errors.append("**Father's Name** is required.")
        if not guardian_phone.strip():     errors.append("**Guardian Phone** is required.")
        if not address.strip():            errors.append("**Address** is required.")
        if not phone.strip():              errors.append("**Phone Number** is required.")
        if not roll_number.strip():        errors.append("**Roll Number** is required.")
        if photo_file and photo_file.size > 2 * 1024 * 1024:
            errors.append("**Photo** must be smaller than 2 MB.")

        if errors:
            st.error("Please fix the following errors before submitting:")
            for e in errors:
                st.markdown(f"- {e}")
        else:
            data = {
                'admission_number': admission_number,
                'enrolment_number': enrolment_number.strip(),
                'first_name': first_name.strip(),
                'last_name': last_name.strip(),
                'email': email.strip(),
                'date_of_birth': str(date_of_birth),
                'gender': gender,
                'father_name': father_name.strip(),
                'mother_name': mother_name.strip(),
                'guardian_name': guardian_name.strip(),
                'guardian_phone': guardian_phone.strip(),
                'address': address.strip(),
                'phone': phone.strip(),
                'class_name': class_name,
                'section': section.strip(),
                'roll_number': roll_number.strip(),
                'blood_group': blood_group,
                'health_issues': health_issues.strip(),
                'photo': _photo_bytes(photo_file),
            }
            ok, msg = add_student(data)
            if ok:
                # Bump key → fresh empty form; store success msg to show after rerun
                st.session_state['add_student_form_key'] = form_key + 1
                st.session_state['add_student_success'] = f"✅ {msg}"
                st.rerun()
            else:
                # DB error — show inline, keep form data (no rerun)
                st.error(f"❌ {msg}")


# ─── Edit ────────────────────────────────────────────────────────────────────

def _student_edit():
    st.subheader("Edit Student")
    st.caption("Search by student name or enrolment number, then select a record to edit.")

    query = st.text_input("Name or Enrolment Number", key="s_edit_search",
                          placeholder="e.g. Ravi  or  ENR-2024-001")

    if st.button("🔍 Find Student", key="btn_find_student_edit"):
        if not query.strip():
            st.warning("Please enter a name or enrolment number.")
        else:
            results = search_students(query.strip())
            if results:
                st.session_state['s_edit_results'] = results
                st.session_state.pop('edit_student', None)
            else:
                st.session_state.pop('s_edit_results', None)
                st.error("No students found.")

    results = st.session_state.get('s_edit_results', [])
    if results and 'edit_student' not in st.session_state:
        options = {
            f"{s['first_name']} {s['last_name']} — {s['enrolment_number']} ({s['class_name']})": s
            for s in results
        }
        chosen_label = st.selectbox("Select student to edit", list(options.keys()),
                                    key="s_edit_select")
        if st.button("Load Selected Student", key="btn_load_selected_student"):
            st.session_state['edit_student'] = options[chosen_label]
            st.rerun()

    if 'edit_student' in st.session_state:
        s = st.session_state['edit_student']

        if st.button("← Back to search results", key="btn_back_student_edit"):
            st.session_state.pop('edit_student', None)
            st.rerun()

        st.info(f"Editing: **{s['first_name']} {s['last_name']}** ({s['admission_number']})")

        if st.session_state.get('edit_student_success'):
            st.success(st.session_state.pop('edit_student_success'))

        with st.form("edit_student_form"):
            # Photo
            st.markdown("**Student Photo**")
            photo_col, _ = st.columns([1, 3])
            with photo_col:
                _show_photo(s.get('photo'), caption="Current Photo")
            photo_file = st.file_uploader("Replace Photo (leave blank to keep current)",
                                          type=["jpg", "jpeg", "png"], key="edit_s_photo")

            st.text_input("Admission Number (Read-only)", value=s['admission_number'], disabled=True)
            enrolment_number = st.text_input("Enrolment Number *",
                                             value=s['enrolment_number'], key="edit_s_enrol")

            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", value=s['first_name'], key="edit_s_fn")
            with col2:
                last_name = st.text_input("Last Name *", value=s['last_name'], key="edit_s_ln")

            email = st.text_input("Email", value=s.get('email', ''), key="edit_s_email")

            col3, col4 = st.columns(2)
            with col3:
                dob = date.fromisoformat(s['date_of_birth']) if s['date_of_birth'] else date.today()
                date_of_birth = st.date_input("Date of Birth *", value=dob, key="edit_s_dob")
            with col4:
                genders = ["Male", "Female", "Other"]
                gender = st.selectbox("Gender *", genders,
                    index=genders.index(s['gender']) if s['gender'] in genders else 0,
                    key="edit_s_gender")

            col5, col6 = st.columns(2)
            with col5:
                father_name = st.text_input("Father's Name *",
                                            value=s['father_name'], key="edit_s_father")
            with col6:
                mother_name = st.text_input("Mother's Name",
                                            value=s.get('mother_name', ''), key="edit_s_mother")

            col7, col8 = st.columns(2)
            with col7:
                guardian_name = st.text_input("Guardian Name",
                                              value=s.get('guardian_name', ''), key="edit_s_guardian")
            with col8:
                guardian_phone = st.text_input("Guardian Phone *",
                                               value=s['guardian_phone'], key="edit_s_gphone")

            address = st.text_area("Address *", value=s['address'],
                                   key="edit_s_address", height=100)

            col9, col10 = st.columns(2)
            with col9:
                phone = st.text_input("Phone Number *", value=s['phone'], key="edit_s_phone")
            with col10:
                classes = get_list_of_classes()
                class_name = st.selectbox("Class *", classes,
                    index=classes.index(s['class_name']) if s['class_name'] in classes else 0,
                    key="edit_s_class")

            col11, col12 = st.columns(2)
            with col11:
                section = st.text_input("Section", value=s.get('section', ''), key="edit_s_section")
            with col12:
                roll_number = st.text_input("Roll Number *",
                                            value=s['roll_number'], key="edit_s_roll")

            col13, _ = st.columns(2)
            with col13:
                bgroups = ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
                bg = s.get('blood_group', '') or ''
                blood_group = st.selectbox("Blood Group", bgroups,
                    index=bgroups.index(bg) if bg in bgroups else 0, key="edit_s_blood")

            health_issues = st.text_area("Health Issues / Allergies",
                value=s.get('health_issues', ''), key="edit_s_health", height=80)

            submitted = st.form_submit_button("💾 Save Changes", width='content')

        if submitted:
            errors = []
            if not enrolment_number.strip():  errors.append("**Enrolment Number** is required.")
            if not first_name.strip():         errors.append("**First Name** is required.")
            if not last_name.strip():          errors.append("**Last Name** is required.")
            if not father_name.strip():        errors.append("**Father's Name** is required.")
            if not guardian_phone.strip():     errors.append("**Guardian Phone** is required.")
            if not address.strip():            errors.append("**Address** is required.")
            if not phone.strip():              errors.append("**Phone Number** is required.")
            if not roll_number.strip():        errors.append("**Roll Number** is required.")
            if photo_file and photo_file.size > 2 * 1024 * 1024:
                errors.append("**Photo** must be smaller than 2 MB.")

            if errors:
                st.error("Please fix the following errors before saving:")
                for e in errors:
                    st.markdown(f"- {e}")
            else:
                new_photo = _photo_bytes(photo_file)   # None = keep existing
                data = {
                    'enrolment_number': enrolment_number.strip(),
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'email': email.strip(),
                    'date_of_birth': str(date_of_birth),
                    'gender': gender,
                    'father_name': father_name.strip(),
                    'mother_name': mother_name.strip(),
                    'guardian_name': guardian_name.strip(),
                    'guardian_phone': guardian_phone.strip(),
                    'address': address.strip(),
                    'phone': phone.strip(),
                    'class_name': class_name,
                    'section': section.strip(),
                    'roll_number': roll_number.strip(),
                    'blood_group': blood_group,
                    'health_issues': health_issues.strip(),
                    'photo': new_photo,
                }
                ok, msg = update_student(s['admission_number'], data)
                if ok:
                    st.session_state['edit_student_success'] = f"✅ {msg}"
                    # Refresh the loaded record so photo/fields reflect saved state
                    updated = get_student_by_admission(s['admission_number'])
                    st.session_state['edit_student'] = updated
                    st.session_state.pop('s_edit_results', None)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


# ─── Fees ────────────────────────────────────────────────────────────────────

def _student_fees(user):
    st.subheader("Student Fee Details")
    st.caption("Search by student name or enrolment number.")

    query = st.text_input("Name or Enrolment Number", key="s_fees_query",
                          placeholder="e.g. Ravi  or  ENR-2024-001")

    if st.button("🔍 Find Student", key="btn_find_student_fees"):
        if not query.strip():
            st.warning("Please enter a name or enrolment number.")
        else:
            results = search_students(query.strip())
            if results:
                st.session_state['s_fee_results'] = results
                st.session_state.pop('fee_student', None)
            else:
                st.session_state.pop('s_fee_results', None)
                st.error("No students found.")

    results = st.session_state.get('s_fee_results', [])
    if results and 'fee_student' not in st.session_state:
        options = {
            f"{s['first_name']} {s['last_name']} — {s['enrolment_number']} ({s['class_name']})": s
            for s in results
        }
        chosen = st.selectbox("Select student", list(options.keys()), key="s_fees_select")
        if st.button("Load Fee Details", key="btn_load_fee_details"):
            st.session_state['fee_student'] = options[chosen]
            st.rerun()

    if 'fee_student' in st.session_state:
        s = st.session_state['fee_student']

        if st.button("← Back to search", key="btn_back_fees"):
            st.session_state.pop('fee_student', None)
            st.rerun()

        monthly_fee = get_fee_for_class(s['class_name'])
        payments = get_fee_payments(s['admission_number'])

        st.markdown(f"### {s['first_name']} {s['last_name']} — {s['class_name']}")
        st.markdown(f"**Monthly Fee:** ₹{monthly_fee:,.2f}")

        today = date.today()
        academic_start = date(today.year if today.month >= 4 else today.year - 1, 4, 1)
        months_elapsed = (today.year - academic_start.year) * 12 + (today.month - academic_start.month) + 1
        total_due = monthly_fee * months_elapsed
        total_paid = sum(p['amount_paid'] for p in payments)
        pending = total_due - total_paid

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Due (This Year)", f"₹{total_due:,.2f}")
        col2.metric("Total Paid", f"₹{total_paid:,.2f}")
        col3.metric("Pending Amount", f"₹{pending:,.2f}",
                    delta=f"-₹{pending:,.2f}" if pending > 0 else "✓ Clear",
                    delta_color="inverse")

        if payments:
            st.markdown("#### Payment History")
            import pandas as pd
            df = pd.DataFrame(payments)[['month_year', 'payment_date', 'amount_paid', 'remarks']]
            df.columns = ['Month', 'Date', 'Amount (₹)', 'Remarks']
            st.dataframe(df, width='content', hide_index=True)
        else:
            st.info("No payment records found.")

        if user['role'] in ('Admin', 'Manager'):
            st.markdown("#### Record New Payment")
            with st.form("add_fee_payment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pay_date = st.date_input("Payment Date", value=date.today(), key="fee_pay_date")
                    amount = st.number_input("Amount Paid (₹)", min_value=0.0,
                                             value=float(monthly_fee), key="fee_amount")
                with col2:
                    month_year = st.text_input("For Month (e.g. April 2025)", key="fee_month_year")
                    remarks = st.text_input("Remarks", key="fee_remarks")
                if st.form_submit_button("✅ Record Payment", width='content'):
                    if not month_year.strip():
                        st.error("**For Month** is required — e.g. 'April 2025'.")
                    else:
                        add_fee_payment(s['admission_number'], str(pay_date),
                                        amount, month_year.strip(), remarks.strip())
                        st.success("Payment recorded successfully.")
                        st.rerun()
