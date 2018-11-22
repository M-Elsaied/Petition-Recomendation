from scrapy.spider import BaseSpider
from scrapy.http import HtmlResponse
from selenium import webdriver
from pymongo import MongoClient
import time
import datetime
import requests
import json
import simplejson
import re
import string
import nltk
from nltk.corpus import stopwords
import TextCleaning

# Crawling spider for Change.org Climate Change opened petitions
class ChangeSpider(BaseSpider):
    driver2 = webdriver.Firefox()
    strIns=''
    name = "change_spider"
    allowed_domains = ['change.org']

    # Search by climate change reference carvahlo,2007
    #start_urls = "https://www.change.org/search?q=" + "climate%20change"+"&offset="
    #start_urls = "https://www.change.org/search?q=" + "global%20warming" + "&offset="
    #start_urls = "https://www.change.org/search?q=" + "greenhouse" + "&offset="

    def get_expression(self):
        verbNoun=['VBZ','VBP','VBN','VBG','VBD','VB','NNS','NNPS','NNP','NN']
        adverbAdjectives=['WRB','RBS','RBR','RB','JJS','JJR','JJ']
        articles = self.petitionDocs
        cur=articles.find({}, no_cursor_timeout=True)
        #cur1=cur.sort('petition_id', 1)
        #cursor=cur1.limit(int(self.Eighty))
        doc_complete=[]
        doc_clean=[]
        doc_completeT=[]
        doc_cleanT=[]
        tList=[]
        tListT = []
        count=0
        exclude = set(string.punctuation)
        stop = set(stopwords.words('english'))
        lines = open("stop3").read().splitlines()
        for word in lines:
            print word
            stop.add(word)
        mysqlStop = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all",
                     "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst",
                     "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway",
                     "anywhere", "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes",
                     "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides",
                     "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co",
                     "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due",
                     "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc",
                     "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen",
                     "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found",
                     "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have",
                     "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself",
                     "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed",
                     "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least",
                     "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
                     "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither",
                     "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing",
                     "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
                     "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
                     "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
                     "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
                     "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system",
                     "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there",
                     "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin",
                     "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to",
                     "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until",
                     "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
                     "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon",
                     "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose",
                     "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself",
                     "yourselves", "the"]
        for word in mysqlStop:
            stop.add(word)

        for p in cur:
            #strip HTML tags from tweet
            try:
                #9969533
                if p['petition_id']==9969533:
                    strip = TextCleaning.strip_tags(p['title'].encode('UTF-8', errors='ignore') + " " + p['overview'].encode('UTF-8',errors='ignore'))
                strip = TextCleaning.strip_tags(p['title'].encode('UTF-8',errors='ignore')+" "+p['overview'].encode('UTF-8',errors='ignore'))
            except Exception as e:
                print ''
                print strip
            doc_complete.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) \
                 if w.lower() in words or not w.isalpha())
            EnCleanedDoc = unicode(EnCleanedDoc, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            posTag = nltk.pos_tag(text)
            countAdjAdv=0
            countNounVerb=0
            for cat in posTag:
                if cat[1] in verbNoun:
                    countNounVerb+=1
                elif cat[1] in adverbAdjectives:
                    countAdjAdv+=1
            if countNounVerb ==0:
                expressivness=0
            else:
                expressivness=float(countAdjAdv) / float(countNounVerb)
            self.petitionDocs.update({"petition_id": p['petition_id']}, {"$set": {"expressivness":expressivness}}, False, False)

    # Open URL in driver
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.petitionDocs = self.db.PetitionNewOpen
        self.driver = webdriver.Firefox()

    def checkExistingPetition(self, petition_id):
        client = MongoClient('mongodb://localhost:27017/')
        collectionOpened = client.ClimateChange.PetitionNew
        collectionClosed = client.ClimateChange.PetitionNewClosed
        collectionVictory = client.ClimateChange.PetitionNewVictory
        resP = collectionOpened.find({"petition_id": int(petition_id)}).count()
        resPC = collectionClosed.find({"petition_id": int(petition_id)}).count()
        resPV = collectionVictory.find({"petition_id": int(petition_id)}).count()
        if resP+resPC+resPV == 0:
            return False
        else:
            return True

    def normalizedfeatures(self):

        cur=self.db.PetitionNewOpen.find().sort([("GI_Ovrst", -1)]).limit(1)
        for i in cur:
            max_GI_Ovrst=i['GI_Ovrst']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_certain", -1)]).limit(1)
        for i in cur:
            max_LIWC_certain=i['LIWC_certain']
        cur=self.db.PetitionNewOpen.find().sort([("GI_Undrst", -1)]).limit(1)
        for i in cur:
            max_GI_Undrst=i['GI_Undrst']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_tentat", -1)]).limit(1)
        for i in cur:
            max_LIWC_tentat=i['LIWC_tentat']
        cur=self.db.PetitionNewOpen.find().sort([("GI_EnlTot", -1)]).limit(1)
        for i in cur:
            max_GI_EnlTot=i['GI_EnlTot']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_insight", -1)]).limit(1)
        for i in cur:
            max_LIWC_insight=i['LIWC_insight']
        cur=self.db.PetitionNewOpen.find().sort([("GI_Positiv", -1)]).limit(1)
        for i in cur:
            max_GI_Positiv=i['GI_Positiv']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_posemo", -1)]).limit(1)
        for i in cur:
            max_LIWC_posemo=i['LIWC_posemo']
        cur=self.db.PetitionNewOpen.find().sort([("GI_Negativ", -1)]).limit(1)
        for i in cur:
            max_GI_Negativ=i['GI_Negativ']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_negemo", -1)]).limit(1)
        for i in cur:
            max_LIWC_negemo=i['LIWC_negemo']
        cur=self.db.PetitionNewOpen.find().sort([("GI_RcTot", -1)]).limit(1)
        for i in cur:
            max_GI_RcTot=i['GI_RcTot']
        cur=self.db.PetitionNewOpen.find().sort([("GI_Ought", -1)]).limit(1)
        for i in cur:
            max_GI_Ought=i['GI_Ought']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_relig", -1)]).limit(1)
        for i in cur:
            max_LIWC_relig=i['LIWC_relig']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_pronoun", -1)]).limit(1)
        for i in cur:
            max_LIWC_pronoun=i['LIWC_pronoun']
        cur=self.db.PetitionNewOpen.find().sort([("LIWC_WC", -1)]).limit(1)
        for i in cur:
            max_LIWC_WC=i['LIWC_WC']
        cur=self.db.PetitionNewOpen.find().sort([("petitionLength", -1)]).limit(1)
        for i in cur:
            max_petitionLength=i['petitionLength']
        cur=self.db.PetitionNewOpen.find().sort([("avg_len_sentences_words", -1)]).limit(1)
        for i in cur:
            max_avg_len_sentences_words=i['avg_len_sentences_words']
        cur=self.db.PetitionNewOpen.find().sort([("Twitter_mentions", -1)]).limit(1)
        for i in cur:
            max_Twitter_mentions=i['Twitter_mentions']
        cur=self.db.PetitionNewOpen.find().sort([("updates_count_int", -1)]).limit(1)
        for i in cur:
            max_updates_count=i['updates_count']
        cur=self.db.PetitionNewOpen.find().sort([("reasons_count_int", -1)]).limit(1)
        for i in cur:
            max_reasons_count=i['reasons_count']
        cur=self.db.PetitionNewOpen.find().sort([("targets_count_int", -1)]).limit(1)
        for i in cur:
            max_targets_count=i['targets_count']

        articles = self.petitionDocs
        cur = articles.find({}, no_cursor_timeout=True)
        for p in cur:
            post={}
            overstatement_norm=(float(p["GI_Ovrst"])/float(max_GI_Ovrst)+float(p["LIWC_certain"])/float(max_LIWC_certain))/2
            understatement_norm = (float(p["GI_Undrst"]) / float(max_GI_Undrst) + float(p["LIWC_tentat"]) / float(
                max_LIWC_tentat)) / 2
            enlightenment_norm = (float(p["GI_EnlTot"]) / float(max_GI_EnlTot) + float(p["LIWC_insight"]) / float(
                max_LIWC_insight)) / 2
            positive_norm = (float(p["GI_Positiv"]) / float(max_GI_Positiv) + float(p["LIWC_posemo"]) / float(
                max_LIWC_posemo)) / 2
            negative_norm = (float(p["GI_Negativ"]) / float(max_GI_Negativ) + float(p["LIWC_negemo"]) / float(
                max_LIWC_negemo)) / 2
            moral_norm = (float(p["GI_RcTot"]) / float(max_GI_RcTot) + float(p["GI_Ought"]) / float(
                max_GI_Ought)+float(p["LIWC_relig"]) / float(max_LIWC_relig)) / 3
            pronoun_norm= float(p["LIWC_pronoun"]) / float(max_LIWC_pronoun)
            post["pronoun_norm"] = pronoun_norm
            post["overstatement_norm"]=overstatement_norm
            post["understatement_norm"]=understatement_norm
            post["enlightenment_norm"] = enlightenment_norm
            post["positive_norm"] = positive_norm
            post["negative_norm"] = negative_norm
            post["moral_norm"] = moral_norm
            post["Twitter_mentions_norm"]=float(p["Twitter_mentions"]) / float(max_Twitter_mentions)
            post["updates_count_norm"] = float(p["updates_count_int"]) / float(max_updates_count)
            post["reasons_count_norm"] = float(p["reasons_count_int"]) / float(max_reasons_count)
            post["targets_count_norm"] = float(p["targets_count_int"]) / float(max_targets_count)
            post["avg_len_sentences_words_norm"]=float(p["avg_len_sentences_words"]) / float(max_avg_len_sentences_words)
            post["petitionLength_norm"] = float(p["petitionLength"]) / float(max_petitionLength)
            post["LIWC_WC_norm"] = float(p["LIWC_WC"]) / float(max_LIWC_WC)
            self.petitionDocs.update({"petition_id": p['petition_id']},{"$set": post}, False)

    # Parse climate change petitions from search results starting from 1st page to last page and insert in database
    def parse(self, firstPage, lastPage, start_url, keyword):
        # open Mongodb local connection
        client = MongoClient('mongodb://localhost:27017/')
        collectionOpened = client.ClimateChange.PetitionNew
        collectionClosed = client.ClimateChange.PetitionNewClosed
        collectionVictory = client.ClimateChange.PetitionNewVictory

        count = 0   #counter for the total number of petitions read so far

        # loop through the search result pages in range
        for pageCount in range(firstPage, lastPage):
            # set the offset parameter in URL
            url=start_url+str((pageCount-1)*10)
            response = HtmlResponse(url)
            self.driver.get(response.url)

            # sleep 2 sec in order to finish loading the page HTML content and avoid being blocked form change.org
            # web server due to many requests in small time
            time.sleep(2)

            # loop through the petitions inside each page
            for itemCount in range(0, 9):
                try:
                    # sleep 0.1 sec to avoid being blocked form change.org
                    # web server due to many requests in small time
                    time.sleep(0.1)

                    ''' Get petition information

                    '''
                    # get the petition by xpath in the page layout
                    petition = self.driver.find_elements_by_xpath('// *[ @ id = "content"] / div / div / div / div / div / div[2] / ul / div[' + str(itemCount + 1) + '] / a')

                    # get the petition link
                    l = petition[0].get_attribute("href")
                    if l=="https://www.change.org/p/ivanovo-circus-in-russia-tell-ivanovo-circus-in-russia-to-stop-torturing-using-polar-bears-in-their-shows":
                        print l
                    # check if the link is for a petition or something else
                    if '/p/' in l:
                        count += 1

                        # get petition id by URL through an http get request after setting change.org api key parameter
                        link = 'https://api.change.org/v1/petitions/get_id?petition_url=' + l + '&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                        response = requests.get(link)

                        # load petition short details in json
                        results = json.loads(response.text)

                        # get petition id
                        petition_id = str(results["petition_id"])
                        if self.checkExistingPetition(petition_id):
                            continue

                        # get all petition details by id through an http get request after setting change.org api key parameter
                        link = 'https://api.change.org/v1/petitions/' + petition_id + '?page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                        response = requests.get(link)
                        petitionDetails = response.text

                        # load all petition details in json to results
                        results = json.loads(response.text)
                        response = HtmlResponse(l)
                        self.driver2.get(response.url)
                        braclet = 1   # boolean to check if the } or not at the end of the json for appending new columns
                        try:
                            # crawling through css selectors to get (current number of supporters, total number of supporters needed to
                            # reach goal, and the goal number of supporters) that is not retrieved by change.org api

                            # get remaining number of supporters needed to reach the petition goal and goal number of supporters by css selector
                            #supp = self.driver2.find_elements_by_css_selector('#content > div > div.container > div.row.mbxxl > div.js-petition-action-panel-container.col-xs-12.col-sm-4.xs-phn.xs-pbm.position-sticky.position-top > div > div > div > div > div.js-sign-and-share-components > div > div.type-s.type-weak > div.txt-r')
                            if results['status']=='victory' or results['status']=='closed':
                                supp = self.driver2.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div[4]/div[2]/div[2]/div/div/div/div/div/div[1]/p')
                                #text = self.driver2.find_element(webdriver.By.xpath("//div/span")).getText()
                                supp = self.driver2.find_element_by_css_selector('p.type-weak')
                                s=supp.text
                                lstSpc = s.rfind(' ')
                                suffix = s[lstSpc:len(s)]
                                suffix1 = re.sub(suffix, '', s)
                                lstSpc = suffix1.rfind(' ')
                                # s.replace(suffix, '')
                                supportersStr = suffix1[lstSpc:len(suffix1)]
                                supporters = int(re.sub(',', '', supportersStr))
                                goalNo = supporters
                                remNo = 0
                            else :
                                supp = self.driver2.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div[4]/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div[2]/div/div/p')
                                s = supp.text
                                lstSpc = s.rfind(' ')
                                goal = s[lstSpc:len(s) - 1]
                                goalex = re.sub(',', '', goal)  # get the goal number of supporters in numbers
                                goalNo = int(goalex)
                                supportersStr = s[0:s.find(' ')]
                                supporters = int(re.sub(',', '', supportersStr))
                                remNo = goalNo - supporters

                            # Append to json supporters numbers to all petition details into strIns which is the string
                            # that consolidates all petition, as well as the assiociated organizations, comments, updates and targets
                            # with this petition
                            self.strIns = petitionDetails[0:len(petitionDetails) - 1] + "," + '"supporters":' + '"' + str(supporters) + '",' + '"remaining_supporters":' + '"' + str(remNo) + '",' + '"needed_supporters":' + '"' + str(goalNo) + '",'
                            braclet = 0   # no }

                        # In case of failure to retrieve the supporters and goal numbers
                        except:
                            self.strIns = petitionDetails    #prepare strIns without supporters numbers

                        # For the sake of code tracing the sequence of reading is saved with the petition
                        if braclet == 1:  # Case there is a braclet remove the bracket and append the tracing sequence
                            self.strIns = self.strIns[0:len(self.strIns) - 1] + ',' + '"keyword":' + '"' + keyword+ '",'+'"devTrace":' + '"' + str((pageCount-1)*10+itemCount) + '",'
                            braclet = 0
                        else:   # Case there is no bracket append the tracing sequence directly
                            self.strIns = self.strIns + '"keyword":' + '"' + keyword+ '",'+'"devTrace":' + '"' + str((pageCount-1)*10+itemCount) + '",'

                        ''' Getting the associated Organizations with this petition if any

                        '''

                        organization_url = str(results["organization_url"])
                        if organization_url != "None":  # if there is organizations associated with this petition

                            try:
                                # get orgnaization with organization url from petition data
                                link = 'https://api.change.org/v1/organizations/get_id?organization_url=' + organization_url + '&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                                response = requests.get(link)   # get organization short description
                                data = json.loads(response.text)    # load organization short description as json
                                organization_id = str(data["organization_id"])  # get organization id

                                # Get organization details by organization id
                                link = 'https://api.change.org/v1/organizations/' + organization_id + '?page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                                response = requests.get(link)
                                org = response.text
                                self.strIns = self.strIns + org[1:len(org) - 1] + ',' # add organization details to conolidated petition data
                            except Exception as e:  # case any exception then print petition
                                print e

                        ''' Get petition associated updates with this petition if any

                        '''

                        # Retreive associated updates with petition by petition id
                        link = 'https://api.change.org/v1/petitions/' + petition_id + '/updates?&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                        response = requests.get(link)
                        data = json.loads(response.text)    # load updates as json
                        upd = simplejson.dumps(data['updates'], separators=(',', ':'))
                        if braclet == 1:    # if there is a braclet remove the braclet and append updates and number of updates
                            self.strIns = self.strIns[0:len(
                                self.strIns) - 1] + ',"updates":' + upd + ',' + '"updates_count":' + '"' + str(
                                len(data['updates'])) + '",'
                            braclet = 0
                        else:   # if there is no braclet directly append updates and number of updates
                            self.strIns = self.strIns + '"updates":' + upd + ',' + '"updates_count":' + '"' + str(
                                len(data['updates'])) + '",'

                        ''' Get associated users comments (reasons) with this petition if any

                        '''
                        # Retreive associated comments (reasons) with petition by petition id
                        link = 'https://api.change.org/v1/petitions/' + petition_id + '/reasons?&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                        response = requests.get(link)
                        data = json.loads(response.text) # load comments  as json
                        rsn = simplejson.dumps(data['reasons'], separators=(',', ':'))

                        # Append comments and number of comments
                        self.strIns = self.strIns + '"reasons":' + rsn + ',' + '"reasons_count":' + '"' + str(
                            len(data['reasons'])) +'",'

                        ''' Get associated target authoroties, agencies or coporates that the petition addresses

                        '''

                        # Retreive associated targets with petition by petition id
                        link = 'https://api.change.org/v1/petitions/' + petition_id + '/targets?&page_size=1000&sort=time_desc&api_key=f7720f80ec4f67eeca1f6932d93069b92b627cc6ac6e5c95a18c89dc8a81792f'
                        response = requests.get(link)
                        data = json.loads(response.text)    # load targets as json
                        trg = simplejson.dumps(data, separators=(',', ':'))
                        # Add collection timestamp
                        ts = time.time()
                        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        # Append targets and number of targets
                        self.strIns = self.strIns + '"targets":' + trg + ',' + '"targets_count":' + '"' + str(
                            len(data)) +  '",' + '"CollectedTimeStamp":'+'"'+st+'"}'


                        # Parse the consolidated petitions and associated targets, comments, updates and organizations as json
                        DicIns = simplejson.loads('[%s]' % self.strIns)

                        # Insert open status petitions in database
                        if results["status"] == 'open':
                            collectionOpened.insert(DicIns)
                        elif results["status"] == 'closed':
                            collectionClosed.insert(DicIns)
                        else:
                            collectionVictory.insert(DicIns)
                except Exception as e:  # case any exception then print petition
                    #print l
                    print(e)
        self.driver.close()



def main():
    # Ontology Wei Liu, 2005
    #start_urls = "https://www.change.org/search?q=" + "climate%20change"+"&offset="
    #start_urls = "https://www.change.org/search?q=" + "global%20warming" + "&offset="
    #start_urls = "https://www.change.org/search?q=" + "greenhouse" + "&offset="
    c = ChangeSpider()  # instantiate ChangeSpider crawler
    '''
    start_url = "https://www.change.org/search?q=" + "climate%20change" + "&offset="
    c.parse(140,165,start_url,"climate change")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "methane" + "&offset="
    c.parse(1, 17, start_url,"methane")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "global%20cooling" + "&offset="
    c.parse(1, 2, start_url,"global cooling")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "nuclear%20winter" + "&offset="
    c.parse(1, 2, start_url,"nuclear winter")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "carbon%20dioxide" + "&offset="
    c.parse(1, 27, start_url,"carbon dioxide")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "c02" + "&offset="
    c.parse(1, 23, start_url,"c02")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "co2" + "&offset="
    c.parse(1, 23, start_url, "co2")  # parse pages from upper to lower bound

    start_url = "https://www.change.org/search?q=" + "emissions" + "&offset="
    c.parse(1, 87, start_url,"emissions")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "pollution" + "&offset="
    c.parse(1, 291, start_url,"pollution")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "arctic" + "&offset="
    c.parse(1, 14, start_url,"arctic")  # parse pages from upper to lower bound

    # Ontology Nophea Sasaki, 2009
    start_url = "https://www.change.org/search?q=" + "forest%20degradation" + "&offset="
    c.parse(1, 4, start_url,"forest degradation")  # parse pages from upper to lower bound

    # ontology Esbjorn 2010
    start_url = "https://www.change.org/search?q=" + "fenvironmental%20vulnerability" + "&offset="
    c.parse(1, 4, start_url,"environmental vulnerability")  # parse pages from upper to lower bound
    start_url = "https://www.change.org/search?q=" + "deforestation" + "&offset="
    c.parse(1, 4, start_url,"deforestation")  # parse pages from upper to lower bound

    # victory 358, open 2,929, closed 1,457 = 4,744
    # open 2,929 - 373<100 words = 2556
    '''
    #c.get_expression()
    c.normalizedfeatures()
if __name__ == '__main__':
    main()