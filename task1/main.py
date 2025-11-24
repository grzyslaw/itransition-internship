import re
import json
import psycopg2
from dotenv import load_dotenv 
import os

load_dotenv()
dsn = f"dbname={os.getenv("DATABASE")} user={os.getenv("USER")} password={os.getenv("PASSWORD")} host={os.getenv("HOST")}"

def fix_json_and_get_data(path_to_file):
    with open(path_to_file) as f:
        s = f.read()

    #take whatever is in between ':' and '=>', put it in quotes and ad ':'
    result = re.sub(r':(.*?)=>', r'"\1":', s)

    data = json.loads(result)
    return data

def create_tables_and_insert_data(data):
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            #create tables
            cur.execute(
                """
                create table book (
                    id numeric primary key,
                    title text,
                    author text,
                    genre text,
                    publisher text,
                    year numeric(4) not null,
                    price text not null
                );

                create table summary (
                    publication_year numeric(4) primary key,
                    book_count numeric,
                    avarage_price_usd numeric(3,2)
                );
                """
            )
            #insert books
            for d in data:
                cur.execute(
                    """
                    insert into book (id, title, author, genre, publisher, year, price)
                    values(%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (d['id'], d['title'], d['author'], d['genre'], d['publisher'], d['year'], d['price'])
                )

            #process the data and insert into summary
            cur.execute(
                """
                with final_prices as (
                    select id, price, year,
                    case
                        when price like '$%' then to_number(substring(price,2), '999999.99')
                        else to_number(substring(price,2), '999999.99') * 1.2
                    end as price_formated
                    from book
                )
                insert into summary(publication_year, book_count, avarage_price_usd)
                (
                    select 
                        year,
                        count(id),
                        round(avg(price_formated), 2)
                    from final_prices
                    group by year
                );
                """
            )

data = fix_json_and_get_data('./task1_d.json')
create_tables_and_insert_data(data)