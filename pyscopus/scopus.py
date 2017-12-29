# -*- coding: utf-8 -*-

import requests
import numpy as np
import pandas as pd
from datetime import date
from pyscopus import APIURI
from pyscopus.utils import _parse_author, _parse_author_retrieval,\
        _parse_affiliation, _parse_entry, _parse_citation,\
        _parse_abstract_retrieval, trunc,\
        _search_scopus

'''
    03/03/2017:
    Rewriting the whole class by request package
    Use pandas.DataFrame and numpy.ndAarray all the time.
'''

class Scopus(object):

    '''
        Scopus class.
        For instantiation of scopus objects to retrieve data from scopus.com
        Refer to http://zhiyzuo.github.com/python-scopus for more information
        Let me know if there's any issue with this code.

        Happy coding,
        Zhiya
        zhiyazuo@gmail.com
    '''

    def __init__(self, apikey=None):
        self.apikey = apikey

    def add_key(self, apikey):
        self.apikey = apikey

    def search(self, query, count=100, type_=1):
        '''
            Search for documents matching the keywords in query
            Details: http://api.elsevier.com/documentation/SCOPUSSearchAPI.wadl
            Tips: http://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm

            Parameters
            ----------------------------------------------------------------------
            query : str
                Query style (see above websites).
            count : int
                The number of records to be returned.

            Returns
            ----------------------------------------------------------------------
            pandas.DataFrame
               Data frame of search results.
        '''


        if type(count) is not int:
            raise ValueError("%s is not a valid input for the number of entries to return." %number)

        result_df, total_count = _search_scopus(self.apikey, query, type_)

        if total_count <= count:
            count = total_count

        if count < 25:
            # if less than 25, just one page of response is enough
            return result_df[:count]

        # if larger than, go to next few pages until enough
        i = 1
        while True:
            index = 25*i
            result_df = result_df.append(_search_scopus(self.apikey, query, type_, index),
                                         ignore_index=True)
            if result_df.shape[0] >= count:
                return result_df[:count]
            i += 1

    def search_author(self, query, count=10):
        '''
            Search for specific authors
            Details: http://api.elsevier.com/documentation/AUTHORSearchAPI.wadl
            Fields: http://api.elsevier.com/content/search/fields/author

            Parameters
            ----------------------------------------------------------------------
            query : str
                Query style (see above websites).
            count : int
                The number of records to be returned.

            Returns
            ----------------------------------------------------------------------
            pandas.DataFrame
               Data frame of search results.
        '''

        return self.search(query, count, 2)

    def search_author_publication(self, author_id, count=10000):
        '''
            Returns a list of document records for an author in the form of pandas.DataFrame.

            Search for specific authors' document records in Scopus
            Same thing for search, with search limited to author id

            Parameters
            ----------------------------------------------------------------------
            author_id : str
                Author id in Scopus database.
            count : int
                The number of records to return. By default set to 10000 for all docs.

            Returns
            ----------------------------------------------------------------------
            pandas.DataFrame
               Data frame of search results.
        '''

        query = 'au-id(%s)'%author_id
        return self.search(query, count)

    def retrieve_author(self, author_id):
        '''
            Search for specific authors
            Details: http://api.elsevier.com/documentation/AuthorRetrievalAPI.wadl

            Parameters
            ----------------------------------------------------------------------
            author_id : str
                Author id in Scopus database.

            Returns
            ----------------------------------------------------------------------
            dict
               Dictionary of author information.
        '''

        par = {'apikey': self.apikey, 'httpAccept': 'application/json'}
        r = requests.get('%s/%s'%(APIURI.AUTHOR, author_id), params=par)

        js = r.json()
        try:
            return _parse_author_retrieval(js)
        except:
            raise ValueError('Author %s not found!' %author_id)

    def retrieve_abstract(self, scopus_id):
        '''
            Retrieve publication abstracts
            Details: https://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl

            Parameters
            ----------------------------------------------------------------------
            scopus_id : str
                Scopus id of a publication in Scopus database.

            Returns
            ----------------------------------------------------------------------
            dict
               Dictionary of publication id, title, and abstract.
        '''

        par = {'apikey': self.apikey, 'httpAccept': 'application/json'}
        r = requests.get('%s/%s'%(APIURI.ABSTRACT, scopus_id), params=par)

        js = r.json()

        try:
            return _parse_abstract_retrieval(js)
        except:
            raise ValueError('Abstract for %s not found!' %scopus_id)

    def retrieve_citation(self, scopus_id_array, year_range):
        '''
            Retrieve citation counts
            Details: https://api.elsevier.com/documentation/AbstractCitationAPI.wadl

            Parameters
            ----------------------------------------------------------------------
            scopus_id_array : array (list, tuple or np.array)
                Scopus id of a publication in Scopus database.

            year_range : array (list, tuple or np.array) of length 2
                1st element is the start year; 2nd element is the end year. Both integers.

            Returns
            ----------------------------------------------------------------------
            pandas DataFrame
               Data frame of citation counts over time.
        '''

        date = '%i-%i' %(year_range[0], year_range[1])

        par = {'apikey': self.apikey, 'scopus_id': ','.join(scopus_id_array), \
                'httpAccept':'application/json', 'date': date}

        r = requests.get(APIURI.CITATION, params=par)
        js = r.json()

        return _parse_citation(js, year_range)

