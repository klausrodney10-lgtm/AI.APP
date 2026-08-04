"""
Put this file next to app.py, then run it BOTH ways in the same terminal:

    python diag.py
    python -m streamlit run diag.py

If the two give different answers, you have two environments.
"""

import os
import sys

LINE = "=" * 58


def report():
    out = []
    out.append(LINE)
    out.append("PYTHON RUNNING THIS")
    out.append(f"   {sys.executable}")
    out.append("")
    out.append("FOLDER I'M IN")
    out.append(f"   {os.getcwd()}")
    out.append("")
    out.append("ARCHITECTURE  (want AMD64, not ARM64)")
    import platform
    out.append(f"   {platform.machine()}   python {sys.version.split()[0]}")
    out.append("")
    out.append(LINE)
    out.append("PACKAGES")

    missing = []
    for name in ["streamlit", "openai", "pypdf", "chromadb", "requests", "dotenv"]:
        try:
            mod = __import__(name)
            where = getattr(mod, "__file__", "") or ""
            out.append(f"   {name:11} OK       {where}")
        except ModuleNotFoundError:
            out.append(f"   {name:11} MISSING")
            missing.append(name)

    out.append("")
    out.append(LINE)
    out.append("FILES IN THIS FOLDER")
    try:
        for f in sorted(os.listdir(".")):
            out.append(f"   {f}")
    except Exception as e:
        out.append(f"   could not list: {e}")

    out.append("")
    out.append(LINE)
    if missing:
        out.append(f"VERDICT: missing {', '.join(missing)}")
        out.append("")
        out.append("Fix, in THIS terminal:")
        out.append(f"   python -m pip install {' '.join(missing).replace('dotenv','python-dotenv')}")
        out.append("")
        out.append("If it says 'already satisfied', pip and python are")
        out.append("different interpreters. Compare:")
        out.append("   python -c \"import sys; print(sys.executable)\"")
        out.append("   pip -V")
    else:
        out.append("VERDICT: everything is here. Run your app with:")
        out.append("   python -m streamlit run app.py")
    out.append(LINE)
    return "\n".join(out)


text = report()

# are we actually running under "streamlit run", or plain python?
in_streamlit = False
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    in_streamlit = get_script_run_ctx() is not None
except Exception:
    in_streamlit = False

if in_streamlit:
    import streamlit as st
    st.set_page_config(page_title="diag")
    st.title("Environment check")
    st.caption("This is what STREAMLIT sees. Compare it with  python diag.py")
    st.code(text)
else:
    print(text)
