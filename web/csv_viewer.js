/**
 * CSV Viewer Extension for ComfyUI
 * 为 CSVViewer 节点提供表格显示功能
 */

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// 注册 CSV 表格显示扩展
app.registerExtension({
    name: "KuAi.CSVViewer",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 只处理 CSVViewer 节点
        if (nodeData.name === "CSVViewer") {
            console.log("[CSVViewer] 注册 CSV 表格显示扩展");

            // 保存原始的 onExecuted 方法
            const onExecuted = nodeType.prototype.onExecuted;

            // 重写 onExecuted 方法以处理表格数据
            nodeType.prototype.onExecuted = function(message) {
                // 调用原始方法
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }

                // 检查是否有 CSV 表格数据
                if (message && message.csv_table && message.csv_table.length > 0) {
                    const tableData = message.csv_table[0];
                    console.log("[CSVViewer] 收到表格数据:", tableData);

                    // 显示表格
                    this.showCSVTable(tableData);
                }
            };

            // 添加显示表格的方法
            nodeType.prototype.showCSVTable = function(tableData) {
                // 移除旧的表格 widget（如果存在）
                if (this.csvTableWidget) {
                    this.removeWidget(this.csvTableWidget);
                }

                // 创建表格 HTML
                const tableHTML = this.createTableHTML(tableData);

                // 创建自定义 widget 来显示表格
                const widget = ComfyWidgets["STRING"](this, "csv_table_display", ["STRING", { multiline: true }], app).widget;
                widget.inputEl.readOnly = true;
                widget.inputEl.style.display = "none"; // 隐藏默认的文本框

                // 创建表格容器
                const tableContainer = document.createElement("div");
                tableContainer.className = "csv-table-container";
                tableContainer.innerHTML = tableHTML;

                // 添加样式
                this.addTableStyles(tableContainer);

                // 将表格容器插入到节点中
                widget.inputEl.parentNode.insertBefore(tableContainer, widget.inputEl);

                // 保存 widget 引用
                this.csvTableWidget = widget;

                // 调整节点大小以适应表格
                this.setSize([Math.max(600, this.size[0]), Math.max(400, this.size[1])]);
            };

            // 创建表格 HTML
            nodeType.prototype.createTableHTML = function(tableData) {
                const { headers, rows, total_rows, file_name } = tableData;

                let html = `
                    <div class="csv-table-header">
                        <strong>文件:</strong> ${file_name}
                        <span class="csv-row-count">(${total_rows} 行)</span>
                    </div>
                    <div class="csv-table-wrapper">
                        <table class="csv-table">
                            <thead>
                                <tr>
                `;

                // 添加表头
                headers.forEach(header => {
                    html += `<th>${this.escapeHTML(header)}</th>`;
                });

                html += `
                                </tr>
                            </thead>
                            <tbody>
                `;

                // 添加数据行
                rows.forEach((row, rowIndex) => {
                    html += `<tr>`;
                    row.forEach(cell => {
                        html += `<td>${this.escapeHTML(cell)}</td>`;
                    });
                    html += `</tr>`;
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;

                return html;
            };

            // HTML 转义函数
            nodeType.prototype.escapeHTML = function(str) {
                if (str === null || str === undefined) return '';
                return String(str)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            };

            // 添加表格样式
            nodeType.prototype.addTableStyles = function(container) {
                // 检查是否已经添加了全局样式
                if (!document.getElementById('csv-viewer-styles')) {
                    const style = document.createElement('style');
                    style.id = 'csv-viewer-styles';
                    style.textContent = `
                        .csv-table-container {
                            margin: 10px;
                            padding: 10px;
                            background: #1e1e1e;
                            border-radius: 5px;
                            max-height: 500px;
                            overflow: auto;
                        }

                        .csv-table-header {
                            margin-bottom: 10px;
                            padding: 5px;
                            background: #2a2a2a;
                            border-radius: 3px;
                            color: #e0e0e0;
                            font-size: 14px;
                        }

                        .csv-row-count {
                            color: #888;
                            font-size: 12px;
                            margin-left: 10px;
                        }

                        .csv-table-wrapper {
                            overflow: auto;
                            max-height: 450px;
                        }

                        .csv-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 12px;
                            background: #252525;
                        }

                        .csv-table th {
                            background: #333;
                            color: #fff;
                            padding: 8px;
                            text-align: left;
                            border: 1px solid #444;
                            position: sticky;
                            top: 0;
                            z-index: 10;
                            font-weight: bold;
                        }

                        .csv-table td {
                            padding: 6px 8px;
                            border: 1px solid #333;
                            color: #ddd;
                        }

                        .csv-table tbody tr:nth-child(even) {
                            background: #2a2a2a;
                        }

                        .csv-table tbody tr:hover {
                            background: #3a3a3a;
                        }

                        /* 滚动条样式 */
                        .csv-table-wrapper::-webkit-scrollbar,
                        .csv-table-container::-webkit-scrollbar {
                            width: 8px;
                            height: 8px;
                        }

                        .csv-table-wrapper::-webkit-scrollbar-track,
                        .csv-table-container::-webkit-scrollbar-track {
                            background: #1e1e1e;
                        }

                        .csv-table-wrapper::-webkit-scrollbar-thumb,
                        .csv-table-container::-webkit-scrollbar-thumb {
                            background: #555;
                            border-radius: 4px;
                        }

                        .csv-table-wrapper::-webkit-scrollbar-thumb:hover,
                        .csv-table-container::-webkit-scrollbar-thumb:hover {
                            background: #666;
                        }
                    `;
                    document.head.appendChild(style);
                }
            };
        }
    }
});

console.log("[CSVViewer] CSV 查看器扩展已加载");
