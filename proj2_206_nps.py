## proj_nps.py
## Skeleton for Project 2, Winter 2018
## ~~~ modify this file, but don't rename it ~~~
import requests
from bs4 import BeautifulSoup
import json
from requests_oauthlib import OAuth1
import secrets

# Gets whole website for national parks
url = 'https://www.nps.gov/index.htm'
page_text = requests.get(url)
page_soup = BeautifulSoup(page_text.text, 'html.parser')

# Base setup and authorization for OAuth
consumer_key = secrets.twitter_api_key
consumer_secret = secrets.twitter_api_secret
access_token = secrets.twitter_access_token
access_secret = secrets.twitter_access_token_secret

url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
requests.get(url, auth=auth)

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NationalSite:
    def __init__(self, p_type='', name='', desc='', street='', city='', state='', p_zip='', url=None):
        self.type = str(p_type).replace('\n', '')
        self.name = str(name).replace('\n', '')
        self.description = str(desc).replace('\n', '')
        self.address_street = str(street).replace('\n', '')
        self.address_city = str(city).replace('\n', '')
        self.state = str(state).replace('\n', '')
        self.address_zip = str(p_zip).replace(' ', '')
        self.url = str(url).replace('\n', '')

    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.state, self.address_zip)

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name):
        self.name = str(name)

    def __str__(self):
        return self.name

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class Tweet:
    def __init__(self, tweet_dict_from_json):
        self.is_retweet = tweet_dict_from_json['retweeted']
        self.user_name = tweet_dict_from_json['user']['screen_name']
        self.text = tweet_dict_from_json['text']
        self.date = str(tweet_dict_from_json['created_at'])
        self.id = tweet_dict_from_json['id_str']
        self.num_retweets = retweets = tweet_dict_from_json['retweet_count']
        self.num_favorites = favorites = tweet_dict_from_json['favorite_count']
        self.popularity_score = self.num_retweets * 2 + self.num_favorites * 3

    def __str__(self):
        return '@{}:{}\n[Retweeted {} times]\n[Favorited {} times]\n[Popularity {}]\n[Tweeted on {} | ID:{}]'.format(self.user_name, self.text, str(self.num_retweets), str(self.num_favorites), str(self.popularity_score), self.date, self.id)

def cacheOpen(kind):

    if kind == 'state':
        CACHE_FNAME = 'stateCache.json'
    elif kind == 'park':
        CACHE_FNAME = 'parksCache.json'
    elif kind == 'nearby_place':
        CACHE_FNAME = 'nearbyCache.json'
    elif kind == 'tweet':
        CACHE_FNAME = 'tweetCache.json'

    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    return CACHE_DICTION

def cacheWrite(kind, cache_dict):

    if kind == 'state':
        CACHE_FNAME = 'stateCache.json'
    elif kind == 'park':
        CACHE_FNAME = 'parksCache.json'
    elif kind == 'nearby_place':
        CACHE_FNAME = 'nearbyCache.json'
    elif kind == 'tweet':
        CACHE_FNAME = 'tweetCache.json'

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    sites = []
    fullUrl = 'https://www.nps.gov/state/' + state_abbr + '/index.htm'
    state_cache = cacheOpen('state')

    if fullUrl in state_cache:
        state_page = state_cache[fullUrl]
    else:
        baseurl = 'https://www.nps.gov'
        state_abbr = state_abbr.lower()
        dropdown = page_soup.find(class_ = 'dropdown-menu')
        states = dropdown.find_all('li')

        for state in states:
            if state_abbr in state.a['href']:
                url = baseurl + state.a['href']

        state_resp = requests.get(fullUrl)
        state_page = state_resp.text
        state_cache[fullUrl] = state_page
        cacheWrite('state', state_cache)
    state_page_soup = BeautifulSoup(state_page, 'html.parser')
    all_state_info = state_page_soup.find(id = 'list_parks')

    for park in all_state_info:
        p_name = park.find('h3')
        try:
            park_name = p_name.string
            p_type = park.find('h2')
            park_type = p_type.string
            p_desc = park.find('p')
            park_desc = p_desc.string
            more_info = park.find_all('a')
            for link in more_info:
                if 'basicinfo' in link['href']:
                    park_link = link['href']
                    break

            park_cache = cacheOpen('park')
            if park_link in park_cache:
                park_page = park_cache[park_link]
            else:
                park_resp = requests.get(park_link)
                park_page = park_resp.text
                park_cache[park_link] = park_page
                cacheWrite('park', park_cache)
            park_page_soup = BeautifulSoup(park_page, 'html.parser')

            try:
                park_street_general = park_page_soup.find(itemprop = "streetAddress")
                park_street = park_street_general.text
            except:
                park_street_general = park_page_soup.find(itemprop = "postOfficeBoxNumber")
                park_street = "PO Box " + park_street_general.text
            park_city_general = park_page_soup.find(itemprop = "addressLocality")
            park_city = park_city_general.string
            park_state_general = park_page_soup.find(itemprop = "addressRegion")
            park_state = park_state_general.string
            park_zip_general = park_page_soup.find(itemprop = "postalCode")
            park_zip = park_zip_general.string

            new_park = NationalSite(park_type, park_name, park_desc, park_street, park_city, park_state, park_zip, park_link)
            sites.append(new_park)
        except:
            pass

    return sites


## Must return the list of NearbyPlaces for the specified NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(site_object):
    google_api_key = secrets.google_places_key
    search_query = str(site_object.name) + ' ' + str(site_object.type)

    nearby_place_cache = cacheOpen('nearby_place')
    firstFullUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?' + '&' + search_query.replace(" ", "+") + '&' + google_api_key
    if firstFullUrl in nearby_place_cache:
        lat_lng_response = nearby_place_cache[firstFullUrl]
    else:
        lat_lng_response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?', params = {'query': search_query, 'key': google_api_key}).json()
        nearby_place_cache[firstFullUrl] = lat_lng_response
        cacheWrite('nearby_place', nearby_place_cache)

    if lat_lng_response['status'] == "ZERO_RESULTS":
        return []

    lat = lat_lng_response['results'][0]['geometry']['location']['lat']
    lng = lat_lng_response['results'][0]['geometry']['location']['lng']
    location = str(lat) + ',' + str(lng)

    nearby_place_cache = cacheOpen('nearby_place')
    secondFullUrl = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + '&' + location
    if secondFullUrl in nearby_place_cache:
        nearby_places_results = nearby_place_cache[secondFullUrl]
    else:
        nearby_places_results = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?', params = {'location': location, 'radius' : '10000', 'key': google_api_key}).json()
        nearby_place_cache[secondFullUrl] = nearby_places_results
        cacheWrite('nearby_place', nearby_place_cache)

    nearby_places = nearby_places_results['results']
    nearby_place_list = []
    for place in nearby_places:
        place_name = place['name']
        a_place = NearbyPlace(place_name)
        nearby_place_list.append(a_place)

    return nearby_place_list

## Must return the list of Tweets that mention the specified NationalSite
## param: a NationalSite object
## returns: a list of up to 10 Tweets, in descending order of "popularity"
def get_tweets_for_site(site_object):
    tweet_cache = cacheOpen('tweet')
    query = site_object.name + " " + site_object.type

    base_url = 'https://api.twitter.com/1.1/search/tweets.json?'
    full_url = base_url + '?' + query.replace(" ", "+")
    if full_url in tweet_cache:
        tweet_data = tweet_cache[full_url]
    else:
        params = {'q': query , "count": '50'}
        auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
        response = requests.get(base_url, params, auth = auth)
        tweet_data = json.loads(response.text)
        tweet_cache[full_url] = tweet_data
        cacheWrite('tweet', tweet_cache)

    tweets = tweet_data['statuses']
    tweet_objects = []
    for tweet in tweets:
        if "retweeted_status" not in tweet:
            if "RT @" not in tweet['text']:
                new_tweet = Tweet(tweet)
                tweet_objects.append(new_tweet)
                if len(tweet_objects) == 10:
                    break

    sorted_tweets = sorted(tweet_objects, key=lambda x: x.popularity_score, reverse=True)

    return sorted_tweets

commands_header = "List of commands:"
commands = "list <stateabbr>\n\tavailable anytime\n\tlists all National Sites in a state\n\tvalid inputs: a two-letter state abbreviation\nnearby <result_number>\n\tavailable only if there is an active result set\n\tlists all Places nearby a given result\n\tvalid inputs: an integer 1-len(result_set_size)\ntweets <result_number>\n\tavailable only if there is an active results set\n\tlists up to 10 most \"popular\" tweets that mention the\n\tselected Site\nexit\n\texits the program\nhelp\n\tlists available commands (these instructions)"
print()
print(commands_header)
print()
print(commands)

us_states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

exit = False
while exit == False:
    print()
    choice = input("Enter command or \'help\' for options: ")
    print()

    if choice == "help":
        print()
        print(commands_header)
        print()
        print(commands)

    elif choice.split()[0] == 'list':
        if len(choice.split()) != 2 or len(choice.split()[1]) != 2:
            print("Invalid syntax. Please try again. Type \'help\' for list of commands.")
        elif choice.split()[1].upper() not in us_states.keys():
            print("Error. Not a valid state abbreviation. Type \'help\' for list of commands.")
        else:
            counter = 1
            abbr = choice.split()[1]
            state = us_states[abbr.upper()]
            new_sites = get_sites_for_state(abbr.lower())
            print("National Sites in {}".format(state))
            print()
            for site in new_sites:
                print(str(counter), site)
                counter += 1
            print()

    elif choice.split()[0] == 'nearby':
        try:
            junk = int(choice.split()[1])
        except:
            print("Invalid syntax. Please enter result number as a number. Type \'help\' for list of commands.")
            continue
        if len(choice.split()) != 2:
            print("Invalid syntax. Please try again. Type \'help\' for list of commands.")
        else:
            counter = 1
            result_num = int(choice.split()[1])
            try:
                if int(choice.split()[1]) < 1 or int(choice.split()[1]) > len(new_sites):
                    print("Error. Please choose a number between 1 and {}.".format(len(new_sites)))
                else:
                    site = new_sites[result_num - 1]
                    nearby_sites = get_nearby_places_for_site(site)
                    site_name = site.name + " " + site.type
                    print("Places near {}".format(site_name))
                    print()
                    if (len(nearby_sites) == 0):
                        print("No nearby results, try another site.")
                    for nearby in nearby_sites:
                        print(str(counter), nearby)
                        counter += 1
                    print()
            except:
                print("Error. No active set to work with. Please create a set of sites using \"list <stateabbr>\".")

    elif choice.split()[0] == 'tweets':
        try:
            junk = int(choice.split()[1])
        except:
            print("Invalid syntax. Please enter result number as a number. Type \'help\' for list of commands.")
            continue
        if len(choice.split()) != 2:
            print("Invalid syntax. Please try again. Type \'help\' for list of commands.")
        else:
            divider = '-'*25
            result_num = int(choice.split()[1])
            try:
                if int(choice.split()[1]) < 1 or int(choice.split()[1]) > len(new_sites):
                    print("Error. Please choose a number between 1 and {}.".format(len(new_sites)))
                else:
                    site = new_sites[result_num - 1]
                    tweets = get_tweets_for_site(site)
                    if len(tweets) == 0:
                        print("No tweet results, try another site.")
                    for tweet in tweets:
                        print(tweet)
                        print(divider)

            except:
                print("Error. No active set to work with. Please create a set of sites using \"list <stateabbr>\".")

    elif choice == "exit":
        exit = True
        print("Bye!")

    else:
        print("Invalid command. Please try again. Type \'help\' for list of commands.")
