from fastapi import Depends
from typing import Annotated, Any
from repository.coin_repository import CoinRepository
from repository.user_repository import UserRepository

# 싱글톤 인스턴스들
_upbit_service_instance = None
_coin_service_instance = None
_coin_repository_instance = None
_user_service_instance = None
_user_repository_instance = None
_trading_histories_service_instance = None
_exchange_credentials_service_instance = None
_assets_service_instance = None
_trading_profit_service_instance = None


# 의존성 주입 함수들
def get_user_service() -> Any:
    global _user_service_instance
    if _user_service_instance is None:
        from service.user_service import UserService  # lazy import

        _user_service_instance = UserService()
    return _user_service_instance


def get_user_repository() -> UserRepository:
    global _user_repository_instance
    if _user_repository_instance is None:
        _user_repository_instance = UserRepository()
    return _user_repository_instance


def get_upbit_service() -> Any:  # Any로 타입 힌트
    global _upbit_service_instance
    if _upbit_service_instance is None:
        from service.upbit_service import UpbitService  # lazy import

        _upbit_service_instance = UpbitService()
    return _upbit_service_instance


def get_coin_service() -> Any:  # Any로 타입 힌트
    global _coin_service_instance
    if _coin_service_instance is None:
        from service.coin_service import CoinService  # lazy import

        _coin_service_instance = CoinService()
    return _coin_service_instance


def get_coin_repository() -> CoinRepository:
    global _coin_repository_instance
    if _coin_repository_instance is None:
        _coin_repository_instance = CoinRepository()
    return _coin_repository_instance


def get_trading_histories_service() -> Any:
    global _trading_histories_service_instance
    if _trading_histories_service_instance is None:
        from service.trading_histories_service import TradingHistoriesService

        _trading_histories_service_instance = TradingHistoriesService()
    return _trading_histories_service_instance


def get_exchange_credentials_service() -> Any:
    global _exchange_credentials_service_instance
    if _exchange_credentials_service_instance is None:
        from service.exchange_credentials_service import ExchangeCredentialsService

        _exchange_credentials_service_instance = ExchangeCredentialsService()
    return _exchange_credentials_service_instance


def get_assets_service() -> Any:
    global _assets_service_instance
    if _assets_service_instance is None:
        from service.assets_service import AssetsService

        _assets_service_instance = AssetsService()
    return _assets_service_instance


def get_trading_profit_service() -> Any:
    global _trading_profit_service_instance
    if _trading_profit_service_instance is None:
        from service.trading_profit_service import TradingProfitService

        _trading_profit_service_instance = TradingProfitService()
    return _trading_profit_service_instance
