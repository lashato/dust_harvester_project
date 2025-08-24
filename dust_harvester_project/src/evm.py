import asyncio
from web3 import Web3
from eth_account import Account
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class EVMConnection:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
        self.account = None
        
        if settings.PRIVATE_KEY:
            self.account = Account.from_key(settings.PRIVATE_KEY)
            
    async def get_latest_block(self):
        """Получить последний блок"""
        try:
            return self.w3.eth.get_block('latest')
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return None
    
    async def get_balance(self, address):
        """Получить баланс адреса"""
        try:
            return self.w3.eth.get_balance(address)
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return 0
    
    async def send_transaction(self, transaction_data):
        """Отправить транзакцию"""
        if settings.DRY_RUN:
            logger.info(f"DRY RUN: Would send transaction: {transaction_data}")
            return {"hash": "0x" + "0" * 64}  # Fake transaction hash
        
        if not self.account:
            raise ValueError("No private key configured for live transactions")
        
        try:
            # Получаем nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Добавляем nonce к транзакции
            transaction_data['nonce'] = nonce
            
            # Подписываем транзакцию
            signed_txn = self.w3.eth.account.sign_transaction(transaction_data, self.account.key)
            
            # Отправляем транзакцию
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return {"hash": tx_hash.hex()}
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            raise
    
    async def call_contract(self, contract_address, function_signature, *args):
        """Вызов функции контракта"""
        try:
            # Упрощенная реализация для примера
            # В реальности нужно использовать ABI контракта
            result = self.w3.eth.call({
                'to': contract_address,
                'data': function_signature
            })
            return result
        except Exception as e:
            logger.error(f"Error calling contract {contract_address}: {e}")
            return None

# Глобальный экземпляр подключения
evm = EVMConnection()
