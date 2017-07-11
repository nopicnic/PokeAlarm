from PokeAlarm.Cache import Cache
import configargparse
import logging

'''
This script will import a CSV file with gym details into the cache so that RM do not have to keep scanning gyms for 
PokeAlarm to show gym names in raids.

Step 1. Enable gym details in RocketMap 
        Use the -gi command line flag (gym-info in config file) to turn on getting names and details on gyms
        Let the gym scanning stay on for an hour or so, to make sure all the raids are in your database.
        You may now turn off gym-info to save requests
Step 2. Export the gymdetails table from your database
        Fire up your SQL command prompt (mysql -u root -p) and run:

select 'gym_id','name','description','url'
UNION ALL
select TO_BASE64(gym_id) as gym_id,name,trim(TRAILING '\n' FROM description) as description,url FROM gymdetails
INTO outfile 'exported_gyms.csv'
FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n';

Step 3. Import the gym info into PokeAlarm
        Copy your new CSV file (exported_gyms.csv unless you changed the name in the last step) into the PokeAlarm 
        folder. 
        note the name of your Manager - this makes things a bit easier. Defined in config.ini as such:
            manager_name: [ MyPokeManager ]
        
        execute the script:
         
         python import_gyms.py -n MyPokeManager exported_gyms.csv
         
         
         The script will run and tell you how many gyms were imported. The rsult will be a file named
            cached_MyPokeManager_gym.pkl
        
        DO NOT DELETE THIS FILE - it is your cache. 
        
        You may delete the CSV file.
        
        If you have several managers, you need to copy the cached_manager_gym.pkl with similar names (WIP) 
        
        100% NO SUPPORT OR HELP ON THIS, YOU ARE ON YOUR OWN
'''

logging.basicConfig(format='%(asctime)s[%(levelname)8.8s] %(message)s',
                    level=logging.INFO)

parser = configargparse.ArgParser(description='Import gym details from a CSV file')
parser.add_argument('-n', '--name', help='Name of manager to import into.',required=True)
parser.add_argument('csv_file',help="CSV file to import")
args = parser.parse_args()

cache = Cache(args.name)
cache.import_gym_csv(args.csv_file)