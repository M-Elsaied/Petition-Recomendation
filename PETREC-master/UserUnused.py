
# Convert user to dictionary
def insertUserDict(user):
    dic = {}
    dic['_id'] = user['_id']
    dic['has_extended_profile'] = user.has_extended_profile
    dic['profile_use_background_image'] = user.profile_use_background_image
    dic['live_following'] = user.live_following
    dic['default_profile_image'] = user.default_profile_image
    dic['id'] = user.id
    dic['profile_background_image_url_https'] = user.profile_background_image_url_https
    dic['translator_type'] = user.translator_type
    dic['verified'] = user.verified
    dic['blocked_by'] = user.blocked_by
    dic['profile_text_color'] = user.profile_text_color
    dic['muting'] = user.muting
    dic['profile_image_url_https'] = user.profile_image_url_https
    dic['profile_sidebar_fill_color'] = user.profile_sidebar_fill_color
    dic['entities'] = user.entities
    dic['followers_count'] = user.followers_count
    dic['profile_sidebar_border_color'] = user.profile_sidebar_border_color
    dic['id_str'] = user.id_str
    dic['profile_background_color'] = user.profile_background_color
    dic['listed_count'] = user.listed_count
    dic['status'] = user.status
    dic['is_translation_enabled'] = user.is_translation_enabled
    dic['utc_offset'] = user.utc_offset
    dic['statuses_count'] = user.statuses_count
    dic['description'] = user.description
    dic['friends_count'] = user.friends_count
    dic['location'] = user.location
    dic['profile_link_color'] = user.profile_link_color
    dic['profile_image_url'] = user.profile_image_url
    dic['following'] = user.following
    dic['geo_enabled'] = user.geo_enabled
    dic['blocking'] = user.blocking
    dic['profile_background_image_url'] = user.profile_background_image_url
    dic['screen_name'] = user.screen_name
    dic['lang'] = user.lang
    dic['profile_background_title'] = user.profile_background_title
    dic['favourites_count'] = user.favourites_count
    dic['name'] = user.name
    dic['notifications'] = user.notifications
    dic['url'] = user.url
    dic['created_at'] = user.created_at
    dic['contributors_enabled'] = user.contributors_enabled
    dic['time_zone'] = user.time_zone
    dic['protected'] = user.protected
    dic['default_profile'] = user.default_profile
    dic['is_translator'] = user.is_translator
    try:
        dic['CollectedTimeStamp'] = user.CollectedTimeStamp
    except:
        print 'no collected time stamp for user: '+str(user.id)
    try:
        dic['memberships'] = user.memberships
    except:
        print 'no memberships for user: '+str(user.id)
    try:
        dic['subscriptions'] = user.subscriptions
    except:
        print 'no subscriptions for user: '+str(user.id)
    try:
        dic['ChangeFollower'] = user.ChangeFollower
    except:
        print 'no ChangeFollower for user: '+str(user.id)
    try:
        dic['friendsList'] = user.friendsList
    except:
        print 'no friendsList for user: '+str(user.id)
    try:
        dic['tweets'] = user.tweets
    except:
        print 'no tweets for user: '+str(user.id)
    try:
        dic['tweets_all'] = user.tweets_all
    except:
        print 'no tweets_all for user: '+str(user.id)
    return dic


# insert lists
def insert_lists(lists,i):
    count = 0
    for l in lists:
        try:
            print l
            #collectionUser.insert(u._json)
        except:
            print "error" + str(count)+" in "+str(i)
        count += 1
    return users


def get_lists(user_id):
    lists = []
    page_count = 0
    for i,groupLists in enumerate(tweepy.Cursor(api.list_members(settings['screen_name']), id=user_id, count=200).pages()):
        print 'Getting page {} for followers'.format(i)
        lists+=groupLists
        insert_lists(groupLists,i)
        l=len(lists)
        '''data = api.rate_limit_status()

        print data['resources']['statuses']['/statuses/home_timeline']
        print data['resources']['users']['/users/lookup']'''
        if i==0:
            print 'went through'
            break
        if (i!=0 and i%14==0):
            time.sleep(901)
    return users

def process_user(user):
    user_id = user['id']
    screen_name = user['screen_name']
    print 'Processing user : {}'.format(screen_name)

    the_user = get_user_from_db(user_id)
    if the_user is None:
        user['followers_ids'] = get_followers_ids(user['screen_name'])
        user['friends_ids'] = get_friends_ids(user['screen_name'])

        users_to_add = []

        users_to_add = [follower._json for follower in
                        get_followers(screen_name) if not is_user_in_db(follower.id)]
        users_to_add += [friend._json for friend in
                         get_friends(screen_name) if not is_user_in_db(friend.id)]
        '''for follower in get_followers(screen_name):
            if not is_user_in_db(follower.id):
                users_to_add.append(follower._json)

        for friend in get_friends(screen_name):
            if not is_user_in_db(friend.id):
                users_to_add.append(friend._json)'''

        users.insert_many(users_to_add)
        #users.insert_one(doc['user'])


def test():

    '''pid = 7838075
    a = {'petition_id': pid}
    results = petitions.find(a).count()  # 7838075
    print str(results)'''
    url=getURL("https://t.co/z7wJ1Q2xjH Help to ban #cat mutilation in Canada! Plz sign: https://t.co/Oiose855cI")
    print url

    twt="https://t.co/z7wJ1Q2xjH Help to ban #cat mutilation in Canada! Plz sign: https://t.co/Oiose855cI"
    print twt.replace(old,"")

def get_lists():
    # Loop on all users
    for u in users.find({}, no_cursor_timeout=True):
        print u['id']
        post = {}
        try:
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(10)  # 10 seconds
            # Get memebership lists
            try:
                memberships = api.lists_memberships(id=u['id'])
            except Exception, msg:
                print "Timed out!"
            post['memberships'] = []
            # Loop on membership lists
            for m in memberships:
                # Convert list to dictionary
                dic = insertListDict(m)
                # Add list dictionary as entry in membership list
                post['memberships'].append(dic)
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(10)  # 10 seconds

            # Get subscription lists
            try:
                subsciptions = api.lists_subscriptions(id=u['id'])
            except Exception, msg:
                print "Timed out!"
            post['subscriptions'] = []
            # Loop on subscription lists
            for s in subsciptions:
                # Convert list to dictionary
                dic = insertListDict(s)
                # Add list dictionary as entry in subscription list
                post['subscriptions'].append(dic)
            # Update user with subscription and membership lists
            users.update({'id': u['id']}, {"$set": post}, upsert=True)
        except Exception as e:
            print(e)

def get_user_friendsOld(uid):
    try:
        users = []
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(15)  # 5 seconds
        count=0

        for i, groupUsers in enumerate(tweepy.Cursor(api.friends, id=uid, count=100).pages()):
            print 'Getting page {} for friends'.format(i)
            for u in groupUsers:
                if u.protected==True:
                    continue
                exc = False
                fu_id = u.id
                qry = {'id': fu_id}
                result = collectionUser.find(qry).count()  # 7838075
                users.append(fu_id)
                if result == 0:  # not found insert user and unknown changeFollower type=""
                    insert_user(u, i, "-")
                    try:
                        get_user_lists(fu_id)
                        get_all_tweets(fu_id)
                    except Exception as e:
                        exc = True
                        print(e)
                        print 'error in getting lists and tweets for user: '+str(fu_id)
                        continue
                else:  # user already exists either change.org follower or friend of other user
                    # case did not get lists
                    userPost={}
                    try:
                        userCur=collectionUser.find_one(qry)
                        #userPost=insertUserDict(userCur)
                        tmp.update({'id': fu_id}, {"$set": userCur}, upsert=True)
                        if userCur['protected']==False:
                            result2 = collectionUser.find(
                                {"$and": [{"id": fu_id}, {"subscriptions": {'$exists': True}}]}).count()
                            if result2 == 0:
                                try:
                                    get_user_lists(fu_id)
                                except Exception as e:
                                    exc = True
                                    print(e)
                                    print 'error in getting lists for user: ' + str(fu_id)
                                    continue
                            resultTweets = collectionUser.find(
                                {"$and": [{"id": fu_id}, {"tweets_all": {'$exists': True}}]}).count()
                            if resultTweets ==0:
                                try:
                                    get_all_tweets(fu_id)
                                except:
                                    exc = True
                                    print 'error in getting tweets for user: ' + str(fu_id)

                        else:
                            continue
                    except:
                        exc = True
                        print(e)
                        print 'error an existing from user table to UserTemp user: ' + str(fu_id)
                #if exc==False :
                count+=1
                if count==100:
                    break
            if count==100:
                break
        try:
            print users
            print '' \
                  ''
            post = {}
            post['friendsList'] = users
            collectionUser.update({'id': uid}, {"$set": post}, upsert=True)
            tmp.update({'id': uid}, {"$set": post}, upsert=True)
        except Exception as e:
            print "error in friends of " + str(uid)
            print(e)
    except Exception as e:
        print(e)

# update friends
def update_user_friends_membership():
    cursor=sampleUsers.find({"l": 1}, no_cursor_timeout=True)
    count=0
    total=0
    try:
        # Loop on all friends
        for dbu in cursor:
            for friend in dbu['friendsList']:
                qry = {'id': friend}
                userPost = {}
                total+=1
                try:
                    userCur = sampleUsers.find_one(qry)
                    # userPost=insertUserDict(userCur)
                    #tmp.update({'id': fu_id}, {"$set": userCur}, upsert=True)
                    if userCur['protected'] == False:
                        resultS = sampleUsers.find(
                            {"$and": [{"id": friend}, {"subscriptions": {'$exists': True}}]}).count()
                        resultM = sampleUsers.find(
                            {"$and": [{"id": friend}, {"memberships": {'$exists': True}}]}).count()
                        if resultS == 0 and resultM ==0:
                            try:
                                get_user_lists(friend)
                            except Exception as e:
                                exc = True
                                #print(e)
                                print 'error in it no' + str(count) + 'getting lists for friend: ' + str(friend) + 'of user: ' + str(dbu['id'])
                                continue
                    else:
                        continue
                except:
                    exc = True
                    #print(e)
                    print 'error in it no'+str(count)+'getting friend: '+str(friend)+ 'of user: '+str(dbu['id'])
                    # if exc==False :
            count += 1
            print 'it'+str(count)+'total number: '+str(total)
    except Exception as e:
        #print(e)
        print 'aaa'


def is_user_in_db(user_id):
    return get_user_from_db(user_id) is None


def get_user_from_db(user_id):
    return users.find_one({'user.id': user_id})


def get_user_from_twitter(user_id):
    return api.get_user(user_id)


def get_followers(user_id):
    users = []
    page_count = 0
    for i, user in enumerate(tweepy.Cursor(api.followers, id=user_id, count=200).pages()):
        print 'Getting page {} for followers'.format(i)
        users += user
    return users


def get_friends(user_id):
    users = []
    page_count = 0
    for user in tweepy.Cursor(api.friends, id=user_id, count=200).pages():
        page_count += 1
        print 'Getting page {} for friends'.format(page_count)
        users.extend(user)
    return users


def get_followers_ids(user_id):
    ids = []
    page_count = 0
    for page in tweepy.Cursor(api.followers_ids, id=user_id, count=5000).pages():
        page_count += 1
        print 'Getting page {} for followers ids'.format(page_count)
        ids.extend(page)

    return ids


def get_friends_ids(user_id):
    ids = []
    page_count = 0
    for page in tweepy.Cursor(api.friends_ids, id=user_id, count=5000).pages():
        page_count += 1
        print 'Getting page {} for friends ids'.format(page_count)
        ids.extend(page)
    return ids


def process_user(user):
    user_id = user['id']
    screen_name = user['screen_name']
    print 'Processing user : {}'.format(user['screen_name'])

    the_user = get_user_from_db(user_id)
    if the_user is None:
        follower_ids = get_followers_ids(user['screen_name'])
        friend_ids = get_friends_ids(user['screen_name'])

        user['followers_ids'] = follower_ids
        user['friends_ids'] = friend_ids

        users_to_add = []
        for follower in get_followers(screen_name):
            if not is_user_in_db(follower.id):
                users_to_add.append(follower._json)

        for friend in get_friends(screen_name):
            if not is_user_in_db(friend.id):
                users_to_add.append(friend._json)

        users.insert_many(users_to_add)
        users.insert_one(doc['user'])


def main():
    if (api.verify_credentials):
        print 'successfully logged in'
        # change.org twitter account
        # change 15947602 , me 104254763
        changeID = 15947602

        # Get tweeted petitions to collect user ratings R
        get_tweeted_petitions()

        # Get Users, friends, tweets and lists from rated users
        update_user_features_from_ratings()



        #lists=get_lists(104254763)
        '''for l in lists:
            print l
            print '*******************************************'
            print '' \
                  ''
            print '' \
                  ''
            print '' \
                  ''
            print '' \
                  ''
        #sys.exit(1)'''

        #get_lists()
        #get_tweets()
        #test()
        #removeDupRatings()
        #get_users_tweets()
        #get_user_from_ratings()
        #get_update_users()
        #get_non_rating_users()
        #update_all_tweets_users()
        #update_user_friends_membership()
        #[2485308468, 761101414080786432, 704259908334583808,
        #ids =  [2485444494,759364128456732672, 231820645]
        #ids=[615834862, 781671033803829248]
        #ids=[2732117643]
        # db.getCollection('UserTemp').find({'id':736751154869080066}) not in table
        # 2732117643 no membership
        #usr=get_user_from_twitter(736751154869080066)
        #insert_user(usr,0,'-')
        #get_user_lists(2732117643)
        #for id in ids:
            #get_user_friends(id)
        get_tweets_dates()