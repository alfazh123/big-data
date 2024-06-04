from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2 import Error

TOPIC_NAME = 'my_favorite_topic'
consumer = KafkaConsumer(TOPIC_NAME)

for msg in consumer:
    print(json.loads(msg.value))
    # data = json.loads(msg.value)
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="adekkoko",
            host="127.0.0.1",
            database="postgres"
        )
        
        cursor = connection.cursor()
        
        data = json.loads(msg.value)
        
        create_table_stocks = """ CREATE TABLE IF NOT EXISTS stocks(
                                        date DATE NOT NULL PRIMARY KEY,
                                        open_price DECIMAL(10,4) NOT NULL,
                                        high_price DECIMAL(10,4) NOT NULL,
                                        low_price DECIMAL(10,4) NOT NULL,
                                        close_price DECIMAL(10,4) NOT NULL,
                                        volume INTEGER NOT NULL
                                        ) """
        
        cursor.execute(create_table_stocks)
        connection.commit()
        print("Table created")
        
        
        for date, items in data["Time Series (Daily)"].items():
            
            insert_data = """ 
                            INSERT INTO stocks (date, open_price, high_price, low_price, close_price, volume)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (date) DO NOTHING
                            """
            item_insert = (date, items['1. open'], items['2. high'], items['3. low'], items['4. close'], items['5. volume'])
            cursor.execute(insert_data, item_insert)
            connection.commit()
        
    except (Exception, Error) as e:
        print("Error While connecting to Postgres", e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Postgres connection is close")