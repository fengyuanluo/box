// ==UserScript==
// @name         Galgame种子上传
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Galgame种子上传
// @author       Luofengyuan
// @match        https://pterclub.com/uploadgame.php?id=*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 当网页加载完成后，执行下面的代码
    window.addEventListener('load', function() {
        // 自动填写种子标题
        const seedTitleInput = document.getElementById('name');
        if (seedTitleInput) {
            seedTitleInput.value = 'v1.0 with 3rd chinese translation';
        }

        // 自动填写种子简介
        // 假设种子简介的文本输入框可以通过textarea标签进行选择
        const seedDescriptionInput = document.querySelector('textarea');
        if (seedDescriptionInput) {
            seedDescriptionInput.value = '配音语言：日语\n字幕语言：中文';
        }

        // 以下是之前脚本的内容，保持不变
        // 选择类型为 "Game (游戏本体)"
        document.getElementById('categories').value = '1';

        // 选择格式为 "Portable"
        document.getElementById('format').value = '4';

        // 选择地区为 "日本 (JPN)"
        document.getElementById('team').value = '6';

        // 勾选 "GalGame" 标签
        let galGameCheckbox = document.getElementById('gg');
        if (galGameCheckbox) {
            galGameCheckbox.checked = true;
        }

        // 勾选 "中字" 标签
        let chineseSubCheckbox = document.getElementById('zhongzi');
        if (chineseSubCheckbox) {
            chineseSubCheckbox.checked = true;
        }

        // 勾选匿名发布
        let anonymousCheckbox = document.querySelector('input[type="checkbox"][name="uplver"]');
        if (anonymousCheckbox) {
            anonymousCheckbox.checked = true;
        }
    });
})();