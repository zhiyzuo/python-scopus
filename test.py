
from scopus import Scopus

key = 'f452b9001062d1049c369e08b8eec1c5'
scopus = Scopus(key)

#query_dict = {'affil': 'University of Iowa', 'authfirst': 'Xi', 'authlast': 'Wang'}
query_dict = {'affil': 'University of Iowa', 'authfirst': 'Tianbao', 'authlast': 'Yang'}
scopus.search_author(query_dict)

#print scopus.search_abstract('84928618086')
#print scopus.search_author_publication('56226310300')
