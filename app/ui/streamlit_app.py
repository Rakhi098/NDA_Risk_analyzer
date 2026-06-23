import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NDA Risk Analyzer Pro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "NDA Risk Analyzer Pro v2.0 - Professional AI-Assisted Risk Analysis"
    }
)

# Custom styling
st.markdown("""
    <style>
    .risk-high {
        background-color: #ffebee;
        border-left: 5px solid #d32f2f;
        padding: 15px;
        border-radius: 5px;
    }
    .risk-medium {
        background-color: #fff3e0;
        border-left: 5px solid #f57c00;
        padding: 15px;
        border-radius: 5px;
    }
    .risk-low {
        background-color: #e8f5e9;
        border-left: 5px solid #388e3c;
        padding: 15px;
        border-radius: 5px;
    }
    .score-box {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .score-number {
        font-size: 36px;
        font-weight: bold;
    }
    .recommendation-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("📋 NDA Risk Analyzer Pro")
st.markdown("**AI-Powered Professional NDA Risk Analysis** | Gemma 2B via Ollama | 100% Offline")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8000",
        help="Base URL of the NDA Risk Analyzer API"
    )
    
    st.divider()
    
    st.header("📌 Quick Start")
    with st.expander("Setup Instructions"):
        st.markdown("""
        **Prerequisites:**
        - Ollama running locally
        - Gemma 2B model: `ollama pull gemma:2b`
        - API server running on port 8000
        
        **Commands:**
        ```bash
        # Terminal 1: Start Ollama
        ollama serve
        
        # Terminal 2: Start API
        cd NDA_Solution
        python run.py --api
        
        # Terminal 3: Start UI (auto-opens)
        python run.py --ui
        ```
        """)
    
    st.divider()
    
    st.header("ℹ️ About")
    st.markdown("""
    **Features:**
    - 🤖 AI analysis with Gemma 2B
    - ✅ Rule-based validation
    - 🔒 Fully offline processing
    - 📊 Risk scoring (0-100)
    - 💡 Mitigation recommendations
    - 📄 Comprehensive reporting
    """)

# Main content
st.markdown("Upload your NDA document for comprehensive risk analysis and recommendations.")

# File uploader
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader(
        "Choose PDF file",
        type="pdf",
        help="Upload your NDA document for analysis"
    )

if uploaded_file is not None:
    # Display file info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"📄 **File:** {uploaded_file.name}")
    with col2:
        st.info(f"📊 **Size:** {uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.info(f"⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}")
    with col4:
        st.info(f"🔍 **Status:** Ready")
    
    # Analyze button
    if st.button("🔍 Analyze NDA Document", type="primary", use_container_width=True):
        with st.spinner("⏳ Analyzing document... Please wait..."):
            start_time = time.time()
            try:
                # Upload to API
                files = {"file": (uploaded_file.name, uploaded_file.getbuffer(), "application/pdf")}
                response = requests.post(f"{api_url}/upload", files=files, timeout=300)
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Success message
                    st.success(f"✅ Analysis complete in {elapsed_time:.2f}s")
                    
                    # Overall Risk Summary
                    st.divider()
                    st.subheader("📊 Executive Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        risk_level = result["overall_risk"]
                        if risk_level == "High":
                            st.error(f"🔴 **Overall Risk: HIGH**")
                        elif risk_level == "Medium":
                            st.warning(f"🟡 **Overall Risk: MEDIUM**")
                        else:
                            st.success(f"🟢 **Overall Risk: LOW**")
                    
                    with col2:
                        st.metric("⚠️ Risky Clauses Found", result["total_risky_clauses"])
                    
                    with col3:
                        avg_score = sum([a.get("risk_score", 0) for a in result["analysis"]]) / len(result["analysis"]) if result["analysis"] else 0
                        st.metric("📈 Avg. Risk Score", f"{avg_score:.0f}/100")
                    
                    st.divider()
                    
                    # Detailed Analysis
                    if result["analysis"]:
                        st.subheader("🔍 Detailed Clause Analysis")
                        st.markdown(f"**{len(result['analysis'])} Clause(s) Requiring Review:**")
                        
                        for idx, clause_analysis in enumerate(result["analysis"], 1):
                            # Clause header with risk level
                            risk_level = clause_analysis["risk"].upper()
                            category = clause_analysis.get("category", "Other")
                            risk_score = clause_analysis.get("risk_score", 0)
                            
                            # Risk color coding
                            if clause_analysis["risk"] == "high":
                                emoji = "🔴"
                                risk_color = "high"
                            elif clause_analysis["risk"] == "medium":
                                emoji = "🟡"
                                risk_color = "medium"
                            else:
                                emoji = "🟢"
                                risk_color = "low"
                            
                            # Create expander for each clause
                            with st.expander(f"{emoji} Clause {idx} — {risk_level} Risk | {category}", expanded=False):
                                
                                # Top section with metrics
                                col1, col2, col3 = st.columns([1, 1, 1])
                                
                                with col1:
                                    risk_color_map = {
                                        "high": "#dc2626",
                                        "medium": "#ea580c",
                                        "low": "#16a34a"
                                    }
                                    risk_color = risk_color_map.get(clause_analysis["risk"], "#16a34a")
                                    card_html = f"""
                                    <div style="text-align: center; padding: 20px; background-color: {risk_color}; 
                                                border-radius: 10px; color: white; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
                                        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">Risk Level</div>
                                        <div style="font-size: 20px; font-weight: bold;">{risk_level}</div>
                                    </div>
                                    """
                                    st.markdown(card_html, unsafe_allow_html=True)
                                
                                with col2:
                                    card_html = f"""
                                    <div style="text-align: center; padding: 20px; background-color: #1e40af; 
                                                border-radius: 10px; color: white; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
                                        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">Category</div>
                                        <div style="font-size: 16px; font-weight: bold;">{category}</div>
                                    </div>
                                    """
                                    st.markdown(card_html, unsafe_allow_html=True)
                                
                                with col3:
                                    card_html = f"""
                                    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                border-radius: 10px; color: white; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
                                        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px;">Risk Score</div>
                                        <div style="font-size: 28px; font-weight: bold;">{risk_score}/100</div>
                                    </div>
                                    """
                                    st.markdown(card_html, unsafe_allow_html=True)
                                
                                st.divider()
                                
                                # Matched Rules
                                if clause_analysis.get("matched_rules"):
                                    st.markdown("### ✅ Matched Validation Rules")
                                    for rule in clause_analysis["matched_rules"]:
                                        st.success(f"• **{rule}**")
                                
                                # AI Explanation
                                st.markdown("### 🤖 AI Analysis")
                                st.info(f"**Explanation:** {clause_analysis['reason']}")
                                
                                # Clause Text
                                st.markdown("### 📄 Clause Text")
                                clause_preview = clause_analysis["clause"][:2000] + ("..." if len(clause_analysis["clause"]) > 2000 else "")
                                clause_html = f"""
                                <div style="background-color:#0f1720;padding:16px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);">
                                    <pre style="white-space:pre-wrap;color:#e6eef8;margin:0;font-size:13px;line-height:1.4">{clause_preview}</pre>
                                </div>
                                """
                                st.markdown(clause_html, unsafe_allow_html=True)
                                
                                # Mitigation Recommendations (clear and actionable)
                                if clause_analysis.get("recommendations"):
                                    st.markdown("### 💡 Mitigation Recommendations")
                                    for i, rec in enumerate(clause_analysis["recommendations"], 1):
                                        rec_html = f"""
                                        <div style=\"background:#07202c;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);margin-bottom:8px;\">
                                          <strong style=\"color:#ffd27f;\">{i}.</strong>
                                          <span style=\"color:#e6eef8;margin-left:8px;\">{rec}</span>
                                        </div>
                                        """
                                        st.markdown(rec_html, unsafe_allow_html=True)

                                # Visual risk indicator
                                try:
                                    pct = int(risk_score)
                                except Exception:
                                    pct = 0
                                st.markdown("### 📈 Risk Meter")
                                st.progress(min(max(pct / 100.0, 0.0), 1.0))
                    
                    else:
                        st.success("""
                        ✅ **No Risky Clauses Detected**
                        
                        This NDA appears to contain standard, balanced terms that are within acceptable risk parameters.
                        All analyzed clauses meet professional standards.
                        """)
                
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "Invalid request")
                    st.error(f"❌ **Request Error:** {error_msg}")
                    st.info("Please verify your PDF file and try again.")
                
                else:
                    st.error(f"❌ **Server Error:** {response.status_code}")
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(error_detail)
                    
            except requests.exceptions.Timeout:
                st.error("❌ **Timeout Error:** Analysis took too long. Try a smaller document.")
            
            except requests.exceptions.ConnectionError:
                st.error(f"❌ **Connection Error:** Cannot reach API at {api_url}")
                with st.expander("🔧 Troubleshooting"):
                    st.markdown(f"""
                    1. Verify API is running:
                    ```bash
                    python run.py --api
                    ```
                    
                    2. Check Ollama is running:
                    ```bash
                    ollama serve
                    ```
                    
                    3. Verify model is downloaded:
                    ```bash
                    ollama pull gemma:2b
                    ```
                    
                    4. Check API URL: {api_url}
                    """)
            
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
                st.info("Check logs for more details or try again.")

st.divider()

