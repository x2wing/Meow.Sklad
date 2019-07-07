import folium
import json
import requests

# Necessary data for locations
locData = {"Алматы": [43.238293, 76.945465],
           "Нур-Султан": [51.128207, 71.430411],
           "Шымкент": [42.315514, 69.586907],
           "Караганда": [49.807754, 73.088504],
           "Актобе": [50.300371, 57.154555],
           "Тараз": [42.901183, 71.378309],
           "Павлодар": [52.285577, 76.940947],
           "Усть-Каменогорск": [49.948759, 82.628459],
           "Семей": [50.416526, 80.256170],
           "Костанай": [53.214480, 63.632073],
           "Атырау": [47.106811, 51.916874],
           "Кызылорда": [44.842557, 65.502545],
           "Уральск": [51.204019, 51.370537],
           "Петропавловск": [54.865472, 69.135602],
           "Актау": [54.865472, 69.135602]
           }


def hereTilesUrl(app_id, app_code, **kwdict):
    """
    Return a HERE map tiles URL, based on default values that can be
    overwritten by kwdict.
    """
    params = dict(app_id=app_id,
                  app_code=app_code,
                  scheme='reduced.day',
                  tilesize='256',
                  tileformat='png8',
                  lg='rus',
                  x='{x}',
                  y='{y}',
                  z='{z}', )

    params.update(kwdict)

    url = ('https://2.base.maps.api.here.com/maptile/2.1/maptile/newest/{scheme}/'
           '{z}/{x}/{y}/{tilesize}/{tileformat}'
           '?lg={lg}&app_id={app_id}&app_code={app_code}'
           ).format(**params)
    return url


def weather(lat, lon, app_id, app_code):
    """
    Return a data about weather info for x,y locations.

    """

    params = dict(product='observation',
                  latitude=lat,
                  longitude=lon,
                  oneobservation=True,
                  app_id=app_id,
                  app_code=app_code,
                  )
    respond = requests.get('https://weather.cit.api.here.com/weather/1.0/report.json',
                           params=params)
    jdata = respond.json()
    return jdata


if __name__ == '__main__':
    from .map_view_wgt import APP_ID, APP_CODE

    # Tiles build
    tilesUrl = hereTilesUrl(app_id=APP_ID, app_code=APP_CODE)

    """
    Create a map
    Settings for Kazakhstan position:
       location=[48.136207, 67.153550]
       zoom_start = 5.5
    """

    m = folium.Map(location=[43.238293, 76.945465],
                   zoom_start=12,
                   tiles=tilesUrl,
                   attr='here.com'
                   )

    # Add markers with weather info on the map
    tooltip = 'Нажмите, чтобы получить больше информации'

    for i in locData:
        # Get a weather data for each location
        wData = weather(locData[i][0], locData[i][1], APP_ID, APP_CODE)
        temper = round(float(wData["observations"]["location"][0]["observation"][0]["temperature"]))
        wSpeed = round(float(wData["observations"]["location"][0]["observation"][0]["windSpeed"]))
        iconUrl = wData["observations"]["location"][0]["observation"][0]["iconLink"]

        # Create markers
        folium.Marker(locData[i],
                      popup='<strong>{0}</strong>'
                            '<p>Температура воздуха: <strong>{1}</strong> градусов</p>'
                            '<p>Скорость ветра: <strong>{2}</strong> м/с</p>'.format(i, temper, wSpeed),
                      tooltip=tooltip,
                      icon=folium.features.CustomIcon(iconUrl, icon_size=(60, 60))).add_to(m)

    # # Geojson overlay
    # overlay = 'geodata.json'
    # folium.GeoJson(overlay).add_to(m)

    # Generate a map
    m.save('map.html')
