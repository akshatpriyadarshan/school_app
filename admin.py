import streamlit as st
from database import get_all_users, create_user, delete_user


def render_admin_panel():
    st.subheader("👤 User Management")
    st.caption("Create and manage login accounts for staff members.")

    # Create new user form
    with st.expander("➕ Create New User", expanded=False):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                login_id = st.text_input("Login ID (5 characters) *", max_chars=5, key="new_login_id")
                name = st.text_input("Full Name *", key="new_user_name")
            with col2:
                password = st.text_input("Password (8 characters) *", max_chars=8,
                                         type="password", key="new_user_pass")
                role = st.selectbox("Role *", ["Teacher", "Manager"], key="new_user_role")

            submitted = st.form_submit_button("Create User", use_container_width=True)
            if submitted:
                errors = []
                if len(login_id.strip()) != 5:
                    errors.append("Login ID must be exactly 5 characters.")
                if len(password) != 8:
                    errors.append("Password must be exactly 8 characters.")
                if not name.strip():
                    errors.append("Full Name is required.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = create_user(login_id.strip(), password, name.strip(), role)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.divider()
    st.markdown("#### Existing Users")

    users = get_all_users()
    if not users:
        st.info("No users created yet.")
    else:
        for u in users:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            col1.markdown(f"**{u['name']}**  \n`{u['login_id']}`")
            col2.markdown(f"Role: **{u['role']}**")
            if col4.button("🗑️ Delete", key=f"del_user_{u['login_id']}"):
                delete_user(u['login_id'])
                st.success(f"User '{u['login_id']}' deleted.")
                st.rerun()
            st.divider()
