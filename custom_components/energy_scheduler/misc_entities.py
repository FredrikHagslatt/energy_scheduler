
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
        self._attr_native_value = 0

        # Attempt to restore the previous value upon initialization
        last_state = self.hass.states.get('sensor.energy_daily_init')
        if last_state and last_state.state != 'unknown':
            parts = last_state.state.split(',')
            if len(parts) == 2:
                self.last_update_date = datetime.strptime(parts[0], '%Y-%m-%d').date()
                self._attr_native_value = float(parts[1])

    def get_energy(self):
        entity_id = 'sensor.develco_zhemi101_summation_delivered'
        entity = self.hass.states.get(entity_id)
        if entity:
            energy = entity.state
        else:
            energy = 0
        logger.info(energy)
        return energy

    def update(self) -> None:
        logger.info('Updating sensor')
        today = datetime.now().date()
        if self.last_update_date != today:
            self._attr_native_value = self.get_energy()
            self.last_update_date = today

            # Store the value and last_update_date persistently
            value_to_store = f"{self.last_update_date.strftime('%Y-%m-%d')},{self._attr_native_value}"
            self.hass.services.call('persistent_notification', 'create', {
                'title': 'Energy Daily Init',
                'message': value_to_store
            })
