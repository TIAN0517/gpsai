import React, { useState, useRef, useEffect } from "react";
import { Layout, Typography, Input, Button, Card, List, message, Spin, Space, Tooltip, Badge, Modal, Tabs, Progress, Alert, Drawer, Switch, notification } from "antd";
import { 
  SendOutlined, HistoryOutlined, ReloadOutlined, HeartFilled, 
  SettingOutlined, BellOutlined, DashboardOutlined, UserOutlined,
  CloudOutlined, DatabaseOutlined, ThunderboltOutlined, InfoCircleOutlined
} from "@ant-design/icons";
import axios from "axios";
import dayjs from "dayjs";
import { API_URL, HEALTH_URL, QUOTA_URL, CACHE_STATUS_URL } from "./config";
import "./index.css";

const { Header, Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

type QueryResult = {
  module: string;
  model: string;
  answer: string;
  query: string;
  system_prompt: string;
  time: string;
  cached?: boolean;
  quota_info?: any;
};

type HealthStatus = {
  status: string;
  apis: any;
  ollama: any;
  cache: any;
  quota: any;
  stats: any;
};

type QuotaInfo = {
  quota_ok: boolean;
  current_usage: any;
  limits: any;
  reset_times: any;
};

const LOGO = (
  <span style={{ fontFamily: "Orbitron, Noto Sans TC, 微軟正黑體", fontWeight: 900, fontSize: 28, color: "#1677ff" }}>
    Jy 技術團隊
  </span>
);

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [history, setHistory] = useState<QueryResult[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [quota, setQuota] = useState<QuotaInfo | null>(null);
  const [healthModal, setHealthModal] = useState(false);
  const [settingsDrawer, setSettingsDrawer] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pwaInstallPrompt, setPwaInstallPrompt] = useState<any>(null);
  const inputRef = useRef<any>(null);

  // PWA 安裝提示
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: any) => {
      e.preventDefault();
      setPwaInstallPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  }, []);

  // 網路狀態監控
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Service Worker 註冊
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration);
          
          // 請求推播權限
          if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
              setNotificationPermission(permission === 'granted');
            });
          }
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
    }
  }, []);

  // 載入本機歷史
  useEffect(() => {
    const h = localStorage.getItem("gas_ai_history");
    if (h) setHistory(JSON.parse(h));
  }, []);

  // 儲存本機歷史
  useEffect(() => {
    localStorage.setItem("gas_ai_history", JSON.stringify(history));
  }, [history]);

  // 定期檢查健康狀態
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 每30秒檢查一次
    return () => clearInterval(interval);
  }, []);

  // 查詢 API
  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await axios.post(API_URL, { query });
      const result: QueryResult = {
        ...data,
        time: dayjs().format("YYYY-MM-DD HH:mm:ss"),
      };
      setResults([result, ...results]);
      setHistory([result, ...history].slice(0, 30));
      setQuery("");
      
      // 顯示快取提示
      if (data.cached) {
        message.success("查詢成功！（快取結果）");
      } else {
        message.success("查詢成功！");
      }

      // 推播通知（如果允許）
      if (notificationPermission && data.cached) {
        new Notification('智慧瓦斯AI', {
          body: '查詢完成（快取結果）',
          icon: '/logo192.png'
        });
      }
    } catch (e: any) {
      const errorMsg = e?.response?.data?.error || "查詢失敗";
      message.error(errorMsg);
      
      // 顯示友善的錯誤提示
      if (e?.response?.status === 429) {
        message.warning("配額已達上限，請稍後再試");
      } else if (e?.response?.status === 503) {
        message.warning("AI服務暫時不可用，請檢查網路連線或稍後再試");
      }
    }
    setLoading(false);
    inputRef.current?.focus();
  };

  // 健康檢查
  const checkHealth = async () => {
    try {
      const { data } = await axios.get(HEALTH_URL);
      setHealth(data);
      
      // 檢查配額
      const quotaResponse = await axios.get(QUOTA_URL);
      setQuota(quotaResponse.data);
      
      // 如果系統不健康，顯示警告
      if (data.status === 'unhealthy') {
        message.warning('系統健康狀態異常，部分功能可能受影響');
      }
    } catch (error) {
      console.error('健康檢查失敗:', error);
    }
  };

  // 安裝 PWA
  const installPWA = async () => {
    if (pwaInstallPrompt) {
      pwaInstallPrompt.prompt();
      const { outcome } = await pwaInstallPrompt.userChoice;
      if (outcome === 'accepted') {
        message.success('應用程式已安裝！');
      }
      setPwaInstallPrompt(null);
    }
  };

  // 快捷鍵送出
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") handleAsk();
  };

  // 點擊歷史查詢
  const handleHistoryClick = (item: QueryResult) => {
    setQuery(item.query);
    inputRef.current?.focus();
  };

  // 清空歷史
  const clearHistory = () => {
    setHistory([]);
    message.success('歷史記錄已清空');
  };

  // 健康狀態渲染
  const renderHealthStatus = () => {
    if (!health) return <Spin />;

    return (
      <div>
        <Alert
          message={`系統狀態: ${health.status === 'healthy' ? '健康' : health.status === 'degraded' ? '部分異常' : '異常'}`}
          type={health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'error'}
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Tabs defaultActiveKey="apis">
          <TabPane tab="API狀態" key="apis">
            {Object.entries(health.apis).map(([name, api]: [string, any]) => (
              <Card key={name} size="small" style={{ marginBottom: 8 }}>
                <Space>
                  <Badge status={api.status === 'healthy' ? 'success' : 'error'} />
                  <Text strong>{api.display_name}</Text>
                  <Text type="secondary">({api.type})</Text>
                </Space>
              </Card>
            ))}
          </TabPane>
          
          <TabPane tab="本地Ollama" key="ollama">
            <Card size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <Badge status={health.ollama.available ? 'success' : 'error'} />
                  <Text strong>本地Ollama</Text>
                  <Text>{health.ollama.available ? '可用' : '不可用'}</Text>
                </Space>
                {health.ollama.available && (
                  <div>
                    <Text strong>可用模型:</Text>
                    <div style={{ marginTop: 8 }}>
                      {health.ollama.models.map((model: string) => (
                        <Tag key={model} color="blue">{model}</Tag>
                      ))}
                    </div>
                  </div>
                )}
              </Space>
            </Card>
          </TabPane>
          
          <TabPane tab="快取狀態" key="cache">
            <Card size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <Switch checked={health.cache.enabled} disabled />
                  <Text>快取功能</Text>
                </Space>
                <Progress 
                  percent={Math.round(health.cache.size / health.cache.max_size * 100)} 
                  format={percent => `${health.cache.size}/${health.cache.max_size}`}
                />
                <Text type="secondary">TTL: {health.cache.ttl}秒</Text>
              </Space>
            </Card>
          </TabPane>
          
          <TabPane tab="配額使用" key="quota">
            <Card size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <Switch checked={health.quota.enabled} disabled />
                  <Text>配額管理</Text>
                </Space>
                <Progress 
                  percent={Math.round(health.quota.current.hourly / health.quota.limits.hourly * 100)} 
                  format={percent => `每小時: ${health.quota.current.hourly}/${health.quota.limits.hourly}`}
                />
                <Progress 
                  percent={Math.round(health.quota.current.daily / health.quota.limits.daily * 100)} 
                  format={percent => `每日: ${health.quota.current.daily}/${health.quota.limits.daily}`}
                />
                <Progress 
                  percent={Math.round(health.quota.current.monthly / health.quota.limits.monthly * 100)} 
                  format={percent => `每月: ${health.quota.current.monthly}/${health.quota.limits.monthly}`}
                />
              </Space>
            </Card>
          </TabPane>
        </Tabs>
      </div>
    );
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={260} className="sider" breakpoint="lg" collapsedWidth="0">
        <div className="logo">{LOGO}</div>
        
        {/* 網路狀態指示器 */}
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <Badge 
            status={isOnline ? 'success' : 'error'} 
            text={isOnline ? '線上' : '離線'}
          />
        </div>
        
        <Title level={4} style={{ color: "#fff", margin: "24px 0 8px" }}>查詢歷史</Title>
        <List
          dataSource={history}
          renderItem={item => (
            <List.Item className="history-item" onClick={() => handleHistoryClick(item)}>
              <HistoryOutlined style={{ color: "#ff9800", marginRight: 8 }} />
              <span className="history-query">{item.query.slice(0, 18)}{item.query.length > 18 ? "..." : ""}</span>
              <span className="history-time">{item.time.slice(5, 16)}</span>
            </List.Item>
          )}
        />
        <div style={{ margin: "24px 0", textAlign: "center" }}>
          <Button
            icon={<ReloadOutlined />}
            onClick={clearHistory}
            size="small"
            danger
            style={{ borderRadius: 20 }}
          >
            清空歷史
          </Button>
        </div>
      </Sider>
      
      <Layout>
        <Header className="header">
          <Title level={2} className="main-title">智慧瓦斯 AI 管理系統</Title>
          <Space>
            {/* PWA 安裝按鈕 */}
            {pwaInstallPrompt && (
              <Button
                icon={<ThunderboltOutlined />}
                type="primary"
                onClick={installPWA}
                style={{ background: "#52c41a", border: "none", borderRadius: 20 }}
              >
                安裝App
              </Button>
            )}
            
            {/* 推播通知按鈕 */}
            <Button
              icon={<BellOutlined />}
              type={notificationPermission ? "primary" : "default"}
              onClick={() => {
                if ('Notification' in window) {
                  Notification.requestPermission().then(permission => {
                    setNotificationPermission(permission === 'granted');
                    if (permission === 'granted') {
                      message.success('推播通知已啟用');
                    }
                  });
                }
              }}
              style={{ borderRadius: 20 }}
            >
              通知
            </Button>
            
            {/* 設定按鈕 */}
            <Button
              icon={<SettingOutlined />}
              onClick={() => setSettingsDrawer(true)}
              style={{ borderRadius: 20 }}
            >
              設定
            </Button>
            
            {/* 健康檢查按鈕 */}
            <Button
              icon={<HeartFilled />}
              type="primary"
              style={{ background: "#ff9800", border: "none", borderRadius: 20 }}
              onClick={() => setHealthModal(true)}
            >
              健康檢查
            </Button>
          </Space>
        </Header>
        
        <Content className="content">
          <Card className="query-card">
            <Input.TextArea
              ref={inputRef}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="請輸入查詢內容（Ctrl+Enter 送出）"
              autoSize={{ minRows: 3, maxRows: 6 }}
              style={{ borderRadius: 12, fontSize: 18, fontFamily: "Noto Sans TC, 微軟正黑體" }}
              disabled={loading}
            />
            <div style={{ textAlign: "right", marginTop: 12 }}>
              <Button
                type="primary"
                icon={<SendOutlined />}
                loading={loading}
                style={{ borderRadius: 20, background: "#1677ff", border: "none", fontWeight: 700 }}
                onClick={handleAsk}
                disabled={!query.trim() || loading}
              >
                送出查詢
              </Button>
            </div>
          </Card>
          
          <div style={{ marginTop: 32 }}>
            <List
              dataSource={results}
              renderItem={item => (
                <Card className="result-card" key={item.time} bordered={false}>
                  <Space direction="vertical" size={4} style={{ width: "100%" }}>
                    <div>
                      <Text strong style={{ color: "#1677ff" }}>分流模組：</Text>
                      <Text>{item.module}</Text>
                      <Text strong style={{ color: "#ff9800", marginLeft: 16 }}>AI模型：</Text>
                      <Text>{item.model}</Text>
                      {item.cached && (
                        <Badge 
                          count="快取" 
                          style={{ backgroundColor: '#52c41a', marginLeft: 8 }} 
                        />
                      )}
                      <Text type="secondary" style={{ float: "right" }}>{item.time}</Text>
                    </div>
                    <div>
                      <Text strong style={{ color: "#1677ff" }}>查詢內容：</Text>
                      <Text>{item.query}</Text>
                    </div>
                    <div>
                      <Text strong style={{ color: "#ff9800" }}>AI回應：</Text>
                      <div className="ai-answer">{item.answer}</div>
                    </div>
                  </Space>
                </Card>
              )}
            />
          </div>
        </Content>
      </Layout>
      
      {/* 健康檢查模態框 */}
      <Modal
        open={healthModal}
        onCancel={() => setHealthModal(false)}
        footer={null}
        title="系統健康檢查"
        width={800}
        centered
      >
        {renderHealthStatus()}
      </Modal>
      
      {/* 設定抽屜 */}
      <Drawer
        title="系統設定"
        placement="right"
        onClose={() => setSettingsDrawer(false)}
        open={settingsDrawer}
        width={400}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Card title="推播通知" size="small">
            <Space>
              <Switch 
                checked={notificationPermission} 
                onChange={(checked) => {
                  if (checked && 'Notification' in window) {
                    Notification.requestPermission().then(permission => {
                      setNotificationPermission(permission === 'granted');
                    });
                  }
                }}
              />
              <Text>啟用推播通知</Text>
            </Space>
          </Card>
          
          <Card title="離線功能" size="small">
            <Space>
              <Badge status={isOnline ? 'success' : 'error'} />
              <Text>網路狀態: {isOnline ? '線上' : '離線'}</Text>
            </Space>
          </Card>
          
          <Card title="PWA 功能" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Badge status={pwaInstallPrompt ? 'processing' : 'default'} />
                <Text>可安裝: {pwaInstallPrompt ? '是' : '否'}</Text>
              </Space>
              {pwaInstallPrompt && (
                <Button 
                  type="primary" 
                  onClick={installPWA}
                  icon={<ThunderboltOutlined />}
                >
                  安裝為App
                </Button>
              )}
            </Space>
          </Card>
        </Space>
      </Drawer>
    </Layout>
  );
}

export default App;
