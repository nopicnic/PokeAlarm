from PokeAlarm.Cache import Cache
import configargparse

parser = configargparse.ArgParser(description='Import gym details from a CSV file')
parser.add_argument('-n', '--name', help='Name of manager to import into.',required=True)
parser.add_argument('csv_file',help="CSV file to import")
args = parser.parse_args()

cache = Cache(args.name)
cache.import_gym_csv(args.csv_file)