from proj2_206_nps import *
import unittest

class TestStateSearch(unittest.TestCase):

    def site_is_in_state_list(self, site_name, site_type, site_list):
        for s in site_list:
            if site_name == s.name and site_type == s.type:
                return True
        return False

    def get_site_from_list(self, site_name, site_list):
        for s in site_list:
            if site_name == s.name:
                return s
        return None

    def setUp(self):
        self.mi_site_list = get_sites_for_state('mi')
        self.az_site_list = get_sites_for_state('az')
        self.isle_royale = self.get_site_from_list('Isle Royale', self.mi_site_list)
        self.lake_mead = self.get_site_from_list('Lake Mead', self.az_site_list)

    def test_basic_search(self):
        self.assertEqual(len(self.mi_site_list), 7)
        self.assertEqual(len(self.az_site_list), 24)

        self.assertTrue(self.site_is_in_state_list('Isle Royale',
            'National Park', self.mi_site_list))
        self.assertFalse(self.site_is_in_state_list('Isle Royale',
            'National Park', self.az_site_list))

        self.assertTrue(self.site_is_in_state_list('Lake Mead',
            'National Recreation Area', self.az_site_list))
        self.assertFalse(self.site_is_in_state_list('Lake Mead',
            'National Recreation Area', self.mi_site_list))

    def test_addresses(self):
        self.assertEqual(self.isle_royale.address_street, '800 East Lakeshore Drive')
        self.assertEqual(self.isle_royale.address_city, 'Houghton')
        self.assertEqual(self.isle_royale.address_zip, '49931')

        self.assertEqual(self.lake_mead.address_street, '601 Nevada Way')
        self.assertEqual(self.lake_mead.address_city, 'Boulder City')
        self.assertEqual(self.lake_mead.address_zip, '89005')

    def test_str(self):
        self.assertEqual(str(self.lake_mead), "Lake Mead (National Recreation Area): 601 Nevada Way, Boulder City, NV 89005")
        self.assertEqual(str(self.isle_royale), "Isle Royale (National Park): 800 East Lakeshore Drive, Houghton, MI 49931")


class TestNearbySearch(unittest.TestCase):

    def place_is_in_places_list(self, place_name, places_list):
        for p in places_list:
            if place_name == p.name:
                return True
        return False

    def test_nearby_search(self):
        site1 = NationalSite('National Monument',
            'Sunset Crater Volcano', 'A volcano in a crater.')
        site2 = NationalSite('National Park',
            'Yellowstone', 'There is a big geyser there.')

        nearby_places1 = get_nearby_places_for_site(site1)
        nearby_places2 = get_nearby_places_for_site(site2)

        self.assertTrue(self.place_is_in_places_list('Cinder Lake Landfill', nearby_places1))
        self.assertTrue(self.place_is_in_places_list('Yellowstone General Store', nearby_places2))

class TestTweets(unittest.TestCase):

    def test_tweets_for_site(self):
        site1 = NationalSite('National Monument',
            'Sunset Crater Volcano', 'A volcano in a crater.')
        site2 = NationalSite('National Park',
            'Yellowstone', 'There is a big geyser there.')

        tweets1 = get_tweets_for_site(site1)
        self.assertTrue(len(tweets1) > 0 and len(tweets1) <= 10)

        tweets2 = get_tweets_for_site(site2)
        self.assertTrue(len(tweets2) > 0 and len(tweets2) <= 10)
        #self.assertEqual(len(tweets2), 10) # Old test

        self.assertTrue(tweets2[0].popularity_score >= tweets2[1].popularity_score)
        self.assertTrue(tweets2[3].popularity_score >= tweets2[7].popularity_score)

        tweet_string = str(tweets2[0]) # will call Tweet.__str__()
        self.assertTrue('@' in tweet_string)
        self.assertTrue('retweeted' in tweet_string)
        self.assertTrue('popularity' in tweet_string)


if __name__ == '__main__':
    #unittest.main()
    pass
