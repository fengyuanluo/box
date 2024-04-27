// ==UserScript==
// @name         VNDB Information Retriever
// @namespace    http://tampermonkey.net/
// @version      0.6
// @description  Retrieves information from VNDB and populates the form on the target website
// @author       Luofengyuan
// @match        https://pterclub.com/uploadgameinfo.php*
// @grant        GM_xmlhttpRequest
// @require      https://momentjs.com/downloads/moment.min.js
// ==/UserScript==
/* global moment */


(function() {
    'use strict';


function findEarliestReleaseDate(doc) {
  const dateElements = doc.querySelectorAll('.tc1');
  if (dateElements.length > 0) {
    const validDates = Array.from(dateElements)
      .map(element => {
        const dateStr = element.textContent.trim();
        // 尝试多种日期格式
        const formats = [
          'YYYY/M/D', 'YYYY/MM/DD', 'YYYY/M/D h:mm A', 'YYYY/MM/DD h:mm A',
          'M/D/YYYY', 'MM/DD/YYYY', 'M/D/YYYY h:mm A', 'MM/DD/YYYY h:mm A',
          'YYYY-M-D', 'YYYY-MM-DD', 'YYYY-M-D h:mm A', 'YYYY-MM-DD h:mm A'
        ];
        return moment(dateStr, formats, true);
      })
      .filter(date => date.isValid())
      .map(date => date.toDate());

    if (validDates.length > 0) {
      const earliestDate = validDates.reduce((a, b) => a < b ? a : b);
      return moment(earliestDate).format('YYYY-MM-DD');
    }
  }
  return null;
}
        // Function to extract publishers excluding grayed out entries
function extractPublishers(doc) {
    let publisherNames = [];
    const tds = doc.querySelectorAll('td');
    let publishersCell;
    for (const td of tds) {
        if (td.textContent.includes('Publishers')) {
            publishersCell = td.nextElementSibling;
            break;
        }
    }
    if (publishersCell) {
        const links = publishersCell.querySelectorAll('a');
        publisherNames = Array.from(links).map(link => {
            if (!link.classList.contains('grayedout')) {
                return link.getAttribute('title').trim();
            }
        }).filter(Boolean);
    }
    return publisherNames.join(', ');
}

    // Create an input box for the VNDB URL
    const referRow = document.querySelector('tr > td.rowfollow');
    if (referRow) {
        // Create an input box for the VNDB URL
        const vndbInput = document.createElement('input');
        vndbInput.type = 'text';
        vndbInput.placeholder = 'Enter VNDB URL';
        vndbInput.style.width = '40px'; // 增加输入框的宽度以适应URL输入
        vndbInput.style.textShadow = 'rgb(0, 0, 0) 0px 0px 0px';

        const submitButton = document.createElement('input');
        submitButton.type = 'button';
        submitButton.value = 'Submit';
        submitButton.style.textShadow = 'rgb(0, 0, 0) 0px 0px 0px';

        const newRow = document.createElement('tr');
        const newRowHead = document.createElement('td');
        newRowHead.className = 'rowhead nowrap';
        newRowHead.vAlign = 'top';
        newRowHead.align = 'right';
        newRowHead.style.textShadow = 'rgb(17, 17, 17) 0px 0px 0px';
        newRowHead.textContent = "VNDB URL:"; // 添加一个输入框标签

        const newRowFollow = document.createElement('td');
        newRowFollow.className = 'rowfollow';
        newRowFollow.vAlign = 'top';
        newRowFollow.align = 'left';
        newRowFollow.style.textShadow = 'rgb(17, 17, 17) 0px 0px 0px';
        newRowFollow.appendChild(vndbInput);
        newRowFollow.appendChild(submitButton);

        newRow.appendChild(newRowHead);
        newRow.appendChild(newRowFollow);

        referRow.parentNode.insertBefore(newRow, referRow.nextSibling);

        submitButton.addEventListener('click', () => {
            const vndbUrl = vndbInput.value;
            fetchVNDBData(vndbUrl);
        });
    }

    function fetchVNDBData(url) {
        GM_xmlhttpRequest({
            method: 'GET',
            url: url,
            onload: function(response) {
                const parser = new DOMParser();
                const doc = parser.parseFromString(response.responseText, 'text/html');

                // Extract information from the VNDB page
                const coverImage = doc.querySelector('meta[property="og:image"]')?.content;
                const englishTitleElem = doc.querySelector('h1[lang="ja-Latn"]');
                const englishTitle = englishTitleElem ? englishTitleElem.textContent.trim() : '';
                const japaneseTitleElem = doc.querySelector('h2.alttitle[lang="ja"]');
                const japaneseTitle = japaneseTitleElem ? japaneseTitleElem.textContent.trim() : '';
const aliases = japaneseTitleElem ? japaneseTitleElem.textContent.trim() : '';
                const playTime = Array.from(doc.querySelectorAll('td')).find(td => td.textContent.includes('Play time'))?.nextElementSibling.textContent.trim();
                const developerRow = Array.from(doc.querySelectorAll('tr')).find(tr => tr.textContent.includes('Developer'));
                const developer = developerRow ? developerRow.nextElementSibling.querySelector('a').textContent.trim() : '';

const publishers = extractPublishers(doc); // Use the new function to extract publishers
/*                 const publishersRow = Array.from(doc.querySelectorAll('tr')).find(tr => tr.textContent.includes('Publishers'));
                const publishers = [];
                if (publishersRow) {
                    publishersRow.nextElementSibling.querySelectorAll('a').forEach(a => {
                        publishers.push(a.textContent.trim());
                    });
                } */

                // 获取最早发布日期
                let releaseDate = findEarliestReleaseDate(doc);
                const introduction = doc.querySelector('meta[property="og:description"]')?.content;
// 获取截图
const screenshotContainer = doc.querySelector('article#screenshots');
const safeScreenshots = Array.from(screenshotContainer.querySelectorAll('a.scrlnk_s0:not(.nsfw)'));
const suggestiveScreenshots = Array.from(screenshotContainer.querySelectorAll('a.scrlnk_s1:not(.nsfw)'));

let screenshots = safeScreenshots.map(a => a.href.replace('.t/', '/'));

// 如果安全级别截图少于 3 张,则添加 Suggestive 级别的截图
if (safeScreenshots.length < 3 && suggestiveScreenshots.length > 0) {
    const additionalScreenshots = suggestiveScreenshots.map(a => a.href.replace('.t/', '/'));
    screenshots = screenshots.concat(additionalScreenshots);
}

                // Populate the form on the target website
                document.querySelector('input[name="small_descr"]').value = aliases;
                document.querySelector('input[name="name"]').value = englishTitle;
                const descriptionField = document.querySelector('textarea[name="descr"]');
                if (descriptionField) {
                    let bbCodeContent = `[center][img]${coverImage}[/img][/center]\n`;
                    bbCodeContent += `  [center][b]基本信息[/b]\n`;
                    bbCodeContent += `  日文名称：${japaneseTitle || ''}\n`;
                    bbCodeContent += `  英文名称：${englishTitle || ''}\n`;
                    bbCodeContent += `  开发商：${developer}\n`;
                    bbCodeContent += `  发行商：${publishers}\n`;
                    bbCodeContent += `  平台：Windows\n`;
                    bbCodeContent += `  首发日期：${releaseDate || ''}[/center]\n`;
                    bbCodeContent += `[center][b]配置要求[/b]\n`;
                    bbCodeContent += `  系统：Windows[/center]\n`;
                    bbCodeContent += `[center][b]游戏简介[/b][/center]\n`;
                    bbCodeContent += `  ${introduction || ''}\n`;
                    bbCodeContent += screenshots.map(screenshot => `  [center]-[img]${screenshot}[/img][/center]\n`).join('');
                    descriptionField.value = bbCodeContent;
                } else {
                    console.error('Could not find the description field on the target website.');
                }

                // 自动选择 Windows
                const consoleSelect = document.querySelector('select[name="console"]');
                if (consoleSelect) {
                    const windowsOption = Array.from(consoleSelect.options).find(option => option.textContent.toLowerCase().includes('windows'));
                    if (windowsOption) {
                        windowsOption.selected = true;
                    }
                }

                //勾选匿名发布
const uplverCheckbox = document.querySelector('input[name="uplver"]');
if (uplverCheckbox) {
uplverCheckbox.checked = true;
}
                // 自动填写发布日期
            const releaseDateField = document.querySelector('input[name="releasedate"]');
            if (releaseDateField) {
                releaseDateField.value = releaseDate;
            }

            // 新增: 自动填写年份字段
            const yearField = document.querySelector('input[name="year"]');
            if (yearField && releaseDate) {
                const releaseYear = new Date(releaseDate).getFullYear();
                yearField.value = releaseYear;
            }
        },
        onerror: function(error) {
            console.error('Error fetching VNDB data:', error);
            }
        });
    }
})();