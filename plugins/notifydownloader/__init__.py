from pathlib import Path
from typing import Any, List, Dict, Tuple, Optional, Union, Set
import time

from app.plugins import _PluginBase
from app.core.config import settings
from app.log import logger
from app.schemas import Notification, NotificationType

class NotifyDownloader(_PluginBase):
    # 插件名称
    plugin_name = "通知下载器"
    # 插件描述
    plugin_desc = "拦截特定下载器的下载请求，仅发送通知而不下载文件。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/jxxghp/MoviePilot-Plugins/main/icons/notify.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "Antigravity"
    # 插件配置项ID前缀
    plugin_config_prefix = "notifydownloader_"
    # 加载顺序
    plugin_order = 0
    # 可使用的用户级别
    auth_level = 2

    # 配置属性
    _enabled: bool = False
    _downloader_name: str = "Notify"
    _notify: bool = True

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._downloader_name = config.get("downloader_name") or "Notify"
            self._notify = config.get("notify")

    def get_state(self) -> bool:
        return self._enabled

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
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
                                            'model': 'notify',
                                            'label': '发送通知',
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
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'downloader_name',
                                            'label': '拦截下载器名称',
                                            'placeholder': '默认为 Notify'
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
                                            'text': '请在 设置 -> 下载器 中添加一个自定义下载器（类型任意，如Qbittorrent），名称需与此处配置一致。插件将拦截该下载器的所有下载请求。'
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
            "downloader_name": "Notify"
        }

    def get_page(self) -> List[dict]:
        return []

    def stop_service(self):
        pass

    def get_module(self) -> Dict[str, Any]:
        """
        获取插件模块声明，用于胁持系统模块实现（方法名：方法实现）
        """
        return {
            "download": self.download
        }

    def download(self, content: Union[Path, str, bytes], download_dir: Path, cookie: str,
                 episodes: Set[int] = None, category: Optional[str] = None, label: Optional[str] = None,
                 downloader: Optional[str] = None
                 ) -> Optional[Tuple[Optional[str], Optional[str], Optional[str], str]]:
        """
        拦截下载请求
        """
        if not self._enabled:
            return None
            
        # 检查是否为目标下载器
        if downloader != self._downloader_name:
            return None

        logger.info(f"NotifyDownloader 拦截到下载请求: {content}")

        # 发送通知
        if self._notify:
            title = "资源订阅通知"
            text = f"已发现资源并拦截下载：\n{content}"
            self.post_message(mtype=NotificationType.Manual, title=title, text=text)

        # 返回伪造的成功结果
        # 下载器名称、种子Hash、种子文件布局、错误原因
        fake_hash = f"notify_{int(time.time())}"
        return downloader, fake_hash, "NoSubfolder", ""
