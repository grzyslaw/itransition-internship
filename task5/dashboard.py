import streamlit as st
import pandas as pd
import os
from analysis import MineStatsAnalyzer
from import_sheet import get_data
from visualize import get_chart
from pdf_report import generate_pdf_report
import dashboard_default_values_config as conf
from dotenv import load_dotenv 


def render_method_and_chart_selectors(analyzer: MineStatsAnalyzer):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        method = st.selectbox(
            "Outlier method",
            ["IQR", "Z-score", "Moving avarage", "Grubbs"],
        )
    with col2:
        mine = st.selectbox("Mine", analyzer.get_all_mines())
    with col3:
        chart_type = st.selectbox("Chart type", ["line", "bar", "stacked"], index=1)
    with col4:
        trend_degree = st.selectbox("Trend degree", [0, 1, 2, 3, 4], index=0)
    return method, mine, chart_type, trend_degree


def render_method_params_sidebar(method: str):
    st.sidebar.header("Method parameters")
    if method == "IQR":
        bound_modifier = st.sidebar.number_input(
            "IQR bound modifier",
            min_value=conf.IQR_BOUND_MIN,
            max_value=conf.IQR_BOUND_MAX,
            value=conf.IQR_BOUND_VAL,
            step=conf.IQR_BOUND_STEP,
        )
        return {"bound_modifier": bound_modifier}
    
    elif method == "Z-score":
        z_threshold = st.sidebar.number_input(
            "Z-score threshold",
            min_value=conf.Z_SCORE_TRESH_MIN,
            max_value=conf.Z_SCORE_TRESH_MAX,
            value=conf.Z_SCORE_TRESH_VAL,
            step=conf.Z_SCORE_TRESH_STEP,
        )
        return {"treshold": z_threshold}

    elif method == "Moving avarage":
        window = st.sidebar.number_input(
            "Moving avarage window (days)",
            min_value=conf.MA_WINDOW_MIN,
            max_value=conf.MA_WINDOW_MAX,
            value=conf.MA_WINDOW_VAL,
            step=conf.MA_WINDOW_STEP,
        )
        distance_percent = st.sidebar.number_input(
            "Distance from MA (fraction)",
            min_value=conf.MA_DISTANCE_MIN,
            max_value=conf.MA_DISTANCE_MAX,
            value=conf.MA_DISTANCE_VAL,
            step=conf.MA_DISTANCE_STEP,
            format="%.2f",
        )
        return {
            "window": window,
            "distance_percent_treshold": distance_percent,
        }

    elif method == "Grubbs":
        alpha = st.sidebar.number_input(
            "Alpha (significance level)",
            min_value=conf.GRUBBS_ALPHA_MIN,
            max_value=conf.GRUBBS_ALPHA_MAX,
            value=conf.GRUBBS_ALPHA_VAL,
            step=conf.GRUBBS_ALPHA_STEP,
            format="%.2f",
        )
        side = st.sidebar.selectbox(
            "Side",
            ["both", "max", "min"],
            index=0,
        )
        return {"alpha": alpha, "side": side}


def get_outliers_for_selection(analyzer: MineStatsAnalyzer,df: pd.DataFrame, method: str, mine: str, params: dict):
    if method == "IQR":
        return analyzer.get_outliers_IQR(mine=mine, **params)

    elif method == "Z-score":
        return analyzer.get_outliers_zscore(mine=mine, **params)

    elif method == "Moving avarage":
        return analyzer.get_outliers_moving_avarage(mine=mine, **params)

    elif method == "Grubbs":
        return analyzer.get_outliers_grubbs(mine=mine, **params)

    return df.iloc[0:0].copy()

def render_report_config_and_button(analyzer: MineStatsAnalyzer, df: pd.DataFrame):
    with st.expander("Generate PDF report"):
        st.write("Configure report parameters and generate a full PDF.")

        chart_type = st.selectbox(
            "Report chart type",
            ["line", "bar", "stacked"],
            index=1,
            key="report_chart_type",
        )
        trend_degree = st.selectbox(
            "Report trend degree",
            [0, 1, 2, 3, 4],
            index=2,
            key="report_trend_degree",
        )

        st.markdown("Method parameters for report")

        col1, col2 = st.columns(2)
        with col1:
            bound_modifier = st.number_input(
                "IQR bound modifier (report)",
                min_value=conf.IQR_BOUND_MIN,
                max_value=conf.IQR_BOUND_MAX,
                value=conf.IQR_BOUND_VAL,
                step=conf.IQR_BOUND_STEP,
                key="report_iqr_bound",
            )
            z_threshold = st.number_input(
                "Z-score threshold (report)",
                min_value=conf.Z_SCORE_TRESH_MIN,
                max_value=conf.Z_SCORE_TRESH_MAX,
                value=conf.Z_SCORE_TRESH_VAL,
                step=conf.Z_SCORE_TRESH_STEP,
                key="report_z_threshold",
            )

        with col2:
            ma_window = st.number_input(
                "MA window (days, report)",
                min_value=conf.MA_WINDOW_MIN,
                max_value=conf.MA_WINDOW_MAX,
                value=conf.MA_WINDOW_VAL,
                step=conf.MA_WINDOW_STEP,
                key="report_ma_window",
            )
            ma_distance = st.number_input(
                "Distance from MA (fraction, report)",
                min_value=conf.MA_DISTANCE_MIN,
                max_value=conf.MA_DISTANCE_MAX,
                value=conf.MA_DISTANCE_VAL,
                step=conf.MA_DISTANCE_STEP,
                format="%.2f",
                key="report_ma_distance",
            )
            alpha = st.number_input(
                "Grubbs alpha (report)",
                min_value=conf.GRUBBS_ALPHA_MIN,
                max_value=conf.GRUBBS_ALPHA_MAX,
                value=conf.GRUBBS_ALPHA_VAL,
                step=conf.GRUBBS_ALPHA_STEP,
                format="%.2f",
                key="report_grubbs_alpha",
            )
            side = st.selectbox(
                "Grubbs side (report)",
                ["both", "max", "min"],
                index=0,
                key="report_grubbs_side",
            )

        generate = st.button("Generate PDF report")

        if generate:
            iqr_params = {"bound_modifier": bound_modifier}
            z_params = {"treshold": z_threshold}
            ma_params = {
                "window": ma_window,
                "distance_percent_treshold": ma_distance,
            }
            grubbs_params = {"alpha": alpha, "side": side}

            pdf_bytes = generate_pdf_report(
                analyzer,
                df,
                iqr_params=iqr_params,
                z_params=z_params,
                ma_params=ma_params,
                grubbs_params=grubbs_params,
                chart_type=chart_type,
                trend_degree=(None if trend_degree == 0 else trend_degree),
            )

            st.download_button(
                "Download report",
                data=pdf_bytes,
                file_name="mine_analysis_report.pdf",
                mime="application/pdf",
            )

def main():
    load_dotenv()
    sheets_link = os.getenv('SHEETS_LINK')
    print(sheets_link)
    df = get_data(sheets_link)
    analyzer = MineStatsAnalyzer(df)

    st.title("Weyland-Yutani Corporation mines dashboard")
    if st.button("🔄 Refresh"):
        st.rerun()
    st.subheader("Descriptive Statistics")
    st.table(analyzer.get_descriptive_statistics())

    st.subheader("Outliers")

    method, mine, chart_type, trend_degree = render_method_and_chart_selectors(analyzer)
    method_params = render_method_params_sidebar(method)

    outliers = get_outliers_for_selection(analyzer, df, method, mine, method_params)

    fig = get_chart(df, outliers, mine, chart_type, trend_degree)
    st.pyplot(fig)

    render_report_config_and_button(analyzer, df)


main()

