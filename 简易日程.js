// ==UserScript==
// @name         日程管理器（AI自动化脚本版）
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  多视图日程 + 智谱AI自动修改日程，支持标签和子任务
// @author       豆包
// @match        *://*/*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @require      https://cdn.tailwindcss.com
// @run-at       document-end
// @license      MIT
// ==/UserScript==

(function() {
    'use strict';

    // ===================== 【照搬你的智谱AI核心配置】 =====================
    const API = {
        SYNC: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        ASYNC: "https://open.bigmodel.cn/api/paas/v4/async/chat/completions",
        RESULT: "https://open.bigmodel.cn/api/paas/v4/async-result/"
    };
    const MODEL_LIST = [
        { label: "GLM-4.7-Flash（文本）", value: "glm-4.7-flash" },
        { label: "GLM-4V-Flash（免费视觉）", value: "glm-4v-flash" },
        { label: "GLM-4.6V-Flash（视觉图像）", value: "glm-4.6v-flash" },
        { label: "GLM-4.1V-Thinking-Flash（视觉图像）", value: "glm-4.1v-thinking-flash" },
        { label: "GLM-4-Flash", value: "glm-4-flash-250414" },
    ];
    const STORAGE = {
        API_KEY: "ZHIPU_API_KEY", MODEL: "ZHIPU_MODEL", TEMP: "ZHIPU_TEMP",
        WIDGET_STATE: "WIDGET_STATE", WIDGET_POS: "WIDGET_POS",
    };
    // =====================================================================

    // ===================== 日程AI固定配置（自动修改日程核心） =====================
    const SCHEDULE_AI_PROMPT = `你是专业的日程管理助手，只返回标准JSON格式，禁止任何解释、文字、markdown。
    支持的指令类型：
    1. add：添加日程 → {"type":"add","data":{"content":"日程内容","time":"14:00"}}
    2. delete：删除日程 → {"type":"delete","keyword":"关键词"} 或 {"type":"delete","id":"日程ID"}
    3. complete：标记完成 → {"type":"complete","id":"日程ID"} 或 {"type":"complete"}(全部完成)
    4. clear：清空所有 → {"type":"clear"}
    严格按照格式返回纯JSON！`;
    // =====================================================================

    // 全局状态
    let isRequesting = false;
    let schedules = [];
    let recycleBin = [];
    let currentDate = new Date();
    let currentView = 'month'; // 视图模式：day, week, month

    // ===================== 样式（深色主题） =====================
    GM_addStyle(`
        #calendar-container { backdrop-filter: blur(8px); }
        .calendar-day { transition: all 0.2s; }
        .calendar-day:hover { background: #2d2d3f; }
        .loading-spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #2d2d3f; }
        ::-webkit-scrollbar-thumb { background: #444; border-radius: 3px; }
        .tag-important-urgent { background: #ef4444; }
        .tag-important { background: #f59e0b; }
        .tag-urgent { background: #3b82f6; }
        .tag-normal { background: #10b981; }
        .subtask { margin-left: 12px; font-size: 9px; opacity: 0.8; }
    `);

    // ===================== 1. 初始化UI（月视图+AI输入框） =====================
    function createUI() {
        const html = `
        <div id="calendar-container" class="fixed top-6 right-6 w-[450px] h-[700px] rounded-2xl flex flex-col z-[9999] border border-gray-700 overflow-hidden bg-[#1e1e2e] text-gray-200 shadow-xl">
            <!-- 拖拽栏 -->
            <div id="drag-handle" class="px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex justify-between items-center cursor-move shrink-0">
                <span class="text-sm font-semibold">📅 日程管理器</span>
                <div class="flex gap-2">
                    <button id="minimize-btn" class="hover:bg-white/20 p-1 rounded text-xs">−</button>
                    <button id="close-btn" class="hover:bg-white/20 p-1 rounded text-xs">×</button>
                </div>
            </div>

            <!-- 智谱AI配置区 -->
            <div class="p-3 border-b border-gray-700 bg-[#161622] shrink-0">
                <div class="grid grid-cols-2 gap-2 mb-2">
                    <input id="zhipu-api-key" placeholder="输入智谱API Key" class="w-full px-3 py-2 text-xs border border-gray-600 rounded-lg bg-[#252535] text-white">
                    <select id="zhipu-model" class="px-3 py-2 text-xs border border-gray-600 rounded-lg bg-[#252535] text-white">
                        ${MODEL_LIST.map(m => `<option value="${m.value}">${m.label}</option>`).join('')}
                    </select>
                </div>
                <!-- AI指令输入 -->
                <div class="flex gap-2">
                    <input id="ai-input" placeholder="输入AI指令：添加下午3点开会 / 删除所有会议..." class="flex-1 px-3 py-2 text-xs border border-gray-600 rounded-lg bg-[#252535] text-white">
                    <button id="ai-send-btn" class="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs">执行AI</button>
                </div>
            </div>

            <!-- 视图切换和日期导航 -->
            <div class="p-3 flex justify-between items-center border-b border-gray-700 shrink-0">
                <div class="flex gap-2">
                    <button id="view-day" class="px-2 py-1 bg-[#252535] rounded text-xs">日</button>
                    <button id="view-week" class="px-2 py-1 bg-[#252535] rounded text-xs">周</button>
                    <button id="view-month" class="px-2 py-1 bg-[#252535] rounded text-xs">月</button>
                </div>
                <div class="flex items-center gap-2">
                    <button id="prev-period" class="px-2 py-1 bg-[#252535] rounded text-xs">←</button>
                    <span id="period-title" class="text-sm font-medium"></span>
                    <button id="next-period" class="px-2 py-1 bg-[#252535] rounded text-xs">→</button>
                </div>
            </div>

            <!-- 星期栏 -->
            <div id="week-header" class="grid grid-cols-7 gap-1 px-2 py-2 text-xs text-gray-400 text-center shrink-0">
                <div>日</div><div>一</div><div>二</div><div>三</div><div>四</div><div>五</div><div>六</div>
            </div>

            <!-- 日历网格 -->
            <div id="calendar-grid" class="grid grid-cols-7 gap-1 p-2 flex-1 overflow-y-auto"></div>

            <!-- 底部操作 -->
            <div class="p-3 border-t border-gray-700 flex gap-2 shrink-0">
                <button id="add-schedule-btn" class="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs">+ 添加日程</button>
                <button id="edit-schedule-btn" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">编辑日程</button>
                <button id="import-btn" class="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">导入</button>
                <button id="export-btn" class="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-xs">导出</button>
                <button id="recycle-bin-btn" class="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-xs">回收站</button>
                <button id="clear-all-btn" class="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs">清空所有</button>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    }

    // ===================== 2. 拖拽/最小化/存储（照搬你的逻辑） =====================
    function initDrag() {
        const dragHandle = document.getElementById('drag-handle');
        const widget = document.getElementById('calendar-container');
        let isDragging = false, startX, startY, startLeft, startTop;

        const savedPos = GM_getValue(STORAGE.WIDGET_POS, null);
        if (savedPos) {
            widget.style.left = savedPos.left + 'px';
            widget.style.top = savedPos.top + 'px';
            widget.style.bottom = 'auto';
            widget.style.right = 'auto';
        }

        dragHandle.addEventListener('mousedown', (e) => {
            isDragging = true;
            const rect = widget.getBoundingClientRect();
            startX = e.clientX; startY = e.clientY;
            startLeft = rect.left; startTop = rect.top;
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            widget.style.left = startLeft + dx + 'px';
            widget.style.top = startTop + dy + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                GM_setValue(STORAGE.WIDGET_POS, {
                    left: widget.offsetLeft,
                    top: widget.offsetTop
                });
            }
        });
    }

    function initMinimize() {
        const btn = document.getElementById('minimize-btn');
        const widget = document.getElementById('calendar-container');
        btn.addEventListener('click', () => {
            widget.classList.toggle('h-[700px]');
            widget.classList.toggle('h-12');
        });
    }

    function initStorage() {
        const apiKey = document.getElementById('zhipu-api-key');
        const model = document.getElementById('zhipu-model');
        apiKey.value = GM_getValue(STORAGE.API_KEY, '');
        model.value = GM_getValue(STORAGE.MODEL, MODEL_LIST[0].value);

        apiKey.addEventListener('input', () => GM_setValue(STORAGE.API_KEY, apiKey.value.trim()));
        model.addEventListener('change', () => GM_setValue(STORAGE.MODEL, model.value));
    }

    // ===================== 3. 日程核心功能（增删改查+本地存储） =====================
    function getSchedules() {
        return GM_getValue('schedules', []);
    }
    function saveSchedules(data) {
        GM_setValue('schedules', data);
        schedules = data;
        renderCalendar();
    }
    function getRecycleBin() {
        return GM_getValue('recycleBin', []);
    }
    function saveRecycleBin(data) {
        GM_setValue('recycleBin', data);
        recycleBin = data;
    }
    function generateId() {
        return Date.now() + Math.random().toString(36).slice(2, 8);
    }

    // 渲染日历
    function renderCalendar() {
        const grid = document.getElementById('calendar-grid');
        const title = document.getElementById('period-title');
        const weekHeader = document.getElementById('week-header');
        schedules = getSchedules();
        recycleBin = getRecycleBin();

        switch (currentView) {
            case 'day':
                renderDayView();
                break;
            case 'week':
                renderWeekView();
                break;
            case 'month':
                renderMonthView();
                break;
        }

        function renderDayView() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            const day = currentDate.getDate();
            const dateStr = `${year}-${String(month+1).padStart(2,0)}-${String(day).padStart(2,0)}`;
            const daySchedules = schedules.filter(s => s.date === dateStr);
            const today = new Date();
            const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();

            title.textContent = `${year}年${month+1}月${day}日`;
            weekHeader.style.display = 'none';
            grid.style.gridTemplateColumns = '1fr';
            grid.innerHTML = '';

            const cell = document.createElement('div');
            cell.className = `calendar-day p-3 rounded bg-[#252535] min-h-[500px] relative ${isToday ? 'ring-1 ring-blue-500' : ''}`;
            cell.innerHTML = `
                <div class="text-sm font-medium ${isToday ? 'text-blue-400' : 'text-gray-300'}">${day}日</div>
                <div class="mt-2 space-y-2 max-h-[450px] overflow-y-auto">
                    ${daySchedules.length > 0 ? daySchedules.map(s => `
                        <div class="text-xs px-2 py-1 rounded ${s.completed ? 'bg-gray-600 line-through' : 'bg-blue-500/30'}" data-id="${s.id}">
                            <div class="flex justify-between items-center">
                                <span>${s.time} ${s.content}</span>
                                ${s.tag ? `<span class="tag-${s.tag} text-[9px] px-1 py-0.5 rounded">${getTagName(s.tag)}</span>` : ''}
                            </div>
                            ${s.subtasks && s.subtasks.length > 0 ? `
                                <div class="subtasks mt-1 space-y-1">
                                    ${s.subtasks.map(st => `
                                        <div class="subtask px-1 py-0.5 rounded ${st.completed ? 'bg-gray-500 line-through' : 'bg-blue-400/30'}" data-subtask-id="${st.id}">
                                            ${st.content}
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('') : '<div class="text-gray-400 text-xs">无日程</div>'}
                </div>
            `;
            grid.appendChild(cell);
        }

        function renderWeekView() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            const day = currentDate.getDate();
            const startOfWeek = new Date(year, month, day - currentDate.getDay());
            const today = new Date();

            title.textContent = `${year}年${month+1}月第${Math.ceil((day + startOfWeek.getDay()) / 7)}周`;
            weekHeader.style.display = 'grid';
            grid.style.gridTemplateColumns = 'repeat(7, 1fr)';
            grid.innerHTML = '';

            for (let i = 0; i < 7; i++) {
                const currentDay = new Date(startOfWeek);
                currentDay.setDate(startOfWeek.getDate() + i);
                const dayStr = currentDay.getDate();
                const dateStr = `${currentDay.getFullYear()}-${String(currentDay.getMonth()+1).padStart(2,0)}-${String(dayStr).padStart(2,0)}`;
                const daySchedules = schedules.filter(s => s.date === dateStr);
                const isToday = dayStr === today.getDate() && currentDay.getMonth() === today.getMonth() && currentDay.getFullYear() === today.getFullYear();

                const cell = document.createElement('div');
                cell.className = `calendar-day p-1 rounded bg-[#252535] min-h-[120px] relative ${isToday ? 'ring-1 ring-blue-500' : ''}`;
                cell.innerHTML = `
                    <div class="text-xs font-medium ${isToday ? 'text-blue-400' : 'text-gray-300'}">${dayStr}</div>
                    <div class="mt-1 space-y-1 max-h-[100px] overflow-y-auto">
                        ${daySchedules.map(s => `
                            <div class="text-[10px] px-1 py-0.5 rounded ${s.completed ? 'bg-gray-600 line-through' : 'bg-blue-500/30'}" data-id="${s.id}">
                                ${s.time} ${s.content}
                            </div>
                        `).join('')}
                    </div>
                `;
                grid.appendChild(cell);
            }
        }

        function renderMonthView() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            const firstDay = new Date(year, month, 1).getDay();
            const lastDate = new Date(year, month + 1, 0).getDate();
            const today = new Date();

            title.textContent = `${year}年${month+1}月`;
            weekHeader.style.display = 'grid';
            grid.style.gridTemplateColumns = 'repeat(7, 1fr)';
            grid.innerHTML = '';

            // 填充日期
            for (let i = 0; i < firstDay; i++) addDayCell('', false);
            for (let d = 1; d <= lastDate; d++) addDayCell(d, true);

            function addDayCell(day, isCurrent) {
                const dateStr = day ? `${year}-${String(month+1).padStart(2,0)}-${String(day).padStart(2,0)}` : '';
                const daySchedules = schedules.filter(s => s.date === dateStr);
                const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();

                const cell = document.createElement('div');
                cell.className = `calendar-day p-1 rounded bg-[#252535] min-h-[80px] relative ${isToday ? 'ring-1 ring-blue-500' : ''}`;
                cell.innerHTML = `
                    <div class="text-xs font-medium ${isToday ? 'text-blue-400' : 'text-gray-300'}">${day || ''}</div>
                    <div class="mt-1 space-y-1 max-h-[60px] overflow-y-auto">
                        ${daySchedules.map(s => `
                            <div class="text-[10px] px-1 py-0.5 rounded ${s.completed ? 'bg-gray-600 line-through' : 'bg-blue-500/30'}" data-id="${s.id}">
                                ${s.time} ${s.content}
                            </div>
                        `).join('')}
                    </div>
                `;
                grid.appendChild(cell);
            }
        }
    }

    // 获取标签名称
    function getTagName(tag) {
        const tagMap = {
            'important-urgent': '重要且紧急',
            'important': '重要',
            'urgent': '紧急',
            'normal': '一般'
        };
        return tagMap[tag] || tag;
    }

    // 绑定日程操作
    function bindScheduleEvents() {
        // 视图切换
        document.getElementById('view-day').onclick = () => { currentView = 'day'; renderCalendar(); };
        document.getElementById('view-week').onclick = () => { currentView = 'week'; renderCalendar(); };
        document.getElementById('view-month').onclick = () => { currentView = 'month'; renderCalendar(); };

        // 周期切换
        document.getElementById('prev-period').onclick = () => {
            switch (currentView) {
                case 'day':
                    currentDate.setDate(currentDate.getDate() - 1);
                    break;
                case 'week':
                    currentDate.setDate(currentDate.getDate() - 7);
                    break;
                case 'month':
                    currentDate.setMonth(currentDate.getMonth() - 1);
                    break;
            }
            renderCalendar();
        };
        document.getElementById('next-period').onclick = () => {
            switch (currentView) {
                case 'day':
                    currentDate.setDate(currentDate.getDate() + 1);
                    break;
                case 'week':
                    currentDate.setDate(currentDate.getDate() + 7);
                    break;
                case 'month':
                    currentDate.setMonth(currentDate.getMonth() + 1);
                    break;
            }
            renderCalendar();
        };

        // 添加日程
        document.getElementById('add-schedule-btn').onclick = () => {
            const content = prompt('日程内容：');
            if (!content) return;
            const time = prompt('时间（如14:00）：', '');
            const tag = prompt('标签（重要且紧急/重要/紧急/一般）：', '一般');
            const tagMap = {
                '重要且紧急': 'important-urgent',
                '重要': 'important',
                '紧急': 'urgent',
                '一般': 'normal'
            };
            const newSchedule = {
                id: generateId(),
                content, time,
                date: currentDate.toISOString().split('T')[0],
                completed: false,
                tag: tagMap[tag] || 'normal',
                subtasks: []
            };
            saveSchedules([...getSchedules(), newSchedule]);
        };

        // 编辑日程
        document.getElementById('edit-schedule-btn').onclick = () => {
            const id = prompt('输入要编辑的日程ID：');
            if (!id) return;
            const list = getSchedules();
            const schedule = list.find(s => s.id === id);
            if (!schedule) {
                alert('未找到该日程');
                return;
            }
            const content = prompt('日程内容：', schedule.content);
            if (content !== null) schedule.content = content;
            const time = prompt('时间（如14:00）：', schedule.time);
            if (time !== null) schedule.time = time;
            const tag = prompt('标签（重要且紧急/重要/紧急/一般）：', getTagName(schedule.tag));
            if (tag !== null) {
                const tagMap = {
                    '重要且紧急': 'important-urgent',
                    '重要': 'important',
                    '紧急': 'urgent',
                    '一般': 'normal'
                };
                schedule.tag = tagMap[tag] || 'normal';
            }
            const addSubtask = confirm('是否添加子任务？');
            if (addSubtask) {
                const subtaskContent = prompt('子任务内容：');
                if (subtaskContent) {
                    if (!schedule.subtasks) schedule.subtasks = [];
                    schedule.subtasks.push({
                        id: generateId(),
                        content: subtaskContent,
                        completed: false
                    });
                }
            }
            saveSchedules(list);
        };

        // 导入日程
        document.getElementById('import-btn').onclick = () => {
            const jsonStr = prompt('请粘贴JSON格式的日程数据：');
            if (!jsonStr) return;
            try {
                const importedSchedules = JSON.parse(jsonStr);
                if (Array.isArray(importedSchedules)) {
                    const currentSchedules = getSchedules();
                    saveSchedules([...currentSchedules, ...importedSchedules]);
                    alert('导入成功！');
                } else {
                    alert('无效的JSON格式');
                }
            } catch (e) {
                alert('导入失败：' + e.message);
            }
        };

        // 导出日程
        document.getElementById('export-btn').onclick = () => {
            const schedules = getSchedules();
            const jsonStr = JSON.stringify(schedules, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `schedules_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        };

        // 回收站
        document.getElementById('recycle-bin-btn').onclick = () => {
            const bin = getRecycleBin();
            if (bin.length === 0) {
                alert('回收站为空');
                return;
            }
            const action = prompt('回收站操作：\n1. 查看所有 (输入 1)\n2. 恢复所有 (输入 2)\n3. 清空回收站 (输入 3)');
            switch (action) {
                case '1':
                    alert(JSON.stringify(bin, null, 2));
                    break;
                case '2':
                    if (confirm('确定恢复所有日程？')) {
                        const currentSchedules = getSchedules();
                        saveSchedules([...currentSchedules, ...bin]);
                        saveRecycleBin([]);
                        alert('恢复成功！');
                    }
                    break;
                case '3':
                    if (confirm('确定清空回收站？')) {
                        saveRecycleBin([]);
                        alert('回收站已清空');
                    }
                    break;
            }
        };

        // 清空所有
        document.getElementById('clear-all-btn').onclick = () => {
            if (confirm('确定清空所有日程？')) {
                const currentSchedules = getSchedules();
                const bin = getRecycleBin();
                saveRecycleBin([...bin, ...currentSchedules]);
                saveSchedules([]);
                alert('所有日程已移至回收站');
            }
        };
    }

    // ===================== 4. 智谱AI请求 + 自动执行日程指令 =====================
    function cleanJson(str) {
        return str.replace(/```json|```/g, '').trim();
    }

    // 发送AI请求（完全适配你的智谱接口）
    async function sendAIScheduleCommand() {
        const apiKey = document.getElementById('zhipu-api-key').value.trim();
        const userPrompt = document.getElementById('ai-input').value.trim();
        const btn = document.getElementById('ai-send-btn');

        if (!apiKey) return alert('请输入智谱API Key');
        if (!userPrompt) return alert('请输入AI指令');
        if (isRequesting) return;

        isRequesting = true;
        btn.innerHTML = '<span class="loading-spin">⏳</span>';
        btn.disabled = true;

        try {
            const res = await fetch(API.SYNC, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: document.getElementById('zhipu-model').value,
                    temperature: 0.1,
                    messages: [
                        { role: 'system', content: SCHEDULE_AI_PROMPT },
                        { role: 'user', content: userPrompt }
                    ],
                    response_format: { type: "json_object" }
                })
            });

            const data = await res.json();
            const result = cleanJson(data.choices[0].message.content);
            const command = JSON.parse(result);

            // 🔥 核心：执行AI返回的指令，自动修改日程
            executeScheduleCommand(command);
            alert('AI执行成功！');
            document.getElementById('ai-input').value = '';
        } catch (e) {
            alert('AI执行失败：' + e.message);
            console.error(e);
        } finally {
            isRequesting = false;
            btn.innerHTML = '执行AI';
            btn.disabled = false;
        }
    }

    // 执行日程指令（自动增删改查）
    function executeScheduleCommand(cmd) {
        let list = getSchedules();
        let bin = getRecycleBin();
        switch (cmd.type) {
            case 'add':
                list.push({
                    id: generateId(),
                    content: cmd.data.content,
                    time: cmd.data.time || '',
                    date: new Date().toISOString().split('T')[0],
                    completed: false,
                    tag: cmd.data.tag || 'normal',
                    subtasks: cmd.data.subtasks || []
                });
                break;
            case 'delete':
                if (cmd.id) {
                    const scheduleToDelete = list.find(s => s.id === cmd.id);
                    if (scheduleToDelete) {
                        bin.push(scheduleToDelete);
                        list = list.filter(s => s.id !== cmd.id);
                    }
                }
                if (cmd.keyword) {
                    const schedulesToDelete = list.filter( => .content.includes(cmd.keyword));
                    bin.push(...schedulesToDelete);
                    list = list.filter( => !.content.includes(cmd.keyword));
                }
                saveRecycleBin(bin);
                break;
            case 'complete':
                if (cmd.id) {
                    const schedule = list.find( => .id === cmd.id);
                    if (schedule) schedule.completed = true;
                } else {
                    list.forEach( => .completed = true);
                }
                break;
            case 'clear':
                bin.push(...list);
                list = [];
                saveRecycleBin(bin);
                break;
            case 'edit':
                if (cmd.id) {
                    const schedule = list.find( => .id === cmd.id);
                    if (schedule) {
                        if (cmd.data.content) schedule.content = cmd.data.content;
                        if (cmd.data.time) schedule.time = cmd.data.time;
                        if (cmd.data.tag) schedule.tag = cmd.data.tag;
                        if (cmd.data.subtasks) schedule.subtasks = cmd.data.subtasks;
                    }
                }
                break;
        }
        saveSchedules(list);
    }

    // ===================== 5. 初始化所有功能 =====================
    function init() {
        createUI();
        initDrag();
        initMinimize();
        initStorage();
        renderCalendar();
        bindScheduleEvents();

        // 绑定AI发送
        document.getElementById('ai-send-btn').onclick = sendAIScheduleCommand;
        document.getElementById('close-btn').onclick = () => document.getElementById('calendar-container').remove();
    }

    window.addEventListener('load', init);
})();
