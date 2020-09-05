import asyncio
import logging
import async_timeout
import aiohttp
import json
from datetime import datetime, timedelta, date

from .const import LOGIN_RESULT_OK, LOGIN_RESULT_UNAUTHORIZED

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5

URL_LOGIN = "https://api.qustodio.com/v1/oauth2/access_token"
URL_ACCOUNT = "https://api.qustodio.com/v1/accounts/me"
URL_PROFILES = "https://api.qustodio.com/v1/accounts/{}/profiles/"
URL_RULES = "https://api.qustodio.com/v1/accounts/{}/profiles/{}/rules?app_rules=1"
URL_SUMARY = "https://api.qustodio.com/v1/accounts/{}/profiles/{}/summary"
URL_DEVICES = "https://api.qustodio.com/v1/accounts/{}/devices"
URL_HOURLY_SUMARY = (
    "https://api.qustodio.com/v2/accounts/{}/profiles/{}/summary_hourly?date={}"
)


class QustodioApi(object):
    def __init__(self, username, password, loop):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._loop = loop
        self._session = None

        self._access_token = None
        self._expires_in = None

    async def login(self):
        if (
            self._access_token is not None
            and not self._expires_in is None
            and self._expires_in > datetime.now()
        ):
            return LOGIN_RESULT_OK
        _LOGGER.info("Logging")
        data = {}

        if self._session is not None:
            session = self._session
            close = False
        else:
            session = aiohttp.ClientSession()
            close = True

        data["client_id"] = "264ca1d226906aa08b03"
        data["client_secret"] = "3e8826cbed3b996f8b206c7d6a4b2321529bc6bd"
        data["grant_type"] = "password"
        data["username"] = self._username
        data["password"] = self._password

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await session.post(URL_LOGIN, data=data)

        if response.reason == "Unauthorized":
            return LOGIN_RESULT_UNAUTHORIZED

        if response.status == 200:
            js = json.loads(await response.text())

        _LOGGER.info(f"Logging Successful")
        self._access_token = js["access_token"]
        self._expires_in = datetime.now() + timedelta(seconds=js["expires_in"])

        if close:
            await session.close()

        return LOGIN_RESULT_OK

    async def get_data(self):
        _LOGGER.info(f"Getting data")
        data = {}
        async with aiohttp.ClientSession() as session:
            self._session = session
            if await self.login() != LOGIN_RESULT_OK:
                return data

            headers = {"Authorization": f"Bearer {self._access_token}"}

            async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                response = await self._session.get(URL_ACCOUNT, headers=headers)

            if response.status == 200:
                js = json.loads(await response.text())
                self._account_id = js["id"]
                self._account_uid = js["uid"]

            # devices
            async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                response = await self._session.get(
                    URL_DEVICES.format(self._account_id), headers=headers
                )

            js = json.loads(await response.text())

            devices = {}
            for device in js:
                devices[device["id"]] = device

            async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                response = await self._session.get(
                    URL_PROFILES.format(self._account_id), headers=headers
                )

            js = json.loads(await response.text())

            days = ["mon", "tue", "wed", "thr", "fri", "sat", "sun"]
            dow = days[datetime.today().weekday()]

            for profile in js:
                p = {}
                p["id"] = profile["id"]
                p["uid"] = profile["uid"]
                p["name"] = profile["name"]
                p["is_online"] = profile["status"]["is_online"]

                device_id = profile["status"]["location"]["device"]
                if p["is_online"]:
                    p["current_device"] = devices[device_id]["name"]
                else:
                    p["current_device"] = None

                async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                    response = await self._session.get(
                        URL_RULES.format(self._account_id, p["id"]), headers=headers
                    )
                js = json.loads(await response.text())
                p["quota"] = js["time_restrictions"]["quotas"][dow]

                # async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                #    response = await self._session.get(
                #        URL_SUMARY.format(self._account_id, p["id"]), headers=headers
                #    )
                # js = json.loads(await response.text())
                # p["time"] = js[0]["total"]

                # Get Hourly Summary
                async with async_timeout.timeout(TIMEOUT, loop=self._loop):
                    response = await self._session.get(
                        URL_HOURLY_SUMARY.format(
                            self._account_uid, p["uid"], date.today()
                        ),
                        headers=headers,
                    )
                js = json.loads(await response.text())

                time = 0
                for entry in js:
                    time = time + entry["screen_time_seconds"]
                p["time"] = time / 60

                data[p["id"]] = p

            await session.close()
            self._session = None
        return data
