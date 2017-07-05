import re
from ner_v1.constant import FROM_MESSAGE
import ner_v1.detectors.constant as detector_constant
from ner_v1.detectors.textual.text.text_detection import TextDetector


class CityDetector(object):
    """
    CityDetector detects cities from the text. It Detects city with the properties like "from", "to", "via" and
    "normal". These cities are returned in a dictionary form that contains relevant text, its actual value
    and its attribute in boolean field i.e. "from", "to", "via", "normal".
    This class uses TextDetector to detect the entity values. It also has model integrated to it that can be used to
    extract relevant text from the text

    Attributes:
        text: string to extract entities from
        entity_name: string by which the detected city entities would be replaced with on calling detect_entity()
        tagged_text: string with city entities replaced with tag defined by entity_name
        text_entity: list to store detected entities from the text
        processed_text: string with detected time entities removed
        tag: entity_name prepended and appended with '__'
    """

    def __init__(self, entity_name):
        """
        Initializes a CityDetector object with given entity_name

        Args:
            entity_name: A string by which the detected substrings that correspond to text entities would be replaced
                         with on calling detect_entity()
        """

        self.entity_name = entity_name
        self.text = ''
        self.bot_message = ''
        self.tagged_text = ''
        self.processed_text = ''
        self.city = []
        self.text_detection_object = TextDetector(entity_name=entity_name)
        self.tag = '__' + self.entity_name + '__'

    def detect_entity(self, text):
        """Detects city in the text string

        Args:
            text: string to extract entities from
            run_model: Boolean True if model needs to run else False
        Returns:
            A tuple of two lists with first list containing the detected city and second list containing their
            corresponding substrings in the given text.

            For example:

                (['Mumbai'], ['bombay'])

            Additionally this function assigns these lists to self.city and self.original_city_text attributes
            respectively.

        """
        self.text = ' ' + text + ' '
        self.text = self.text.lower()
        self.processed_text = self.text
        self.tagged_text = self.text
        city_data = self._detect_city()
        self.city = city_data
        return city_data

    def detect_city(self):
        """
        Takes a message and writtens the list of city present in the text
        :return: tuple (list of location , original text)
        """

    def _detect_city(self):
        """
        Detects "departure" and "arrival" from the object's text attribute

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected date, and second list containing corresponding original substrings in text

        """
        # print 'detection for default task'
        final_city_dict_list = []
        city_dict_list = self._detect_departure_arrival_city_prepositions()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        city_dict_list = self._detect_departure_arrival_city()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        city_dict_list = self._detect_arrival_departure_city()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        city_dict_list = self._detect_departure_city()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        city_dict_list = self._detect_arrival_city()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        city_dict_list = self._detect_any_city()
        final_city_dict_list.extend(city_dict_list)
        self._update_processed_text(city_dict_list)

        return final_city_dict_list

    def _detect_city_format(self):
        """

        """
        return self._city_dict_from_text(text=self.processed_text, normal_property=True)

    def _detect_departure_arrival_city(self):
        """
        Finds <any text><space(s)><'-' or 'to' or '2'><space(s)><any text> in the given text.
        It  splits the text into two parts on '-' or 'to' or '2'
        and detects the departure city in the first (left) part and detects arrival city in the second (right) part

        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        patterns = re.findall(r'\s(([A-Za-z]+)\s*(\-|to|2|and)\s*([A-Za-z\s]+))\.?\b', self.processed_text.lower())
        for pattern in patterns:

            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[1], from_property=True)
            )

            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[3], to_property=True)
            )

        return city_dict_list

    def _detect_departure_arrival_city_prepositions(self):
        """
        Finds <preposition><any text><space(s)><'-' or 'to' or '2' or preposition><space(s)><any text> in the given
        text.
        It  splits the text into two parts on '-' or 'to' or '2'
        and detects the departure city in the first (left) part and detects arrival city in the second (right) part

        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        patterns = re.findall(
            r'\s((?:from|frm|departing|depart|leaving|leave)\s*([A-Za-z]+)\s*(?:and|to|2|for|fr|arriving|arrive|reaching|reach|rch)\s*([A-Za-z]+))\.?\b',
            self.processed_text.lower())

        for pattern in patterns:
            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[1], from_property=True)
            )

            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[2], to_property=True)
            )

        return city_dict_list

    def _detect_arrival_departure_city(self):
        """
        Finds <preposition><any text><space(s)><'-' or 'to' or '2' or preposition><space(s)><any text> in the given
        text.
        It  splits the text into two parts on '-' or 'to' or '2'
        and detects the arrival city in the first (left) part and detects departure city in the second (right) part

        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        patterns = re.findall(
            r'\s((?:and|to|2|for|fr|arriving|arrive|reaching|reach|rch)\s*([A-Za-z]+)\s*(?:from|frm|departing|depart|leaving|leave)\s*([A-Za-z]+))\.?\b',
            self.processed_text.lower())

        for pattern in patterns:
            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[2], from_property=True)
            )

            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[1], to_property=True)
            )

        return city_dict_list

    def _detect_departure_city(self):
        """
        Finds departure type cities in the given text by matching few keywords like 'from', 'departing',
        'leaving', 'departure city', 'departing', 'going to' . It detects dates in the part of text right to these
        keywords.

        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        patterns = re.findall(
            r'\s((from|frm|departing|depart|leaving|leave|origin city\:|departure city\:|going to)\s*([A-Za-z]+))\.?\s',
            self.processed_text.lower())

        for pattern in patterns:
            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[2], from_property=True)
            )

        return city_dict_list

    def _detect_arrival_city(self):
        """
        Finds return type dates in the given text by matching few keywords like 'arriving', 'arrive',
        'reaching', 'reach', 'destination city:' . It detects city in the part of text right
        to these keywords.

        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        patterns = re.findall(
            r'\s((to|2|for|fr|arriving|arrive|reaching|reach|rch|destination city\:|arrival city\:)\s*([A-Za-z]+))\.?\s',
            self.processed_text.lower())

        for pattern in patterns:
            city_dict_list.extend(
                self._city_dict_from_text(text=pattern[2], to_property=True)
            )

        return city_dict_list

    def _detect_any_city(self):
        """
        This function makes use of bot_message. In a chatbot user might just enter city name based on the
        previous question asked by the bot. So, if the previous question asked by the bot contains words like
        departure city, origin city, origin and if the current message contains city then we assign the
        detected city as departure_city. if the previous message contains words like arrival city, destination city,
        flying to in the bots message and the current message contains the city then we assign the detected city as
        arrival city


        Args:
            city_list: Optional, list to store dictionaries of detected cities
            original_list: Optional, list to store corresponding original substrings of text which were detected as
                            departure and arrival type city entities

        Returns:
            Tuple containing two lists, first containing dictionaries, each containing 'departure_city'
            and 'arrival_city' keys and dictionaries returned form TextDetector as their values,
            for each detected city, and second list containing corresponding original substrings in text
        """
        city_dict_list = []
        departure_city_flag = False
        arrival_city_flag = False
        if self.bot_message:
            departure_regexp = re.compile(
                r'departure city|origin city|origin|traveling from|leaving from|flying from|travelling from')
            arrival_regexp = re.compile(
                r'traveling to|travelling to|arrival city|arrival|destination city|destination|leaving to|flying to')
            if departure_regexp.search(self.bot_message) is not None:
                departure_city_flag = True
            elif arrival_regexp.search(self.bot_message) is not None:
                arrival_city_flag = True

        patterns = re.findall(r'\s((.+))\.?\b', self.processed_text.lower())

        for pattern in patterns:
            pattern = list(pattern)
            city_dict_list = self._city_dict_from_text(text=pattern[1])
            if city_dict_list:
                if len(city_dict_list) > 1:
                    city_dict_list[0][detector_constant.CITY_FROM_PROPERTY] = True
                    city_dict_list[-1][detector_constant.CITY_TO_PROPERTY] = True
                else:
                    if departure_city_flag:
                        city_dict_list[0][detector_constant.CITY_FROM_PROPERTY] = True
                    elif arrival_city_flag:
                        city_dict_list[0][detector_constant.CITY_TO_PROPERTY] = True
                    else:
                        city_dict_list[0][detector_constant.CITY_NORMAL_PROPERTY] = True
        return city_dict_list

    def _city_dict_from_text(self, text, from_property=False, to_property=False, via_property=False,
                             normal_property=False, detection_method=FROM_MESSAGE):
        """

        :param text:
        :return:
        """
        city_dict_list = []
        city_list, original_list = self._city_value(text=text)
        index = 0
        for city in city_list:
            city_dict_list.append(
                {
                    detector_constant.CITY_VALUE: city,
                    detector_constant.ORIGINAL_CITY_TEXT: original_list[index],
                    detector_constant.CITY_FROM_PROPERTY: from_property,
                    detector_constant.CITY_TO_PROPERTY: to_property,
                    detector_constant.CITY_VIA_PROPERTY: via_property,
                    detector_constant.CITY_NORMAL_PROPERTY: normal_property,
                    detector_constant.CITY_DETECTION_METHOD: detection_method
                }
            )
            index += 1
        return city_dict_list

    def _city_value(self, text):
        """
        Detects city from text by running TextDetection class.

        Args:
            text: message to process
        Returns:
            A tuple of two lists with first list containing the detected cities and second list containing their
            corresponding substrings in the given text. For example:

            For example:

                (['Mumbai'], ['bombay'])
        """
        city_list, original_list = self.text_detection_object.detect_entity(text)
        return city_list, original_list

    def _update_processed_text(self, city_dict_list):
        """
        Replaces detected cities with tag generated from entity_name used to initialize the object with

        A final string with all cities replaced will be stored in object's tagged_text attribute
        A string with all cities removed will be stored in object's processed_text attribute

        Args:
            original_city_strings: list of substrings of original text to be replaced with tag created from entity_name
        """
        for city_dict in city_dict_list:
            self.tagged_text = self.tagged_text.replace(city_dict[detector_constant.ORIGINAL_CITY_TEXT], self.tag)
            self.processed_text = self.processed_text.replace(city_dict[detector_constant.ORIGINAL_CITY_TEXT], '')

    def set_bot_message(self, bot_message):
        """
        Sets the object's bot_message attribute

        Args:
            bot_message: string
        """

        self.bot_message = bot_message

    def convert_dict_in_tuple(self, entity_dict_list):
        """

        :param entity_dict_list:
        :return:
        """
        entity_list, original_list, detection_list = [], [], []
        for entity_dict in entity_dict_list:
            entity_list.append(
                {
                    detector_constant.CITY_VALUE: entity_dict[detector_constant.CITY_VALUE],
                    detector_constant.CITY_FROM_PROPERTY: entity_dict[detector_constant.CITY_FROM_PROPERTY],
                    detector_constant.CITY_TO_PROPERTY: entity_dict[detector_constant.CITY_TO_PROPERTY],
                    detector_constant.CITY_VIA_PROPERTY: entity_dict[detector_constant.CITY_VIA_PROPERTY],
                    detector_constant.CITY_NORMAL_PROPERTY: entity_dict[detector_constant.CITY_NORMAL_PROPERTY],

                }
            )
            original_list.append(entity_dict[detector_constant.ORIGINAL_CITY_TEXT])
            detection_list.append(entity_dict[detector_constant.CITY_DETECTION_METHOD])
        return entity_list, original_list, detection_list
