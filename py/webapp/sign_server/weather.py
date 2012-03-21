'''
Created on Mar 7, 2012

@author: robert
'''
from xml.etree import ElementTree as ET
import urllib

class Weather(object):
    '''
    classdocs
    '''

    maxCharsPerRow = 32
    weatherFeedUrl = 'http://www.weather.gov/xml/current_obs/KMSP.xml'


    def __init__(self):
        '''
        Constructor
        '''


    def getCurrentWeather(self):
        curWeatherXml =  ET.XML(urllib.urlopen(self.weatherFeedUrl).read());
        rows = []
        rows.append(curWeatherXml.find('weather').text[:self.maxCharsPerRow])
        rows.append(('Temperature: ' + curWeatherXml.find('temperature_string').text)[:self.maxCharsPerRow])
        rows.append(('Wind: ' + curWeatherXml.find('wind_string').text)[:self.maxCharsPerRow])
#        rows.append(('Windchill: ' + curWeatherXml.find('windchill_string').text)[:self.maxCharsPerRow])
        return rows
