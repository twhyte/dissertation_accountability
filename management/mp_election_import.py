from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import os
import unicodecsv as csv
import unicodedata
import io
import time

class Command(BaseCommand):
    help = 'Imports MP election data from .csv file from Chris Cochrane'
    ### So far this works at about 80% match rate. A lot of this is inconsistency in francophone names; next step is ascii-ization for more general attempts

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.createcount = 0
    
    def handle(self, *args, **options):
        #self.decodeNames() # populates new ascii name fields, firstname_ascii and lastname_ascii, in member table
        
        path = os.path.join(os.getcwd(), "canada", "mpelect.csv")

        # Write out diagnostic files for failures, used to help improve matching accuracy
        
        pidfailpath = os.path.join(os.getcwd(), "canada", "pidfail.csv")
        confailpath = os.path.join(os.getcwd(), "canada", "confail.csv")
        datefailpath = os.path.join(os.getcwd(), "canada", "datefail.csv")

        with open (path, 'rb') as f:
            pidfail=open(pidfailpath, 'wb')
            confail=open(confailpath, 'wb')
            datefail=open(datefailpath, 'wb')
            r = csv.DictReader(f, encoding='utf-8')
            pidw = csv.DictWriter(pidfail, encoding='utf-8', fieldnames=r.fieldnames)
            conw = csv.DictWriter(confail, encoding='utf-8', fieldnames=r.fieldnames)
            datew = csv.DictWriter(datefail, encoding='utf-8', fieldnames=r.fieldnames)
            pidw.writeheader()
            conw.writeheader()
            datew.writeheader()
            for row in r:
                self.processElect(row, pidw, conw, datew)
            pidfail.close()
            confail.close()

        # self.calculateMargins()

        print("Finished processing. " + str(self.createcount) +"objects created.")

    def processElect(self, row, pidw, conw, datew):
        '''Main processing routine for each row of file'''
        
        try:
            edate = datetime.datetime.strptime(row['edate'], "%Y-%m-%d")
        except ValueError:
            print("Date error; check source file at id: "+row['ID'])
            datew.writerow(row)
            return()
        
        eyear = int(row['Year'])
        if eyear <= 1900:
            return()
        
        pid = self.linkMP(row)

        if pid is None:
            pidw.writerow(row)
            return()

        else:
            electedint = int(row['Elected'])
            elect=False
            if electedint == 0:
                elect = False
            elif electedint == 1:
                elect = True
            else:
                print("Bool error; check source file at id: "+row['ID']) # This is probably a source file typo, easiest to manually correct there
                return()

            con = constituency.objects.filter(pid_fk=pid,startdate=edate)
            if len(con)==0:
                con = constituency.objects.filter(pid_fk=pid,startdate__year=eyear)
                if len(con)==0:
                    conw.writerow(row)
                    return()
                
            if len(con)>1:
                print("Multiple constituencies error; check source file at id: "+row['ID']) # May require manual name disambiguation due to riding name shifts, or a manual date typo
                conw.writerow(row)
                return()

            # Now we have one constituency in the qs, so we're good here.

            con_good = con[0]
            
            b, created = election_mp.objects.update_or_create(partyid = con_good.partyid,
                                           electiondate = edate,
                                           pid = pid,
                                           result = row['Result'],
                                           elected=elect,
                                            cid = con_good,
                                            riding = row['Riding'],
                                            province = row['Province'],
                                            electiontype = row["Election_Type"])

            if created==True:
                self.createcount +=1

    def linkMP(self, row):
        '''Links an MP from file to their member file'''
        edate = row["edate"]
        last = row["Surname"]
        first = row["Name"]
        mparty = row["Party"]
        dob = row["DofB"]
        mriding = row["Riding"]

        qs = member.objects.filter(lastname__iexact=last) | member.objects.filter(lastname_ascii__iexact=last)

        if len(qs)==0:
            try:
                testcon = constituency.objects.get(startdate=edate, riding__iexact=mriding)
                return(testcon.member)
                
            except:
                return(None)

        elif len(qs) > 1:
            
            # we need to disambiguate this MP; try firstname and variants, then use constituency data
            fn_qs = qs.filter(firstname__iexact=first) | qs.filter(firstname_ascii__iexact=first)
            if len(fn_qs)==0:
                fn_split_qs = qs.filter(firstname__iexact=first.split()[0]) | qs.filter(firstname_ascii__iexact=first.split()[0])
                if len(fn_split_qs)==0:
                    try:
                        testcon = constituency.objects.get(startdate=edate, riding__iexact=mriding)
                        return(testcon.member)
                    except:
                        return(None)
                elif len(fn_split_qs) > 1:
                    conqs = constituency.objects.filter(startdate=edate)
                    match = []
                    for obj in fn_split_qs:
                        try:
                            match.append(conqs.get(pid=obj.pid))
                        except:
                            pass
                    if len(match)==0:
                        return(None)
                    elif len(match)==1:
                        return(match[0].pid_fk)
                            
                    else:
                        return(None)

                else:
                    return(fn_split_qs[0])


            elif len(fn_qs) > 1:
                conqs = constituency.objects.filter(startdate=edate)
                match = []
                for obj in fn_qs:
                    try:
                        match.append(conqs.get(pid=obj.pid))
                    except:
                        pass
                if len(match)==0:
                    return(None)
                elif len(match)==1:
                    return(match[0].pid_fk)
                            
                else:
                    return(None)

            else:
                return(fn_qs[0])

        else:
            return(qs[0])
    
    def calculateMargins(self):
        pass

    def decodeNames(self):
        def remove_accents(input_str):
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
        
        qs = member.objects.all()
        for mp in qs:
            mp.firstname_ascii = remove_accents(mp.firstname)
            mp.firstname_ascii_cut = mp.firstname_ascii.split()[0]
            mp.lastname_ascii = remove_accents(mp.lastname)
            mp.save()
                  

            
                  

        

        

   
