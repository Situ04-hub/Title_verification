# import pandas as pd
# from django.core.management.base import BaseCommand
# from validator.models import NewspaperTitle

# class Command(BaseCommand):
#     help = 'Import titles from an HTML-formatted XLS file'


#     def handle(self, *args, **options):
#         file_path = 'data/TestExcel.xls'
#         self.stdout.write(f"Reading from {file_path}...")

#         try:
#             # 1. Read the HTML table
#             tables = pd.read_html(file_path)
#             df = tables[0]

#             # 2. Target the 2nd column (Index 1)
#             # This is where your newspaper titles are located
#             raw_titles = df.iloc[:, 1].astype(str).tolist()

#             # 3. Prepare the objects for the database
#             objs = []
#             for t in raw_titles:
#                 clean_title = t.strip()
#                 # Skip empty cells or cells containing 'nan'
#                 if clean_title and clean_title.lower() != 'nan':
#                     objs.append(NewspaperTitle(
#                         title_text=clean_title[:255], 
#                         status='EXISTING'
#                     ))

#             # 4. Save to Database
#             self.stdout.write(f"Importing {len(objs)} titles from the 2nd column...")
#             NewspaperTitle.objects.bulk_create(objs, ignore_conflicts=True)
            
#             self.stdout.write(self.style.SUCCESS("Success! Database updated with 2nd column data."))

#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"Error during import: {e}"))
import os
import pandas as pd
from django.core.management.base import BaseCommand
from validator.models import NewspaperTitle

class Command(BaseCommand):
    help = 'Imports all .xls files from the data directory'

    def handle(self, *args, **options):
        # 1. Define the folder path
        data_folder = 'data'
        
        # 2. Get a list of all files in that folder ending with .xls
        files = [f for f in os.listdir(data_folder) if f.endswith('.xls')]
        
        if not files:
            self.stdout.write(self.style.WARNING("No .xls files found in the 'data' folder."))
            return

        for file_name in files:
            file_path = os.path.join(data_folder, file_name)
            self.stdout.write(f"Processing: {file_name}...")

            try:
                # 3. Read the HTML-formatted XLS
                tables = pd.read_html(file_path)
                df = tables[0]

                # 4. Target the 2nd column (Index 1) for titles
                raw_titles = df.iloc[:, 1].astype(str).tolist()

                # 5. Build list of objects
                objs = []
                for t in raw_titles:
                    clean_title = t.strip()
                    if clean_title and clean_title.lower() != 'nan':
                        objs.append(NewspaperTitle(
                            title_text=clean_title[:255], 
                            status='EXISTING'
                        ))

                # 6. Save to DB (ignore_conflicts=True handles duplicates across files)
                NewspaperTitle.objects.bulk_create(objs, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(f"Finished {file_name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in {file_name}: {e}"))

        self.stdout.write(self.style.SUCCESS("\nAll files processed successfully!"))