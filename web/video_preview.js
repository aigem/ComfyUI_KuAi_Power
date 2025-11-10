import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KuAi.VideoPreview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "PreviewVideo") {
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                if (message.video && message.video.length > 0) {
                    const videoUrl = message.video[0];
                    
                    // 创建视频预览
                    if (!this.videoWidget) {
                        this.videoWidget = this.addDOMWidget("video", "preview", document.createElement("div"));
                    }
                    
                    const container = this.videoWidget.element;
                    container.innerHTML = "";
                    container.style.cssText = "width: 100%; min-height: 200px; display: flex; flex-direction: column; gap: 8px;";
                    
                    const video = document.createElement("video");
                    video.src = videoUrl;
                    video.controls = true;
                    video.autoplay = false;
                    video.style.cssText = "width: 100%; max-height: 400px; border-radius: 4px;";
                    
                    const link = document.createElement("a");
                    link.href = videoUrl;
                    link.target = "_blank";
                    link.textContent = "🔗 在新标签页打开";
                    link.style.cssText = "color: #0066cc; text-decoration: none; font-size: 12px;";
                    
                    container.appendChild(video);
                    container.appendChild(link);
                    
                    this.setSize([Math.max(this.size[0], 320), Math.max(this.size[1], 280)]);
                }
            };
        }
    }
});
