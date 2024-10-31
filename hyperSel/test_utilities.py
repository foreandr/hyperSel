try:
    from . import soup_utilities
    from . import spider_universal
    from . import ui_utilities
    
except:
    import soup_utilities
    import spider_universal
    import ui_utilities

import json

# Example user-provided field configurations
def test():
    # Example URLs (can be more dynamic in a real-world scenario)
    list_of_urls = [
        "https://podcasts.apple.com/us/podcast/lex-fridman-podcast/id1434243584",
        "https://podcasts.apple.com/us/podcast/modern-wisdom/id1347973549",
        "https://podcasts.apple.com/us/podcast/the-tim-ferriss-show/id863897795",

    ]
    
    # USER-DEFINED FIELD CONFIGURATIONS
    
    root_config = spider_universal.create_field_config(
        name="root_section",
        function=soup_utilities.get_full_soup_by_tag_and_class,
        tag="li",
        selector_name="svelte-8rlk6b",
        single=False
    )
    
    title_config = spider_universal.create_field_config(
        name="title",
        function=soup_utilities.get_text_by_tag_and_class,
        tag="span",
        selector_name="episode-details__title-text"
    )

    description_config = spider_universal.create_field_config(
        name="description",
        function=soup_utilities.get_text_by_tag_and_class,
        tag="span",
        selector_name="multiline-clamp__text svelte-73d2pa",
        single=False,
        index=1
    )

    url_config = spider_universal.create_field_config(
        name="url",
        function=soup_utilities.get_href_by_tag_and_class,
        tag="a",
        selector_name="link-action svelte-1wtdvjb",
        needed=True
    )

    field_configs = {**root_config, **title_config, **description_config, **url_config}
    
    # Recursion regex pattern
    recursion_url_regex = r'https:\/\/podcasts\.apple\.com\/[a-z]{2}\/podcast\/[a-zA-Z\-]+\/id\d+'

    # Call the crawl function, passing the user-defined fields and options
    spider_universal.crawl(
        list_of_urls=list_of_urls,
        field_configs=field_configs,
        recursion_url_regex=recursion_url_regex,
        max_recursions=3,
        max_time=30,
        site_time_delay=8,
        headless=False,
    )

def test2():
    # Load data from demo_data.json
    with open('./demo_data.json', 'r') as file:
        data_entries = json.load(file)

        app = ui_utilities.App()
        app.mainloop()
    pass

# Run the app
if __name__ == "__main__":
    test2()
    