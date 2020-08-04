import xml.etree.ElementTree as ET
import re
import time

class XmlParser:
    # Download XML filing
    def download_xml(url, tries=1):
        try:
            response = urllib.request.urlopen(url)
        except:
            print('Something went wrong. Try again', tries)
            if tries < 5:
                time.sleep(5 * tries)
                download_xml(url, tries + 1)
        else:
            # decode the response into a string
            data = response.read().decode('utf-8')
            # set up the regular expression extractoer in order to get the relevant part of the filing
            matcher = re.compile('<\?xml.*ownershipDocument>', flags=re.MULTILINE | re.DOTALL)
            matches = matcher.search(data)
            # the first matching group is the extracted XML of interest
            xml = matches.group(0)
            # instantiate the XML object
            root = ET.fromstring(xml)
            print(url)
            return root
