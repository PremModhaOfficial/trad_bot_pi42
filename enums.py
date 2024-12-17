from enum import Enum
from json import dumps


class PlaceType(Enum):
    ORDER_FORM = "ORDER_FORM"


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class OrderParams:
    def __init__(
        self,
        quantity: float,
        price: float = 0,
        placeType: str = "ORDER_FORM",
        side: Side = Side.BUY,
        symbol: str = "",
        reduceOnly: bool = False,
        marginAsset: str = "",
        orderType: str = "MARKET",
        takeProfitPrice: float = 0,
        stopLossPrice: float = 0,
        stopPrice: float = 0,
    ):
        self.quantity = quantity
        self.price = price
        self.placeType = placeType
        self.side = side
        self.symbol = symbol
        self.reduceOnly = reduceOnly
        self.marginAsset = marginAsset
        self.orderType = orderType
        self.takeProfitPrice = takeProfitPrice
        self.stopLossPrice = stopLossPrice
        self.stopPrice = stopPrice

    def __repr__(self):

        return dumps(
            {
                "quantity": self.quantity,
                "price": self.price,
                "placeType": self.placeType,
                "side": self.side,
                "symbol": self.symbol,
                "reduceOnly": self.reduceOnly,
                "marginAsset": self.marginAsset,
                "orderType": self.orderType,
                "takeProfitPrice": self.takeProfitPrice,
                "stopLossPrice": self.stopLossPrice,
                "stopPrice": self.stopPrice,
            }
        )
