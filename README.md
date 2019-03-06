#  Medidata Django App

#  Install Database

**Step 1:** Install PostgreSQL

**Step 2:** Create user and database on PostgreSQL

#  How to Setup Django App

**Step 1:** git clone this repo

**Step 2:** cd to the cloned repo

**Step 3:** install python library with `pip install -r config/requirements.txt`

**Step 4:** migrate database with `python mange_local.py migrate`

#  Initial Data

**Step 1:** Import snomed data with `python manage.py loaddata initial_data/snomedct.json`

**Step 2:** Import snomed data with `python manage.py loaddata initial_data/og.json`

#  Run Django App

**python manage_local.py runserver**
