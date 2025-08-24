import asyncio
from typing import List, Tuple
import random
from src.incentives.base import BaseIncentiveStrategy
from src.config import settings
from src.evm import evm
from src.utils.metrics import metrics
import logging

logger = logging.getLogger(__name__)

class AmmSkim(BaseIncentiveStrategy):
    """
    Стратегия поиска surplus токенов в AMM парах для skim операций
    """
    
    def __init__(self):
        super().__init__()
        self.uniswap_factory = settings.UNISWAP_V2_FACTORY
        self.pairs_checked = set()
    
    async def discover_candidates(self) -> List[Tuple[str, str, float]]:
        """
        Поиск кандидатов для skim операций в AMM парах
        """
        logger.info(f"Starting candidate discovery, max pairs: {settings.MAX_PAIRS}")
        metrics.start_session()
        
        candidates = []
        
        try:
            # Получаем список пар для проверки
            pairs_to_check = await self._get_pairs_to_check()
            
            logger.info(f"Found {len(pairs_to_check)} pairs to check")
            
            # Проверяем каждую пару на наличие surplus
            for i, pair_address in enumerate(pairs_to_check):
                if i >= settings.MAX_PAIRS:
                    break
                
                try:
                    candidate = await self._check_pair_for_surplus(pair_address)
                    if candidate:
                        candidates.append(candidate)
                        logger.info(f"Found candidate in pair {pair_address}: surplus {candidate[2]}")
                    
                    metrics.record_pair_checked(pair_address)
                    
                    # Небольшая задержка между проверками
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error checking pair {pair_address}: {e}")
                    metrics.record_error(f"Error checking pair {pair_address}: {e}", "pair_check")
            
            metrics.record_candidates_found(len(candidates))
            logger.info(f"Discovery complete. Found {len(candidates)} candidates")
            
        except Exception as e:
            logger.error(f"Error in candidate discovery: {e}")
            metrics.record_error(f"Discovery error: {e}", "discovery")
        
        return candidates
    
    async def execute_candidate(self, candidate: Tuple[str, str, float]) -> bool:
        """
        Выполнить skim операцию для кандидата
        """
        if not await self.validate_candidate(candidate):
            logger.warning(f"Invalid candidate: {candidate}")
            return False
        
        pair_address, token_address, surplus = candidate
        
        try:
            # Создаем транзакцию для skim операции
            transaction_data = await self._create_skim_transaction(pair_address, token_address)
            
            if not transaction_data:
                logger.error(f"Failed to create transaction for {pair_address}")
                return False
            
            # Отправляем транзакцию
            result = await evm.send_transaction(transaction_data)
            
            if result and result.get('hash'):
                logger.info(f"Skim transaction sent: {result['hash']}")
                
                # Записываем метрики
                gas_cost_eth = (transaction_data.get('gasPrice', 0) * transaction_data.get('gas', 0)) / 10**18
                metrics.record_candidate_executed(surplus, gas_cost_eth)
                
                return True
            else:
                logger.error(f"Failed to send skim transaction for {pair_address}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing candidate {candidate}: {e}")
            metrics.record_error(f"Execution error for {pair_address}: {e}", "execution")
            return False
    
    async def _get_pairs_to_check(self) -> List[str]:
        """
        Получить список адресов пар для проверки
        """
        # В реальной реализации здесь будет обращение к Uniswap Factory
        # Для демонстрации генерируем примерные адреса пар
        pairs = []
        
        try:
            # Эмуляция получения пар из factory контракта
            # В реальности нужно вызывать getPair или allPairs
            for i in range(min(settings.MAX_PAIRS * 2, 200)):  # Больше пар для выборки
                # Генерируем валидные Ethereum адреса для примера
                pair_address = f"0x{''.join([f'{random.randint(0, 15):x}' for _ in range(40)])}"
                pairs.append(pair_address)
            
            logger.info(f"Generated {len(pairs)} example pairs for checking")
            
        except Exception as e:
            logger.error(f"Error getting pairs to check: {e}")
        
        return pairs
    
    async def _check_pair_for_surplus(self, pair_address: str) -> Tuple[str, str, float] | None:
        """
        Проверить пару на наличие surplus токенов
        """
        try:
            # Эмуляция проверки surplus в паре
            # В реальности здесь будет вызов getReserves и проверка баланса контракта
            
            # Случайно определяем, есть ли surplus (для демонстрации)
            has_surplus = random.random() < 0.05  # 5% шанс найти surplus
            
            if has_surplus:
                # Генерируем данные о surplus
                token_address = f"0x{''.join([f'{random.randint(0, 15):x}' for _ in range(40)])}"
                surplus_amount = random.uniform(0.001, 0.1)  # От 0.001 до 0.1 ETH
                
                return (pair_address, token_address, surplus_amount)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking surplus for pair {pair_address}: {e}")
            return None
    
    async def _create_skim_transaction(self, pair_address: str, token_address: str) -> dict | None:
        """
        Создать транзакцию для skim операции
        """
        try:
            # Получаем оптимизированную цену газа
            from src.utils.gas import optimize_gas_price
            gas_price = await optimize_gas_price()
            
            # Создаем данные транзакции
            transaction_data = {
                'from': evm.account.address,  # ИСПРАВЛЕНИЕ: добавлен адрес отправителя
                'to': pair_address,
                'value': 0,  # Skim не требует отправки ETH
                'gas': settings.GAS_LIMIT,
                'gasPrice': gas_price,
                'data': self._encode_skim_function_call(),
                'chainId': settings.CHAIN_ID
            }
            
            return transaction_data
            
        except Exception as e:
            logger.error(f"Error creating skim transaction for {pair_address}: {e}")
            return None
    
    def _encode_skim_function_call(self) -> str:
        """
        Закодировать вызов функции skim()
        """
        # Сигнатура функции skim() в Uniswap V2
        # skim() function selector: 0xbc25cf77
        return "0xbc25cf77"
    
    async def get_pair_reserves(self, pair_address: str) -> Tuple[int, int] | None:
        """
        Получить резервы пары
        """
        try:
            # В реальной реализации здесь будет вызов getReserves()
            # Для демонстрации возвращаем случайные значения
            reserve0 = random.randint(1000, 1000000) * 10**18
            reserve1 = random.randint(1000, 1000000) * 10**18
            
            return (reserve0, reserve1)
            
        except Exception as e:
            logger.error(f"Error getting reserves for pair {pair_address}: {e}")
            return None
