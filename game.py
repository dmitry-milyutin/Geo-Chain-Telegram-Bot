import geonamescache

gc = geonamescache.GeonamesCache()

def city_info(city):
    found_city = gc.search_cities(city, contains_search=False)
    latitude = found_city[0]["latitude"]
    longitude = found_city[0]["longitude"]
    population = found_city[0]["population"]
    countrycode = found_city[0]["countrycode"]
    return latitude, longitude, population, countrycode

def validate_city(city, cities):
    if len(cities) > 0:
        last_letter = cities[-1][-1]
        if city[0].lower() != last_letter.lower():
            return "Your city has to start with the last letter of mine, enter another city"
    if not len(gc.search_cities(city, contains_search=False)):
        return "I've never heard of your city, enter another one"
    elif city in cities:
        return "Pick a new city, that one was already named"

def get_population(city):
    return int(city['population'])

def find_city(letter, seen):
    cities = list(gc.get_cities().values())
    cities.sort(key=get_population, reverse=True)
    for city in cities:
        name = city['name']
        if name.lower().startswith(letter.lower()) and name not in seen:
            return name
    return None