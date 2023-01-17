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

INDEX = 'sinhala-songs'

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def boost(boost_array):
    # views is not taken for search
    
    term1 ="title^{}".format(boost_array[1])
    term2 = "genre^{}".format(boost_array[2])
    term3 = "english_artist^{}".format(boost_array[3])
    term4 = "artist^{}".format(boost_array[4])
    term5 = "english_lyricist^{}".format(boost_array[5])
    term6 = "lyrics^{}".format(boost_array[6])
    term7 = "english_music^{}".format(boost_array[7])
    term8 = "music^{}".format(boost_array[8])
    term9 = "song_lyrics^{}".format(boost_array[9])
    term10 = "guitar_key^{}".format(boost_array[10])
    
    return [term1,term2,term3,term4,term5,term6,term7,term8,term9,term10]

def search(phrase):
    # flag order
    # 0 - number
    # 1 - title
    # 2 - sin_gen
    # 3 - eng_art
    # 4 - sin_art
    # 5 - eng_lyr
    # 6 - sin_lyr
    # 7 - eng_mus
    # 8 - sin_mus
    # 9 - song_lyrics
    # 10 - guitar_key
    flags = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    num=0
    # If term is in english,boost guitar key
    if isEnglish(phrase):
        print ('English:',phrase)
        flags[3] = 2
        flags[5] = 2
        flags[7] = 2
        flags[10] = 3
        print ('Boosting for english language')
    else:
        print('Sinhala:',phrase)
        flags[2] = 3
        flags[4] = 3
        flags[6] = 3
        flags[8] = 3
        flags[9] = 3
        print('Boosting for sinhala language')

    tokens = phrase.split()
    # Identify numbers
    for word in tokens:
        if word.isdigit():
            flags[0] = 1
            num = int(word)
            print ('Identified sort number',num)
        # Check whether a value from any list is present
        for i in range(2,9):
            if word in all_lists[i]:
                print('Boosting field',i,'for',word,'in all list')
                flags[i] = 5
        # Check whether token matches any synonyms
        for i in range(2,9):
            if word in synonym_list[i]:
                print('Boosting field', i, 'for', word, 'in synonym list')
                flags[i] = 5
        if word in syn_key:
            print('Boosting guitar key')
            flags[10] = 5
        if word in syn_popularity:
            print('Start sort by views')
            if flags[0] == 0:
                flags[0] = 1
                num = 500
    # Check whether full phrase is in any list
    for i in range(2, 9):
        if phrase in all_lists[i]:
            print('Boosting field', i, 'for', phrase, 'in all list')
            flags[i] = 5
    # If there are more than 5 words,boost lyrics
    if len(tokens) > 5:
        print('Boosting song lyrics for tokens > 5')
        flags[9] = 5
    fields = boost(flags)
    print(fields)
    # If the query contain a number call sort query
    if flags[0] == 0:
        query_body = queries.agg_multi_match_q(phrase, fields)
        print('Making Faceted Query')
    else:
        query_body = queries.agg_multi_match_and_sort_q(phrase, num, fields)
        print('Making Range Query')
    res = es.search(index=INDEX, body=query_body)
    return res

def get_all_gen():
    with open('summary-corpus/all_genres.json', 'r') as t:
        all_genres = json.loads(t.read())
        return all_genres.keys(), all_genres.values()
def get_all_art():
    with open('summary-corpus/all_artists.json', 'r') as t:
        all_artists = json.loads(t.read())
        return all_artists.keys(), all_artists.values()
def get_all_lyrics():
    with open('summary-corpus/all_lyricists.json', 'r') as t:
        all_lyricists = json.loads(t.read())
        return all_lyricists.keys(), all_lyricists.values()
def get_all_music():
    with open('summary-corpus/all_music.json', 'r') as t:
        all_music = json.loads(t.read())
        return all_music.keys(), all_music.values()


english_genres, sinhala_genres = get_all_gen()
english_artists, sinhala_artists = get_all_art()
english_lyrics, sinhala_lyrics = get_all_lyrics()
english_music, sinhala_music = get_all_music()
all_lists = [None, None, sinhala_genres, english_artists, sinhala_artists, english_lyrics, sinhala_lyrics, english_music, sinhala_music]

syn_lyrics = ['ගත්කරු','රචකයා','ලියන්නා','ලියන','රචිත','ලියපු','ලියව්‌ව','රචනා','රචක','ලියන්']
syn_eng_lyrics = ['lyricist','write','wrote','songwriter']
syn_artist = ['ගායකයා','ගයනවා','ගායනා','ගායනා','ගැයු','ගයන']
syn_eng_artist = ['sing', 'artist','singer','sung']
syn_music = ['සංගීත']
syn_eng_music = ['composer','music','composed']
syn_popularity=['හොඳම','ජනප්‍රිය','ප්‍රචලිත','ප්‍රසිද්ධ','හොදම','ජනප්‍රියම']
syn_key = ['Minor','Major','minor','major']
syn_genre = ['කැලිප්සෝ','සම්භාව්ය','වත්මන්','චිත්‍රපට','පොප්','දේවානුභාවයෙන්','රන්','පැරණි','රන්වන්','පොප්','කණ්ඩායම්','යුගල','අලුත්','නව','පැරණි','පොප්ස්']

synonym_list = [None, None, syn_genre, syn_eng_artist, syn_artist, syn_eng_lyrics, syn_lyrics, syn_eng_music, syn_music]
#terms = ["ආදරේ මන්දිරේ",'amaradeva 10','top 10','ඉල්ලීම']

# for word in terms:
#     search(word)