import graph
import util
import config
from collections import Counter
import time
import log

def print_children_metadata(node, G):
    """
    Print the metadata of all children of a given node in the graph.

    :param node: The node whose children’s metadata needs to be printed.
    :param G: The graph containing the nodes and their metadata.
    """
    if not G.has_node(node):
        print(f"Node '{node}' does not exist in the graph.")
        return

    print(f"Children metadata for node '{node}':")
    children = list(G.successors(node))
    if not children:
        print(f"Node '{node}' has no children.")
        return

    for child in children:
        metadata = G.nodes[child].get("metadata", {})
        print(f"Child: {child} [len:{len(str(metadata))}], Metadata: {metadata}")

def print_metadata(final_data, G):
    """
    Print the metadata for nodes whose metadata length (as a string) matches the 'values' list.

    :param final_data: The filtered data, a list of dictionaries.
    :param G: The graph containing nodes and metadata.
    """
    for entry in final_data:
        for node, values in entry.items():
            print(f"Node: {node}, Values (lengths to match): {values}")
            print("Metadata for matching nodes:")
            for child in G.successors(node):  # Iterate over all child nodes of `node`
                metadata = G.nodes[child].get("metadata", {})
                metadata_length = len(str(metadata))
                if metadata_length in values:  # Check if the metadata length matches any value
                    print(f"  Child: {child}, Metadata: {metadata}")
                    log.log_function()
            print("-" * 40)  # Separator for readability

def calculate_median(values):
    """Calculate the median of a list."""
    n = len(values)
    if n == 0:
        return 0  # Avoid division by zero
    sorted_values = sorted(values)
    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]
    else:
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2


def calculate_standard_deviation(values, mean):
    """Calculate the standard deviation of a list."""
    if len(values) == 0:
        return 0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def calculate_mode(values):
    """Calculate the mode of a list."""
    if not values:
        return 0
    counter = Counter(values)
    mode_data = counter.most_common(1)
    return mode_data[0][0] if mode_data else 0

def preclean_data(array_of_dicts, G, track_string="1976 BMW 2002"):
    """
    Pre-clean the data by removing values below min_chars or above max_chars.
    Also, filter out invalid metadata for each key and its child nodes in the graph G.

    :param array_of_dicts: The dataset to be cleaned.
    :param G: The graph containing nodes and metadata.
    :param track_string: A string to track and report when it gets filtered out.
    """
    def is_string_in_metadata(data, search_string):
        """Check if the string is present in the metadata of children with matching lengths."""
        for entry in data:
            for key, values in entry.items():
                for child in G.successors(key):
                    metadata = G.nodes[child].get("metadata", {})
                    metadata_length = len(str(metadata))
                    if metadata_length in values:  # Only check children with matching metadata lengths
                        if search_string in str(metadata):
                            return True
        return False

    # Start with the initial dataset
    current_data = array_of_dicts
    print(f"Initial data count: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' not found in initial metadata.")
        input("Press Enter to continue...")

    # Criterion 0: Skip entries where the key's tag is in a specified list
    skip_tags = ["head", "body"]
    new_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            key_metadata = G.nodes[key].get("metadata", {})
            if key_metadata.get("tag") in skip_tags:
                continue
            cleaned_entry[key] = value
        if cleaned_entry:
            new_data.append(cleaned_entry)
    current_data = new_data
    print(f"After key tag filter: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' was filtered out after key tag filter.")
        input("Press Enter to continue...")

    # Criterion 1: Remove children with metadata length > max_chars
    new_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_children = []
            for child in G.successors(key):
                metadata = G.nodes[child].get("metadata", {})
                if len(str(metadata)) <= config.CHARS_MAXIMUM:
                    filtered_children.append(child)
            if filtered_children:
                cleaned_entry[key] = value
        if cleaned_entry:
            new_data.append(cleaned_entry)
    current_data = new_data
    print(f"After max_chars filter: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' was filtered out after max_chars filter.")
        input("Press Enter to continue...")

    # Criterion 2: Remove children with metadata length < min_chars
    new_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_children = []
            for child in G.successors(key):
                metadata = G.nodes[child].get("metadata", {})
                if len(str(metadata)) >= config.CHARS_MINIMUM:
                    filtered_children.append(child)
            if filtered_children:
                cleaned_entry[key] = value
        if cleaned_entry:
            new_data.append(cleaned_entry)
    current_data = new_data
    print(f"After min_chars filter: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' was filtered out after min_chars filter.")
        input("Press Enter to continue...")

    # Criterion 3: Remove children with tags 'script' or 'style'
    new_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_children = []
            for child in G.successors(key):
                metadata = G.nodes[child].get("metadata", {})
                if metadata.get("tag") not in ["script", "style", "link"]:
                    filtered_children.append(child)
            if filtered_children:
                cleaned_entry[key] = value
        if cleaned_entry:
            new_data.append(cleaned_entry)
    current_data = new_data
    print(f"After tag filter: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' was filtered out after tag filter.")
        input("Press Enter to continue...")

    # Criterion 4: Remove children with empty 'text'
    new_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_children = []
            for child in G.successors(key):
                metadata = G.nodes[child].get("metadata", {})
                if metadata.get("text") != []:
                    filtered_children.append(child)
            if filtered_children:
                cleaned_entry[key] = value
        if cleaned_entry:
            new_data.append(cleaned_entry)
    current_data = new_data
    print(f"After text filter: {len(current_data)}")
    if track_string and not is_string_in_metadata(current_data, track_string):
        print(f"'{track_string}' was filtered out after text filter.")
        input("Press Enter to continue...")

    # Criterion 5: Filter values step by step
    # Step 1: Filter values below CHARS_MINIMUM
    step1_data = []
    for i in current_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_values = []
            for x in value:
                if x >= config.CHARS_MINIMUM:
                    filtered_values.append(x)
            if filtered_values:
                cleaned_entry[key] = filtered_values
        if cleaned_entry:
            step1_data.append(cleaned_entry)

    print(f"After filtering values below CHARS_MINIMUM: {len(step1_data)}")
    if track_string and not is_string_in_metadata(step1_data, track_string):
        print(f"'{track_string}' was filtered out after values below CHARS_MINIMUM filter.")
        input("Press Enter to continue...")

    # Step 2: Filter values above CHARS_MAXIMUM
    step2_data = []
    for i in step1_data:
        cleaned_entry = {}
        for key, value in i.items():
            filtered_values = []
            for x in value:
                if x <= config.CHARS_MAXIMUM:
                    filtered_values.append(x)
            if filtered_values:
                cleaned_entry[key] = filtered_values
        if cleaned_entry:
            step2_data.append(cleaned_entry)
    print(f"After filtering values above CHARS_MAXIMUM: {len(step2_data)}")
    if track_string and not is_string_in_metadata(step2_data, track_string):
        print(f"'{track_string}' was filtered out after values above CHARS_MAXIMUM filter.")
        input("Press Enter to continue...")

    print_metadata(step2_data, G)

    # Step 3: Filter out entries with insufficient children
    final_data = []
    for i in step2_data:
        cleaned_entry = {}
        for key, value in i.items():
            if len(value) >= config.MIN_CHILDREN:
                cleaned_entry[key] = value
        if cleaned_entry:
            final_data.append(cleaned_entry)
            
    print(f"After filtering entries with insufficient children: {len(final_data)}")
    if track_string and not is_string_in_metadata(final_data, track_string):
        print(f"'{track_string}' was filtered out after insufficient children filter.")
        
        input("Press Enter to continue...")
        

    # exit()
    # At this point, `final_data` contains the result after all filtering steps.
    # print_metadata(final_data, G)


    #print(final_data)
    #node = list(final_data[0].keys())[0]
    #print_children_metadata(node, G)
    
    # Return the final cleaned data
    # input("--")
    return final_data

def get_matching_children(G, winner_key, winner_data):
    """
    Extracts the children of the winning node whose metadata lengths match the values in winner_data.

    Parameters:
    - G: The graph containing the nodes and metadata.
    - winner_key: The key of the winning node.
    - winner_data: The list of metadata lengths to match.

    Returns:
    - A list of dictionaries containing matching children and their metadata.
    """
    matching_children = []
    for child in G.successors(winner_key):
        child_metadata = G.nodes[child].get("metadata", {})
        child_metadata_length = len(str(child_metadata))

        if child_metadata.get("tag") in ["script", "style"]:  # Skip 'script' or 'style' tags
            # print(child_metadata)
            # exit()
            continue
        if child_metadata.get("text") == []:  # Skip if 'text' is empty
            continue

        # If the length of the metadata matches a value in the winner's data, add it
        if child_metadata_length in winner_data:
            matching_children.append({"child": child, "metadata": child_metadata})

    return matching_children

def flatten_matching_children(matching_children):
    """
    Flattens the metadata text of matching children into a list of lists.
    
    Parameters:
    - matching_children: List of dictionaries containing child nodes and their metadata.
    
    Returns:
    - A list of lists containing the flattened text data from the metadata.
    """
    flattened_data = []
    for child_info in matching_children:
        metadata = child_info.get("metadata", {})
        text_data = metadata.get("text", [])
        if text_data:  # Ensure there is text data to process
            flattened_data.append(text_data)
    return flattened_data

def child_arr_processor(G, array_of_dicts=[{}]):
    # Pre-clean the data
    cleaned_data = preclean_data(array_of_dicts, G) # , track_string='$7,399'
    input("---???")

    finalists_calculated = calc_best_score(cleaned_data)
    scored_finalists = score_finalists(finalists_calculated)
    winner_key = scored_finalists["winner"]
    winner_data = scored_finalists["data"]
    matching_children = get_matching_children(G, winner_key, winner_data)
    flattened_data = flatten_matching_children(matching_children)
    return winner_key, flattened_data

def score_finalists(finalists):
    print(finalists)
    """Score each finalist based on various criteria and return the overall winner with data."""
    # Define the criteria for scoring
    criteria = {
        "highest_mean": lambda x: x["mean"],
        "highest_median": lambda x: x["median"],
        "highest_mode": lambda x: x["mode"],
        "smallest_range_min_max": lambda x: x["range_min_max"],
        "lowest_standard_deviation": lambda x: x["std_dev"],
        "highest_min_value": lambda x: x["min"],  # Highest minimum value
        "longest_list": lambda x: len(x["data"]),  # Length of the list
    }

    # Initialize scores and raw criterion tracking
    scores = {key: {"score": 0, "criteria": [], "raw_scores": {}} for finalist in finalists for key in finalist if key.startswith("node_")}
    total_criteria = len(criteria)

    # Determine the winner for each criterion and track scores
    for criterion, getter in criteria.items():
        # Determine sorting order: reverse=True for "highest", reverse=False for "lowest"
        is_highest = "highest" in criterion or criterion == "longest_list"
        sorted_finalists = sorted(finalists, key=lambda x: getter(x), reverse=is_highest)
        for finalist in sorted_finalists:
            key = list(finalist.keys())[0]
            scores[key]["raw_scores"][criterion] = getter(finalist)  # Save raw score for this criterion

        # Determine the winner (highest rank for "highest", lowest rank for "lowest")
        winner_key = list(sorted_finalists[0].keys())[0]
        scores[winner_key]["score"] += 1  # Increment the score for the winner
        scores[winner_key]["criteria"].append(criterion)  # Track the criterion they won

    # Determine the overall winner (node with the most criteria wins)
    winner = max(scores.items(), key=lambda x: x[1]["score"])
    winner_key = winner[0]
    winner_data = next((finalist for finalist in finalists if winner_key in finalist), None)

    # Print detailed information about the winner
    '''
    print(f"Overall Winner: {winner_key} with {winner[1]['score']}/{total_criteria} points")
    print(f"  Wins: {', '.join(winner[1]['criteria'])}")
    print(f"  Raw Scores:")
    for criterion, raw_score in winner[1]["raw_scores"].items():
        print(f"    {criterion}: {round(raw_score, 2)}")
    print(f"  Data: {winner_data[winner_key]}")
    print("-" * 40)
    '''

    # Return the winner's key and their corresponding data
    return {"winner": winner_key, "data": winner_data[winner_key]}

def calc_best_score(finalists):
    """Process and display results for finalists."""
    if not finalists:
        print("NONE FIT, FUCK")
        return None

    # Add additional statistics to each finalist
    processed_finalists = []
    for finalist in finalists:
        for key, value in finalist.items():
            mean_value = sum(value) / len(value) if value else 0
            median_value = calculate_median(value)
            mode_value = calculate_mode(value)
            min_value = min(value) if value else 0
            max_value = max(value) if value else 0
            std_dev = calculate_standard_deviation(value, mean_value)
            range_min_max = max_value - min_value
            range_mean_median_mode = abs(mean_value - median_value) + abs(median_value - mode_value)

            # Add the processed finalist with the original data
            processed_finalists.append({
                key: value,
                "data": value,  # Preserve the original list
                "mean": mean_value,
                "median": median_value,
                "mode": mode_value,
                "min": min_value,
                "max": max_value,
                "std_dev": std_dev,
                "range_min_max": range_min_max,
                "range_mean_median_mode": range_mean_median_mode,
            })

    # Score the finalists
    return processed_finalists
    
def find_most_children_node(G):
    """
    Finds the node with the most children, ensuring the total average characters
    in its relevant data exceed a threshold and the number of children exceeds a minimum.
    Prints and returns the node ID and its children's metadata.
    """

    array_of_dicts = []

    for node in G.nodes:
        all_child_metadata_string_lengths = []
        for c in list(G.successors(node)):
            len_metadata = len(str(G.nodes[c]['metadata']))
            all_child_metadata_string_lengths.append(len_metadata)

        array_of_dicts.append({node:all_child_metadata_string_lengths})

    best_node, flattened_metadata = child_arr_processor(G, array_of_dicts)

    if best_node == None:
        print("LITERALLY NOTHING")
        return None, []
    input("-")
    return best_node, flattened_metadata

def main(soup, i):
    """
    Main function to build the graph and visualize it interactively.
    """
    G = graph.soup_to_graph(soup)

    # Use Pyvis interactive visualization
    graph.visualize_graph_pyvis(G)

    most_children_node, children_metadata = find_most_children_node(G)
    
    data = data_preprocessing(data=children_metadata)
    file = f"./logs/temp_data{i}.csv"
    util.write_to_csv(data, filename=file)

    # Example: Load the data back
    loaded_data = util.read_from_csv(file)
    for j in loaded_data:
        print(j)
        print('======================')

    print(F"FINISHED READING FROM CSV [{i}]")

def data_preprocessing(data, root_url=None):
    '''
    TODO: get rid of anomalies in this data, there is still noise
    url fixing
    '''
    final_data = []

    for i in data:
        # print(i)
        sub_data = []
        for j in i:
            if j in util.valid_html_tags:
                continue
            else:
                sub_data.append(j)
        final_data.append(sub_data)
        # print("---")
    
    #for i in final_data:
    #    print(i)

    return final_data



if __name__ == "__main__":
   
    '''OTHER SITES TO CHECK:
    # https://www.asiaautosales.ca/
    # https://www.autocango.com/
    # https://www.pickles.com.au/pickles-cars?srsltid=AfmBOooX8Gdm_DE31Ql2o2yc-KBgsYJeseKpD0xUwVoWWAfWVBndr4oo
    # https://www.blocket.se/bilar/sok?filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22BMW%22%5D%7D
    # https://www.kbb.com/
   
    '''

    urls = [
        #"https://www.cars.com/shopping/results/?stock_type=all&makes%5B%5D=bmw&models%5B%5D=bmw-128&maximum_distance=all&zip=48061",
        #"https://www.autotrader.ca/cars/?rcp=0&rcs=0&prx=100&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch&mdl=Accord&make=Honda&loc=N5V%204E1",
        #"https://www.kijiji.ca/b-peterborough/cars/k0l1700218?dc=true",
        #"https://www.edmunds.com/inventory/srp.html?make=honda&model=honda%7Ccivic",
        #"https://www.ebay.com/b/Ford-Cars-and-Trucks/6001/bn_24016471",
        #"https://londonon.craigslist.org/search/cta",
        #"https://www.truecar.com/used-cars-for-sale/listings/honda/",
        #"https://www.autotempest.com/results?make=honda&zip=N5V4E1&radius=500",
        # "https://www.autolist.com/listings#limit=20&make=Honda&page=1&radius=100",
        "https://www.carpages.ca/used-cars/search/?search_radius=250&province_code=on&city=peterborough&ll=44.302336,-78.364672",

        #"https://www.hemmings.com/classifieds/cars-for-sale",
        #"https://www.carsdirect.com/acura",
    ]




    
    ''''''
    urls = [
        # "https://www.carvana.com/cars/filters?cvnaid=eyJmaWx0ZXJzIjp7Im1ha2VzIjpbeyJuYW1lIjoiSG9uZGEiLCJwYXJlbnRNb2RlbHMiOlt7Im5hbWUiOiJDaXZpYyIsInRyaW1zIjpbXX1dLCJtb2RlbHMiOltdfV19fQ%3D%3D"
        "https://www.facebook.com/marketplace/107401009289940/cars/"
    ]
    import instance
    browser = instance.Browser(
                driver_choice="selenium", 
                headless=True, 
                use_tor=False,
                default_profile=False
        )  

    for i, url in enumerate(urls):
        try:
            browser.go_to_site( url) 
            time.sleep(2)
            browser.take_screenshot()
            input("934-1298243")
            exit()
            
            soup = browser.return_current_soup()
            log.log_function(soup)
            main(soup, i)
            input("---")

        except Exception as e:
            print(e)
            print(url)
            input("URL FAILED")
    
    soup = log.load_file_as_soup("./logs/log.txt")
    main(soup, i=1)