from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Index
import json
import configparser
import queries

config = configparser.ConfigParser()
config.read('config.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)

INDEX = 'sinhala-metaphors'

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def boost(boost_array):

    term1 ="english_name^{}".format(boost_array[1])
    term2 = "english_lyricist^{}".format(boost_array[2])
    term3 = "english_composer^{}".format(boost_array[3])
    term4 = "english_singer^{}".format(boost_array[4])
    term5 = "sinhala_name^{}".format(boost_array[5])
    term6 = "sinhala_lyricist^{}".format(boost_array[6])
    term7 = "sinhala_composer^{}".format(boost_array[7])
    term8 = "sinhala_singer^{}".format(boost_array[8])
    term9 = "lyrics^{}".format(boost_array[9])
    term10 = "sinhala_meta_one^{}".format(boost_array[10])
    term11 = "sinhala_meta_one_meaning^{}".format(boost_array[8])
    term12 = "sinhala_meta_two^{}".format(boost_array[9])
    term13 = "sinhala_meta_two_meaning^{}".format(boost_array[10])
    
    return [term1,term2,term3,term4,term5,term6,term7,term8,term9,term10,term11,term12,term13]

def search(phrase):

    flags = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    num=0

    tokens = phrase.split()

    dig_list = [int(s) for s in tokens if s.isdigit()]

    if ("Top" in phrase or "top" in phrase or "හොඳම" in phrase or "හොදම" in phrase) and len(dig_list)==1:
        num = dig_list[0]
        flags[0] = 1
        
    fields = boost(flags)
    print(fields)
    
    # If the query contain a number call sort query
    if flags[0] == 0:
        query_body = queries.fuzzy_multi_match(phrase, fields)
        print('Making Faceted Query')
    else:
        query_body = queries.sorted_fuzzy_multi_match(phrase, num, fields)
        print('Making Range Query')

    res = es.search(index=INDEX, body=query_body) # Calling the elastic search client with the corresponding query body

    return res