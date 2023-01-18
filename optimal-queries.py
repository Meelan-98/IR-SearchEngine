import json



def multi_match(query, fields=['title','song_lyrics'], operator ='or'):
	q = {
		"query": {
			"multi_match": {
                "query": query,
                "fields": fields,
                "type": "best_fields", # best_fields, most_fields, cross-fields, phrase, phrase_prefix try all
                "operator": "or",
                "minimum_should_match": 2, # How many terms must be included to match if the operator is or
                "analyzer": "standard", # standard, simple, whitespace, stop, keyword, pattern, <language>, fingerprint
                "fuzziness": "AUTO", # The number of character edits (insert, delete, substitute) to get the required term
                "fuzzy_transpositions": True, # Allow character swaps
                "lenient": False, # Avoid data type similarity requirement
                "prefix_length": 0, 
                "max_expansions": 50,
                "auto_generate_synonyms_phrase_query": True,
                "cutoff_frequency": 0.01,
                "zero_terms_query": "none"
			}
		}
	}
	return q



