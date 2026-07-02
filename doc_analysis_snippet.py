# ============================================================================
# DROP-IN REPLACEMENT — DOMINATE 3AI  "Document Analysis" section
# ----------------------------------------------------------------------------
# WHAT THIS DOES (vs. the old single-analysis version):
#   - Lets the user choose Normal / Advanced / Monetized reports to generate
#     FROM the uploaded document (same engine as the main report flow).
#   - Renders each chosen report (bullet-point format).
#   - Adds Download PDF + Download .txt + Email for the document analysis.
#
# HOW TO INCORPORATE INTO YOUR EXISTING app_finalv5.py:
#   1) Find the existing block that starts with:
#          # -- Document analysis (uploaded consulting document) --
#      and ends just before:
#          # -- Render stored reports --
#      DELETE that whole block and PASTE everything below in its place.
#
#   2) (Optional) In the sidebar "Clear Form" button, add these keys to the
#      list it pops so Clear also wipes a document analysis:
#          "doc_reports", "doc_report_subject"
#
# REQUIRES (already in app_finalv5.py): REPORT_BLUEPRINTS,
#   generate_section_report, parse_sections, qml_metrics, render_report,
#   build_pdf, build_text_export, send_email, company_logo_url, and the form
#   variables org_name / org_domain. No new imports needed.
# ============================================================================

# ── Document analysis (uploaded consulting document) ──────────────────────────
_doc_text = st.session_state.get("uploaded_doc_text", "")
if _doc_text and not _doc_text.startswith("["):
    _doc_name = st.session_state.get("uploaded_doc_name", "document")
    _doc_subject = _doc_name.rsplit(".", 1)[0]          # filename without extension

    st.markdown('<div class="sec-lbl">📎 Document Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">Analyze: {_doc_name}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:12px;color:rgba(255,255,255,0.5);margin-bottom:8px;'>"
        f"{len(_doc_text):,} characters loaded. Choose which reports DOMINATE 3AI should "
        f"generate from this document using the local {MODEL_NAME} model.</div>",
        unsafe_allow_html=True,
    )

    # Pick which report types to produce FROM the document.
    _dca, _dcb, _dcc = st.columns(3)
    with _dca:
        _dn = st.checkbox("Normal Report", value=False, key="doc_gen_normal")
    with _dcb:
        _da = st.checkbox("Advanced Report", value=True, key="doc_gen_advanced")
    with _dcc:
        _dm = st.checkbox("Monetized (QML)", value=False, key="doc_gen_monetized")

    _doc_types = [t for t, on in
                  (("normal", _dn), ("advanced", _da), ("monetized", _dm)) if on]

    analyze_clicked = st.button("🔍 Analyze Document", type="primary", use_container_width=True)

    if analyze_clicked:
        if not _doc_types:
            st.error("Select at least one report type to generate from the document.")
        else:
            _doc_prompt = (
                "You are a senior management consultant. Analyze the following consulting "
                f"document for {_doc_subject} and produce a rigorous, specific report.\n\n"
                "DOCUMENT:\n" + _doc_text[:3500]
            )
            _dreports = {}
            _dbar = st.progress(0)
            _dstatus = st.empty()
            for _i, _rt in enumerate(_doc_types):
                _bp = REPORT_BLUEPRINTS[_rt]
                _dstatus.markdown(
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:12px;"
                    f"color:rgba(0,200,255,0.7);'>▶ Generating {_bp['label']} from document...</div>",
                    unsafe_allow_html=True,
                )
                _draw = generate_section_report(
                    _doc_prompt, tuple(_bp["sections"]), _bp["depth"], _bp["tokens"])
                _dsecs = parse_sections(_draw, _bp["sections"])
                _dobj = {"title": f"{_bp['label']}: {_doc_subject}", "sections": _dsecs}
                if _rt == "monetized":
                    _ds, _dr = qml_metrics(_doc_subject)
                    _dobj["qml_score"] = _ds
                    _dobj["projected_roi"] = _dr
                _dreports[_rt] = _dobj
                _dbar.progress(int((_i + 1) / len(_doc_types) * 100))
            _dstatus.markdown(
                "<div style='color:#00E5A0;font-family:JetBrains Mono,monospace;font-size:12px;'>"
                "✓ Document analysis complete.</div>", unsafe_allow_html=True)
            st.session_state["doc_reports"] = _dreports
            st.session_state["doc_report_subject"] = _doc_subject

    # ── Render + download + email the document-analysis reports ───────────────
    if st.session_state.get("doc_reports"):
        _dreports = st.session_state["doc_reports"]
        _dsubject = st.session_state.get("doc_report_subject", _doc_subject)
        for _rt in ["normal", "advanced", "monetized"]:
            if _rt in _dreports:
                render_report(_dreports[_rt], _rt)

        st.markdown("---")
        _dlogo = company_logo_url(org_name, org_domain)
        _dtext = build_text_export(_dreports, _dsubject)
        _dpdf = build_pdf(_dreports, _dsubject, _dlogo)
        _dbase = (f"{_dsubject.replace(' ', '_')}_DOMINATE3AI_DOCANALYSIS_"
                  f"{datetime.now().strftime('%Y%m%d')}")

        _dd1, _dd2 = st.columns(2)
        with _dd1:
            if _dpdf:
                st.download_button("⬇ Download PDF", data=_dpdf,
                                   file_name=f"{_dbase}.pdf", mime="application/pdf",
                                   use_container_width=True, type="primary",
                                   key="doc_pdf_dl")
            else:
                st.button("⬇ Download PDF", use_container_width=True, disabled=True,
                          key="doc_pdf_dl_disabled")
                st.caption("Install reportlab for PDF export:  pip install reportlab")
        with _dd2:
            st.download_button("⬇ Download .txt", data=_dtext,
                               file_name=f"{_dbase}.txt", mime="text/plain",
                               use_container_width=True, key="doc_txt_dl")

        st.markdown('<div class="sec-lbl">📧 Email Document Analysis</div>',
                    unsafe_allow_html=True)
        _de1, _de2 = st.columns([3, 1])
        with _de1:
            _drecipient = st.text_input("Recipient email address",
                                        placeholder="name@company.com",
                                        label_visibility="collapsed",
                                        key="doc_email_recipient")
        with _de2:
            _dsend = st.button("✉ Send to Email", use_container_width=True,
                               key="doc_email_send")

        if _dsend:
            if not _drecipient or "@" not in _drecipient:
                st.error("Please enter a valid email address.")
            else:
                _dmail_subj = f"DOMINATE 3AI Document Analysis — {_dsubject}"
                if _dpdf:
                    _datt = (f"{_dbase}.pdf", _dpdf, "pdf")
                    _dbody = (f"Hello,\n\nPlease find attached the DOMINATE 3AI document "
                              f"analysis for {_doc_name}, generated on "
                              f"{datetime.now().strftime('%Y-%m-%d %H:%M')} using a local "
                              f"Ollama model.\n\n— DOMINATE 3AI · ABP Communications LLC")
                else:
                    _datt = None
                    _dbody = _dtext
                with st.spinner("Sending document analysis..."):
                    _dok, _dmsg = send_email(_drecipient, _dmail_subj, _dbody, _datt)
                if _dok:
                    st.success(f"✅ {_dmsg}" + (" (PDF attached)" if _dpdf else " (text only)"))
                else:
                    st.warning(f"⚠ {_dmsg}")
    st.markdown("---")


