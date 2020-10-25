"""
This component provides HA sensor for date reminder

For more details about this sensor, please refer to the documentation at
https://home-assistant.io/components/sensor.date_reminder/

KK 10/24/2020 - Got from here - https://github.com/aneisch/home-assistant-config
"""

import datetime
from datetime import timedelta
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ATTR_DAYS = 'days_since'
ATTR_REMAINING = 'days_remaining'

DEFAULT_NAME = 'Date Reminder'
CONF_START_INPUT_DATETIME = 'start_date_input'
CONF_REMINDER = 'days_in_future'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_START_INPUT_DATETIME): cv.string,
    vol.Required(CONF_REMINDER): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up date countdown sensor."""
    days_in_future = config.get(CONF_REMINDER)
    sensor_name = config.get(CONF_NAME)
    input_datetime = config.get(CONF_START_INPUT_DATETIME)

    add_devices([Reminder(hass, input_datetime, sensor_name, days_in_future)])


class Reminder(Entity):
    """Implementation of the date reminder sensor."""

    def __init__(self, hass, input_datetime, sensor_name, days_in_future):
        """Initialize the sensor."""
        self._input_datetime = input_datetime
        self.hass = hass
        self.days_in_future = days_in_future
        self._name = sensor_name
        self._state = None
        self._data = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        return {
            ATTR_DAYS: self._data.get("days_since"),
            ATTR_REMAINING: self._data.get("days_remaining"),
        }

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:calendar'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Calculate time since start"""
        start_date = self.hass.states.get(self._input_datetime).state
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        days = (datetime.datetime.now() - start_date)

        days = days.days

        self._data["days_since"] = days
        self._data["days_remaining"] = int(self.days_in_future) - days

        if days >= int(self.days_in_future):
          self._state = True
        else:
          self._state = False
