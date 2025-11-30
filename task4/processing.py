import pandas as pd
import yaml
import re
from dateutil import parser


# ---- Helper functions ----
def import_data(csv_file, parquet_file, yaml_file):
    df_users = pd.read_csv(csv_file)
    df_orders = pd.read_parquet(parquet_file)
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    df_books = pd.DataFrame(data)
    df_books.columns = [c.lstrip(':') for c in df_books.columns]
    return df_users, df_orders, df_books

def string_extract_numbers(s:str):
    return re.sub(r'[^0-9]','',s)

def string_extract_numbers_decimals(s:str):
    matched = re.search(r'([0-9]+)\D+([0-9]+)', s)
    if matched:
        return f"{matched.group(1)}.{matched.group(2)}"
    else:
        return string_extract_numbers(s)

def string_extract_currency(s:str):
    usd_aliases = ['usd','$']
    isUSD = any(alias in s.lower() for alias in usd_aliases)
    return 'usd' if isUSD else 'eur'

def convert_EUR_USD(eur):
    return eur * 1.2

def get_paid_price(unit_price:str, quantity):
    num = float(string_extract_numbers_decimals(unit_price))
    curr = string_extract_currency(unit_price)
    converted = num if curr == 'usd' else convert_EUR_USD(num)
    return quantity * converted

def extract_date_from_timestamp(t:str):
    matched = re.search(r'(\d{1,4}[-/][a-zA-Z0-9]{1,9}[-/]\d{1,4})', t)
    if not matched:
        dt = parser.parse(t)
    else:
        dt = pd.to_datetime(matched.group(1), errors='raise')
    return dt.strftime('%Y-%m-%d')

def deduplicate_users_by_phone(df:pd.DataFrame):
    df = df.groupby('phone')
    df = df.agg({
        'name':'first',
        'address':'first',
        'email':'first',
        'id': lambda x: list(x)
    })
    df = df.reset_index()
    df = df.rename(columns={'id': 'original_ids'})
    return df


# ---- Preprocessing ----
def preprocess_users_df(df:pd.DataFrame):
    df['phone'] = df['phone'].apply(string_extract_numbers)
    df = deduplicate_users_by_phone(df)
    return df

def preprocess_orders_df(df:pd.DataFrame):
    df['paid_price'] = df.apply(
        lambda row: get_paid_price(row['unit_price'], row['quantity']),
        axis=1
    )
    df['date'] = df['timestamp'].apply(extract_date_from_timestamp)
    df = df.drop_duplicates(subset=['user_id','book_id','date'])
    return df    

def preprocess_books_df(df:pd.DataFrame):
    df['authors_set_sorted'] = df['author'].str.split(',').apply(
        lambda list: tuple(sorted(a.strip() for a in list))
    )
    df = df.drop_duplicates(subset=['title','author','year','publisher'])
    return df

# ---- Queries ----
def get_unique_users(df:pd.DataFrame):
    return len(df)

def get_top_5_days_by_revenue(df:pd.DataFrame):
    result = (
        df.groupby('date')['paid_price']
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    result = result.rename('Revenue')
    result.index.name = 'Date'
    return result

def get_unique_sets_of_authors(df:pd.DataFrame):
    result = df['authors_set_sorted'].nunique()
    return result

def get_most_popular_author(df_books:pd.DataFrame, df_orders:pd.DataFrame):
    bestseller_book_id = (
        df_orders.groupby('book_id')['quantity']
        .sum()
        .idxmax()
    )
    author = df_books.loc[df_books['id'] == bestseller_book_id, 'authors_set_sorted'].iloc[0]
    return author

def get_top_customer_by_spending(df_orders:pd.DataFrame, df_users:pd.DataFrame):
    top_spender_id = (
        df_orders.groupby('user_id')['paid_price']
        .sum()
        .idxmax()
    )
    top_spender_row = (
        df_users[df_users['original_ids'].apply(lambda ids: top_spender_id in ids)].iloc[0]
    )
    return {
        'name': top_spender_row['name'],
        'ids': top_spender_row['original_ids']
    }

def get_daily_revenue_series(df:pd.DataFrame):
    daily_revenue = (
        df.groupby('date')['paid_price']
        .sum()
        .sort_index()
    )
    return daily_revenue 

# ---- Data report -------
def get_report_data(dataset_folder_number):
    df_users, df_orders, df_books = import_data(
        f'./data/DATA{dataset_folder_number}/users.csv',
        f'./data/DATA{dataset_folder_number}/orders.parquet',
        f'./data/DATA{dataset_folder_number}/books.yaml'
    )
    df_users = preprocess_users_df(df_users)
    df_books = preprocess_books_df(df_books)
    df_orders = preprocess_orders_df(df_orders)
    return (
        get_top_5_days_by_revenue(df_orders), 
        get_unique_users(df_users), 
        get_unique_sets_of_authors(df_books), 
        get_most_popular_author(df_books, df_orders), 
        get_top_customer_by_spending(df_orders, df_users),
        get_daily_revenue_series(df_orders)
    )
    

