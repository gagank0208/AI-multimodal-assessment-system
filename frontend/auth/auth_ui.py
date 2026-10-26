
from pathlib import Path
from html import escape

import streamlit as st

from auth.firebase_auth import login_user, register_user


def load_auth_css():
    css_path = Path(__file__).resolve().parent / "style.css"

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_auth():
    load_auth_css()

    st.markdown(
        """
        <div class="auth-header">
            <div class="auth-logo">🎙️</div>
            <div class="auth-title">
                AI Interview
                <span class="auth-pink">Assessment Studio</span>
            </div>
        </div>
        <div class="auth-subtitle">
            Multimodal Assessment · Computer Vision · Speech · Semantic NLP
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("### Candidate Access")

        mode = st.radio(
            "Choose an option",
            ["Login", "Create account"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
        )

        with st.form("firebase_auth_form", clear_on_submit=True):
            name = ""

            if mode == "Create account":
                name = st.text_input(
                    "Full name",
                    placeholder="Enter your full name",
                )

            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            if mode == "Create account":
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                )
            else:
                confirm_password = ""

            submitted = st.form_submit_button(
                "Create account" if mode == "Create account" else "Login",
                type="primary",
                use_container_width=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            email = email.strip()

            if not email or not password:
                st.error("Please enter your email and password.")

            elif mode == "Create account" and not name.strip():
                st.error("Please enter your full name.")

            elif mode == "Create account" and password != confirm_password:
                st.error("Your passwords do not match.")

            elif mode == "Create account" and len(password) < 6:
                st.error("Password must contain at least 6 characters.")

            else:
                try:
                    with st.spinner("Authenticating with Firebase..."):
                        if mode == "Create account":
                            result = register_user(
                                name,
                                email,
                                password,
                            )
                        else:
                            result = login_user(email, password)

                    st.session_state["auth_user"] = {
                        "uid": result["localId"],
                        "email": result["email"],
                        "name": result.get("displayName", name),
                    }

                    st.session_state["auth_id_token"] = result["idToken"]
                    st.session_state["auth_refresh_token"] = (
                        result["refreshToken"]
                    )

                    st.rerun()

                except ValueError as exc:
                    st.error(str(exc))

    with right:
        st.markdown(
            """
            <div class="auth-info">
                <h2>📋 Interview Protocol &amp; Guidelines</h2>

                <div class="feature">
                    <div class="feature-title">👁️ Computer Vision Analysis</div>
                    Tracks facial expressions, gaze alignment and head movement.
                </div>

                <div class="feature">
                    <div class="feature-title">🎙️ Speech Analysis</div>
                    Evaluates speaking pace, hesitation and filler words.
                </div>

                <div class="feature">
                    <div class="feature-title">🧠 Semantic NLP</div>
                    Evaluates answers against relevant interview concepts.
                </div>

                <div class="feature">
                    <div class="feature-title">🔒 Secure Candidate Access</div>
                    Sign in to access your interview assessment workspace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_authenticated_controls():
    user = st.session_state["auth_user"]
    display_name = escape(user.get("name") or user.get("email") or "user")
    email = escape(user.get("email") or "")

    identity, logout = st.columns([6, 1])
    with identity:
        st.caption(f"Signed in as **{display_name}** ({email})")

    with logout:
        if st.button("Log out", key="auth_logout", use_container_width=True):
            for key in (
                "auth_user",
                "auth_id_token",
                "auth_refresh_token",
                "auth_mode",
                "current_page",
                "candidate_name",
                "candidate_email",
                "active_role",
                "question_idx",
                "duration",
                "interview_completed",
                "last_result",
            ):
                st.session_state.pop(key, None)
            st.rerun()
