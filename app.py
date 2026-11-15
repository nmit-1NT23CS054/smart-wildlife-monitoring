from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "monitoring_outputs"

st.set_page_config(page_title="Smart Wildlife Monitoring",
                   page_icon="🐘", layout="wide")
st.title("Smart Wildlife Monitoring and Threat Analysis")
st.caption("YOLO11s detection | ByteTrack tracking | Protected-zone monitoring")

def load_json(path):
    return json.loads(path.read_text()) if path.exists() else {}

metrics = load_json(REPORT_DIR / "detection_metrics.json")
history_path = REPORT_DIR / "tracking_history.csv"
events_path = REPORT_DIR / "wildlife_events.csv"
threat_path = REPORT_DIR / "threat_analysis.csv"
video_path = REPORT_DIR / "tracked_wildlife.mp4"

history = pd.read_csv(history_path) if history_path.exists() else pd.DataFrame()
events = pd.read_csv(events_path) if events_path.exists() else pd.DataFrame()
threats = pd.read_csv(threat_path) if threat_path.exists() else pd.DataFrame()

st.subheader("Detection model performance")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Precision", f"{metrics.get('precision',0):.3f}")
c2.metric("Recall", f"{metrics.get('recall',0):.3f}")
c3.metric("mAP@50", f"{metrics.get('mAP50',0):.3f}")
c4.metric("mAP@50-95", f"{metrics.get('mAP50_95',0):.3f}")

st.divider()
left,right = st.columns([1.4,1])
with left:
    st.subheader("Tracked wildlife video")
    if video_path.exists():
        st.video(str(video_path))
    else:
        st.info("Run the notebook tracking cells to create a video.")
with right:
    st.subheader("Unique track IDs by species")
    if not history.empty:
        summary = history.groupby("species")["cumulative_unique_tracks"].max().reset_index()
        summary.columns = ["species","unique_track_ids"]
        st.plotly_chart(px.bar(summary,x="species",y="unique_track_ids"),
                        use_container_width=True)
        st.metric("Total unique track IDs", int(summary["unique_track_ids"].sum()))
    else:
        st.info("No tracking history available.")

st.divider()
st.subheader("Wildlife activity over time")
if not history.empty:
    st.plotly_chart(px.line(history,x="time_seconds",
                            y="cumulative_unique_tracks",color="species"),
                    use_container_width=True)
else:
    st.info("No tracking history available.")

st.subheader("Monitoring events")
if not events.empty:
    a,b,c = st.columns(3)
    a.metric("Total events", len(events))
    b.metric("Line crossings", int((events["event"]=="LINE_CROSSING").sum()))
    c.metric("Protected-zone entries",
             int((events["event"]=="PROTECTED_ZONE_ENTRY").sum()))
    st.dataframe(events,use_container_width=True)
else:
    st.info("No events were recorded.")

st.subheader("Threat and priority analysis")
if not threats.empty:
    if "risk_label" in threats.columns:
        counts = threats["risk_label"].value_counts().reset_index()
        counts.columns = ["priority","events"]
        st.plotly_chart(px.bar(counts,x="priority",y="events"),
                        use_container_width=True)
    st.dataframe(threats,use_container_width=True)
else:
    st.info("Threat analysis report is not available.")

st.caption("Track IDs are not biological identities. Zone events and priorities are monitoring aids, not proof of danger or illegal activity.")
