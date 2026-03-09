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
    if (!dateStr || dateStr === 'Invalid Date') {
        return '未知';
    }
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            return '未知';
        }
        return date.toLocaleString('zh-CN');
    } catch (e) {
        return '未知';
    }
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
    
    if (!dailyData || dailyData.length === 0) {
        summaryContainer.innerHTML = '<div class="summary-card"><h3>暂无数据</h3></div>';
        return;
    }
    
    // 计算统计数据
    const latest = dailyData[0];
    const totalInflow = dailyData.reduce((sum, d) => sum + (d.total || 0), 0);
    const positiveDays = dailyData.filter(d => (d.total || 0) > 0).length;
    const negativeDays = dailyData.filter(d => (d.total || 0) < 0).length;
    
    const cards = [
        {
            title: '最新流入',
            value: latest.total || 0,
            class: (latest.total || 0) >= 0 ? 'positive' : 'negative'
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
    
    if (!dailyData || dailyData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="13">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = dailyData.map(row => {
        const cells = [
            row.date || '-',
            row.blackrock || 0,
            row.fidelity || 0,
            row.bitwise || 0,
            row.ark || 0,
            row.invesco || 0,
            row.franklin || 0,
            row.valkyrie || 0,
            row.vaneck || 0,
            row.wtree || 0,
            row.grayscale_gb || 0,
            row.grayscale_btc || 0,
            row.total || 0
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
        const { data, last_updated, server_time } = result;
        
        // 更新最后更新时间
        const updateEl = document.getElementById('last-update');
        if (updateEl) {
            updateEl.textContent = `最后更新: ${formatDate(last_updated)}`;
        }
        
        // 渲染数据
        if (data && data.daily_data) {
            renderSummary(data.daily_data);
            renderTable(data.daily_data);
        }
        
        // 显示服务器时间
        const countdownEl = document.getElementById('countdown');
        if (countdownEl && server_time) {
            countdownEl.textContent = `服务器时间: ${formatDate(server_time)}`;
        }
    } else {
        const updateEl = document.getElementById('last-update');
        if (updateEl) {
            updateEl.textContent = '数据加载失败';
        }
    }
}

// 初始化
async function init() {
    await updatePage();
    
    // 每 5 分钟自动刷新
    setInterval(updatePage, 5 * 60 * 1000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
