// ==UserScript==
// @name         一键放弃认领种子
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  自动取消认领红色标签的种子或所有种子
// @author       YZFly
// @match        https://pterclub.com/viewclaims.php*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 创建一个容器
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '10px';
    container.style.right = '10px';
    container.style.zIndex = '1000';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '10px';

    // 创建按钮样式
    const buttonStyle = `
        padding: 10px;
        background-color: #ff0000;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 5px;
    `;

    // 创建图标
    const createIcon = (iconText) => {
        const icon = document.createElement('span');
        icon.innerText = iconText;
        icon.style.fontSize = '16px';
        return icon;
    };

    // 创建按钮
    const createButton = (text, iconText, onClick) => {
        const button = document.createElement('button');
        button.innerText = text;
        button.style.cssText = buttonStyle;
        button.prepend(createIcon(iconText));
        button.addEventListener('click', onClick);
        return button;
    };

    // 按钮点击事件
    const cancelClaims = (filterFn) => {
        const rows = document.querySelectorAll('tr');
        rows.forEach(row => {
            if (filterFn(row)) {
                const cancelLink = row.querySelector('a.remove-confirm');
                if (cancelLink) {
                    const url = cancelLink.getAttribute('data-url');
                    if (url) {
                        // 发送请求取消认领
                        fetch(url, {
                            method: 'GET',
                            credentials: 'include'
                        }).then(response => {
                            if (response.ok) {
                                console.log(`取消认领成功: ${url}`);
                            } else {
                                console.error(`取消认领失败: ${url}`);
                            }
                        }).catch(error => {
                            console.error(`请求错误: ${error}`);
                        });
                    }
                }
            }
        });
    };

    // 创建按钮并添加到容器
    const redTagButton = createButton('放弃认领红色标签的种子', '🔴', () => {
        cancelClaims(row => row.querySelector('img.progbarred'));
    });
    const allButton = createButton('放弃认领所有种子', '⚪', () => {
        cancelClaims(() => true);
    });

    container.appendChild(redTagButton);
    container.appendChild(allButton);

    // 将容器添加到页面
    document.body.appendChild(container);
})();