import click
from tinker.cli import pass_environment
import tinker.configs.mongodb
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import string
import math
import time
import random
import pickle


@click.group()
@pass_environment
def cli(ctx):
    '''MongoDB Tools'''
    # try:
    client_host = tinker.configs.mongodb.MONGO_HOST
    client_port = tinker.configs.mongodb.MONGO_PORT
    client_db = tinker.configs.mongodb.MONGO_DB
    client_col = tinker.configs.mongodb.MONGO_COL

    client = MongoClient(client_host, client_port)
    ctx.db = client[client_db]
    ctx.collection = ctx.db[client_col]
    ctx.log(click.style('MongoDB Connected', bg='blue', fg='white'))

@cli.command('post', short_help='post entry')
@pass_environment
def post(ctx):
    '''post items in collection'''
    post = {
        "text": "Hello World",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.utcnow()
        }
    post_id = ctx.collection.insert_one(post).inserted_id
    ctx.log(post_id)

@cli.command('count', short_help='count entries')
@pass_environment
def count(ctx):
    '''count items in collection'''
    # log(ctx.db.list_collection_names())
    
@cli.command('collections', short_help='list collections')
@pass_environment
def count(ctx):
    '''count items in collection'''
    ctx.log(ctx.db.list_collection_names())
