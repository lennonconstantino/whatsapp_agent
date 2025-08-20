from abc import ABC, abstractmethod
from typing import Union, Callable
import json
import os
from pathlib import Path

# 1. Interface para carregadores de mensagem do sistema
class SystemMessageProvider(ABC):
    @abstractmethod
    def get_message(self, context: str = "", **kwargs) -> str:
        pass

# 2. Implementações concretas dos provedores
class StaticSystemMessageProvider(SystemMessageProvider):
    """Provedor com mensagem estática (comportamento atual)"""
    
    def __init__(self, message: str):
        self.message = message
    
    def get_message(self, context: str = "", **kwargs) -> str:
        return self.message.format(context=context)


class FileSystemMessageProvider(SystemMessageProvider):
    """Provedor que carrega de arquivo"""
    
    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)
    
    def get_message(self, context: str = "", **kwargs) -> str:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                template = file.read().strip()
                return template.format(context=context, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"System message template not found: {self.filepath}")


class ConfigSystemMessageProvider(SystemMessageProvider):
    """Provedor que carrega de arquivo de configuração JSON/YAML"""
    
    def __init__(self, config_path: Union[str, Path], template_key: str = "system_message"):
        self.config_path = Path(config_path)
        self.template_key = template_key
    
    def get_message(self, context: str = "", **kwargs) -> str:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                template = config.get(self.template_key, "")
                return template.format(context=context, **kwargs)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load system message from config: {e}")


class EnvironmentSystemMessageProvider(SystemMessageProvider):
    """Provedor que carrega de variáveis de ambiente"""
    
    def __init__(self, env_var: str = "SYSTEM_MESSAGE_TEMPLATE"):
        self.env_var = env_var
    
    def get_message(self, context: str = "", **kwargs) -> str:
        template = os.getenv(self.env_var)
        if not template:
            raise ValueError(f"Environment variable {self.env_var} not found")
        return template.format(context=context, **kwargs)


class DynamicSystemMessageProvider(SystemMessageProvider):
    """Provedor que permite construção dinâmica da mensagem"""
    
    def __init__(self, builder_func: Callable):
        self.builder_func = builder_func
    
    def get_message(self, context: str = "", **kwargs) -> str:
        return self.builder_func(context=context, **kwargs)


# 3. Factory para criar provedores
class SystemMessageProviderFactory:
    @staticmethod
    def create_static(message: str) -> StaticSystemMessageProvider:
        return StaticSystemMessageProvider(message)
    
    @staticmethod
    def create_from_file(filepath: Union[str, Path]) -> FileSystemMessageProvider:
        return FileSystemMessageProvider(filepath)
    
    @staticmethod
    def create_from_config(config_path: Union[str, Path], 
                          template_key: str = "system_message") -> ConfigSystemMessageProvider:
        return ConfigSystemMessageProvider(config_path, template_key)
    
    @staticmethod
    def create_from_env(env_var: str = "SYSTEM_MESSAGE_TEMPLATE") -> EnvironmentSystemMessageProvider:
        return EnvironmentSystemMessageProvider(env_var)
    
    @staticmethod
    def create_dynamic(builder_func: Callable) -> DynamicSystemMessageProvider:
        return DynamicSystemMessageProvider(builder_func)