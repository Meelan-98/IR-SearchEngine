from elasticsearch import Elasticsearch, helpers
import configparser
import queries
import booster
from booster import isEnglish

config = configparser.ConfigParser()
config.read('config.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)

INDEX = 'sinhala-metaphors'

def boost(boost_array):

    term1 ="english_name^{}".format(boost_array[0])
    term2 = "english_lyricist^{}".format(boost_array[1])
    term3 = "english_composer^{}".format(boost_array[2])
    term4 = "english_singer^{}".format(boost_array[3])
    term5 = "sinhala_name^{}".format(boost_array[4])
    term6 = "sinhala_lyricist^{}".format(boost_array[5])
    term7 = "sinhala_composer^{}".format(boost_array[6])
    term8 = "sinhala_singer^{}".format(boost_array[7])
    term9 = "lyrics^{}".format(boost_array[8])
    term10 = "sinhala_meta_one^{}".format(boost_array[9])
    term11 = "sinhala_meta_one_meaning^{}".format(boost_array[10])
    term12 = "sinhala_meta_two^{}".format(boost_array[11])
    term13 = "sinhala_meta_two_meaning^{}".format(boost_array[12])
    
    return [term1,term2,term3,term4,term5,term6,term7,term8,term9,term10,term11,term12,term13]

def search(phrase,search_type):

    tokens = phrase.split()

    if (search_type == "anywhere"):

        flags = booster.boost_field(phrase)
        fields = boost(flags)
        
        num = 0
        counted_list = False
        dig_list = [int(s) for s in tokens if s.isdigit()]

        if ("Top" in phrase or "top" in phrase or "හොඳම" in phrase or "හොදම" in phrase) and len(dig_list)==1:
            num = dig_list[0]
            counted_list =  True
        
        if counted_list == False:     # If the query contain a number call sort query
            query_body = queries.fuzzy_multi_match(phrase, fields)
        else:
            query_body = queries.sorted_fuzzy_multi_match(phrase, num, fields)

    elif (search_type == "title_only"):
        if (isEnglish(phrase)==True):
            query_body = queries.single_phrase_match(phrase, "english_name")
        else:
            query_body = queries.single_phrase_match(phrase, "sinhala_name")

    elif (search_type == "metaphors_only"):
        if (isEnglish(phrase)==False):
            query_body = queries.multi_match(phrase, ["sinhala_meta_one","sinhala_meta_two"])
        else:
            return("Cannot search metaphors in english")
    
    elif (search_type == "composers_only"):
        if (isEnglish(phrase)==True):
            query_body = queries.single_field_full_match(phrase,"english_composer")
        else:
            query_body = queries.single_field_full_match(phrase,"sinhala_composer")

    res = es.search(index=INDEX, body=query_body) # Calling the elastic search client with the corresponding query body
    return res