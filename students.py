import streamlit as st
from datetime import datetime, date
from database import (add_student, get_student_by_admission, update_student,
                      get_fee_structure, get_fee_for_class, get_fee_payments,
                      add_fee_payment, get_list_of_classes)
from dateutil.relativedelta import relativedelta


def render_students(user):
    role = user['role']
    can_edit = role in ('Admin', 'Manager', 'Teacher')

    tabs = st.tabs(["🔍 Search", "➕ Add Student", "✏️ Edit Student", "💰 Fees"])

    with tabs[0]:
        _student_search()

    with tabs[1]:
        if can_edit:
            _student_add()
        else:
            st.info("You don't have permission to add students.")

    with tabs[2]:
        if can_edit:
            _student_edit()
        else:
            st.info("You don't have permission to edit students.")

    with tabs[3]:
        _student_fees(user)


def _student_search():
    st.subheader("Search Student")
    adm = st.text_input("Enter Admission Number", key="search_adm_input")
    if st.button("Search", key="btn_search_student"):
        if not adm.strip():
            st.warning("Please enter an Admission Number.")
        else:
            student = get_student_by_admission(adm.strip())
            if student:
                _display_student_card(student)
            else:
                st.error("No student found with that Admission Number.")


def _display_student_card(s):
    st.success("Student Found!")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Admission No:** {s['admission_number']}")
        st.markdown(f"**Enrolment No:** {s['enrolment_number']}")
        st.markdown(f"**Name:** {s['first_name']} {s['last_name']}")
        st.markdown(f"**Gender:** {s['gender']}")
        st.markdown(f"**Date of Birth:** {s['date_of_birth']}")
        st.markdown(f"**Blood Group:** {s.get('blood_group', '-')}")
        st.markdown(f"**Email:** {s.get('email', '-')}")
        st.markdown(f"**Phone:** {s['phone']}")
    with col2:
        st.markdown(f"**Class:** {s['class_name']}")
        st.markdown(f"**Section:** {s.get('section', '-')}")
        st.markdown(f"**Roll Number:** {s['roll_number']}")
        st.markdown(f"**Father's Name:** {s['father_name']}")
        st.markdown(f"**Mother's Name:** {s.get('mother_name', '-')}")
        st.markdown(f"**Guardian:** {s.get('guardian_name', '-')}")
        st.markdown(f"**Guardian Phone:** {s['guardian_phone']}")
        st.markdown(f"**Address:** {s['address']}")
    if s.get('health_issues'):
        st.markdown(f"**Health Issues:** {s['health_issues']}")


def _student_add():
    st.subheader("Add New Student")
    with st.form("add_student_form"):
        admission_number = st.text_input(
            "Admission Number (Auto-generated)",
            value=f"ADM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            disabled=True
        )
        enrolment_number = st.text_input("Enrolment Number *", key="add_enrolment")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", key="add_first")
        with col2:
            last_name = st.text_input("Last Name *", key="add_last")
        email = st.text_input("Email", key="add_email")
        col3, col4 = st.columns(2)
        with col3:
            date_of_birth = st.date_input("Date of Birth *", key="add_dob",
                                          min_value=date(1990, 1, 1), max_value=date.today())
        with col4:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"], key="add_gender")
        col5, col6 = st.columns(2)
        with col5:
            father_name = st.text_input("Father's Name *", key="add_father")
        with col6:
            mother_name = st.text_input("Mother's Name", key="add_mother")
        col7, col8 = st.columns(2)
        with col7:
            guardian_name = st.text_input("Guardian Name (if applicable)", key="add_guardian")
        with col8:
            guardian_phone = st.text_input("Guardian Phone *", key="add_guardian_phone")
        address = st.text_area("Address *", key="add_address", height=100)
        col9, col10 = st.columns(2)
        with col9:
            phone = st.text_input("Phone Number *", key="add_phone")
        with col10:
            class_name = st.selectbox("Class *", get_list_of_classes(), key="add_class")
        col11, col12 = st.columns(2)
        with col11:
            section = st.text_input("Section", key="add_section")
        with col12:
            roll_number = st.text_input("Roll Number *", key="add_roll")
        col13, col14 = st.columns(2)
        with col13:
            blood_group = st.selectbox("Blood Group",
                ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], key="add_blood")
        health_issues = st.text_area("Health Issues / Allergies", key="add_health", height=80)

        submitted = st.form_submit_button("➕ Add Student", use_container_width=True)
        if submitted:
            errors = []
            if not enrolment_number.strip(): errors.append("Enrolment Number")
            if not first_name.strip(): errors.append("First Name")
            if not last_name.strip(): errors.append("Last Name")
            if not father_name.strip(): errors.append("Father's Name")
            if not guardian_phone.strip(): errors.append("Guardian Phone")
            if not address.strip(): errors.append("Address")
            if not phone.strip(): errors.append("Phone Number")
            if not roll_number.strip(): errors.append("Roll Number")

            if errors:
                st.error(f"Required fields missing: {', '.join(errors)}")
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
                    'health_issues': health_issues.strip()
                }
                ok, msg = add_student(data)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def _student_edit():
    st.subheader("Edit Student")
    adm = st.text_input("Enter Admission Number to Edit", key="edit_adm_input")
    if st.button("Load Student", key="btn_load_student"):
        student = get_student_by_admission(adm.strip())
        if student:
            st.session_state['edit_student'] = student
        else:
            st.error("Student not found.")
            st.session_state.pop('edit_student', None)

    if 'edit_student' in st.session_state:
        s = st.session_state['edit_student']
        st.info(f"Editing: **{s['first_name']} {s['last_name']}** ({s['admission_number']})")

        with st.form("edit_student_form"):
            st.text_input("Admission Number (Read-only)", value=s['admission_number'], disabled=True)
            enrolment_number = st.text_input("Enrolment Number *", value=s['enrolment_number'], key="edit_enrolment")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", value=s['first_name'], key="edit_first")
            with col2:
                last_name = st.text_input("Last Name *", value=s['last_name'], key="edit_last")
            email = st.text_input("Email", value=s.get('email', ''), key="edit_email")
            col3, col4 = st.columns(2)
            with col3:
                dob = date.fromisoformat(s['date_of_birth']) if s['date_of_birth'] else date.today()
                date_of_birth = st.date_input("Date of Birth *", value=dob, key="edit_dob")
            with col4:
                genders = ["Male", "Female", "Other"]
                gender = st.selectbox("Gender *", genders,
                    index=genders.index(s['gender']) if s['gender'] in genders else 0, key="edit_gender")
            col5, col6 = st.columns(2)
            with col5:
                father_name = st.text_input("Father's Name *", value=s['father_name'], key="edit_father")
            with col6:
                mother_name = st.text_input("Mother's Name", value=s.get('mother_name', ''), key="edit_mother")
            col7, col8 = st.columns(2)
            with col7:
                guardian_name = st.text_input("Guardian Name", value=s.get('guardian_name', ''), key="edit_guardian")
            with col8:
                guardian_phone = st.text_input("Guardian Phone *", value=s['guardian_phone'], key="edit_gphone")
            address = st.text_area("Address *", value=s['address'], key="edit_address", height=100)
            col9, col10 = st.columns(2)
            with col9:
                phone = st.text_input("Phone Number *", value=s['phone'], key="edit_phone")
            with col10:
                classes = get_list_of_classes()
                class_name = st.selectbox("Class *", classes,
                    index=classes.index(s['class_name']) if s['class_name'] in classes else 0,
                    key="edit_class")
            col11, col12 = st.columns(2)
            with col11:
                section = st.text_input("Section", value=s.get('section', ''), key="edit_section")
            with col12:
                roll_number = st.text_input("Roll Number *", value=s['roll_number'], key="edit_roll")
            col13, _ = st.columns(2)
            with col13:
                bgroups = ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
                bg = s.get('blood_group', '')
                blood_group = st.selectbox("Blood Group", bgroups,
                    index=bgroups.index(bg) if bg in bgroups else 0, key="edit_blood")
            health_issues = st.text_area("Health Issues / Allergies",
                value=s.get('health_issues', ''), key="edit_health", height=80)

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
            if submitted:
                errors = []
                if not enrolment_number.strip(): errors.append("Enrolment Number")
                if not first_name.strip(): errors.append("First Name")
                if not last_name.strip(): errors.append("Last Name")
                if not father_name.strip(): errors.append("Father's Name")
                if not guardian_phone.strip(): errors.append("Guardian Phone")
                if not address.strip(): errors.append("Address")
                if not phone.strip(): errors.append("Phone Number")
                if not roll_number.strip(): errors.append("Roll Number")

                if errors:
                    st.error(f"Required fields missing: {', '.join(errors)}")
                else:
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
                        'health_issues': health_issues.strip()
                    }
                    ok, msg = update_student(s['admission_number'], data)
                    if ok:
                        st.success(msg)
                        st.session_state.pop('edit_student', None)
                        st.rerun()
                    else:
                        st.error(msg)


def _student_fees(user):
    st.subheader("Student Fee Details")
    adm = st.text_input("Enter Admission Number", key="fees_adm_input")
    if st.button("Load Fee Details", key="btn_load_fees"):
        student = get_student_by_admission(adm.strip())
        if student:
            st.session_state['fee_student'] = student
        else:
            st.error("Student not found.")
            st.session_state.pop('fee_student', None)

    if 'fee_student' in st.session_state:
        s = st.session_state['fee_student']
        monthly_fee = get_fee_for_class(s['class_name'])
        payments = get_fee_payments(s['admission_number'])

        st.markdown(f"### {s['first_name']} {s['last_name']} — {s['class_name']}")
        st.markdown(f"**Monthly Fee:** ₹{monthly_fee:,.2f}")

        # Calculate months from joining (use current date)
        today = date.today()
        # We'll use the DB joining date as academic year start (April of current year or previous)
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
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No payment records found.")

        # Add payment (Admin/Manager only)
        if user['role'] in ('Admin', 'Manager'):
            st.markdown("#### Record New Payment")
            with st.form("add_fee_payment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pay_date = st.date_input("Payment Date", value=date.today(), key="fee_pay_date")
                    amount = st.number_input("Amount Paid (₹)", min_value=0.0, value=float(monthly_fee), key="fee_amount")
                with col2:
                    month_year = st.text_input("For Month (e.g. April 2025)", key="fee_month_year")
                    remarks = st.text_input("Remarks", key="fee_remarks")
                if st.form_submit_button("✅ Record Payment", use_container_width=True):
                    if not month_year.strip():
                        st.error("Please enter the month/year for this payment.")
                    else:
                        add_fee_payment(s['admission_number'], str(pay_date), amount,
                                        month_year.strip(), remarks.strip())
                        st.success("Payment recorded successfully.")
                        st.rerun()
