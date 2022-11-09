"""Energy Scheduler"""

DOMAIN = "energy_scheduler"

async def async_setup(hass, config):
    hass.states.async_set("hello_state.world", "Poolus")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up nordpool as config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return true
