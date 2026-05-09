import streamlit as st
from database import get_all_users, create_user, delete_user


def render_admin_panel():
    st.subheader("👤 User Management")
    st.caption("Create and manage login accounts for staff members.")

    form_key = st.session_state.get('add_user_form_key', 0)

    if st.session_state.get('add_user_success'):
        st.success(st.session_state.pop('add_user_success'))

    with st.expander("➕ Create New User", expanded=st.session_state.get('add_user_expander', False)):
        with st.form(f"create_user_form_{form_key}"):
            col1, col2 = st.columns(2)
            with col1:
                login_id = st.text_input(
                    "Login ID (exactly 5 characters) *",
                    max_chars=5,
                    key=f"new_login_id_{form_key}",
                    placeholder="e.g. usr01"
                )
                name = st.text_input(
                    "Full Name *",
                    key=f"new_user_name_{form_key}",
                    placeholder="e.g. Sunita Rao"
                )
            with col2:
                password = st.text_input(
                    "Password (exactly 8 characters) *",
                    max_chars=8,
                    type="password",
                    key=f"new_user_pass_{form_key}",
                    placeholder="8 characters"
                )
                role = st.selectbox("Role *", ["Teacher", "Manager"], key=f"new_user_role_{form_key}")

            submitted = st.form_submit_button("✅ Create User", use_container_width=True)

        if submitted:
            errors = []
            if len(login_id.strip()) != 5:
                errors.append(f"**Login ID** must be exactly 5 characters (you entered {len(login_id.strip())}).")
            if len(password) != 8:
                errors.append(f"**Password** must be exactly 8 characters (you entered {len(password)}).")
            if not name.strip():
                errors.append("**Full Name** is required.")

            if errors:
                st.error("Please fix the following errors:")
                for e in errors:
                    st.markdown(f"- {e}")
                # Keep expander open so user sees the errors alongside the form
                st.session_state['add_user_expander'] = True
            else:
                ok, msg = create_user(login_id.strip(), password, name.strip(), role)
                if ok:
                    st.session_state['add_user_form_key'] = form_key + 1
                    st.session_state['add_user_success'] = f"✅ {msg} — Login ID: **{login_id.strip()}**, Role: **{role}**"
                    st.session_state['add_user_expander'] = False
                    st.rerun()
                else:
                    # DB error (duplicate ID) — keep form data, show error inline
                    st.error(f"❌ {msg}")
                    st.session_state['add_user_expander'] = True

    st.divider()
    st.markdown("#### Existing Users")

    users = get_all_users()
    if not users:
        st.info("No users created yet. Use the form above to add staff login accounts.")
    else:
        # Header row
        hc1, hc2, hc3, hc4 = st.columns([2, 2, 1, 1])
        hc1.markdown("**Name / Login ID**")
        hc2.markdown("**Role**")

        st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

        for u in users:
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            c1.markdown(f"**{u['name']}**  \n`{u['login_id']}`")
            c2.markdown(
                f"<span style='background:#e0f2fe;color:#0369a1;padding:3px 10px;"
                f"border-radius:12px;font-size:13px;font-weight:600'>{u['role']}</span>",
                unsafe_allow_html=True
            )
            # Confirm-delete pattern: first click arms, second click fires
            arm_key = f"arm_del_{u['login_id']}"
            if not st.session_state.get(arm_key):
                if c4.button("🗑️ Delete", key=f"del_btn_{u['login_id']}"):
                    st.session_state[arm_key] = True
                    st.rerun()
            else:
                c3.markdown("**Sure?**")
                if c4.button("✅ Yes", key=f"confirm_del_{u['login_id']}"):
                    delete_user(u['login_id'])
                    st.session_state.pop(arm_key, None)
                    st.success(f"User '{u['name']}' deleted.")
                    st.rerun()
                if c3.button("Cancel", key=f"cancel_del_{u['login_id']}"):
                    st.session_state.pop(arm_key, None)
                    st.rerun()

            st.markdown("<hr style='margin:4px 0'>", unsafe_allow_html=True)
