from typing import Any, Dict, Literal, Optional
from openai import OpenAI
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

from pydantic import BaseModel, Field, field_validator, model_validator

_ = load_dotenv() # forcar a execucao

'''

# Tipos literais para providers suportados
ProviderType = Literal["openai", "google"]

class ModelConfig(BaseModel):
    """Configuração de um modelo de IA."""
    
    key_name: str = Field(..., description="Nome único para identificar o modelo")
    provider: ProviderType = Field(..., description="Provedor do modelo")
    model_name: str = Field(..., description="Nome do modelo no provedor")
    temperature: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=2.0, 
        description="Temperatura para geração (0.0 a 2.0)"
    )
    max_tokens: Optional[int] = Field(
        default=None, 
        gt=0, 
        description="Número máximo de tokens"
    )
    top_p: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Top-p para sampling"
    )
    
    class Config:
        # Permite campos extras se necessário
        extra = "forbid"
        # Usa enum values
        use_enum_values = True
        # Validação na atribuição
        validate_assignment = True
    
    @field_validator('key_name')
    @classmethod
    def validate_key_name(cls, v):
        """Valida se key_name não está vazio e não contém espaços."""
        if not v or not v.strip():
            raise ValueError("key_name não pode estar vazio")
        if ' ' in v:
            raise ValueError("key_name não pode conter espaços")
        return v.strip()
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v):
        """Valida se model_name não está vazio."""
        if not v or not v.strip():
            raise ValueError("model_name não pode estar vazio")
        return v.strip()
    
class EnvironmentConfig(BaseModel):
    """Configurações de ambiente."""
    
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="Chave da API OpenAI"
    )
    google_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY"),
        description="Chave da API Google"
    )
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        """Valida chave OpenAI se fornecida."""
        if v and not v.startswith('sk-'):
            raise ValueError("Chave OpenAI deve começar com 'sk-'")
        return v

class ModelsConfiguration(BaseModel):
    """Configuração completa dos modelos."""
    
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    models: list[ModelConfig] = Field(default_factory=list, description="Lista de configurações de modelos")
    
    # Mapeamento de provedores
    _provider_map: Dict[str, Any] = {
        "openai": OpenAI,
        # "google": ChatGoogleGenerativeAI  # Descomentie quando disponível
    }
    
    class Config:
        extra = "forbid"
        validate_assignment = True
    
    @model_validator(mode='after')
    def validate_provider_support(self):
        """Valida se todos os provedores são suportados."""
        models = self.models
        supported_providers = set(self._provider_map.keys())
        
        for model in models:
            if hasattr(model, 'provider') and model.provider not in supported_providers:
                raise ValueError(
                    f"Provedor '{model.provider}' não suportado. "
                    f"Provedores suportados: {list(supported_providers)}"
                )
        return self
    
    def create_chat_model(self, model_config: ModelConfig):
        """Cria um modelo de chat baseado na configuração."""
        if model_config.provider not in self._provider_map:
            raise ValueError(
                f"Provedor não suportado: {model_config.provider}. "
                f"Provedores suportados: {list(self._provider_map.keys())}"
            )
        
        model_class = self._provider_map[model_config.provider]
        
        # Parâmetros base
        params = {"model": model_config.model_name}
        
        # Adicionar parâmetros opcionais se fornecidos
        if model_config.temperature is not None:
            params["temperature"] = model_config.temperature
        if model_config.max_tokens is not None:
            params["max_tokens"] = model_config.max_tokens
        if model_config.top_p is not None:
            params["top_p"] = model_config.top_p
        
        # Adicionar API key se necessário
        if model_config.provider == "openai" and self.environment.openai_api_key:
            params["api_key"] = self.environment.openai_api_key
        elif model_config.provider == "google" and self.environment.google_api_key:
            params["api_key"] = self.environment.google_api_key
        
        return model_class(**params)
    
    def create_all_models(self) -> Dict[str, Any]:
        """Cria todos os modelos configurados."""
        created_models = {}
        
        for model_config in self.models:
            try:
                created_models[model_config.key_name] = self.create_chat_model(model_config)
                print(f"Modelo '{model_config.key_name}' criado com sucesso")
            except Exception as e:
                print(f"Erro ao criar modelo '{model_config.key_name}': {e}")
        
        return created_models
    
    def get_model_by_key(self, key_name: str) -> Optional[ModelConfig]:
        """Obtém configuração de modelo por key_name."""
        for model in self.models:
            if model.key_name == key_name:
                return model
        return None
    
    def add_model(self, model_config: ModelConfig) -> None:
        """Adiciona uma nova configuração de modelo."""
        # Verificar se key_name já existe
        if any(m.key_name == model_config.key_name for m in self.models):
            raise ValueError(f"Modelo com key_name '{model_config.key_name}' já existe")
        
        self.models.append(model_config)
    
    def remove_model(self, key_name: str) -> bool:
        """Remove um modelo pela key_name."""
        for i, model in enumerate(self.models):
            if model.key_name == key_name:
                del self.models[i]
                return True
        return False

# Configuração padrão dos modelos
DEFAULT_MODEL_CONFIGS = [
    ModelConfig(
        key_name="gemini_2.5_flash",
        provider="google",
        model_name="gemini-2.5-flash-preview-04-17",
        temperature=1.0,
    ),
    ModelConfig(
        key_name="3.5-turbo",
        provider="openai",
        model_name="gpt-3.5-turbo",
    ),
    ModelConfig(
        key_name="o4",
        provider="openai",
        model_name="o4-mini-2025-04-16",
    ),
    ModelConfig(
        key_name="gpt_4o",
        provider="openai",
        model_name="gpt-4o-2024-08-06",
    ),
]

# Instância global da configuração
config = ModelsConfiguration(models=DEFAULT_MODEL_CONFIGS)

# Criar todos os modelos
models = config.create_all_models()

'''

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

_PROVIDER_MAP = {
    "openai": ChatOpenAI,
    #"google": ChatGoogleGenerativeAI
}

MODEL_CONFIGS = [
    # {
    #     "key_name": "gemini_2.5_flash",
    #     "provider" : "google",
    #     "model_name": "gemini-2.5-flash-preview-04-17",
    #     "temprature": 1.0,
    # },
    {
        "key_name":"3.5-turbo",
        "provider":"openai",
        "model_name":"gpt-3.5-turbo",
    },
    {
        "key_name": "o4",
        "provider": "openai",
        "model_name": "o4-mini-2025-04-16",
    },
    {
        "key_name": "gpt_4o",
        "provider": "openai",
        "model_name": "gpt-4o-2024-08-06",
    },
]

def _create_chat_model(model_name: str, provider: str, temperature: float | None = None):
    if provider not in _PROVIDER_MAP:
        raise ValueError(f"Provedor nao suportado: {provider}. Provedores suportados sao: {list(_PROVIDER_MAP.keys())}")

    model_class = _PROVIDER_MAP[provider]
    params = {"model": model_name}
    if temperature is not None:
        params["temperature"] = temperature

    return model_class(**params)

models = {}

for config in MODEL_CONFIGS:
    models[config["key_name"]] = _create_chat_model(
        model_name=config["model_name"],
        provider=config["provider"],
        temperature=config.get("temperature")
    )

if __name__ == "__main__":
    print()