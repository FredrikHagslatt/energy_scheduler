# Energy Scheduler

This integrations reads energy prices from Nordpool and schedules which hours to run energy heavy equipment like water heaters.

## Installation

1. Ensure HACS is installed in your Home Assistant instance.
2. Add this repository to HACS.
3. Install the "Value Saver" integration via HACS.
4. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: energy_scheduler
    scheduler: manual
    default_mode: "off"
    hours_on: 1,2,3,4,5
