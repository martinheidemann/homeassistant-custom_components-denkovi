"""
Support for an exposed Denkovi HTTP API of a device.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.arest/
"""

import logging
from datetime import timedelta

import requests
import voluptuous as vol

from homeassistant.components.switch import (SwitchEntity, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_RESOURCE, CONF_PASSWORD)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_RELAYS = 'relays'
CONF_INVERT = 'invert'
CONF_PINS = 'pins'

DEFAULT_NAME = 'Denkovi switch'

PIN_FUNCTION_SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_PINS): cv.string,
    vol.Optional(CONF_INVERT, default=False): cv.boolean,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_RESOURCE): cv.url,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_RELAYS, default={}):
        vol.Schema({cv.string: PIN_FUNCTION_SCHEMA})
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Denkovi switches."""
    resource = config.get(CONF_RESOURCE)
    password = config.get(CONF_PASSWORD)

    try:
        denkoviModule = DenkoviModule(resource, password)
    except DenkoviException as e:
        _LOGGER.error(str(e))
        return False

    dev = []
    relays = config.get(CONF_RELAYS)
    for relaynum, relay in relays.items():
        dev.append(DenkoviSwitchRelay(denkoviModule, relay.get(CONF_NAME), relay.get(CONF_PINS), relay.get(CONF_INVERT)))

    add_entities(dev)

class DenkoviModule():

    def __init__(self, resource, password):
        self._resource = resource
        self._password = password
        self.update()

    def turn_on_or_off(self, pinList, payload):
        try:
            response_str = '{}/current_state.json?pw={}'.format(self._resource, self._password)

            for pin in pinList.split():
                response_str += '&Relay{}={}'.format(int(pin), payload)

            self._response = requests.get(response_str, timeout=20)

        except requests.exceptions.ConnectionError:
            raise DenkoviConnectException('turn_on_or_off - No route to device {}'.format(self._resource))

    def get_state(self, pinList):
        if self._response.status_code == 200:
            try:
                rc = 0

                for pin in pinList.split():
                  rc += int(self._response.json()['CurrentState']['Output'][int(pin) - 1]['Value'])

                if rc > 0:
                    return 1
                else:
                    return 0
            except:
                raise DenkoviException('Unexpected JSONL {}'.format(self._response.content))
        else:
            raise DenkoviException('Unexpected HTTP Response code: {}'.format(self._response.status_code))

    @Throttle(timedelta(minutes=5))
    def update(self):
        _LOGGER.info("Updating DenkoviModule %s", self._resource)
        """Get the latest data from Denkovi API and update the state."""
        try:
            self._response = requests.get('{}/current_state.json?pw={}'.format(self._resource, self._password), timeout=30)
            if self._response.status_code != 200:
                raise DenkoviException('Unexpected HTTP Response code: {}'.format(self._response.status_code))
        except requests.exceptions.MissingSchema:
            raise DenkoviException("Missing resource or schema in configuration. Add http:// to your URL")
        except requests.exceptions.ConnectionError:
            raise DenkoviConnectException('update - No route to device {}'.format(self._resource))


class DenkoviSwitchBase(SwitchEntity):
    """Representation of an Denkovi switch."""

    def __init__(self, denkoviModule, name):
        """Initialize the switch."""
        self._denkoviModule = denkoviModule
        self._name = name
        self._unique_id = name
        self._state = None
        self._available = True

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique id of the switch."""
        return self._unique_id

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._available


class DenkoviSwitchRelay(DenkoviSwitchBase):
    """Representation of an Denkovi switch. Based on digital I/O."""

    def __init__(self, denkoviModule, name, pinList, invert):
        """Initialize the switch."""
        super().__init__(denkoviModule, name)
        self._pinList = pinList
        self._invert = invert
        self.update()

    def turn_on(self, **kwargs):
        """Turn the device on."""
        turn_on_payload = int(not self._invert)
        self.turn_on_or_off(turn_on_payload)
        _LOGGER.info("Turning on %s", self._name)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        turn_off_payload = int(self._invert)
        self.turn_on_or_off(turn_off_payload)
        _LOGGER.info("Turning off %s", self._name)

    def turn_on_or_off(self, payload):
        """Turn the device on or off."""
        try:
            self._denkoviModule.turn_on_or_off(self._pinList, payload)
            status_value = int(self._invert)
            self._state = self._denkoviModule.get_state(self._pinList) != status_value
            self._available = True
        except DenkoviException as e:
            _LOGGER.error("Error turning on or off: %s", str(e))
            self._available = False

    def update(self):
        """Get the latest data from Denkovi API and update the state."""
        try:
            self._denkoviModule.update()
            status_value = int(self._invert)
            self._state = self._denkoviModule.get_state(self._pinList) != status_value
            self._available = True
        except DenkoviException:
            _LOGGER.error("Error updating state for relay %s, %s", str(self._relay), str(e))
            self._available = False

class DenkoviException(Exception):
    pass

class DenkoviConnectException(DenkoviException):
    pass
