#TODO: warning

class Scopus(object):

    '''
        Scopus Class
    '''
    _search_url_base = "http://api.elsevier.com/content/search/scopus?"
    _author_url_base = "http://api.elsevier.com/content/search/author?"
    _abstract_url_base = "http://api.elsevier.com/content/abstract/scopus_id/"

    def __init__(self, apikey=None):
        self.apikey = apikey

    def _parse_affiliation(self, affilixml):
        institution = affilixml.find('affilname').text
        city = affilixml.find('affiliation-city').text
        country = affilixml.find('affiliation-country').text
        return institution + ', ' + city + ', ' + country
    
    def _parse_author(self, authorxml):
        author_id = authorxml.find('dc:identifier').text.split(':')[-1]
        lastname = authorxml.find('surname').text
        firstname = authorxml.find('given-name').text
        document_count = int(authorxml.find('document-count').text)
        # affiliations
        affil = authorxml.find('affiliation-current')
        institution = affil.find('affiliation-name').text
        city = affil.find('affiliation-city').text
        country = affil.find('affiliation-country').text
        affiliation = institution + ', ' + city + ', ' + country

        return {'author_id': author_id, 'name': firstname + ' ' + lastname, 'document_count': document_count,\
                'affiliation': affiliation}

    def _parse_xml(self, xml):
        # {{{ _parse_xml
        try:
            scopus_id = xml.find('dc:identifier').text.split(':')[-1]
        except:
            scopus_id = None
        try:
            title = xml.find('dc:title').text
        except:
            title = None
        try:
            publicationname = xml.find('prism:publicationname').text
        except:
            publicationname = None
        try:
            issn = xml.find('prism:issn').text
        except:
            issn = None
        try:
            isbn = xml.find('prism:isbn').text
        except:
            isbn = None
        try:
            eissn = xml.find('prism:eissn').text
        except:
            eissn = None
        try:
            volume = xml.find('prism:volume').text
        except:
            volume = None
        try:
            pagerange = xml.find('prism:pagerange').text
        except:
            pagerange = None
        try:
            coverdate = xml.find('prism:coverdate').text
        except:
            coverdate = None
        try:
            doi = xml.find('prism:doi').text
        except:
            doi = None
        try:
            citationcount = int(xml.find('citedby-count').text)
        except:
            citationcount = None
        try:
            affiliation = self._parse_affiliation(xml.find('affiliation'))
        except:
            affiliation = None
        try:
            aggregationtype = xml.find('prism:aggregationtype').text
        except:
            aggregationtype = None
        try:
            sub_dc = xml.find('subtypedescription').text
        except:
            sub_dc = None

        return {'scopus_id': scopus_id, 'title': title, 'publication_name':publicationname, 'issn': issn, 'isbn': isbn, \
                'eissn': eissn, 'volume': volume, 'page_range': pagerange, 'cover_date': coverdate, 'doi': doi, \
                'citation_count': citationcount, 'affiliation': affiliation, 'aggregation_type': aggregationtype, \
                'subtype_description': sub_dc}
        #}}}
        
    def authenticate(self, apikey):
        self.apikey = apikey

    '''
    def search(self, query, verbose=False):
        #{{{ general search
        import warnings
        import numpy as np
        from urllib2 import urlopen
        from bs4 import BeautifulSoup as bs
        #TODO: Verbose mode

        '''
            General search
            Search fields: http://api.elsevier.com/content/search/fields/scopus
        '''
        pass
        #}}}
    '''

    def search_author(self, query_dict, show=True, verbose=False):
        #{{{ search for author
        import warnings
        import numpy as np
        import pandas as pd 
        from urllib2 import urlopen
        from bs4 import BeautifulSoup as bs
        #TODO: Verbose mode;
        #      Limited to "and" logic

        '''
            Search for specific authors
            Details: http://api.elsevier.com/documentation/AUTHORSearchAPI.wadl
            Fields: http://api.elsevier.com/content/search/fields/author

            query_dict: a dictoinary containing all the fields as key-value pairs
        '''

        # parse query dictionary
        from urllib import quote
        query = ''
        for key in query_dict:
            query += key + '%28{}%29'.format(quote(query_dict[key])) + '%20and%20'
        query = query[:-9]

        url = self._author_url_base +\
            'apikey={}&query={}&start=0&httpAccept=application/xml'.format(self.apikey, query)


        soup = bs(urlopen(url).read(), 'lxml')
        total = float(soup.find('opensearch:totalresults').text)

        print 'A total number of ', int(total), ' records for the query.'
        starts = np.array([i*25 for i in range(int(np.ceil(total/25.)))])

        author_list = []
        for start in starts:
            search_url = self._author_url_base + \
            'apikey={}&start={}&query={}&httpAccept=application/xml'.format(self.apikey, start, query)

            results = bs(urlopen(search_url).read(), 'lxml')
            entries = results.find_all('entry')
            for entry in entries:
                author_list.append(self._parse_author(entry))

        if show:
            df = pd.DataFrame(author_list)
            print df
        
        return author_list
        # }}}

    def search_author_publiaction(self, author_id, verbose=False):
        #{{{ search author's publications
        import warnings
        import numpy as np
        from urllib2 import urlopen
        from bs4 import BeautifulSoup as bs
        #TODO: Verbose mode

        '''
            Search author's publication by author id
        '''
        url = self._search_url_base + 'apikey={}&query=au-id({})&start=0&httpAccept=application/xml'.format(self.apikey, author_id)
        soup = bs(urlopen(url).read(), 'lxml')
        total = float(soup.find('opensearch:totalresults').text)
        print 'A toal number of ', int(total), ' records for author ', author_id
        starts = np.array([i*25 for i in range(int(np.ceil(total/25.)))])

        publication_list = []
        for start in starts:
            search_url = self._search_url_base + 'apikey={}&start={}&query=au-id({})&httpAccept=application/xml'.format(self.apikey, start, author_id)
            results = bs(urlopen(search_url).read(), 'lxml')
            entries = results.find_all('entry')
            for entry in entries:
                publication_list.append(self._parse_xml(entry))
        
        return publication_list
        # }}}
    
    def search_abstract(self, scopus_id=None, pub_record=None, save=False, verbose=False):
        #{{{ search for abstracts
        import warnings
        import numpy as np
        from urllib2 import urlopen
        from bs4 import BeautifulSoup as bs
        #TODO: Verbose mode; Fixing possible bugs
        '''
            pub_record: a dictionary storing the specified publication's information
        '''
        if scopus_id == None:
            scopus_id = pub_record['scopus_id']

        abstract_url = self._abstract_url_base + scopus_id + "?APIKEY={}&httpAccept=application/xml".format(self.apikey)

        try:
            abstract = bs(urlopen(abstract_url).read(), 'lxml')
        except:
            print 'Fail to retrieve the abstract of publication: ', scopus_id
            return None

        if save:
            with open('./{}.xml'.format(scopus_id), 'w') as abxml:
                abxml.write(abstract)
        else:
            return abstract
        #}}}
        
