export const translations = {
  en: {
    // Sidebar
    'nav.home': 'Home',
    'nav.technical': 'Technical Selection',
    'nav.alpha': 'Alpha Selection',
    'nav.ai': 'AI Selection',
    'nav.settings': 'Settings',
    'user.role': 'Admin',
    'user.name': 'User',

    // Header
    'header.search': 'Search strategies, stocks...',

    // Settings - Headers
    'settings.title': 'Settings',
    'settings.subtitle': 'Manage your application configuration and preferences.',
    'settings.reset': 'Reset Defaults',
    'settings.save': 'Save Changes',
    'settings.saving': 'Saving...',
    'settings.reset.confirm': 'Are you sure you want to reset all settings to defaults?',
    'settings.save.success': 'Settings saved successfully.',
    'settings.save.error': 'Failed to save settings.',

    // Settings - Trading
    'settings.trading.title': 'Trading Configuration',
    'settings.trading.capital': 'Initial Capital',
    'settings.trading.commission': 'Commission Rate',
    'settings.trading.tax': 'Tax Rate',
    'settings.trading.risk_free': 'Risk Free Rate',

    // Settings - AI
    'settings.ai.title': 'AI & LLM',
    'settings.ai.provider': 'Provider',
    'settings.ai.model': 'Model Name',
    'settings.ai.key': 'API Key',
    'settings.ai.base_url': 'Base URL (Optional)',
    'settings.ai.temp': 'Temperature',
    'settings.ai.permission': 'Permission Level',
    'settings.ai.permission.consultant': 'Consultant (Q&A Only)',
    'settings.ai.permission.coding': 'Coding Assistant (Generate Code)',
    'settings.ai.permission.copilot': 'Co-pilot (Full Control)',

    // Settings - System
    'settings.system.title': 'System',
    'settings.system.theme': 'Theme',
    'settings.system.log_level': 'Log Level',
    'settings.system.auto_update': 'Auto-update Market Data on Startup',
    'settings.system.theme.light': 'Light',
    'settings.system.theme.dark': 'Dark',
    'settings.system.theme.system': 'System Default',

    // Common
    'loading': 'Loading...',
    'error': 'Error',
  },
  zh: {
    // Sidebar
    'nav.home': '首页 (Home)',
    'nav.technical': '技术选股 (Technical)',
    'nav.alpha': 'Alpha 选股',
    'nav.ai': 'AI 选股',
    'nav.settings': '设置 (Settings)',
    'user.role': '管理员',
    'user.name': '用户',

    // Header
    'header.search': '搜索策略、股票...',

    // Settings - Headers
    'settings.title': '设置',
    'settings.subtitle': '管理您的应用配置和偏好。',
    'settings.reset': '重置默认',
    'settings.save': '保存更改',
    'settings.saving': '保存中...',
    'settings.reset.confirm': '您确定要将所有设置重置为默认值吗？',
    'settings.save.success': '设置保存成功。',
    'settings.save.error': '保存设置失败。',

    // Settings - Trading
    'settings.trading.title': '交易配置 (Trading)',
    'settings.trading.capital': '初始资金',
    'settings.trading.commission': '佣金率',
    'settings.trading.tax': '印花税率',
    'settings.trading.risk_free': '无风险利率',

    // Settings - AI
    'settings.ai.title': 'AI & LLM',
    'settings.ai.provider': '提供商',
    'settings.ai.model': '模型名称',
    'settings.ai.key': 'API Key',
    'settings.ai.base_url': 'Base URL (可选)',
    'settings.ai.temp': '温度 (Temperature)',
    'settings.ai.permission': '权限等级',
    'settings.ai.permission.consultant': '咨询顾问 (仅问答)',
    'settings.ai.permission.coding': '代码助理 (生成代码)',
    'settings.ai.permission.copilot': '全自动副驾驶 (全权控制)',

    // Settings - System
    'settings.system.title': '系统 (System)',
    'settings.system.theme': '主题',
    'settings.system.log_level': '日志级别',
    'settings.system.auto_update': '启动时自动更新行情',
    'settings.system.theme.light': '浅色',
    'settings.system.theme.dark': '深色',
    'settings.system.theme.system': '系统默认',

    // Common
    'loading': '加载中...',
    'error': '错误',
  }
};

export type Language = 'en' | 'zh';
export type TranslationKey = keyof typeof translations.en;
