# -*- coding: utf-8 -*-
import APIURI
import numpy as np
import pandas as pd
from datetime import date
from utils import _parse_author, _parse_author_retrieval,\
        _parse_affiliation, _parse_entry, _parse_citation,\
        _parse_abstract_retrieval

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

    def search(self, query, count=100):
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

        from utils import _search_scopus

        if type(count) is not int:
            raise ValueError("%s is not a valid input for the number of entries to return." %number)

        result_df, total_count = _search_scopus(self.apikey, query, 1)

        if count < 25:
            # if less than 25, just one page of response is enough
            return result_df[:count]

        if total_count <= count:
            count = total_count

        # if larger than, go to next few pages until enough
        index = 1
        while True:
            result_df = result_df.append(_search_scopus(self.apikey, query, 1, index), ignore_index=True)
            if len(result_df.index) >= count:
                return result_df[:count]
            index += 1

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

        from utils import _search_scopus

        result_df, total_count = _search_scopus(self.apikey, query, 2)
        if type(count) is not int:
            raise ValueError("%s is not a valid input for the number of entries to return." %str(count))

        if count < 25:
            # if less than 25, just one page of response is enough
            return result_df[:count]

        if total_count <= count:
            count = total_count

        # if larger than, go to next few pages until enough
        index = 1
        while True:
            result_df = result_df.append(_search_scopus(self.apikey, query, 2, index), ignore_index=True)
            if len(result_df.index) >= count:
                return result_df[:count]
            index += 1

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

        import requests, APIURI
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

        import requests, APIURI
        par = {'apikey': self.apikey, 'httpAccept': 'application/json'}
        r = requests.get('%s/%s'%(APIURI.ABSTRACT, scopus_id), params=par)

        js = r.json()

        try:
            return _parse_abstract_retrieval(js)
        except:
            raise ValueError('Abstract for %s not found!' %scopus_id)

    def retrieve_citation(self, scopus_id, daterange=None, show=True, write2file=None):
        '''
            daterange is a tuple
            write2file: file path
            return a list of citations over time
        '''

        # by default: recent three years
        if daterange is None:
            this_year = date.today().year
            daterange = (this_year-2, this_year)

        datestring = '%i-%i' %(daterange)
        
        if scopus_id is str or scopus_id is unicode:
            citation_url = "%sapikey=%s&scopus_id=%s&date=%s&httpAccept=application/xml" \
                    %(self._citation_overview_url_base, self.apikey, scopus_id, datestring)
        else:
            citation_url = "%sapikey=%s&scopus_id=%s&date=%s&httpAccept=application/xml" \
                    %(self._citation_overview_url_base, self.apikey, ",".join(scopus_id), datestring)

        soup = bs(urlopen(citation_url).read(), 'lxml')

        pub_citation_dict = _parse_citation(soup, daterange)

        if show:
            yearrange = range(daterange[0], daterange[1]+1)
            print 'Scopus ID\t StartYear\t Previous\t %s \t\t Later' %('\t\t '.join(map(str, yearrange)))
            for pub in pub_citation_dict:
                print '%s\t %i\t\t %i\t\t %s\t\t %i' %(pub, pub_citation_dict[pub]['year'],\
                    pub_citation_dict[pub]['previous_count'],\
                    '\t\t '.join(map(str, pub_citation_dict[pub]['annual_count'])),\
                    pub_citation_dict[pub]['later_count'])
        
        if write2file:
            f = io.open(write2file, 'w', encoding='utf-8')
            writer = csv.writer(f)
            yearrange = range(daterange[0], daterange[1]+1)
            writer.writerow(['Scopus ID', 'previous'] + yearrange + ['later'])
            for pub in pub_citation_dict:
                writer.writerow([pub, pub_citation_dict[pub]['previous_count']] + \
                    pub_citation_dict[pub]['annual_count'] + [pub_citation_dict[pub]['later_count']])

            f.close()

        # }}}
        return pub_citation_dict

