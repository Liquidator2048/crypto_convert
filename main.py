# encoding: utf-8
from decimal import Decimal

import npyscreen

from coingecko import CoingeckoApi
from numericstringparser import NumericStringParser


class CoinApp(npyscreen.NPSApp):
    currencies = ["usd", "eur"]

    def __init__(self):
        self.f = None
        self.size = None
        self.coin = None
        self.currency = None
        self.calc = None
        self.value = None
        self.price = None
        self.capi = CoingeckoApi()

    def _calculate(self):
        self._set_value("calculating ...")
        try:
            size = self._get_size()
            symbol = self.coin.get_value()
            currency = self.currencies[self.currency.get_value()[0]]
            price = self.capi.get_price_by_symbol(
                symbol=symbol,
                currency=currency
            )
            self._set_size(size)
            self._set_price(price)
            self._set_value(price * size)
        except Exception as e:
            self._set_price("")
            if hasattr(e, "message"):

                self._set_value(f"ERROR {e.__class__.__name__}: {e.message}")
            else:
                self._set_value(f"ERROR {e.__class__.__name__}")

    def _get_size(self) -> Decimal:
        nsp = NumericStringParser()
        return Decimal(nsp.eval(self.size.get_value().replace(",", ".")))

    def _set_size(self, value):
        self.size.set_value(str(value))
        self.size.update()

    def _set_value(self, value):
        self.value.set_value(str(value))
        self.value.update()

    def _set_price(self, value):
        self.price.set_value(str(value))
        self.price.update()

    def main(self):
        self.f = npyscreen.SplitForm(name="Price convert", lines=15, columns=40, minimum_lines=24, minimum_columns=30,
                                     draw_line_at=10)
        self.size = self.f.add(npyscreen.TitleText, name="Coin value:", )
        self.coin = self.f.add(npyscreen.TitleText, name="Coin:")
        # self.currency = self.f.add(npyscreen.TitleCombo, name="Convert to:", values=self.currencies)
        self.currency = self.f.add(npyscreen.TitleSelectOne, max_height=4, value=[0, ], name="Currency:",
                                   values=self.currencies, scroll_exit=True)
        self.calc = self.f.add(npyscreen.ButtonPress, name="Calculate", when_pressed_function=self._calculate)
        self.f.nextrely += 2
        self.price = self.f.add(npyscreen.TitleText, name="price: ", editable=False)
        self.value = self.f.add(npyscreen.TitleText, name="result: ", editable=False)
        self.f.edit()


if __name__ == "__main__":
    app = CoinApp()
    app.run()
