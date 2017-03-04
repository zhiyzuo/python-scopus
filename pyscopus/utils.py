# -*- coding: utf-8 -*-
'''
    Helper Functions
'''

import numpy as np
import pandas as pd

def _parse_citation(citexml, daterange):
    citeinfo_list = citexml.find_all('citeinfo')
    pub_citation_dict = {}
    for pub in citeinfo_list:
        pub_id = pub.find('dc:identifier').text.split(':')[-1]
        start_year = np.uint16(pub.find('sort-year').text)
        previous_count = np.uint32(pub.find('pcc').text)
        later_count = np.uint32(pub.find('lcc').text)
        annual_count_tags = pub.find_all('cc')
        annual_count_lists = [np.uint32(annual_count_tags[i].text)\
                for i in range(daterange[1]-daterange[0]+1)]
        
        pub_citation_dict[pub_id] = {'year':start_year, 'previous_count': previous_count,\
                'later_count': later_count, 'annual_count': annual_count_lists}

    return pub_citation_dict

def _parse_affiliation(js_affiliation):
    name = js_affiliation['affilname']
    city = js_affiliation['affiliation-city']
    country = js_affiliation['affiliation-country']
    return '%s, %s, %s' %(name, city, country)

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
        publicationname = entry['prism:publicationname']
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
        eissn = entry['prism:eissn']
    except:
        eissn = None
    try:
        volume = entry['prism:volume']
    except:
        volume = None
    try:
        pagerange = entry['prism:pagerange']
    except:
        pagerange = None
    try:
        coverdate = entry['prism:coverdate']
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
        aggregationtype = entry['prism:aggregationtype']
    except:
        aggregationtype = None
    try:
        sub_dc = entry['subtypedescription']
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

def _parse_author_retrieval(authorxml):
    status = authorxml.find('author-retrieval-response')['status']
    if status != 'found':
        return None
    try:
        num_doc = int(authorxml.find('document-count').text)
    except:
        num_doc = 'n/a'

    try:
        num_cited = int(authorxml.find('cited-by-count').text)
    except:
        num_cited = 'n/a'

    try: 
        num_citation = int(authorxml.find('citation-count').text)
    except:
        num_citation = 'n/a'

    # affiliation
    current_aff_list = authorxml.findAll('affiliation-current')[1].findAll('affiliation')
    aff_list = []
    for aff in current_aff_list:
        id_ = aff['affiliation-id']
        #name_ = aff.find('afdispname').text.encode('utf-8')
        name_ = aff.find('afdispname').text.encode('utf-8')
        addr_tag = aff.find('address')
        try:
            #country_ = addr_tag.find('country').text.encode('utf-8')
            country_ = addr_tag.find('country').text.encode('utf-8')
        except:
            country_ = 'n/a'
        
        try:
            #state_ = addr_tag.find('state').text.encode('utf-8')
            state_ = addr_tag.find('state').text.encode('utf-8')
        except:
            state_ = 'n/a'
        
        try:
            #city_ = addr_tag.find('city').text.encode('utf-8')
            city_ = addr_tag.find('city').text.encode('utf-8')
        except:
            city_ = 'n/a'
        
        try:
            #street_ = addr_tag.find('address-part').text.encode('utf-8')
            street_ = addr_tag.find('address-part').text.encode('utf-8')
        except:
            street_ = 'n/a'
        
        try:
            #postal_code_ = addr_tag.find('postal-code').text.encode('utf-8')
            postal_code_ = addr_tag.find('postal-code').text.encode('utf-8')
        except:
            postal_code_ = 'n/a'
        
        address_ = street_ + ',' + city_ + ',' + state_ + ',' + postal_code_ + ',' + country_
        aff_dict = {'id': id_, 'name': name_, 'address': address_}
        aff_list.append(aff_dict)

    # affiliation history
    try:
        aff_history_list = authorxml.findAll('affiliation-history')[1].findAll('affiliation')
    except:
        aff_history_list = []
    history_aff = []
    for aff in aff_history_list:
        id_ = aff['affiliation-id']
        name_ = aff.find('afdispname').text.encode('utf-8')
        addr_tag = aff.find('address')
        try:
            country_ = addr_tag.find('country').text.encode('utf-8')
        except:
            country_ = 'n/a'
        
        try:
            state_ = addr_tag.find('state').text.encode('utf-8')
        except:
            state_ = 'n/a'
        
        try:
            city_ = addr_tag.find('city').text.encode('utf-8')
        except:
            city_ = 'n/a'
        
        try:
            street_ = addr_tag.find('address-part').text.encode('utf-8')
        except:
            street_ = 'n/a'
        
        try:
            postal_code_ = addr_tag.find('postal-code').text.encode('utf-8')
        except:
            postal_code_ = 'n/a'
        
        address_ = street_ + ',' + city_ + ',' + state_ + ',' + postal_code_ + ',' + country_
        aff_dict = {'id': id_, 'name': name_, 'address': address_}
        history_aff.append(aff_dict)

    # subject areas
    subject_area_list = authorxml.find('subject-areas').findAll('subject-area')
    subject_areas = []
    for sub in subject_area_list:
        subject_areas.append(sub.text.strip().encode('utf-8'))

    # name variants are NOT included
    surname = authorxml.find('preferred-name').find('surname').text.encode('utf-8')
    given_name = authorxml.find('preferred-name').find('given-name').text.encode('utf-8')

    # journal history
    journal_list = authorxml.find('journal-history').findAll('journal')
    journal_history = []
    for j in journal_list:
        journal_history.append(j.find('sourcetitle').text.encode('utf-8'))

    # }}}

    return {'first-name': given_name, 'last-name':surname, 'journal-history': journal_history, \
            'subject-areas': subject_areas, 'affiliation-history': history_aff, 'cited-by-count': num_cited,\
            'current-affiliation': aff_list, 'document-count': num_doc, 'citation-count': num_citation}

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

    import requests, APIURI
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
