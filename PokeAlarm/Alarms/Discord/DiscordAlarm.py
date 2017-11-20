# Standard Library Imports
import logging
import requests

# 3rd Party Imports

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, get_static_map_url, \
    reject_leftover_parameters, require_and_remove_key, get_image_url

log = logging.getLogger('Discord')
try_sending = Alarm.try_sending
replace = Alarm.replace

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class DiscordAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'username': "<pkmn>",
            'content': "",
            'icon_url': get_image_url(
                "monsters/<pkmn_id_3>_<form_id_or_empty>.png"),
            'avatar_url': get_image_url(
                "monsters/<pkmn_id_3>_<form_id_or_empty>.png"),
            'title': "A wild <pkmn> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            'username': "Pokestop",
            'content': "",
            'icon_url': get_image_url("stop/ready.png"),
            'avatar_url': get_image_url("stop/ready.png"),
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            'username': "<new_team> Gym Alerts",
            'content': "",
            'icon_url': get_image_url("gyms/<new_team_id>.png"),
            'avatar_url': get_image_url("gyms/<new_team_id>.png"),
            'title': "A Team <old_team> gym has fallen!",
            'url': "<gmaps>",
            'body': "It is now controlled by <new_team>."
        },
        'egg': {
            'username': "Egg",
            'content': "",
            'icon_url': get_image_url("eggs/<raid_level>.png"),
            'avatar_url': get_image_url("eggs/<raid_level>.png"),
            'title': "Raid is incoming!",
            'url': "<gmaps>",
            'body': "A level <raid_level> raid will hatch at "
                    + "<begin_24h_time> (<begin_time_left>)."
        },
        'raid': {
            'username': "Raid",
            'content': "",
            'icon_url': get_image_url(
                "monsters/<pkmn_id_3>_<form_id_or_empty>.png"),
            'avatar_url': get_image_url("eggs/<raid_level>.png"),
            'title': "Level <raid_level> Raid is available against <pkmn>!",
            'url': "<gmaps>",
            'body': "The raid is available until <24h_time> (<time_left>)."
        },
        "gym_colors": {
            "?": "FFFFFF",
            "0": "FFFFFF",
            "1": "0000FF",
            "2": "FF0000",
            "3": "FFFF00"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings, max_attempts, static_map_key):
        # Required Parameters
        self.__webhook_url = require_and_remove_key(
            'webhook_url', settings, "'Discord' type alarms.")
        self.__max_attempts = max_attempts

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))
        self.__disable_embed = parse_boolean(
            settings.pop('disable_embed', "False"))
        self.__avatar_url = settings.pop('avatar_url', "")
        self.__map = settings.pop('map', {})
        self.__static_map_key = static_map_key

        # Set Alert Parameters
        self.__pokemon = self.create_alert_settings(
            settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(
            settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(
            settings.pop('gym', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(
            settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(
            settings.pop('raid', {}), self._defaults['raid'])

        self.__gym_colors = settings.pop("gym_colors", self._defaults["gym_colors"])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Discord alarm.")

        log.info("Discord Alarm has been created!")

    # (Re)connect with Discord
    def connect(self):
        pass

    # Send a message letting the channel know that this alarm has started
    def startup_message(self):
        if self.__startup_message:
            args = {
                'url': self.__webhook_url,
                'payload': {
                    'username': 'PokeAlarm',
                    'content': 'PokeAlarm activated!'
                }
            }
            try_sending(log, self.connect, "Discord",
                        self.send_webhook, args, self.__max_attempts)
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'webhook_url': settings.pop('webhook_url', self.__webhook_url),
            'username': settings.pop('username', default['username']),
            'avatar_url': settings.pop('avatar_url', default['avatar_url']),
            'disable_embed': parse_boolean(
                settings.pop('disable_embed', self.__disable_embed)),
            'content': settings.pop('content', default['content']),
            'icon_url': settings.pop('icon_url', default['icon_url']),
            'title': settings.pop('title', default['title']),
            'url': settings.pop('url', default['url']),
            'body': settings.pop('body', default['body']),
            'map': get_static_map_url(
                settings.pop('map', self.__map), self.__static_map_key)
        }

        reject_leftover_parameters(settings, "'Alert level in Discord alarm.")
        return alert

    # Send Alert to Discord
    def send_alert(self, alert, info):
        log.debug("Attempting to send notification to Discord.")
        payload = {
            # Usernames are limited to 32 characters
            'username': replace(alert['username'], info)[:32],
            'content': replace(alert['content'], info),
            'avatar_url': replace(alert['avatar_url'], info),
        }
        if alert['disable_embed'] is False:
            payload['embeds'] = [{
                'title': replace(alert['title'], info),
                'url': replace(alert['url'], info),
                'description': replace(alert['body'], info),
                'thumbnail': {'url': replace(alert['icon_url'], info)}
            }]
            if 'color' in info:
                payload['embeds'][0]['color'] = info['color']

            if alert['map'] is not None:
                coords = {
                    'lat': info['lat'],
                    'lng': info['lng']
                }
                payload['embeds'][0]['image'] = {
                    'url': replace(alert['map'], coords)
                }
        args = {
            'url': alert['webhook_url'],
            'payload': payload
        }
        try_sending(log, self.connect,
                    "Discord", self.send_webhook, args, self.__max_attempts)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        log.debug("Pokemon notification triggered.")
        pokemon_info['color'] = self.get_color(pokemon_info.get('iv', '?'))
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        log.debug("Pokestop notification triggered.")
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        log.debug("Gym notification triggered.")
        self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        raid_info['color'] = int(self.__gym_colors["{}".format(raid_info.get('team_id'), '0')], 16)
        self.send_alert(self.__egg, raid_info)

    def raid_alert(self, raid_info):
        raid_info['color'] = int(self.__gym_colors["{}".format(raid_info.get('team_id'), '0')], 16)
        self.send_alert(self.__raid, raid_info)

    # Send a payload to the webhook url
    def send_webhook(self, url, payload):
        log.debug(payload)
        resp = requests.post(url, json=payload, timeout=5)
        if resp.ok is True:
            log.debug("Notification successful (returned {})".format(
                resp.status_code))
        else:
            log.debug("Discord response was {}".format(resp.content))
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(resp.status_code))

    # Returns color for discord embeds
    @staticmethod
    def get_color(color_id):
        color_ = 0x4F545C

        try:
            if float(color_id) < 25:
                color_ = 0x9d9d9d
            elif float(color_id) < 50:
                color_ = 0xffffff
            elif float(color_id) < 82:
                color_ = 0x1eff00
            elif float(color_id) < 90:
                color_ = 0x0070dd
            elif float(color_id) < 100:
                color_ = 0xa335ee
            elif float(color_id) >= 100:
                color_ = 0xff8000
        except:
            try:
                if color_id == "?":
                    color_ = 0x4F545C
                elif color_id == "Valor":
                    color_ = 0xFE0103
                elif color_id == "Mystic":
                    color_ = 0x1102FD
                elif color_id == "Instinct":
                    color_ = 0xF6F006
                elif color_id[-1] == 's' or color_id[-1] == 'm':
                    color_ = 0xff66ff
                else:
                    color_ = 0x4F545C
            except:
                color_ = 0x4F545C
        return color_

