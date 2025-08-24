from abc import ABC, abstractmethod
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class BaseIncentiveStrategy(ABC):
    """Базовый класс для стратегий поиска арбитражных возможностей"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    async def discover_candidates(self) -> List[Tuple[str, str, float]]:
        """
        Поиск кандидатов для арбитража
        
        Returns:
            List[Tuple[str, str, float]]: Список кортежей (pair_address, token_address, surplus_amount)
        """
        pass
    
    @abstractmethod
    async def execute_candidate(self, candidate: Tuple[str, str, float]) -> bool:
        """
        Выполнить арбитраж для кандидата
        
        Args:
            candidate: Кортеж (pair_address, token_address, surplus_amount)
            
        Returns:
            bool: True если транзакция была успешно отправлена
        """
        pass
    
    async def validate_candidate(self, candidate: Tuple[str, str, float]) -> bool:
        """
        Валидировать кандидата перед выполнением
        
        Args:
            candidate: Кортеж (pair_address, token_address, surplus_amount)
            
        Returns:
            bool: True если кандидат валиден
        """
        try:
            pair_address, token_address, surplus = candidate
            
            # Базовые проверки
            if not pair_address or not token_address:
                return False
            
            if surplus <= 0:
                return False
            
            # Проверка формата адресов (упрощенная)
            if not (pair_address.startswith('0x') and len(pair_address) == 42):
                return False
            
            if not (token_address.startswith('0x') and len(token_address) == 42):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating candidate {candidate}: {e}")
            return False
    
    def get_strategy_info(self) -> dict:
        """Получить информацию о стратегии"""
        return {
            'name': self.name,
            'description': self.__doc__ or 'No description available'
        }
