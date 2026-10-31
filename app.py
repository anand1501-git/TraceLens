import os

import requests
import streamlit as st


API_URL = os.getenv("TRACELENS_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="TraceLens", page_icon="🔎")
st.title("TraceLens")
st.write("Paste a Python traceback to inspect its frames and root cause.")

traceback_text = st.text_area(
    "Python traceback",
    height=260,
    placeholder="Paste the complete traceback here..."
)

if st.button("Analyze", type="primary"):
    if not traceback_text.strip():
        st.error("Paste a traceback before starting the analysis.")
    else:
        try:
            response = requests.post(
                f"{API_URL.rstrip('/')}/api/analyze",
                json={"traceback": traceback_text},
                timeout=(3, 60)
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as error:
            st.error(f"Could not reach the TraceLens API: {error}")
        else:
            parsed = result["traceback"]
            report = result["root_cause"]

            st.subheader("Traceback")
            st.write(
                f"**Error:** {parsed['error_type'] or 'Unknown'}"
                + (
                    f": {parsed['error_message']}"
                    if parsed["error_message"]
                    else ""
                )
            )
            if parsed["frames"]:
                st.dataframe(parsed["frames"], use_container_width=True)
            else:
                st.warning("No Python file frames were found.")

            st.subheader("Root-cause analysis")
            if report["status"] != "analyzed":
                st.warning(report["reason"])
            else:
                failing = report["failing_function"]
                st.write(
                    f"Failing function: `{failing['function']}` "
                    f"({failing['file']}:{failing['error_line']})"
                )
                if report["caller_chain"]:
                    st.write("Caller chain:")
                    for caller in report["caller_chain"]:
                        st.code(caller, language="text")
                else:
                    st.info("No callers were found in the analyzed source.")

                issue = report["data_issue"]
                if issue:
                    st.error(issue["explanation"])
                    st.caption(issue["evidence"])
                else:
                    st.info(
                        "No supported suspicious data-flow value was found."
                    )