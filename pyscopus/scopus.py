# -*- coding: utf-8 -*-

import requests, warnings, os, json
import numpy as np
import pandas as pd
from datetime import date
from pyscopus import APIURI
from pyscopus.utils import _parse_author, _parse_author_retrieval,\
        _parse_affiliation, _parse_entry, _parse_citation,\
        _parse_abstract_retrieval, trunc,\
        _search_scopus, _parse_serial, _parse_aff

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

    def search(self, query, count=100, type_=1, view='COMPLETE'):
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
            view : string
                Returned result view (i.e., return fields). Can only be STANDARD for author search.

            Returns
            ----------------------------------------------------------------------
            pandas.DataFrame
               Data frame of search results.
        '''


        if type(count) is not int:
            raise ValueError("%s is not a valid input for the number of entries to return." %number)

        result_df, total_count = _search_scopus(self.apikey, query, type_, view=view)

        if total_count <= count:
            count = total_count

        if count <= 25:
            # if less than 25, just one page of response is enough
            return result_df[:count]

        # if larger than, go to next few pages until enough
        i = 1
        while True:
            index = 25*i
            result_df = pd.concat([ result_df, _search_scopus(self.apikey, query, type_, view=view, index=index) ], ignore_index=True)
            if result_df.shape[0] >= count:
                return result_df[:count]
            i += 1

    def search_author(self, query, view='STANDARD', count=10):
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
            view : string
                Returned result view (i.e., return fields). Can only be STANDARD for author search.

            Returns
            ----------------------------------------------------------------------
            pandas.DataFrame
               Data frame of search results.
        '''

        return self.search(query, count, type_=2, view=view)

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

    def retrieve_abstract(self, scopus_id, download_path=None, view='FULL'):
        '''
            Retrieve publication abstracts
            Details: https://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl

            Parameters
            ----------------------------------------------------------------------
            scopus_id : str
                Scopus id of a publication in Scopus database.
            download_path : str
                Where to save JSON response for this abstract retreival result. Default is None (do not save)
            view : str
                Options: BASIC, META, META_ABS, REF, FULL (default)


            Returns
            ----------------------------------------------------------------------
            dict
               Dictionary of publication id, title, and abstract.
        '''

        par = {'apikey': self.apikey, 'httpAccept': 'application/json', 'view': view}
        r = requests.get('%s/%s'%(APIURI.ABSTRACT, scopus_id), params=par)

        js = r.json()

        if download_path is not None:
            if not os.path.exists(download_path):
                os.mkdir(download_path)
            if not download_path.endswith('/'):
                download_path += '/'
            json.dump(js, open(download_path+scopus_id+'.json', 'w'))

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

    def retrieve_full_text(self, full_text_link):
        r = requests.get(full_text_link, params={'apikey': self.apikey,
                                                 'httpAccept': 'application/json'}
                        )
        return r.json()['full-text-retrieval-response']['originalText']

    def search_serial(self, title, view='CITESCORE', count=200):
        '''
            Search serial title metadata
            Details: https://dev.elsevier.com/documentation/SerialTitleAPI.wadl

            Parameters
            ----------
            title : str
                Title to be searched in the database
            view : str
                Options: STANDARD, ENHANCED, CITESCORE (default), COVERIMAGE
            count : int
                Max number of results to be returned (200 by default)

            Returns
            -------
            3 pandas DataFrames:
                - first one is the meta information
                - second one is the temporal citescore in each year
                - last one is the temporal rank/percentile for each subject code in each year
            If cite score is not avaiable then the last two are empty
        '''
        if type(count) != int or count > 200:
            warnings.warn("count corrected to be 200", UserWarning)
            count = 200
        if view not in ['STANDARD', 'ENHANCED', 'CITESCORE']:
            warnings.warn("view corrected to be CITESCORE", UserWarning)
            view = 'CITESCORE'
        par = {'apiKey': self.apikey, 'title': title,
                'count': count, 'view': view}
        r = requests.get(APIURI.SERIAL_SEARCH, par)
        return _parse_serial(r.json())

    def retrieve_serial(self, issn, view='CITESCORE'):
        '''
            Retrieve serial title metadata, given issn
            Details: https://dev.elsevier.com/documentation/SerialTitleAPI.wadl

            Parameters
            ----------
            issn : str
                ISSN of the serial
            view : str
                Options: STANDARD, ENHANCED, CITESCORE (default), COVERIMAGE

            Returns
            -------
            3 pandas DataFrames:
                - first one is the meta information
                - second one is the temporal citescore in each year
                - last one is the temporal rank/percentile for each subject code in each year
            If cite score is not avaiable then the last two are empty
        '''

        if view not in ['STANDARD', 'ENHANCED', 'CITESCORE']:
            warnings.warn("view corrected to be CITESCORE", UserWarning)
            view = 'CITESCORE'
        par = {'apiKey': self.apikey, 'view': view}

        r = requests.get(APIURI.SERIAL_RETRIEVAL+issn,
                         params=par)
        return _parse_serial(r.json())

    def retrieve_affiliation(self, aff_id, view='STANDARD'):
        '''
            Retrieve affiliation profile, given id
            Details: https://dev.elsevier.com/documentation/AffiliationRetrievalAPI.wadl

            Parameters
            ----------
            aff_id : str
                affiliation_id
            view : str
                Options: STANDARD (default), LIGHT, BASIC

            Returns
            -------
        '''

        par = {'apiKey': self.apikey, 'view': view, 'httpAccept': 'application/json'}

        r = requests.get(APIURI.AFFL_RETRIEVAL+aff_id,
                         params=par)
        d = _parse_aff(r.json()['affiliation-retrieval-response'])
        d['aff_id'] = aff_id
        return d
