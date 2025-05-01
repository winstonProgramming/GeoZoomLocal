import geopandas
import folium
import os
from shapely.geometry import Point
import random
import re
import webbrowser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import subprocess
import datetime

world = geopandas.read_file('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson')

# creating directories
if not os.path.exists('question_maps_html'):
    os.makedirs('question_maps_html')
if not os.path.exists('question_maps_png'):
    os.makedirs('question_maps_png')


def create_question_maps():
    # writing longitude and latitude answers into js script
    def edit_script(long_answers, lat_answers):
        with open('script', 'r') as f:
            edited_script = f.read()
        with open('script.js', 'w', encoding='utf-8') as f:
            f.write(re.sub('let long_answers = \[];', f'let long_answers = {long_answers};', edited_script))
        with open('script.js', 'r') as f:
            edited_script = f.read()
        with open('script.js', 'w', encoding='utf-8') as f:
            f.write(re.sub('let lat_answers = \[];', f'let lat_answers = {lat_answers};', edited_script))

    with open('script', 'r') as file:
        script = file.read()
    with open('script.js', 'w', encoding='utf-8') as file:
        file.write(script)

    longitude_answers = []
    latitude_answers = []
    for i in range(5):
        is_land = False
        longitude = 0
        latitude = 0
        # checking that randomly generated longitudes and latitudes are on land
        while not is_land:
            longitude = random.uniform(-180, 180)
            latitude = random.uniform(-60, 70)
            point = Point(longitude, latitude)
            is_land = world.geometry.apply(lambda geom: geom.contains(point)).any()
        longitude_answers.append(longitude)
        latitude_answers.append(latitude)
        # creating map
        m = folium.Map(location=[latitude, longitude],
                       zoom_start=3,
                       dragging=False,
                       zoom_control=False,
                       scrollWheelZoom=False,
                       touchZoom=False,
                       doubleClickZoom=False)
        folium.GeoJson(world,
                       style_function=lambda feature: {'fillColor': 'white', 'weight': 0},
                       highlight_function=lambda feature: {}).add_to(m)
        question_map_html = m.get_root().render()
        # creating html files for each zoom level
        for j in range(10):
            path = f'question_maps_html/question_map_{j + 1}_{i + 1}.html'
            with open(path, 'w', encoding='utf-8') as file:
                file.write(re.sub(r'"zoom": 3', f'"zoom": {j + 3}', question_map_html))
    edit_script(longitude_answers, latitude_answers)


def capture_screenshots():
    # creating driver
    driver_path = "D:/Winston's Data/Downloads/geckodriver-v0.36.0-win32/geckodriver.exe"
    firefox_options = Options()
    firefox_options.set_preference("geo.enabled", False)
    firefox_options.add_argument("--headless")
    firefox_options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
    service = Service(executable_path=driver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # taking screenshot of each html file
    for i in range(1, 6):
        for j in range(1, 11):
            input_file = 'question_maps_html/question_map_' + str(j) + '_' + str(i) + '.html'
            output_file = 'question_maps_png/question_map_' + str(j) + '_' + str(i) + '.png'

            driver.get(os.path.abspath(input_file))

            time.sleep(0.5)

            driver.save_screenshot(output_file)

    driver.quit()


create_question_maps()
capture_screenshots()

webbrowser.open('file://' + os.path.realpath('index.html'))
