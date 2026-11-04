#!/usr/bin/env node

const cdpBase = (process.env.CDP_URL || "http://127.0.0.1:9223").replace(
  /\/+$/,
  "",
);

const platforms = [
  {
    id: "doubao",
    label: "豆包",
    urlIncludes: "doubao.com",
    loggedOut: /扫码登录|手机号登录|登录后即可|登录后继续/,
    loggedIn: /退出登录|账号设置|账户设置/,
    loggedInSignals: ["新工作任务", "最近"],
  },
  {
    id: "yuanbao",
    label: "元宝",
    urlIncludes: "yuanbao.tencent.com",
    loggedOut: /未登录|扫码登录|手机号登录|登录后继续/,
    loggedIn: /退出登录|账号设置|账户设置/,
    loggedInSignals: ["新建对话", "最近"],
  },
];

async function fetchTargets() {
  const response = await fetch(`${cdpBase}/json/list`);
  if (!response.ok) {
    throw new Error(`无法读取 Chrome 标签页，HTTP ${response.status}`);
  }
  const targets = await response.json();
  return targets.filter((target) => target.type === "page");
}

function evaluate(target, expression) {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(target.webSocketDebuggerUrl);
    const timer = setTimeout(() => {
      socket.close();
      reject(new Error(`${target.title || target.url} 读取超时`));
    }, 10000);

    socket.addEventListener("open", () => {
      socket.send(
        JSON.stringify({
          id: 1,
          method: "Runtime.evaluate",
          params: {
            expression,
            returnByValue: true,
            awaitPromise: true,
          },
        }),
      );
    });

    socket.addEventListener("message", async (event) => {
      const raw =
        typeof event.data === "string"
          ? event.data
          : await new Response(event.data).text();
      const message = JSON.parse(raw);
      if (message.id !== 1) {
        return;
      }
      clearTimeout(timer);
      socket.close();
      if (message.error || message.result?.exceptionDetails) {
        reject(new Error(JSON.stringify(message.error || message.result)));
        return;
      }
      resolve(message.result?.result?.value);
    });

    socket.addEventListener("error", () => {
      clearTimeout(timer);
      reject(new Error("Chrome CDP WebSocket 连接失败"));
    });
  });
}

function classify(text, config) {
  if (config.loggedOut.test(text)) {
    return "logged_out";
  }
  if (config.loggedIn.test(text)) {
    return "logged_in";
  }
  if (
    config.loggedInSignals?.length &&
    config.loggedInSignals.every((signal) => text.includes(signal))
  ) {
    return "logged_in";
  }
  return "unknown";
}

async function main() {
  let targets;
  try {
    targets = await fetchTargets();
  } catch (error) {
    console.error(`登录态检查失败：${error.message}`);
    process.exit(2);
  }

  const results = [];
  for (const config of platforms) {
    const target = targets.find((item) =>
      String(item.url || "").includes(config.urlIncludes),
    );
    if (!target) {
      results.push({
        id: config.id,
        label: config.label,
        status: "missing_tab",
        url: "",
      });
      continue;
    }

    const page = await evaluate(
      target,
      `({
        title: document.title,
        url: location.href,
        text: (document.body?.innerText || "").slice(0, 20000)
      })`,
    );
    results.push({
      id: config.id,
      label: config.label,
      status: classify(page.text || "", config),
      title: page.title || "",
      url: page.url || target.url,
    });
  }

  for (const result of results) {
    console.log(
      `${result.label}: ${result.status}${result.url ? ` | ${result.url}` : ""}`,
    );
  }

  if (results.some((result) => result.status !== "logged_in")) {
    process.exit(2);
  }
}

main().catch((error) => {
  console.error(`登录态检查失败：${error.message}`);
  process.exit(2);
});
