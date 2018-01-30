from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import datetime

class Command(BaseCommand):
    help = 'Populates pmorleader field, minister field, juniorminister field, and whip field. Options: verbose(bool) to print working date, date(yyyy-mm-dd) for starting date'

    def add_arguments(self, parser):
        parser.add_argument( 
            '--verbose',
            type=bool,
            action='store',
            dest='verbose',
            default=True,
        )

        parser.add_argument(
            '--date',
            type=str,
            action='store',
            dest='date',
            default='1926-01-01',
        )

    
    def handle(self, *args, **options):

        datelist = datenav.objects.filter(hansarddate__gte=options['date']).order_by('hansarddate').values_list('hansarddate', flat=True)

        lead = "Prime Minister"
        opplead = "Leader of the Official Opposition"
        junior_minister_list = ["Secretary to the", "Secretary for", "Assistant to the", "Parliamentary Secretary"]
        minister_list = ["Minister", "Solicitor General", "Secretary of State", "Postmaster General", "Superintendent-General"]
        wh = "Whip"
        hl = "House Leader"
        h2 = "Leader of the Government"

        for date in datelist:
            if options['verbose']:
                print(str(date))

            qs = basehansard.objects.filter(speechdate=date).exclude(pid__isnull=True).order_by('basepk')
            
            for speech in qs:
            
                poslist = position.objects.filter(pid__pid=speech.pid).filter(startdate__lte=date).filter(enddate__gte=date).values_list('positionname', flat=True)
                
                if len(poslist)==0: # just in case, error correction for any early runs here
                    speech.pmorleader = False
                    speech.minister = False
                else:
                    for aposition in poslist:
                        for jm in junior_minister_list:
                            if jm in aposition:
                                speech.juniorminister = True
                        if lead in aposition:
                            if "Deputy" in aposition:
                                speech.pmorleader = False
                            elif "Secretary" in aposition:
                                speech.pmorleader = False
                                speech.minister = False
                                speech.juniorminister = True
                            else:
                                speech.pmorleader = True
                                speech.minister = True
                        elif opplead in aposition:
                            if "Deputy" in aposition:
                                speech.pmorleader = False
                            else:
                                speech.pmorleader = True
                        elif wh in aposition:
                            speech.whip = True
                        elif hl in aposition:
                            speech.houseleader=True
                        elif h2 in aposition:
                            speech.houseleader=True
                        else:
                            for m in minister_list:
                                if aposition.startswith(m): # we assume that "true" ministers will have a title that begins with eg. "Minister"
                                    speech.minister = True

                speech.save()
            ### juniorminister corrections -- but some people ARE both secretaries and ministers, so...
            ### deputy prime minister corrections should be taken care of by the above
            



        

        

   
