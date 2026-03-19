// ==UserScript==
// @name         深色月视图日程管理器(仿截图版)
// @namespace    http://tampermonkey.net/
// @version      3.0
// @description  仿滴答清单风格的深色月视图日程管理器，支持AI自动化
// @author       豆包
// @match        *://*/*
// @grant        GM_addStyle
// @grant        GM_setValue
// @grant        GM_getValue
// @run-at       document-end
// @license      MIT
// ==/UserScript==

// ===================== 【AI配置区 - 请自行修改】 =====================
const AI_CONFIG = {
  API_URL: "https://api.openai.com/v1/chat/completions", // AI接口地址(兼容OpenAI格式)
  API_KEY: "你的AI密钥", // 填写你的AI API Key
  MODEL: "gpt-3.5-turbo", // AI模型名称
};
// =====================================================================

(function () {
  "use strict";

  // 注入自定义样式（完全对齐截图风格）
  GM_addStyle(`
    /* 全局容器 */
    #calendar-container {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #1e1e2e;
      z-index: 999998;
      color: #e0e0e0;
      font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
      display: flex;
      flex-direction: column;
    }
    /* 顶部栏 */
    #calendar-header {
      display: flex;
      align-items: center;
      padding: 12px 20px;
      border-bottom: 1px solid #2d2d3f;
      gap: 16px;
    }
    .header-icon {
      font-size: 20px;
      cursor: pointer;
      color: #888;
    }
    .header-icon:hover {
      color: #e0e0e0;
    }
    #month-title {
      font-size: 18px;
      font-weight: 500;
    }
    .header-actions {
      margin-left: auto;
      display: flex;
      gap: 12px;
      align-items: center;
    }
    .header-btn {
      background: #2d2d3f;
      border: none;
      color: #e0e0e0;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
    }
    .header-btn:hover {
      background: #3d3d5f;
    }
    .view-toggle {
      display: flex;
      gap: 4px;
      background: #2d2d3f;
      padding: 4px;
      border-radius: 6px;
    }
    .view-btn {
      background: transparent;
      border: none;
      color: #888;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
    }
    .view-btn.active {
      background: #409eff;
      color: #fff;
    }
    .month-nav {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .month-arrow {
      background: transparent;
      border: none;
      color: #888;
      font-size: 16px;
      cursor: pointer;
    }
    .month-arrow:hover {
      color: #e0e0e0;
    }
    /* 主内容区：侧边栏+月历 */
    #calendar-main {
      flex: 1;
      display: flex;
      overflow: hidden;
    }
    /* 侧边栏 */
    #sidebar {
      width: 48px;
      background: #161622;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px 0;
      gap: 24px;
      border-right: 1px solid #2d2d3f;
    }
    .sidebar-icon {
      font-size: 20px;
      color: #888;
      cursor: pointer;
    }
    .sidebar-icon.active, .sidebar-icon:hover {
      color: #409eff;
    }
    /* 月历区域 */
    #calendar-content {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
    }
    /* 月历表头（星期） */
    #calendar-weekdays {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
      margin-bottom: 8px;
    }
    .weekday {
      text-align: center;
      font-size: 14px;
      color: #888;
      padding: 8px 0;
    }
    /* 月历网格 */
    #calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      grid-template-rows: repeat(6, 120px);
      gap: 8px;
    }
    .calendar-day {
      background: #252535;
      border-radius: 8px;
      padding: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .day-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .day-number {
      font-size: 14px;
      font-weight: 500;
    }
    .day-number.today {
      background: #409eff;
      color: #fff;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .day-festival {
      font-size: 12px;
      color: #2ea043;
    }
    .day-schedules {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .schedule-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 6px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
    }
    .schedule-item:hover {
      opacity: 0.8;
    }
    .schedule-checkbox {
      width: 12px;
      height: 12px;
      accent-color: #2ea043;
    }
    .schedule-time {
      color: #aaa;
      font-size: 11px;
    }
    .schedule-content {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .schedule-item.completed .schedule-content {
      text-decoration: line-through;
      color: #666;
    }
    /* 底部栏 */
    #calendar-footer {
      padding: 12px 20px;
      border-top: 1px solid #2d2d3f;
      display: flex;
      justify-content: center;
      gap: 16px;
    }
    .footer-view-btn {
      background: transparent;
      border: none;
      color: #888;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
    }
    .footer-view-btn.active {
      color: #409eff;
      font-weight: 500;
    }
    .upgrade-btn {
      position: absolute;
      bottom: 60px;
      right: 20px;
      background: #ff9f43;
      color: #fff;
      border: none;
      padding: 8px 16px;
      border-radius: 20px;
      cursor: pointer;
      font-size: 12px;
    }
    /* 滚动条美化 */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #2d2d3f;
    }
    ::-webkit-scrollbar-thumb {
      background: #444;
      border-radius: 3px;
    }
  `);

  // 核心数据类
  class CalendarManager {
    constructor() {
      this.schedules = this.getLocalSchedules();
      this.currentDate = new Date();
      this.currentView = "month"; // 默认月视图
      this.initUI();
      this.bindEvent();
      this.renderCalendar();
    }

    // 读取本地存储
    getLocalSchedules() {
      return GM_getValue("schedules", []);
    }
    // 保存本地存储
    saveLocalSchedules() {
      GM_setValue("schedules", this.schedules);
    }
    // 生成ID
    generateId() {
      return Date.now() + Math.random().toString(36).substr(2, 5);
    }

    // 初始化UI
    initUI() {
      const html = `
        <div id="calendar-container">
          <!-- 顶部栏 -->
          <div id="calendar-header">
            <span class="header-icon">📅</span>
            <span id="month-title">${this.getMonthTitle()}</span>
            <div class="header-actions">
              <button class="header-btn" id="add-btn">+ 添加</button>
              <div class="view-toggle">
                <button class="view-btn" id="view-month">月</button>
                <button class="view-btn" id="view-week">周</button>
                <button class="view-btn" id="view-day">日</button>
              </div>
              <div class="month-nav">
                <button class="month-arrow" id="prev-month">‹</button>
                <button class="month-arrow" id="next-month">›</button>
              </div>
              <span class="header-icon">⋮</span>
            </div>
          </div>
          <!-- 主内容区 -->
          <div id="calendar-main">
            <!-- 侧边栏 -->
            <div id="sidebar">
              <span class="sidebar-icon">☑️</span>
              <span class="sidebar-icon active">🗓</span>
              <span class="sidebar-icon">📊</span>
              <span class="sidebar-icon">🔍</span>
              <span class="sidebar-icon">⚙️</span>
            </div>
            <!-- 月历内容 -->
            <div id="calendar-content">
              <div id="calendar-weekdays">
                <div class="weekday">周日</div>
                <div class="weekday">周一</div>
                <div class="weekday">周二</div>
                <div class="weekday">周三</div>
                <div class="weekday">周四</div>
                <div class="weekday">周五</div>
                <div class="weekday">周六</div>
              </div>
              <div id="calendar-grid"></div>
            </div>
          </div>
          <!-- 底部栏 -->
          <div id="calendar-footer">
            <button class="footer-view-btn" id="view-year">年视图</button>
            <button class="footer-view-btn active" id="view-month-footer">月视图</button>
            <button class="footer-view-btn" id="view-week-footer">周视图</button>
            <button class="footer-view-btn" id="view-day-footer">日视图</button>
            <button class="footer-view-btn" id="view-schedule">日程视图</button>
            <button class="footer-view-btn" id="view-multi">多日视图</button>
            <button class="footer-view-btn" id="view-multi-week">多周视图</button>
          </div>
          <button class="upgrade-btn">立即升级</button>
        </div>
      `;
      document.body.insertAdjacentHTML("beforeend", html);
      this.dom = {
        container: document.getElementById("calendar-container"),
        monthTitle: document.getElementById("month-title"),
        prevMonth: document.getElementById("prev-month"),
        nextMonth: document.getElementById("next-month"),
        addBtn: document.getElementById("add-btn"),
        calendarGrid: document.getElementById("calendar-grid"),
      };
    }

    // 绑定事件
    bindEvent() {
      // 月份切换
      this.dom.prevMonth.onclick = () => {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
      };
      this.dom.nextMonth.onclick = () => {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
      };
      // 添加日程
      this.dom.addBtn.onclick = () => {
        const content = prompt("请输入日程内容：");
        if (content) {
          const time = prompt("请输入时间（如 14:00）：") || "";
          this.addSchedule(content, time);
        }
      };
      // 视图切换（简化实现，仅月视图可用）
      document.querySelectorAll(".view-btn, .footer-view-btn").forEach(btn => {
        btn.onclick = () => {
          document.querySelectorAll(".view-btn, .footer-view-btn").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
        };
      });
    }

    // 获取月份标题
    getMonthTitle() {
      return `${this.currentDate.getFullYear()}年${this.currentDate.getMonth() + 1}月`;
    }

    // 渲染月历
    renderCalendar() {
      this.dom.monthTitle.textContent = this.getMonthTitle();
      const year = this.currentDate.getFullYear();
      const month = this.currentDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      const today = new Date();

      // 计算月历网格需要填充的日期
      const days = [];
      // 填充上月剩余日期
      const firstDayOfWeek = firstDay.getDay(); // 0=周日, 6=周六
      for (let i = 0; i < firstDayOfWeek; i++) {
        days.push(new Date(year, month, -firstDayOfWeek + i + 1));
      }
      // 填充当月日期
      for (let i = 1; i <= lastDay.getDate(); i++) {
        days.push(new Date(year, month, i));
      }
      // 填充下月剩余日期，补满6行（42天）
      while (days.length < 42) {
        days.push(new Date(year, month + 1, days.length - firstDayOfWeek + 1));
      }

      // 渲染日期格子
      let html = "";
      days.forEach(day => {
        const dateStr = day.toISOString().split("T")[0];
        const isCurrentMonth = day.getMonth() === month;
        const isToday = day.toDateString() === today.toDateString();
        const daySchedules = this.schedules.filter(s => s.date === dateStr);
        const festival = this.getFestival(day); // 简单节日模拟

        html += `
          <div class="calendar-day ${isCurrentMonth ? "" : "other-month"}">
            <div class="day-header">
              <span class="day-number ${isToday ? "today" : ""}">${day.getDate()}</span>
              ${festival ? `<span class="day-festival">${festival}</span>` : ""}
            </div>
            <div class="day-schedules">
              ${daySchedules.map(s => `
                <div class="schedule-item ${s.completed ? "completed" : ""}" data-id="${s.id}" style="background: ${s.color}">
                  <input type="checkbox" class="schedule-checkbox" ${s.completed ? "checked" : ""}>
                  <span class="schedule-time">${s.time}</span>
                  <span class="schedule-content">${s.content}</span>
                </div>
              `).join("")}
            </div>
          </div>
        `;
      });
      this.dom.calendarGrid.innerHTML = html;

      // 绑定日程事件
      document.querySelectorAll(".schedule-item").forEach(item => {
        const checkbox = item.querySelector(".schedule-checkbox");
        const id = item.dataset.id;
        checkbox.onchange = () => this.toggleComplete(id);
      });
    }

    // 模拟节日（可扩展）
    getFestival(day) {
      const festivals = {
        "8-15": "中元节",
        "9-2": "白露",
        "9-10": "教师节",
        "9-22": "秋分",
        "9-29": "中秋节",
      };
      const key = `${day.getMonth() + 1}-${day.getDate()}`;
      return festivals[key] || "";
    }

    // 基础日程操作
    addSchedule(content, time = "") {
      if (!content) return;
      const colors = ["#409eff", "#67c23a", "#e6a23c", "#f56c6c", "#909399", "#8e44ad"];
      const schedule = {
        id: this.generateId(),
        content: content,
        time: time,
        date: new Date().toISOString().split("T")[0], // 默认今天
        color: colors[Math.floor(Math.random() * colors.length)],
        completed: false,
      };
      this.schedules.push(schedule);
      this.saveLocalSchedules();
      this.renderCalendar();
    }

    toggleComplete(id) {
      const schedule = this.schedules.find(s => s.id === id);
      schedule.completed = !schedule.completed;
      this.saveLocalSchedules();
      this.renderCalendar();
    }

    // AI处理核心（保留原功能）
    async aiHandle(prompt) {
      if (!prompt || !AI_CONFIG.API_KEY || AI_CONFIG.API_KEY === "你的AI密钥") {
        alert("请输入指令或配置AI密钥！");
        return;
      }
      const systemPrompt = `你是日程助手，仅返回标准化JSON指令，无任何其他内容！支持类型：
      1.add:添加 → {"type":"add","data":{"content":"日程内容","time":"14:00"}}
      2.delete:删除 → {"type":"delete","keyword":"关键词"} / {"type":"delete","id":"id"}
      3.complete:标记完成 → {"type":"complete","id":"id"} / {"type":"complete"}(全部)
      4.clear:清空 → {"type":"clear"}
      严格按格式返回JSON！`;
      try {
        const res = await fetch(AI_CONFIG.API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${AI_CONFIG.API_KEY}`,
          },
          body: JSON.stringify({
            model: AI_CONFIG.MODEL,
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: prompt },
            ],
            temperature: 0.1,
          }),
        });
        const data = await res.json();
        const aiResult = data.choices[0].message.content.trim();
        this.executeAiCommand(JSON.parse(aiResult));
      } catch (err) {
        console.error(err);
        alert("AI请求失败：" + err.message);
      }
    }

    executeAiCommand(cmd) {
      switch (cmd.type) {
        case "add":
          this.addSchedule(cmd.data.content, cmd.data.time || "");
          break;
        case "delete":
          if (cmd.id) {
            this.schedules = this.schedules.filter( => .id !== cmd.id);
          } else if (cmd.keyword) {
            this.schedules = this.schedules.filter( => !.content.includes(cmd.keyword));
          }
          this.saveLocalSchedules();
          this.renderCalendar();
          break;
        case "complete":
          if (cmd.id) {
            this.schedules.find( => .id === cmd.id).completed = true;
          } else {
            this.schedules.forEach( => .completed = true);
          }
          this.saveLocalSchedules();
          this.renderCalendar();
          break;
        case "clear":
          this.schedules = [];
          this.saveLocalSchedules();
          this.renderCalendar();
          break;
      }
    }
  }

  // 启动脚本
  new CalendarManager();
})();
