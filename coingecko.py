import logging
from decimal import Decimal
from typing import Optional, Dict, List
from functools import cache
import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger("django")


class CoingeckoApi(object):
    _base_url = 'https://api.coingecko.com/api/v3'

    def __init__(self):
        self._http_session = requests.session()
        http_adapter = HTTPAdapter(max_retries=Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 502, 503, 504, 522]
        ))
        self._http_session.mount(self._base_url, http_adapter)

    def _request(self, uri, method='get', params: Optional[Dict] = None, data: Optional[Dict] = None, **kwargs):
        try:
            response = self._http_session.request(
                method=method,
                url=f'{self._base_url}/{uri}',
                data=data,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            raise

    def _request_paginated_field(
        self,
        uri: str,
        field_name: str,
        method='get',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ):
        params = params or {}
        params['page'] = 1
        response = self._request(
            uri=uri,
            method=method,
            params=params,
            data=data,
            **kwargs
        )

        while len(response[field_name]):
            yield from response[field_name]
            params['page'] += 1
            response = self._request(
                uri=uri,
                method=method,
                params=params,
                data=data,
                **kwargs
            )

    def _request_paginated(
        self,
        uri: str,
        method='get',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ):
        page = 1
        params = params or {}
        params['page'] = page
        response = self._request(
            uri=uri,
            method=method,
            params=params,
            data=data,
            **kwargs
        )

        while len(response):
            yield from response
            page += 1
            params['page'] = page
            response = self._request(
                uri=uri,
                method=method,
                params=params,
                data=data,
                **kwargs
            )

    @cache
    def get_coins(self):
        return self._request(
            'coins/list'
        )

    @cache
    def get_coin_by_symbol(self, symbol: str):
        coins = self.get_coins()
        try:
            return [
                coin for coin in coins
                if coin['symbol'].lower() == symbol.lower()
            ][0]
        except IndexError:
            return None

    def get_simple_price(
        self,
        ids: List,
        vs_currencies: List,
        include_market_cap=False,
        include_24hr_vol=False,
        include_24hr_change=False,
        include_last_updated_at=False
    ):
        logging.info(f"coingecko: getting current price of {ids}")
        return self._request(
            'simple/price',
            params={
                'ids': ','.join(ids),
                'vs_currencies': ','.join(vs_currencies),
                'include_market_cap': str(include_market_cap).lower(),
                'include_24hr_vol': str(include_24hr_vol).lower(),
                'include_24hr_change': str(include_24hr_change).lower(),
                'include_last_updated_at': str(include_last_updated_at).lower(),
            }
        )

    @cache
    def get_price_by_symbol(self, symbol, currency) -> Decimal:
        coin = self.get_coin_by_symbol(symbol=symbol)
        p = self.get_simple_price(ids=[coin['id']], vs_currencies=[currency])
        return Decimal(p[coin['id']][currency])
