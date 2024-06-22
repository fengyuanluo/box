// ==UserScript==
// @name         VNDB Information Retriever
// @namespace    http://tampermonkey.net/
// @version      0.7
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

    function getDlsiteSystemRequirements(vndbUrl) {
  console.log('Fetching system requirements from VNDB link:', vndbUrl);
  // 从VNDB链接中提取作品ID
  const match = vndbUrl.match(/\/id\/(VJ\d+)\.html/);
  if (!match) {
    console.log('Could not extract product ID from VNDB link.');
    return Promise.resolve(null);
  }
  const productId = match[1];
  // 构造Dlsite作品页面链接
  const dlsiteUrl = `https://www.dlsite.com/pro/work/=/product_id/${productId}.html`;
  console.log('Fetching system requirements from Dlsite link:', dlsiteUrl);

  return new Promise((resolve, reject) => {
    GM_xmlhttpRequest({
      method: 'GET',
      url: dlsiteUrl,
      onload: function(response) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(response.responseText, 'text/html');
        const specList = doc.querySelector('.work_spec_list');
        if (specList) {
          console.log('Found spec list element:', specList);
          let systemRequirements = '';
          const dtElements = specList.querySelectorAll('dt');
          const ddElements = specList.querySelectorAll('dd');
          console.log('Found', dtElements.length, 'dt elements and', ddElements.length, 'dd elements.');
          for (let i = 0; i < dtElements.length; i++) {
            const dtText = dtElements[i].textContent.trim();
            const ddText = ddElements[i].textContent.trim();
            console.log('dt:', dtText, '- dd:', ddText);
            systemRequirements += `${dtText}: ${ddText}\n`;
          }
          resolve(systemRequirements);
        } else {
          console.log('Could not find spec list element.');
          resolve(null);
        }
      },
      onerror: function(error) {
        console.error('Error fetching system requirements from dlsite:', error);
        reject(error);
      }
    });
  });
}

    const referRow = document.querySelector('tr > td.rowfollow');
    if (referRow) {
        const vndbInput = document.createElement('input');
        vndbInput.type = 'text';
        vndbInput.placeholder = 'Enter VNDB URL';
        vndbInput.style.width = '40px';
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
        newRowHead.textContent = "VNDB URL:";

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

        submitButton.addEventListener('click', async () => {
            const vndbUrl = vndbInput.value;
            fetchVNDBData(vndbUrl);
        });
    }

    async function fetchVNDBData(url) {
        GM_xmlhttpRequest({
            method: 'GET',
            url: url,
            onload: async function(response) {
                const parser = new DOMParser();
                const doc = parser.parseFromString(response.responseText, 'text/html');

                const coverImage = doc.querySelector('meta[property="og:image"]')?.content;
                const englishTitleElem = doc.querySelector('h1[lang="ja-Latn"]');
                const englishTitle = englishTitleElem ? englishTitleElem.textContent.trim() : '';
                const japaneseTitleElem = doc.querySelector('h2.alttitle[lang="ja"]');
                const japaneseTitle = japaneseTitleElem ? japaneseTitleElem.textContent.trim() : '';
                const aliases = japaneseTitleElem ? japaneseTitleElem.textContent.trim() : '';
                const playTime = Array.from(doc.querySelectorAll('td')).find(td => td.textContent.includes('Play time'))?.nextElementSibling.textContent.trim();
                const developerRow = Array.from(doc.querySelectorAll('tr')).find(tr => tr.textContent.includes('Developer'));
                const developer = developerRow ? developerRow.nextElementSibling.querySelector('a').textContent.trim() : '';

                const publishers = extractPublishers(doc);

                let releaseDate = findEarliestReleaseDate(doc);
                const introduction = doc.querySelector('meta[property="og:description"]')?.content;

                const screenshotContainer = doc.querySelector('article#screenshots');
                let screenshots = [];
                if (screenshotContainer) {
                    const safeScreenshots = Array.from(screenshotContainer.querySelectorAll('a.scrlnk_s0:not(.nsfw)'));
                    const suggestiveScreenshots = Array.from(screenshotContainer.querySelectorAll('a.scrlnk_s1:not(.nsfw)'));

                    screenshots = safeScreenshots.map(a => a.href.replace('.t/', '/'));

                    if (safeScreenshots.length < 3 && suggestiveScreenshots.length > 0) {
                        const additionalScreenshots = suggestiveScreenshots.map(a => a.href.replace('.t/', '/'));
                        screenshots = screenshots.concat(additionalScreenshots);
                    }
                }

                document.querySelector('input[name="small_descr"]').value = aliases;
                document.querySelector('input[name="name"]').value = englishTitle;

                // 获取dlsite链接
                const dlsiteLink = doc.querySelector('#buynow a[href*="dlsite.com"]');
                let systemRequirements = '系统：Windows';
                if (dlsiteLink) {
                    const dlsiteUrl = dlsiteLink.href;
                    try {
                        const dlsiteRequirements = await getDlsiteSystemRequirements(dlsiteUrl);
                        if (dlsiteRequirements) {
                            systemRequirements = dlsiteRequirements;
                        }
                    } catch (error) {
                        console.error('Error fetching system requirements from dlsite:', error);
                    }
                }

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
                    bbCodeContent += `  ${systemRequirements}[/center]\n`;
                    bbCodeContent += `[center][b]游戏简介[/b][/center]\n`;
                    bbCodeContent += `  ${introduction || ''}\n`;
                    bbCodeContent += screenshots.map(screenshot => `  [center]-[img]${screenshot}[/img][/center]\n`).join('');
                    descriptionField.value = bbCodeContent;
                } else {
                    console.error('Could not find the description field on the target website.');
                }

                const consoleSelect = document.querySelector('select[name="console"]');
                if (consoleSelect) {
                    const windowsOption = Array.from(consoleSelect.options).find(option => option.textContent.toLowerCase().includes('windows'));
                    if (windowsOption) {
                        windowsOption.selected = true;
                    }
                }

                const uplverCheckbox = document.querySelector('input[name="uplver"]');
                if (uplverCheckbox) {
                    uplverCheckbox.checked = true;
                }

                const releaseDateField = document.querySelector('input[name="releasedate"]');
                if (releaseDateField) {
                    releaseDateField.value = releaseDate;
                }

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