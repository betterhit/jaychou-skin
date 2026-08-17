# 周杰伦主题皮肤 · DeepSeek Harness Web

一个给 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) Web GUI 的深色主题皮肤。
风格灵感来自《夜的第七章》《十一月的萧邦》：**午夜蓝 × 鎏金 × 单封面氛围光 × 上浮音符**。

> ⚠️ **版权声明**：本皮肤内嵌的专辑封面取自 Wikipedia（非自由版权缩略图），**仅限个人本地使用，请勿公开分发或商用**。若需公开，请先替换为自有授权的图片。

<img width="1440" height="900" alt="screenshot" src="https://github.com/user-attachments/assets/70d2de9e-6565-4ab8-a51a-f28bbd971823" />


## 特性

- **午夜蓝 × 鎏金**配色，强制深色，不随系统/设置偏好变化；
- **单封面朦胧氛围壁纸**：《十一月的萧邦》，顶部构图、去饱和+模糊+轻罩；
- **6 枚金色音符**从底部缓缓上浮（克制、半透明、不挡点击）；
- **右下角「♫ jaychou」签名 + 4 张专辑小封面**（唱片架）；
- **尊重系统「减少动态」设置**：开启后自动停掉动画。

## 安装

### 方式 A：客户端插件（推荐）

```sh
cd ~/.dsh/profiles/web
pnpm add "file:/绝对路径/jaychou-skin/plugin"
# 或用打包好的 tarball：
# pnpm add /绝对路径/jaychou-skin-0.1.0.tgz
```

在 `~/.dsh/profiles/web/cordis.patch.yml` 里追加：

```yaml
- insert:
    - id: jaychou-skin
      name: jaychou-skin
```

重启 `dsh web` 并刷新页面。

### 方式 B：Stylus / 浏览器注入

用 Stylus 把 `jaychou-skin.css` 作用于 `http://127.0.0.1:3080`。

> 注：浮动音符需要 JS 创建 DOM 元素，Stylus 方式只有配色/壁纸/签名，没有音符特效。

## 构建

改完配置后重新生成全部产物（`jaychou-skin.css` 与 `plugin/`）：

```sh
python3 build-skin.py
```

## 自定义

| 想改什么 | 改哪里 |
|---|---|
| 壁纸封面 | `build-skin.py` 顶部 `AMBIENT_COVER` |
| 小封面 | `COVERS` 列表 |
| 壁纸亮度/模糊/色调 | `build_ambient()` 里的 `Color/Brightness/Blur/veil` |
| 音符数量/位置/速度 | `NOTES` 列表 + `FX_CSS` 里的 keyframes |
| 配色 | `DARK_TOKENS` |

## 目录

```
jaychou-skin/
├── build-skin.py       # 构建脚本（唯一源，重跑即重新生成）
├── jaychou-skin.css    # 独立样式（Stylus 用，构建产物）
├── plugin/             # 客户端插件包（分发对象，自包含）
├── albums/             # 14 张原始封面素材
└── opt/sq/             # 方形裁剪封面（构建实际读取）
```

## 许可

代码仅供个人本地使用。内嵌专辑封面版权归原作者所有，**请勿再分发**。详见 `LICENSE`。
