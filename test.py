
from pyscopus import Scopus

# please generate your own key
key = "*********"
scopus = Scopus(key)

#query_dict = {'affil': 'University of Iowa', 'authfirst': 'Xi', 'authlast': 'Wang'}
#query_dict = {'affil': 'Stanford University', 'authfirst': 'Andrew', 'authlast': 'Ng'}
#scopus.search_author(query_dict)

#pub_info = scopus.search_abstract('0141607824')
andrew_pubs = scopus.search_author_publication('35410071600')
lda = andrew_pubs[152]

