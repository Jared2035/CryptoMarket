/**
 * CryptoMarket 前端应用
 */

// API 基础 URL
const API_BASE = '';

// 格式化数字
function formatNumber(num) {
    if (num === 0) return '0.0';
    const formatted = num.toFixed(1);
    return num > 0 ? `+${formatted}` : formatted;
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
}

// 获取数据
async function fetchData() {
    try {
        const response = await fetch('/api/btc-etf-flow');
        if (!response.ok) throw new Error('获取数据失败');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// 渲染汇总卡片
function renderSummary(dailyData) {
    const summaryContainer = document.getElementById('summary');
    
    // 计算统计数据
    const latest = dailyData[0];
    const totalInflow = dailyData.reduce((sum, d) => sum + d.total, 0);
    const positiveDays = dailyData.filter(d => d.total > 0).length;
    const negativeDays = dailyData.filter(d => d.total < 0).length;
    
    const cards = [
        {
            title: '最新流入',
            value: latest.total,
            class: latest.total >= 0 ? 'positive' : 'negative'
        },
        {
            title: '累计流入',
            value: totalInflow,
            class: totalInflow >= 0 ? 'positive' : 'negative'
        },
        {
            title: '流入天数',
            value: positiveDays,
            class: 'positive'
        },
        {
            title: '流出天数',
            value: negativeDays,
            class: 'negative'
        }
    ];
    
    summaryContainer.innerHTML = cards.map(card => `
        <div class="summary-card">
            <h3>${card.title}</h3>
            <div class="value ${card.class}">${formatNumber(card.value)}M</div>
        </div>
    `).join('');
}

// 渲染表格
function renderTable(dailyData) {
    const tbody = document.getElementById('table-body');
    
    tbody.innerHTML = dailyData.map(row => {
        const cells = [
            row.date,
            row.blackrock,
            row.fidelity,
            row.bitwise,
            row.ark,
            row.invesco,
            row.franklin,
            row.valkyrie,
            row.vaneck,
            row.wtree,
            row.grayscale_gb,
            row.grayscale_btc,
            row.total
        ];
        
        return `
            <tr>
                ${cells.map((cell, index) => {
                    if (index === 0) return `<td>${cell}</td>`;
                    const value = parseFloat(cell) || 0;
                    const className = value > 0 ? 'positive' : value < 0 ? 'negative' : '';
                    return `<td class="${className}">${formatNumber(value)}</td>`;
                }).join('')}
            </tr>
        `;
    }).join('');
}

// 更新页面
async function updatePage() {
    const result = await fetchData();
    
    if (result && result.data) {
        const { data, last_update, next_update_in } = result;
        
        // 更新最后更新时间
        document.getElementById('last-update').textContent = 
            `最后更新: ${formatDate(last_update)}`;
        
        // 渲染数据
        renderSummary(data.daily_data);
        renderTable(data.daily_data);
        
        // 开始倒计时
        startCountdown(Math.floor(next_update_in));
    } else {
        document.getElementById('last-update').textContent = '数据加载失败';
    }
}

// 倒计时
function startCountdown(seconds) {
    const countdownEl = document.getElementById('countdown');
    
    const updateCountdown = () => {
        if (seconds <= 0) {
            countdownEl.textContent = '更新中...';
            updatePage();
            return;
        }
        
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        countdownEl.textContent = `下次更新: ${mins}:${secs.toString().padStart(2, '0')}`;
        seconds--;
        setTimeout(updateCountdown, 1000);
    };
    
    updateCountdown();
}

// 初始化
async function init() {
    await updatePage();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
