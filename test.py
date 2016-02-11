
from scopus import Scopus

key = 'f452b9001062d1049c369e08b8eec1c5'
scopus = Scopus(key)
print scopus.search_author('56226310300')
#print scopus.search_abstract('84928618086')
