#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the Jay Chou (周杰伦) skin for DeepSeek Harness Web — v6 电影感极简版.
Outputs:
  jaychou-skin.css      — standalone stylesheet (Stylus / console / plugin)
  plugin/package.json   — client-plugin package manifest
  plugin/index.js       — host-side stub
  plugin/client.js      — built client bundle (registers theme + injects skin)
"""
import base64
import io
import json
import os

from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OPT = os.path.join(HERE, "opt")  # original covers at native aspect ratio
SQ = os.path.join(OPT, "sq")  # square center-cropped covers
PLUGIN = os.path.join(HERE, "plugin")

def cover_square(img, size):
    """Center-crop to square then resize, so the cover never distorts."""
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    return img.crop((left, top, left + s, top + s)).resize((size, size), Image.LANCZOS)


# 单封面氛围壁纸：只取一张最暗最 moody 的封面，烘焙成朦胧的午夜蓝光斑。
AMBIENT_COVER = "05-novembers-chopin.jpg"  # 十一月的萧邦
AMBIENT_SIZE = 1280


def build_ambient(size=AMBIENT_SIZE):
    """Turn one album cover into a visible-but-soft ambient backdrop.

    Moderate desaturation + soft blur keeps the cover recognizable as a moody
    glow — visible, not a loud collage and not pitch black. Shapes stay, colours
    are muted, and a light navy veil unifies the hue into the midnight palette.
    """
    with Image.open(os.path.join(SQ, AMBIENT_COVER)) as src:
        img = cover_square(src.convert("RGB"), size)
    img = ImageEnhance.Color(img).enhance(0.65)       # 保留更多色彩
    img = ImageEnhance.Brightness(img).enhance(1.15)  # 略提亮
    img = ImageEnhance.Contrast(img).enhance(1.00)
    img = img.filter(ImageFilter.GaussianBlur(6))     # 更清晰，封面可辨认
    veil = Image.new("RGB", img.size, (8, 11, 17))    # 极轻罩统一色相
    img = Image.blend(img, veil, 0.08)
    return img


def ambient_datauri(size=AMBIENT_SIZE):
    img = build_ambient(size)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


# 右下角签名区的专辑封面小图（4 张，读自 opt/sq/ 正方形裁剪图）
COVERS = ["01-fantasy.jpg", "06-still-fantasy.jpg", "08-capricorn.jpg", "09-the-era.jpg"]
THUMB_SIZE = 80  # px，供 36px 展示位使用（含 retina 余量）


def thumb_datauri(name, size=THUMB_SIZE):
    with Image.open(os.path.join(SQ, name)) as src:
        img = cover_square(src.convert("RGB"), size)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def thumb_vars(names, prefix):
    return "\n".join(
        f'  --jc-{prefix}{i+1}: url("{thumb_datauri(name)}");'
        for i, name in enumerate(names)
    )


# cover urls exposed once as CSS variables (dedupes repeated embedding)
COVER_VARS = f"""body {{
  --jc-wallpaper: url("{ambient_datauri()}");
{thumb_vars(COVERS, "c")}
}}"""

# ---------------------------------------------------------------------------
# token dictionaries (v6 alphas: near-opaque panels over the faint ambient)
# ---------------------------------------------------------------------------
DARK_TOKENS = {
    "--dsw-alias-bg-base": "rgba(8,11,17,0.46)",
    "--dsw-alias-bg-layer-1": "rgba(10,14,21,0.44)",
    "--dsw-alias-bg-layer-2": "rgba(12,17,25,0.42)",
    "--dsw-alias-bg-layer-3": "rgba(14,20,30,0.40)",
    "--dsw-alias-bg-mask-1": "rgba(0,0,0,0.60)",
    "--dsw-alias-bg-mask-2": "rgba(0,0,0,0.2)",
    "--dsw-alias-bg-mask-3": "rgba(0,0,0,0.56)",
    "--dsw-alias-bg-mask-photo": "rgba(0,0,0,0.88)",
    "--dsw-alias-bg-mask-drop": "rgba(8,11,17,0.7)",
    "--dsw-alias-bg-module-platform": "rgba(10,14,21,0.48)",
    "--dsw-alias-bg-multi-select": "rgba(14,19,28,0.60)",
    "--dsw-alias-bg-overlay": "rgba(16,21,32,0.94)",
    "--dsw-alias-bg-skeleton": "rgba(212,175,55,0.10)",
    "--dsw-alias-border-inverted2": "rgba(212,175,55,0.10)",
    "--dsw-alias-border-inverted": "rgba(212,175,55,0.08)",
    "--dsw-alias-border-l1": "rgba(212,175,55,0.10)",
    "--dsw-alias-border-l2-darkmode-thin": "rgba(212,175,55,0.12)",
    "--dsw-alias-border-l2": "rgba(212,175,55,0.16)",
    "--dsw-alias-border-l3": "rgba(212,175,55,0.22)",
    "--dsw-alias-border-l4": "rgba(212,175,55,0.30)",
    "--dsw-alias-brand-primary-invert": "#0a0d13",
    "--dsw-alias-brand-primary-new-colorprimary-new-color": "#d4af37",
    "--dsw-alias-brand-primary": "#d4af37",
    "--dsw-alias-brand-text": "#e8c766",
    "--dsw-alias-button-contrast-fill": "#d4af37",
    "--dsw-alias-button-elevated-fill": "rgba(12,16,24,0.60)",
    "--dsw-alias-button-floating-fill": "rgba(12,16,24,0.65)",
    "--dsw-alias-button-floating-hover": "rgba(16,21,32,0.72)",
    "--dsw-alias-button-ghost-active-border": "rgba(212,175,55,0.45)",
    "--dsw-alias-button-ghost-active-fill": "rgba(212,175,55,0.14)",
    "--dsw-alias-button-ghost-active-hover": "rgba(212,175,55,0.20)",
    "--dsw-alias-button-info-fill": "#c9a227",
    "--dsw-alias-button-info-hover": "#d4af37",
    "--dsw-alias-button-primary-dimmed": "rgba(212,175,55,0.16)",
    "--dsw-alias-button-primary-fill": "#d4af37",
    "--dsw-alias-button-primary-hover": "#e6c55e",
    "--dsw-alias-button-tool-bar-fill-invisible": "rgba(212,175,55,0.18)",
    "--dsw-alias-button-tool-bar-fill": "rgba(212,175,55,0.28)",
    "--dsw-alias-button-tool-bar-hover": "rgba(212,175,55,0.38)",
    "--dsw-alias-interactive-bg-active": "rgba(212,175,55,0.12)",
    "--dsw-alias-interactive-bg-hover-accent": "rgba(212,175,55,0.16)",
    "--dsw-alias-interactive-bg-hover-danger": "rgba(242,90,90,0.15)",
    "--dsw-alias-interactive-bg-hover-solid": "rgba(16,21,32,0.65)",
    "--dsw-alias-interactive-bg-hover": "rgba(212,175,55,0.08)",
    "--dsw-alias-label-caption": "#83795f",
    "--dsw-alias-label-dimmed": "#4a4230",
    "--dsw-alias-label-primary-bluish": "#f2ead8",
    "--dsw-alias-label-primary-dimmed": "#efe6d0",
    "--dsw-alias-label-primary-foreground": "#1c1503",
    "--dsw-alias-label-primary-inverted": "#2a2110",
    "--dsw-alias-label-primary": "#f2ead8",
    "--dsw-alias-label-secondary": "#cbbfa3",
    "--dsw-alias-label-tertiary": "#9a8f74",
    "--dsw-alias-markdown-citation": "rgba(212,175,55,0.10)",
    "--dsw-alias-markdown-code-block-banner": "rgba(8,10,15,0.85)",
    "--dsw-alias-markdown-code-block": "rgba(8,10,15,0.88)",
    "--dsw-alias-markdown-code-segment-selected": "rgba(212,175,55,0.14)",
    "--dsw-alias-markdown-code-segment-unselected": "rgba(8,10,15,0.88)",
    "--dsw-alias-markdown-inline-code": "rgba(212,175,55,0.12)",
    "--dsw-alias-markdown-placeholder": "rgba(212,175,55,0.06)",
    "--dsw-alias-markdown-tag": "rgba(212,175,55,0.12)",
    "--dsw-alias-scrollbar-bg-l1": "#26241c",
    "--dsw-alias-scrollbar-bg-l2": "#312d20",
    "--dsw-alias-scrollbar-hover-l1": "#40391f",
    "--dsw-alias-scrollbar-hover-l2": "#4c4322",
    "--dsw-alias-state-business-primary": "#d4af37",
    "--dsw-alias-state-business-tertiary": "rgba(212,175,55,0.15)",
    "--dsw-alias-state-error-primary": "#f05252",
    "--dsw-alias-state-error-secondary": "#f05252",
    "--dsw-alias-state-success-primary": "#4cc38a",
    "--dsw-alias-state-success-secondary": "#34d399",
    "--dsw-alias-state-success-tertiary": "rgba(76,195,138,0.15)",
    "--dsw-alias-state-warn-label": "#f0b429",
    "--dsw-alias-state-warn-primary": "#f0b429",
    "--dsw-alias-state-warn-secondary": "#eaa03f",
    "--dsw-alias-state-warn-tertiary": "rgba(240,180,41,0.15)",
    "--dsw-alias-toast-bg": "rgba(18,24,36,0.97)",
    "--dsw-alias-tooltip-bg": "rgba(18,24,36,0.97)",
    "--dsw-specific-bubble-highlight": "rgba(212,175,55,0.10)",
    "--dsw-specific-bubble": "rgba(10,14,21,0.88)",
    "--dsw-specific-input-major": "rgba(8,11,17,0.60)",
    "--dsw-specific-login-input": "rgba(9,12,18,0.94)",
    "--dsw-specific-menu": "rgba(14,19,28,0.96)",
    "--dsw-specific-selector": "rgba(14,19,28,0.85)",
    "--dsw-specific-sidebar-fill": "rgba(6,9,14,0.44)",
    "--dsw-specific-sidebar-nav-item-active-accent": "#d4af37",
    "--dsw-specific-sidebar-nav-item-active": "rgba(212,175,55,0.12)",
    "--dsw-specific-sidebar-nav-item-hover": "rgba(212,175,55,0.07)",
    "--dsw-specific-tip": "rgba(212,175,55,0.08)"
}

# ---------------------------------------------------------------------------
# 2. imagery css (v7: single-cover ambient wallpaper + side cover thumbnails)
# ---------------------------------------------------------------------------
IMAGERY_CSS = f"""/* ============================================================
   周杰伦 Jay Chou 主题皮肤 · 装饰层 v7
   单封面氛围壁纸（顶部构图）+ 左右专辑封面小图边框
   ============================================================ */

/* 封面素材只内嵌一次，通过 CSS 变量复用 */
{COVER_VARS}

/* 页面底色：午夜蓝 */
html {{
  background-color: #080b11;
}}
body {{
  background-color: #080b11 !important;
}}

/* 全屏氛围壁纸：单张封面烘焙成朦胧光斑，仅作气氛；
   取顶部构图（center top）露出人物头部，四周轻收暗（vignette） */
body::before {{
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 78% 68% at 50% 42%, rgba(8,11,17,0.00) 0%, rgba(8,11,17,0.24) 100%),
    var(--jc-wallpaper) center top / cover no-repeat,
    #080b11;
}}

/* 应用内容层盖在壁纸之上 */
#root {{
  position: relative;
  z-index: 1;
}}

/* 输入框：极细鎏金描边 */
[data-composer-card] {{
  box-shadow: 0 0 0 1px rgba(212,175,55,0.22), 0 12px 36px rgba(0,0,0,0.40) !important;
}}

/* 右下角签名：♫ jaychou 金色名牌 + 4 张小封面（唱片架） */
body::after {{
  content: "♫ jaychou";
  position: fixed;
  right: 14px;
  bottom: 12px;
  z-index: 9;
  pointer-events: none;
  width: 236px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: rgba(212,175,55,0.88);
  font: 600 12px/1 ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  letter-spacing: 0.08em;
  text-shadow: 0 1px 8px rgba(0,0,0,0.9);
  background:
    linear-gradient(90deg, rgba(8,11,17,0.55) 0%, transparent 32%),
    var(--jc-c1) right 128px top 2px / 36px auto no-repeat,
    var(--jc-c2) right 86px top 2px / 36px auto no-repeat,
    var(--jc-c3) right 44px top 2px / 36px auto no-repeat,
    var(--jc-c4) right 2px top 2px / 36px auto no-repeat;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.6));
}}
@media (max-width: 900px) {{
  body::after {{ display: none; }}
}}

/* 聊天区：适度暗化让壁纸若隐若现、文字清晰（气泡本身不透明） */
[data-conversation-scroll] {{
  background: rgba(8,11,17,0.28);
}}

/* 选区 */
::selection {{
  background: rgba(212,175,55,0.85);
  color: #1c1503;
}}

/* 滚动条：鎏金 */
body {{
  --dsh-scrollbar-thumb: rgba(212,175,55,0.34);
  --dsh-scrollbar-thumb-hover: rgba(212,175,55,0.55);
}}
"""

# ---------------------------------------------------------------------------
# 3. standalone stylesheet (tokens + imagery)
# ---------------------------------------------------------------------------
def token_block(selector, tokens):
    lines = [selector + " {"]
    for k, v in tokens.items():
        lines.append(f"  {k}: {v} !important;")
    lines.append("}")
    return "\n".join(lines)

# DeepSeek brand-blue statics -> gold (components that read statics directly)
STATIC_OVERRIDES = f"""/* DeepSeek 品牌蓝 → 鎏金（静态 token 兜底） */
body {{
  --dsw-static-deepseek-50: #f7efd4 !important;
  --dsw-static-deepseek-100: #efe0ac !important;
  --dsw-static-deepseek-200: #e6cf82 !important;
  --dsw-static-deepseek-300: #d9bc5e !important;
  --dsw-static-deepseek-400: #d4af37 !important;
  --dsw-static-deepseek-450: #c9a227 !important;
  --dsw-static-deepseek-500: #b8912f !important;
  --dsw-static-deepseek-600: #96771f !important;
  --dsw-static-deepseek-700-delete: #6b5410 !important;
  --dsw-static-deepseek-800: #4a3d14 !important;
  --dsw-static-deepseek-900: #3a3010 !important;
}}
"""

FX_CSS = """/* ---------- ③ 音符特效 + 签名呼吸 ---------- */
.jc-notes { position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 40; }
.jc-note { position: absolute; bottom: -40px; color: #d4af37; font-family: Georgia, "Times New Roman", serif; line-height: 1; animation-name: jc-note-float; animation-timing-function: linear; animation-iteration-count: infinite; will-change: transform, opacity; text-shadow: 0 0 14px rgba(212,175,55,0.5); }
@keyframes jc-note-float { 0% { transform: translateY(0) translateX(0) rotate(-8deg); opacity: 0; } 12% { opacity: 0.30; } 85% { opacity: 0.18; } 100% { transform: translateY(-104vh) translateX(30px) rotate(16deg); opacity: 0; } }
body::after { animation: jc-sig-breathe 3.2s ease-in-out infinite; }
@keyframes jc-sig-breathe { 0%, 100% { opacity: 0.85; } 50% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .jc-note { animation: none; display: none; } body::after { animation: none; } }
"""

NOTES = [
    {"left": "12%", "dur": 11, "delay": 0, "glyph": "♪", "size": 18},
    {"left": "27%", "dur": 9, "delay": 2.5, "glyph": "♫", "size": 14},
    {"left": "42%", "dur": 13, "delay": 5, "glyph": "♪", "size": 16},
    {"left": "58%", "dur": 10, "delay": 1.5, "glyph": "♫", "size": 15},
    {"left": "74%", "dur": 12, "delay": 4, "glyph": "♪", "size": 18},
    {"left": "88%", "dur": 9.5, "delay": 7, "glyph": "♫", "size": 13},
]

STANDALONE_CSS = f"""/* ============================================================
   周杰伦 Jay Chou 主题皮肤 · DeepSeek Harness Web（v10 音符版）
   风格：夜的第七章 —— 午夜蓝 × 鎏金 × 单封面朦胧氛围光 × 上浮音符
   应用方式见 README.md（Stylus / 控制台 / 客户端插件）
   封面素材来源：Wikipedia（非自由版权图，仅个人本地使用）
   ============================================================ */

/* ---------- ① 语义 token 覆盖（强制深色，不依赖主题属性） ---------- */

{token_block("body", DARK_TOKENS)}

/* ---------- ①b DeepSeek 品牌蓝 → 鎏金 ---------- */

{STATIC_OVERRIDES}

/* ---------- ② 专辑封面装饰 ---------- */

{IMAGERY_CSS}

/* ---------- ③ 音符特效 + 签名呼吸 ---------- */

{FX_CSS}
"""

PLUGIN_CSS = f"""/* ============================================================
   周杰伦 Jay Chou 主题皮肤 · 插件注入层（v10 音符版）
   token 覆盖带 !important：免疫 ThemePresenter 的 inline 收回
   ============================================================ */

{token_block("body", DARK_TOKENS)}

{STATIC_OVERRIDES}

{IMAGERY_CSS}

{FX_CSS}
"""

with open(os.path.join(HERE, "jaychou-skin.css"), "w", encoding="utf-8") as f:
    f.write(STANDALONE_CSS)

# ---------------------------------------------------------------------------
# 4. plugin package
# ---------------------------------------------------------------------------
os.makedirs(PLUGIN, exist_ok=True)

with open(os.path.join(PLUGIN, "package.json"), "w", encoding="utf-8") as f:
    json.dump({
        "name": "jaychou-skin",
        "version": "0.1.0",
        "private": True,
        "description": "周杰伦主题皮肤（DeepSeek Harness Web）：午夜蓝 × 鎏金 × 单封面氛围光",
        "type": "module",
        "main": "index.js",
        "exports": {
            ".": "./index.js",
            "./client": "./client.js",
            "./package.json": "./package.json",
        },
        "dsh": {
            "client": {
                "platform": "web",
                "inject": ["@deepseek-ai/dsh-client-ui-theme"],
                "immediately": True,
            }
        },
    }, f, ensure_ascii=False, indent=2)
    f.write("\n")

with open(os.path.join(PLUGIN, "index.js"), "w", encoding="utf-8") as f:
    f.write("""// Host-side stub for the jaychou-skin client plugin.
// The real work happens in the browser half (./client.js).
export const name = "jaychou-skin";
export const apply = () => {};
""")

# ---------------------------------------------------------------------------
# 5. client bundle (template preserved from the working v2 build)
# ---------------------------------------------------------------------------
skin_css_js = json.dumps(PLUGIN_CSS)
tokens_js = json.dumps(DARK_TOKENS, ensure_ascii=False)
notes_js = json.dumps(NOTES, ensure_ascii=False)

FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="7" fill="#0a0d13"/>'
    '<text x="16" y="23" font-size="19" text-anchor="middle" fill="#d4af37" '
    'font-family="Georgia, serif">\u266a</text></svg>'
)


client_js = f"""// Built client bundle for the jaychou-skin client plugin.
// - Registers the 'jaychou' dark theme on the ThemeRuntime (for the settings
//   surface / inspection) and activates it;
// - Injects the full skin stylesheet (token overrides carry !important, so
//   the ui-layout ThemePresenter's inline retraction cannot undo the palette);
// - Swaps the favicon to a gold note.
// exports.inject uses SERVICE names: the fiber waits for the "theme" service
// provided by @deepseek-ai/dsh-client-ui-theme (never package names).
window.__ModuleLoader__.load({{
  id: "jaychou-skin",
  factory: (require) => {{
    var module = {{ exports: {{}} }};
    var exports = module.exports;
    Object.defineProperty(exports, Symbol.toStringTag, {{ value: "Module" }});

    var SKIN_CSS = {skin_css_js};
    var TOKENS = {tokens_js};
    var NOTES = {notes_js};

    function mountNotes() {{
      var el = document.createElement("div");
      el.className = "jc-notes";
      el.setAttribute("aria-hidden", "true");
      for (var i = 0; i < NOTES.length; i++) {{
        var n = NOTES[i];
        var s = document.createElement("span");
        s.className = "jc-note";
        s.textContent = n.glyph;
        s.style.left = n.left;
        s.style.fontSize = n.size + "px";
        s.style.animationDuration = n.dur + "s";
        s.style.animationDelay = "-" + n.delay + "s";
        el.appendChild(s);
      }}
      document.body.appendChild(el);
      return el;
    }}

    function setFavicon() {{
      try {{
        var href = "data:image/svg+xml;charset=utf-8," + encodeURIComponent({json.dumps(FAVICON_SVG)});
        var link = document.querySelector('link[rel="icon"]');
        if (link) link.href = href;
      }} catch (e) {{ /* non-fatal */ }}
    }}

    /**
     * Register the 'jaychou' dark theme, activate it, and inject the
     * album-cover decoration layer. Idempotent across fiber re-entries.
     */
    function apply(ctx) {{
      var disposeTheme = function () {{}};
      try {{
        disposeTheme = ctx.theme.register({{
          id: "jaychou",
          colorScheme: "dark",
          tokens: TOKENS
        }});
      }} catch (e) {{
        // already registered (fiber re-entry / HMR) — keep the existing one
      }}

      var tagId = "jaychou-skin/skin.css";
      var style = document.createElement("style");
      style.dataset.plugin = "jaychou-skin";
      style.dataset.pluginCss = tagId;
      style.textContent = SKIN_CSS;
      document.head.appendChild(style);

      // Force the dark base palette attribute so the base dark tokens and the
      // skin's unconditional overrides are both active, regardless of the OS
      // preference or the async settings adoption.
      document.body.setAttribute("data-ds-dark-theme", "");

      try {{ ctx.theme.setTheme("jaychou"); }} catch (e) {{ /* not registered yet? */ }}
      setFavicon();

      var notesEl = mountNotes();

      // The Host settings scope adopts its persisted preference asynchronously
      // after connection; third-party theme ids are in-process only, so that
      // adoption resets the preference (to "system") right after we activate.
      // Re-assert jaychou within a short window so the adopted default cannot
      // flip the color-scheme attribute; later manual preference changes are
      // left alone (the light token block then takes over).
      var __reassertDeadline = Date.now() + 30000;
      ctx.on("theme/change", function (__snap) {{
        // Re-assert the dark base attribute AFTER the current dispatch so the
        // ThemePresenter (which may remove it for a light snapshot) cannot win
        // the attribute race; the unconditional token block works either way.
        queueMicrotask(function () {{
          document.body.setAttribute("data-ds-dark-theme", "");
        }});
        if (Date.now() <= __reassertDeadline && __snap.active.id !== "jaychou") {{
          try {{ ctx.theme.setTheme("jaychou"); }} catch (e) {{}}
        }}
      }});

      // NOTE: ctx.effect(fn) in this client framework RUNS fn immediately and
      // collects its RETURN value as the unload cleanup (React-effect style:
      // `() => {{ setup(); return () => teardown(); }}`). So the teardown must be
      // RETURNED, otherwise the style/theme are disposed on the spot.
      ctx.effect(() => () => {{
        disposeTheme();
        style.remove();
        notesEl.remove();
      }}, "jaychou-skin: teardown");
    }}

    var inject = ["theme"];
    exports.apply = apply;
    exports.inject = inject;
    return module.exports;
  }}
}});
"""

with open(os.path.join(PLUGIN, "client.js"), "w", encoding="utf-8") as f:
    f.write(client_js)

# ---------------------------------------------------------------------------
print("OK")
print("jaychou-skin.css:", round(os.path.getsize(os.path.join(HERE, "jaychou-skin.css")) / 1024, 1), "KB")
print("plugin/client.js:", round(os.path.getsize(os.path.join(PLUGIN, "client.js")) / 1024, 1), "KB")
