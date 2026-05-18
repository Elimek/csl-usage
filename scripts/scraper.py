"""
CSL prepaid 用量爬虫
GitHub Actions + Playwright 自动登录提取余额/流量/到期日
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from playwright.async_api import async_playwright

CSL_USER = os.environ.get("CSL_USER", "59985735")
CSL_PASS = os.environ.get("CSL_PASS", "")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "docs", "data", "history.json")
HKT = timezone(timedelta(hours=8))


async def scrape():
    if not CSL_PASS:
        print("ERROR: CSL_PASS 环境变量未设置")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="zh-HK",
            timezone_id="Asia/Hong_Kong"
        )
        page = await context.new_page()

        # ===== 1. 登录 =====
        await page.goto("https://prepaid.hkcsl.com/login", wait_until="networkidle")
        await asyncio.sleep(3)

        try:
            await page.locator('#acceptButton').click(timeout=3000)
            await asyncio.sleep(0.5)
        except:
            pass

        await page.locator('nav.loginTabs a.tab-link').nth(1).click()
        await asyncio.sleep(1)
        await page.locator('#msisdn').fill(CSL_USER)
        await page.locator('#pwd').fill(CSL_PASS)
        await asyncio.sleep(0.5)
        await page.locator('#submitBut').click()
        await asyncio.sleep(5)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        if "login" in page.url.lower() or "forgetpassword" in page.url.lower():
            print(f"登录失败! URL: {page.url}")
            await browser.close()
            sys.exit(1)
        print(f"登录成功! URL: {page.url}")

        # ===== 2. 提取 dashboard 基本数据 =====
        dashboard = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                const data = {};
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === '余额') {
                        const val = parseFloat(lines[i + 1]);
                        if (!isNaN(val)) data.balance_hkd = val;
                    }
                    if (lines[i] === '到期日' && lines[i + 1] && /^\\d{4}-\\d{2}-\\d{2}$/.test(lines[i + 1])) {
                        data.expiry_date = lines[i + 1];
                    }
                    if (lines[i] === '状况') data.status = lines[i + 1];
                    if (lines[i] === '实名登记状况') data.registered = lines[i + 1];
                }
                return data;
            }
        """)

        print(json.dumps(dashboard, ensure_ascii=False))

        # ===== 3. 进入余量查询页面 =====
        await page.get_by_text("余量查询").first.click()
        await asyncio.sleep(3)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # ===== 4. DOM 解析用量数据 =====
        usage_data = await page.evaluate("""
            () => {
                const plans = [];
                const backgrounds = document.querySelectorAll('.displayBackground');
                for (const bg of backgrounds) {
                    const titleEl = bg.querySelector('.displayTitleBox');
                    const name = titleEl ? titleEl.innerText.trim() : '';

                    const itemBoxes = bg.querySelectorAll('.displayItemBox');
                    let expiry = null, used = null, remaining = null, unit = null;

                    for (const box of itemBoxes) {
                        const labelEl = box.querySelector('.displayItem');
                        const valueEl = box.querySelector('.displayItemBold');
                        if (!labelEl || !valueEl) continue;

                        const label = labelEl.innerText.trim();
                        const value = valueEl.innerText.trim();

                        if (label === '有效期至') {
                            expiry = value;
                        } else if (label === '已使用量') {
                            const m = value.match(/([\\d.]+)\\s*(GB|MB|KB)/);
                            if (m) {
                                used = parseFloat(m[1]);
                                unit = m[2];
                            } else {
                                used = value;
                            }
                        } else if (label === '余下用量') {
                            const parts = value.split(/\\s+/);
                            const num = parseFloat(parts[0].replace(/,/g, ''));
                            if (!isNaN(num)) {
                                remaining = num;
                                unit = parts.slice(1).join(' ') || null;
                            } else {
                                remaining = value;
                            }
                        }
                    }

                    if (name) {
                        // 从计划名提取 total GB (如 "100GB" 从 "100GB@42Mbps")
                        const totalMatch = name.match(/(\\d+)\\s*GB/);
                        const total_gb = totalMatch ? parseFloat(totalMatch[1]) : null;

                        if (name.includes('通話') || name.includes('通话')) {
                            plans.push({type: 'voice', name, remaining, unit, expiry});
                        } else {
                            plans.push({type: 'data', name, total_gb, used_gb: used, remaining_gb: remaining, unit, expiry});
                        }
                    }
                }
                return plans;
            }
        """)

        # 构建最终 snapshot
        snapshot = {
            "timestamp": datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S"),
            "phone": CSL_USER,
            "balance_hkd": dashboard.get("balance_hkd"),
            "expiry_date": dashboard.get("expiry_date"),
            "status": dashboard.get("status"),
            "registered": dashboard.get("registered"),
            "plans": usage_data,
        }

        await browser.close()
        return snapshot


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def deduplicate(history):
    """去重：相同时间戳的记录只保留一条"""
    seen = set()
    unique = []
    for h in history:
        key = h.get("timestamp", "")
        if key not in seen:
            seen.add(key)
            unique.append(h)
    return unique


if __name__ == "__main__":
    snapshot = asyncio.run(scrape())
    print("\n=== 本次抓取结果 ===")
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))

    history = load_history()
    history.append(snapshot)
    history = deduplicate(history)
    if len(history) > 365:
        history = history[-365:]
    save_history(history)
    print(f"\n✅ 已保存。历史记录共 {len(history)} 条")
