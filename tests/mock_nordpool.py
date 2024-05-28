#!/bin/python3

from datetime import datetime, timedelta


class MockNordPool:

    @staticmethod
    def raw():
        mock_now = datetime(1970, 1, 1, 0, 0, 0, 000000)

        raw_today = []
        raw_tomorrow = []
        for hour in range(24):
            today = {
                "start": mock_now.isoformat(),
                "end": (mock_now + timedelta(hours=1)).isoformat(),
                "value": hour,
            }
            tomorrow = {
                "start": (mock_now + timedelta(days=1)).isoformat(),
                "end": (mock_now + timedelta(days=1, hours=1)).isoformat(),
                "value": hour,
            }

            raw_today.append(today)
            raw_tomorrow.append(tomorrow)
            mock_now += timedelta(hours=1)

        tomorrow_valid = True

        attributes = {}
        attributes["raw_today"] = raw_today
        attributes["raw_tomorrow"] = raw_tomorrow
        attributes["tomorrow_valid"] = tomorrow_valid

        return attributes

    @staticmethod
    def day():
        return [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
        ]

    @staticmethod
    def day_ranked():
        return [
            23,
            22,
            21,
            20,
            19,
            18,
            17,
            16,
            15,
            14,
            13,
            12,
            11,
            10,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
            0,
        ]
