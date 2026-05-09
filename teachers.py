import streamlit as st
from datetime import datetime, date
from database import (add_teacher, get_teacher_by_id, update_teacher,
                      search_teachers, get_salary_payments, add_salary_payment)
import io


# ─── helpers ─────────────────────────────────────────────────────────────────

def _photo_bytes(uploaded_file):
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

def render_teachers(user):
    role = user['role']
    can_edit = role in ('Admin', 'Manager')

    tabs = st.tabs(["🔍 Search", "➕ Add Teacher", "✏️ Edit Teacher", "💵 Salary"])

    with tabs[0]:
        _teacher_search()
    with tabs[1]:
        _teacher_add() if can_edit else st.info("You don't have permission to add teachers.")
    with tabs[2]:
        _teacher_edit() if can_edit else st.info("You don't have permission to edit teachers.")
    with tabs[3]:
        _teacher_salary(user)


# ─── Search ──────────────────────────────────────────────────────────────────

def _teacher_search():
    st.subheader("Search Teacher")
    st.caption("Search by teacher name or Employee ID.")

    query = st.text_input("Name or Employee ID", key="t_search_query",
                          placeholder="e.g. Sunita Rao  or  EMP-20240901120000")

    if st.button("🔍 Search", key="btn_search_teacher"):
        if not query.strip():
            st.warning("Please enter a name or Employee ID.")
        else:
            results = search_teachers(query.strip())
            if results:
                st.session_state['t_search_results'] = results
            else:
                st.session_state.pop('t_search_results', None)
                st.error("No teachers found matching your search.")

    results = st.session_state.get('t_search_results', [])
    if results:
        st.success(f"{len(results)} teacher(s) found.")
        for t in results:
            with st.expander(
                f"**{t['first_name']} {t['last_name']}** — {t['employee_id']} | {t['status']}",
                expanded=len(results) == 1
            ):
                _display_teacher_card(t)


def _display_teacher_card(t):
    photo_col, info_col = st.columns([1, 3])
    with photo_col:
        _show_photo(t.get('photo'), caption=f"{t['first_name']} {t['last_name']}")
    with info_col:
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
            st.markdown(f"**Class Assigned:** {t.get('class_assigned') or '-'}")
            st.markdown(f"**Status:** {t['status']}")


# ─── Add ─────────────────────────────────────────────────────────────────────

def _teacher_add():
    st.subheader("Add New Teacher")

    form_key = st.session_state.get('add_teacher_form_key', 0)

    if st.session_state.get('add_teacher_success'):
        st.success(st.session_state.pop('add_teacher_success'))

    with st.form(f"add_teacher_form_{form_key}"):
        st.markdown("**Teacher Photo**")
        photo_file = st.file_uploader("Upload Photo (JPG/PNG, max 2 MB)",
                                      type=["jpg", "jpeg", "png"],
                                      key=f"add_t_photo_{form_key}")

        employee_id = st.text_input(
            "Employee ID (Auto-generated)",
            value=f"EMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            disabled=True)

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", key=f"add_t_fn_{form_key}")
        with col2:
            last_name = st.text_input("Last Name *", key=f"add_t_ln_{form_key}")

        col3, col4 = st.columns(2)
        with col3:
            email = st.text_input("Email *", key=f"add_t_email_{form_key}")
        with col4:
            phone = st.text_input("Phone Number *", key=f"add_t_phone_{form_key}")

        col5, col6 = st.columns(2)
        with col5:
            date_of_birth = st.date_input("Date of Birth *", key=f"add_t_dob_{form_key}",
                                          min_value=date(1950, 1, 1), max_value=date.today())
        with col6:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"],
                                  key=f"add_t_gender_{form_key}")

        col7, col8 = st.columns(2)
        with col7:
            qualification = st.text_input("Qualification *", key=f"add_t_qual_{form_key}")
        with col8:
            joining_date = st.date_input("Joining Date *", key=f"add_t_join_{form_key}",
                                         min_value=date(2000, 1, 1), max_value=date.today())

        col9, col10 = st.columns(2)
        with col9:
            salary_amount = st.number_input("Salary Amount *", min_value=0.0,
                                            key=f"add_t_salary_{form_key}")
        with col10:
            salary_frequency = st.selectbox("Salary Frequency", ["Monthly", "Yearly"],
                                            key=f"add_t_freq_{form_key}")

        col11, col12 = st.columns(2)
        with col11:
            bank_account = st.text_input("Bank Account Number *", key=f"add_t_bank_{form_key}")
        with col12:
            ifsc_code = st.text_input("IFSC Code *", key=f"add_t_ifsc_{form_key}")

        col13, col14 = st.columns(2)
        with col13:
            class_assigned = st.text_input("Class Assigned", key=f"add_t_class_{form_key}")
        with col14:
            status = st.selectbox("Status *", ["Active", "Inactive", "On Leave"],
                                  key=f"add_t_status_{form_key}")

        submitted = st.form_submit_button("➕ Add Teacher", use_container_width=True)

    if submitted:
        errors = []
        if not first_name.strip():      errors.append("**First Name** is required.")
        if not last_name.strip():       errors.append("**Last Name** is required.")
        if not email.strip():           errors.append("**Email** is required.")
        if not phone.strip():           errors.append("**Phone Number** is required.")
        if not qualification.strip():   errors.append("**Qualification** is required.")
        if salary_amount <= 0:          errors.append("**Salary Amount** must be greater than 0.")
        if not bank_account.strip():    errors.append("**Bank Account Number** is required.")
        if not ifsc_code.strip():       errors.append("**IFSC Code** is required.")
        if photo_file and photo_file.size > 2 * 1024 * 1024:
            errors.append("**Photo** must be smaller than 2 MB.")

        if errors:
            st.error("Please fix the following errors before submitting:")
            for e in errors:
                st.markdown(f"- {e}")
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
                'status': status,
                'photo': _photo_bytes(photo_file),
            }
            ok, msg = add_teacher(data)
            if ok:
                st.session_state['add_teacher_form_key'] = form_key + 1
                st.session_state['add_teacher_success'] = f"✅ {msg}"
                st.rerun()
            else:
                st.error(f"❌ {msg}")


# ─── Edit ────────────────────────────────────────────────────────────────────

def _teacher_edit():
    st.subheader("Edit Teacher")
    st.caption("Search by teacher name or Employee ID, then select a record to edit.")

    query = st.text_input("Name or Employee ID", key="t_edit_search",
                          placeholder="e.g. Sunita  or  EMP-20240901120000")

    if st.button("🔍 Find Teacher", key="btn_find_teacher_edit"):
        if not query.strip():
            st.warning("Please enter a name or Employee ID.")
        else:
            results = search_teachers(query.strip())
            if results:
                st.session_state['t_edit_results'] = results
                st.session_state.pop('edit_teacher', None)
            else:
                st.session_state.pop('t_edit_results', None)
                st.error("No teachers found.")

    results = st.session_state.get('t_edit_results', [])
    if results and 'edit_teacher' not in st.session_state:
        options = {
            f"{t['first_name']} {t['last_name']} — {t['employee_id']} ({t['status']})": t
            for t in results
        }
        chosen_label = st.selectbox("Select teacher to edit", list(options.keys()),
                                    key="t_edit_select")
        if st.button("Load Selected Teacher", key="btn_load_selected_teacher"):
            st.session_state['edit_teacher'] = options[chosen_label]
            st.rerun()

    if 'edit_teacher' in st.session_state:
        t = st.session_state['edit_teacher']

        if st.button("← Back to search results", key="btn_back_teacher_edit"):
            st.session_state.pop('edit_teacher', None)
            st.rerun()

        st.info(f"Editing: **{t['first_name']} {t['last_name']}** ({t['employee_id']})")

        if st.session_state.get('edit_teacher_success'):
            st.success(st.session_state.pop('edit_teacher_success'))

        with st.form("edit_teacher_form"):
            st.markdown("**Teacher Photo**")
            photo_col, _ = st.columns([1, 3])
            with photo_col:
                _show_photo(t.get('photo'), caption="Current Photo")
            photo_file = st.file_uploader("Replace Photo (leave blank to keep current)",
                                          type=["jpg", "jpeg", "png"], key="edit_t_photo")

            st.text_input("Employee ID (Read-only)", value=t['employee_id'], disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", value=t['first_name'], key="edit_t_fn")
            with col2:
                last_name = st.text_input("Last Name *", value=t['last_name'], key="edit_t_ln")

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
                qualification = st.text_input("Qualification *",
                                              value=t['qualification'], key="edit_t_qual")
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
                bank_account = st.text_input("Bank Account Number *",
                                             value=t['bank_account'], key="edit_t_bank")
            with col12:
                ifsc_code = st.text_input("IFSC Code *", value=t['ifsc_code'], key="edit_t_ifsc")

            col13, col14 = st.columns(2)
            with col13:
                class_assigned = st.text_input("Class Assigned",
                    value=t.get('class_assigned', ''), key="edit_t_class")
            with col14:
                statuses = ["Active", "Inactive", "On Leave"]
                status = st.selectbox("Status *", statuses,
                    index=statuses.index(t['status']) if t['status'] in statuses else 0,
                    key="edit_t_status")

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if submitted:
            errors = []
            if not first_name.strip():      errors.append("**First Name** is required.")
            if not last_name.strip():       errors.append("**Last Name** is required.")
            if not email.strip():           errors.append("**Email** is required.")
            if not phone.strip():           errors.append("**Phone Number** is required.")
            if not qualification.strip():   errors.append("**Qualification** is required.")
            if salary_amount <= 0:          errors.append("**Salary Amount** must be greater than 0.")
            if not bank_account.strip():    errors.append("**Bank Account Number** is required.")
            if not ifsc_code.strip():       errors.append("**IFSC Code** is required.")
            if photo_file and photo_file.size > 2 * 1024 * 1024:
                errors.append("**Photo** must be smaller than 2 MB.")

            if errors:
                st.error("Please fix the following errors before saving:")
                for e in errors:
                    st.markdown(f"- {e}")
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
                    'status': status,
                    'photo': _photo_bytes(photo_file),
                }
                ok, msg = update_teacher(t['employee_id'], data)
                if ok:
                    st.session_state['edit_teacher_success'] = f"✅ {msg}"
                    updated = get_teacher_by_id(t['employee_id'])
                    st.session_state['edit_teacher'] = updated
                    st.session_state.pop('t_edit_results', None)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


# ─── Salary ──────────────────────────────────────────────────────────────────

def _teacher_salary(user):
    st.subheader("Teacher Salary Details")
    st.caption("Search by teacher name or Employee ID.")

    query = st.text_input("Name or Employee ID", key="t_salary_query",
                          placeholder="e.g. Sunita  or  EMP-20240901120000")

    if st.button("🔍 Find Teacher", key="btn_find_teacher_salary"):
        if not query.strip():
            st.warning("Please enter a name or Employee ID.")
        else:
            results = search_teachers(query.strip())
            if results:
                st.session_state['t_salary_results'] = results
                st.session_state.pop('salary_teacher', None)
            else:
                st.session_state.pop('t_salary_results', None)
                st.error("No teachers found.")

    results = st.session_state.get('t_salary_results', [])
    if results and 'salary_teacher' not in st.session_state:
        options = {
            f"{t['first_name']} {t['last_name']} — {t['employee_id']}": t
            for t in results
        }
        chosen = st.selectbox("Select teacher", list(options.keys()), key="t_salary_select")
        if st.button("Load Salary Details", key="btn_load_salary_details"):
            st.session_state['salary_teacher'] = options[chosen]
            st.rerun()

    if 'salary_teacher' in st.session_state:
        t = st.session_state['salary_teacher']

        if st.button("← Back to search", key="btn_back_salary"):
            st.session_state.pop('salary_teacher', None)
            st.rerun()

        monthly_salary = (t['salary_amount'] if t['salary_frequency'] == 'Monthly'
                          else t['salary_amount'] / 12)

        st.markdown(f"### {t['first_name']} {t['last_name']} — {t['employee_id']}")
        st.markdown(f"**Monthly Salary:** ₹{monthly_salary:,.2f} &nbsp;|&nbsp; "
                    f"**Frequency:** {t['salary_frequency']} (₹{t['salary_amount']:,.2f})")

        today = date.today()
        join_date = date.fromisoformat(t['joining_date'])
        months_employed = max(1, (today.year - join_date.year) * 12 + (today.month - join_date.month) + 1)
        payments = get_salary_payments(t['employee_id'])
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
                        st.error("**For Month** is required — e.g. 'April 2025'.")
                    else:
                        add_salary_payment(t['employee_id'], str(pay_date),
                                           amount, month_year.strip(), remarks.strip())
                        st.success("Salary payment recorded.")
                        st.rerun()
