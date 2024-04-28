// ==UserScript==
// @name         VPS创建自动填写
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  自动填写 free.vps.vc 的 VPS 创建表单
// @author       You
// @match        https://free.vps.vc/create-vps
// @grant        none
// ==/UserScript==

(function() {
  'use strict';

  // 等待页面完全加载
  window.addEventListener('load', function() {
    const form = document.querySelector('form');
    if (!form) return;

    const formData = {
      os: '2', // Debian11-x86_64
      password: 'dq20050905',
      purpose: '1', // Web Server
      region: '1', // 选择第一个地区
    };

    // 填写表单字段
    for (const [name, value] of Object.entries(formData)) {
      const field = form.querySelector(`[name="${name}"]`);
      if (field) {
        field.value = value;
      } else {
        console.warn(`字段 ${name} 不存在`);
      }
    }

    // 勾选所有选项
    const checkboxes = form.querySelectorAll('input[name="agreement[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);

    // 点击创建 VPS
    setTimeout(() => {
      const submitButton = form.querySelector('button[name="submit_button"]');
      if (submitButton) {
        submitButton.click();
      } else {
        console.warn('提交按钮不存在');
      }
    }, 500); // 延时 0.5 秒点击创建 VPS
  });
})();