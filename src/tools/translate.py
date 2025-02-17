from typing import Any, Dict
from src.tools.base import BaseTool
from src.config import Config 
from openai import OpenAI


class TranslateTool(BaseTool):
    def __init__(self, name: str, config: Config):
        """
        翻译工具，继承自 EasyTool 类。
        :param name: 工具名称
        :param config: 配置对象，包含API密钥等信息
        """
        super().__init__(name, config)
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        self.llm_model = config.get('model') if config else None
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.openai_api_key}"
        }

    async def _translate_text(self, text: str, target_lang: str) -> str:
        """
        执行翻译操作
        :param text: 要翻译的文本
        :param target_lang: 目标语言
        :return: 翻译后的文本
        """
        messages = [
            {
                "role": "system",
                "content": f"你是一个专业的医学领域翻译。请将以下文本翻译成{target_lang}，保持专业性和准确性。只翻译title和abstract两个字段，其他字段不翻译，返回翻译结果，并保留原json格式,不要添加任何解释。"
            },
            {
                "role": "user",
                "content": text
            }
        ]

        response = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行翻译任务
        :param input_data: 包含以下字段的字典：
            - text: 要翻译的文本
            - target_lang: 目标语言
            - timeout: (可选) 超时时间
            - max_retries: (可选) 最大重试次数
        :return: 包含翻译结果的字典
        """
        text = input_data.get('text')
        target_lang = input_data.get('target_lang', '中文')
        timeout = input_data.get('timeout')
        max_retries = input_data.get('max_retries')

        if not text:
            self.logger.error("未提供待翻译文本")
            return {"error": "需要提供待翻译文本"}

        if not self.config.openai_api_key:
            self.logger.error("未配置OpenAI API密钥")
            return {"error": "未配置OpenAI翻译服务API密钥"}

        try:
            translated_text = await self._execute_operation(
                self._translate_text,
                text,
                target_lang,
                timeout=timeout,
                max_retries=max_retries,
                error_prefix="翻译操作"
            )

            self.logger.info(f"成功将文本翻译成{target_lang}")
            return {
                "original_text": text,
                "translated_text": translated_text,
                "target_language": target_lang
            }

        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    def __str__(self):
        return f"TranslatorTool(name={self.name})" 