import streamlit as st
from datetime import datetime, date
from database import (add_teacher, get_teacher_by_id, update_teacher,
                      get_salary_payments, add_salary_payment)


def render_teachers(user):
    role = user['role']
    can_edit = role in ('Admin', 'Manager')

    tabs = st.tabs(["🔍 Search", "➕ Add Teacher", "✏️ Edit Teacher", "💵 Salary"])

    with tabs[0]:
        _teacher_search()

    with tabs[1]:
        if can_edit:
            _teacher_add()
        else:
            st.info("You don't have permission to add teachers.")

    with tabs[2]:
        if can_edit:
            _teacher_edit()
        else:
            st.info("You don't have permission to edit teachers.")

    with tabs[3]:
        _teacher_salary(user)


def _teacher_search():
    st.subheader("Search Teacher")
    emp_id = st.text_input("Enter Employee ID", key="search_emp_input")
    if st.button("Search", key="btn_search_teacher"):
        if not emp_id.strip():
            st.warning("Please enter an Employee ID.")
        else:
            teacher = get_teacher_by_id(emp_id.strip())
            if teacher:
                _display_teacher_card(teacher)
            else:
                st.error("No teacher found with that Employee ID.")


def _display_teacher_card(t):
    st.success("Teacher Found!")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Employee ID:** {t['employee_id']}")
        st.markdown(f"**Name:** {t['first_name']} {t['last_name']}")
        st.markdown(f"**Gender:** {t['gender']}")
        st.markdown(f"**Date of Birth:** {t['date_of_birth']}")
        st.markdown(f"**Email:** {t['email']}")
        st.markdown(f"**Phone:** {t['phone']}")
        st.markdown(f"**Qualification:** {t['qualification']}")
    with col2:
        st.markdown(f"**Joining Date:** {t['joining_date']}")
        st.markdown(f"**Salary:** ₹{t['salary_amount']:,.2f} ({t['salary_frequency']})")
        st.markdown(f"**Bank Account:** {t['bank_account']}")
        st.markdown(f"**IFSC Code:** {t['ifsc_code']}")
        st.markdown(f"**Class Assigned:** {t.get('class_assigned', '-')}")
        st.markdown(f"**Status:** {t['status']}")


def _teacher_add():
    st.subheader("Add New Teacher")
    with st.form("add_teacher_form"):
        employee_id = st.text_input(
            "Employee ID (Auto-generated)",
            value=f"EMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            disabled=True
        )
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", key="add_t_first")
        with col2:
            last_name = st.text_input("Last Name *", key="add_t_last")
        col3, col4 = st.columns(2)
        with col3:
            email = st.text_input("Email *", key="add_t_email")
        with col4:
            phone = st.text_input("Phone Number *", key="add_t_phone")
        col5, col6 = st.columns(2)
        with col5:
            date_of_birth = st.date_input("Date of Birth *", key="add_t_dob",
                                          min_value=date(1950, 1, 1), max_value=date.today())
        with col6:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"], key="add_t_gender")
        col7, col8 = st.columns(2)
        with col7:
            qualification = st.text_input("Qualification *", key="add_t_qual")
        with col8:
            joining_date = st.date_input("Joining Date *", key="add_t_join",
                                         min_value=date(2000, 1, 1), max_value=date.today())
        col9, col10 = st.columns(2)
        with col9:
            salary_amount = st.number_input("Salary Amount *", min_value=0.0, key="add_t_salary")
        with col10:
            salary_frequency = st.selectbox("Salary Frequency", ["Monthly", "Yearly"], key="add_t_freq")
        col11, col12 = st.columns(2)
        with col11:
            bank_account = st.text_input("Bank Account Number *", key="add_t_bank")
        with col12:
            ifsc_code = st.text_input("IFSC Code *", key="add_t_ifsc")
        col13, col14 = st.columns(2)
        with col13:
            class_assigned = st.text_input("Class Assigned", key="add_t_class")
        with col14:
            status = st.selectbox("Status *", ["Active", "Inactive", "On Leave"], key="add_t_status")

        submitted = st.form_submit_button("➕ Add Teacher", use_container_width=True)
        if submitted:
            errors = []
            if not first_name.strip(): errors.append("First Name")
            if not last_name.strip(): errors.append("Last Name")
            if not email.strip(): errors.append("Email")
            if not phone.strip(): errors.append("Phone")
            if not qualification.strip(): errors.append("Qualification")
            if salary_amount <= 0: errors.append("Salary Amount")
            if not bank_account.strip(): errors.append("Bank Account")
            if not ifsc_code.strip(): errors.append("IFSC Code")

            if errors:
                st.error(f"Required fields missing: {', '.join(errors)}")
            else:
                data = {
                    'employee_id': employee_id,
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'email': email.strip(),
                    'phone': phone.strip(),
                    'date_of_birth': str(date_of_birth),
                    'gender': gender,
                    'qualification': qualification.strip(),
                    'joining_date': str(joining_date),
                    'salary_amount': salary_amount,
                    'salary_frequency': salary_frequency,
                    'bank_account': bank_account.strip(),
                    'ifsc_code': ifsc_code.strip(),
                    'class_assigned': class_assigned.strip(),
                    'status': status
                }
                ok, msg = add_teacher(data)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def _teacher_edit():
    st.subheader("Edit Teacher")
    emp_id = st.text_input("Enter Employee ID to Edit", key="edit_emp_input")
    if st.button("Load Teacher", key="btn_load_teacher"):
        teacher = get_teacher_by_id(emp_id.strip())
        if teacher:
            st.session_state['edit_teacher'] = teacher
        else:
            st.error("Teacher not found.")
            st.session_state.pop('edit_teacher', None)

    if 'edit_teacher' in st.session_state:
        t = st.session_state['edit_teacher']
        st.info(f"Editing: **{t['first_name']} {t['last_name']}** ({t['employee_id']})")

        with st.form("edit_teacher_form"):
            st.text_input("Employee ID (Read-only)", value=t['employee_id'], disabled=True)
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", value=t['first_name'], key="edit_t_first")
            with col2:
                last_name = st.text_input("Last Name *", value=t['last_name'], key="edit_t_last")
            col3, col4 = st.columns(2)
            with col3:
                email = st.text_input("Email *", value=t['email'], key="edit_t_email")
            with col4:
                phone = st.text_input("Phone Number *", value=t['phone'], key="edit_t_phone")
            col5, col6 = st.columns(2)
            with col5:
                dob = date.fromisoformat(t['date_of_birth'])
                date_of_birth = st.date_input("Date of Birth *", value=dob, key="edit_t_dob")
            with col6:
                genders = ["Male", "Female", "Other"]
                gender = st.selectbox("Gender *", genders,
                    index=genders.index(t['gender']) if t['gender'] in genders else 0,
                    key="edit_t_gender")
            col7, col8 = st.columns(2)
            with col7:
                qualification = st.text_input("Qualification *", value=t['qualification'], key="edit_t_qual")
            with col8:
                jd = date.fromisoformat(t['joining_date'])
                joining_date = st.date_input("Joining Date *", value=jd, key="edit_t_join")
            col9, col10 = st.columns(2)
            with col9:
                salary_amount = st.number_input("Salary Amount *", min_value=0.0,
                    value=float(t['salary_amount']), key="edit_t_salary")
            with col10:
                freqs = ["Monthly", "Yearly"]
                salary_frequency = st.selectbox("Salary Frequency", freqs,
                    index=freqs.index(t['salary_frequency']) if t['salary_frequency'] in freqs else 0,
                    key="edit_t_freq")
            col11, col12 = st.columns(2)
            with col11:
                bank_account = st.text_input("Bank Account Number *", value=t['bank_account'], key="edit_t_bank")
            with col12:
                ifsc_code = st.text_input("IFSC Code *", value=t['ifsc_code'], key="edit_t_ifsc")
            col13, col14 = st.columns(2)
            with col13:
                class_assigned = st.text_input("Class Assigned", value=t.get('class_assigned', ''), key="edit_t_class")
            with col14:
                statuses = ["Active", "Inactive", "On Leave"]
                status = st.selectbox("Status *", statuses,
                    index=statuses.index(t['status']) if t['status'] in statuses else 0,
                    key="edit_t_status")

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
            if submitted:
                errors = []
                if not first_name.strip(): errors.append("First Name")
                if not last_name.strip(): errors.append("Last Name")
                if not email.strip(): errors.append("Email")
                if not phone.strip(): errors.append("Phone")
                if not qualification.strip(): errors.append("Qualification")
                if salary_amount <= 0: errors.append("Salary Amount")
                if not bank_account.strip(): errors.append("Bank Account")
                if not ifsc_code.strip(): errors.append("IFSC Code")

                if errors:
                    st.error(f"Required fields missing: {', '.join(errors)}")
                else:
                    data = {
                        'first_name': first_name.strip(),
                        'last_name': last_name.strip(),
                        'email': email.strip(),
                        'phone': phone.strip(),
                        'date_of_birth': str(date_of_birth),
                        'gender': gender,
                        'qualification': qualification.strip(),
                        'joining_date': str(joining_date),
                        'salary_amount': salary_amount,
                        'salary_frequency': salary_frequency,
                        'bank_account': bank_account.strip(),
                        'ifsc_code': ifsc_code.strip(),
                        'class_assigned': class_assigned.strip(),
                        'status': status
                    }
                    ok, msg = update_teacher(t['employee_id'], data)
                    if ok:
                        st.success(msg)
                        st.session_state.pop('edit_teacher', None)
                        st.rerun()
                    else:
                        st.error(msg)


def _teacher_salary(user):
    st.subheader("Teacher Salary Details")
    emp_id = st.text_input("Enter Employee ID", key="salary_emp_input")
    if st.button("Load Salary Details", key="btn_load_salary"):
        teacher = get_teacher_by_id(emp_id.strip())
        if teacher:
            st.session_state['salary_teacher'] = teacher
        else:
            st.error("Teacher not found.")
            st.session_state.pop('salary_teacher', None)

    if 'salary_teacher' in st.session_state:
        t = st.session_state['salary_teacher']
        payments = get_salary_payments(t['employee_id'])

        st.markdown(f"### {t['first_name']} {t['last_name']} — {t['employee_id']}")

        monthly_salary = (t['salary_amount'] if t['salary_frequency'] == 'Monthly'
                          else t['salary_amount'] / 12)
        st.markdown(f"**Monthly Salary:** ₹{monthly_salary:,.2f}")
        st.markdown(f"**Frequency:** {t['salary_frequency']} | ₹{t['salary_amount']:,.2f}")

        # Calculate months since joining
        today = date.today()
        join_date = date.fromisoformat(t['joining_date'])
        months_employed = max(1, (today.year - join_date.year) * 12 + (today.month - join_date.month) + 1)
        total_due = monthly_salary * months_employed
        total_paid = sum(p['amount_paid'] for p in payments)
        pending = total_due - total_paid

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Due (Since Joining)", f"₹{total_due:,.2f}")
        col2.metric("Total Paid", f"₹{total_paid:,.2f}")
        col3.metric("Pending", f"₹{pending:,.2f}",
                    delta=f"-₹{pending:,.2f}" if pending > 0 else "✓ Clear",
                    delta_color="inverse")

        if payments:
            st.markdown("#### Payment History")
            import pandas as pd
            df = pd.DataFrame(payments)[['month_year', 'payment_date', 'amount_paid', 'remarks']]
            df.columns = ['Month', 'Date', 'Amount (₹)', 'Remarks']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No salary payment records found.")

        # Record payment (Admin/Manager only)
        if user['role'] in ('Admin', 'Manager'):
            st.markdown("#### Record Salary Payment")
            with st.form("add_salary_payment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pay_date = st.date_input("Payment Date", value=date.today(), key="sal_pay_date")
                    amount = st.number_input("Amount Paid (₹)", min_value=0.0,
                                             value=float(monthly_salary), key="sal_amount")
                with col2:
                    month_year = st.text_input("For Month (e.g. April 2025)", key="sal_month_year")
                    remarks = st.text_input("Remarks", key="sal_remarks")
                if st.form_submit_button("✅ Record Payment", use_container_width=True):
                    if not month_year.strip():
                        st.error("Please enter the month/year.")
                    else:
                        add_salary_payment(t['employee_id'], str(pay_date), amount,
                                           month_year.strip(), remarks.strip())
                        st.success("Salary payment recorded.")
                        st.rerun()
