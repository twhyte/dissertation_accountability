from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import os
import unicodecsv as csv
from dilipadsite.settings import MEDIA_ROOT

class Command(BaseCommand):
    help = 'Dumps a .csv of each day in a year/month dir structure, to media/'

    def dump(self, qs, outfile_path):
        model = qs.model
	writer = csv.writer(open(outfile_path, 'w'))
	
	headers = []
	for field in model._meta.fields:
            headers.append(field.name)
	writer.writerow(headers)
	for obj in qs:
            row = []
            for field in headers:
                if field in headers:
                    val = getattr(obj, field)
                    val2 = 0
                    if type(val) == bool:
                        if val == True:
                            val2 = 1
                        val = val2
                    row.append(val)
            writer.writerow(row)

    def handle(self, *args, **options):

        datelist = datenav.objects.filter(hansarddate__gte="1926-11-02").values_list('hansarddate', flat=True)
        basefilepath = os.path.join(MEDIA_ROOT,'lipad')
##        remainder = [] # this is a doublecheck for broken days
        for date in datelist:
            m = str(date.month)
            d = str(date.day)
            y = str(date.year)
            outpath = os.path.join(basefilepath, y, m)
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            filename = y+"-"+m+"-"+d+".csv"
            filepath = os.path.join(outpath,filename)
            print(filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
                print ('skipping...')
            else:
                # implement filters here
                qs = basehansard.objects.filter(speechdate=date).exclude(speakerposition='topic').exclude(speakerposition='subtopic').exclude(speakerposition='stagedirection').order_by('basepk')
                self.dump(qs, filepath)
##                remainder.append(date)
##        for r in remainder:
##            print r.isoformat()

                



                
                
