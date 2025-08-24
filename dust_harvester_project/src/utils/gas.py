import asyncio
from src.config import settings
from src.evm import evm
import logging

logger = logging.getLogger(__name__)

async def estimate_gas_cost(transaction_data):
    """Оценить стоимость газа для транзакции"""
    try:
        # Получаем текущую цену газа
        gas_price = evm.w3.eth.gas_price
        
        # Используем настройки или оценку газа
        gas_limit = settings.GAS_LIMIT
        
        # Применяем множитель
        gas_cost = gas_price * gas_limit * settings.GAS_MULTIPLIER
        
        return gas_cost
    except Exception as e:
        logger.error(f"Error estimating gas cost: {e}")
        return 0

async def get_current_gas_price():
    """Получить текущую цену газа"""
    try:
        return evm.w3.eth.gas_price
    except Exception as e:
        logger.error(f"Error getting gas price: {e}")
        return evm.w3.to_wei(settings.GAS_PRICE_GWEI, 'gwei')

async def is_profitable(candidate):
    """Проверить, прибыльна ли возможность после учета газа"""
    try:
        pair, token, surplus = candidate
        
        # Конвертируем surplus в Wei (предполагаем, что это ETH)
        surplus_wei = float(surplus) * 10**18 if isinstance(surplus, (int, float, str)) else 0
        
        # Создаем примерные данные транзакции для оценки газа
        transaction_data = {
            'to': pair,
            'value': 0,
            'gas': settings.GAS_LIMIT,
            'gasPrice': await get_current_gas_price()
        }
        
        # Оцениваем стоимость газа
        gas_cost = await estimate_gas_cost(transaction_data)
        
        # Проверяем прибыльность
        profit = surplus_wei - gas_cost
        min_profit_wei = settings.MIN_PROFIT_ETH * 10**18
        
        is_prof = profit > min_profit_wei
        
        if is_prof:
            logger.info(f"Profitable candidate: {pair}, profit: {profit/10**18:.6f} ETH")
        else:
            logger.debug(f"Not profitable: {pair}, profit: {profit/10**18:.6f} ETH, gas: {gas_cost/10**18:.6f} ETH")
        
        return is_prof
        
    except Exception as e:
        logger.error(f"Error checking profitability for {candidate}: {e}")
        return False

async def optimize_gas_price():
    """Оптимизировать цену газа на основе сетевых условий"""
    try:
        current_price = await get_current_gas_price()
        
        # Простая логика оптимизации - используем текущую цену с множителем
        optimized_price = int(current_price * settings.GAS_MULTIPLIER)
        
        return optimized_price
    except Exception as e:
        logger.error(f"Error optimizing gas price: {e}")
        return evm.w3.to_wei(settings.GAS_PRICE_GWEI, 'gwei')
