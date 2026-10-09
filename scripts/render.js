// Renders src/video.html frame-by-frame with Playwright and encodes it with ffmpeg.
//
//   node scripts/render.js                 -> output/eka_knowledge_hub_60s.mp4 (with output/mix.wav if present)
//   node scripts/render.js --stills 1,7,12 -> output/stills/t_<sec>.png for quick checks
const { chromium } = require("playwright");
const { spawn, execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const URL = "file://" + path.join(ROOT, "src/video.html");
const FPS = 30;
const WORKERS = Number(process.env.WORKERS || 4);
const OUT = path.join(ROOT, "output");

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(URL);
  await page.evaluate(() => window.ready);
  return page;
}

async function stills(times) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  fs.mkdirSync(path.join(OUT, "stills"), { recursive: true });
  for (const t of times) {
    await page.evaluate(t => window.render(t), t);
    const f = path.join(OUT, "stills", `t_${String(t).padStart(5, "0")}.png`);
    await page.screenshot({ path: f });
    console.log(f);
  }
  await browser.close();
}

async function renderSegment(browser, idx, from, to, file) {
  const page = await openPage(browser);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", String(FPS), file], { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error("ffmpeg " + c)))));
  for (let f = from; f < to; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: "png" });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if ((f - from) % 60 === 0) console.log(`worker ${idx}: frame ${f}/${to}`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

async function full() {
  const browser = await chromium.launch();
  const total = await (async () => { const p = await openPage(browser); const d = await p.evaluate(() => window.DURATION); await p.close(); return Math.round(d * FPS); })();
  const segDir = path.join(OUT, "segments");
  fs.mkdirSync(segDir, { recursive: true });
  const per = Math.ceil(total / WORKERS);
  const segs = [];
  const jobs = [];
  for (let w = 0; w < WORKERS; w++) {
    const from = w * per, to = Math.min(total, from + per);
    if (from >= to) break;
    const file = path.join(segDir, `seg_${w}.mp4`);
    segs.push(file);
    jobs.push(renderSegment(browser, w, from, to, file));
  }
  await Promise.all(jobs);
  await browser.close();

  const list = path.join(segDir, "list.txt");
  fs.writeFileSync(list, segs.map(s => `file '${s}'`).join("\n"));
  const silent = path.join(OUT, "eka_knowledge_hub_60s_noaudio.mp4");
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", silent], { stdio: "inherit" });
  const mix = path.join(OUT, "mix.wav");
  if (fs.existsSync(mix)) {
    const final = path.join(OUT, "eka_knowledge_hub_60s.mp4");
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", silent, "-i", mix, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", final], { stdio: "inherit" });
    console.log("wrote", final);
  }
  console.log("wrote", silent);
}

const i = process.argv.indexOf("--stills");
if (i > -1) stills(process.argv[i + 1].split(",").map(Number));
else full();
