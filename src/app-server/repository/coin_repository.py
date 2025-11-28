import logging
from typing import List, Dict, Any
from database.database_connection import db
from model.Coins import Coins


class CoinRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def save_coin_list(self, coin_list: List[Coins]):
        """
        코인 목록을 저장 (중복 체크: 기존 코인은 업데이트, 새로운 코인만 추가)
        
        Args:
            coin_list: 저장할 코인 목록
            
        Returns:
            (새로 추가된 개수, 업데이트된 개수) 튜플
        """
        session = None
        try:
            session = db.get_session()

            # 기존 코인 목록 조회 (market_code 기준)
            existing_coins = {
                coin.market_code: coin 
                for coin in session.query(Coins).all()
            }
            
            new_count = 0
            updated_count = 0
            
            for coin in coin_list:
                if coin.market_code in existing_coins:
                    # 기존 코인 업데이트
                    existing_coin = existing_coins[coin.market_code]
                    existing_coin.symbol = coin.symbol
                    existing_coin.quote_currency = coin.quote_currency
                    existing_coin.korean_name = coin.korean_name
                    existing_coin.english_name = coin.english_name
                    existing_coin.img_url = coin.img_url
                    existing_coin.exchange = coin.exchange
                    existing_coin.is_active = coin.is_active
                    updated_count += 1
                else:
                    # 새로운 코인 추가
                    session.add(coin)
                    new_count += 1
            
            session.commit()

            self.logger.info(
                f"코인 목록 저장 완료: 새로 추가 {new_count}개, 업데이트 {updated_count}개"
            )
            
            return {"new": new_count, "updated": updated_count}
            
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
