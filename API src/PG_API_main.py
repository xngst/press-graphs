"""
#############################################################
PressGraphs API
#############################################################
Endpoints:
    /date/list/<search_word>/<substring_match>/<start_date>/<end_date>/<site>
    /date/count/<search_word>/<substring_match>/<start_date>/<end_date>/<site>
    /info/sites/all
    /info/dates/first
    /info/dates/last
    /info/sites/exists/<site>
"""
#############################################################
# IMPORTS
#############################################################

import configparser
import uuid
import mysql.connector
from functools import lru_cache
from flask import Flask, jsonify
#from flask_cors import CORS

config = configparser.ConfigParser()
config.read("/home/pg_config.ini") #define your own credentials here

#############################################################
# DEFINITIONS
#############################################################

def make_conn():
    """
    #connects to local mysql db
    """
    conn = mysql.connector.connect(
        host=<HOST>, #add your own host here
        user=config["mysql_db"]["user"],
        password=config["mysql_db"]["password"],
        database=config["mysql_db"]["database"])
    return conn

def api_key_exists(api_key:str) -> bool:
    """
    checks if api_key exists in user table
    """
    conn = make_conn()
    cur = conn.cursor()
    query = "SELECT EXISTS(SELECT * FROM user where api_key=%s)"
    cur.execute(query, (api_key,))
    res = cur.fetchone()
    if res[0] == 1:
        return True

#############################################################
# APP INSTANINATION
#############################################################

app = Flask(__name__)
#CORS(app)

#############################################################
# ROOT
#############################################################

@app.route('/')
def index():
    """
    #tests connectivity to local mysql database
    """
    conn = make_conn()
    if conn:
        return "conn ok"

    return "no conn"

#############################################################
# CREATE USER AND GET API KEY
#############################################################
#/create/username

@app.route("/create/<username>")
def create(username):
    """
    creates user and apy key if user not exists
    """
    conn = make_conn()
    cur = conn.cursor(buffered=True)
    query = "SELECT EXISTS(SELECT * FROM user WHERE user=%s)"
    cur.execute(query, (username,))
    res = cur.fetchone()

    if res[0] == 0:
        api_key = str(uuid.uuid4())[:10]
        query = """INSERT INTO user (user,api_key)
        VALUES (%s, %s)"""
        val = (username, api_key,)
        cur.execute(query, val)
        conn.commit()
        return jsonify({"user":username,"api key":api_key})

    return jsonify({"message": "username already exists",
    "status_code": 404})

#############################################################
# L I S T
#############################################################
#/api_key/date/list/search_word/substring_match/start_date/end_date/site

@app.route("/date/list/<api_key>/<search_word>/<substring_match>/<start_date>/<end_date>/<site>")
#@lru_cache(maxsize = 16)
def date_list(*,
              api_key: str,
              start_date: str,
              end_date: str,
              site: str,
              search_word: str,
              substring_match: str):
    """
    #todo
    """

    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    if search_word:
        search_word = search_word.split()[0]
        search_word = search_word.lower()
        if substring_match == "1":
            search_word = f"%{search_word}%"
        else:
            search_word = f"% {search_word} %"
    else:
        return print("no search_word provided")

    if start_date:
        start_date = start_date.split()[0]
    else:
        return print("no start_date provided")

    if end_date:
        end_date = end_date.split()[0]
    else:
        return print("no end_date provided")

    conn = make_conn()
    cur = conn.cursor(buffered=True)

    if site == "all":
        query = """SELECT date, site, title, url
            FROM news_table_2
            WHERE news_table_2.date BETWEEN %s AND %s
            AND LOWER(news_table_2.title) LIKE %s
            ORDER BY news_table_2.date ASC,
                     news_table_2.site ASC,
                     news_table_2.title ASC
            """
        cur.execute(query, (start_date, end_date, search_word, ))

    else:
        site = site.split()[0]
        site = site.lower()
        query = """SELECT date, site, title, url
            FROM news_table_2
            WHERE news_table_2.date BETWEEN %s AND %s
            AND news_table_2.site = %s
            AND LOWER(news_table_2.title) LIKE %s
            ORDER BY news_table_2.date ASC,
                     news_table_2.site ASC,
                     news_table_2.title ASC
            """
        cur.execute(query, (start_date, end_date, site, search_word, ))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({"date": str(row[0]),
                      "site": row[1],
                      "title": row[2],
                      "url": row[3]})

    fields = {"fields":[{"date": "type: string (YYYY-MM-DD)"},
                        {"site": "type: string"},
                        {"title": "type: string"},
                        {"url": "type: string"}]}

    result_json = jsonify([{"schema": fields}, {"data": items}])

    return result_json

#############################################################
# C O U N T
#############################################################
#/api_key/date/count/search_word/substring_match/start_date/end_date/site

@app.route("/date/count/<api_key>/<search_word>/<substring_match>/<start_date>/<end_date>/<site>")
#@lru_cache(maxsize = 16)
def date_count(*,
               api_key: str,
               start_date: str,
               end_date: str,
               site: str,
               search_word: str,
               substring_match: str):

    """
    #todo
    """

    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    if search_word:
        search_word = search_word.split()[0]
        search_word = search_word.lower()
        if substring_match == "1":
            search_word = f"%{search_word}%"
        else:
            search_word = f"% {search_word} %"
    else:
        return print("no search_word provided")

    if start_date:
        start_date = start_date.split()[0]
    else:
        return print("no start_date provided")

    if end_date:
        end_date = end_date.split()[0]
    else:
        return print("no end_date provided")

    conn = make_conn()
    cur = conn.cursor(buffered=True)

    if site == "all":
        query = """SELECT date, COUNT(title) as count
        FROM news_table_2
        WHERE news_table_2.date BETWEEN %s AND %s
        AND LOWER(news_table_2.title) like %s
        GROUP BY news_table_2.date
        ORDER by news_table_2.date ASC
        """
        cur.execute(query, (start_date, end_date, search_word,))

    else:
        site = site.split()[0]
        site = site.lower()
        query = """SELECT date, COUNT(title) as count
        FROM news_table_2
        WHERE news_table_2.date BETWEEN %s AND %s
        AND news_table_2.site = %s
        AND LOWER(news_table_2.title) like %s
        GROUP BY news_table_2.date
        ORDER by news_table_2.date ASC,
                 news_table_2.site ASC
        """
        cur.execute(query, (start_date, end_date, site, search_word,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({"date": str(row[0]),
                      "count": row[1]})

    fields = {"fields":[{"date": "type: string (YYYY-MM-DD)"},
    {"count": "type: integer"}]}

    result_json = jsonify([{"schema": fields}, {"data": items}])

    return result_json

#############################################################
# I N F O
#############################################################
#/api_key/info/sites/all
#/api_key/info/sites/exists/site
#/api_key/info/dates/first
#/api_key/info/dates/last

@app.route("/<api_key>/info/sites/all")
@lru_cache(maxsize = 16)
def all_sites(api_key: str) -> str:
    """
    list of all sites contained in database
    """

    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    conn = make_conn()
    cur = conn.cursor(buffered=True)

    query = "SELECT EXISTS(SELECT * FROM user where api_key=%s)"
    cur.execute(query,(api_key,))
    res = cur.fetchone()
    if res[0] == 0:
        return jsonify({"message": "wrong api_key", "status_code": 404})

    query = """SELECT DISTINCT site
    FROM news_table_2
    ORDER by site ASC"""
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({"site": str(row[0])})

    fields = {"fields":[{"site": "type: string"}]}

    result_json = jsonify([{"schema": fields}, {"data": items}])
    return result_json

@app.route("/<api_key>/info/sites/exists/<site>")
@lru_cache(maxsize = 16)
def site_exists(api_key:str, site: str):
    """
    checks if site is contained in database
    returns 1 when site exists, otherwise returns 0
    """
    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    conn = make_conn()
    cur = conn.cursor(buffered=True)
    query = "SELECT EXISTS(SELECT * FROM news_table_2 where site=%s)"
    cur.execute(query, (site,))
    res = cur.fetchone()
    return jsonify({"exists": res[0]})

@app.route("/<api_key>/info/dates/first")
@lru_cache(maxsize = 16)
def min_date(api_key: str):
    """
    first date contained in database
    """
    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    conn = make_conn()
    cur = conn.cursor(buffered=True)
    query = """SELECT MIN(date) as max_date
    FROM news_table_2
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({"date": str(row[0])})

    fields = {"fields":[{"date": "type: string (YYYY-MM-DD)"}]}

    result_json = jsonify([{"schema": fields}, {"data": items}])
    return result_json

@app.route("/<api_key>/info/dates/last")
@lru_cache(maxsize = 16)
def max_date(api_key: str):
    """
    returns last date contained in database
    """
    if not api_key_exists(api_key):
        return jsonify({"message": "wrong api_key", "status_code": 404})

    conn = make_conn()
    cur = conn.cursor(buffered=True)
    query = """SELECT MAX(date) as max_date
    FROM news_table_2
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = []
    for row in rows:
        items.append({"date": str(row[0])})

    fields = {"fields":[{"date": "type: string (YYYY-MM-DD)"}]}

    result_json = jsonify([{"schema": fields}, {"data": items}])
    return result_json



