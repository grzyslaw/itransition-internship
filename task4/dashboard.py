import streamlit as st
import matplotlib.pyplot as plt
from processing import get_report_data

st.title('Task 4 BI dashboard')

def get_daily_revenue_chart(daily_revenue):
    ticks = daily_revenue.index[::50]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(daily_revenue.index, daily_revenue.values)
    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue')
    ax.set_title('Daily Revenue')
    ax.set_xticks(ticks)
    fig.autofmt_xdate()
    return fig

def render_tab(
        top_5_days_by_revenue,
        num_unique_users,
        num_unique_authors,
        most_popular_author,
        best_buyer,
        daily_revenue
):
    st.subheader('Key metrics')
    col1, col2 = st.columns(2)
    with col1:
        st.metric('**Number of unique users:**', num_unique_users)
    with col2:
        st.metric('**Unique sets of authors:**', num_unique_authors)

    col3, col4 = st.columns(2)
    with col3:
        st.write('**Most popular author(s):**')
        for a in most_popular_author:
            st.write(a)
    with col4:
        st.write('**Top customer by spending:**')
        st.write(best_buyer['name'])
        for id in best_buyer['ids']:
            st.write(f'ids: {id}')
    
    st.markdown('---')
    st.subheader('Top 5 Days by revenue (YYYY-MM-DD)')
    st.table(top_5_days_by_revenue)
    
    

    st.markdown('---')
    st.subheader('Daily revenue chart')
    st.pyplot(get_daily_revenue_chart(daily_revenue))

tab1, tab2, tab3 = st.tabs(['DATA1', 'DATA2', 'DATA3'])


with tab1:
    render_tab(*get_report_data(dataset_folder_number=1))
with tab2:
    render_tab(*get_report_data(dataset_folder_number=2))
with tab3:
    render_tab(*get_report_data(dataset_folder_number=3))

