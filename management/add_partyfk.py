from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from dilipadsite.models import *
import datetime

class Command(BaseCommand):
    help = "Populates party_fk for basehansard table"

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            action='store',
            dest='date',
            default='1922-01-14',
        )

        # Verbose mode prints dates
        
        parser.add_argument( 
            '--verbose',
            type=bool,
            action='store',
            dest='verbose',
            default=False,
        )

    def handle(self, *args, **options):

        datelist = datenav.objects.filter(hansarddate__gte=options['date']).order_by('hansarddate').values_list('hansarddate', flat=True)

        for date in datelist:
            if options['verbose']:
                print(str(date))
            
            qs = basehansard.objects.filter(speechdate=date).exclude(pid__isnull=True).exclude(pid__exact='').exclude(pid__exact='unmatched').exclude(pid__exact='intervention').order_by('basepk')
            for speech in qs:
                try:
                    mem = member.objects.get(pid=speech.pid)
                except ObjectDoesNotExist:
                    # this person doesn't have a memberfile; probably byelection followed by a loss
                    continue
                    
                try:
                    const = constituency.objects.get(pid=speech.pid, startdate__lte=date, enddate__gte=date)
                except constituency.MultipleObjectsReturned:
                    # Handles electoral weirdness cases like R.B. Bennett in 1931
                    # In these cases, use the record with the broadest date range
                    const = constituency.objects.filter(pid=speech.pid, startdate__lte=date, enddate__gte=date).order_by('startdate').first()
                except ObjectDoesNotExist:
                    # this person is a senator, an unelected minister, or speaker of the senate
                    # we shall flage these people with the prob_senator field
                    
                    speech.prob_senator = True
                    speech.save()
                    continue
                
                try:
                    ps = parlsess.objects.get(startdate__lte=date, enddate__gte=date)
                except ObjectDoesNotExist:
                    # This is a garbage date (OCR error), so we can omit
                    continue

                speech.party_fk = const.partyid
                speech.save()

