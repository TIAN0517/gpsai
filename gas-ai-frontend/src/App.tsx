import React, { useState, useRef, useEffect } from "react";
import { Layout, Typography, Input, Button, Card, List, message, Spin, Space, Tooltip, Badge, Modal, Tabs, Progress, Alert, Drawer, Switch, Tag } from "antd";
import { 
  SendOutlined, HistoryOutlined, ReloadOutlined, HeartFilled, 
  SettingOutlined, BellOutlined, ThunderboltOutlined, GiftOutlined, SmileOutlined
} from "@ant-design/icons";
import axios from "axios";
import dayjs from "dayjs";
import { API_URL, HEALTH_URL, QUOTA_URL, LOTTERY_URL } from "./config";
import "./index.css";

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;
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
  const [healthModal, setHealthModal] = useState(false);
  const [settingsDrawer, setSettingsDrawer] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pwaInstallPrompt, setPwaInstallPrompt] = useState<any>(null);
  const [lotteryResult, setLotteryResult] = useState<string | null>(null);
  const [lotterySpinning, setLotterySpinning] = useState(false);
  const [selectedGrid, setSelectedGrid] = useState<number | null>(null);
  const [hasDrawn, setHasDrawn] = useState(false);
  const [running, setRunning] = useState(false);
  const [prizeAmount, setPrizeAmount] = useState<number | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [prizeModal, setPrizeModal] = useState(false);
  const [analysisModal, setAnalysisModal] = useState(false);
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

  // 顏色與金額對應
  const gridColors = [
    '#00eaff', // 藍
    '#1677ff', // 深藍
    '#ff9800', // 橘
    '#00ffb0'  // 青
  ];
  // 調整金額機率分布，100元極難中
  const prizeOptions = [
    { amount: 20, color: '#00eaff' },
    { amount: 20, color: '#00eaff' },
    { amount: 20, color: '#00eaff' },
    { amount: 20, color: '#00eaff' },
    { amount: 20, color: '#00eaff' },
    { amount: 20, color: '#00eaff' },
    { amount: 30, color: '#1677ff' },
    { amount: 30, color: '#1677ff' },
    { amount: 30, color: '#1677ff' },
    { amount: 50, color: '#ff9800' },
    { amount: 50, color: '#ff9800' },
    { amount: 100, color: '#00ffb0' }, // 100元僅1格，極難中
  ];
  // 每日自動重置
  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    const lastDraw = localStorage.getItem('lottery_last_draw');
    if (lastDraw !== today) {
      setHasDrawn(false);
      setPrizeAmount(null);
      setSelectedGrid(null);
      setRunning(false);
      localStorage.setItem('lottery_last_draw', today);
    }
  }, []);
  // 外圈16格圓點
  const dotCount = 16;
  // 跑馬燈動畫與抽獎邏輯
  const startLottery = async () => {
    if (hasDrawn || running) return;
    setRunning(true);
    setPrizeAmount(null);
    setShowConfetti(false);
    // 隨機決定中獎金額與顏色
    const prize = prizeOptions[Math.floor(Math.random() * prizeOptions.length)];
    setPrizeAmount(prize.amount);
    // 決定停在哪一格
    const targetIdx = Math.floor(Math.random() * dotCount);
    let steps = 32 + targetIdx;
    for (let i = 0; i <= steps; i++) {
      setSelectedGrid(i % dotCount);
      await new Promise(res => setTimeout(res, 80 + Math.min(i*6, 180)));
    }
    setHasDrawn(true);
    setRunning(false);
    setShowConfetti(true);
    setPrizeModal(true);
    setTimeout(() => setShowConfetti(false), 1800);
    localStorage.setItem('lottery_last_draw', new Date().toISOString().slice(0, 10));
  };

  // 抽獎獎項
  const lotteryPrizes = [
    "100元折價券",
    "免費瓦斯安檢一次",
    "會員積分加倍",
    "瓦斯器具9折券",
    "恭喜中獎！下次再接再厲",
    "50元折價券",
    "專屬客服諮詢券"
  ];

  // 抽獎邏輯
  const handleLottery = async () => {
    setLotterySpinning(true);
    setLotteryResult(null);
    try {
      const { data } = await axios.post(LOTTERY_URL);
      setTimeout(() => {
        if (data.success) {
          setLotteryResult(data.prize);
          message.success(data.msg || "抽獎成功！");
        } else {
          setLotteryResult(null);
          message.info(data.msg || "今日已抽過，請明天再來！");
        }
        setLotterySpinning(false);
      }, 1200); // 動畫延遲
    } catch (e: any) {
      setTimeout(() => {
        setLotteryResult(null);
        message.error(e?.response?.data?.msg || "抽獎失敗，請稍後再試");
        setLotterySpinning(false);
      }, 1200);
    }
  };

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
      // const quotaResponse = await axios.get(QUOTA_URL);
      // setQuota(quotaResponse.data);
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

  // 假資料（LPG企業級全成本結構）
  const stationData = [
    {
      name: '吉安站',
      buyTon: 10,
      buyKg: 10000,
      rawCost: 120000,
      labor: 32000,
      daily: 8000,
      insurance: 6000,
      carInsurance: 4000,
      depreciation: 7000,
      other: 3000,
      sale: 180000,
    },
    {
      name: '美崙站',
      buyTon: 7,
      buyKg: 7000,
      rawCost: 84000,
      labor: 22000,
      daily: 6000,
      insurance: 4200,
      carInsurance: 3000,
      depreciation: 5000,
      other: 2000,
      sale: 126000,
    },
    {
      name: '市區站',
      buyTon: 15,
      buyKg: 15000,
      rawCost: 180000,
      labor: 48000,
      daily: 12000,
      insurance: 9000,
      carInsurance: 7000,
      depreciation: 11000,
      other: 5000,
      sale: 270000,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh", background: "none" }}>
      <Layout>
        <Header className="header">
          <Title level={2} className="main-title">智慧瓦斯 AI 管理系統</Title>
          <Space>
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
            <Button
              icon={<SettingOutlined />}
              onClick={() => setSettingsDrawer(true)}
              style={{ borderRadius: 20 }}
            >
              設定
            </Button>
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
        <Content className="content dashboard-bg" style={{ minHeight: 'calc(100vh - 64px)', position: 'relative', overflow: 'hidden', padding: 0 }}>
          {/* 動態背景粒子/光暈/線條可後續加上 */}
          <div className="dashboard-main-layout">
            {/* 左側六邊形卡片區 */}
            <div className="dashboard-side dashboard-side-left">
              <div className="hex-card-svg"><svg viewBox="0 0 100 86" width="100" height="86"><polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/><text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">瓦斯器具</text></svg></div>
              <div className="hex-card-svg"><svg viewBox="0 0 100 86" width="100" height="86"><polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/><text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">優惠券</text></svg></div>
              <div className="hex-card-svg"><svg viewBox="0 0 100 86" width="100" height="86"><polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/><text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">FAQ</text></svg></div>
            </div>
            {/* 中央圓環主題區 */}
            <div className="dashboard-center">
              <div className="dashboard-center-circle dashboard-center-circle-large">
                {/* 多層SVG發光圓環與粒子動畫＋16格圓點跑馬燈 */}
                <svg width="520" height="520" className="dashboard-rings" style={{ position: 'absolute', left: 0, top: 0 }}>
                  <circle cx="260" cy="260" r="240" fill="none" stroke="#1677ff88" strokeWidth="8" />
                  <circle cx="260" cy="260" r="180" fill="none" stroke="#00eaff66" strokeWidth="4" />
                  <circle cx="260" cy="260" r="120" fill="none" stroke="#ff980055" strokeWidth="2.5" />
                  {/* 外圈16格圓點 */}
                  {Array.from({length: dotCount}).map((_, idx) => {
                    const angle = (idx / dotCount) * 2 * Math.PI;
                    const radius = 200;
                    const center = 260;
                    const x = center + radius * Math.cos(angle);
                    const y = center + radius * Math.sin(angle);
                    const isSelected = selectedGrid === idx;
                    return (
                      <circle
                        key={idx}
                        cx={x}
                        cy={y}
                        r={isSelected ? 18 : 12}
                        fill={isSelected ? '#ff9800' : '#00eaff'}
                        stroke={isSelected ? '#fff' : '#1677ff'}
                        strokeWidth={isSelected ? 5 : 2}
                        style={{ filter: isSelected ? 'drop-shadow(0 0 16px #ff9800)' : 'drop-shadow(0 0 8px #00eaff)' }}
                      />
                    );
                  })}
                </svg>
                {/* 中央閃電LOGO（可點擊） */}
                <div
                  className="lottery-logo-glow"
                  style={{ position: 'absolute', left: 130, top: 130, width: 260, height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: hasDrawn || running ? 'not-allowed' : 'pointer', zIndex: 2 }}
                  onClick={startLottery}
                >
                  <ThunderboltOutlined style={{ fontSize: 180, color: hasDrawn ? '#888' : '#00eaff', filter: 'drop-shadow(0 0 32px #00eaff) drop-shadow(0 0 64px #ff9800)' }} />
                  {showConfetti && (
                    <svg className="lottery-confetti" width="260" height="260" style={{ position: 'absolute', left: 0, top: 0, pointerEvents: 'none' }}>
                      {Array.from({length: 24}).map((_, i) => (
                        <circle key={i} cx={130} cy={130} r={8+Math.random()*8} fill="#ff9800" opacity={0.7}
                          style={{
                            transform: `rotate(${i*15}deg) translate(0,-110px)`,
                            transformOrigin: '130px 130px',
                            animation: `confetti-burst 1.2s cubic-bezier(.7,1.8,.2,.8) forwards`,
                            animationDelay: `${i*0.02}s`
                          }}
                        />
                      ))}
                    </svg>
                  )}
                </div>
                {/* 品牌名與副標題 */}
                <div className="dashboard-center-title" style={{ fontSize: '2.8rem', marginTop: 320, color: '#00eaff', fontWeight: 900, letterSpacing: 2, textShadow: '0 0 24px #1677ff, 0 0 48px #00eaff88, 0 0 8px #fff' }}>九九瓦斯行</div>
                <div className="dashboard-center-sub" style={{ fontSize: '1.5rem', color: '#00eaff', fontWeight: 700, letterSpacing: 1, textShadow: '0 0 16px #00eaff88' }}>AI管理系統</div>
                {/* 抽獎說明、祝福語、結果顯示區 */}
                <div style={{ marginTop: 24, textAlign: 'center' }}>
                  {/* 不顯示任何說明文字與中獎字體 */}
                </div>
              </div>
            </div>
            {/* 右側六邊形卡片區 */}
            <div className="dashboard-side dashboard-side-right">
              <div className="hex-card-svg" onClick={() => setAnalysisModal(true)} style={{ cursor: 'pointer', filter: 'drop-shadow(0 0 24px #00eaff)' }}>
                <svg viewBox="0 0 100 86" width="100" height="86">
                  <polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/>
                  <text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">數據大屏</text>
                </svg>
              </div>
              <div className="hex-card-svg"><svg viewBox="0 0 100 86" width="100" height="86"><polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/><text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">GIS地圖</text></svg></div>
              <div className="hex-card-svg"><svg viewBox="0 0 100 86" width="100" height="86"><polygon points="50,3 97,25 97,61 50,83 3,61 3,25" fill="#1a2a4f" stroke="#00eaff" strokeWidth="3"/><text x="50%" y="54%" textAnchor="middle" fill="#00eaff" fontSize="16" fontWeight="bold" dy=".3em">歷史查詢</text></svg></div>
            </div>
          </div>
          {/* 底部六邊形導航條 */}
          <div className="dashboard-bottom-nav">
            <div className="hex-nav">系統管理</div>
            <div className="hex-nav">派工管理</div>
            <div className="hex-nav">設備管理</div>
            <div className="hex-nav">維修管理</div>
            <div className="hex-nav">促案管理</div>
          </div>
        </Content>
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
        {/* 中獎彈窗Modal */}
        <Modal
          open={prizeModal}
          onCancel={() => setPrizeModal(false)}
          footer={null}
          centered
          closable={true}
          bodyStyle={{ borderRadius: 32, background: 'linear-gradient(135deg, #fffbe6 0%, #ffe0b2 100%)', boxShadow: '0 8px 32px #ff980088', padding: 0 }}
          style={{ borderRadius: 32, overflow: 'hidden' }}
        >
          <div style={{ textAlign: 'center', padding: 32, minHeight: 320 }}>
            {/* 鞭炮/粒子動畫 */}
            <svg width="120" height="120" style={{ margin: '0 auto 16px auto', display: 'block' }}>
              {Array.from({length: 18}).map((_, i) => (
                <circle key={i} cx={60} cy={60} r={8+Math.random()*8} fill="#ff9800" opacity={0.7}
                  style={{
                    transform: `rotate(${i*20}deg) translate(0,-48px)`,
                    transformOrigin: '60px 60px',
                    animation: `confetti-burst 1.2s cubic-bezier(.7,1.8,.2,.8) forwards`,
                    animationDelay: `${i*0.03}s`
                  }}
                />
              ))}
            </svg>
            <div style={{ fontWeight: 900, fontSize: 32, color: '#ff9800', margin: '16px 0 8px 0', letterSpacing: 2 }}>
              恭喜獲得 {prizeAmount} 元折價券！
            </div>
            <div style={{ fontSize: 20, color: '#1677ff', fontWeight: 700, marginTop: 12 }}>感謝您支持九九瓦斯行</div>
            <div style={{ color: '#888', marginTop: 8, fontSize: 15 }}>祝您用氣平安順心！</div>
          </div>
        </Modal>
        {/* 企業成本分析大屏Modal */}
        <Modal
          open={analysisModal}
          onCancel={() => setAnalysisModal(false)}
          footer={null}
          centered
          width={1100}
          bodyStyle={{ borderRadius: 32, background: 'linear-gradient(135deg, #0a1833 0%, #1677ff 100%)', boxShadow: '0 8px 32px #00eaff88', padding: 0 }}
          style={{ borderRadius: 32, overflow: 'hidden' }}
        >
          <div style={{ padding: 32, color: '#fff' }}>
            <div style={{ fontSize: 28, fontWeight: 900, color: '#00eaff', marginBottom: 18, letterSpacing: 2, textAlign: 'center', textShadow: '0 0 24px #1677ff' }}>LPG企業級全成本大分析</div>
            {/* 查詢條件下拉選單（預留） */}
            <div style={{ textAlign: 'right', marginBottom: 16 }}>
              <select style={{ fontSize: 16, borderRadius: 8, padding: '4px 12px', background: '#1a2a4f', color: '#00eaff', border: '1px solid #00eaff' }} disabled>
                <option>2024年6月</option>
              </select>
              <select style={{ fontSize: 16, borderRadius: 8, padding: '4px 12px', background: '#1a2a4f', color: '#00eaff', border: '1px solid #00eaff', marginLeft: 8 }} disabled>
                <option>全部分裝場</option>
              </select>
            </div>
            {/* 全公司總覽卡片 */}
            {(() => {
              const total = stationData.reduce((acc, st) => ({
                buyTon: acc.buyTon + st.buyTon,
                buyKg: acc.buyKg + st.buyKg,
                rawCost: acc.rawCost + st.rawCost,
                labor: acc.labor + st.labor,
                daily: acc.daily + st.daily,
                insurance: acc.insurance + st.insurance,
                carInsurance: acc.carInsurance + st.carInsurance,
                depreciation: acc.depreciation + st.depreciation,
                other: acc.other + st.other,
                sale: acc.sale + st.sale,
              }), { buyTon: 0, buyKg: 0, rawCost: 0, labor: 0, daily: 0, insurance: 0, carInsurance: 0, depreciation: 0, other: 0, sale: 0 });
              const totalCost = total.rawCost + total.labor + total.daily + total.insurance + total.carInsurance + total.depreciation + total.other;
              const grossProfit = total.sale - total.rawCost;
              const netProfit = total.sale - totalCost;
              const netRate = total.sale ? Math.round((netProfit / total.sale) * 100) : 0;
              return (
                <div style={{ background: 'rgba(10,24,51,0.95)', borderRadius: 18, boxShadow: '0 4px 32px #00eaff88', padding: 24, marginBottom: 32, textAlign: 'center', border: '2px solid #00eaffcc', maxWidth: 1000, margin: '0 auto 32px auto' }}>
                  <div style={{ fontSize: 22, fontWeight: 900, color: '#00eaff', marginBottom: 8, letterSpacing: 1 }}>全公司總覽</div>
                  <div style={{ fontSize: 15, color: '#ff9800', marginBottom: 4 }}>進貨（上游叫瓦斯）</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>噸數 <b>{total.buyTon}</b> 噸 / <b>{total.buyKg}</b> 公斤</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>原料成本 <b style={{ color: '#ff9800' }}>{total.rawCost}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>人工成本</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>薪資、加班、獎金 <b>{total.labor}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>日常開銷</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>水電、辦公、雜支 <b>{total.daily}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>勞健保</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>勞保、健保、退休金 <b>{total.insurance}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>車體保險</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>車輛保險、強制險 <b>{total.carInsurance}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>設備磨耗</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>折舊、維修 <b>{total.depreciation}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>其他費用</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>行銷、稅金、雜項 <b>{total.other}</b></div>
                  <div style={{ fontSize: 16, margin: '8px 0', color: '#ff9800' }}>總成本 <b>{totalCost}</b></div>
                  <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>銷售收入</div>
                  <div style={{ fontSize: 16, marginBottom: 2 }}>總銷售 <b style={{ color: '#00eaff' }}>{total.sale}</b></div>
                  <div style={{ fontSize: 15, color: '#00ffb0', marginBottom: 4 }}>毛利</div>
                  <div style={{ fontSize: 16, color: '#00ffb0', marginBottom: 2 }}>毛利 <b>{grossProfit}</b></div>
                  <div style={{ fontSize: 15, color: '#00ffb0', marginBottom: 4 }}>營業淨利</div>
                  <div style={{ fontSize: 20, fontWeight: 900, color: '#00ffb0', marginBottom: 4 }}>{netProfit}</div>
                  <Progress percent={netRate} showInfo={false} strokeColor="#00ffb0" trailColor="#222" style={{ marginBottom: 4 }} />
                  <div style={{ fontSize: 13, color: '#00ffb0' }}>淨利率 {netRate}%</div>
                </div>
              );
            })()}
            {/* 各分裝場卡片 */}
            <div style={{ display: 'flex', gap: 24, justifyContent: 'center' }}>
              {stationData.map(st => {
                const totalCost = st.rawCost + st.labor + st.daily + st.insurance + st.carInsurance + st.depreciation + st.other;
                const grossProfit = st.sale - st.rawCost;
                const netProfit = st.sale - totalCost;
                const netRate = st.sale ? Math.round((netProfit / st.sale) * 100) : 0;
                return (
                  <div key={st.name} style={{ background: 'rgba(10,24,51,0.85)', borderRadius: 18, boxShadow: '0 4px 24px #00eaff44', padding: 18, minWidth: 260, textAlign: 'center', border: '2px solid #00eaff55' }}>
                    <div style={{ fontSize: 20, fontWeight: 700, color: '#00eaff', marginBottom: 8 }}>{st.name}</div>
                    <div style={{ fontSize: 15, color: '#ff9800', marginBottom: 4 }}>進貨（上游叫瓦斯）</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>噸數 <b>{st.buyTon}</b> 噸 / <b>{st.buyKg}</b> 公斤</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>原料成本 <b style={{ color: '#ff9800' }}>{st.rawCost}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>人工成本</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>薪資、加班、獎金 <b>{st.labor}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>日常開銷</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>水電、辦公、雜支 <b>{st.daily}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>勞健保</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>勞保、健保、退休金 <b>{st.insurance}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>車體保險</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>車輛保險、強制險 <b>{st.carInsurance}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>設備磨耗</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>折舊、維修 <b>{st.depreciation}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>其他費用</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>行銷、稅金、雜項 <b>{st.other}</b></div>
                    <div style={{ fontSize: 16, margin: '8px 0', color: '#ff9800' }}>總成本 <b>{totalCost}</b></div>
                    <div style={{ fontSize: 15, color: '#00eaff', marginBottom: 4 }}>銷售收入</div>
                    <div style={{ fontSize: 16, marginBottom: 2 }}>總銷售 <b style={{ color: '#00eaff' }}>{st.sale}</b></div>
                    <div style={{ fontSize: 15, color: '#00ffb0', marginBottom: 4 }}>毛利</div>
                    <div style={{ fontSize: 16, color: '#00ffb0', marginBottom: 2 }}>毛利 <b>{grossProfit}</b></div>
                    <div style={{ fontSize: 15, color: '#00ffb0', marginBottom: 4 }}>營業淨利</div>
                    <div style={{ fontSize: 20, fontWeight: 900, color: '#00ffb0', marginBottom: 4 }}>{netProfit}</div>
                    <Progress percent={netRate} showInfo={false} strokeColor="#00ffb0" trailColor="#222" style={{ marginBottom: 4 }} />
                    <div style={{ fontSize: 13, color: '#00ffb0' }}>淨利率 {netRate}%</div>
                  </div>
                );
              })}
            </div>
            <div style={{ color: '#888', fontSize: 15, marginTop: 24, textAlign: 'center' }}>（本頁為靜態模擬，未來可串接AI查詢自動分析）</div>
          </div>
        </Modal>
      </Layout>
    </Layout>
  );
}

export default App;
