# VPS Node Manager

安全读取 VPS 现有代理配置，识别五个既有节点并生成客户端导出文件。v0.1 默认不修改服务端配置、不重启服务、不生成或轮换密钥。

## 安装

```bash
sudo bash install.sh
sudo vps-node-manager audit
sudo vps-node-manager update --dry-run
sudo vps-node-manager update
```

默认安装到 /opt/vps-node-manager。首次运行复制 config/settings.example.json 为本机 config/settings.json；请检查路径后再审计。

## 管理的节点

- Hysteria2 UDP 52851
- VLESS Reality TCP 32490
- VLESS Argo WS 443（保留域名）
- VMess TLS WS TCP 321（替换连接 IP，保留 TLS SNI）
- VMess WS TCP 80

VMess 两个入站均由 x-ui 管理。无法完整识别五类节点时拒绝覆盖正式输出。

## 安全边界

- update 只更新本项目 output，不修改服务端配置。
- 输出目录 0700、文件 0600；原子写入并备份旧输出。
- 公网 IPv4 获取失败、节点数量不符或解析错误时中止。
- 不记录 UUID、密码、私钥；Reality 公钥从现有私钥派生。
- Hysteria2 客户端 SNI/insecure 偏好单独保存在本机 settings.json。
- 不要提交真实配置、数据库、节点链接或 settings.json。

## 当前限制

v0.1 是保守的只读解析/导出基线。不同 v2ray-agent、sing-box、x-ui 版本的 JSON/YAML 结构可能不同；首次使用必须先执行 audit，若有字段不匹配应按 VPS 实际配置完善适配器。服务端自动修改功能未启用。
