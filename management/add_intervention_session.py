from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from dilipadsite.models import *

class Command(BaseCommand):
    help = "Writes missing parlsess data to the basehansard table for interventions and speeches by the Speaker"

    def handle(self, *args, **options):
        qs = basehansard.objects.filter(parlnum__isnull=True).filter(pid__isnull=False).filter(speechdate__lte='2015-11-01').filter(speechdate__gte='1925-01-01')
        #qs = basehansard.objects.filter(pid__exact='intervention') | basehansard.objects.filter(speakeroldname__icontains='speaker') | basehansard.objects.filter(speakerposition__icontains='speaker')
        for speech in qs.iterator():
            try:
                ps = parlsess.objects.get(startdate__lte=speech.speechdate, enddate__gte=speech.speechdate)
                speech.parlnum = ps.parlnum
                speech.sessnum = ps.sessnum
                speech.save()

            except:
                print(speech.speechdate) # catches OCR garbage dates; these records can be manually removed if we want
