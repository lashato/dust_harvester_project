import time
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'start_time': None,
            'total_candidates_found': 0,
            'total_candidates_executed': 0,
            'total_profit_eth': 0.0,
            'total_gas_spent_eth': 0.0,
            'execution_times': [],
            'errors': [],
            'pairs_checked': set(),
            'last_run_stats': {}
        }
    
    def start_session(self):
        """Начать новую сессию метрик"""
        self.metrics['start_time'] = datetime.now()
        logger.info("Metrics session started")
    
    def record_candidates_found(self, count: int):
        """Записать количество найденных кандидатов"""
        self.metrics['total_candidates_found'] += count
        self.metrics['last_run_stats']['candidates_found'] = count
    
    def record_candidate_executed(self, profit_eth: float, gas_cost_eth: float):
        """Записать выполненного кандидата"""
        self.metrics['total_candidates_executed'] += 1
        self.metrics['total_profit_eth'] += profit_eth
        self.metrics['total_gas_spent_eth'] += gas_cost_eth
    
    def record_execution_time(self, duration_seconds: float):
        """Записать время выполнения"""
        self.metrics['execution_times'].append(duration_seconds)
        
        # Оставляем только последние 100 записей
        if len(self.metrics['execution_times']) > 100:
            self.metrics['execution_times'] = self.metrics['execution_times'][-100:]
    
    def record_error(self, error_message: str, error_type: str = 'general'):
        """Записать ошибку"""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'type': error_type
        }
        self.metrics['errors'].append(error_record)
        
        # Оставляем только последние 50 ошибок
        if len(self.metrics['errors']) > 50:
            self.metrics['errors'] = self.metrics['errors'][-50:]
    
    def record_pair_checked(self, pair_address: str):
        """Записать проверенную пару"""
        self.metrics['pairs_checked'].add(pair_address)
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку метрик"""
        runtime = 0
        if self.metrics['start_time']:
            runtime = (datetime.now() - self.metrics['start_time']).total_seconds()
        
        avg_execution_time = 0
        if self.metrics['execution_times']:
            avg_execution_time = sum(self.metrics['execution_times']) / len(self.metrics['execution_times'])
        
        net_profit = self.metrics['total_profit_eth'] - self.metrics['total_gas_spent_eth']
        
        success_rate = 0
        if self.metrics['total_candidates_found'] > 0:
            success_rate = (self.metrics['total_candidates_executed'] / self.metrics['total_candidates_found']) * 100
        
        return {
            'runtime_seconds': runtime,
            'total_candidates_found': self.metrics['total_candidates_found'],
            'total_candidates_executed': self.metrics['total_candidates_executed'],
            'success_rate_percent': success_rate,
            'total_profit_eth': self.metrics['total_profit_eth'],
            'total_gas_spent_eth': self.metrics['total_gas_spent_eth'],
            'net_profit_eth': net_profit,
            'average_execution_time': avg_execution_time,
            'unique_pairs_checked': len(self.metrics['pairs_checked']),
            'error_count': len(self.metrics['errors']),
            'last_run_stats': self.metrics['last_run_stats']
        }
    
    def save_to_file(self, filename: str = 'metrics.json'):
        """Сохранить метрики в файл"""
        try:
            # Конвертируем set в list для JSON сериализации
            metrics_copy = self.metrics.copy()
            metrics_copy['pairs_checked'] = list(metrics_copy['pairs_checked'])
            
            if metrics_copy['start_time']:
                metrics_copy['start_time'] = metrics_copy['start_time'].isoformat()
            
            with open(filename, 'w') as f:
                json.dump(metrics_copy, f, indent=2)
            
            logger.info(f"Metrics saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving metrics to file: {e}")
    
    def load_from_file(self, filename: str = 'metrics.json'):
        """Загрузить метрики из файла"""
        try:
            with open(filename, 'r') as f:
                loaded_metrics = json.load(f)
            
            # Конвертируем обратно в нужные типы
            if 'pairs_checked' in loaded_metrics:
                loaded_metrics['pairs_checked'] = set(loaded_metrics['pairs_checked'])
            
            if loaded_metrics.get('start_time'):
                loaded_metrics['start_time'] = datetime.fromisoformat(loaded_metrics['start_time'])
            
            self.metrics.update(loaded_metrics)
            logger.info(f"Metrics loaded from {filename}")
        except Exception as e:
            logger.error(f"Error loading metrics from file: {e}")

# Глобальный экземпляр коллектора метрик
metrics = MetricsCollector()
