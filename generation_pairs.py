####
# Generates QP argumentation pairs for reputation defence analysis
####

import sqlalchemy as sqa
import pandas as pd

first_only = True

engine = sqa.create_engine('postgresql://xxx.xxx.xxx.xxx')
sql = sqa.text(' '.join((
    "SELECT *",
    "FROM dilipadsite_basehansard",
    "WHERE (pid != '' and pid != 'unmatched' and pid !='intervention')",
    "AND (speakerposition != 'subtopic' and speakerposition != 'topic' and speakerposition !='stagedirection')"
    "AND (maintopic like '%ORAL QUESTION PERIOD%' or maintopic like '%Oral Questions%' or maintopic like '%Oral Question Period%')",
    "AND (speakername not like '%Member%')",
    "AND (speechdate > '1975-04-07' and speechdate < '2010-03-31')", # Polling available date range
       "AND (speechtext <> '') ORDER BY basepk ;",
)))

data = pd.read_sql_query(sql, engine)
engine.dispose()

print("Finished query.")

unique_dates = sorted(data.speechdate.unique())
df = pd.DataFrame(columns=['subtopic','speechdate','opp_text','gov_text'])

unique_dates = [x for x in unique_dates if len(data.loc[(data['speechdate'] == x)]) > 25]

for date in unique_dates:

    print(date)
    date_data = data.loc[(data['speechdate'] == date)]

    if first_only == True:
        # Find unique subtopics on this day
        try:
            for st in date_data.subtopic.unique().tolist():
                gov_speech = ''
                opp_speech = ''
                st_data = date_data.loc[(date_data['subtopic'] == st)].sort_values('basepk')
                if st_data['government'].iloc[0]==False:
                    opp_speech = st_data['speechtext'].iloc[0]
                    if st_data['government'].iloc[1]==True:
                        # Make sure it's not the Speaker who's talking:
                        if "Speaker" not in st_data['speakerposition'].iloc[1] and "Order" not in st_data['speechtext'].iloc[1]:
                            gov_speech = st_data['speechtext'].iloc[1]
                if opp_speech != '' and gov_speech != '':
                    df = df.append({'subtopic':st, 'speechdate':date,'opp_text':opp_speech,'gov_text':gov_speech}, ignore_index=True)
        except IndexError:
            pass

df.to_csv('QA_speeches.csv')
        
                    
                    
                    
                

            
            
            
        
        
        
