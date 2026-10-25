# Alterações deste fork

Base: [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv), commit `a6b560a`, com alterações para Samsung Tizen até a versão local **1.2.4**.

## Dispositivos HDMI

- Cartões com nome do dispositivo, foto e identificação da porta.
- Leitura de nome e conexão pela API Samsung `VIDEOSOURCE`.
- Verde para conectado, vermelho para desconectado/sem sinal, cinza para status indisponível. Conexão/standby não é uma medição do estado elétrico do aparelho.
- Atualização a cada cinco segundos enquanto a interface estiver visível; suspensa no editor e no segundo plano.
- Editor aberto segurando OK por 650 ms ou com Play/Pause. Permite escolher HDMI genérico, Switch 2, Wii U, PS5 ou Steam Deck e informar um nome de até 40 caracteres.
- Validação de nome vazio; Salvar confirma, Voltar/Cancelar descarta. Preferências por porta mantidas no armazenamento local do app (`fmtv.hdmi.v1`).
- Configuração inicial de exemplo: HDMI 1 Switch 2, HDMI 2 Wii U, HDMI 3 PS5, HDMI 4 Steam Deck. Um nome válido informado pela TV é usado antes do exemplo; a edição manual tem prioridade.

## Logotipos

Disney+ e HBO Max usam SVGs locais, com proporção preservada e tamanho adequado tanto na prateleira quanto em Todos os Apps. As marcas não dependem dos ícones pequenos devolvidos pelo sistema. Fontes e créditos em `web/icons/vector-logo-sources.txt`; fotos de dispositivos em `home-device-sources.json` e `home-NOTICE.txt`.

## Tizen e TV aberta

- Atalho superior **Tizen** abre `com.samsung.tv.csfs`, a interface padrão Samsung.
- Atalho inferior **TV ao Vivo** mantém o fluxo original: selecionar a fonte TV e abrir `org.tizen.tv-viewer`. Quando a fonte não é listada, o viewer é aberto diretamente.
- Manifesto com operação principal, retomada sem recarga e metadados de multitarefa/prelaunch.
- Botão Home e inicialização foram vinculados ao novo app na Samsung usada durante o desenvolvimento. Esse vínculo é específico do aparelho/firmware e **não é configurado automaticamente por este repositório**. O fork não publica os auxiliares de alteração nativa usados localmente. Em outras TVs, siga a configuração de inicialização suportada pela Samsung; compatibilidade do botão Home não é prometida.

## Demonstração HTML

`docs/index.html` é um único arquivo portátil com CSS, JavaScript, fontes e imagens incorporados. Funciona offline, sem instalar nada e sem conectar a uma TV. Reproduz a interface real com apps, clima e estados HDMI fictícios; mostra mensagens de simulação ao abrir apps/Tizen/TV aberta. Setas, Enter, Esc, ponteiro e editor HDMI funcionam; há controles de dia/noite e entradas.

Recrie a demonstração com `python tools/build_demo.py`. O gerador usa valores de exemplo e não lê `config.properties`. Imagens de apresentação em `docs/demo-preview.png`.

## Validação e limites

Pacotes das versões 1.2.0 a 1.2.4 foram instalados em Samsung QN85B com Tizen 6.5. Testes locais no Edge, com APIs Tizen simuladas, cobriram imagens, estados HDMI, atualização, editor, persistência, cancelamento, nome vazio, OK longo sem abrir entrada, Tizen e TV aberta como ações separadas. Layout conferido em 720p e 1080p.

Os testes simulados não comprovam comportamento de sintonizador, CEC, retorno imediato pelo Home ou boot em todo firmware. A demonstração não controla dispositivos reais. Google TV e webOS herdados do upstream não foram validados neste fork.

## Privacidade e licenças

Configuração pessoal, IP da TV, chaves de API, certificados, senhas, pacotes assinados e logs locais não são publicados. A licença MIT e os créditos do projeto original são preservados. As marcas e fotos de produtos continuam pertencendo aos respectivos titulares; consulte os arquivos de atribuição antes de redistribuí-las fora deste contexto.
