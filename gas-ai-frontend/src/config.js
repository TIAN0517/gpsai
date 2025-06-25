// API endpoint 設定，方便前後端分離與日後調整
export const API_URL = process.env.REACT_APP_API_URL || "/ai_ask";
export const HEALTH_URL = process.env.REACT_APP_HEALTH_URL || "/health";
export const QUOTA_URL = process.env.REACT_APP_QUOTA_URL || "/quota";
export const MODULES_URL = process.env.REACT_APP_MODULES_URL || "/modules";
export const NOTICE_URL = process.env.REACT_APP_NOTICE_URL || "/notice";
export const CACHE_STATUS_URL = process.env.REACT_APP_CACHE_STATUS_URL || "/cache/status";
export const CACHE_CLEAR_URL = process.env.REACT_APP_CACHE_CLEAR_URL || "/cache/clear";
export const HISTORY_URL = process.env.REACT_APP_HISTORY_URL || "/history";
export const LOGIN_URL = process.env.REACT_APP_LOGIN_URL || "/login";
export const LOGOUT_URL = process.env.REACT_APP_LOGOUT_URL || "/logout";

// PWA 設定
export const PWA_CONFIG = {
  name: "智慧瓦斯AI管理系統",
  short_name: "智慧瓦斯AI",
  description: "Jy技術團隊 - 專業瓦斯行管理AI助手",
  theme_color: "#2676ff",
  background_color: "#161a2a",
  display: "standalone",
  orientation: "portrait-primary"
};

// 企業品牌設定
export const BRAND_CONFIG = {
  name: "智慧瓦斯AI管理系統",
  developer: "Jy技術團隊",
  primary_color: "#2676ff",
  secondary_color: "#ff9800",
  font_family: "Orbitron, Noto Sans TC, 微軟正黑體"
}; 