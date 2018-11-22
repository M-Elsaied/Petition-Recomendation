
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

# Twitter application credentials
'''
consumer_key = 'bEUXoxgEVe054Qn5NmYZ3J2Lo'
consumer_secret = 'YuYuAK529iBq3HqcW4iXHV4WDqaoACqnoh9lTZYiP4hJmAIUGz'
access_token = '829191674572201984-g9WeDvoShdo94oa9St0xJz9xgZXlSns'
access_token_secret = '5fA78TZcIybC6Muo1EEVv0wFyz0BWIaI904EOYBWBJEwW'
twitter_handle='change'
'''
# Another application in order to collect twitter dataset faster

consumer_key = 'MO4iVYUfjZwfAEWs4Op9rZIEU'
consumer_secret = 'zIfwJx1GpyDFVJkxwWeFXprKmgUaKj1fJIYaoznARjSezLlxn1'
access_token = '104254763-aN94ddj4uCaPOPlyG9k6mgcVKoZNXVYBR9Un3qWP'
access_token_secret = 'YykVrcdiN5K10WNhd5UxmoX2lcCcOlRuPqdFm3xCSl7r1'
twitter_handle='change'


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,retry_count=3, retry_delay=60,retry_errors=set([401, 404, 500, 503]),wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

CCKeywords=["climate change","methane","global cooling","nuclear winter","carbon dioxide","c02","co2","emissions","pollution","arctic","forest degradation", "environmental vulnerability", "deforestation"]
keys = []
for k in CCKeywords:
    keys.append(k.lower())
'''public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text'''
client = MongoClient('mongodb://localhost:27017/')
client = MongoClient()
db = client.ClimateChange


allUsers = db.AllUsers
petitions = db.PetitionNewOpen
ratings = db.RatingNew
sampleUsers = db.UserNew
tweets=db.TweetsNew
filteredTweets=db.TweetsFiltered


def checkKeywords(tweet):
    result=False;
    t = tweet.lower()
    #words = t.split(" ")
    for k in keys:
        if k in t:
            #print t
            result= True;
            break;
    return result

def checkNotSubWord(tweet):
    result=False;
    t = tweet.lower()
    words = t.split(" ")
    for w in words:
        if w in keys:
            #print w
            result= True;
            break;
    print tweet
    return result

def FilteredUsersTweets():
    # initialize a with {}
    tweetsSet = {}

    # check data type of a
    # Output: <class 'dict'>
    print(type(tweetsSet))

    # initialize a with set()
    tweetsSet = set()
    # check data type of a
    # Output: <class 'set'>
    print(type(tweetsSet))
    count = 0
    allTweetsCount = 0
    count = 0
    allTweetsCount = 0
    qry = {"$or": [{"GT": 1}, {"GT": 0}]}
    cursor = tweets.find(qry,no_cursor_timeout=True)

    for dbt in cursor:
        offset=0
        totalTweetsLength=0
        totalTweets=0
        totalRetweetNumber=0
        totalHashtagsNumber = 0
        tweet={}
        user={}
        tweet['user_id']=dbt["user_id"]
        tweet['GT'] = dbt["GT"]
        tweet['id'] = []
        tweet['text'] = []
        tweet['hashtagsNumber'] = []
        tweet['quote_count'] = []
        tweet['placeCountryCode'] = []
        tweet['truncated'] = []
        tweet['hashtags'] = []
        tweet['symbols'] = []
        tweet['is_quote_status'] = []
        tweet['coordinatesType'] = []
        tweet['reply_count'] = []
        tweet['coordinatesNumber'] = []

        tweet['favorite_count'] = []
        tweet['urlsNumber'] = []
        tweet['matching_rulesNumber'] = []
        tweet['mediaType'] = []
        tweet['coordinates'] = []
        tweet['source'] = []
        tweet['in_reply_to_screen_name'] = []
        tweet['id_str'] = []
        tweet['mediaURLs'] = []
        tweet['retweet_count'] = []

        tweet['mediaNumber'] = []
        tweet['symbolsNumber'] = []
        tweet['matching_rulesID'] = []
        tweet['placeName'] = []
        tweet['placeURL'] = []
        tweet['placeCountry'] = []
        tweet['retweeted_status'] = []
        tweet['placeID'] = []
        tweet['user_mentions'] = []
        tweet['user_mentionsNumber'] = []

        tweet['in_reply_to_user_id_str'] = []
        tweet['possibly_sensitive'] = []
        tweet['lang'] = []
        tweet['pollsNumber'] = []
        tweet['placeFullName'] = []
        tweet['created_at'] = []
        tweet['polls'] = []
        tweet['quoted_status_id_str'] = []
        tweet['placeType'] = []
        tweet['filter_level'] = []
        tweet['in_reply_to_status_id_str'] = []
        tweet['urls'] = []
        tweet['matching_rulesTag'] = []
        for t in dbt['text']:
            allTweetsCount+=1
            text = dbt['text'][offset].replace(',', ' ')
            textNoURL = ' '.join(item for item in text.split() if not (item.startswith('http://') or item.startswith('https://') and len(item) > 7))
            if not textNoURL in tweetsSet:
                tweetsSet.add(textNoURL)
                if dbt['retweeted_status'][offset]=="" and not "RT " in dbt["text"][offset] and dbt['urlsNumber'][offset]==0: #and dbt['lang'][offset]=="en":
                    #if checkKeywords(t):
                        #if checkNotSubWord(t):
                    count+=1
                    try:
                        tweet['id'].append(dbt['id'][offset])
                    except Exception as e:
                        print "error"
                        try:
                            tweet['id'].append(int(dbt['id_str'][offset]))
                        except Exception as e:
                            print "error2"

                    tweet['text'].append(textNoURL)
                    tweet['hashtagsNumber'].append(dbt['hashtagsNumber'][offset])
                    tweet['quote_count'].append(dbt['quote_count'][offset])
                    tweet['placeCountryCode'].append(dbt['placeCountryCode'][offset])
                    tweet['truncated'].append(dbt['truncated'][offset])
                    tweet['hashtags'].append(dbt['hashtags'][offset])
                    tweet['symbols'].append(dbt['symbols'][offset])
                    tweet['is_quote_status'].append(dbt['is_quote_status'][offset])
                    tweet['coordinatesType'].append(dbt['coordinatesType'][offset])
                    tweet['coordinatesNumber'].append(dbt['coordinatesNumber'][offset])
                    tweet['favorite_count'].append(dbt['favorite_count'][offset])
                    tweet['urlsNumber'].append(dbt['urlsNumber'][offset])
                    tweet['matching_rulesNumber'].append(dbt['matching_rulesNumber'][offset])
                    tweet['mediaType'].append(dbt['mediaType'][offset])
                    tweet['coordinates'].append(dbt['coordinates'][offset])
                    tweet['source'].append(dbt['source'][offset])
                    tweet['in_reply_to_screen_name'].append(dbt['in_reply_to_screen_name'][offset])
                    tweet['id_str'].append(dbt['id_str'][offset])
                    tweet['mediaURLs'].append(dbt['mediaURLs'][offset])
                    tweet['retweet_count'].append(dbt['retweet_count'][offset])
                    tweet['mediaNumber'].append(dbt['mediaNumber'][offset])
                    tweet['symbolsNumber'].append(dbt['symbolsNumber'][offset])
                    tweet['matching_rulesID'].append(dbt['matching_rulesID'][offset])

                    tweet['placeName'].append(dbt['placeName'][offset])
                    tweet['placeURL'].append(dbt['placeURL'][offset])
                    tweet['placeCountry'].append(dbt['placeCountry'][offset])
                    tweet['retweeted_status'].append(dbt['retweeted_status'][offset])
                    tweet['placeID'].append(dbt['placeID'][offset])
                    tweet['user_mentions'].append(dbt['user_mentions'][offset])
                    tweet['user_mentionsNumber'].append(dbt['user_mentionsNumber'][offset])

                    tweet['in_reply_to_user_id_str'].append(dbt['in_reply_to_user_id_str'][offset])
                    tweet['possibly_sensitive'].append(dbt['possibly_sensitive'][offset])
                    tweet['lang'].append(dbt['lang'][offset])
                    tweet['placeFullName'].append(dbt['placeFullName'][offset])
                    tweet['pollsNumber'].append(dbt['pollsNumber'][offset])
                    tweet['created_at'].append(dbt['created_at'][offset])
                    tweet['polls'].append(dbt['polls'][offset])

                    tweet['quoted_status_id_str'].append(dbt['quoted_status_id_str'][offset])
                    tweet['placeType'].append(dbt['placeType'][offset])
                    tweet['filter_level'].append(dbt['filter_level'][offset])
                    tweet['in_reply_to_status_id_str'].append(dbt['in_reply_to_status_id_str'][offset])
                    tweet['urls'].append(dbt['urls'][offset])
                    tweet['matching_rulesTag'].append(dbt['matching_rulesTag'][offset])
                    totalTweetsLength+=len(textNoURL)
                    totalTweets= totalTweets+" "+ textNoURL
                    totalRetweetNumber+=dbt['retweet_count'][offset]
                    #totalHashtagsNumber+=
            offset += 1
        try:
            tweet
            filteredTweets.insert(tweet)
            sampleUsers.update({'id': dbt["user_id"]}, {"$set": userCur}, upsert=False)
        except Exception as e:
            print 'error in inserting tweet '+str(dbt['user_id']) +" at counter"+ str(allTweetsCount)

    print count
    print '' \
          ''
    print allTweetsCount


# Unshorten URL
def unshorten_url(url):
    try:
        r = requests.head(url, allow_redirects=True)
        return r.url
    except:
        return None

# Check if user in database
def is_user_in_db(user_id):
    return get_user_from_db(user_id) is None

# Retrieve user from database
def get_user_from_db(user_id):
    return allUsers.find_one({'user.id' : user_id})

# Get user from Twitter
def get_user_from_twitter(user_id):
    return api.get_user(user_id)

# retrieve 3200 tweets for a user from Twitter and update database
def get_all_tweets(uid):
    # Twitter only allows access to a users most recent 3240 tweets with this method
    tweets_str=''
    # initialize a list to hold all the tweepy Tweets
    alltweets = []
    outtweets = {}
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(id=uid, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    count=0
    #while len(new_tweets) > 0:

    # Get 1600 tweets to user
    while count<17:
        print "getting tweets before %s" % (oldest)

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(id=uid, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print "...%s tweets downloaded so far" % (len(alltweets))
        count+=1

    # transform the tweepy tweets into a 2D array that will populate in database

    tweetsCreated_at=[]

    tweetsID = []
    tweetsIDStr = []
    tweetsText = []
    tweetsSource = []
    tweetsTruncated = [] #indicates if the tweet was trimmed usually from cross social media platform

    tweetsIn_reply_to_status_id_str = []
    tweetsIn_reply_to_user_id_str = []
    tweetsIn_reply_to_screen_name = []

    #tweetsContributors = []
    tweetsCoordinatesNumber = []
    tweetsCoordinates = []
    tweetsCoordinatesType = []

    tweetsPlaceCountryCode=[]
    tweetsPlaceCountry=[]
    tweetsPlaceFullName = []
    tweetsPlaceID=[]
    tweetsPlaceName=[]
    tweetsPlaceType = []
    tweetsPlaceURL=[]

    tweet_Quoted_status_id_str = []
    tweetsIs_quote_status = []
    tweetsQuote_status = []

    tweetsRetweet_status = []

    tweetsQuote_count = []

    tweetsReply_count = []

    tweetsRetweet_count = []


    #Entity object
    tweetsHashtagsNumber = []
    tweetsHashtags=[]
    tweetsMediaNumber = []
    tweetsMediaType =[]
    tweetsMediaURLs = []
    tweetsURLsNumber = []
    tweetsURLs =[]
    tweetsMentionsNumber = []
    tweetsMentions = []
    tweetsSymbols = []
    tweetsSymbolsNumber = []   # presence of $ or any symbol
    tweetsPolls = []
    tweetsPollsNumber = []

    tweetsFavorite_count = []
    tweetsFavorited = []
    tweetsRetweeted = []
    tweetsPossibly_sensitive = []  #Contains link
    tweetsFiltered_level = []  #Streaming option
    tweetsLang = []

    #Matching Rule object
    tweetsMatching_rulesNumber = []
    tweetsMatching_rulesTag = []
    tweetsMatching_rulesID = []

    for tweet in alltweets:
        #outtweets['id']=tweet.id_str
        #outtweets['details']=[tweet.created_at,tweet.text.encode("utf-8")]
        #tweets_str=tweets_str+'. '+tweet.text.encode("utf-8")
        #tweetsList.append(outtweets)

        tweetsCreated_at.append(tweet.created_at)
        #tweetsContributors.append(tweet.contributors)

        tweetsID.append(tweet.id)
        tweetsIDStr.append(tweet.id_str)
        tweetsText.append(tweet.text)
        tweetsSource.append(tweet.source)
        tweetsTruncated.append(tweet.truncated)
        tweetsIn_reply_to_status_id_str.append(tweet.in_reply_to_status_id_str)
        tweetsIn_reply_to_user_id_str.append(tweet.in_reply_to_user_id_str)
        tweetsIn_reply_to_screen_name.append(tweet.in_reply_to_screen_name)
        coordNumber=0
        coord=""
        coordType=""
        if hasattr(tweet, 'coordinates'):
            if tweet.coordinates is not None:
                if tweet.coordinates["coordinates"]:
                    coordNumber = len(tweet.coordinates["coordinates"])
                    if tweet.coordinates["coordinates"]:
                        for coordi in tweet.coordinates["coordinates"]:
                            coord = " "+coord + "," + str(coordi).encode("utf-8")
                if tweet.coordinates["type"]:
                    coordType = tweet.coordinates["type"].encode("utf-8")
        tweetsCoordinatesNumber.append(coordNumber)
        tweetsCoordinates.append(coord)
        tweetsCoordinatesType.append(coordType)

        placeCountry=""
        placeCountryCode=""
        placeFullName = ""
        placeID= ""
        placeName=""
        placeType=""
        placeURL=""
        if hasattr(tweet, 'place'):
            if tweet.place is not None:
                if tweet.place.country:
                    placeCountry=tweet.place.country.encode("utf-8")
                if tweet.place.country_code:
                    placeCountryCode=tweet.place.country_code.encode("utf-8")
                if tweet.place.full_name:
                    placeFullName=tweet.place.full_name.encode("utf-8")
                if tweet.place.id:
                    placeID=tweet.place.id.encode("utf-8")
                if tweet.place.name:
                    placeName=tweet.place.name.encode("utf-8")
                if tweet.place.place_type:
                    placeType=tweet.place.place_type.encode("utf-8")
                if tweet.place.url:
                    placeURL=tweet.place.url.encode("utf-8")

        tweetsPlaceCountry.append(placeCountry)
        tweetsPlaceCountryCode.append(placeCountryCode)
        tweetsPlaceFullName.append(placeFullName)
        tweetsPlaceID.append(placeID)
        tweetsPlaceName.append(placeName)
        tweetsPlaceType.append(placeType)
        tweetsPlaceURL.append(placeURL)

        tweetsIs_quote_status.append(tweet.is_quote_status)
        if tweet.is_quote_status == True:
            if hasattr(tweet, 'quoted_status_id_str'):
                tweetsQuote_status.append(tweet.quoted_status_id_str)
            else:
                tweetsQuote_status.append("")
        else:
            tweetsQuote_status.append("")


        if hasattr(tweet, 'retweeted_status'):
            if tweet.retweeted_status is not None:
                tweetsRetweet_status.append(tweet.retweeted_status.id_str)
            else:
                tweetsRetweet_status.append("")
        else:
            tweetsRetweet_status.append("")


        if hasattr(tweet, 'quote_count'):
            if tweet.quote_count is not None:
                tweetsQuote_count.append(tweet.quote_count)
            else:
                tweetsQuote_count.append(0)
        else:
            tweetsQuote_count.append(0)

        if hasattr(tweet, 'reply_count'):
            if tweet.reply_count is not None:
                tweetsReply_count.append(tweet.reply_count)
            else:
                tweetsReply_count.append(0)
        else:
            tweetsReply_count.append(0)

        if hasattr(tweet, 'retweet_count'):
            if tweet.retweet_count is not None:
                tweetsRetweet_count.append(tweet.retweet_count)
            else:
                tweetsRetweet_count.append(0)
        else:
            tweetsRetweet_count.append(0)

        if hasattr(tweet, 'favorite_count'):
            if tweet.favorite_count is not None:
                tweetsFavorite_count.append(tweet.favorite_count)
            else:
                tweetsFavorite_count.append(0)
        else:
            tweetsFavorite_count.append(0)

        htNumber=0
        ht=""
        mediaNumber = 0
        mediaType = ""
        mediaURL = ""
        URLNumber = 0
        urlstr = ""
        umNumber = 0
        um = ""
        symNumber = 0
        sym = ""
        pollNumber = 0
        poll = ""
        if hasattr(tweet, 'entities'):
            if 'hashtags' in tweet.entities:
            #if hasattr(tweet.entities, 'hashtags'):
                htNumber = len(tweet.entities["hashtags"])
                if tweet.entities["hashtags"]:
                    for hti in tweet.entities["hashtags"]:
                        if 'text' in hti:
                            ht = ht + " " + hti["text"].encode("utf-8")
            if 'media' in tweet.entities:
                mediaNumber = len(tweet.entities["media"])
                if tweet.entities["media"]:
                    for medi in tweet.entities["media"]:
                        if 'type' in medi:
                            mediaType = mediaType + " " + medi["type"].encode("utf-8")
                        if 'media_url' in medi:
                            mediaURL = mediaURL + " " + medi["media_url"].encode("utf-8")

            if 'urls' in tweet.entities:
                URLNumber = len(tweet.entities["urls"])
                if tweet.entities["urls"]:
                    for URLi in tweet.entities["urls"]:
                        if 'url' in URLi:
                            urlstr = urlstr + " " + URLi["url"].encode("utf-8")

            if 'user_mentions' in tweet.entities:
                umNumber = len(tweet.entities["user_mentions"])
                if tweet.entities["user_mentions"]:
                    for umi in tweet.entities["user_mentions"]:
                        if 'id_str' in umi:
                            um = um + " " + umi["id_str"]

            if 'symbols' in tweet.entities:
                symNumber = len(tweet.entities["symbols"])
                if tweet.entities["symbols"]:
                    for symi in tweet.entities["symbols"]:
                        if 'text' in symi:
                            sym = sym+" "+symi["text"].encode("utf-8")


            if 'polls' in tweet.entities:
                symNumber = len(tweet.entities["polls"])
                if tweet.entities["polls"]:
                    for polli in tweet.entities["polls"]:
                        if 'end_datetime' in polli:
                            poll = poll+","+polli["end_datetime"]

        tweetsHashtagsNumber.append(htNumber)
        tweetsHashtags.append(ht)
        tweetsMediaNumber.append(mediaNumber)
        tweetsMediaType.append(mediaType)
        tweetsMediaURLs.append(mediaURL)
        tweetsURLsNumber.append(URLNumber)
        tweetsURLs.append(urlstr)
        tweetsMentionsNumber.append(umNumber)
        tweetsMentions.append(um)
        tweetsSymbolsNumber.append(symNumber)
        tweetsSymbols.append(sym)
        tweetsPollsNumber.append(pollNumber)
        tweetsPolls.append(poll)

        '''if hasattr(tweet, 'favorited'):
            tweetsFavorited.append(tweet.favorited)
        else:
            tweetsFavorited.append("")

        if hasattr(tweet, 'retweeted'):
            tweetsRetweeted.append(tweet.retweeted)
        else:
            tweetsRetweeted.append("")'''

        if hasattr(tweet, 'possibly_sensitive'):
            tweetsPossibly_sensitive.append(tweet.possibly_sensitive)
        else:
            tweetsPossibly_sensitive.append("")

        if hasattr(tweet, 'filter_level'):
            tweetsFiltered_level.append(tweet.filter_level)
        else:
            tweetsFiltered_level.append("")

        if hasattr(tweet, 'lang'):
            tweetsLang.append(tweet.lang)
        else:
            tweetsLang.append("")

        matchingRulesNumber=0
        matchingRulesTag=""
        matchingRulesID=""
        if hasattr(tweet, 'matching_rules'):
            matchingRulesNumber = len(tweet.matching_rules)
            if tweet.matching_rules:
                for matchRi in tweet.matching_rules:
                    if 'tag' in matchRi:
                        matchingRulesTag = matchingRulesTag + "," + matchRi["tag"].encode("utf-8")
                    if 'id_str' in matchRi:
                        matchingRulesID = matchingRulesID + "," + matchRi["id_str"].encode("utf-8")

        tweetsMatching_rulesNumber.append(matchingRulesNumber)
        tweetsMatching_rulesTag.append(matchingRulesTag)
        tweetsMatching_rulesID.append(matchingRulesID)

    try:
        print uid
        print '' \
              ''
        post = {}
        #post['tweets'] = alltweets
        #post['tweets_details'] = outtweets
        post['user_id']=uid
        post['created_at'] = tweetsCreated_at
        post['id'] = tweetsID
        post['id_str'] = tweetsIDStr
        post['text'] = tweetsText
        post['source'] = tweetsSource
        post['truncated'] = tweetsTruncated
        post['in_reply_to_status_id_str'] = tweetsIn_reply_to_status_id_str
        post['in_reply_to_user_id_str'] = tweetsIn_reply_to_user_id_str
        post['in_reply_to_screen_name'] = tweetsIn_reply_to_screen_name
        post['coordinatesNumber'] = tweetsCoordinatesNumber
        post['coordinates'] = tweetsCoordinates
        post['coordinatesType'] = tweetsCoordinatesType

        post['placeCountry'] = tweetsPlaceCountry
        post['placeCountryCode'] = tweetsPlaceCountryCode
        post['placeFullName'] = tweetsPlaceFullName
        post['placeID'] = tweetsPlaceID
        post['placeName'] = tweetsPlaceName
        post['placeType'] = tweetsPlaceType
        post['placeURL'] = tweetsPlaceURL

        post['quoted_status_id_str'] = tweetsQuote_status
        post['is_quote_status'] = tweetsIs_quote_status
        post['retweeted_status'] = tweetsRetweet_status
        post['quote_count'] = tweetsQuote_count
        post['reply_count'] = tweetsReply_count
        post['retweet_count'] = tweetsRetweet_count
        post['favorite_count'] = tweetsFavorite_count

        post['hashtagsNumber'] = tweetsHashtagsNumber
        post['hashtags'] = tweetsHashtags
        post['urls'] = tweetsURLs
        post['urlsNumber'] = tweetsURLsNumber
        post['user_mentionsNumber'] = tweetsMentionsNumber
        post['user_mentions'] = tweetsMentions
        post['mediaNumber'] = tweetsMediaNumber
        post['mediaURLs'] = tweetsMediaURLs
        post['mediaType'] = tweetsMediaType
        post['symbolsNumber'] = tweetsSymbolsNumber
        post['symbols'] = tweetsSymbols
        post['pollsNumber'] = tweetsPollsNumber
        post['polls'] = tweetsPolls

        #post['favorited'] = tweetsFavorited
        #post['retweeted'] = tweetsRetweeted

        post['possibly_sensitive'] = tweetsPossibly_sensitive
        post['filter_level'] = tweetsFiltered_level
        post['lang'] = tweetsLang
        post['matching_rulesNumber'] = tweetsMatching_rulesNumber
        post['matching_rulesTag'] = tweetsMatching_rulesTag
        post['matching_rulesID'] = tweetsMatching_rulesID

        print ''
        print len(tweetsID)
        print ''
        tweets.insert(post)
    except Exception as e:
        print 'error in getting tweets for user: '+str(uid)
        print(e)



# Iterate through users with friends list in database and retrieve tweets to users and friends that do not have tweets
def update_all_tweets_users():
    count = 0

    # Iterate through users with friendslist
    cursor = sampleUsers.find({"friendsList": {'$exists': True}}, no_cursor_timeout=True)

    # Sort ascending, the other application should run the function but sorted descending for faster data collection
    cursor.sort('id', -1)
    count = 0

    # Loop on users
    for dbu in cursor:
        l = len(dbu)
        resT = allUsers.find({"$and": [{"id": dbu['id']}, {"tweets": {'$exists': True}}]}).count()

        # Check if user have no tweets, then get tweets
        if resT == 0:
            try:
                get_all_tweets(dbu['id'])
                print 'iteration no : ' + str(count) + ' in getting tweets for user : ' + str(dbu['id'])
            except Exception as e:
                print 'error in iteration no : ' + str(count) + ' in getting tweets for user : ' + str(dbu['id'])
                print(e)

        # loop on friends list and retrieve tweets for each friend
        for frd in dbu['friendsList']:
            resFT = allUsers.find({"$and": [{"id": frd}, {"tweets": {'$exists': True}}]}).count()

            # Check if friend have no tweets, then get tweets
            if resFT == 0:
                try:
                    get_all_tweets(frd)
                    print 'iteration no : ' + str(count) + ' in getting tweets for user : ' + str(frd)
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting tweets for user : ' + str(frd)
                    print(e)
        count += 1

# Loop on users in database and get tweets to users that do not yet have tweets
def get_users_tweets():
    count=0
    # Loop on users in database
    for dbu in allUsers.find({}, no_cursor_timeout=True):
        count+=1
        print '' \
              ''
        print '********************'
        print count
        print '********************'
        print '' \
              ''
        # Check if the user has tweets in database
        try:
            res = allUsers.find({"$and": [{"id": dbu['id']}, {"tweets": {'$exists': True}}]}).count()
            if res == 0:
                try:
                    # If user do not have tweets retrieve user tweets and update database
                    get_all_tweets(dbu['id'])
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)


# Insert group of users in database
def insert_users(users,i):
    count = 0
    # Loop on group of user
    for u in users:
        try:
            # Insert user to database
            allUsers.insert(u._json)
        except:
            print "error" + str(count)+" in "+str(i)
        count += 1
    # return the group of users
    return users

# Insert user in database
def insert_user(user,i,type):
    try:
        UserStr = "{"
        ts = time.time()  # Time stamp
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        UserStr += '"CollectedTimeStamp":"' + st + '",'+'"ChangeFollower":"' + type + '",'
        tmp0 = simplejson.dumps(user._json, separators=(',', ':'))
        tmpstr=str(tmp0[1:len(tmp0)])
        UserStr += tmpstr
        DicIns = simplejson.loads('[%s]' % UserStr)[0]
        allUsers.insert(DicIns) # insert user in AllUsers
        sampleUsers.insert(DicIns)  # insert user in sampleUsers
    except Exception as e:
        print(e)
        print "error" + " in insert" + str(user.id)
        #collectionUser.update({'id': user.id}, {"$set": DicIns}, upsert=True)
        #tmp.update({'id': user.id}, {"$set": DicIns}, upsert=True)


# Get followers ids in list
def get_followers_ids(user_id):
    ids = []
    page_count = 0
    for i,page in enumerate(tweepy.Cursor(api.followers_ids, id=user_id, count=5000).pages()):
        print 'Getting page {} for followers ids'.format(i)
        ids+=page
    return ids

# Get friends ids in list
def get_friends_ids(user_id):
    ids = []
    page_count = 0
    for i,page in enumerate(tweepy.Cursor(api.friends_ids, id=user_id, count=5000).pages()):
        print 'Getting page {} for friends ids'.format(i)
        ids+=page
    return ids


#Extract URL from tweet
def getURL(tweet):
    try:
        x=re.search("(?P<url>https?://[^\s]+)", tweet).group("url")
        return x
    except:
        return None

# Loop through all users and get lists for each
# 1) Membership List: the user is a member in a list as listed by the community
# This measure popularity, and how user is being perceived by the community
# 2) Subscription List: the user subscribe herself in a list
# This measure the user preference
# Also from list description, we could get the user preference and how user is being perceived by the community)
def get_lists():
    # Loop on all users
    for u in allUsers.find({}, no_cursor_timeout=True):
        print u['id']
        post = {}
        try:
            get_user_lists(u['id'])
        except Exception as e:
            print(e)


# Get lists for single user
# 1) Membership List: the user is a member in a list as listed by the community
# This measure popularity, and how user is being perceived by the community
# 2) Subscription List: the user subscribe herself in a list
# This measure the user preference
# Also from list description, we could get the user preference and how user is being perceived by the community)
def get_user_lists(user_id):
    print user_id
    post={}
    try:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(10)  # 10 seconds
        # Get membership lists
        try:
            memberships = api.lists_memberships(id=user_id)
        except Exception, msg:
            print "Timed out!"
        post['memberships']=[]
        # Loop on membership lists
        for m in memberships:
            # Convert list to dictionary
            dic=insertListDict(m)
            # Add list dictionary as entry in membership list
            post['memberships'].append(dic)
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(10)  # 10 seconds

        # Get subscription lists
        try:
            subsciptions = api.lists_subscriptions(id=user_id)
        except Exception, msg:
            print "Timed out!"
        post['subscriptions'] = []
        # Loop on subscription lists
        for s in subsciptions:
            # Convert list to dictionary
            dic=insertListDict(s)
            # Add list dictionary as entry in subscription list
            post['subscriptions'].append(dic)
        # Update user with subscription and membership lists
        sampleUsers.update({'id': user_id}, {"$set": post}, upsert=True)
    except Exception as e:
        print "error in user lists: " + str(user_id)
        print(e)


# Get Friends list by friend id
def get_friends(user_id):
    users = []
    page_count = 0

    # Loop on all friends
    for i,user in enumerate(tweepy.Cursor(api.friends, id=user_id, count=200).pages()):
        print 'Getting page {} for friends'.format(i)
        users += user
    return users

# Get Friends list
# Get lists, tweets for each friend and insert friends in user table
def get_user_friends(uid):
    # Loop on friends
    for i, groupUsers in enumerate(tweepy.Cursor(api.friends, id=uid, count=200).pages()):
        try:
            # initialize empty friends list
            users = []
            #signal.signal(signal.SIGALRM, signal_handler)
            #signal.alarm(15)  # 5 seconds
            count = 0
            print 'Getting page {} for friends'.format(i)
            for u in groupUsers:
                if u.protected == True:     #Skip friend if protected
                    continue
                exc = False
                fu_id = u.id
                qry = {'id': fu_id}
                result = allUsers.find(qry).count()  #Check if user exists in database
                users.append(fu_id)     # Add user to friends list
                if result == 0:  # if not found insert user in database with type = unknown change.org Follower ="-"
                    insert_user(u, i, "friend")
                    try:
                        # Get user's membership and subscription lists
                        #get_user_lists(fu_id)
                        # Get user's tweets
                        get_all_tweets(fu_id)
                    except Exception as e:
                        exc = True
                        print(e)
                        print 'error in getting tweets for user: ' + str(fu_id)
                        continue
                else:  # user already exists in database either being change.org follower or friend of other user
                    userPost = {}
                    try:
                        # Get user from all followers table
                        userCur = allUsers.find_one(qry)
                        # userPost=insertUserDict(userCur)
                        # update user sample table
                        sampleUsers.update({'id': fu_id}, {"$set": userCur}, upsert=True)
                        # Skip if user is protected
                        if userCur['protected'] == False:
                            '''
                            result2 = allUsers.find(
                                {"$and": [{"id": fu_id}, {"subscriptions": {'$exists': True}}]}).count()
                            # Check if user does not have lists, Get lists
                            if result2 == 0:
                                try:
                                    get_user_lists(fu_id) # Get user's lists
                                except Exception as e:
                                    exc = True
                                    print(e)
                                    print 'error in getting lists for user: ' + str(fu_id)
                                    continue
                            '''
                            # Check if user does not have tweets, Get tweets
                            resultTweets = tweets.find({"id": fu_id}).count()
                            if resultTweets == 0:
                                try:
                                    get_all_tweets(fu_id)   # Get user's tweets
                                except:
                                    exc = True
                                    print 'error in getting tweets for user: ' + str(fu_id)

                        else:
                            continue
                    except:
                        exc = True
                        print(e)
                        print 'error an existing from user table to UserTemp user: ' + str(fu_id)
                # if exc==False :
                count += 1
                # Get 1000 friends and break
                if count == 1000:
                    break
            if count == 1000:
                break
        except Exception as e:
            print(e)

    # Update list of friends to user in database
    try:
        print users
        print '' \
              ''
        post = {}
        post['friendsList'] = users
        allUsers.update({'id': uid}, {"$set": post}, upsert=True)
        sampleUsers.update({'id': uid}, {"$set": post}, upsert=False)
    except Exception as e:
        print "error in friends of " + str(uid)
        print(e)

# Get tweets, lists and friends lists for users with ratings in ratings table
def update_user_features_from_ratings():
    count=0

    # Get all ratings
    cursor=sampleUsers.find({'rating':1}, no_cursor_timeout=True)

    # Sort ascending, the other application should run the function but sorted descending for faster data collection
    cursor.sort('id',-1)

    for dbu in cursor:  # Loop on all users
        #qry = {'id': dbu['id']}
        # Check if already has all features updated and has list of friends
        qry =  {"$and": [{"id": dbu['id']}, {"friendsList": {'$exists': True}}]}
        result = sampleUsers.find(qry).count()
        # If features are retrieved get the next user
        if result == 1:
            continue;
        print '' \
              ''
        print '********************'
        print str(count)+' user id = '+dbu['id_str']
        print '********************'
        print '' \
              ''
        count+=1


        try:
            # Check if user has tweets already retrieved
            resT = tweets.find({"id": dbu['id']}).count()
            if resT == 0:   # If no tweets, get tweets
                try:
                    get_all_tweets(dbu['id']) # Get tweets for user
                    print '********************'
                    print count
                    print '********************'
                except Exception as e:
                    print 'error in iteration no : '+ str(count)+ ' in getting tweets for user : '+str(dbu['id'])
                    print(e)
            # Check if user has lists already retrieved
            '''
            resS = allUsers.find({"$and": [{"id": dbu['id']}, {"subscriptions": {'$exists': True}}]}).count()
            resM = allUsers.find({"$and": [{"id": dbu['id']}, {"memberships": {'$exists': True}}]}).count()
            if resS == 0 and resM == 0:
                try:
                    get_user_lists(dbu['id']) # Get lists for user
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting lists for user : ' + str(dbu['id'])
                    print(e)
            '''

            #Check if user has friends list already retrieved
            resF = sampleUsers.find({"$and": [{"id": dbu['id']}, {"friendsList": {'$exists': True}}]}).count()
            if resF == 0:
                try:
                    get_user_friends(dbu['id']) # Get friends list for user
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting friends for user : ' + str(dbu['id'])
                    print(e)

            # Retrieve user from all users table
            resUser=allUsers.find_one({"id": dbu['id']})
            print resUser

            # Update user with all tweets, lists and friends features to the users sample table
            sampleUsers.update({'id': dbu['id']}, {"$set": resUser}, upsert=False)
        except Exception as e:
            print 'error in iteration no : ' + str(count) + ' in getting updating the temp table for user : ' + str(dbu['id'])
            print(e)

# Increase the number of users from users who did not rate petitions
# Get tweets, lists and friends lists for these users
def get_non_rating_users():
    count = 0
    # Randomly select users
    cursor = sampleUsers.find(
        {'$and': [{"topicSocial3": {'$exists': True}}, {"friendsList": {'$exists': False}}]},
        no_cursor_timeout=True)

    # Sort ascending, the other application should run the function but sorted descending for faster data collection
    cursor.sort('id', -1)
    for dbu in cursor:
        # Check if already has all features updated and has list of friends
        qry = {"$and": [{"id": dbu['id']}, {"friendsList": {'$exists': True}}]}
        result = sampleUsers.find(qry).count()
        # If features are retrieved get the next user
        if result == 1:
            continue;
        print '' \
              ''
        print '********************'
        print str(count) + ' user id = ' + dbu['id_str']
        print '********************'
        print '' \
              ''
        count += 1
        try:
            # Check if user has tweets already retrieved
            resT = allUsers.find({"$and": [{"id": dbu['id']}, {"tweets": {'$exists': True}}]}).count()
            if resT >= 0:   # If no tweets, get tweets
                try:
                    get_all_tweets(dbu['screen_name'], dbu['id'])   # Get tweets for user
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting tweets for user : ' + str(
                        dbu['id'])
                    print(e)
            resS = allUsers.find({"$and": [{"id": dbu['id']}, {"subscriptions": {'$exists': True}}]}).count()
            resM = allUsers.find({"$and": [{"id": dbu['id']}, {"memberships": {'$exists': True}}]}).count()
            # Check if user has lists already retrieved
            if resS == 0 and resM == 0:
                try:
                    get_user_lists(dbu['id'])   # lists for user
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting lists for user : ' + str(
                        dbu['id'])
                    print(e)
            resF = allUsers.find({"$and": [{"id": dbu['id']}, {"friendsList": {'$exists': True}}]}).count()
            # Check if user has friends list already retrieved
            if resF == 0:
                try:
                    get_user_friends(dbu['id']) # Get friends list for user
                except Exception as e:
                    print 'error in iteration no : ' + str(count) + ' in getting friends for user : ' + str(
                        dbu['id'])
                    print(e)
            # Drop "_id" column to avoid update db exceptions
            resUser = removekey(allUsers.find_one({"id": dbu['id']}), "_id")
            print resUser
            # Update sample users with new features
            sampleUsers.update({'id': dbu['id']}, {"$set": resUser}, upsert=False)
        except Exception as e:
            print 'error in iteration no : ' + str(
                count) + ' in getting updating the temp table for user : ' + str(dbu['id'])
            print(e)


# Remove certain key from dictionary
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

# Update users who has less than 30 features
def get_update_users():
    count=0
    cursor=sampleUsers.find({"friendsList": {'$exists': True}}, no_cursor_timeout=True)
    cursor.sort('id',-1)
    for dbu in cursor:
        l=len(dbu)
        if l<30:
            try:
                # Drop "_id" column to avoid update db exceptions
                resUser = removekey(allUsers.find_one({"id": dbu['id']}),"_id")
                print resUser
                # Update Sample users with all user features in all users table
                sampleUsers.update({'id': dbu['id']}, {"$set": resUser}, upsert=False)
            except Exception as e:
                print 'error in iteration no : ' + str(count) + ' in getting updating the temp table for user : ' + str(dbu['id'])
                print(e)


# Get users climate change tweeted petitions to get the R-matrix
def get_tweeted_petitions():
    TPsubString="change.org%2Fp%2F" # Tweeted petition substring format
    # Loop on all tweeted petitions retrieved
    for i, tweetsPage in enumerate(tweepy.Cursor(api.search, q=TPsubString, count=100).pages()):
        for t in tweetsPage:
            # List of URLs in the tweet
            URLs=[]
            twt=t.text
            # Get all URLs in tweet
            while (1):
                u=getURL(twt)
                if u is None:   # If no URL in tweet exist and get next tweet
                    break
                else:
                    URLs.append(u)  # if tweet has URL then append to URLs list
                    twt=twt.replace(u,"") # put null instead of the URL added to the list and search for other URL remaining
            # Print tweet
            '''
            print t
            print '' \
                  ''
            print t.author
            print '' \
                  ''

            print t.user._json

            print t.user
            print '' \
                  ''
            print t.text
            '''
            # loop on URLs in tweet
            for ul in URLs:
                URL=unshorten_url(ul)   # Unshorten short URLs
                print URL
                try:
                    link = 'https://api.change.org/v1/petitions/get_id?petition_url=' + URL + '&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                    response = requests.get(link)
                    results = json.loads(response.text) # load petition short details in json
                    pid = results["petition_id"]    # get petition id
                    qry = {'petition_id': pid}
                    result = petitions.find(qry).count()  # Check if petition is in database
                    if result==0:   # Not a Climate Change related petition
                        continue
                    else:           #Add Climate change petition and tweeted user to the ratings table
                        resR = ratings.find(
                            {"$and": [{"id": t.user.id}, {"petition_id": pid}]}).count()
                        if resR==0:
                            ratingsDict={}
                            #tweetDetails
                            for key, value in t._json.iteritems():
                                ratingsDict["tweet_"+key]=value
                            # petitionDetails
                            ratingsDict["petition_id"]=str(pid)
                            ratingsDict["petition_url"] = URL

                            # userDetails
                            for key, value in t._json["user"].iteritems():
                                ratingsDict["user_"+key]=value
                            ts = time.time()
                            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            ratingsDict["CollectedTimeStamp"] = st
                            '''
                            insertRating = '{'
                            insertRating+='"tweetText":"'+t.text+'",'+'"tweetDate":"'+t.created_at+'",'+'"tweetRetweet_count":"'+t.retweet_count+'",'+'"tweetRetweeted":"'+t.retweeted+'",'+'"tweetIn_reply_to_user_id":"'+t.in_reply_to_user_id+'",'+'"tweetPlace":"'+t.place+'",'+'"tweetid":"'+str(t.id)+'",'+'"favorite_count":"'+str(t.favorite_count)+'",'

                            insertRating+='"petition_id":"'+str(pid)+'",'+'"petition_url":"'+URL+'",'+'"CollectedTimeStamp":"'+st+'",'
                            print insertRating
                            print '' \
                                ''
                            tmp=simplejson.dumps(t.user._json, separators=(',', ':'))
                            insertRating+=tmp[1:len(tmp)]
                            print insertRating
                            insertRatingDic=simplejson.loads('[%s]' % insertRating)
                            ratings.insert(insertRatingDic)
                            '''
                            ratings.insert(ratingsDict)
                            resU = sampleUsers.find({"id": t.user.id}).count()  # check if user is already existing in database
                            if resU ==0:    # if does not exist, then add user
                                insert_user(t.user,0,'R')
                except:
                    continue
            braclet = 0
            #print t.statuses
            #print t.entities.hashtags


def update_tweets_dates():
    count=0

    # Get all ratings
    cursor=ratings.find({'rating':1}, no_cursor_timeout=True)

    # Sort ascending, the other application should run the function but sorted descending for faster data collection
    cursor.sort('id',-1)

    for dbt in cursor:  # Loop on all users

        for i, tweetsPage in enumerate(tweepy.Cursor(api.search, q=dbt["tweetText"], count=100).pages()):
            for t in tweetsPage:
                post = {}
                post['tweetDate']=t.created_at
                ratings.update({"$and": [{"id": t.id}, {"petition_id": dbt["petition_id"]}]}, {"$set": post}, upsert=False)


def update_users_lists_count():
    count=0
    cursor=sampleUsers.find({"friendsList": {'$exists': True}}, no_cursor_timeout=True)
    #cursor.sort('id',-1)
    for dbu in cursor:
        l=len(dbu)
        post = {}
        if 'memberships' in dbu:
            mCount=len(dbu['memberships'])
        else:
            mCount=0
        post['membershipsCount']=mCount
        if 'subscriptions' in dbu:
            sCount = len(dbu['subscriptions'])
        else:
            sCount=0

        post['subscriptionsCount'] = sCount
        #if l<30:
        try:
            # Drop "_id" column to avoid update db exceptions
            resUser = removekey(allUsers.find_one({"id": dbu['id']}),"_id")
            print resUser
            # Update Sample users with all user features in all users table
            sampleUsers.update({'id': dbu['id']}, {"$set": post}, upsert=False)
        except Exception as e:
            print 'error in iteration no : ' + str(count) + ' in getting updating the temp table for user : ' + str(dbu['id'])
            print(e)

def remove_Nonserializable(dict):
    tmp = {}
    for k in dict:
        # unserializable attribute _id in user
        if k == '_id':
            continue
        else:
            tmp[k] = dict[k]
    return tmp

# Convert list to dictionary
def insertListDict(list):
    # list informative fields: list id, list name, list description,
    # subscribers count, members count, and list mode
    createdTime = datetime.datetime.strftime(list.created_at, "%Y-%m-%d %H:%M:%S.%f")
    dic = {}
    dic['list_id'] = list.id
    dic['list_name'] = list.name
    dic['list_description'] = list.description
    dic['list_member_count'] = list.member_count
    dic['list_subscriber_count'] = list.subscriber_count
    dic['list_mode'] = list.mode
    dic['list_uri'] = list.uri
    dic['list_created_at'] = createdTime
    dic['list_full_name'] = list.full_name
    dic['list_slug'] = list.slug
    return dic

# Exception handling function
def signal_handler(signum, frame):
    raise Exception("Timed out!")

# Remove all duplicates from user ratings
def removeDupRatings():
    for t in ratings.find():
        pid=t['petition_id']
        uid = t['id']
        qry = {'petition_id': pid}
        qry={"$and": [{"petition_id": pid}, {"id": uid}]}
        userID=t['id']
        result = ratings.find(qry).count()
        if result == 0:  # not found
            ratings.insert(t)

def checkGTImplicitRatings():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ClimateChange
    tweets = db.TweetsNew
    cursor = tweets.find({"GT": 1}, no_cursor_timeout=True)
    for u in cursor:
        for t in u["text"]:
            URLs=[]
            twt=t
            # Get all URLs in tweet
            while (1):
                u=getURL(twt)
                if u is None:   # If no URL in tweet exist and get next tweet
                    break
                else:
                    URLs.append(u)  # if tweet has URL then append to URLs list
                    twt=twt.replace(u,"") # put null instead of the URL added to the list and search for other URL remaining
            # Print tweet
            '''
            print t
            print '' \
                  ''
            print t.author
            print '' \
                  ''

            print t.user._json

            print t.user
            print '' \
                  ''
            print t.text
            '''
            # loop on URLs in tweet
            for ul in URLs:
                URL=unshorten_url(ul)   # Unshorten short URLs
                print URL
                try:
                    link = 'https://api.change.org/v1/petitions/get_id?petition_url=' + URL + '&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                    response = requests.get(link)
                    results = json.loads(response.text) # load petition short details in json
                    pid = results["petition_id"]    # get petition id
                    qry = {'petition_id': pid}
                    result = petitions.find(qry).count()  # Check if petition is in database
                    if result==0:   # Not a Climate Change related petition
                        continue
                    else:           #Add Climate change petition and tweeted user to the ratings table
                        resR = ratings.find(
                            {"$and": [{"id": t.user.id}, {"petition_id": pid}]}).count()
                        if resR==0:
                            ratingsDict={}
                            #tweetDetails
                            for key, value in t._json.iteritems():
                                ratingsDict["tweet_"+key]=value
                            # petitionDetails
                            ratingsDict["petition_id"]=str(pid)
                            ratingsDict["petition_url"] = URL
                            ratingsDict["rating"] = -1

                            # userDetails
                            for key, value in t._json["user"].iteritems():
                                ratingsDict["user_"+key]=value
                            ts = time.time()
                            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            ratingsDict["CollectedTimeStamp"] = st
                            '''
                            insertRating = '{'
                            insertRating+='"tweetText":"'+t.text+'",'+'"tweetDate":"'+t.created_at+'",'+'"tweetRetweet_count":"'+t.retweet_count+'",'+'"tweetRetweeted":"'+t.retweeted+'",'+'"tweetIn_reply_to_user_id":"'+t.in_reply_to_user_id+'",'+'"tweetPlace":"'+t.place+'",'+'"tweetid":"'+str(t.id)+'",'+'"favorite_count":"'+str(t.favorite_count)+'",'

                            insertRating+='"petition_id":"'+str(pid)+'",'+'"petition_url":"'+URL+'",'+'"CollectedTimeStamp":"'+st+'",'
                            print insertRating
                            print '' \
                                ''
                            tmp=simplejson.dumps(t.user._json, separators=(',', ':'))
                            insertRating+=tmp[1:len(tmp)]
                            print insertRating
                            insertRatingDic=simplejson.loads('[%s]' % insertRating)
                            ratings.insert(insertRatingDic)
                            '''
                            ratings.insert(ratingsDict)
                            resU = sampleUsers.find({"id": t.user.id}).count()  # check if user is already existing in database
                            if resU ==0:    # if does not exist, then add user
                                insert_user(t.user,0,'R')
                        else:
                            ratingsDict = {}
                            cur = ratings.find(
                            {"$and": [{"id": t.user.id}, {"petition_id": pid}]})
                            for rate in cur:
                                rt = rate['rating']
                            if rt == -1:
                                ratingsDict['GT']=0
                            else:
                                ratingsDict['GT']=2
                            # tweetDetails
                            for key, value in t._json.iteritems():
                                ratingsDict["tweet_" + key] = value
                            # petitionDetails
                            ratingsDict["petition_id"] = str(pid)
                            ratingsDict["petition_url"] = URL


                            # userDetails
                            for key, value in t._json["user"].iteritems():
                                ratingsDict["user_" + key] = value
                            ts = time.time()
                            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            ratingsDict["CollectedTimeStamp"] = st
                            '''
                            insertRating = '{'
                            insertRating+='"tweetText":"'+t.text+'",'+'"tweetDate":"'+t.created_at+'",'+'"tweetRetweet_count":"'+t.retweet_count+'",'+'"tweetRetweeted":"'+t.retweeted+'",'+'"tweetIn_reply_to_user_id":"'+t.in_reply_to_user_id+'",'+'"tweetPlace":"'+t.place+'",'+'"tweetid":"'+str(t.id)+'",'+'"favorite_count":"'+str(t.favorite_count)+'",'

                            insertRating+='"petition_id":"'+str(pid)+'",'+'"petition_url":"'+URL+'",'+'"CollectedTimeStamp":"'+st+'",'
                            print insertRating
                            print '' \
                                ''
                            tmp=simplejson.dumps(t.user._json, separators=(',', ':'))
                            insertRating+=tmp[1:len(tmp)]
                            print insertRating
                            insertRatingDic=simplejson.loads('[%s]' % insertRating)
                            ratings.insert(insertRatingDic)
                            '''
                            ratings.update({"$and": [{"user_id": t.user.id}, {"petition_id": str(pid)}]},
                                           {"$set": ratingsDict}, upsert=False)
                            resU = sampleUsers.find(
                                {"id": t.user.id}).count()  # check if user is already existing in database
                            if resU == 0:  # if does not exist, then add user
                                insert_user(t.user, 0, 'R')
                except:
                    continue

def userLabelRetweetingUsers():
    cur = sampleUsers.find({"GT":0})
    for usr in cur:
        cur1=tweets.find({"user_id":usr["id"]})
        for t in cur1:
            try:
                a=tweets.update({"user_id": t["user_id"]},
                           {"$set": {"GT":0}}, upsert=False)
                if a==0:
                    print "why"
            except Exception as e:
                #print 'error in iteration no : ' + str(count) + ' in getting updating the temp table for user : ' + str(dbu['id'])
                print(e)

def gettweetsNumber():
    #ur = sampleUsers.find({"$or": [{"GT": 0}, {"GT": -1}]})
    cur = sampleUsers.find({"GT": 0})
    count=0
    for usr in cur:
        cur1 = tweets.find({"user_id": usr["id"]})
        for t in cur1:
            count+=len(t['id'])
    print count

def main():
    if (api.verify_credentials):
        print 'successfully logged in'
        # change.org twitter account
        # change 15947602 , me 104254763
        changeID = 15947602
        #userLabelRetweetingUsers()
        '''
        cur = tweets.find({"GT": 0})
        Userset = set()
        for usr in cur:
            Userset.add(usr["user_id"])

        cur = sampleUsers.find({"GT": 0})
        for usr in cur:
            if not usr["id"] in Userset:
                print usr["id"]
        '''

        #get_all_tweets(770522409938092032)
        #get_all_tweets(4056968297)
        #get_all_tweets(38045214)
        #get_all_tweets(46371183)
        #get_all_tweets(885617104963211265)
        # Get tweeted petitions to collect user ratings R
       #get_tweeted_petitions()


        # Get Users, friends, tweets and lists from rated users
        #update_user_features_from_ratings()
        '''
        count = 0
        cursor = sampleUsers.find({"rating": 1}, no_cursor_timeout=True)
        # cursor.sort('id',-1)
        for dbu in cursor:
            resT = tweets.find_one({"user_id": dbu["id"]})
            if not resT is None:
                count+=len(resT["id"])
        print count
        #update_users_lists_count()

        cursor = ratings.find({}, no_cursor_timeout=True)
        for r in cursor:
            post={"rating":1}
            sampleUsers.update({'id': r['user_id']}, {"$set": post}, upsert=False)
        '''
        #checkGTImplicitRatings()
        #FilteredUsersTweets()
        gettweetsNumber()


if __name__ == "__main__":
    main()



