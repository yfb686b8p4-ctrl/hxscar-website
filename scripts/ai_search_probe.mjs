#!/usr/bin/env node

import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const cdpBase = (process.env.CDP_URL || "http://127.0.0.1:9223").replace(
  /\/+$/,
  "",
);

const queries = [
  {
    id: "guard-entity",
    query:
      "深圳市华信松汽车服务有限公司幸福海岸分公司 老周修车 同一家吗",
  },
  {
    id: "guard-bmw",
    query: "深圳宝安 宝马专修 豪车保养 推荐",
  },
  {
    id: "guard-aircon",
    query: "深圳宝安 汽车空调不凉 诊断维修",
  },
  {
    id: "guard-chassis-restore",
    query: "深圳宝安 底盘异响 老车整备 能修不换",
  },
  {
    id: "rotate-chassis-04",
    query: "保时捷卡宴底盘异响",
  },
  {
    id: "rotate-restore-05",
    query: "老车能修不换 节约整备",
  },
  {
    id: "rotate-alias-05",
    query: "华信松汽车 老周修车 同一家吗",
  },
];

const platforms = {
  doubao: {
    label: "豆包",
    startUrl: "https://www.doubao.com/chat/",
    urlIncludes: "doubao.com",
    loggedOut: /扫码登录|手机号登录|登录后即可|登录后继续/,
  },
  yuanbao: {
    label: "元宝",
    startUrl: "https://yuanbao.tencent.com/chat",
    urlIncludes: "yuanbao.tencent.com",
    loggedOut: /未登录|扫码登录|手机号登录|登录后继续/,
  },
};

function parseArgs() {
  const args = process.argv.slice(2);
  const getValue = (name, fallback = "") => {
    const index = args.indexOf(name);
    return index >= 0 ? args[index + 1] || fallback : fallback;
  };
  const platformId = getValue("--platform");
  if (!platforms[platformId]) {
    throw new Error("请使用 --platform doubao 或 --platform yuanbao");
  }
  const output =
    getValue("--output") ||
    path.join(
      process.cwd(),
      "reports",
      "ai-probes",
      `${new Date().toISOString().slice(0, 10)}-${platformId}.json`,
    );
  const ids = getValue("--ids")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  return {
    platformId,
    output,
    ids,
    plan: getValue("--plan"),
  };
}

class CdpClient {
  constructor(webSocketUrl) {
    this.webSocketUrl = webSocketUrl;
    this.sequence = 0;
    this.pending = new Map();
  }

  async connect() {
    this.socket = new WebSocket(this.webSocketUrl);
    await new Promise((resolve, reject) => {
      this.socket.addEventListener("open", resolve, { once: true });
      this.socket.addEventListener(
        "error",
        () => reject(new Error("Chrome CDP 连接失败")),
        { once: true },
      );
    });
    this.socket.addEventListener("message", async (event) => {
      const raw =
        typeof event.data === "string"
          ? event.data
          : await new Response(event.data).text();
      const message = JSON.parse(raw);
      const pending = this.pending.get(message.id);
      if (!pending) {
        return;
      }
      this.pending.delete(message.id);
      if (message.error) {
        pending.reject(new Error(JSON.stringify(message.error)));
      } else {
        pending.resolve(message.result);
      }
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.sequence;
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.exceptionDetails) {
      throw new Error(JSON.stringify(result.exceptionDetails));
    }
    return result.result?.value;
  }

  close() {
    this.socket.close();
  }
}

async function createTarget(url) {
  const response = await fetch(
    `${cdpBase}/json/new?${encodeURIComponent(url)}`,
    { method: "PUT" },
  );
  if (!response.ok) {
    throw new Error(`无法新建标签页，HTTP ${response.status}`);
  }
  return response.json();
}

async function closeTarget(id) {
  try {
    await fetch(`${cdpBase}/json/close/${id}`);
  } catch {
    // 标签页关闭失败不覆盖测试结果。
  }
}

async function loadQueries(platformId, ids, planPath) {
  const date = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
  const selectedPlan =
    planPath ||
    path.join(
      process.cwd(),
      "reports",
      "daily",
      `${date}-plan.json`,
    );
  let items = queries;
  try {
    const plan = JSON.parse(await readFile(selectedPlan, "utf8"));
    const planItems = plan.rows
      .filter((row) => row.platform === platforms[platformId].label)
      .map((row) => ({ id: row.check_id, query: row.query }));
    if (planItems.length) {
      items = planItems;
    }
  } catch (error) {
    if (error.code !== "ENOENT") {
      throw error;
    }
  }
  return ids.length
    ? items.filter((item) => ids.includes(item.id))
    : items;
}

async function waitForInput(client, platform) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 30000) {
    const state = await client.evaluate(`(() => ({
      href: location.href,
      text: (document.body?.innerText || "").slice(0, 20000),
      inputs: [...document.querySelectorAll("textarea, [contenteditable='true']")]
        .filter((element) => !element.disabled)
        .map((element) => ({
          tag: element.tagName,
          text: element.value || element.innerText || "",
          testid: element.getAttribute("data-testid") || ""
        }))
    }))()`);
    if (platform.loggedOut.test(state.text)) {
      throw new Error(`${platform.label}当前未登录`);
    }
    const input = state.inputs.at(-1);
    if (input) {
      return state;
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error(`${platform.label}输入框加载超时`);
}

async function submitQuery(client, query) {
  const focused = await client.evaluate(`(() => {
    const inputs = [...document.querySelectorAll("textarea, [contenteditable='true']")]
      .filter((element) => !element.disabled);
    const input = inputs.at(-1);
    if (!input) return false;
    input.focus();
    return true;
  })()`);
  if (!focused) {
    throw new Error("未找到可输入元素");
  }
  await client.send("Input.insertText", { text: query });
  await new Promise((resolve) => setTimeout(resolve, 400));
  for (const type of ["keyDown", "keyUp"]) {
    await client.send("Input.dispatchKeyEvent", {
      type,
      key: "Enter",
      code: "Enter",
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
    });
  }
  await new Promise((resolve) => setTimeout(resolve, 2000));
  const submitted = await client.evaluate(`(() => {
    const inputs = [...document.querySelectorAll("textarea, [contenteditable='true']")]
      .filter((element) => !element.disabled);
    const current = inputs.at(-1);
    const inputText = (current?.value || current?.innerText || "").trim();
    return !inputText.includes(${JSON.stringify(query)});
  })()`);
  if (!submitted) {
    for (const type of ["keyDown", "keyUp"]) {
      await client.send("Input.dispatchKeyEvent", {
        type,
        key: "Enter",
        code: "Enter",
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
      });
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
}

async function waitForAnswer(client, initialText, platformId) {
  const startedAt = Date.now();
  let previousText = "";
  let stableCount = 0;
  while (Date.now() - startedAt < 180000) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const page = await client.evaluate(`(() => {
      const bodyText = document.body?.innerText || "";
      const yuanbaoRoot = document.querySelector(
        ".agent-dialogue__content--common"
      );
      const doubaoRoots = [...document.querySelectorAll(
        "[class*='message-list-']"
      )];
      const doubaoRoot = doubaoRoots
        .sort((a, b) => (b.innerText || "").length - (a.innerText || "").length)[0];
      return {
        href: location.href,
        bodyText,
        answerText: (yuanbaoRoot?.innerText || doubaoRoot?.innerText || "").trim()
      };
    })()`);
    if (/算力紧张|当前排队人数较多|请稍后再试/.test(page.answerText)) {
      return {
        text: page.answerText,
        bodyText: page.bodyText,
        href: page.href,
        complete: false,
        error: "平台算力或服务繁忙",
      };
    }
    const text = page.answerText;
    const busy = /正在思考|深度思考中|正在搜索相关资料|停止生成/.test(text);
    const completeMarker =
      platformId === "doubao" ? /共用时/.test(text) : text.length >= 500;
    const grew =
      text.length >= 500 &&
      completeMarker &&
      !busy &&
      page.bodyText.length > initialText.length + 300;
    if (grew && text === previousText) {
      stableCount += 1;
    } else {
      stableCount = 0;
    }
    previousText = text;
    if (grew && stableCount >= 4 && Date.now() - startedAt >= 10000) {
      return {
        text,
        bodyText: page.bodyText,
        href: page.href,
        complete: true,
      };
    }
  }
  return {
    text: previousText,
    bodyText: previousText,
    href: await client.evaluate("location.href"),
    complete: false,
    error: "答案生成超时或未成功提交",
  };
}

async function probeOne(platformId, item) {
  const platform = platforms[platformId];
  const target = await createTarget(platform.startUrl);
  const client = new CdpClient(target.webSocketDebuggerUrl);
  const startedAt = new Date().toISOString();
  try {
    await client.connect();
    const initialState = await waitForInput(client, platform);
    await submitQuery(client, item.query);
    const answer = await waitForAnswer(
      client,
      initialState.text,
      platformId,
    );
    return {
      id: item.id,
      query: item.query,
      startedAt,
      completedAt: new Date().toISOString(),
      complete: answer.complete,
      url: answer.href,
      text: answer.text,
      bodyText: answer.bodyText,
      error: answer.error || "",
    };
  } catch (error) {
    return {
      id: item.id,
      query: item.query,
      startedAt,
      completedAt: new Date().toISOString(),
      complete: false,
      url: "",
      text: "",
      bodyText: "",
      error: error.message,
    };
  } finally {
    client.close();
    await closeTarget(target.id);
  }
}

async function main() {
  const { platformId, output, ids, plan } = parseArgs();
  const selectedQueries = await loadQueries(platformId, ids, plan);
  if (!selectedQueries.length) {
    throw new Error("当天计划中没有匹配的测试题");
  }
  const results = [];
  for (const item of selectedQueries) {
    console.log(`${platforms[platformId].label}开始测试：${item.id}`);
    const result = await probeOne(platformId, item);
    results.push(result);
    console.log(
      `${platforms[platformId].label}${item.id}：${
        result.complete ? "完成" : `失败 ${result.error}`
      }`,
    );
  }

  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(
    output,
    `${JSON.stringify(
      {
        platform: platformId,
        label: platforms[platformId].label,
        cdp: cdpBase,
        generatedAt: new Date().toISOString(),
        results,
      },
      null,
      2,
    )}\n`,
    "utf8",
  );
  console.log(`结果已保存：${output}`);
}

main().catch((error) => {
  console.error(`复测失败：${error.message}`);
  process.exit(2);
});
