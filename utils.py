import requests, time
import pandas as pd
from bs4 import BeautifulSoup as Soup

BASE_URL = "https://api.elsevier.com/content/abstract/scopus_id/"

def _check_pub_validity(sid, author_id, author_affil_id_list, apikey):
    global BASE_URL
    r = requests.get(BASE_URL+sid, params={'apikey': apikey})
    soup = Soup(r.content, 'lxml')
    author_list = soup.find('authors').find_all('author')

    ## go through the author list to find the author first, by matching author id
    for au in author_list:
        if au['auid'] == author_id:
            ## find it and break
            break

    ## check the affiliation id: note that an author may have a list of affiliations
    this_affil_id_list = [affil_tag['id'] for affil_tag in au.find_all('affiliation')]
    ## get the affiliation id and check if there are any overlap
    if len(set(author_affil_id_list).intersection(set(this_affil_id_list))) > 0:
        return True
    return False

def check_pub_validity(scopus_obj, author_id, author_affil_id_list, apikey):
    ## first find out all pub
    pub_df = scopus_obj.search_author_publication(author_id)
    ## do this for all non-null scopus ids
    pub_df = pub_df[~pub_df.scopus_id.isnull()]
    ## list to save all eligble scopus ids
    eligible_scopus_id_list = list()
    for i, sid in enumerate(pub_df.scopus_id.values):
        if (i+1)%5==0:
            time.sleep(pd.np.random.random()+.3)
        if _check_pub_validity(sid, author_id, author_affil_id_list, apikey):
            ## if true, save it
            eligible_scopus_id_list.append(sid)
    ## finally, get a subset of the original pub_df
    filtered_pub_df = pub_df.query("scopus_id in @eligible_scopus_id_list")
    return filtered_pub_df
