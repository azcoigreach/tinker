import click
from tinker.cli import pass_environment
import tinker.configs.mongodb
from pymongo import MongoClient
import pprint
from datetime import datetime, timedelta
import json
import string
import math
import time
import random
import pickle
from colorama import Fore



@click.option('--refresh', '-r', default=None, type=int,
              help='Refresh value in seconds')
@click.option('--tz_offset', '-tz', default=0, type=int,
              help='Time Zone offset (db times are GMT)')
@click.option('--offset', '-o', default=None, type=int,
              help='Time frame of query - X hours offset before end_time')
@click.option('--end_time', '-e', default=None,
              help='Query start datetime "2018-02-19 16:20"')
@click.option('--start_time', '-s', default=None,
              help='Query start datetime "2018-02-18 16:20"')
@click.option('--limit', '-l', default=10,
              help='Limit query results')
@click.group()
@pass_context
def cli(ctx, offset, end_time, start_time, limit, tz_offset, refresh):
    '''Query Twitter Database'''
    ctx.end_time = end_time
    ctx.start_time = start_time
    ctx.limit = limit
    ctx.refresh = refresh
    ctx.tz_offset = tz_offset
    ctx.offset = offset

@pass_context
def calc_datetime(ctx):

    ctx.vlog(Fore.LIGHTMAGENTA_EX + 'Datetime Options')

    if ctx.end_time == None:
        ctx.end_dt = (datetime.now() + timedelta(hours=ctx.tz_offset))
        
    else:
        try:
            ctx.end_dt = datetime.strptime(ctx.end_time, '%Y-%m-%d %H:%M')
        except ValueError as ve:
            ctx.log(Fore.LIGHTRED_EX + 'Error: %s', ve)
            sys.exit(-1)
    if (ctx.offset == None) and (ctx.start_time == None):
        ctx.offset = 24
        ctx.start_dt = (ctx.end_dt - timedelta(hours=ctx.offset))
    elif (ctx.offset != None) and (ctx.start_time != None):
        ctx.log('Can not use OFFSET and START_TIME together. Pick one.')
        sys.exit(-1)
    elif (ctx.offset != None):
        ctx.start_dt = (ctx.end_dt - timedelta(hours=ctx.offset))
    elif (ctx.start_time != None):
        try:
            ctx.start_dt = datetime.strptime(ctx.start_time, '%Y-%m-%d %H:%M')
        except ValueError as ve:
            ctx.log(Fore.LIGHTRED_EX + 'Error: %s', ve)
            sys.exit(-1)
    
    ctx.vlog(Fore.LIGHTGREEN_EX + 'Limit: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.limit)
    ctx.vlog(Fore.LIGHTGREEN_EX + 'End Time: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.end_dt)
    ctx.vlog(Fore.LIGHTGREEN_EX + 'Start Time: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.start_dt)
    ctx.vlog(Fore.LIGHTGREEN_EX + 'Offset: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.offset)
    ctx.vlog(Fore.LIGHTGREEN_EX + 'TZ Offset: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.tz_offset)
    ctx.vlog(Fore.LIGHTGREEN_EX + 'Refresh: ' + Fore.LIGHTYELLOW_EX + '%s', ctx.refresh)

@pass_context
def process_time(item):
    time.sleep(1)

def show_item(item):
    if item is not None:
        return '%d' % item

@cli.command('top_users', short_help='top_users stuff')
@pass_context
def top_users(ctx):
    '''Query top users doc!!!'''

    try:
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'Top Users')
        
        client_host = data_tools.configs.mongodb.MONGO_HOST
        client_port = data_tools.configs.mongodb.MONGO_PORT
        client_db = data_tools.configs.mongodb.MONGO_DB
        client_col = data_tools.configs.mongodb.MONGO_COL
        
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Host: ' + Fore.LIGHTYELLOW_EX + '%s', client_host)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Port: ' + Fore.LIGHTYELLOW_EX + '%s',client_port)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'DB: ' + Fore.LIGHTYELLOW_EX + '%s',client_db)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Collection: ' + Fore.LIGHTYELLOW_EX + '%s',client_col)

        client = MongoClient(client_host, client_port)
        db = client[client_db]
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'MongoDB connected...')

    except Exception as err:
        ctx.log(err)
    
    def get_top_users():
        query = db[client_col].aggregate([
                {'$match': {'created_at': {'$gte': ctx.start_dt,
                                        '$lte': ctx.end_dt}}},
                {'$group': {'_id': '$user.screen_name',
                            'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit' : ctx.limit}])
        
        users = []
        with open(ctx.home + '/top_users.pickle', 'wb') as f:
                
            try: 
                for i in iter(query):
                    ctx.log(Fore.LIGHTRED_EX + i['_id'] + ' : ' + str(i['count']))
                    users.append(i)
                
                pickle.dump(users, f)

            except TypeError as te:
                ctx.log(Fore.LIGHTRED_EX + 'Error: %s', te)
                ctx.log(Fore.LIGHTYELLOW_EX + '***')
                ctx.log(Fore.LIGHTCYAN_EX + query)

    if ctx.refresh == None:
        calc_datetime(ctx)
        get_top_users()
    else:
        while True:
            calc_datetime(ctx)
            get_top_users()           
            with click.progressbar(iterable=None, length=ctx.refresh, label='Refresh Time',
                                   show_eta=False, show_percent=False, show_pos=True,
                                   item_show_func=None,
                                   bar_template='%(label)s  %(bar)s | %(info)s',
                                   fill_char=click.style(u'#', fg='cyan'),
                                   empty_char=' ') as bar:
                for item in bar:
                    process_time(item)

@cli.command('top_hashtags', short_help='top_hashtags stuff')
@pass_context
def top_hashtags(ctx):
    '''Query top hashtags doc!!!'''

    try:
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'Top Hashtags')
        
        client_host = data_tools.configs.mongodb.MONGO_HOST
        client_port = data_tools.configs.mongodb.MONGO_PORT
        client_db = data_tools.configs.mongodb.MONGO_DB
        client_col = data_tools.configs.mongodb.MONGO_COL
        
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Host: ' + Fore.LIGHTYELLOW_EX + '%s', client_host)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Port: ' + Fore.LIGHTYELLOW_EX + '%s',client_port)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'DB: ' + Fore.LIGHTYELLOW_EX + '%s',client_db)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Collection: ' + Fore.LIGHTYELLOW_EX + '%s',client_col)

        client = MongoClient(client_host, client_port)
        db = client[client_db]
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'MongoDB connected...')

    except Exception as err:
        ctx.log(err)
    
    def get_top_hashtags():
        query = db[client_col].aggregate([
                {'$match': {'created_at': {'$gte': ctx.start_dt,
                                        '$lte': ctx.end_dt}}},
                {'$unwind': '$entities.hashtags'},
                {'$group': {'_id': '$entities.hashtags.text',
                            'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit' : ctx.limit}])
        
        users = []
        with open(ctx.home + '/top_hashtags.pickle', 'wb') as f:
                
            try: 
                for i in iter(query):
                    ctx.log(Fore.LIGHTRED_EX + i['_id'] + ' : ' + str(i['count']))
                    users.append(i)
                
                pickle.dump(users, f)

            except TypeError as te:
                ctx.log(Fore.LIGHTRED_EX + 'Error: %s', te)
                ctx.log(Fore.LIGHTYELLOW_EX + '***')
                ctx.log(Fore.LIGHTCYAN_EX + query)

    if ctx.refresh == None:
        calc_datetime(ctx)
        get_top_hashtags()
    else:
        while True:
            calc_datetime(ctx)
            get_top_hashtags()           
            with click.progressbar(iterable=None, length=ctx.refresh, label='Refresh Time',
                                   show_eta=False, show_percent=False, show_pos=True,
                                   item_show_func=None,
                                   bar_template='%(label)s  %(bar)s | %(info)s',
                                   fill_char=click.style(u'#', fg='cyan'),
                                   empty_char=' ') as bar:
                for item in bar:
                    process_time(item)

@cli.command('top_mentions', short_help='top_mentions stuff')
@pass_context
def top_mentions(ctx):
    '''Query top mentions doc!!!'''

    try:
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'Top Mentions')
        
        client_host = data_tools.configs.mongodb.MONGO_HOST
        client_port = data_tools.configs.mongodb.MONGO_PORT
        client_db = data_tools.configs.mongodb.MONGO_DB
        client_col = data_tools.configs.mongodb.MONGO_COL
        
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Host: ' + Fore.LIGHTYELLOW_EX + '%s', client_host)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Port: ' + Fore.LIGHTYELLOW_EX + '%s',client_port)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'DB: ' + Fore.LIGHTYELLOW_EX + '%s',client_db)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Collection: ' + Fore.LIGHTYELLOW_EX + '%s',client_col)

        client = MongoClient(client_host, client_port)
        db = client[client_db]
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'MongoDB connected...')

    except Exception as err:
        ctx.log(err)
    
    def get_top_mentions():
        query = db[client_col].aggregate([
                {'$match': {'created_at': {'$gte': ctx.start_dt,
                                        '$lte': ctx.end_dt}}},
                {'$unwind': '$entities.user_mentions'},
                {'$group': {'_id': '$entities.user_mentions.screen_name',
                            'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit' : ctx.limit}])
        
        users = []
        with open(ctx.home + '/top_mentions.pickle', 'wb') as f:
                
            try: 
                for i in iter(query):
                    ctx.log(Fore.LIGHTRED_EX + i['_id'] + ' : ' + str(i['count']))
                    users.append(i)
                
                pickle.dump(users, f)

            except TypeError as te:
                ctx.log(Fore.LIGHTRED_EX + 'Error: %s', te)
                ctx.log(Fore.LIGHTYELLOW_EX + '***')
                ctx.log(Fore.LIGHTCYAN_EX + query)

    if ctx.refresh == None:
        calc_datetime(ctx)
        get_top_mentions()
    else:
        while True:
            calc_datetime(ctx)
            get_top_mentions()           
            with click.progressbar(iterable=None, length=ctx.refresh, label='Refresh Time',
                                   show_eta=False, show_percent=False, show_pos=True,
                                   item_show_func=None,
                                   bar_template='%(label)s  %(bar)s | %(info)s',
                                   fill_char=click.style(u'#', fg='cyan'),
                                   empty_char=' ') as bar:
                for item in bar:
                    process_time(item)

@cli.command('count', short_help='count tweets in db')
@pass_context
def count(ctx):
    '''count tweets in db'''
    
    # connect_db()

    try:
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'Count Tweets')
        
        client_host = data_tools.configs.mongodb.MONGO_HOST
        client_port = data_tools.configs.mongodb.MONGO_PORT
        client_db = data_tools.configs.mongodb.MONGO_DB
        client_col = data_tools.configs.mongodb.MONGO_COL
        
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Host: ' + Fore.LIGHTYELLOW_EX + '%s', client_host)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Port: ' + Fore.LIGHTYELLOW_EX + '%s', client_port)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'DB: ' + Fore.LIGHTYELLOW_EX + '%s', client_db)
        ctx.vlog(Fore.LIGHTCYAN_EX + 'Collection: ' + Fore.LIGHTYELLOW_EX + '%s', client_col)

        client = MongoClient(client_host, client_port)
        db = client[client_db]
        ctx.vlog(Fore.LIGHTMAGENTA_EX + 'MongoDB connected...')

    except Exception as err:
        ctx.log(Fore.LIGHTRED_EX + 'Error: %s', err)
    
    def get_count():
        query = db[client_col].find({'created_at': {'$gte': ctx.start_dt,
                                                    '$lte': ctx.end_dt}}).count()
        
        
        with open(ctx.home + '/count.pickle', 'wb') as f:
            try: 
                ctx.log(Fore.LIGHTRED_EX + 'count: ' + Fore.LIGHTYELLOW_EX + '%s', query)
                pickle.dump(query, f)
            except TypeError as te:
                ctx.log(Fore.LIGHTRED_EX + 'Error: %s', te)
                ctx.log(Fore.LIGHTYELLOW_EX + '***')
                ctx.log(Fore.LIGHTCYAN_EX + query)

    if ctx.refresh == None:
        calc_datetime(ctx)
        get_count()
    else:
        while True:
            calc_datetime(ctx)
            get_count()
            with click.progressbar(iterable=None, length=ctx.refresh, label='Refresh Time',
                                   show_eta=False, show_percent=False, show_pos=True,
                                   item_show_func=None,
                                   bar_template='%(label)s  %(bar)s | %(info)s',
                                   fill_char=click.style(u'#', fg='cyan'),
                                   empty_char=' ') as bar:
                for item in bar:
                    process_time(item)