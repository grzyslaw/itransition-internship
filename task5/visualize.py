import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def prepare_series(df:pd.DataFrame, mine:str):
    x_dates = df['Date'].copy()
    x_numeric = np.arange(len(df))
    y = df[mine].copy()
    return df.copy(), x_dates, x_numeric, y

def get_outliers_for_mine(df:pd.DataFrame, mine:str):
    return df[df['Mine'] == mine].copy()

def compute_trendline(x:np.ndarray, y:np.ndarray, degree:int):
    if degree == 0:
        return None
    model = np.poly1d(np.polyfit(x,y,degree))
    return model(x)

def apply_trendline(ax, x_dates, y):
    ax.plot(x_dates, y, linestyle='--', color='red', linewidth=3, label = "Trendline")

def apply_chart_by_type(ax, x_dates, y, df, df_outliers, chart_type, mine):
    if chart_type == 'line':
        ax.plot(x_dates, y, label=mine)
        if not df_outliers.empty:
            ax.scatter(df_outliers['Date'], df_outliers[mine], label='Outliers')
    elif chart_type == 'bar':
        ax.bar(x_dates, y, width=1, label=mine)
        if not df_outliers.empty:
            ax.bar(df_outliers['Date'], df_outliers[mine], width=1, label='Outliers')
    elif chart_type == 'stacked':
        is_outlier = df['Date'].isin(df_outliers['Date'])
        moving_avg = df[mine].rolling(window=7, min_periods=1).mean().values
        is_spike = is_outlier & (y > moving_avg)
        is_drop = is_outlier & (y < moving_avg)

        baseline = np.where(is_spike, moving_avg, y)
        spike_component = np.where(is_spike, y - moving_avg, 0.0)
        
        ax.bar(x_dates, baseline, width=1.0, label="Baseline / normal")
        ax.bar(x_dates, spike_component, bottom=baseline, width=1.0, label="Spike above 7d MA")
        if is_drop.any():
            ax.bar(x_dates[is_drop], y[is_drop], width=1.0, label="Drop vs 7d MA",linewidth=0.8)
    else:
        raise ValueError('chart type must be: line, bar or stacked')

def get_chart(df:pd.DataFrame, df_outliers:pd.DataFrame, mine:str, chart_type:str='line', trend_degree:int=0):
    df_plot, x_dates, x_numeric, y = prepare_series(df, mine)
    df_out = get_outliers_for_mine(df_outliers, mine)
    trend = compute_trendline(x_numeric, y, trend_degree)
    trend_text = ''

    fig, ax = plt.subplots(figsize=(16,8))
    apply_chart_by_type(ax, x_dates, y, df_plot, df_out, chart_type, mine)
    if trend is not None:
        trend_text = f' + trend (polynomial of degree = {trend_degree})'
        apply_trendline(ax, x_dates, trend)
    title = f'{mine} - {chart_type} chart with outliers' + trend_text

    ax.set_title(title)
    ax.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel('Output')
    fig.autofmt_xdate()
    # fig.tight_layout()
    return fig
    
