// Функции для управления harvester
function startHarvester() {
    fetch('/start_harvester', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'started') {
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            showNotification('Harvester запущен', 'success');
        } else if (data.status === 'already_running') {
            showNotification('Harvester уже работает', 'warning');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка запуска harvester', 'danger');
    });
}

function stopHarvester() {
    fetch('/stop_harvester', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'stopped') {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            showNotification('Harvester остановлен', 'info');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка остановки harvester', 'danger');
    });
}

// Обновление статуса
function updateStatus() {
    fetch('/status')
    .then(response => response.json())
    .then(data => {
        // Обновляем статус
        const statusText = document.getElementById('status-text');
        if (statusText) {
            if (data.running) {
                statusText.innerHTML = '<span class="text-success">Активен</span>';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                statusText.innerHTML = '<span class="text-secondary">Остановлен</span>';
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }
        
        // Обновляем счетчики
        const candidatesCount = document.getElementById('candidates-count');
        if (candidatesCount) {
            candidatesCount.textContent = data.candidates_found;
        }
        
        const transactionsCount = document.getElementById('transactions-count');
        if (transactionsCount) {
            transactionsCount.textContent = data.transactions_sent;
        }
        
        // Обновляем время последнего запуска
        const lastRun = document.getElementById('last-run');
        if (lastRun && data.last_run) {
            const date = new Date(data.last_run);
            lastRun.textContent = date.toLocaleString('ru-RU');
        }
    })
    .catch(error => {
        console.error('Error updating status:', error);
    });
}

// Обновление списка кандидатов
function updateCandidates() {
    fetch('/candidates')
    .then(response => response.json())
    .then(data => {
        const tbody = document.getElementById('candidates-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (data.candidates && data.candidates.length > 0) {
            data.candidates.forEach(candidate => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${candidate.pair}</td>
                    <td><code>${candidate.token}</code></td>
                    <td>${candidate.surplus}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="3" class="text-center text-muted">Кандидаты не найдены</td>';
            tbody.appendChild(row);
        }
    })
    .catch(error => {
        console.error('Error updating candidates:', error);
    });
}

// Показать уведомление
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Загружаем данные при загрузке страницы
    updateStatus();
    updateCandidates();
});
