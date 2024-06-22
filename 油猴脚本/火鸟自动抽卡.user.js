// ==UserScript==
// @name         原神自动抽卡
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  自动进行原神抽卡
// @author       You
// @match        https://zhuque.in/gaming/genshin/character/draw
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 添加自定义CSS样式
    const style = `
        #genshin-wish-dialog {
            position: fixed;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            z-index: 9999;
            cursor: move;
        }
    `;
    const styleElement = document.createElement('style');
    styleElement.innerHTML = style;
    document.head.appendChild(styleElement);

    // 创建对话框
    const dialog = document.createElement('div');
    dialog.id = 'genshin-wish-dialog';
    dialog.innerHTML = `
        <h2>原神自动抽卡</h2>
        <label>
            抽卡池选择:
            <select id="wish-type">
                <option value="standard">常驻祈愿</option>
                <option value="character">UP祈愿</option>
            </select>
        </label>
        <br>
        <label>
            抽卡次数(10的倍数):
            <input type="number" id="wish-count" min="10" step="10" value="10">
        </label>
        <br>
        <button id="start-wish">开始抽卡</button>
    `;
    document.body.appendChild(dialog);

    // 设置对话框初始位置为屏幕中央
    const dialogWidth = dialog.offsetWidth;
    const dialogHeight = dialog.offsetHeight;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    dialog.style.left = `${(windowWidth - dialogWidth) / 2}px`;
    dialog.style.top = `${(windowHeight - dialogHeight) / 2}px`;

    // 使对话框可移动
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    const dragElement = document.getElementById('genshin-wish-dialog');
    dragElement.addEventListener('mousedown', dragStart);
    dragElement.addEventListener('mouseup', dragEnd);
    dragElement.addEventListener('mousemove', drag);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        isDragging = true;
    }

    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            setTranslate(currentX, currentY, dragElement);
        }
    }

    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }

    // 获取DOM元素
    const wishTypeSelect = document.getElementById('wish-type');
const wishCountInput = document.getElementById('wish-count');
const startWishButton = document.getElementById('start-wish');

// 点击开始抽卡按钮
startWishButton.addEventListener('click', () => {
    const wishType = wishTypeSelect.value;
    const wishCount = wishCountInput.value;

    // 找到对应的抽卡按钮
    const tenWishButton = Array.from(document.querySelectorAll('div[style*="cursor: pointer;"]')).find(div => div.textContent.includes('连抽十次'));

    if (tenWishButton) {
        let clickCount = 0;
        const interval = setInterval(() => {
            tenWishButton.click();
            clickCount += 10;
            if (clickCount >= wishCount) {
                clearInterval(interval);
                alert(`抽卡完成,共抽了${wishCount}次`);
            }
        }, 500);
    } else {
        alert('未找到抽卡按钮');
    }
});
})();