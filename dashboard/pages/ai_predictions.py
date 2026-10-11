"""AI & Predictive Analytics Page for Medical Operations Intelligence."""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_row,
    create_line_chart,
    create_bar_chart
)
from ml.model_manager import ModelManager


def render_ai_predictions(db, filters):
    st.title("🤖 AI Predictions & Machine Learning Analytics")
    facility_id = filters.get("facility")

    try:
        mm = ModelManager(db)

        # 1. Action to retrain models
        col_title, col_btn = st.columns([3, 1])
        with col_btn:
            if st.button("🔄 Retrain All ML Models", type="primary"):
                with st.spinner("Training Ridge Regression & Random Forest models on live MongoDB data..."):
                    res = mm.train_all_models(facility_id=facility_id)
                    st.success(f"Models Retrained: {res}")

        st.markdown("---")

        # Automatically ensure models are trained for initial render
        if not mm.patient_forecaster.is_trained:
            mm.patient_forecaster.train(facility_id=facility_id)
        if not mm.no_show_predictor.is_trained:
            mm.no_show_predictor.train(facility_id=facility_id)

        # 2. Patient Volume Forecast (Next 30 Days)
        st.subheader("📈 30-Day Patient Volume Demand Forecast")
        preds = mm.patient_forecaster.predict(days=30)
        metrics = mm.patient_forecaster.metrics

        if preds:
            df_pred = pd.DataFrame(preds)
            st.plotly_chart(
                create_line_chart(df_pred, x="date", y="predicted_count", title="Predicted Daily Patient Volume (Ridge Regression)"),
                use_container_width=True
            )
            st.caption(
                f"Model Performance Metrics — MAE: **{metrics.get('mae', 'N/A')}** | "
                f"RMSE: **{metrics.get('rmse', 'N/A')}** | R²: **{metrics.get('r2', 'N/A')}** | "
                f"Train Samples: **{metrics.get('train_size', 0)}**"
            )
        else:
            st.info("Click 'Retrain All ML Models' to generate patient volume demand forecasts.")

        st.markdown("---")

        # 3. High Risk No-Show Patients & Feature Importance
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚨 High-Risk No-Show Appointments")
            risk_appts = mm.no_show_predictor.get_risk_appointments(facility_id=facility_id)
            if risk_appts:
                df_risk = pd.DataFrame(risk_appts)
                st.dataframe(df_risk[["appointment_id", "patient_id", "date", "type", "probability"]], use_container_width=True)
                no_show_metrics = mm.no_show_predictor.metrics
                st.caption(f"Random Forest Accuracy: **{no_show_metrics.get('accuracy', 0)*100:.1f}%** | AUC: **{no_show_metrics.get('auc', 0):.3f}**")
            else:
                st.info("No scheduled appointments flagged as high no-show risk.")

        with col2:
            st.subheader("🔍 No-Show Risk Factors")
            imp = mm.no_show_predictor.get_feature_importance()
            if imp:
                df_imp = pd.DataFrame(imp)
                st.plotly_chart(
                    create_bar_chart(df_imp, x="feature", y="importance", title="Random Forest Feature Importance"),
                    use_container_width=True
                )
            else:
                st.info("Train no-show predictor to view risk feature importance.")

        st.markdown("---")

        # 4. Anomaly Detection Alerts
        st.subheader("⚠️ Operational Anomaly Detection (Isolation Forest)")
        anomalies = mm.anomaly_detector.detect_all_anomalies(facility_id=facility_id)
        if anomalies:
            tabs = st.tabs(["Wait Time Anomalies", "Volume Anomalies", "Revenue Anomalies"])
            with tabs[0]:
                wait_anom = anomalies.get("waiting_time_anomalies", [])
                if wait_anom:
                    st.dataframe(pd.DataFrame(wait_anom), use_container_width=True)
                else:
                    st.success("✅ No wait time anomalies detected.")
            with tabs[1]:
                vol_anom = anomalies.get("volume_anomalies", [])
                if vol_anom:
                    st.dataframe(pd.DataFrame(vol_anom), use_container_width=True)
                else:
                    st.success("✅ No patient volume anomalies detected.")
            with tabs[2]:
                rev_anom = anomalies.get("revenue_anomalies", [])
                if rev_anom:
                    st.dataframe(pd.DataFrame(rev_anom), use_container_width=True)
                else:
                    st.success("✅ No revenue collection anomalies detected.")

    except Exception as e:
        st.error(f"Error rendering AI Predictions: {e}")
