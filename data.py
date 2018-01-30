import string
import datetime
import math
import time
import pickle
import statistics

import sqlalchemy as sqa
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import matplotlib.dates as mpldates
import gensim

###########

#### Select all Question Period speeches within study date range
#### Change this to go along with QP polling dates: speechdate <= '2010-03-31' & speechdate >= '1975-04-07'
#### or QP analysis dates (for Nona): speechdate <= '2015-12-31' & speechdate >= '1975-04-07'


engine = sqa.create_engine('postgresql://xxx.xxx.xxx.xxx')
sql = sqa.text(' '.join((
    "SELECT *",
    "FROM dilipadsite_basehansard",
    "WHERE (pid != '' and pid != 'unmatched' and pid !='intervention')",
    "AND (speakerposition != 'subtopic' and speakerposition != 'topic' and speakerposition !='stagedirection')"
    "AND (maintopic like '%ORAL QUESTION PERIOD%' or maintopic like '%Oral Questions%' or maintopic like '%Oral Question Period%')",
    "AND (speakername not like '%Member%')",
    "AND (speechdate > '1975-04-07' and speechdate < '2010-03-31')",
    #"AND (speechdate > '1975-04-07' and speechdate < '1977-03-31')", # TESTING
    #"AND (speechdate > '1927-01-01' and speechdate < '2015-12-31')", # All dates
    "AND (speechtext <> '') ORDER BY basepk ;",
)))

data = pd.read_sql_query(sql, engine)
engine.dispose()

print("Finished query.")

#### Dump query if desired

##with open("query_qp.pkl", "wb") as f:
##    pickle.dump(data, f)

#### Read query if desired

##with open("query_qp.pkl", "rb") as f:
##    data = pickle.load(f)

#### For each unique date, concatenate opposition and government speeches,
#### tokenize etc., and store in a new df called 'qpcompare'

unique_dates = sorted(data.speechdate.unique())
#qpcompare = pd.DataFrame(columns=['speechdate', 'simil'])

##big_compare = pd.DataFrame(columns=['id','speechdate','text'])
##gensim_data = pd.DataFrame(columns=['id','gov','offopp','speechdate','text'])
vectorizer = TfidfVectorizer(strip_accents='unicode', stop_words ='english')

#### Filter out garbage days

unique_dates = [x for x in unique_dates if len(data.loc[(data['speechdate'] == x)]) > 25]

rows_list_big = []
rows_list_gensim = []

for date in unique_dates:

    print(date)

    gov_speeches = (data.loc[(data['speechdate'] == date) & (data['government'] == True)]['speechtext']).tolist()
    opp_speeches = (data.loc[(data['speechdate'] == date) & (data['government'] == False)]['speechtext']).tolist()
    
    #### Append speeches to gensim training data

    for index, speech in enumerate(gov_speeches):
        rows_list_gensim.append({'id':(date.strftime("%d-%m-%Y") + "-G-" + str(index)),'text':speech,'speechdate':date,'gov':True,'opp':False})
        
    for index, speech in enumerate(opp_speeches):
        rows_list_gensim.append({'id':(date.strftime("%d-%m-%Y") + "-O-" + str(index)),'text':speech,'speechdate':date,'gov':False,'opp':True})

    #### Create opposition/government concatenation

    rows_list_big.append({'id':(date.strftime("%d-%m-%Y") + "-G"),'text':" ".join(gov_speeches), 'speechdate':date})
    rows_list_big.append({'id':(date.strftime("%d-%m-%Y") + "-O"),'text':" ".join(opp_speeches), 'speechdate':date})

#### Create DF using list method (faster than appending)

big_compare = pd.DataFrame(rows_list_big)
gensim_data = pd.DataFrame(rows_list_gensim)      

#### Construct term-document matrix

transform = vectorizer.fit_transform(big_compare['text'])
big_compare['vec'] = list(transform)

#### Dump temporary tables if desired

with open("qp_govopp_bigcompare.pkl", "wb") as f:
    pickle.dump(big_compare, f)

with open("qp_govopp_gensimdata.pkl", "wb") as f:
    pickle.dump(gensim_data, f)

#### doc2vec Method 1 (train on concatenation)

##print("Starting doc2vec Method 1...")
##
##documents = [gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(row['text']), tags=[row['id']])
##             for index, row in big_compare.iterrows()]
##
##d2vmodel1 = gensim.models.Doc2Vec(documents, size=200, window=8, min_count=5, workers=3, iter=20)
##
##print("Finished doc2vec.")

#### doc2vec Method 2 (train on separate documents)

print("Starting doc2vec Method 2...")

documents = [gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(row['text']), tags=[row['id']])
             for index, row in gensim_data.iterrows()]

d2vmodel2 = gensim.models.Doc2Vec(documents, size=200, window=8, min_count=5, workers=7, iter=50)

print("Finished doc2vec.")

#### Dump model if desired

with open("qp_govopp_d2vmodel.pkl", "wb") as f:
    pickle.dump(d2vmodel2, f)

#### Calculate similarities for each pair/type of pair

#### Testing: time average processing time per day
##start_time = time.time()

qp_list = []

for date in unique_dates:
    indices = big_compare.loc[big_compare['speechdate']==date].index
    cs = cosine_similarity(big_compare.iloc[indices[0]]['vec'],
                           big_compare.iloc[indices[1]]['vec']).item(0)

    #### for doc2vec Model 2, infer vector of both concatenated texts for this day, then compare similarity of those vectors

    d2v_govvec = d2vmodel2.infer_vector(gensim.utils.simple_preprocess(big_compare.iloc[indices[0]]['text']), alpha=0.025, steps=100)
    d2v_oppvec = d2vmodel2.infer_vector(gensim.utils.simple_preprocess(big_compare.iloc[indices[1]]['text']), alpha=0.025, steps=100)
    
    cs_d2v = cosine_similarity(d2v_govvec.reshape(1, -1), d2v_oppvec.reshape(1, -1))

    #### Or, calculate average similarity across all gov/opp pairs (Model 3)

    simil_list = []

    #### Get list of all government and opposition IDs

    gov_id_list = (gensim_data.loc[(gensim_data['speechdate'] == date) & (gensim_data['gov'] == True)]['id']).tolist()
    opp_id_list = (gensim_data.loc[(gensim_data['speechdate'] == date) & (gensim_data['opp'] == True)]['id']).tolist()

    for gid in gov_id_list:
        for oid in opp_id_list:
            simil_list.append(float(abs(cosine_similarity(d2vmodel2.docvecs[oid].reshape(1, -1),d2vmodel2.docvecs[gid].reshape(1, -1)).flatten()[0])))
    
    if cs==0:
        #### This is a garbage day so we can safely drop it
        pass
    else:
        try:
            qp_list.append({'speechdate':date,
                                          'simil':cs,
                                          'simil_d2v_m2':cs_d2v.flatten()[0],
                                          'simil_d2v_m3':statistics.mean(simil_list),
                                          'poll_govt':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['pollpct'],
                                          'prev_poll_govt':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['prevpollpct'],
                                          'poll_offopp':data.loc[(data['speechdate'] == date) & (data['offopp'] == True)].iloc[0]['pollpct'],
                                          'prev_poll_offopp':data.loc[(data['speechdate'] == date) & (data['offopp'] == True)].iloc[0]['prevpollpct'],
                                          'gov_party':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['speakerparty'],
                                          'offopp_party':data.loc[(data['speechdate'] == date) & (data['offopp'] == True)].iloc[0]['speakerparty'],
                                          'majority':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['majority'],
                                          'govtseatpct':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['seatpct'],
                                          'offoppseatpct':data.loc[(data['speechdate'] == date) & (data['offopp'] == True)].iloc[0]['seatpct'],
                                          'parlnum':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['parlnum'],
                                          'sessnum':data.loc[(data['speechdate'] == date) & (data['government'] == True)].iloc[0]['sessnum']
                                         })
        except IndexError:
            print(date) # IndexError for any remaining garbage days


##print("Average time per day:")
##print((time.time() - start_time)/len(unique_dates))

qpcompare = pd.DataFrame(qp_list)

#### export qpcompare data for further study

qpcompare.to_csv('qp_govopp.csv')

#### Dump a pickle too, if desired

with open("qp_govopp.pkl", "wb") as f:
    pickle.dump(qpcompare, f)

#### Simple plots for diagnostic purposes

##plt.scatter([mpldates.date2num(d) for d in qpcompare.speechdate], qpcompare.simil)
##
####plt.show()
##
    
#### Quarterly bins

qpcompare.index = pd.DatetimeIndex(qpcompare.speechdate)

##qpcompare_quarter_mean = qpcompare.groupby(pd.Grouper(freq='Q'))
##qpcompare_quarter_std = qpcompare.groupby(pd.Grouper(freq='Q')).std()
## x_labels = [x.strftime('%b %Y') for x in qpcompare_quarter_mean.groups.keys()]
##
##x = qpcompare_quarter_mean.boxplot(subplots=False, fontsize='8',rot=90, showfliers=False)
##plt.draw()
##x.set_xticklabels(x_labels)

y = pd.DataFrame(qpcompare['simil_d2v_m3'])
##y = pd.DataFrame(qpcompare['simil'])
x_labels = [x.strftime('%b %Y') for x in (y.groupby(pd.Grouper(freq='Q'))).groups.keys()]
x = y.boxplot(by=pd.Grouper(freq='Q'), fontsize='8',rot=90, showfliers=False)
plt.draw()
x.set_xticklabels(x_labels)
plt.show()
