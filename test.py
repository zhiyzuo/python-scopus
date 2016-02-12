
from scopus import Scopus

key = 'f452b9001062d1049c369e08b8eec1c5'
scopus = Scopus(key)

#query_dict = {'affil': 'University of Iowa', 'authfirst': 'Xi', 'authlast': 'Wang'}
#query_dict = {'affil': 'Stanford University', 'authfirst': 'Andrew', 'authlast': 'Ng'}
#scopus.search_author(query_dict)

pub_info = scopus.search_abstract('0141607824')
#andrew_pubs = scopus.search_author_publication('35410071600')
