import os
from dataclasses import dataclass

@dataclass
class Settings:
    # Основные настройки
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "56"))  # BSC mainnet (дешевле газ!)
    RPC_URL: str = os.getenv("RPC_URL", "https://bsc-dataseed1.binance.org/")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    
    # Параметры поиска
    MAX_PAIRS: int = int(os.getenv("MAX_PAIRS", "100"))
    MIN_PROFIT_ETH: float = float(os.getenv("MIN_PROFIT_ETH", "0.001"))
    
    # Настройки газа
    GAS_LIMIT: int = int(os.getenv("GAS_LIMIT", "300000"))
    GAS_PRICE_GWEI: int = int(os.getenv("GAS_PRICE_GWEI", "3"))  # Намного дешевле на BSC!
    GAS_MULTIPLIER: float = float(os.getenv("GAS_MULTIPLIER", "1.2"))
    
    # Адреса контрактов PancakeSwap на BSC
    UNISWAP_V2_FACTORY: str = os.getenv("UNISWAP_V2_FACTORY", "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73")
    UNISWAP_V2_ROUTER: str = os.getenv("UNISWAP_V2_ROUTER", "0x10ED43C718714eb63d5aA57B78B54704E256024E")
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __post_init__(self):
        """Валидация настроек после инициализации"""
        if not self.PRIVATE_KEY and not self.DRY_RUN:
            raise ValueError("PRIVATE_KEY требуется для LIVE режима")
        
        if self.MIN_PROFIT_ETH <= 0:
            raise ValueError("MIN_PROFIT_ETH должен быть больше 0")

# Глобальный экземпляр настроек
settings = Settings()
