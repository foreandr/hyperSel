import re

def get_href_by_tag_and_class(soup, tag, selector_name, single=True, index=None, **kwargs):
    """
    Function to extract the href attribute from an <a> tag (or any tag) with a specified class.
    """
    try:
        if single:
            element = soup.find(tag, class_=selector_name)
            if element and element.has_attr('href'):
                return element['href']
            return None
        else:
            elements = soup.find_all(tag, class_=selector_name)
            hrefs = [element['href'] for element in elements if element.has_attr('href')]
            
            if index is not None and 0 <= index < len(hrefs):
                return hrefs[index]
            elif index is None:
                return hrefs
            else:
                return None
    except Exception as e:
        return None

def get_full_soup_by_tag_and_class(soup, tag, selector_name, single=True, **kwargs):

    try:
        if single:
            element = soup.find(tag, class_=selector_name)
            if element:
                return element
            return None
        else:
            elements = soup.find_all(tag, class_=selector_name)
            if elements:
                return elements
            return None
    except Exception as e:
        return None

def get_text_by_tag_and_class(soup, tag, selector_name, single=True, index=None, regex_pattern=None):

    try:
        if single:
            element = soup.find(tag, class_=selector_name)
            if element:
                text = element.text
                if regex_pattern:
                    cleaned_text = re.sub(regex_pattern, '', text)
                    try:
                        return float(cleaned_text)
                    except ValueError:
                        return None
                return text
            return None
        else:
            elements = soup.find_all(tag, class_=selector_name)
            results = []
            for element in elements:
                text = element.text
                if regex_pattern:
                    cleaned_text = re.sub(regex_pattern, '', text)
                    try:
                        results.append(float(cleaned_text))
                    except ValueError:
                        results.append(None)
                else:
                    results.append(text)
            if index is not None and 0 <= index < len(results):
                return results[index]
            elif index is None:
                return results
            else:
                return None
    except Exception as e:
        return None

def get_text_by_id(soup, tag=None, id_name=None, single=True, index=None, regex_pattern=None, **kwargs):
    try:
        if single:
            element = soup.find(tag, {"id": id_name}) if tag else soup.find({"id": id_name})
            if element:
                text = element.text
                if regex_pattern:
                    match = re.search(regex_pattern, text)
                    if match:
                        return match.group(1)
                return text
            return None
        else:
            elements = soup.find_all(tag, {"id": id_name}) if tag else soup.find_all({"id": id_name})
            results = []
            for element in elements:
                text = element.text
                if regex_pattern:
                    match = re.search(regex_pattern, text)
                    if match:
                        results.append(match.group(1))
                else:
                    results.append(text)
            if index is not None and 0 <= index < len(results):
                return results[index]
            elif index is None:
                return results
            else:
                return None
    except Exception as e:
        return None
    
def get_regex_items_from_soup(soup, single=True, index=None, regex_pattern=None, **kwargs):
    try:
        text = str(soup)
        if regex_pattern:
            matches = re.findall(regex_pattern, text)
            if single:
                return matches[0] if matches else None
            else:
                if index is not None and 0 <= index < len(matches):
                    return matches[index]
                return matches if matches else None
        return None
    except Exception as e:
        return None
