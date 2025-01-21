import sqlite3
import json
from datetime import datetime
from datetime import datetime, timedelta
import config
import log
file_path = "./logs/data.json"

# Function to create the table
def create_table():
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_uid TEXT UNIQUE,
            job_title TEXT,
            job_link TEXT,
            published_date TEXT,
            location TEXT,
            payment_verified TEXT,
            rating TEXT,
            proposals TEXT,
            job_description TEXT,
            price REAL,
            original_scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recent_scrape_time TIMESTAMP,
            extra_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_or_update_job(job_data):
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()

    # Predefined columns in the database schema
    predefined_columns = {
        "job_uid", "job_title", "job_link", "published_date", "location",
        "payment_verified", "rating", "proposals", "job_description",
        "price", "original_scrape_time", "recent_scrape_time"
    }

    # Separate predefined fields and extra fields
    predefined_data = {k: v for k, v in job_data.items() if k in predefined_columns}
    extra_data = {k: v for k, v in job_data.items() if k not in predefined_columns}
    extra_data_json = json.dumps(extra_data) if extra_data else None

    # Ensure timestamps for scrape times
    predefined_data["recent_scrape_time"] = predefined_data.get(
        "recent_scrape_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    try:
        # Attempt to insert a new job
        cursor.execute('''
            INSERT INTO jobs (
                job_uid, job_title, job_link, published_date, location, 
                payment_verified, rating, proposals, job_description, 
                price, recent_scrape_time, extra_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            predefined_data.get("job_uid"),
            predefined_data.get("job_title"),
            predefined_data.get("job_link"),
            predefined_data.get("published_date"),
            predefined_data.get("location"),
            predefined_data.get("payment_verified"),
            predefined_data.get("rating"),
            predefined_data.get("proposals"),
            predefined_data.get("job_description"),
            float(predefined_data.get("price", 0.0)),
            predefined_data.get("recent_scrape_time"),
            extra_data_json
        ))
    except sqlite3.IntegrityError:
        # Update recent_scrape_time and extra_data if the job_uid already exists
        cursor.execute('''
            UPDATE jobs
            SET recent_scrape_time = ?, extra_data = ?
            WHERE job_uid = ?
        ''', (
            predefined_data.get("recent_scrape_time"),
            extra_data_json,
            predefined_data.get("job_uid")
        ))

    conn.commit()
    conn.close()


# Function to insert multiple jobs with extra fields handling
def insert_many_jobs(job_list):
    
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()

    predefined_columns = {
        "job_uid", "job_title", "job_link", "published_date", "location",
        "payment_verified", "rating", "proposals", "job_description",
        "price", "original_scrape_time", "recent_scrape_time"
    }

    for job_data in job_list:
        # Separate predefined fields and extra fields
        predefined_data = {k: v for k, v in job_data.items() if k in predefined_columns}
        extra_data = {k: v for k, v in job_data.items() if k not in predefined_columns}
        extra_data_json = json.dumps(extra_data) if extra_data else None

        # Ensure timestamps for scrape times
        predefined_data["recent_scrape_time"] = predefined_data.get(
            "recent_scrape_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        try:
            # Attempt to insert a new job
            cursor.execute('''
                INSERT INTO jobs (
                    job_uid, job_title, job_link, published_date, location, 
                    payment_verified, rating, proposals, job_description, 
                    price, recent_scrape_time, extra_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                predefined_data.get("job_uid"),
                predefined_data.get("job_title"),
                predefined_data.get("job_link"),
                predefined_data.get("published_date"),
                predefined_data.get("location"),
                predefined_data.get("payment_verified"),
                predefined_data.get("rating"),
                predefined_data.get("proposals"),
                predefined_data.get("job_description"),
                float(predefined_data.get("price", 0.0)),
                predefined_data.get("recent_scrape_time"),
                extra_data_json
            ))
        except sqlite3.IntegrityError:
            # Update recent_scrape_time and extra_data if the job_uid already exists
            cursor.execute('''
                UPDATE jobs
                SET recent_scrape_time = ?, extra_data = ?
                WHERE job_uid = ?
            ''', (
                predefined_data.get("recent_scrape_time"),
                extra_data_json,
                predefined_data.get("job_uid")
            ))

    conn.commit()
    conn.close()
    print("total:", count_entries())


# Function to delete all jobs from the table
def delete_all_jobs():
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs')
    conn.commit()
    conn.close()


# Function to count the number of entries
def count_entries():
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM jobs')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Function to load JSON data from a file and insert it into the database
def load_data_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load the JSON data into a Python object
    insert_many_jobs(data)  # Insert all data into the database

def add_current_data():
    

    file_path = "./logs/data.json"

    # Create the table
    create_table()

    # Load data from file and insert it into the database
    load_data_from_file(file_path)

    # Print the number of entries after insertion
    conn = sqlite3.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM jobs')
    print("Total entries:", cursor.fetchone()[0])
    conn.close()

def search_jobs(include_words, exclude_words, days_ago=None):
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT * FROM jobs WHERE 1=1
    '''
    params = []

    # Include words in title or description (case-insensitive)
    if include_words:
        include_query = " AND (" + " OR ".join(
            ["LOWER(job_title) LIKE ? OR LOWER(job_description) LIKE ?" for _ in include_words]
        ) + ")"
        query += include_query
        for word in include_words:
            params.extend([f"%{word.lower()}%", f"%{word.lower()}%"])

    # Exclude words from title or description (case-insensitive)
    if exclude_words:
        exclude_query = " AND " + " AND ".join(
            ["LOWER(job_title) NOT LIKE ? AND LOWER(job_description) NOT LIKE ?" for _ in exclude_words]
        )
        query += exclude_query
        for word in exclude_words:
            params.extend([f"%{word.lower()}%", f"%{word.lower()}%"])

    # Filter by original_scrape_time within the last N days
    if days_ago is not None:
        date_threshold = datetime.now() - timedelta(days=days_ago)
        query += " AND original_scrape_time >= ?"
        params.append(date_threshold.strftime('%Y-%m-%d %H:%M:%S'))

    # Execute query
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results

def use_search():
    
    # Search example
    include_words = ["kijiji"]
    exclude_words = []
    days_ago = 7100

    # Perform the search
    results = search_jobs(include_words, exclude_words, days_ago)

    # Print results
    print(f"Found {len(results)} jobs:")
    for job in results:
        log.log_function(job)
        # print(job)

def get_website_frequency_from_content():
    
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()

    # Expanded websites list
    websites = [
        "kijiji", "zillow", "craigslist", "facebook", "ebay", "cars", "real estate",
        "autotrader", "carvana", "truecar", "carmax", "carsdirect",
        "vroom", "bringatrailer", "hemmings", "copart", "manheim",
        "autotempest", "classiccars", "ebay motors", "facebook marketplace",
        "trulia",
        "forrent", "hotpads", "loopnet", "propertyfinder", "airbnb", "vrbo",
        "padmapper", "renthop", "remax", "century21", "bhgre", "sothebysrealty",
        "mls", "rightmove", "zoopla", "onTheMarket",
        "movoto", "coldwellbanker", "hudhomesusa",
        "offerpad", "opendoor", "divvyhomes", "homesnap", "rocketHomes", "point2homes",
        "luxuryrealestate", "propertyguru", "liv.rent", "apartmentsguide",
        "realestateview", "rentcafe", "abodo", "roomster", "spareRoom", "zumper",
        "autobytel", "edmunds", "motortrend", "drivetime", "autolist", "autoNation",
        "beepi", "carbrain", "instamotor", "ridescout", "carsforsale",
        "dealertrack", "carstory",  "peddle", "getaround", "turo",
        "hertz", "sixt", "avis",
    ]

    # Query to fetch titles and descriptions
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT job_title, job_description FROM jobs')
        jobs = cursor.fetchall()

    # Combine and search for website mentions
    frequency_dict = {website: 0 for website in websites}
    for job_title, job_description in jobs:
        content = f"{job_title or ''} {job_description or ''}".lower()
        for website in websites:
            if website in content:
                frequency_dict[website] += 1

    min_occurances =3
    frequency_dict = {k: v for k, v in frequency_dict.items() if v > min_occurances}

    # Sort websites by frequency
    sorted_frequency = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)

    return sorted_frequency

if __name__ == "__main__":
    use_search()
    exit()


    print("total:", count_entries())


