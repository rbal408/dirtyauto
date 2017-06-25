from bs4 import BeautifulSoup
import requests
from dirtyauto import log


class DigikeyPartInfo(object):

    """For parsing part info on digikey"""

    pricing = ""
    packaging = ""
    mpn = ""
    temp = ""
    moq = ""

    def __init__(self, partn):
        """
        :param part_list: list of the part numbers
        """
        self.log = log(self.__class__.__name__)
        self.partn = partn
        self.soup = self.get_soup(self.partn)

    @staticmethod
    def get_soup(partn):
        """
        :param partn part number input
        """
        page = requests.get(
            "https://www.digikey.com/products/en?keywords=" + partn)
        return BeautifulSoup(page.content, 'html.parser')

    def get_productlnk_from_productTable(self):
        """
        :return: return list with product links from product search table
        """
        links = []
        row_soup = self.soup.find_all('td', {"class": "tr-mfgPartNumber"})
        for item in row_soup:
            int_lnk = item.find('a').get('href')
            links.append("https://www.digikey.com" + int_lnk)
        print(links)
        return links

    def page_type(self):
        """
        :return: return string with type
        """

        if self.soup.find('table', id="productTable"):
            return "productTable"
        elif self.soup.find('table', id='product-dollars'):
            return "productPage"
        elif 'No Results Found | DigiKey Electronics' in self.soup.title.string:
            self.log.error(
                "There's no part found with this part number on DIGIKEY:" + self.partn)
            return None
        elif self.soup.find_all('a', href=True, text='Clock/Timing - Clock Generators, PLLs, Frequency Synthesizers'):
            tree_lnk = self.soup.find(
                'a', href=True, text='Clock/Timing - Clock Generators, PLLs, Frequency Synthesizers')
            # print(tree_lnk)
            # tree_lnk = self.soup.find_all('a', attrs={'href': True,
            #                                           'class': 'catfilterlink'})
            # for div in tree_lnk:
            #     print(div.get('href'))
            # print(tree_lnk['href'])
            # print(type(tree_lnk))
            # print(len(tree_lnk))
            # print(tree_lnk.get('href'))
            product_table_lnk = "https://www.digikey.com" + tree_lnk.get('href')
            print(product_table_lnk)
            _page = requests.get(product_table_lnk)
            self.soup = BeautifulSoup(_page.content, 'html.parser')
            return "searchPage"
        else:
            self.log.error("Found Nothing here with P/N: " + self.partn)

    def parse_table(self):
        pass


class MultiPartDigikey(DigikeyPartInfo):
    """
    Processing multiple parts
    """

    def __init__(self):
        self.log = log(self.__class__.__name__)
        self._part_list = None

    @property
    def part_list(self):
        return self._part_list

    @part_list.setter
    def part_list(self, part_input):
        if not isinstance(part_input, list):
            if isinstance(part_input, str):
                self.log.warning(
                    "Input is not a list, converting string to list")
                self._part_list = [part_input]
                return
            elif isinstance(part_input, int):
                self.log.warning("Input is not a list, converting int to list")
                self._part_list = [str(part_input)]
            else:
                self.log.error("Input is not a list, cannot process " +
                               str(type(part_input)))
        else:
            self._part_list = part_input

    def found_parts(self):
        part_lst = []
        for x in self._part_list:
            _soup = self.get_soup(x)
            if _soup.find("table", id="productTable"):
                part_lst.append(1)
            else:
                part_lst.append(0)
        return part_lst
