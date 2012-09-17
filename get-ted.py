import urllib2
from lxml import etree
from optparse import OptionParser

class DownloadError(Exception):
    pass

class ContentParserError(Exception):
    pass

def out(msg, *args):
    print '%s' % (msg)


class Ted(object):
    """
    Ted Object. Hold all the information about the ted talk. 
    """
    def __init__(self, name, url, published, **kwargs):
        self.name = name
        self.url = url
        self.published = published

    def __repr__(self):
        return '%s' % self.name
    
    @property
    def filename(self):
        return '__TODO__: Parse Filename from url'

    def download():
        """
        Call this to method to start downloading this ted. 

        TODO: Try using wget. Not sure if the progress meter would
        """
        pass
    
    def get_download_size(self):
        pass


class TedList(object):
    """
    """
    url = 'http://www.ted.com/talks/quick-list'
    _ted_list = [] 
    _html_tree = None
    
    def __init__(self, localfile=False):
        self.localfile = localfile
    
    def __repr__(self):
        return '\n'.join(['%s - %s' % (i, v) for i,v in enumerate(self._ted_list)])
            

    def populate(self):
        """
        Calls the routine methods to download and parse the content
        into a usable list
        """
        self._download_list()
        for ted in self._parse_html():
            self._ted_list.append(Ted(**ted))

    def _download_list(self):
        try:
            f = urllib2.urlopen(self.url) if not self.localfile else open(self.localfile)
        except urllib2.URLError:
            raise DownloadError('Could not download TedTalks List. Check internet connection.')
        except IOError, e:
            raise DownloadError('Could not open TedTalks local file. %s' % e)
        try:
            self._html_tree = etree.parse(f, etree.HTMLParser())
        except Exception, e: # TODO: Replace with appropriate Exception catcher
            raise ContentParserError('Could not parse TedTalks List. %s' % e)
        
    def _parse_html(self):
        """
        Generator function to extract dictionary from the Etree parsed HTML.

        returns: Generator containing instantiated Ted Class

        Example html
        <tr>
	    <td>Aug 2012</td>
	    <td>TEDxBoston 2012</td>
	    <td>
		<a href="http://www.ted.com/talks/caitria_and_morgan_o_neill_how_to_step_up_in_the_face_of_disaster.html">Caitria and Morgan ONeill: How to step up in the face of disaster</a></td>
	    <td>09:23</td>
            <td>
                <a href="http://download.ted.com/talks/CaitriaONeill_2012X-light.mp4?apikey=TEDDOWNLOAD">Low</a> | 
                <a href="http://download.ted.com/talks/CaitriaONeill_2012X.mp4?apikey=TEDDOWNLOAD">Regular</a> | 
                <a href="http://download.ted.com/talks/CaitriaONeill_2012X-480p.mp4?apikey=TEDDOWNLOAD">High</a>
            </td>
	</tr>
        """
        
        for tr in self._html_tree.xpath('//table')[0].xpath('//tr[td]'):
            children = tr.findall('.//td')
            extracted = {
                'published': children[0].text,
                'name': children[2].find('.//a').text,
                'url': children[2].find('.//a').attrib.get('href'),
                'runtime': children[0].text,
            }
            yield extracted


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-f', '--local-file', dest='localfile', default=False,
                    help='Use the local html file instead of downloading it.', metavar='FILE'  )
    (options, args) = parser.parse_args()
    tedlst = TedList(options.localfile)
    out('Tedlst instantiated: %s'  % tedlst)
    tedlst.populate()
    out('Tedlst populated: %s'  % tedlst)
