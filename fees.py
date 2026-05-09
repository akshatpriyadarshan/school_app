import streamlit as st
from database import get_fee_structure, update_fee_structure, get_list_of_classes


def render_fee_structure(user):
    st.subheader("📋 Fee Structure")
    is_admin = user['role'] == 'Admin'

    fee_data = get_fee_structure()
    fee_map = {f['class_name']: f['monthly_fee'] for f in fee_data}
    classes = get_list_of_classes()

    selected_class = st.selectbox("Select Class to View Fee", classes, key="fee_struct_class")
    monthly_fee = fee_map.get(selected_class, 0)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
         color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 16px 0;">
        <div style="font-size: 14px; opacity: 0.85;">Monthly Fee for</div>
        <div style="font-size: 22px; font-weight: 700; margin: 4px 0;">{selected_class}</div>
        <div style="font-size: 36px; font-weight: 800;">₹{monthly_fee:,.2f}</div>
        <div style="font-size: 13px; opacity: 0.75;">Annual: ₹{monthly_fee * 12:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### All Classes Fee Overview")

    # Display all fees in a nice table
    cols = st.columns(3)
    for i, cls in enumerate(classes):
        fee = fee_map.get(cls, 0)
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 8px;
                 padding: 10px 14px; margin-bottom: 8px;">
                <div style="font-size: 12px; color: #64748b;">{cls}</div>
                <div style="font-size: 18px; font-weight: 700; color: #1e293b;">₹{fee:,.0f}/mo</div>
            </div>
            """, unsafe_allow_html=True)

    # Admin can edit
    if is_admin:
        st.divider()
        st.markdown("#### ✏️ Edit Fee Structure (Admin Only)")
        with st.form("edit_fee_form"):
            edit_class = st.selectbox("Select Class to Edit", classes, key="fee_edit_class")
            current_fee = fee_map.get(edit_class, 0)
            new_fee = st.number_input(
                f"New Monthly Fee for {edit_class}",
                min_value=0.0, value=float(current_fee), step=50.0, key="new_fee_amount"
            )
            if st.form_submit_button("💾 Update Fee", use_container_width=True):
                update_fee_structure(edit_class, new_fee)
                st.success(f"Fee for {edit_class} updated to ₹{new_fee:,.2f}/month.")
                st.rerun()
