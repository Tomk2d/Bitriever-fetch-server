from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, Any
import logging
from dto.http_response import ErrorResponse, SuccessResponse
from dto.trading_profit_dto import CalculateProfitRequest
from dependencies import get_trading_profit_service

router = APIRouter(prefix="/trading-profit", tags=["거래 수익률"])
logger = logging.getLogger(__name__)


@router.post("/calculate", summary="거래 수익률 테스트 계산")
async def calculate_profit(
    request: CalculateProfitRequest,
    trading_profit_service: Annotated[Any, Depends(get_trading_profit_service)],
):
    """
    거래 내역 수익률 계산 및 업데이트, 보유 종목 평단 저장
    
    - 최초 fetch인 경우 (is_initial=True): 전체 거래 내역을 순회하며 계산
    - 이후 업데이트인 경우 (is_initial=False): coin_holdings_past 테이블의 기존 보유 종목 평단을 사용하여 계산
    """
    try:
        # 거래소 코드 검증
        if request.exchange_code not in [1, 2, 3, 4]:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status_code=400,
                    error_code="INVALID_EXCHANGE_CODE",
                    message="잘못된 거래소 코드입니다",
                    details="거래소 코드는 1(Upbit), 2(Bithumb), 3(Binance), 4(OKX) 중 하나여야 합니다",
                ).dict(),
            )

        # 수익률 계산 및 업데이트
        result = trading_profit_service.calculate_and_update_profit_loss(
            request.user_id, request.exchange_code, request.is_initial
        )

        return SuccessResponse(
            data=result,
            message=f"수익률 계산이 완료되었습니다. 업데이트: {result['updated_count']}개, 보유 종목: {result['holdings_count']}개, 삭제: {result['deleted_holdings_count']}개",
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"수익률 계산 검증 에러: {e}")
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
        logger.error(f"수익률 계산 중 예상치 못한 에러: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="서버 내부 오류가 발생했습니다",
                details=str(e),
            ).dict(),
        )

