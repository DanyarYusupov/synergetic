from clickhouse_driver import Client
import pandas as pd
import datetime as dt
import time
import datetime


# def date_processing(x):
#     if x is not None:
#         x = (datetime.datetime.fromtimestamp(int(x), tz=datetime.timezone(datetime.timedelta(hours=3)))).strftime('%Y-%m-%d %H:%M:%S')
#     return pd.to_datetime(x, errors='coerce')



def get_24_hours_data(start, end):

    client = Client(host='81.163.23.152',
                port='9000',
                user='valiotti',
                password='valiotti')

    query = f"""
           SELECT itemId AS id,
                    ozon.search.name AS name, 
                    ozon.products.category as products_category,
                    search_string,
                    ozon.keywords.priority AS keywords_priority,
                    ozon.products.priority AS products_priority,
                    ozon.keywords.priority.category AS keywords_category,
                    update_time,
                    position,
                    toTimezone(FROM_UNIXTIME(update_time), 'Europe/Moscow') AS time,
                    toDayOfMonth(time) as day
            FROM ozon.search LEFT JOIN ozon.products ON ozon.search.itemId == ozon.products.id
                             LEFT JOIN ozon.keywords ON ozon.search.search_string == ozon.keywords.keyword 
            where update_time > {start} AND update_time < {end} AND searchStatus=='FOUND' 
            order by ozon.products.category, ozon.keywords.priority"""

    df = client.query_dataframe(query=query)

    #df['time'] = df['update_time'].apply(date_processing)


    return df

# def visibility():

#     client = Client(host='81.163.23.152',
#                 port='9000',
#                 user='valiotti',
#                 password='valiotti')

#     query = f"""
#            SELECT *, toTimezone(FROM_UNIXTIME(updated_at), 'Europe/Moscow') AS time,
#                  toDayOfMonth(time) as day
#             FROM ozon.visibility"""

#     df = client.query_dataframe(query=query)

#     df['time'] = df['updated_at'].apply(date_processing)


#     return df