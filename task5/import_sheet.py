import pandas as pd

def import_data_from_google_sheets(url:str, tab:int):
    url_clean, _ = url.rsplit('/', 1)
    url_export = f'{url_clean}/export?format=csv&gid={tab}'
    df = pd.read_csv(url_export)
    return df

def preprocess_data(df:pd.DataFrame):
    for col in df.columns:
        if col == 'Date':
            df[col] = pd.to_datetime(df[col])
        else:
            df[col] = df[col].str.replace(',', '.').astype(float)
    df['total'] = df.sum(axis=1, numeric_only=True)
    return df

def get_data(url:str, tab:int=31299030):
    return preprocess_data(import_data_from_google_sheets(url,tab))
