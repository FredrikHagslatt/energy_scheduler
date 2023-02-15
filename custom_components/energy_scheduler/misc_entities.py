
from datetime import datetime
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import ENERGY_KILO_WATT_HOUR

import logging

logger = logging.getLogger(__name__)


class EnergyDailyInit(SensorEntity):
    _attr_name = "Energy Daily Init"

    def __init__(self, hass):
        logger.info("Energy Daily Init")
        self.hass = hass
        self.last_update_date = datetime(1970, 1, 1).date()
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_value = 0

    def get_energy(self):
        entity_id = 'sensor.develco_zhemi101_summation_delivered'
        energy = self.hass.states.get(entity_id).state
        return energy

    @ property
    def update_value(self):
        self._attr_native_value = self.get_energy()

    def update(self) -> None:
        logger.info('Updating sensor')
        today = datetime.now().date()
        if self.last_update_date != today:
            self.update_value()
            self.last_update_date = today

