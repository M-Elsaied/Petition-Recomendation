import numpy as np
import pandas as pd
from pymongo import MongoClient
from stemming.porter2 import stem
import time
import datetime
from scipy.spatial.distance import cosine, euclidean
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import cross_validation as cv
import matplotlib.pyplot as plt
import TextCleaning
import sys
reload(sys)
sys.setdefaultencoding('utf8')

client = MongoClient('mongodb://localhost:27017/')
collectionUser = client.ClimateChange.UserNew
collectionAllUser = client.ClimateChange.AllUsers
collectionPetition = client.ClimateChange.PetitionNewOpen
client = MongoClient()
db = client.ClimateChange
dbOld = client.ClimateChangeOld
RDb=db.RatingNew
RDu=db.UserNew
RDb_copy=dbOld.Rating_copy


class Recommender:


    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.collectionPetition = client.ClimateChange.PetitionNewOpen
        self.collectionUser = client.ClimateChange.UserNew
        self.rating = db.RatingNew
        self.df= self.read_ratings()
        self.uniquePetitions = self.df["petition_id"].unique()
        self.uniqueUsers = self.df["user_id"].unique()
        all_data = self.df
        n_users = self.uniqueUsers
        self.list_n_users=[]
        for i in n_users:
            self.list_n_users.append(i)
        self.list_n_users.sort()

        n_items=self.uniquePetitions
        self.list_n_items=[]
        for j in n_items:
             self.list_n_items.append(j)
        self.list_n_items.sort()
        petitionsF = self.preparePetitionsFeatures()
        usersF = self.prepareUsersFeatures()
        self.petitionFSorted = {}
        for p in self.list_n_items:
            self.petitionFSorted[p] = petitionsF[p]
        self.userFSorted = {}
        for u in self.list_n_users:
            self.userFSorted[u] = usersF[u]

        self.petitionF_lists = []
        self.petitionIndexRef = {}
        count = 0
        for k, v in self.petitionFSorted.iteritems():
            self.petitionF_lists.append(v)
            self.petitionIndexRef[count] = k
            count += 1

        self.userF_lists = []
        self.userIndexRef = {}
        count = 0
        for k, v in self.userFSorted.iteritems():
            self.userF_lists.append(v)
            self.userIndexRef[count] = k
            count += 1
        from sklearn import cross_validation as cv


        # without splitting to training and validation


        n_usr=len(self.list_n_users)
        n_it = n_items.shape[0]
        # Create training and test matrix
        self.all_R = np.zeros((n_usr, n_it))
        for line in all_data.itertuples():
            self.all_R[self.list_n_users.index(line[1]) , self.list_n_items.index(line[2])] = line[3]


        self.all_I = self.all_R.copy()
        self.all_I[self.all_I > 0] = 1
        self.all_I[self.all_I == 0] = 0

        # dividing data into training and testing
        train_data, test_data = cv.train_test_split(self.df, test_size=0.25)

        train_data = pd.DataFrame(train_data)
        test_data = pd.DataFrame(test_data)

        self.R = np.zeros((n_usr, n_it))
        for line in train_data.itertuples():
            self.R[self.list_n_users.index(line[1]) , self.list_n_items.index(line[2])] = line[3]

        self.T = np.zeros((n_usr, n_it))
        for line in test_data.itertuples():
            self.T[self.list_n_users.index(line[1]), self.list_n_items.index(line[2])] = line[3]

        # Index matrix for training data
        self.I = self.R.copy()
        self.I[self.I > 0] = 1
        self.I[self.I == 0] = 0

        # Index matrix for test data
        self.I2 = self.T.copy()
        self.I2[self.I2 > 0] = 1
        self.I2[self.I2 == 0] = 0


        self.MF_CF_res=None
        self.Con_pet_model = None
        self.Con_pet_res = None
        self.pResults=None
        self.pResultsIndexes=None
        self.uResults=None
        self.uResultsIndexes=None
        self.MF_RStar=None
        self.Con_pRstar=None
        self.Con_uRstar=None
        self.HybRstar=None

    # get number of times a petition was mentioned in ratings
    def getMentions(pid):
        qry = {'id': str(pid)}
        return RDb.find(qry).count()  # 7838075


    def checkDuplicateRatings(self):
        userRatingsids={}

        for ur in RDb.find({'GT':0},no_cursor_timeout=True):
            # user: 804905568502771713, petition: 12912638
            # user: 724425767535300609
            # user: 903243562887860225
            if str(ur['user_id'])+ur['petition_id'] in userRatingsids:
                if userRatingsids[str(ur['user_id'])+ur['petition_id']] == ur['GT']:
                    print 'duplicating: user '+str(ur['user_id'])+' rated petition '+ ur['petition_id']+' with GT: '+str(ur['GT'])
            else:
                userRatingsids[str(ur['user_id']) + str(ur['petition_id'])] = ur['GT']
        for ur in RDb.find({'GT': 1}, no_cursor_timeout=True):
            if str(ur['user_id']) + str(ur['petition_id'])in userRatingsids:
                if userRatingsids[str(ur['user_id']) + str(ur['petition_id'])] == ur['GT']:
                    print 'duplicating: user '+str(ur['user_id'])+' rated petition '+ str(ur['petition_id'])+' with GT: '+str(ur['GT'])
                else:
                    print 'both: user ' + str(ur['user_id']) + ' rated petition ' + str(ur['petition_id']) + ' with GT:0 and 1'
            else:
                userRatingsids[str(ur['user_id']) + str(ur['petition_id'])] = ur['GT']



    # Predict the unknown ratings through the dot product of the latent features for users and items
    def prediction(self,P,Q):
        return np.dot(P.T,Q)

    def MatrixPred(self,P,Q):
        return np.dot(P,Q.T)

    # Calculate the RMSE
    def rmse_hyb(self,I,R,Q,P):
        wMF=0.95
        wPC=0.02
        wUC=0.03
        return np.sqrt(np.sum((I * (R - self.MatrixPred(P,Q)*wMF-self.Con_pRstar*wPC-self.Con_uRstar*wUC))**2)/len(R[R > 0]))


    def rmse(self,I,R,Q,P):
        return np.sqrt(np.sum((I * (R - self.MatrixPred(P,Q)))**2)/len(R[R > 0]))

    def rmse_Rstar(self,I,R,Rstar):
        return np.sqrt(np.sum((I * (R - Rstar))**2)/len(R[R > 0]))


    def read_ratings(self):
        """ Read from Mongo and Store into DataFrame """
        # Ratings cursor
        cursorR = RDb.find({"$or": [{"GT": 0}, {"GT": 1},{"GT": -1}]}, no_cursor_timeout=True)
        # Expand the cursor and construct the DataFrame
        df =  pd.DataFrame(list(cursorR))
        newColumns=['user_id','petition_id','rating']
        df2=df[newColumns]
        print df2.head()
        return df2


    def CF_MF_recommender(self):
        lmbda = 0.1  # Regularisation weight
        k = 20  # Dimensionality of the latent feature space
        m, n = self.R.shape  # Number of users and items
        n_epochs = 100  # Number of epochs
        gamma = 0.01  # Learning rate

        # unknown user and items features

        P = np.random.rand(m,k)  # initial user feature matrix with random numbers
        Q = np.random.rand(n,k)  # initial petition feature matrix with random numbers
        train_errors = []
        test_errors = []
        # Only consider non-zero matrix
        users, items = self.R.nonzero()
        for epoch in xrange(n_epochs):
            for u, i in zip(users, items):
                e = self.R[u, i] - self.prediction(P[u,:], Q[i,:])  # Calculate error for gradient
                P[u,:] += gamma * (e * Q[i,:] - lmbda * P[u,:])  # Update latent user feature matrix
                Q[i,:] += gamma * (e * P[u,:] - lmbda * Q[i,:])  # Update latent petition feature matrix
            train_rmse = self.rmse(self.I, self.R, Q, P)  # Calculate root mean squared error from train dataset
            test_rmse = self.rmse(self.I2, self.T, Q, P)  # Calculate root mean squared error from test dataset
            train_errors.append(train_rmse)
            test_errors.append(test_rmse)
        self.MF_RStar=self.MatrixPred(P,Q)

        # Compute RMSE
        # Check performance by plotting train and test errors
        plt.plot(range(n_epochs), train_errors, marker='o', label='Training Data');
        plt.plot(range(n_epochs), test_errors, marker='v', label='Test Data');
        plt.title('SGD-WR MF Learning Curve')
        plt.xlabel('Number of Epochs');
        plt.ylabel('RMSE');
        plt.legend()
        plt.grid()
        plt.show()


    def nonRatingUsersAndPetitions(self):
        for u in self.collectionUser.find({"$or": [{"GT": 0}, {"GT": 1}, {"GT": -1}]}, no_cursor_timeout=True):
            for p in collectionPetition.find({}, no_cursor_timeout=True):
                post={}
                post['user_id']=u['id_str']
                post['petition_id']=p['petition_id']
                post['rating']=0
                post['GT']=-1
                ratingCount = RDb.find({"$and": [{'user_id': u['id_str']}, {'petition_id': p['petition_id']}]}).count()  # check if user is already existing in database
                if ratingCount == 0:  # if does not exist, then add ratings
                    RDb.update({"$and": [{'user_id': u['id_str']}, {'petition_id': p['petition_id']}]}, {"$set": post}, upsert=True)


    def updateDataType(self):
        cur = self.rating.find({"$or": [{"GT": 0}, {"GT": 1}, {"GT": -1}]})
        #cur = RDb.find({"GT": -1})
        for r in cur:
            post={}
            post['petition_id']=int(r['petition_id'])
            post['user_id'] = str(r['user_id'])
            RDb.update({"$and": [{'user_id': r['user_id']}, {'petition_id': r['petition_id']}]}, {"$set": post}, upsert=False)


    def preparePetitionsFeatures(self):
        petitionsF={}
        for p in self.collectionPetition.find({}, no_cursor_timeout=True):
            features=[]
            wc=0
            if p['LIWC_WC']<100:
                wc=0
            else:
                wc=1
            if p['image_url']:
                pic=1
            else:
                pic=0

            features.append(pic)

            features.append(wc)
            features.append(p['petitionLength_norm'])
            features.append(p['avg_len_sentences_words_norm'])
            features.append(p['positive_norm'])
            features.append(p['negative_norm'])
            features.append(p['enlightenment_norm'])
            features.append(p['overstatement_norm'])
            features.append(p['understatement_norm'])
            features.append(p['moral_norm'])
            features.append(p['expressivness'])
            features.append(p['pronoun_norm'])


            features.append(p['supporters_remaining_percent'])
            features.append(p['Twitter_mentions_norm'])
            features.append(p['reasons_count_norm'])
            features.append(p['updates_count_norm'])

            for i in range(50):
                features.append(p['TFIDF_LDA_50topics_topic'+str(i)])

            petitionsF[p['petition_id']]=features
        return petitionsF

    def prepareUsersFeatures(self):
        cur = self.collectionUser.find({"$or": [{"GT": 0}, {"GT": 1}, {"GT": -1}]})
        usersF={}
        max_statuses_count=0
        max_followers_count=0
        max_friends_count=0
        max_listed_count=0
        max_tweetsFavorite_count=0
        max_tweetsRetweets_count=0
        max_tweetsHashtags=0
        max_tweetAvgLength=0
        for u in cur:
            if u['statuses_count']>max_statuses_count:
                max_statuses_count=u['statuses_count']
            if u['followers_count']>max_followers_count:
                max_followers_count=u['followers_count']
            if u['friends_count']>max_friends_count:
                max_friends_count=u['friends_count']
            if u['listed_count']>max_listed_count:
                max_listed_count=u['listed_count']
            if u['tweetsFavorite_count']> max_tweetsFavorite_count:
                max_tweetsFavorite_count=u['tweetsFavorite_count']
            if u['tweetsRetweets_count']>max_tweetsRetweets_count:
                max_tweetsRetweets_count=u['tweetsRetweets_count']
            if u['tweetsHashtags']>max_tweetsHashtags:
                max_tweetsHashtags=u['tweetsHashtags']
            if u['tweetAvgLength']>max_tweetAvgLength:
                max_tweetAvgLength=u['tweetAvgLength']
            features=[]
            features.append(u['statuses_count'])
            features.append(u['followers_count'])
            features.append(u['friends_count'])
            features.append(u['listed_count'])
            features.append(u['tweetsFavorite_count'])
            features.append(u['tweetsRetweets_count'])
            features.append(u['tweetsHashtags'])
            features.append(u['tweetAvgLength'])
            features.append(u['expressivness'])

            for i in range(50):
                features.append(u['TFIDF_LDA_50topics_topic'+str(i)])
            usersF[u['id_str']]=features

        for key in usersF:
            usersF[key][0]=usersF[key][0]/max_statuses_count
            usersF[key][1]=usersF[key][1]/max_followers_count
            usersF[key][2]=usersF[key][2]/max_friends_count
            usersF[key][3] = usersF[key][3] / max_listed_count
            usersF[key][4] = usersF[key][4] / max_tweetsFavorite_count
            usersF[key][5] = usersF[key][5] / max_tweetsRetweets_count
            usersF[key][6] = usersF[key][6] / max_tweetsHashtags
            usersF[key][7] = usersF[key][7] / max_tweetAvgLength

        return usersF

    def contF_recommenderPetitions_model(self):
        petitions_cosine_similarities = linear_kernel(np.array(self.petitionF_lists))
        count=0
        results = {}
        resultsIndexes={}
        for idx, row in self.petitionFSorted.iteritems():
                similar_indices = petitions_cosine_similarities[count].argsort()[:-10:-1]
                similar_items = [(petitions_cosine_similarities[count][i], self.petitionFSorted[idx]) for i in similar_indices]

                # First item is the item itself, so remove it.
                # Each dictionary entry is like: [(1,2), (3,4)], with each tuple being (score, item_id)
                results[idx] = similar_items[1:]
                resultsIndexes[idx]=similar_indices[1:]
                count+=1
        count=0
        '''
        for i in results:
            print i
            print ""
            print ""
            count+=1
        '''
        print('done!')
        self.pResults=results
        self.pResultsIndexes=resultsIndexes
        return

    def contF_recommenderUsers_model(self):
        users_cosine_similarities = linear_kernel(np.array(self.userF_lists))
        count=0
        results = {}
        resultsIndexes={}
        for idx, row in self.userFSorted.iteritems():
                similar_indices = users_cosine_similarities[count].argsort()[:-10:-1]
                similar_items = [(users_cosine_similarities[count][i], self.userFSorted[idx]) for i in similar_indices]

                # First item is the item itself, so remove it.
                # Each dictionary entry is like: [(1,2), (3,4)], with each tuple being (score, item_id)
                results[idx] = similar_items[1:]
                resultsIndexes[idx]=similar_indices[1:]
                count+=1
        count=0
        '''
        for i in results:
            print i
            print ""
            print ""
            count+=1
        '''
        print('done!')
        self.uResults=results
        self.uResultsIndexes=resultsIndexes
        return


    def contF_recommenderUsers_BoW(self):
        temp_usersF={}
        usersF = {}
        results={}
        resultsIndexes={}
        desc=[]
        for p in self.collectionUser.find({"$or": [{"GT": 0}, {"GT": 1}, {"GT": -1}]}):
            st=TextCleaning.strip_tags(p['LDA_cleanedDescription'].decode('utf-8').strip().lower())
            temp_usersF[p['id_str']]=st
            desc.append(st)
        print('Number of words (after pre-processing) in the corpus = ',
              len(set([word for w in desc for word in w])))
        for k in self.userFSorted:
            usersF[k]=temp_usersF[k]
        tf = TfidfVectorizer(analyzer='word', stop_words='english')

        #ds=pd.DataFrame(usersF.items(), columns=['petition_id', 'description'])

        tfidf_matrix = tf.fit_transform(desc)
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        count=0
        for idx, row in usersF.iteritems():
            similar_indices = cosine_similarities[count].argsort()[:-10:-1]
            similar_items = [(cosine_similarities[count][i], usersF[idx]) for i in similar_indices]
            #similar_indices = cosine_similarities[count].argsort()[:-10:-1]
            #similar_items = [(cosine_similarities[count][i], ds['petition_id'][i]) for i in similar_indices]
            # First item is the item itself, so remove it.
            # Each dictionary entry is like: [(1,2), (3,4)], with each tuple being (score, item_id)
            results[count] = similar_items[1:]
            resultsIndexes[count] = similar_indices[1:]
            count += 1
        count = 0
        users, items = self.all_R.nonzero()
        Con_BoW_pRstar=self.all_R.copy()
        for u, i in zip(users, items):
            # compute weighted average petition based similarity rating
            real = self.all_R[u][i]
            count = 0
            wAvg = 0
            simSum = 0
            petition = self.list_n_items[i]
            user = self.list_n_users[u]
            for sim in results[u]:
                C = resultsIndexes[u][count]
                spetition = self.list_n_items[C]
                A = self.all_R[C][i]
                B = sim[0]
                wAvg += A * B
                simSum += sim[0]
                count += 1
            if simSum==0:
                wAvg=0
            else:
                wAvg = float(wAvg) / (simSum)
            Con_BoW_pRstar[u][i] = wAvg

        rmse = self.rmse_Rstar(self.all_I, self.all_R,
                               Con_BoW_pRstar)  # Calculate root mean squared error from dataset
        print rmse



    def contF_recommenderPetitions_BoW(self):
        temp_petitionsF={}
        petitionsF = {}
        results={}
        resultsIndexes={}
        desc=[]
        for p in self.collectionPetition.find({}, no_cursor_timeout=True):
            st=TextCleaning.strip_tags(p['title'].decode('utf-8').strip().lower() + " " + p['overview'].decode('utf-8').strip().lower())
            temp_petitionsF[p['petition_id']]=st
            desc.append(st)
        print('Number of words (after pre-processing) in the corpus = ',
              len(set([word for w in desc for word in w])))
        for k in self.petitionFSorted:
            petitionsF[k]=temp_petitionsF[k]
        tf = TfidfVectorizer(analyzer='word', stop_words='english')

        #ds=pd.DataFrame(petitionsF.items(), columns=['petition_id', 'description'])

        tfidf_matrix = tf.fit_transform(desc)
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        count=0
        for idx, row in petitionsF.iteritems():
            similar_indices = cosine_similarities[count].argsort()[:-10:-1]
            similar_items = [(cosine_similarities[count][i], petitionsF[idx]) for i in similar_indices]
            #similar_indices = cosine_similarities[count].argsort()[:-10:-1]
            #similar_items = [(cosine_similarities[count][i], ds['petition_id'][i]) for i in similar_indices]
            # First item is the item itself, so remove it.
            # Each dictionary entry is like: [(1,2), (3,4)], with each tuple being (score, item_id)
            results[count] = similar_items[1:]
            resultsIndexes[count] = similar_indices[1:]
            count += 1
        count = 0
        users, items = self.all_R.nonzero()
        Con_BoW_pRstar=self.all_R.copy()
        for u, i in zip(users, items):
            # compute weighted average petition based similarity rating
            real = self.all_R[u][i]
            count = 0
            wAvg = 0
            simSum = 0
            petition = self.list_n_items[i]
            user = self.list_n_users[u]
            for sim in results[i]:
                C = resultsIndexes[i][count]
                spetition = self.list_n_items[C]
                A = self.all_R[u][C]
                B = sim[0]
                wAvg += A * B
                simSum += sim[0]
                count += 1
            wAvg = float(wAvg) / (simSum)
            Con_BoW_pRstar[u][i] = wAvg

        rmse = self.rmse_Rstar(self.all_I, self.all_R,
                               Con_BoW_pRstar)  # Calculate root mean squared error from dataset
        print rmse

    def contF_recommenderPetitions(self):
        # Only consider non-zero matrix
        users, items = self.all_R.nonzero()
        self.Con_pRstar=self.all_R.copy()
        for u, i in zip(users, items):
            # compute weighted average petition based similarity rating
            real = self.all_R[u][i]
            count=0
            wAvg=0
            simSum=0
            petition=self.list_n_items[i]
            user=self.list_n_users[u]
            for sim in self.pResults[self.petitionIndexRef[i]]:
                C=self.pResultsIndexes[self.petitionIndexRef[i]][count]
                spetition=self.list_n_items[C]
                A=self.all_R[u][C]
                B=sim[0]
                wAvg+=A*B
                simSum+=sim[0]
                count+=1
            wAvg=float(wAvg)/(simSum)
            self.Con_pRstar[u][i]=wAvg

        rmse = self.rmse_Rstar(self.all_I, self.all_R, self.Con_pRstar)  # Calculate root mean squared error from dataset
        print rmse

    def contF_recommenderUsers(self):
        # Only consider non-zero matrix
        users, items = self.all_R.nonzero()
        self.Con_uRstar = self.all_R.copy()
        for u, i in zip(users, items):
            # compute weighted average petition based similarity rating
            real = self.all_R[u][i]
            count = 0
            wAvg = 0
            simSum = 0
            petition = self.list_n_items[i]
            user = self.list_n_users[u]
            for sim in self.uResults[self.userIndexRef[u]]:
                C = self.uResultsIndexes[self.userIndexRef[u]][count]
                suser = self.list_n_users[C]
                A = self.all_R[C][i]
                B = sim[0]
                wAvg += A * B
                simSum += sim[0]
                count += 1
            if simSum==0:
                wAvg=0
            else:
                wAvg = float(wAvg) / (simSum)
            self.Con_uRstar[u][i] = wAvg

        rmse = self.rmse_Rstar(self.all_I, self.all_R,
                               self.Con_uRstar)  # Calculate root mean squared error from dataset
        print rmse


    def Hybrid_recommender(self):
        lmbda = 0.1  # Regularisation weight
        k = 20  # Dimensionality of the latent feature space
        m, n = self.R.shape  # Number of users and items
        n_epochs = 100  # Number of epochs
        gamma = 0.01  # Learning rate


        # unknown user and items features

        P = np.random.rand(m,k)  # initial user feature matrix with random numbers
        Q = np.random.rand(n,k)  # initial petition feature matrix with random numbers
        train_errors = []
        test_errors = []
        # Only consider non-zero matrix
        users, items = self.R.nonzero()
        for epoch in xrange(n_epochs):
            for u, i in zip(users, items):
                e = self.R[u, i] - self.prediction(P[u,:], Q[i,:])  # Calculate error for gradient
                P[u,:] += gamma * (e * Q[i,:] - lmbda * P[u,:])  # Update latent user feature matrix
                Q[i,:] += gamma * (e * P[u,:] - lmbda * Q[i,:])  # Update latent petition feature matrix
            train_rmse = self.rmse_hyb(self.I, self.R, Q, P)  # Calculate root mean squared error from train dataset
            test_rmse = self.rmse_hyb(self.I2, self.T, Q, P)  # Calculate root mean squared error from test dataset
            train_errors.append(train_rmse)
            test_errors.append(test_rmse)
        self.HybRstar=self.MatrixPred(P,Q)

        # Compute RMSE
        # Check performance by plotting train and test errors
        plt.plot(range(n_epochs), train_errors, marker='o', label='Training Data');
        plt.plot(range(n_epochs), test_errors, marker='v', label='Test Data');
        plt.title('SGD-WR MF Learning Curve')
        plt.xlabel('Number of Epochs');
        plt.ylabel('RMSE');
        plt.legend()
        plt.grid()
        plt.show()



def main():
    #delete_extra_user_rating()
    #update_ratings()
    #nonRatingUsersAndPetitions()
    #updateDataType()
    #checkDuplicateRatings()
    obj = Recommender()

    #obj.CF_MF_recommender()


    print "Ratings: %d" % len(obj.df)
    print "Unique users: %d" % len(obj.uniquePetitions)
    print "Unique petitions: %d" % len(obj.uniqueUsers)
    Users=obj.df["user_id"].unique()
    Petitions=obj.df["petition_id"].unique()
    dense_matrix = obj.df.pivot_table(values="rating", index=["user_id"], columns=["petition_id"])
    print "Shape of the user-item matrix: %d x %d" % dense_matrix.shape
    #print dense_matrix.isnan().sum() #np.isnan(dense_matrix).count()

    # Petition based filtering

    obj.contF_recommenderPetitions_model()
    obj.contF_recommenderPetitions()

    #obj.contF_recommenderPetitions_BoW()

    # user based filtering
    obj.contF_recommenderUsers_model()
    obj.contF_recommenderUsers()

    obj.contF_recommenderUsers_BoW()


    # hybrid
    #obj.Hybrid_recommender()


    '''


    df_data=read_ratings()


    #a=dense_matrix.isnull().sum(axis=1)
    print dense_matrix['rating']

    dense_matrix = dense_matrix.fillna(-1)
    print dense_matrix.head()
    '''

    '''
    ccPetitions=[]
    for p in collectionPetition.find({}, no_cursor_timeout=True):
        ccPetitions.append(p['petition_id'])
    for p in RDb.find({}, no_cursor_timeout=True):
        if not p[petition] in ccPetitions:
            print p

    '''

    #print setQRecommender()
    #unifyUser()
    #print setPRecommender()
    #update_Petition_LDA()
    #recommender()
    #print setPRecommenderMissing()
    #print count_users_network()
    #print count_users_tweets()
    #print count_users_subsciptions()
    #print count_users_memberships()



if __name__ == '__main__':
    main()

    # user: 804905568502771713, petition: 12912638
    # user: 724425767535300609
    # user: 903243562887860225