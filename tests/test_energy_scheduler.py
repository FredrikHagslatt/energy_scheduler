import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from custom_components.energy_scheduler.sensor import EnergyScheduler
from tests.mock_nordpool import MockNordPool


@pytest.fixture
def hass():
    hass_mock = MagicMock()
    hass_mock.states.get = MockNordPool.raw()
    return hass_mock


@pytest.fixture
def config():
    return {
        "scheduler": "auto",
        "default_mode": "on",
        "hours_off": "22,23",
        "hours_on": "8,9",
    }


def test_read_config(config):
    scheduler = EnergyScheduler(None, config)
    assert scheduler.config["scheduler"] == "auto"
    assert scheduler.config["default_mode"] == "on"
    assert scheduler.config["hours_off"] == [22, 23]
    assert scheduler.config["hours_on"] == [8, 9]


def test_set_mode(config):
    scheduler = EnergyScheduler(None, config)
    scheduler.set_mode("Off")
    assert scheduler.now == "Off"
    assert scheduler.now_value == 0

    scheduler.set_mode("On")
    assert scheduler.now == "On"
    assert scheduler.now_value == 1


def test_get_nordpool_entity_id(hass, config):
    hass.states.entity_ids.return_value = ["sensor.nordpool"]
    scheduler = EnergyScheduler(hass, config)
    assert scheduler.get_nordpool_entity_id() == "sensor.nordpool"


def test_rank_hours_after_price(config):
    scheduler = EnergyScheduler(None, config)
    hours = MockNordPool.day()

    ranked_hours = scheduler.rank_hours_after_price(hours)
    assert ranked_hours == MockNordPool.day_ranked()


def test_calculate_auto_mode(config):
    scheduler = EnergyScheduler(None, config)
    hours = MockNordPool.day()
    today = scheduler.calculate_auto_mode(hours)
    print(today)
    assert today == [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ]


def test_calculate_manual_mode():
    scheduler = EnergyScheduler(None, {"default_mode": "on", "hours_off": "1,2,5"})
    today = scheduler.calculate_manual_mode()
    assert today == [
        1,
        0,
        0,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ]


def test_update(hass):
    scheduler = EnergyScheduler(
        hass,
        {
            "scheduler": "auto",
            "default_mode": "on",
            "hours_off": "22,23",
            "hours_on": "8,9",
        },
    )
    scheduler.get_nordpool_raw = MagicMock(
        return_value=(
            [
                {"value": 0},
                {"value": 1},
                {"value": 2},
                {"value": 3},
                {"value": 4},
                {"value": 5},
                {"value": 6},
                {"value": 7},
                {"value": 8},
                {"value": 9},
                {"value": 10},
                {"value": 11},
                {"value": 12},
                {"value": 13},
                {"value": 14},
                {"value": 15},
                {"value": 16},
                {"value": 17},
                {"value": 18},
                {"value": 19},
                {"value": 20},
                {"value": 21},
                {"value": 22},
                {"value": 23},
            ],
            [
                {"value": 0},
                {"value": 1},
                {"value": 2},
                {"value": 3},
                {"value": 4},
                {"value": 5},
                {"value": 6},
                {"value": 7},
                {"value": 8},
                {"value": 9},
                {"value": 10},
                {"value": 11},
                {"value": 12},
                {"value": 13},
                {"value": 14},
                {"value": 15},
                {"value": 16},
                {"value": 17},
                {"value": 18},
                {"value": 19},
                {"value": 20},
                {"value": 21},
                {"value": 22},
                {"value": 23},
            ],
            True,
        )
    )

    with patch("datetime.datetime") as mock_datetime:
        mock_now = datetime(1970, 1, 1, 2, 13, 13, 000000)
        mock_datetime.now.return_value = mock_now
        scheduler.update()

        assert scheduler.now == "Off"
        assert scheduler.now_value == 0
        assert scheduler.tomorrow_valid is True

        mock_now = datetime(2023, 2, 2, 8, 13, 13, 000000)
        mock_datetime.now.return_value = mock_now

        scheduler.update()

        assert scheduler.now == "On"
        assert scheduler.now_value == 1
        assert scheduler.tomorrow_valid is True
