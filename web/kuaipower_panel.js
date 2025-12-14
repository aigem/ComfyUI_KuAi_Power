import { app } from "../../scripts/app.js";

app.registerExtension({
  name: "KuAi.Panel",
  async setup() {
    // 分类中文映射
    const categoryNameMap = {
      "ScriptGenerator": "📝 脚本生成",
      "Sora2": "🎬 Sora2 视频生成",
      "Veo3": "🚀 Veo3.1 视频生成",
      "Grok": "🤖 Grok 视频生成",
      "NanoBanana": "🍌 Nano Banana 图像生成",
      "Utils": "🛠️ 工具节点",
      "Product": "📦 产品管理",
      "配套能力": "🛠️ 配套能力"
    };

    // 自动发现节点
    const discoverNodes = () => {
      const categories = {};

      for (const [nodeType, nodeClass] of Object.entries(LiteGraph.registered_node_types)) {
        const category = nodeClass.category;
        if (category && (category.toLowerCase().startsWith("kuai/") || category.toLowerCase().startsWith("kuaipower/"))) {
          const categoryName = category.split("/")[1];
          const displayCategory = categoryNameMap[categoryName] || categoryName;

          if (!categories[displayCategory]) {
            categories[displayCategory] = [];
          }

          const displayName = nodeClass.display_name || nodeClass.title || nodeType;

          categories[displayCategory].push({
            name: nodeType,
            display: displayName
          });
        }
      }

      return categories;
    };

    // 防抖函数
    const debounce = (func, wait) => {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    };

    // 注册左侧侧边栏按钮
    app.extensionManager.registerSidebarTab({
      id: "kuaipower-panel",
      icon: "pi pi-cog",
      title: "KuAi Power 节点",
      tooltip: "快捷键：Ctrl + Shift + K",
      type: "custom",
      render: (el) => {
        // 容器样式
        el.style.cssText = `
          padding: 12px;
          background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%);
          color: #e0e0e0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
          height: 100%;
          overflow-y: auto;
          box-sizing: border-box;
        `;

        // 标题栏
        const header = document.createElement("div");
        header.style.cssText = `
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 2px solid #4a9eff;
        `;
        header.innerHTML = `
          <span style="font-size:16px;font-weight:600;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,0.3);">🔧 KuAi Power</span>
          <button id="kuai-close" style="background:none;border:none;color:#888;cursor:pointer;font-size:20px;transition:color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#888'">×</button>
        `;
        el.appendChild(header);

        // 搜索框
        const searchContainer = document.createElement("div");
        searchContainer.style.cssText = "margin-bottom:12px;position:relative;";
        searchContainer.innerHTML = `
          <input 
            id="kuai-search" 
            type="text" 
            placeholder="🔍 搜索节点..." 
            style="
              width:100%;
              padding:8px 32px 8px 10px;
              background:#2a2a2a;
              border:1px solid #3e3e3e;
              border-radius:6px;
              color:#e0e0e0;
              font-size:13px;
              box-sizing:border-box;
              transition:border-color 0.2s;
            "
            onfocus="this.style.borderColor='#4a9eff'"
            onblur="this.style.borderColor='#3e3e3e'"
          />
          <span id="kuai-clear" style="
            position:absolute;
            right:8px;
            top:50%;
            transform:translateY(-50%);
            color:#666;
            cursor:pointer;
            font-size:16px;
            display:none;
            transition:color 0.2s;
          " onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#666'">×</span>
        `;
        el.appendChild(searchContainer);

        const searchInput = searchContainer.querySelector("#kuai-search");
        const clearBtn = searchContainer.querySelector("#kuai-clear");

        // 快捷键提示
        const shortcutNote = document.createElement("div");
        shortcutNote.textContent = "快捷键：Ctrl + Shift + K";
        shortcutNote.style.cssText = "color:#666;font-size:11px;margin-bottom:10px;text-align:center;";
        el.appendChild(shortcutNote);

        // 节点容器
        const nodesContainer = document.createElement("div");
        nodesContainer.id = "kuai-nodes-container";
        el.appendChild(nodesContainer);

        // 自动发现节点
        const allNodes = discoverNodes();
        let currentFilter = "";

        // 渲染节点列表
        const renderNodes = (filter = "") => {
          nodesContainer.innerHTML = "";
          let hasResults = false;

          Object.entries(allNodes).forEach(([category, items]) => {
            const filteredItems = filter
              ? items.filter(item =>
                item.display.toLowerCase().includes(filter.toLowerCase()) ||
                item.name.toLowerCase().includes(filter.toLowerCase())
              )
              : items;

            if (filteredItems.length === 0) return;
            hasResults = true;

            const categoryDiv = document.createElement("div");
            categoryDiv.style.marginBottom = "8px";

            const title = document.createElement("div");
            title.textContent = `${filter ? '▼' : '▶'} ${category} (${filteredItems.length})`;
            title.style.cssText = `
              color: #4a9eff;
              font-size: 13px;
              font-weight: 600;
              padding: 8px 10px;
              background: linear-gradient(135deg, #2a2a2a 0%, #323232 100%);
              border-radius: 6px;
              cursor: pointer;
              user-select: none;
              transition: all 0.2s;
              box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            `;
            title.addEventListener("mouseenter", () => {
              title.style.background = "linear-gradient(135deg, #323232 0%, #3a3a3a 100%)";
              title.style.transform = "translateX(2px)";
            });
            title.addEventListener("mouseleave", () => {
              title.style.background = "linear-gradient(135deg, #2a2a2a 0%, #323232 100%)";
              title.style.transform = "translateX(0)";
            });

            const container = document.createElement("div");
            container.className = "items-container";
            container.style.cssText = `
              display: ${filter ? 'block' : 'none'};
              margin-top: 6px;
              padding-left: 4px;
            `;

            filteredItems.forEach(({ name, display }) => {
              const btn = document.createElement("div");
              btn.textContent = display;
              btn.style.cssText = `
                background: linear-gradient(135deg, #252525 0%, #2d2d2d 100%);
                border-left: 3px solid #4a9eff;
                padding: 8px 12px;
                margin-bottom: 4px;
                cursor: pointer;
                color: #e0e0e0;
                font-size: 12px;
                border-radius: 4px;
                transition: all 0.2s;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
              `;
              btn.addEventListener("mouseenter", () => {
                btn.style.background = "linear-gradient(135deg, #2d2d2d 0%, #353535 100%)";
                btn.style.transform = "translateX(4px)";
                btn.style.borderLeftColor = "#5ab0ff";
              });
              btn.addEventListener("mouseleave", () => {
                btn.style.background = "linear-gradient(135deg, #252525 0%, #2d2d2d 100%)";
                btn.style.transform = "translateX(0)";
                btn.style.borderLeftColor = "#4a9eff";
              });
              btn.addEventListener("click", () => {
                const node = LiteGraph.createNode(name);
                if (node) {
                  node.pos = [app.canvas.graph_mouse[0], app.canvas.graph_mouse[1]];
                  app.graph.add(node);
                  app.canvas.selectNode(node);
                  app.graph.setDirtyCanvas(true, true);

                  // 视觉反馈
                  btn.style.background = "#4a9eff";
                  setTimeout(() => {
                    btn.style.background = "linear-gradient(135deg, #252525 0%, #2d2d2d 100%)";
                  }, 200);
                }
              });
              container.appendChild(btn);
            });

            title.addEventListener("click", () => {
              if (!filter) {
                // 关闭所有同级
                nodesContainer.querySelectorAll(".items-container").forEach(c => {
                  if (c !== container) {
                    c.style.display = "none";
                    const t = c.previousSibling;
                    // 使用更通用的正则，匹配任何 emoji 开头的分类名
                    const catName = t.textContent.match(/^[▶▼]\s*(.+?)\s*\(/)[1].trim();
                    t.textContent = `▶ ${catName} ${t.textContent.match(/\(\d+\)/)[0]}`;
                  }
                });
                // 切换当前
                const isOpen = container.style.display === "block";
                container.style.display = isOpen ? "none" : "block";
                // 使用更通用的正则，匹配任何 emoji 开头的分类名
                const catName = title.textContent.match(/^[▶▼]\s*(.+?)\s*\(/)[1].trim();
                title.textContent = isOpen
                  ? `▶ ${catName} ${title.textContent.match(/\(\d+\)/)[0]}`
                  : `▼ ${catName} ${title.textContent.match(/\(\d+\)/)[0]}`;
              }
            });

            categoryDiv.append(title, container);
            nodesContainer.appendChild(categoryDiv);
          });

          // 无结果提示
          if (!hasResults) {
            nodesContainer.innerHTML = `
              <div style="
                text-align:center;
                padding:20px;
                color:#666;
                font-size:13px;
              ">
                😕 未找到匹配的节点
              </div>
            `;
          }
        };

        // 初始渲染
        renderNodes();

        // 搜索功能（防抖）
        const handleSearch = debounce((value) => {
          currentFilter = value;
          clearBtn.style.display = value ? "block" : "none";
          renderNodes(value);
        }, 300);

        searchInput.addEventListener("input", (e) => handleSearch(e.target.value));

        clearBtn.addEventListener("click", () => {
          searchInput.value = "";
          clearBtn.style.display = "none";
          renderNodes("");
        });

        // 关闭按钮
        document.getElementById("kuai-close").addEventListener("click", () => {
          const sidebarButton = document.querySelector('[data-id="kuaipower-panel"]');
          if (sidebarButton) {
            sidebarButton.click();
          }
        });
      }
    });

    // 快捷键切换侧边栏 (Ctrl+Shift+K)
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "k") {
        e.preventDefault();
        e.stopPropagation();

        const sidebarButton = document.querySelector('[data-id="kuaipower-panel"]');
        if (sidebarButton) {
          sidebarButton.click();
        }
      }
    });

    console.log("[KuAi_Power] 面板扩展已加载（增强版）");
  }
});
