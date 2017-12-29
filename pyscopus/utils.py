# -*- coding: utf-8 -*-
'''
    Helper Functions
'''

import requests
import numpy as np
import pandas as pd
from pyscopus import APIURI

def _parse_citation(js_citation, year_range):
    resp = js_citation['abstract-citations-response']
    cite_info_list = resp['citeInfoMatrix']['citeInfoMatrixXML']['citationMatrix']['citeInfo']

    year_range = (year_range[0], year_range[1]+1)
    columns = ['scopus_id', 'previous_citation'] + [str(yr) for yr in range(*year_range)] + ['later_citation', 'total_citation']
    citation_df = pd.DataFrame(columns=columns)

    year_arr = np.arange(year_range[0], year_range[1]+1)
    for cite_info in cite_info_list:
        cite_dict = {}
        # dc:identifier: scopus id
        cite_dict['scopus_id'] = cite_info['dc:identifier'].split(':')[-1]
        # pcc: previous citation counts
        try:
            cite_dict['previous_citation'] = cite_info['pcc']
        except:
            cite_dict['previous_citation'] = pd.np.NaN
        # cc: citation counts during year range
        try:
            cc = cite_info['cc']
        except:
            return pd.DataFrame()
        for index in range(len(cc)):
            year = str(year_arr[index])
            cite_dict[year] = cc[index]['$']
        # lcc: later citation counts
        try:
            cite_dict['later_citation'] = cite_info['lcc']
        except:
            cite_dict['later_citation'] = pd.np.NaN
        # rowTotal: total citation counts
        try:
            cite_dict['total_citation'] = cite_info['rowTotal']
        except:
            cite_dict['total_citation'] = pd.np.NaN
        citation_df = citation_df.append(cite_dict, ignore_index=True)

    return citation_df[columns]

def _parse_affiliation(js_affiliation):
    l = list()
    for js_affil in js_affiliation:
        name = js_affil['affilname']
        city = js_affil['affiliation-city']
        country = js_affil['affiliation-country']
        l.append({'name': name, 'city': city, 'country': country})
    return l

def _parse_author_affiliation(js_affiliation_entry):
    affiliation_dict = {}

    ip_doc = js_affiliation_entry['ip-doc']
    try:
        affiliation_dict['parent-id'] = js_affiliation_entry['@parent']
    except:
        affiliation_dict['parent-id'] = None

    try:
        affiliation_dict['id'] = ip_doc['@id']
    except:
        affiliation_dict['id'] = None

    try:
        affiliation_dict['parent-name'] = ip_doc['parent-preferred-name']
    except:
        affiliation_dict['parent-name'] = None

    try:
        affiliation_dict['name'] = ip_doc['afdispname']
    except:
        affiliation_dict['name'] = None

    try:
        affiliation_dict['address'] = ', '.join(ip_doc['address'].values())
    except:
        affiliation_dict['address'] = None

    try:
        affiliation_dict['url'] = ip_doc['org-URL']
    except:
        affiliation_dict['url'] = None
    return affiliation_dict

def _parse_affiliation_history(js_affiliation_history):
    columns = ('id', 'name', 'parent-id', 'parent-name', 'url')
    affiliation_history_df = pd.DataFrame(columns=columns)

    for affiliation in js_affiliation_history:
        affiliation_history_df = affiliation_history_df.append(\
                                    _parse_author_affiliation(affiliation), \
                                    ignore_index=True)
    return affiliation_history_df

def _parse_author(entry):
    author_id = entry['dc:identifier'].split(':')[-1]
    lastname = entry['preferred-name']['surname']
    firstname = entry['preferred-name']['given-name']
    doc_count = int(entry['document-count'])
    # affiliations
    affil = entry['affiliation-current']
    try:
        institution_name = affil['affiliation-name']
    except:
        institution_name = None
    try:
        institution_id = affil['affiliation-id']
    except:
        institution_id = None
    #city = affil.find('affiliation-city').text
    #country = affil.find('affiliation-country').text
    #affiliation = institution + ', ' + city + ', ' + country

    return pd.Series({'author_id': author_id, 'name': firstname + ' ' + lastname, 'document_count': doc_count,\
            'affiliation': institution_name, 'affiliation_id': institution_id})

def _parse_article(entry):
    try:
        scopus_id = entry['dc:identifier'].split(':')[-1]
    except:
        scopus_id = None
    try:
        title = entry['dc:title']
    except:
        title = None
    try:
        publicationname = entry['prism:publicationName']
    except:
        publicationname = None
    try:
        issn = entry['prism:issn']
    except:
        issn = None
    try:
        isbn = entry['prism:isbn']
    except:
        isbn = None
    try:
        eissn = entry['prism:eIssn']
    except:
        eissn = None
    try:
        volume = entry['prism:volume']
    except:
        volume = None
    try:
        pagerange = entry['prism:pageRange']
    except:
        pagerange = None
    try:
        coverdate = entry['prism:coverDate']
    except:
        coverdate = None
    try:
        doi = entry['prism:doi']
    except:
        doi = None
    try:
        citationcount = int(entry['citedby-count'])
    except:
        citationcount = None
    try:
        affiliation = _parse_affiliation(entry['affiliation'])
    except:
        affiliation = None
    try:
        aggregationtype = entry['prism:aggregationType']
    except:
        aggregationtype = None
    try:
        sub_dc = entry['subtypeDescription']
    except:
        sub_dc = None

    return pd.Series({'scopus_id': scopus_id, 'title': title, 'publication_name':publicationname,\
            'issn': issn, 'isbn': isbn, 'eissn': eissn, 'volume': volume, 'page_range': pagerange,\
            'cover_date': coverdate, 'doi': doi,'citation_count': citationcount, 'affiliation': affiliation,\
            'aggregation_type': aggregationtype, 'subtype_description': sub_dc})

def _parse_entry(entry, type_):
    if type_ == 1 or type_ == 'article':
        return _parse_article(entry)
    else:
        return _parse_author(entry)

def _parse_author_retrieval(author_entry):
    resp = author_entry['author-retrieval-response'][0]

    # create a dict to store the data
    author_dict = {}

    # coredata
    coredata = resp['coredata']
    author_dict['author-id'] = coredata['dc:identifier'].split(':')[-1]
    for item in ('eid', 'document-count', 'cited-by-count', 'citation-count'):
        author_dict[item] = coredata[item]

    # author-profile
    author_profile = resp['author-profile']

    ## perferred name
    perferred_name = author_profile['preferred-name']
    author_dict['name'] = perferred_name['given-name'] + ' ' + perferred_name['surname']
    author_dict['last'] = perferred_name['surname']
    author_dict['first'] = perferred_name['given-name']
    author_dict['indexed-name'] = perferred_name['indexed-name']

    ## publication range
    author_dict['publication-range'] = tuple(author_profile['publication-range'].values())

    ## affiliation-current
    author_dict['affiliation-current'] = _parse_author_affiliation(\
                                         author_profile['affiliation-current']['affiliation'])

    ## journal-history
    author_dict['journal-history'] = pd.DataFrame(author_profile['journal-history']['journal'])

    ## affiliation-history
    author_dict['affiliation-history'] = _parse_affiliation_history(\
                                         author_profile['affiliation-history']['affiliation'])

    return author_dict

def _parse_abstract_retrieval(abstract_entry):
    resp = abstract_entry['abstracts-retrieval-response']

    # coredata
    coredata = resp['coredata']
    # keys to exclude
    unwanted_keys = ('dc:creator', 'link')

    abstract_dict = {key: coredata[key] for key in coredata.keys()\
                                        if key not in unwanted_keys}
    # rename keys
    abstract_dict['scopus-id'] = abstract_dict.pop('dc:identifier').split(':')[-1]
    abstract_dict['abstract'] = abstract_dict.pop('dc:description')
    abstract_dict['title'] = abstract_dict.pop('dc:title')

    return abstract_dict

def _search_scopus(key, query, type_, index=0):
    '''
        Search Scopus database using key as api key, with query.
        Search author or articles depending on type_

        Parameters
        ----------
        key : string
            Elsevier api key. Get it here: https://dev.elsevier.com/index.html
        query : string
            Search query. See more details here: http://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm
        type_ : string or int
            Search type: article or author. Can also be 1 for article, 2 for author.
        index : int
            Start index. Will be used in search_scopus_plus function

        Returns
        -------
        pandas DataFrame
    '''

    par = {'apikey': key, 'query': query, 'start': index, 'httpAccept': 'application/json'}
    if type_ == 'article' or type_ == 1:
        r = requests.get(APIURI.SEARCH, params=par)
    else:
        r = requests.get(APIURI.SEARCH_AUTHOR, params=par)

    js = r.json()
    total_count = int(js['search-results']['opensearch:totalResults'])
    entries = js['search-results']['entry']

    result_df = pd.DataFrame([_parse_entry(entry, type_) for entry in entries])

    if index == 0:
        return(result_df, total_count)
    else:
        return(result_df)

def trunc(s,min_pos=0,max_pos=75,ellipsis=True):
    """Truncation beautifier function
    This simple function attempts to intelligently truncate a given string
    """
    __author__ = 'Kelvin Wong <www.kelvinwong.ca>'
    __date__ = '2007-06-22'
    __version__ = '0.10'
    __license__ = 'Python http://www.python.org/psf/license/'

    """Return a nicely shortened string if over a set upper limit 
    (default 75 characters)
    
    What is nicely shortened? Consider this line from Orwell's 1984...
    0---------1---------2---------3---------4---------5---------6---------7---->
    When we are omnipotent we shall have no more need of science. There will be
    
    If the limit is set to 70, a hard truncation would result in...
    When we are omnipotent we shall have no more need of science. There wi...
    
    Truncating to the nearest space might be better...
    When we are omnipotent we shall have no more need of science. There...
    
    The best truncation would be...
    When we are omnipotent we shall have no more need of science...
    
    Therefore, the returned string will be, in priority...
    
    1. If the string is less than the limit, just return the whole string
    2. If the string has a period, return the string from zero to the first
        period from the right
    3. If the string has no period, return the string from zero to the first
        space
    4. If there is no space or period in the range return a hard truncation
    
    In all cases, the string returned will have ellipsis appended unless
    otherwise specified.
    
    Parameters:
        s = string to be truncated as a String
        min_pos = minimum character index to return as Integer (returned
                  string will be at least this long - default 0)
        max_pos = maximum character index to return as Integer (returned
                  string will be at most this long - default 75)
        ellipsis = returned string will have an ellipsis appended to it
                   before it is returned if this is set as Boolean 
                   (default is True)
    Returns:
        Truncated String
    Throws:
        ValueError exception if min_pos > max_pos, indicating improper 
        configuration
    Usage:
    short_string = trunc(some_long_string)
    or
    shorter_string = trunc(some_long_string,max_pos=15,ellipsis=False)
    """
    # Sentinel value -1 returned by String function rfind
    NOT_FOUND = -1
    # Error message for max smaller than min positional error
    ERR_MAXMIN = 'Minimum position cannot be greater than maximum position'
    
    # If the minimum position value is greater than max, throw an exception
    if max_pos < min_pos:
        raise ValueError(ERR_MAXMIN)
    # Change the ellipsis characters here if you want a true ellipsis
    if ellipsis:
        suffix = '...'
    else:
        suffix = ''
    # Case 1: Return string if it is shorter (or equal to) than the limit
    length = len(s)
    if length <= max_pos:
        return s + suffix
    else:
        # Case 2: Return it to nearest period if possible
        try:
            end = s.rindex('.',min_pos,max_pos)
        except ValueError:
            # Case 3: Return string to nearest space
            end = s.rfind(' ',min_pos,max_pos)
            if end == NOT_FOUND:
                end = max_pos
        return s[0:end] + suffix
