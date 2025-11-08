import os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import logging
from typing import Annotated, Any
from fastapi import Depends
from dependencies import (
    get_upbit_service,
    get_coin_service,
    get_exchange_credentials_service,
    get_assets_service,
)
from dto.http_response import ErrorResponse, SuccessResponse
from dto.exchange_credentials_dto import ExchangeProvider
from dto.assets_dto import AssetsSyncRequest


router = APIRouter(prefix="/upbit")
load_dotenv()
logger = logging.getLogger(__name__)


@router.get("/allTradingHistory")
async def fetch_trading_history(
    upbit_service: Annotated[Any, Depends(get_upbit_service)]
):
    try:
        # 여기 나중에 db에서 조회하는걸로 변경
        access_key = os.getenv("UPBIT_ACCESS_KEY", "")
        secret_key = os.getenv("UPBIT_SECRET_KEY", "")

        uuids = upbit_service.fetch_all_trading_uuids(access_key, secret_key)

        trading_histies = upbit_service.fetch_all_trading_history(
            access_key, secret_key, uuids
        )
        return SuccessResponse(
            data=trading_histies, message="거래 내역 조회가 완료되었습니다"
        )
    except Exception as e:
        logger.error(f"예상치 못한 에러: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="서버 내부 오류가 발생했습니다",
                details=str(e),
            ).dict(),
        )


@router.post("/allCoinList")
async def fetch_and_save_all_coin_list(
    upbit_service: Annotated[Any, Depends(get_upbit_service)],
    coin_service: Annotated[Any, Depends(get_coin_service)],
):
    try:
        fetched_data_list = upbit_service.fetch_all_coin_list()
        saved_coin_list = coin_service.save_all_coin_list(fetched_data_list)

        return SuccessResponse(
            data=saved_coin_list, message="모든 코인 리스트 조회가 완료되었습니다"
        )
    except Exception as e:
        logger.error(f"예상치 못한 에러: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="서버 내부 오류가 발생했습니다",
                details=str(e),
            ).dict(),
        )


@router.get("/accounts/{user_id}")
async def fetch_accounts(
    user_id: str,
    upbit_service: Annotated[Any, Depends(get_upbit_service)],
    exchange_credentials_service: Annotated[
        Any, Depends(get_exchange_credentials_service)
    ],
):
    """Upbit 계정 잔고 조회"""
    try:
        # DB에서 Upbit 자격증명 조회
        credentials = exchange_credentials_service.get_credentials(
            user_id, ExchangeProvider.UPBIT
        )

        if not credentials:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    status_code=404,
                    error_code="CREDENTIALS_NOT_FOUND",
                    message="Upbit 자격증명을 찾을 수 없습니다",
                    details=f"사용자 {user_id}의 Upbit 자격증명이 없습니다",
                ).dict(),
            )

        # 복호화된 키 확인
        if not credentials.access_key or not credentials.secret_key:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    status_code=500,
                    error_code="CREDENTIALS_DECRYPTION_FAILED",
                    message="자격증명 복호화에 실패했습니다",
                    details="자격증명을 복호화할 수 없습니다",
                ).dict(),
            )

        # Upbit API로 계정 잔고 조회
        accounts = upbit_service.fetch_accounts(
            credentials.access_key, credentials.secret_key
        )

        return SuccessResponse(
            data=accounts, message="계정 잔고 조회가 완료되었습니다"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 잔고 조회 중 예상치 못한 에러: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="서버 내부 오류가 발생했습니다",
                details=str(e),
            ).dict(),
        )


@router.post("/accounts")
async def sync_accounts(
    request: AssetsSyncRequest,
    assets_service: Annotated[Any, Depends(get_assets_service)],
    exchange_credentials_service: Annotated[
        Any, Depends(get_exchange_credentials_service)
    ],
):
    """Upbit 계정 잔고를 assets 테이블에 동기화"""
    try:
        user_id = request.user_id

        # DB에서 Upbit 자격증명 조회
        credentials = exchange_credentials_service.get_credentials(
            user_id, ExchangeProvider.UPBIT
        )

        if not credentials:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    status_code=404,
                    error_code="CREDENTIALS_NOT_FOUND",
                    message="Upbit 자격증명을 찾을 수 없습니다",
                    details=f"사용자 {user_id}의 Upbit 자격증명이 없습니다",
                ).dict(),
            )

        # 복호화된 키 확인
        if not credentials.access_key or not credentials.secret_key:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    status_code=500,
                    error_code="CREDENTIALS_DECRYPTION_FAILED",
                    message="자격증명 복호화에 실패했습니다",
                    details="자격증명을 복호화할 수 없습니다",
                ).dict(),
            )

        # Assets Service로 자산 동기화
        result = assets_service.sync_upbit_assets(user_id)

        return SuccessResponse(
            data=result,
            message=f"자산 동기화가 완료되었습니다. 저장: {result['saved_count']}개, 삭제: {result['deleted_count']}개",
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"자산 동기화 검증 에러: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                status_code=400,
                error_code="VALIDATION_ERROR",
                message=str(e),
                details="입력된 정보를 확인해주세요",
            ).dict(),
        )
    except Exception as e:
        logger.error(f"자산 동기화 중 예상치 못한 에러: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="서버 내부 오류가 발생했습니다",
                details=str(e),
            ).dict(),
        )
