import os
from subprocess import Popen, PIPE
import time
import urllib2
from lxml import etree
from optparse import OptionParser

class DownloadError(Exception):
    pass

class ContentParserError(Exception):
    pass

def out(msg, *args):
    """
    @TODO
    """
    print '%s' % (msg)

def call_and_output(*args):
    """
    Wrapper function for calling a subprocess.
    This will wait till it's complete and output the stdout as its running
    """
    cmd = Popen(*args, stdout=PIPE)
    while 1:
        cmdout, cmderr = cmd.communicate()
        if cmdout:
            out(cmdout)
        status = cmd.poll()
        if status:
            return status
        time.sleep(0.5) 

class Config(object):
    """
    Not sure if this is needed yet..

    Configuration object
    """
    __inst = None
    def __new__(cls, *args, **kwargs):
        if not cls.__inst:
            cls.__inst = object.__new__(cls, *args, **kwargs)
        return cls.__inst


class Ted(object):
    """
    Ted Object. Hold all the information about the ted talk. 
    """
    _EXIST_NOT = 1
    _EXIST_PART = 2
    _EXIST_FULL = 3

    existing = None
    part_suffix = '.part'
    def __init__(self, name, url, published, **kwargs):
        self.name = name
        self.url = url
        self.published = published
        self.download_dir = os.getcwd()
        self.filename_tmp = '%s%s' % (self.filename, self.part_suffix)

    def __repr__(self):
        return '%s' % self.name
    
    @property
    def filename(self):
        return self.url.split('/')[-1:][0].split('?')[0]
    
    def download(self, dl_dir=None):
        """
        Call this to method to start downloading this ted. 

        TODO: Look at implementing a python downloader for crossplatformness.
        """
        additional_args = []
        if dl_dir:
            self.download_dir = dl_dir

        exist = self._get_existance_state()
        download_file = self.filename_tmp

        if exist == self._EXIST_FULL:
            out('File \'%s\' already exists..skipping')
        elif exist == self._EXIST_PART:
            out('File partially exists, continuing')
            additional_args = ['-c']

        cmd = ['wget', self.url, '-O', download_file]
        cmd.extend(additional_args)
        out('calling: %s' % ''.join(cmd))
        status = call_and_output(cmd)

        full_path_file = os.path.join(self.self.download_dir, self.filename)
        full_path_tmp = os.path.join(self.self.download_dir, self.filename_tmp)
        try:
            os.rename(full_path_tmp, full_path_file)
        except:
            #TODO
            pass
        
        return status

    def _get_existance_state(self):
        if os.path.isfile(os.path.join(self.download_dir, self.filename)):
            return self._EXIST_FULL
        elif os.path.isfile(os.path.join(self.download_dir, self.filename_tmp)):
            return self._EXIST_PART
        else:
            return self._EXIST_NOT


    def get_download_size(self):
        pass


    def set_existing(self, value):
        self.existing = value


class TedList(object):
    """
    """
    url = 'http://www.ted.com/talks/quick-list'
    _ted_list = []
    _existing_ted_list = []
    _html_tree = None
    _ted_list_completed = []

    def __init__(self, localfile=False):
        self.localfile = localfile
        self.download_dir = os.getcwd()
    
    def __repr__(self):
        return '\n'.join(['%s - %s' % (i, v) for i,v in enumerate(self._ted_list)])
            
    def populate(self):
        """
        Calls the routine methods to download and parse the content
        into a usable list
        """
        self._fetch_list()
        for ted in self._parse_html():
            tedobj = Ted(**ted)
            self._ted_list.append(tedobj)

    def download_one(self, index=0):
        self._ted_list[index].download(self.download_dir)
    
    def download_all(self):
        pass

    def _get_current_ted_list(self):
        self._existing_ted_list = os.listdir(self.download_dir)

    def set_download_dir(self, dl_dir):
        self.download_dir = os.abspath(dl_dir)

    def _fetch_list(self):
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
        if not self._html_tree:
            raise ContentParserError('Oh noes! Something went wrong, no HTML data to parse.')

        for i, tr in enumerate(self._html_tree.xpath('//table')[0].xpath('//tr[td]')):
            children = tr.findall('.//td')
            try:
                extracted = {
                    'published': children[0].text,
                    'name': children[2].find('.//a').text,
                    'url': children[-1].findall('.//a')[-1].attrib.get('href'),
                    'runtime': children[0].text,
                }
            except IndexError:
                continue
            
            yield extracted


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-f', '--local-file', dest='localfile', default=False,
                    help='Use the local html file instead of downloading it.', metavar='FILE')
    (options, args) = parser.parse_args()
    tedlst = TedList(options.localfile)
    out('Tedlst instantiated: %s'  % tedlst)
    tedlst.populate()
    out('Tedlst populated: %s'  % tedlst)
    tedlst.download_one()
