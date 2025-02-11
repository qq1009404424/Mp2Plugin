
import threading
from typing import Any, List, Dict, Tuple, Optional

from app.core.module import ModuleManager
from app.helper.module import ModuleHelper

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase

lock = threading.Lock()


class CustomModule(_PluginBase):
    # 插件名称
    plugin_name = "自定义模块"
    # 插件描述
    plugin_desc = "加载自定义模块。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/InfinityPacer/MoviePilot-Plugins/main/icons/customplugin.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "xly1009"
    # 作者主页
    author_url = "https://github.com/InfinityPacer"
    # 插件配置项ID前缀
    plugin_config_prefix = "custommodule_"
    # 加载顺序
    plugin_order = 81
    # 可使用的用户级别
    auth_level = 1

    _onlyonce = False
    _enabled = True

    def init_plugin(self, config: dict = None):
        if not config:
            return
        self._onlyonce=config.get("onlyonce")
        logger.info(f"CustomModule OnlyOnce:{self._onlyonce}")
        if self._onlyonce:
            self.execute()

    def get_state(self):
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """

        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                            'hint': '开启后插件将处于激活状态',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即运行一次',
                                            'hint': '插件将立即运行一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '修改筛选器：FIFTY 50% DOUBLE 2x FREE 免费 '
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '只搜索免费 2x免费  FREE & DOUBLE > FREE > FIFTY'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '只搜索免费 2x免费 50%的种子 FREE & DOUBLE > FREE > FIFTY & DOUBLE > FIFTY '
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "only_once": False
        }

    def get_page(self) -> List[dict]:
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        [{
            "id": "服务ID",
            "name": "服务名称",
            "trigger": "触发器：cron/interval/date/CronTrigger.from_crontab()",
            "func": self.xxx,
            "kwargs": {} # 定时器参数
        }]
        """
        services = []
        return services

    def stop_service(self):
        """
        退出插件
        """
        pass

    def execute(self):
        """
        执行用户任务。如果用户任务不存在，则记录错误日志并发送系统通知
        """

        logger.info(f"开始执行任务")
        modulemanage=ModuleManager()
        modules = ModuleHelper.load(
            "app.plugins.custommodule.modules",
            filter_func=lambda _, obj: hasattr(obj, 'init_module') and hasattr(obj, 'init_setting')
        )
        for module in modules:
            module_id = module.__name__
            modulemanage._modules[module_id] = module
            try:
                # 生成实例
                _module = module()
                # 初始化模块
                _module.init_module()
                modulemanage._running_modules[module_id] = _module
                logger.info(f"Moudle Loaded：{module_id}")
            except Exception as err:
                logger.error(f"Load Moudle Error：{module_id}，{str(err)} ", exc_info=True)
        pass

    def __log_and_notify_error(self, message):
        """
        记录错误日志并发送系统通知
        """
        logger.error(message)
        self.systemmessage.put(message, title=f"{self.plugin_name}")
