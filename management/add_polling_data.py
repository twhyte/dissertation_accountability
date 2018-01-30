from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from dilipadsite.models import *
import unicodecsv as csv
import datetime
import os
from dilipadsite.settings import MEDIA_ROOT
from django.db.models import Avg

class Command(BaseCommand):
    help = "Collapses polls.csv source to quarterly and populates polls table (on --load=True) and assigns to speeches during that time span. Relies upon party_fk in basehansard"

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            action='store',
            dest='date',
            default='1948-01-01',
        )

        # Verbose mode prints dates
        
        parser.add_argument( 
            '--verbose',
            type=bool,
            action='store',
            dest='verbose',
            default=False,
        )

        # load loads in polling data from polls.csv and populates the polls table
        
        parser.add_argument( 
            '--load',
            type=bool,
            action='store',
            dest='load',
            default=False,
        )

    def handle(self, *args, **options):

        if options['load']==True:

            # polls.objects.all().delete() # clear past runs for safety
            
            party_dict = {'Liberal': party.objects.get(pk=20), 'PC': party.objects.get(pk=4), 'NDP': party.objects.get(pk=2),
                          "ReformCA":party.objects.get(pk=7), "Bloc Quebecois":party.objects.get(pk=12), "Creditiste":party.objects.get(pk=5),
                          "Social Credit":party.objects.get(pk=8), "Bloc Populaire":party.objects.get(pk=23),
                          "Labour Progressive":party.objects.get(pk=41), "Green Party":party.objects.get(pk=18), "Other":party.objects.get(pk=54)}
                            
            filepath = os.path.join(MEDIA_ROOT,'polls','polls.csv')
            with open(filepath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    quart = 0
                    try:
                        month_int = datetime.datetime.strptime(row["Month"], '%B').month
                        if month_int <= 3:
                            quart = 1
                        elif month_int <= 6:
                            quart = 2
                        elif month_int <= 9:
                            quart = 3
                        else:
                            quart = 4
                    except:
                        # this is already in quarter format
                        month_int = 0
                        if row["Month"]=="Q1":
                            quart = 1
                        elif row["Month"]=="Q2":
                            quart = 2
                        elif row["Month"]=="Q3":
                            quart = 3
                        elif row["Month"]=="Q4":
                            quart = 4
                            
                    for current_party in list(party_dict.keys()):
                        pct = row[current_party]
                        try:
                            pct = float(pct)
                        except ValueError:
                            continue
                        
                        b, created = polls.objects.get_or_create(year=int(row["Year"]),
                                            month = month_int,
                                            quarter = quart,
                                            party_fk = party_dict[current_party],
                                            pollpct = pct)

                        if current_party == "ReformCA":
                            # What we'll do for simplicity is create a dupe for any Reform record so we can also find it via the CA
                            
                            b, created = polls.objects.get_or_create(year=int(row["Year"]),
                                                month = month_int,
                                                quarter = quart,
                                                party_fk = party.objects.get(pk=13),
                                                pollpct = pct)
                            
                        if current_party == "NDP":
                            # likewise for the CCF

                            b, created = polls.objects.get_or_create(year=int(row["Year"]),
                                                month = month_int,
                                                quarter = quart,
                                                party_fk = party.objects.get(pk=14),
                                                pollpct = pct)

                        if current_party == "PC":
                            # and for the CPC

                            b, created = polls.objects.get_or_create(year=int(row["Year"]),
                                                month = month_int,
                                                quarter = quart,
                                                party_fk = party.objects.get(pk=15),
                                                pollpct = pct)


            # after all poll objects have been created, calculate the quarterly averages

            party_dict["Canadian Alliance"]=party.objects.get(pk=13)
            party_dict["CCF"]=party.objects.get(pk=14)
            party_dict["CPC"]=party.objects.get(pk=15)
            
            for current_year in list(range(1953,2011)):
                for current_quarter in list(range(1,5)):
                    for current_party in list(party_dict.keys()):
                        qs = polls.objects.filter(year=current_year).filter(quarter=current_quarter).filter(party_fk=party_dict[current_party])
                        agg=qs.aggregate(Avg('pollpct'))['pollpct__avg']
                        for poll in qs:
                            poll.q_avg_pollpct = agg
                            poll.save()                                                            


        datelist = datenav.objects.filter(hansarddate__gte=options['date']).order_by('hansarddate').values_list('hansarddate', flat=True)
        

        for date in datelist:
            if options['verbose']:
                print(str(date))

            # convert date to year and quarter

            current_year = date.year
            current_quarter = 0
            month_int = date.month
            if month_int <= 3:
                current_quarter = 1
            elif month_int <= 6:
                current_quarter = 2
            elif month_int <= 9:
                current_quarter = 3
            else:
                current_quarter = 4
            
            qs = basehansard.objects.filter(speechdate=date).exclude(pid__isnull=True).exclude(pid__exact='').exclude(pid__exact='unmatched').exclude(pid__exact='intervention').exclude(party_fk=party.objects.get(pk=31)).order_by('basepk')
            for speech in qs:
                poll_qs = polls.objects.filter(party_fk=speech.party_fk).filter(year=current_year).filter(quarter=current_quarter)
                if len(poll_qs)==0:
                    pass
                else:
                    speech.pollpct = poll_qs.first().q_avg_pollpct
                    speech.save()
                    

                
