"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([EnergyScheduler(hass, config)])


class EnergyScheduler(SensorEntity):
    _attr_name = "Energy Scheduler"
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    #_attr_device_class = SensorDeviceClass.ENUM
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass, config):
        self.hass = hass
        self.config = self.read_config(config)
        logger.info("Initiating Energy Scheduler")

        self.now_value = 0
        self.now = 'Off'
        self.today = []
        self.raw_today = []

    def read_config(self, config):
        scheduler = config.get('scheduler', 'auto')

        schedulers = {'auto', 'manual', 'always_on', 'always_off'}
        if not scheduler in schedulers:
            logger.error('Invalid scheduler' + str(scheduler) +
                         '. Setting scheduler to auto')
            scheduler = 'auto'

        default_mode = config.get("default_mode", "on")

        hours_off = config.get("hours_off", None)
        if hours_off != None:
            hours_off = [int(hour) for hour in hours_off.split(',')]

        hours_on = config.get('hours_on', None)
        if hours_on != None:
            hours_on = [int(hour) for hour in hours_on.split(',')]

        if scheduler == 'manual':
            if default_mode == 'on' and hours_off == None:
                logger.warning(
                    'default_mode = on, no hours_off configured. Setting scheduler to always_on')
                scheduler = 'always_on'
            if default_mode == 'off' and hours_on == None:
                logger.warning(
                    'default_mode = off, no hours_on configured. Setting scheduler to always_off')
                scheduler = 'always_off'

        conf_dict = {
            'scheduler': scheduler,
            'default_mode': default_mode,
            'hours_off': hours_off,
            'hours_on': hours_on,
        }

        return conf_dict

    def set_mode(self, mode):
        modes = {'Off': 0, 'On': 1}
        self.now = mode
        self.now_value = modes[mode]
        self._attr_native_value = self.now_value

    def get_nordpool_raw_today(self):
        nordpool_raw_today = self.hass.data["nordpool"]._data['SEK']['today']['SE3']['values']
        # Every element is a reference and needs to de copied individually to not interfere with the Nordpool integration
        copied_list = [element.copy() for element in nordpool_raw_today]
        return copied_list.copy()

    def rank_hours_after_price(self, today):
        today_with_hours = [(i, today[i]) for i in range(len(today))]
        sorted_today_with_hours = sorted(
            today_with_hours, key=lambda tup: tup[1], reverse=True)

        ranked_hours = [0] * 24
        for i in range(len(sorted_today_with_hours)):
            ranked_hours[sorted_today_with_hours[i][0]] = i
        return ranked_hours

    def calculate_auto_mode(self, ranked_hours):
        DEFAULT_HOURS = 6
        today = []
        for rank in ranked_hours:
            if DEFAULT_HOURS > rank:
                mode = 0
            else:
                mode = 1
            today.append(mode)
        return today

    def calculate_manual_mode(self):
        if self.config.get('default_mode') == 'on':
            today = [1] * 24

            for hour in self.config.get('hours_off'):
                today[hour] = 0

        if self.config.get('default_mode') == 'off':
            today = [0] * 24

            for hour in self.config.get('hours_on'):
                today[hour] = 1

        return today

    def update(self) -> None:
        logger.info('Updating sensor')

        nordpool_raw_today = self.get_nordpool_raw_today()
        nordpool_today = [hour['value'] for hour in nordpool_raw_today]
        ranked_hours = self.rank_hours_after_price(nordpool_today)

        if self.config.get('scheduler') == 'auto':
            self.today = self.calculate_auto_mode(ranked_hours)

        elif self.config.get('scheduler') == 'manual':
            self.today = self.calculate_manual_mode()

        elif self.config.get('scheduler') == 'always_on':
            self.today = [1] * 24

        elif self.config.get('scheduler') == 'always_off':
            self.today = [0] * 24

        this_hour = int(datetime.now().strftime("%H"))
        if self.today[this_hour]:
            self.set_mode('On')
        else:
            self.set_mode('Off')

        raw_today = nordpool_raw_today
        for i in range(len(raw_today)):
            raw_today[i]['value'] = self.today[i]
        self.raw_today = raw_today

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "now": self.now,
            "now_value": self.now_value,
            "today": self.today,
            "raw_today": self.raw_today
        }
