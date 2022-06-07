

import re

from pyowm import OWM

from jarvis.settings import WEATHER_API
from jarvis.skills.collection.location import LocationSkill
from jarvis.skills.collection.internet import InternetSkills
from jarvis.skills.skill import AssistantSkill


class WeatherSkills(AssistantSkill):
    
    @classmethod
    def tell_the_weather(cls, voice_transcript, skill):
        """
        Tells the weather of a place
        :param tag: string (e.g 'weather')
        :param voice_transcript: string (e.g 'weather in London')

        NOTE: If you have the error: 'Reason: Unable to find the resource', try another location
        e.g weather in London
        """
        tags = cls.extract_tags(voice_transcript, skill['tags'])
        for tag in tags:
            reg_ex = re.search(tag + ' [a-zA-Z][a-zA-Z] ([a-zA-Z]+)', voice_transcript)
            try:
                if WEATHER_API['key']:
                    city = cls._get_city(reg_ex)
                    if city:
                        status, temperature = cls._get_weather_status_and_temperature(city)
                        if status and temperature:
                            cls.response("Current weather in %s is %s.\n"
                                         "The maximum temperature is %0.2f degree celcius. \n"
                                         "The minimum temperature is %0.2f degree celcius."
                                         % (city, status, temperature['temp_max'], temperature['temp_min'])
                                         )
                        else:
                            cls.response("Sorry the weather API is not available now..")
                    else:
                        cls.response("Sorry, no location for weather, try again..")
                else:
                    cls.response("Weather forecast is not working.\n"
                                 "You can get an Weather API key from: https://openweathermap.org/appid")
            except Exception as e:
                if InternetSkills.internet_availability():
                    # If there is an error but the internet connect is good, then the weather API has problem
                    cls.console_manager.console_output(error_log=e)
                    cls.response("I faced an issue with the weather site..")

    @classmethod
    def _get_weather_status_and_temperature(cls, city):
        owm = OWM(API_key=WEATHER_API['key'])
        if owm.is_API_online():
            obs = owm.weather_at_place(city)
            weather = obs.get_weather()
            status = weather.get_status()
            temperature = weather.get_temperature(WEATHER_API['unit'])
            return status, temperature
        else:
            return None, None

    @classmethod
    def _get_city(cls, reg_ex):
        if not reg_ex:
            cls.console(info_log='Identify your location..')
            city, latitude, longitude = LocationSkill.get_location()
            if city:
                cls.console(info_log='You location is: {0}'.format(city))
            else:
                cls.console(error_log="I couldn't find your location")
        else:
            city = reg_ex.group(1)
        return city
