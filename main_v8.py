import json
import requests
import folium
from geopy import distance
from geopy.distance import lonlat
from dotenv import load_dotenv
import os


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def main():
    load_dotenv()
    apikey = os.getenv("API_KEY_YANDEX")

    point = input("Где вы находитесь? ")
    coord_user = fetch_coordinates(apikey, point)

    with open("coffee.json", "r", encoding="CP1251") as points:
        coffee_points = points.read()

    file_content = json.loads(coffee_points)

    coord_for_dist = lonlat(*coord_user)
    cafe_list = []
    for cafe in file_content:
        cafe_dictionary = {}

        cafe_dictionary["title"] = cafe["Name"]
        coord_cafe = cafe["Latitude_WGS84"], cafe["Longitude_WGS84"]

        cafe_dictionary["distance"] = distance.distance(coord_for_dist, coord_cafe).km
        cafe_dictionary["latitude"] = cafe["Latitude_WGS84"]
        cafe_dictionary["longitude"] = cafe["Longitude_WGS84"]

        cafe_list.append(cafe_dictionary)

    def get_cafe_distance(distance):
        return distance["distance"]

    sorted_cafe_list = sorted(cafe_list, key=get_cafe_distance)
    five_the_nearest_cafes = sorted_cafe_list[:5]

    coord_lon_user, coord_lat_user = coord_user

    points_map = folium.Map([coord_lat_user, coord_lon_user], zoom_start=12)

    for cafe_point in five_the_nearest_cafes:
        folium.Marker(
            location=[cafe_point["latitude"], cafe_point["longitude"]],
            tooltip="Нажми на меня!",
            popup=cafe_point["title"],
            icon=folium.Icon(icon="cloud")
            ).add_to(points_map)

    points_map.save("index.html")


if __name__ == "__main__":
    main()
