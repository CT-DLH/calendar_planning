// ==UserScript==
// @name         深色日程规划器(仿截图版)
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  仿截图风格的深色日程规划器，支持AI自动化
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
    #schedule-container {
      position: fixed;
      top: 50px;
      right: 20px;
      width: 380px;
      background: #1e1e2e;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      z-index: 999999;
      font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
      user-select: none;
      overflow: hidden;
      color: #e0e0e0;
    }
    #schedule-header {
      padding: 12px 16px;
      display: flex;
      gap: 12px;
      align-items: center;
      border-bottom: 1px solid #2d2d3f;
    }
    .header-btn {
      flex: 1;
      padding: 10px 0;
      background: #2d2d3f;
      border: none;
      border-radius: 8px;
      color: #e0e0e0;
      font-size: 16px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .header-btn:hover {
      background: #3d3d5f;
    }
    #window-controls {
      display: flex;
      gap: 8px;
      margin-left: auto;
    }
    .window-btn {
      background: transparent;
      border: none;
      color: #888;
      font-size: 18px;
      cursor: pointer;
      padding: 0 4px;
    }
    .window-btn:hover {
      color: #e0e0e0;
    }

    /* 日期导航栏 */
    #date-nav {
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid #2d2d3f;
    }
    .date-arrow {
      background: transparent;
      border: none;
      color: #888;
      font-size: 16px;
      cursor: pointer;
    }
    .date-arrow:hover {
      color: #e0e0e0;
    }
    .date-list {
      flex: 1;
      display: flex;
      justify-content: space-between;
    }
    .date-item {
      text-align: center;
      padding: 8px 4px;
      border-radius: 8px;
      cursor: pointer;
      min-width: 40px;
      position: relative;
    }
    .date-item.active {
      background: #2ea043;
      color: #fff;
    }
    .date-item .week {
      font-size: 14px;
      display: block;
    }
    .date-item .date {
      font-size: 12px;
      opacity: 0.8;
      display: block;
    }
    .date-dot {
      position: absolute;
      top: 4px;
      right: 4px;
      width: 6px;
      height: 6px;
      background: #f9c74f;
      border-radius: 50%;
    }

    /* 待办列表 */
    #schedule-body {
      padding: 16px;
      max-height: 420px;
      overflow-y: auto;
    }
    .todo-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #2d2d3f;
    }
    .todo-checkbox {
      width: 18px;
      height: 18px;
      accent-color: #2ea043;
      cursor: pointer;
    }
    .todo-content {
      flex: 1;
      font-size: 16px;
    }
    .todo-content.completed {
      text-decoration: line-through;
      color: #666;
    }
    .todo-actions {
      display: flex;
      gap: 12px;
    }
    .todo-btn {
      background: transparent;
      border: none;
      color: #888;
      font-size: 16px;
      cursor: pointer;
    }
    .todo-btn:hover {
      color: #e0e0e0;
    }
    .add-todo-btn {
      width: 100%;
      padding: 12px;
      margin-top: 12px;
      background: #2d2d3f;
      border: 1px dashed #444;
      border-radius: 8px;
      color: #888;
      font-size: 20px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .add-todo-btn:hover {
      border-color: #666;
      color: #e0e0e0;
    }

    /* 底部统计 */
    #schedule-footer {
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid #2d2d3f;
      font-size: 14px;
      color: #888;
    }
    .footer-icons {
      display: flex;
      gap: 16px;
    }
    .footer-icon {
      cursor: pointer;
      font-size: 18px;
    }
    .footer-icon:hover {
      color: #e0e0e0;
    }
    .todo-count {
      color: #888;
    }
  `);

  // 核心数据类
  class ScheduleManager {
    constructor() {
      this.schedules = this.getLocalSchedules();
      this.currentDate = new Date();
      this.initUI();
      this.bindEvent();
      this.renderDateNav();
      this.renderTodoList();
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
        <div id="schedule-container">
          <div id="schedule-header">
            <button class="header-btn" id="focus-btn">开始专注</button>
            <button class="header-btn" id="remind-btn">添加提醒</button>
            <div id="window-controls">
              <button class="window-btn" id="min-btn">−</button>
              <button class="window-btn" id="close-btn">×</button>
            </div>
          </div>
          <div id="date-nav">
            <button class="date-arrow" id="prev-week">←</button>
            <div class="date-list" id="date-list"></div>
            <button class="date-arrow" id="next-week">→</button>
          </div>
          <div id="schedule-body">
            <div id="todo-list"></div>
            <button class="add-todo-btn" id="add-todo">+</button>
          </div>
          <div id="schedule-footer">
            <div class="footer-icons">
              <span class="footer-icon">☰</span>
              <span class="footer-icon">🗓</span>
            </div>
            <div class="todo-count" id="todo-count">今0 总0</div>
          </div>
        </div>
      `;
      document.body.insertAdjacentHTML("beforeend", html);
      this.dom = {
        container: document.getElementById("schedule-container"),
        dateList: document.getElementById("date-list"),
        todoList: document.getElementById("todo-list"),
        todoCount: document.getElementById("todo-count"),
        addTodo: document.getElementById("add-todo"),
        prevWeek: document.getElementById("prev-week"),
        nextWeek: document.getElementById("next-week"),
        minBtn: document.getElementById("min-btn"),
        closeBtn: document.getElementById("close-btn"),
        focusBtn: document.getElementById("focus-btn"),
        remindBtn: document.getElementById("remind-btn"),
      };
    }

    // 绑定事件
    bindEvent() {
      // 拖拽
      this.dragElement(this.dom.container);
      // 最小化/关闭
      this.dom.minBtn.onclick = () => this.dom.container.style.display = "none";
      this.dom.closeBtn.onclick = () => this.dom.container.remove();
      // 周切换
      this.dom.prevWeek.onclick = () => {
        this.currentDate.setDate(this.currentDate.getDate() - 7);
        this.renderDateNav();
        this.renderTodoList();
      };
      this.dom.nextWeek.onclick = () => {
        this.currentDate.setDate(this.currentDate.getDate() + 7);
        this.renderDateNav();
        this.renderTodoList();
      };
      // 添加待办
      this.dom.addTodo.onclick = () => this.addTodo("新待办");
      // 专注/提醒按钮（可扩展功能）
      this.dom.focusBtn.onclick = () => alert("专注模式待实现");
      this.dom.remindBtn.onclick = () => {
        const content = prompt("请输入提醒内容：");
        if (content) this.addTodo(content);
      };
    }

    // 拖拽实现
    dragElement(elem) {
      let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      const header = document.getElementById("schedule-header");
      header.onmousedown = dragStart;
      function dragStart(e) {
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = dragEnd;
        document.onmousemove = dragMove;
      }
      function dragMove(e) {
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        elem.style.top = (elem.offsetTop - pos2) + "px";
        elem.style.right = "auto";
        elem.style.left = (elem.offsetLeft - pos1) + "px";
      }
      function dragEnd() {
        document.onmouseup = null;
        document.onmousemove = null;
      }
    }

    // 渲染日期导航
    renderDateNav() {
      const weekDays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
      const startOfWeek = new Date(this.currentDate);
      startOfWeek.setDate(this.currentDate.getDate() - this.currentDate.getDay() + 1); // 周一为起点
      let html = "";
      for (let i = 0; i < 7; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        const isToday = d.toDateString() === new Date().toDateString();
        const hasSchedule = this.schedules.some(s => s.date === d.toISOString().split("T")[0]);
        html += `
          <div class="date-item ${isToday ? "active" : ""}" data-date="${d.toISOString().split("T")[0]}">
            <span class="week">${weekDays[i]}</span>
            <span class="date">${d.getMonth()+1}-${d.getDate()}</span>
            ${hasSchedule ? '<span class="date-dot"></span>' : ''}
          </div>
        `;
      }
      this.dom.dateList.innerHTML = html;
      // 绑定日期点击
      document.querySelectorAll(".date-item").forEach(item => {
        item.onclick = () => {
          this.currentDate = new Date(item.dataset.date);
          this.renderDateNav();
          this.renderTodoList();
        };
      });
    }

    // 渲染待办列表
    renderTodoList() {
      const todayStr = new Date().toISOString().split("T")[0];
      const currentDateStr = this.currentDate.toISOString().split("T")[0];
      const currentSchedules = this.schedules.filter(s => s.date === currentDateStr);

      let html = "";
      currentSchedules.forEach(item => {
        html += `
          <div class="todo-item" data-id="${item.id}">
            <input type="checkbox" class="todo-checkbox" ${item.completed ? "checked" : ""}>
            <span class="todo-content ${item.completed ? "completed" : ""}">${item.content}</span>
            <div class="todo-actions">
              <button class="todo-btn edit-btn">✏️</button>
              <button class="todo-btn del-btn">🗑️</button>
            </div>
          </div>
        `;
      });
      this.dom.todoList.innerHTML = html;

      // 绑定待办事件
      document.querySelectorAll(".todo-item").forEach(item => {
        const checkbox = item.querySelector(".todo-checkbox");
        const editBtn = item.querySelector(".edit-btn");
        const delBtn = item.querySelector(".del-btn");
        const id = item.dataset.id;

        checkbox.onchange = () => this.toggleComplete(id);
        editBtn.onclick = () => {
          const newContent = prompt("编辑待办：", this.schedules.find(s => s.id === id).content);
          if (newContent) this.editTodo(id, newContent);
        };
        delBtn.onclick = () => this.deleteTodo(id);
      });

      // 更新统计
      const todayCount = this.schedules.filter(s => s.date === todayStr).length;
      const totalCount = this.schedules.length;
      this.dom.todoCount.textContent = `今${todayCount} 总${totalCount}`;
    }

    // 基础待办操作
    addTodo(content) {
      if (!content) return;
      const todo = {
        id: this.generateId(),
        content: content,
        completed: false,
        date: this.currentDate.toISOString().split("T")[0],
      };
      this.schedules.push(todo);
      this.saveLocalSchedules();
      this.renderTodoList();
      this.renderDateNav();
    }
    deleteTodo(id) {
      this.schedules = this.schedules.filter(s => s.id !== id);
      this.saveLocalSchedules();
      this.renderTodoList();
      this.renderDateNav();
    }
    toggleComplete(id) {
      const todo = this.schedules.find(s => s.id === id);
      todo.completed = !todo.completed;
      this.saveLocalSchedules();
      this.renderTodoList();
    }
    editTodo(id, content) {
      const todo = this.schedules.find(s => s.id === id);
      todo.content = content;
      this.saveLocalSchedules();
      this.renderTodoList();
    }

    // AI处理核心（保留原功能）
    async aiHandle(prompt) {
      if (!prompt || !AI_CONFIG.API_KEY || AI_CONFIG.API_KEY === "你的AI密钥") {
        alert("请输入指令或配置AI密钥！");
        return;
      }
      const systemPrompt = `你是日程助手，仅返回标准化JSON指令，无任何其他内容！支持类型：
      1.add:添加 → {"type":"add","data":{"content":"日程内容"}}
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
          this.addTodo(cmd.data.content);
          break;
        case "delete":
          if (cmd.id) this.deleteTodo(cmd.id);
          else if (cmd.keyword) {
            this.schedules = this.schedules.filter( => !.content.includes(cmd.keyword));
            this.saveLocalSchedules();
            this.renderTodoList();
            this.renderDateNav();
          }
          break;
        case "complete":
          if (cmd.id) this.schedules.find( => .id === cmd.id).completed = true;
          else this.schedules.forEach( => .completed = true);
          this.saveLocalSchedules();
          this.renderTodoList();
          break;
        case "clear":
          this.schedules = [];
          this.saveLocalSchedules();
          this.renderTodoList();
          this.renderDateNav();
          break;
      }
    }
  }

  // 启动脚本
  new ScheduleManager();
})();
