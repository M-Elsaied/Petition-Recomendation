
import time
import json
import simplejson
import re
import tweepy
import time
import datetime
import requests
import signal
import csv
import ast
import sys
from pymongo import MongoClient
import oauth2
import oauth2 as oauth
import json
import sqlite3
from HTMLParser import HTMLParser
import twitter

# Twitter application credentials
consumer_key = 'MO4iVYUfjZwfAEWs4Op9rZIEU'
consumer_secret = 'zIfwJx1GpyDFVJkxwWeFXprKmgUaKj1fJIYaoznARjSezLlxn1'
access_token = '104254763-aN94ddj4uCaPOPlyG9k6mgcVKoZNXVYBR9Un3qWP'
access_token_secret = 'YykVrcdiN5K10WNhd5UxmoX2lcCcOlRuPqdFm3xCSl7r1'
twitter_handle='change'


consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
#client = oauth.Client(consumer, access_token)

client = MongoClient('mongodb://localhost:27017/')
client = MongoClient()
db = client.ClimateChange


allUsers = db.AllUsers
petitions = db.PetitionNewOpen
ratings = db.RatingNew
sampleUsers = db.UserNew
tweets=db.TweetsNew


timeline_endpoint = "https://api.twitter.com/1.1/statuses/home_timeline.json"
#response, data = client.request(timeline_endpoint)
db_file = "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/django/UserRatings/production/db.sqlite3"
try:
    conn = sqlite3.connect(db_file)
except Exception as e:
    print(e)

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def getGTUsers():
    #lang en, in, no, ht,tl

    # select user_id from GTapp_ratings where user_id in (85694830, 933968376682164224, 1126590570, 3017568426)
    sql= '''select distinct * from GTapp_ratings'''
    cur = conn.cursor()
    curU = conn.cursor()
    curI= conn.cursor()
    curR= conn.cursor()
    #cur.executemany('insert into GTapp_petition(petition_id,url,title) values (?,?,?)', (petition,))

    # insert ratings

    curR.execute('select * from GTapp_ratings')
    '''
    for rowr in curR:
        try:
            print '' \
                  ''
            post = {}
            # post['tweets'] = alltweets
            # post['tweets_details'] = outtweets
            post['sqliteID'] = rowr[0]
            post['GT'] = 1
            post['rating'] = rowr[1]
            post['petition_id'] = rowr[2]
            post['code'] = rowr[3]
            post['user_id'] = rowr[4]
            ratings.update({'$and': [{"user_id": int(rowr[2])}, {"petition_id": str(rowr[4])}]}, {"$set": post}, upsert=True)
        except Exception as e:
            print 'error in getting ratings of petition '+rowr[2]+'for user: ' + str(rowr[4])
            print(e)
    '''
    cur.execute('select distinct user_id from GTapp_ratings')
    for row in cur:
       # get user
        curU.execute('SELECT * FROM GTapp_twitteruser where id_str=?', (row[0],))
        for u in curU:
           try:
               print '' \
                     ''
               post = {}
               # post['tweets'] = alltweets
               # post['tweets_details'] = outtweets
               post['sqliteID'] = u[0]
               post['GT']=1
               post['id_str'] = u[1]
               post['ChangeFollower'] = u[2]
               post['CollectedTimeStamp'] = u[3]
               post['blocked_by'] = u[4]
               post['blocking'] = u[5]
               post['contributors_enabled'] = u[6]
               post['created_at'] = u[7]
               post['default_profile'] = u[8]
               post['default_profile_image'] = u[9]
               post['description'] = u[10]
               post['favourites_count'] = u[11]
               post['follow_request_sent'] = u[12]
               post['followers_count'] = u[13]
               post['following'] = u[14]
               post['friends_count'] = u[15]
               post['geo_enabled'] = u[16]
               post['has_extended_profile'] = u[17]
               post['is_translation_enabled'] = u[18]
               post['is_translator'] = u[19]
               post['lang'] = u[20]
               post['listed_count'] = u[21]
               post['live_following'] = u[22]
               post['location'] = u[23]
               post['muting'] = u[24]
               post['name'] = u[25]
               post['notifications'] = u[26]
               post['profile_background_color'] = u[27]
               post['profile_background_image_url'] = u[28]
               post['profile_background_image_url_https'] = u[29]
               post['profile_background_tile'] = u[30]
               post['profile_image_url'] = u[31]
               post['profile_image_url_https'] = u[32]
               post['profile_link_color'] = u[33]
               post['profile_sidebar_border_color'] = u[34]
               post['profile_sidebar_fill_color'] = u[35]
               post['profile_text_color'] = u[36]
               post['profile_use_background_image'] = u[37]
               post['protected'] = u[38]
               post['statuses_count'] = u[39]
               post['time_zone'] = u[40]
               post['translator_type'] = u[41]
               post['url'] = u[42]
               post['utc_offset'] = u[43]
               post['verified'] = u[44]
               post['screen_name'] = u[45]
               sampleUsers.update({'id': row[0]}, {"$set": post}, upsert=True)
           except Exception as e:
               print 'error in getting ratings for user: ' + str(row[0])
               print(e)
        # get tweets
        curI.execute('SELECT * FROM GTapp_tweets where user_id=?', (row[0],))
        # initialize dictionary of tweets
        try:
           #print '' \
                 #''
           post = {}
           # post['tweets'] = alltweets
           # post['tweets_details'] = outtweets
           post['user_id'] = int(row[0])
           post['GT']=1
           post['sqliteID'] = []
           post['collected_at'] = []
           post['created_at'] = []
           post['id_str'] = []
           post['text'] = []
           post['source'] = []
           post['truncated'] = []
           post['in_reply_to_status_id_str'] = []
           post['in_reply_to_user_id_str'] = []
           post['in_reply_to_screen_name'] = []
           post['coordinatesNumber'] = []
           post['coordinates'] = []
           post['coordinatesType'] = []

           post['placeCountry'] = []
           post['placeCountryCode'] = []
           post['placeFullName'] = []
           post['placeID'] = []
           post['placeName'] = []
           post['placeType'] = []
           post['placeURL'] = []

           post['quoted_status_id_str'] = []
           post['is_quote_status'] = []
           post['retweeted_status'] = []
           post['quote_count'] = []
           post['reply_count'] = []
           post['retweet_count'] = []
           post['favorite_count'] = []

           post['hashtagsNumber'] = []
           post['hashtags'] = []
           post['urls'] = []
           post['urlsNumber'] = []
           post['user_mentionsNumber'] = []
           post['user_mentions'] = []
           post['mediaNumber'] = []
           post['mediaURLs'] = []
           post['mediaType'] = []
           post['symbolsNumber'] = []
           post['symbols'] = []
           post['pollsNumber'] = []
           post['polls'] = []

           # post['favorited'] = tweetsFavorited
           # post['retweeted'] = tweetsRetweeted

           post['possibly_sensitive'] = []
           post['filter_level'] = []
           post['lang'] = []
           post['matching_rulesNumber'] = []
           post['matching_rulesTag'] = []
           post['matching_rulesID'] = []

        except Exception as e:
           print 'error in getting ratings for user: ' + row[0]
           print(e)
        # insert tweets
        for cell in curI:
           #print cell[0]
           try:
               post['sqliteID'].append(cell[0])
               post['collected_at'].append(cell[1])
               post['created_at'].append(cell[2])
               post['id_str'].append(cell[4])
               post['text'].append(cell[5])
               post['source'].append(cell[6])
               post['truncated'].append(cell[7])
               post['in_reply_to_status_id_str'].append(cell[8])
               post['in_reply_to_user_id_str'].append(cell[9])
               post['in_reply_to_screen_name'].append(cell[10])
               post['coordinatesNumber'].append(cell[11])
               post['coordinates'].append(cell[12])
               post['coordinatesType'].append(cell[13])

               post['placeCountry'].append(cell[14])
               post['placeCountryCode'].append(cell[15])
               post['placeFullName'].append(cell[16])
               post['placeID'].append(cell[17])
               post['placeName'].append(cell[18])
               post['placeType'].append(cell[19])
               post['placeURL'].append(cell[20])

               post['quoted_status_id_str'].append(cell[21])
               post['is_quote_status'].append(cell[22])
               post['retweeted_status'].append(cell[23])
               post['quote_count'].append(cell[24])
               post['reply_count'].append(cell[25])
               post['retweet_count'].append(cell[26])
               post['favorite_count'].append(cell[27])

               post['hashtagsNumber'].append(cell[28])
               post['hashtags'].append(cell[29])
               post['urls'].append(cell[30])
               post['urlsNumber'].append(cell[31])
               post['user_mentionsNumber'].append(cell[32])
               post['user_mentions'].append(cell[33])
               post['mediaNumber'].append(cell[34])
               post['mediaURLs'].append(cell[35])
               post['mediaType'].append(cell[36])
               post['symbolsNumber'].append(cell[37])
               post['symbols'].append(cell[38])
               post['pollsNumber'].append(cell[39])
               post['polls'].append(cell[40])

               # post['favorited'] = tweetsFavorited
               # post['retweeted'] = tweetsRetweeted

               post['possibly_sensitive'].append(cell[41])
               post['filter_level'].append(cell[42])
               post['lang'].append(cell[43])
               post['matching_rulesNumber'].append(cell[44])
               post['matching_rulesTag'].append(cell[45])
               post['matching_rulesID'].append(cell[46])
           except Exception as e:
               print 'error in getting tweet '+cell[4]+' for user: ' + str(row[0])
               print(e)
        try:
            tweets.update({'user_id': int(row[0])}, {"$set": post}, upsert=True)
        except Exception as e:
            print 'error in getting tweets for user: ' + row[0]
            print(e)


# do_stuff_with_row
def insert_petition(conn, petition):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO GTapp_petition(petition_id,url,title)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.executemany('insert into GTapp_petition(petition_id,url,title) values (?,?,?)', (petition,))
    conn.commit()
    #cur.execute(sql, petition)
    #return cur.lastrowid

def stripHtmlOverview(petitions):
    count=0
    for p in petitions.find():
        overviewStripped = strip_tags(p['overview'])
        petitions.update({"petition_id": p['petition_id']}, {"$set": {"overviewStripped": overviewStripped}}, False, False)

def computeLength(petitions):
    count=0
    for p in petitions.find():
        overviewStripped = strip_tags(p['overview'])
        words = overviewStripped.split(" ")
        l=len(words)
        petitions.update({"petition_id": p['petition_id']}, {"$set": {"petitionLength": l}}, False, False)


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def insertQualityPetitions(petitions,petitionsGT):
    for p in petitions.find({"petitionLength":{ "$gt": 99}}):
        tmp=removekey(p,"_id")
        try:
            petitionsGT.insert(tmp)
            #petitionsGT.update_one({'petition_id': tmp['petition_id']},{"$set": tmp}, upsert=True)
        except Exception as e:
            print(e)


def migratePetition():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ClimateChange
    petitions = db.PetitionNewOpen
    total=[]
    for p in petitions.find():
        pet=[]
        pet.append(p["petition_id"])
        pet.append(p["url"])
        pet.append(p["title"])
        insert_petition(conn, tuple(pet))
        total.append(tuple(pet))
    #insert_petition(conn,total)

def getGT():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ClimateChange
    users = db.UserNew
    cursor = users.find({"$and": [{"rating": 1}, {"statuses_count": { "$gt": 300}}]}, no_cursor_timeout=True)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    for dbu in cursor:
        # Send Direct Message to official Twitter handle
        user=dbu["name"]
        msg="Dear "+user+"\n I am currently working on my dissertation to design a recommender system with social network and psycholinguistic features for the unique context of online petitions. \nThe study is IRB approved. For more details, please find a link to the consent http://bit.ly/2p1EGwA \nYour input is needed to rate 10-15 petition according to your interest to train the model and help \nthe online petitioning community and their causes to be better matched with users on social media that shares their concerns. \nPlease feel free to submit and share the questionnaire in the link below: https://goo.gl/KqTJE5\nThank you,\nAhmed"
        sn=dbu["screen_name"]
        # update the status
        try:
            api.update_status(status="Hello Everyone !"+"@ahmed_nosho")
        except Exception as e:
            #print 'error in iteration no : ' + str(count) + ' in getting tweets for user : ' + str(dbu['id'])
            print(e)
        #api.send_direct_message(screen_name=sn, text=msg)
        #send_msg = api.PostDirectMessage(msg, user_id=None, screen_name=sn)

def sendTweet2Retweeters():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ClimateChange
    users = db.UserNew
    cursor = users.find({"GT": 0}, no_cursor_timeout=True)
    for dbu in cursor:
        print '@'+dbu["screen_name"]

def numbeofMentions(petitions,ratings):
    mentions={}
    for r in ratings.find({"GT": 0}, no_cursor_timeout=True):
        mentions[r["petition_id"]]=0
    for r in ratings.find({"GT": 0}, no_cursor_timeout=True):
        mentions[r["petition_id"]]+=1
    for k in mentions:
        petitions.update({"petition_id": int(k)}, {"$set": {"Twitter_mentions": mentions[k]}}, False, False)

def numbeofMentionsTo0(petitions):
    mentions={}
    for p in petitions.find({"Twitter_mentions": {'$exists': False}}, no_cursor_timeout=True):
        petitions.update({"petition_id": p['petition_id']}, {"$set": {"Twitter_mentions": 0}}, False, False)

def remainingPercent(petitions):
    mentions={}
    for p in petitions.find({}, no_cursor_timeout=True):
        petitions.update({"petition_id": p['petition_id']}, {"$set": {"supporters_remaining_percent": float(p['supporters'])/float(p['goal'])}}, False, False)

def strCount(petitions):
    posts={}
    for p in petitions.find({}, no_cursor_timeout=True):
        posts = {}
        posts["updates_count_int"]=int(p["updates_count"])
        posts["reasons_count_int"] = int(p["updates_count"])
        posts["signature_count_int"] = int(p["signature_count"])
        posts["targets_count_int"] = int(p["targets_count"])
        petitions.update({"petition_id": p['petition_id']}, {"$set": posts}, False, False)


def main():
    rows = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
            ('2006-04-05', 'BUY', 'MSOFT', 1000, 72.00),
            ('2006-04-06', 'SELL', 'IBM', 500, 53.00)]
    row = ('2006-03-28', 'BUY', 'IBM', 1000, 45.00)
    print type(row)

    temp="Prior to President Trump and the appointment of Scott Pruitt as EPA Administrator, there was a entire page on the EPA website dedicated to climate change education"
    a=temp.split(" ")
    print len (a)
    #migratePetition()
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ClimateChange
    petitions = db.PetitionNewOpen
    ratings = db.RatingNew
    #sendTweet2Retweeters()
    #numbeofMentions(petitions,ratings)
    #numbeofMentionsTo0(petitions)
    #remainingPercent(petitions)
    strCount(petitions)
    #petitionsClosed = db.PetitionNewClosed
    #petitionsVictory = db.PetitionNewVictory
    #stripHtmlOverview(petitionsVictory)
    #computeLength(petitionsVictory)

    #insertQualityOpenedPetitions()
    #insertQualityPetitions(petitionsVictory,db.b)
    #getGT()
    #getGTUsers()

if __name__ == '__main__':
    main()