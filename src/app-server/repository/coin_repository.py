import logging
from typing import List, Dict, Any
from database.database_connection import db
from model.Coins import Coins


class CoinRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def save_coin_list(self, coin_list: List[Coins]):
        session = None
        try:
            session = db.get_session()

            saved_coin_list = session.bulk_save_objects(coin_list)
            session.commit()

            return saved_coin_list
        except Exception as e:
            self.logger.error(f"코인 목록 저장 중 에러 발생: {e}")
            if session:
                session.rollback()
            raise e
        finally:
            if session:
                session.close()

    def get_all_coins(self):
        session = None
        try:
            session = db.get_session()
            coins = session.query(Coins).all()
            return coins
        except Exception as e:
            self.logger.error(f"코인 목록 조회 중 에러 발생: {e}")
            raise e
        finally:
            if session:
                session.close()
