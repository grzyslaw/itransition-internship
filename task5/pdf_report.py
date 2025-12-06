from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import io
from analysis import MineStatsAnalyzer
from visualize import get_chart
import pandas as pd
import numpy as np

def draw_table(ax, title:str, df:pd.DataFrame):
    ax.axis('off')
    ax.set_title(title, pad=20)
    if isinstance(df, pd.Series):
        df = df.to_frame().T
    if df.empty:
        ax.text(0.5, 0.5, "No anomalies detected", ha="center", va="center")
    else:
        cellText = []
        for row in df.itertuples(index=False):
            formatted_row = []
            for v in row:
                if isinstance(v, (int, float, np.number)):
                    formatted_row.append(round(v, 3))
                elif isinstance(v, pd.Timestamp):
                    formatted_row.append(v.strftime("%Y-%m-%d"))
                else:
                    formatted_row.append(str(v))
            cellText.append(formatted_row)
        ax.table(
            cellText=cellText,
            rowLabels=df.index,
            colLabels=df.columns,
            loc='center'
        )

def draw_bar_anomalies(ax, title:str, method_names:list, counts:list):
    ax.bar(method_names, counts)
    ax.set_title(title, pad=20)
    ax.set_ylabel('Count')
    for i,c in enumerate(counts):
        ax.text(i, c, str(c), ha='center', va='bottom')

def generate_summary_page(analyzer:MineStatsAnalyzer, outliers_by_method:dict):
    stats = analyzer.get_descriptive_statistics()
    methods = list(outliers_by_method.keys())
    anomaly_counts = []
    for m in methods:
        anomaly_counts.append(len(outliers_by_method[m]))
    fig, (ax_table, ax_bar) = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(10,8)
    )
    draw_table(ax_table, 'Descriptive statistics – all mines + Total', stats)
    draw_bar_anomalies(ax_bar, 'Total anomalies detected per method', methods, anomaly_counts)
    return fig
    
def generate_mine_overview_page(analyzer:MineStatsAnalyzer, outliers_by_method:dict, mine:str):
    stats = analyzer.get_descriptive_statistics(mine)
    methods = list(outliers_by_method.keys())
    anomaly_counts = []
    for m in methods:
        anomaly_counts.append(len(outliers_by_method[m][outliers_by_method[m]["Mine"] == mine]))
    fig, (ax_table, ax_bar) = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(10,8)
    )
    draw_table(ax_table, f'Descriptive statistics - {mine}', stats)
    draw_bar_anomalies(ax_bar, f'Anomalies per method - {mine}', methods, anomaly_counts)
    return fig

def generate_anomaly_details_page(
    df: pd.DataFrame, 
    df_outliers: pd.DataFrame,
    mine: str, 
    method_name: str, 
    rows_per_page:int = 25
):
    df_out = df_outliers[df_outliers["Mine"] == mine].copy()
    pages = []
    
    if df_out.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        draw_table(ax, f'{mine} – {method_name} anomalies', df_out)
        pages.append(fig)
        return pages    
    
    median_val = df[mine].median()
    df_out["Type"] = np.where(df_out[mine] >= median_val, "Spike", "Drop")
    table_df = df_out[["Date", mine, "Type"]].copy()
    
    num_pages = (len(table_df) + rows_per_page - 1) // rows_per_page
    for page_idx in range(num_pages):
        start = page_idx * rows_per_page
        end = start + rows_per_page
        chunk = table_df.iloc[start:end]

        fig, ax = plt.subplots(figsize=(8, 6))
        draw_table(ax, f'{mine} – {method_name} anomalies (page {page_idx+1}/{num_pages})', chunk)
        pages.append(fig)

    return pages

def generate_mine_method_chart_page(
    df: pd.DataFrame, 
    outliers_df: pd.DataFrame, 
    mine: str, 
    method_name: str, 
    chart_type: str, 
    trend_degree: int
):    
    fig = get_chart(
        df,
        outliers_df,
        mine=mine,
        chart_type=chart_type,
        trend_degree=trend_degree,
    )
    fig.axes[0].set_title(f"{mine} – {method_name} ({chart_type}, deg={trend_degree})")
    return fig

def generate_pdf_report(
    analyzer: MineStatsAnalyzer,
    df: pd.DataFrame,
    iqr_params: dict,
    z_params: dict,
    ma_params: dict,
    grubbs_params: dict,
    chart_type: str = "bar",
    trend_degree: int = 2,
):
    mines = analyzer.get_all_mines()
    outliers_by_method = analyzer.get_all_outliers_by_method(
        iqr_params=iqr_params,
        z_params=z_params,
        ma_params=ma_params,
        grubbs_params=grubbs_params,
    )

    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        fig = generate_summary_page(analyzer, outliers_by_method)
        pdf.savefig(fig)
        plt.close(fig)

        for mine in mines:
            fig = generate_mine_overview_page(analyzer, outliers_by_method, mine)
            pdf.savefig(fig)
            plt.close(fig)

            for method_name, out_df in outliers_by_method.items():
                fig = generate_mine_method_chart_page(
                    df,
                    out_df,
                    mine,
                    method_name,
                    chart_type=chart_type,
                    trend_degree=trend_degree,
                )
                pdf.savefig(fig)
                plt.close(fig)

                pages = generate_anomaly_details_page(df, out_df, mine, method_name)
                for fig in pages:
                    pdf.savefig(fig)
                    plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()


