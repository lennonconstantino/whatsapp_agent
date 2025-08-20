# Cadastro no MetaAPI - Whatsapp Business
- Como criar uma conta de desenvolvedor na Meta
    - https://developers.facebook.com/docs/development/register
        - Observações
            1. Durante o processo de cadastro, você precisará se verificar usando um número de telefone. Observe que este não será o número de telefone do seu cliente WhatsApp final. Em vez disso, você receberá um número de telefone de teste atribuído pela plataforma, que poderá ser alterado posteriormente para outro número de telefone.
            2. Após o registro, acesse seu painel e crie um aplicativo.
            3. Além disso, você precisará de uma Conta Meta Business (MBA) que será associada à sua conta real, ou poderá criar uma nova para vincular ao seu MBA. Você também pode pular essa etapa, pois será automaticamente solicitado a vincular ou criar um MBA na próxima etapa.
            4. DICA MAIS IMPORTANTE, crie um site simples que tenha:
            - Nome da empresa
            - O que vocês fazem (descrição clara)
            - Endereço/localização
            - Horário de funcionamento
            - Forma de contato
            - Algumas fotos dos produtos
            5. Caminho: Vá no Business Manager da Meta → Entre em Configurações de Negócios → Clique na sua empresa → Na seção Detalhes da empresa, adicione/atualize a URL do seu site.
    - Adicione um produto do WhatsApp ao seu aplicativo
        - Após criar um aplicativo na sua conta de desenvolvedor Meta, você será solicitado a adicionar produtos a ele. Aqui, você deve escolher o WhatsApp e seguir o processo de configuração. Caso ainda não tenha criado, crie uma conta Meta Business aqui. Assim que terminar, você terá uma conta de teste do WhatsApp Business e um número de telefone de teste.
    - Adicionar um Número de Destinatário
        1. No menu à esquerda do Painel do Aplicativo, navegue até WhatsApp > Configuração da API. Lá, em "Enviar e receber mensagens", selecione o campo "Para" e escolha "Gerenciar lista de números de telefone". Aqui, você pode adicionar um número de telefone com permissão para enviar e receber mensagens do seu número de teste. Idealmente, este deve ser o seu próprio número de telefone, pois você deseja testar seu aplicativo. Antes de vincular esta conta da API do WhatsApp a um número real, você só poderá adicionar até 5 números de destinatários.
        2. Em WhatsApp > Configuração da API, agora você pode enviar uma mensagem de teste preenchendo o campo de origem com seu número de telefone de teste e o campo de destino com seu número de destinatário (seu próprio número de telefone).
        3. Gere um token de acesso. Este é o seu WHATSAPP_API_TOKEN, que precisaremos mais adiante.

    - Gerar Token
        https://developers.facebook.com/docs/whatsapp/business-management-api/get-started#tokens-de-acesso-do-usu-rio
    - Webhook Notification
        - https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples/
        - https://developers.facebook.com/blog/post/2022/10/24/sending-messages-with-whatsapp-in-your-python-applications/

# Ngrok:
- Se cadastrar no site: https://dashboard.ngrok.com/
- Na Aba Getting Started, está bem descrito os próximos passos.
    - Instalar os pacotes de acordo ao seu sistema operacional (Mac, Linux, Windows)
Ephemeral Domain
```bash
ngrok config add-authtoken $TOKEN
ngrok http http://localhost:$PORT
```

# Configuração do Webhook:
- Depende do Ngrok configurado

- Preencha a “URL de Callback", com o link gerado no Ngrok e adicione /webhook no final do endpoint.
- Preencha o “Verificar token”, com a chave que vai ficar no seu servidor.
- Habilitar os “campos do webhook”: flows e messages

# Toda vez que rodar o Whatsapp Business para testar
- rodar o Ngrok
- pegar o endpoint Forwaring https://...ngrok-free.app
- rodar o server
- ir no na pagina da Meta de Configuração do Webhook
- atualizar a URL de Callback:
    - https://...ngrok-free.app/webhook
    - VERIFICATION_TOKEN
    - atualizar
