# Wiki Yuv

## Visão geral da plataforma YUV

A plataforma YUV oferece uma solução completa para o rastreamento, monitoramento de ativos e gestão de frotas. Todos os módulos foram projetados para serem intuitivos, eficientes e centralizarem informações críticas para tomada de decisão.

## BI

### BI: Descrição

O módulo BI da YUV é o ambiente de análise avançada de dados da operação. Ele transforma os dados coletados pelos ativos em informações visuais e estratégicas para apoiar a tomada de decisões mais rápidas, baseadas em evidência.

### BI: Filtros Inteligentes

No topo do painel, estão disponíveis filtros para segmentar os dados de forma personalizada. É possível cruzar as informações por:

- Cliente

- Ativos

- Motoristas

- Tipos de Alarme

- Período (data/hora)

Após aplicar os filtros, clique em "Gerar" para atualizar os gráficos e painéis com os dados correspondentes.

### BI: Painéis de Análise

O módulo apresenta gráficos dinâmicos e interativos para facilitar a análise visual de padrões operacionais, riscos e oportunidades. Os principais painéis são listados nas seções abaixo.

### BI: Ocorrências

Gráfico de status das ocorrências registradas no período, categorizadas por:

- Sem risco

- Com risco

- Aguardando tratativa

Esse painel ajuda a identificar gargalos operacionais e prioridades de atuação.

### BI: Alarmes por Período

Gráfico (linha ou barras) com a distribuição temporal dos alarmes.

Utilizações práticas:

- Identificação de picos de alertas

- Análise de comportamento ao longo do dia/semana

- Diagnóstico de falhas repetidas

### BI: Top 10 Motoristas com Mais Alarmes

Ranking dos motoristas que mais geraram eventos de alarme.

Ajuda na:

- Identificação de condutas inadequadas

- Planejamento de feedbacks ou treinamentos

- Gestão de risco por motorista

### BI: Top 10 Placas com Mais Alarmes

Ranking dos veículos com maior número de alertas.

Indica:

- Ativos com possíveis falhas técnicas

- Riscos elevados por mau uso

- Necessidade de manutenção ou análise mais profunda

### BI: Quantidade de Alarmes por Tipo

Gráfico de pizza ou barras com a distribuição por tipo de alarme.

Exemplos:

- Excesso de velocidade

- Desconexão

- Entrada em cerca eletrônica

- Ignição fora de horário

Permite visualizar quais eventos são mais frequentes na operação.

### BI: Tabela de Alarmes

Tabela completa com os dados detalhados de cada evento de alarme:

| IMEI | Identificador | Tipo de Alarme | Data/Hora |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

### BI: Tabela de Ocorrências

Tabela com os eventos registrados (manualmente ou automaticamente), contendo:

| Cliente | Identificador | Motorista | IMEI | Último Alarme | Tipo | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | ... | ... |

### BI: Dicas de Uso

- Combine filtros para investigações mais precisas (ex: motorista + tipo de alarme + período)

- Use os rankings “Top 10” para programas de feedback ou correções de rota

- Exporte capturas dos gráficos para relatórios mensais

### BI: Benefícios

- Identificação rápida de comportamentos anormais

- Redução de riscos e falhas operacionais

- Apoio à manutenção preditiva, treinamentos e planejamento

- Melhoria contínua baseada em dados reais e atualizados

## Cadastros

### Cadastros: Ativos - Descrição

O módulo Ativos permite cadastrar, editar e gerenciar todos os veículos, máquinas ou equipamentos rastreados pela plataforma. Cada ativo é vinculado a um equipamento (IMEI) e pode ser identificado por nome, prefixo, modelo, cor e outros campos.

### Cadastros: Ativos - Tela Principal

A tabela apresenta os seguintes campos:

| Campo | Descrição |
| --- | --- |
| Identificador | Nome único ou placa do ativo |
| Cliente | Empresa vinculada |
| Modelo / Ano | Informações do ativo |
| IMEI | Número do equipamento |
| # (Ações) | Menu de edição |

Inclui campo de pesquisa rápida e botão + Cadastrar.

### Cadastros: Ativos - Cadastro e Edição

Campos disponíveis ao cadastrar ou editar:

| Campo | Descrição |
| --- | --- |
| Identificador | Nome exibido (ex: placa) |
| Prefixo | Código secundário |
| Fabricante | Marca do ativo |
| Modelo | Ex: HR-V, Caminhão 3/4 |
| Ano | Ano de fabricação |
| Cor | Cor (opcional) |
| IMEI | Equipamento vinculado |
| Cliente | Empresa responsável |

### Cadastros: Ativos - Vinculação com Equipamento

Todo ativo precisa estar vinculado a um equipamento (IMEI) previamente cadastrado, para que haja rastreamento e vídeo associados corretamente.

### Cadastros: Ativos - Aplicações Comuns

- Gerenciamento por cliente

- Atualização de dados em caso de troca/venda

- Controle de ativos sem imei

- Localização de falhas de cadastro

### Cadastros: Ativos - Boas Práticas

- Use nomenclatura padronizada (ex: PLACA-CLIENTE)

- Evite duplicação de IMEI

- Sempre vincule ao cliente correto

### Cadastros: Chips - Descrição

O módulo Chips permite cadastrar e gerenciar os cartões SIM responsáveis pela conectividade dos equipamentos.

### Cadastros: Chips - Tela Principal

| Campo | Descrição |
| --- | --- |
| Operadora | Provedora (ex: Vivo, Claro) |
| Número | Número do chip |
| ICCID | Serial do chip |
| IMEI | Equipamento vinculado |
| # (Ações) | Edição ou exclusão |

Inclui busca por número ou operadora.

### Cadastros: Chips - Cadastro de Chip

Clique em + Cadastrar e preencha:

| Campo | Descrição |
| --- | --- |
| Número | Com DDD |
| ICCID | Serial de 19-20 dígitos |
| Operadora | Seleção da lista |

ICCID é opcional, mas recomendado.

### Cadastros: Chips - Operadoras Suportadas

- Vivo

- Claro

- Tim

- Oi

- Vodafone

- Allcom (Claro, Vivo)

- Algar

- Sierra

### Cadastros: Chips - Vinculação com Equipamentos

Chips devem ser vinculados a equipamentos (IMEIs) para habilitar a comunicação em tempo real.

### Cadastros: Chips - Boas Práticas

- Cadastre com ICCID correto

- Atualize chips após troca de equipamento

- Use descrições genéricas apenas em testes

### Cadastros: Usuários - Descrição

Permite criar, editar e gerenciar os acessos à plataforma. Dividido em:

- Minha empresa (estrutura própria)

- Meus clientes (estrutura delegada)

### Cadastros: Usuários - Tela Principal

| Campo | Descrição |
| --- | --- |
| Foto | Avatar do usuário |
| Nome | Nome completo |
| E-mail | Login e notificações |
| Grupo de Permissão | Regras de acesso |
| Ativo | Status (ativo/inativo) |
| # (Ações) | Editar ou excluir |

Permite alternar entre estruturas e buscar por nome/e-mail.

### Cadastros: Usuários - Cadastro

Campos disponíveis:

| Campo | Descrição |
| --- | --- |
| Foto | Upload opcional |
| Nome | Nome completo |
| E-mail | Para login |
| Senha / Confirmação | Mínimo 8 caracteres |
| Grupo de Permissão | Permissões associadas |
| Fuso Horário | Ex: GMT -3:00 |
| Idioma | pt-BR padrão |

### Cadastros: Clientes - Descrição

Cadastro e gestão de empresas/unidades que usarão a plataforma. Cada cliente pode ter usuários, ativos e permissões próprios.

### Cadastros: Clientes - Tela Principal

| Campo | Descrição |
| --- | --- |
| Nome | Nome da empresa |
| E-mail | Principal |
| Grupo de Permissão | Regras de acesso |
| Configuração de Ocorrência | Padrão ou personalizada |
| Ativo | Status |
| # (Ações) | Editar |

Inclui busca rápida por nome ou e-mail.

### Cadastros: Clientes - Cadastro (Etapa 1 - Dados)

| Campo | Descrição |
| --- | --- |
| Nome | Nome do cliente |
| CEP / Endereço / Bairro / Cidade / Complemento |  |
| Telefone | Contato |
| Observação | Anotações |
| Configuração de Ocorrência | Escolha da regra padrão ou customizada |

### Cadastros: Clientes - Cadastro (Etapa 2 - Acesso)

| Campo | Descrição |
| --- | --- |
| Nome | Administrador do cliente |
| E-mail | Login |
| Senha / Confirmação |  |
| Fuso Horário / Idioma |  |
| Grupo de Permissão |  |

### Cadastros: Clientes - Observações e Boas Práticas

- Clientes inativos não acessam o sistema

- Use nomes e grupos padrão para facilitar cadastros

- Utilize e-mails reais para notificações e suporte

### Cadastros: Equipamentos - Descrição

Gerenciamento de equipamentos instalados nos veículos, vinculando IMEI, chip e ativo.
Modelos: 
jimi - JC371,JC450,JC400AD,JC400D,JC400A,JC400P,JC181
Hikivision - G40
Streamax - AG600
Cadastros: Equipamentos - Tela Principal

| Campo | Descrição |
| --- | --- |
| IMEI | Identificador único |
| Modelo | Ex: JC400AD, LL303 |
| Cliente / Ativo / Chip | Associações |
| Último Heartbeat | Última comunicação |
| Situação | Online/Offline |
| Status | Ativo ou inativo |

### Cadastros: Equipamentos - Cadastro

Campos para novo equipamento:

- IMEI (obrigatório)

- Modelo

- Chip (opcional)

- Botão "Requisitar Alarme"

### Cadastros: Equipamentos - Edição

Permite atualizar cliente, ativo, chip e modelo.

### Cadastros: Equipamentos - Indicadores e Observações

- Situação Online/Offline baseado no último heartbeat

- Equipamentos podem estar sem vínculo inicial

### Cadastros: Grupos de Permissão - Visão Geral

Gerencia os grupos de acesso da plataforma, definidos por:

- Nome

- Tipo de usuário: Dealer ou Customer

- Quantidade de usuários vinculados

### Cadastros: Grupos de Permissão - Tela Principal

Campos visíveis:

| Campo | Descrição |
| --- | --- |
| Nome | Do grupo |
| Tipo | Dealer / Customer |
| Qtd. de Usuários | Total de usuários nesse grupo |
| Ações | Editar / Excluir |

Inclui busca rápida e botão + Cadastrar.

### Cadastros: Grupos de Permissão - Cadastro

| Campo | Descrição |
| --- | --- |
| Nome | Nome do grupo |
| Tipo de Usuário | Dealer ou Customer |

### Cadastros: Grupos de Permissão - Ações

- Editar grupo

- Excluir (se não houver usuários vinculados)

### Cadastros: Motoristas - Descrição

Registro e controle de motoristas vinculados aos clientes e ativos. Gerencia CNH, exames médicos, categorias e Face ID.

### Cadastros: Motoristas - Tela Principal

| Campo | Descrição |
| --- | --- |
| Foto | Imagem do motorista |
| Cliente | Empresa vinculada |
| Nome | Completo |
| Data de Nascimento |  |
| CNH | Número da carteira |
| CNH expira em | Validade |
| Exame médico expira em | Validade |
| Identificador | Código interno |
| Categorias | Habilitação (A-E) |
| # (Ações) | Edição |
| Habilitar Acesso App | Desabilitado / Habilitado |
| Face ID | Upload das imagens |

Busca rápida por nome ou cliente.

### Cadastros: Motoristas - Cadastro

| Campo | Descrição |
| --- | --- |
| Foto | Opcional |
| Nome | Completo |
| Cliente | Vinculado |
| Identificador | Código interno |
| Data de nascimento | dd/mm/aaaa |
| CNH e validade |  |
| Exame médico e validade |  |
| Categorias | A, B, C, D, E |

### Cadastros: Motoristas - Observações e Boas Práticas

- Associe corretamente ao cliente

- Atualize CNH e exames para evitar bloqueios

- Use identificadores padrões (ex: matrícula)

- No cadastro do motorista, não deve ser utilizado acento.

### Cadastros: Checklist Motorista

| Campo | Descrição |
| --- | --- |
| Nome | Completo |
| Motorista | Completo |

### Cadastros: Checklist Motorista - Observações e Boas Práticas

| Item do Checklist |
| --- |
| Tipo de Atributo |
| Verdadeiro/Falso |
| Data |
| Data e Hora |
| Arquivo/ Imagem |
| Número |
| Porcentagem |
| Texto |
| Hora |

### Cadastros: Configurações de Ocorrência - Descrição

Personaliza avaliação e classificação de alarmes com base em quantidade mínima, tempo e gravidade.

### Cadastros: Configurações de Ocorrência - Tela Principal

| Campo | Descrição |
| --- | --- |
| Nome | Da configuração |
| Qtd. de Clientes | Usando esta configuração |
| # (Ações) | Editar |

Busca por nome.

### Cadastros: Configurações de Ocorrência - Cadastro

| Campo | Descrição |
| --- | --- |
| Nome | Nome da configuração |
| Tipo de Alarme | Ex: Risco de Colisão |
| Qtd. Mínima | Número de ocorrências |
| Período | Tempo (minutos) |
| Gravidade | Baixo, Médio, Alto |

Pode-se adicionar/remover múltiplos alarmes.

### Cadastros: Configurações de Ocorrência - Observações e Boas Práticas

- Crie configurações padrão reutilizáveis

- Nomeie com clareza (ex: "Cliente A – Perfil Crítico")

- Altere parâmetros conforme comportamento da frota

## Checklist Motorista

### Checklist de motorista: Descrição

- Inicialmente a função deve ser liberada por solicitação ao time Yuv, para a inclusão da funcionalidade no seu sistema.

- Com a funcionalidade liberada, devemos instalar o APK no aparelho do motorista que irá utilizar a funcionalidade. Vale ressaltar que o APK é exclusivo para utilização.

- Com o APK instalado devemos configurar as permissões de usuários para a criação, edição e acompanhamento do usuario responsável.

- Edição da permissão: Para editarmos a visualização da funcionalidade, devemos ir até Grupo de permissão, Revendedor e clicar em editar o grupo e habilitar as seguintes funcionalidades conforme a imagem abaixo

![Imagem do Notion](https://app.notion.com/image/attachment%3Aa4f90a78-df2b-4a65-b1bc-b8783d87bcf5%3Aimage.png?table=block&id=1cbc5336-61ae-83b7-b856-01e6cae1980d&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

- Com esses funcionalidades habilitadas ao grupo de permissão do usuario o mesmo poderá habilitar o motorista para a utilização do APK, criar e editar o check list.

- Cadastro do motorista para o login no APK. Agora devemos seguir até Cadastro – motorista e habilitar o login.

![Imagem do Notion](https://app.notion.com/image/attachment%3Aa934eb51-b019-457e-bf03-bfa9f2fedc65%3Aimage.png?table=block&id=6d9c5336-61ae-8218-bfd9-0180e1fb7ba7&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Ao habilitar a chave Acesso ao appirá abrir a senha.

O login será o CPF do motorista e a senha deve ser cadastrada e repassada ao motorista em questão.

- Caso o motorista já esteja cadastrado podemos fazer a edição e habilitar a chave do APP.

- Com o motorista devidamente cadastrado o próximo passo será a configuração do Check List.

- Para o cadastro e edição do check list iremos em cadastros/ checklist motorista no menu lateral esquerdo. Clicando em cadastrar se abrirá a seguinte tela.

![Imagem do Notion](https://app.notion.com/image/attachment%3Ab1b4829f-9882-4f65-b7f1-97d8b95c8d8f%3Aimage.png?table=block&id=3cec5336-61ae-83e7-83c9-014cac42e450&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Nessa tela iremos dar um nome ao check list, incluir os motoristas que utilizarão e editar os itens que desejamos nesse check list.

Itens do check list:

![Imagem do Notion](https://app.notion.com/image/attachment%3A0aa0b5f6-b238-4706-92e3-fed749eeed2c%3Aimage.png?table=block&id=f6ec5336-61ae-8343-ba76-0118ba4bc4a5&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Os campos que irão conter nesse check list, são totalmente personalizados e podemos definir o formato de resposta como mostra a imagem acima bem como tornar o seu preenchimento obrigatorio. Vale ressaltar que podemos criar quantos checklists forem nescessarios.

- Agora que cadastramos nosso motorista e criamos nosso checklist Passaremos a utilização.

### Checklist Motorista - Passo a passo

Login no APK (motorista)

1. Abra o app no celular.

1. Digite o CPF (somente números).

1. Digite a senha informada pela empresa.

1. Toque em Entrar.

1. Selecione o checklist disponível, preencha e anexe fotos quando solicitado, depois Finalizar/Enviar.

Acompanhar no Histórico (gestor)

1. Na plataforma web, vá em Checklists → Histórico.

1. Use o campo Pesquisar para filtrar por checklist.

1. Observe as colunas: Motorista, Checklist, Ativo, Data, Status, Ações.

- Status:

- Em viagem = checklist em andamento (motorista ainda preenchendo/viagem ativa).

- Finalizado = checklist concluído e enviado.

Ver detalhes em Ações

- Na linha desejada, clique no ícone de Ações (editar/visualizar).

- Abra o checklist para acompanhar respostas e as fotos anexadas pelo motorista.

- Histórico de Checklist

![Imagem do Notion](https://app.notion.com/image/attachment%3Aecd02fc2-4a35-4087-91a3-615019e7fd0e%3Aimage.png?table=block&id=e84c5336-61ae-8365-9096-81828f814e30&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Detalhes do Checklist

![Imagem do Notion](https://app.notion.com/image/attachment%3Afc728a0f-4416-4c23-b34e-71ce32aa9f48%3Aimage.png?table=block&id=368c5336-61ae-834d-9e6a-81a8115b9b22&spaceId=05ff8f53-497d-415d-9872-38d4eb2d0d4c&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Importante: Ao desligar a ignição do veículo (ignição off), o app desvincula automaticamente o motorista do veículo e encerra a viagem.

## Comandos

### Comandos: Descrição

O módulo Comandos permite a comunicação direta com os equipamentos da plataforma YUV, enviando instruções e recebendo respostas em tempo real.

É utilizado principalmente para:

- Diagnósticos remotos

- Testes de funcionamento

- Atualizações ou consultas de dados operacionais

### Comandos: Tela Principal

A interface inicial apresenta:

| Campo | Descrição |
| --- | --- |
| Histórico de Comandos | Lista de equipamentos recentemente acessados |
| Status | Indica se o equipamento está Online ou Offline |
| Equipamento | Modelo e IMEI do dispositivo selecionado |
| Cliente | Proprietário vinculado ao equipamento |
| Mapa | Exibição geográfica dos equipamentos conectados |

##### Busca Rápida

Há um campo de pesquisa para localizar equipamentos diretamente pelo IMEI.

### Comandos: Comunicação com o Equipamento

Ao clicar em um equipamento na lista, abre-se um painel com:

| Campo | Descrição |
| --- | --- |
| Conversa | Histórico dos comandos enviados e respostas recebidas |
| Envio de Comandos | Campo de entrada para comandos manuais |
| Status Atual | Exibe dados como versão de firmware, localização GNSS, nível de bateria etc. |

##### Envio de Comandos

Digite o comando no campo e clique no ícone de envio (avião de papel) para transmiti-lo.

### Comandos: Cadastro de Novo Comando

Para iniciar comunicação com um novo equipamento (não listado no histórico):

| Campo | Descrição |
| --- | --- |
| Novo Comando | Botão para buscar e iniciar contato com um novo IMEI |

### Comandos: Observações Importantes

- Apenas dispositivos Online recebem comandos imediatamente

- A resposta pode levar alguns segundos, dependendo da conexão de rede

- Equipamentos Offline só responderão após reconectarem

### Comandos: Boas Práticas

- Sempre verifique o status Online antes de enviar comandos importantes

- Use comandos padrões de diagnóstico (ex: versão, GNSS) antes de enviar ações críticas

- Mantenha registro de comandos enviados para fins de auditoria ou análise futura

## Como acessar o BI

### Como acessar o BI: Descrição

O módulo BI (Business Intelligence) da plataforma YUV disponibiliza dashboards dinâmicos com indicadores de desempenho da frota e eventos registrados pelos rastreadores.

### Como acessar o BI: Objetivo

Oferecer uma visão gerencial para análise de comportamento, produtividade e segurança dos ativos e motoristas.

### Como acessar o BI: Passo a passo

1. Acesse o menu: BI, localizado na barra lateral esquerda

1. Escolha entre os dashboards disponíveis, como:

- Eventos e Alarmes

- Desempenho dos Motoristas

- Ativos Online/Offline

1. Utilize os filtros (data, cliente, tipo de evento) para refinar a análise

1. Exporte gráficos ou relatórios utilizando os botões de exportação (Excel ou PDF)

### Como acessar o BI: Observações

- O BI é atualizado em tempo real com base nos dados dos dispositivos ativos

- É possível solicitar dashboards personalizados por meio da equipe de suporte YUV

- O acesso aos dashboards depende do Grupo de Permissão atribuído ao usuário

## Como cadastrar um ativo

### Cadastro de Ativos: Descrição

O cadastro de ativos na plataforma YUV é utilizado para vincular veículos ou equipamentos a um cliente, permitindo a gestão de localização, comandos e relatórios operacionais.

### Cadastro de Ativos: Objetivo

Cadastrar um novo ativo, associando-o a um equipamento (IMEI) já existente no sistema.

### Cadastro de Ativos: Passo a Passo

1. Acesse o menu Cadastros > Ativos

1. Clique no botão "Cadastrar" no canto superior direito.

1. Preencha os campos obrigatórios:

- Identificador: Nome ou código interno do ativo

- Prefixo: (Opcional) código visual no veículo

- Fabricante: Marca do veículo ou equipamento

- Modelo: Modelo do ativo (ex.: "LL303", "JC400")

- Ano: Ano de fabricação (opcional)

- Cor: Cor principal do ativo

- Equipamento: Selecione o IMEI do dispositivo instalado

- Cliente: Associe o ativo a um cliente já cadastrado

1. Após preencher os dados, clique em "Editar" ou "Salvar".

### Cadastro de Ativos: Observações Importantes

- Um equipamento (IMEI) só pode ser vinculado a um único ativo.

- O Identificador bem definido facilita buscas e relatórios.

- O cliente precisa estar cadastrado previamente para poder vincular um ativo a ele.

## Como configurar alertas

### Como configurar alertas: Descrição

A configuração de alertas na plataforma YUV permite monitorar eventos específicos gerados pelos equipamentos, como colisões, curvas bruscas ou ausência de atividade.

### Como configurar alertas: Objetivo

Permitir que o usuário receba notificações automáticas sobre comportamentos críticos ou situações de risco identificadas pelos rastreadores.

### Como configurar alertas: Passo a passo

1. Acesse o menu: Cadastros > Configurações de Ocorrências

1. Clique no botão "Cadastrar" no canto superior direito.

1. Preencha os campos necessários:

- Nome: identificação da nova configuração

- Parâmetros:

- Tipo de Alarme: escolha o evento a ser monitorado (ex.: Risco de Colisão, Olhos Fechados)

- Quantidade Mínima: número mínimo de eventos para gerar a ocorrência

- Período: intervalo de tempo (em minutos) para avaliação

- Gravidade: selecione o nível (Baixo, Médio, Alto)

1. Para adicionar mais de um parâmetro, clique no botão "+"

1. Finalize clicando em "Cadastrar"

### Como configurar alertas: Observações

- A configuração personalizada de alertas permite adaptar a severidade conforme o perfil do cliente ou frota.

- Pode ser vinculada a clientes específicos na tela: Cadastros > Clientes

- As ocorrências geradas alimentam os dashboards e relatórios da plataforma

## Como enviar um comando

### Comandos: Descrição

O envio de comandos permite interagir diretamente com os equipamentos (rastreadores) da plataforma YUV para executar ações específicas, como atualizações, configurações ou diagnósticos.

### Comandos: Objetivo

Permitir que o usuário envie comandos operacionais para ativos conectados, com finalidades como:

- Consultar status do dispositivo

- Realizar ajustes remotos

- Executar ações administrativas ou técnicas

### Comandos: Passo a Passo

1. Acesse o menu → Comandos

1. Na tela, localize o Histórico de Comandos e clique em "Novo Comando" no canto superior direito.

1. Preencha os campos obrigatórios:

- Equipamento: Selecione o dispositivo (por IMEI)

- Comando: Digite o comando de acordo com o modelo do equipamento

1. Clique no ícone de Enviar para transmitir o comando

### Comandos: Observações Importantes

- Nem todos os equipamentos aceitam os mesmos comandos. Verifique a compatibilidade na documentação técnica do modelo.

- O histórico de comandos exibe o status de envio: sucesso, falha, ou pendente.

- Dispositivos offline não recebem comandos imediatamente; o envio será refeito quando o equipamento voltar a se comunicar.

## Como identificar se um equipamento está offline

### Como identificar se um equipamento está offline: Descrição

O status de conectividade dos equipamentos na plataforma YUV é fundamental para garantir o rastreamento contínuo e a coleta de dados. Equipamentos offline podem indicar problemas de rede, energia ou instalação.

### Como identificar se um equipamento está offline: Objetivo

Identificar rapidamente se um dispositivo deixou de se comunicar com a plataforma.

### Como identificar se um equipamento está offline: Passo a passo

1. Acesse o menu: Rastreamento

1. Observe o contador no topo da tela:

- Online: quantidade de dispositivos ativos

- Offline: quantidade de dispositivos que não estão enviando dados

1. Utilize a barra de filtros para exibir apenas dispositivos offline

1. Verifique o último heartbeat (última comunicação):

- Se a data for muito antiga, o equipamento está inativo

1. Clique sobre o ativo para visualizar detalhes:

- Data/hora da última posição

- Última comunicação recebida

### Como identificar se um equipamento está offline: Observações

- Equipamentos offline podem ter como causa:

- Falta de sinal GSM (operadora)

- Problemas de energia no veículo

- Falha no chip de dados

- Problemas no próprio dispositivo

- Heartbeats muito antigos (dias ou semanas) indicam falha crítica

### Como identificar se um equipamento está offline: Boas práticas

- Configure alertas automáticos para detectar inatividade superior a 24h

- Priorize a verificação de dispositivos offline em áreas críticas (logística, segurança, emergência)

- Verifique se a falha está no dispositivo ou na linha de comunicação (chip/SIM card)

## Dashboard

### Dashboard: Descrição

O Dashboard da plataforma YUV é a visão geral em tempo real de toda a operação. Ele consolida dados operacionais e destaca os principais alertas, riscos e status de conectividade dos ativos.

> Ideal para monitoramento instantâneo, gestão de incidentes e acompanhamento do estado geral da frota.

### Dashboard: Visão Rápida

O topo do Dashboard exibe os seguintes indicadores-chave da operação:

| Indicador | Significado |
| --- | --- |
| Ocorrências | Total de eventos registrados no período |
| Aguardando Tratativa | Ocorrências sem resolução registrada |
| Online | Ativos com comunicação ativa |
| Offline | Ativos que não estão reportando dados |

Os dados são atualizados automaticamente caso a opção "Atualização automática" esteja habilitada (botão no canto superior direito).

### Dashboard: Riscos Operacionais

Abaixo dos indicadores, há uma barra de risco com a distribuição das ocorrências por gravidade:

- Baixo Risco – Notificações informativas

- Médio Risco – Desvios, ignição fora de horário

- Alto Risco – Falhas críticas, bloqueios, alertas de segurança

Essas classificações ajudam a priorizar respostas rápidas e decisões operacionais.

### Dashboard: Tabela de Eventos

Tabela que exibe detalhes de eventos por ativo, incluindo alarmes, riscos e status de conexão:

| Cliente | IMEI | Data | Status | Tipo | Risco | # |
| --- | --- | --- | --- | --- | --- | --- |

> Útil para auditoria rápida ou detecção de padrões de comportamento.

### Dashboard: Uso Estratégico

O Dashboard é ideal para:

- Supervisores de operações em tempo real

- Equipes de suporte técnico

- Times de segurança e manutenção

- Diagnóstico e triagem de falhas de conectividade

### Dashboard: Dicas de Monitoramento

- Muitos dispositivos offline podem indicar falhas generalizadas (rede, energia, equipamento).

- Ocorrências sem tratativa são prioridade para mitigar riscos.

- Ativos com risco alto devem ser verificados de imediato.

## Equipamento não comunica na plataforma

##### 1. Verificações Iniciais

Pergunta 1: O LED azul do equipamento está FIXO?

- Se NÃO:

➤ Verifique se o equipamento está em área com cobertura de internet.

➤ Certifique-se de que o chip inserido é de APN Privada.

➤ Se SIM, envie o comando de APN conforme modelo e firmware do equipamento.

- Se SIM:

➤ Faça o envio do comando SERVER, conforme a plataforma, modelo e firmware.

2. Comandos de APN por modelo e firmware

| Modelo | Comando de APN |
| --- | --- |
| JC450 | APN,NOME_APN,,,,LOGIN,,SENHA,,,IP,,IP |
| JC400 FW BBSA ou FOBA | APN666666,,,,NOMEAPN#######LOGIN###SENHA##### |
| JC400 FW WABA | APNNOMEAPN#######LOGIN###SENHA##### |
| JC400AD | APN,NOME_APN,,,,LOGIN,,SENHA,,,IPv4,,IPv4 |
| JC181 | APN,APN,,LOGIN,,SENHA |

3. Comandos de SERVER por modelo e firmware

| Modelo | Comando de SERVER |
| --- | --- |
| JC450 | SERVER,1,othub.jmbrasil.com.br,21122,NA,NA,NA |
| JC400 FW BBSA ou FOBA | SERVER,666666,1,othub.jmbrasil.com.br,21100 |
| JC400 FW WABA | SERVER,1,othub.jmbrasil.com.br,21100 |
| JC400AD | SERVER,1,othub.jmbrasil.com.br,21100 |
| JC181 | SERVER,1,othub.jmbrasil.com.br,21122 |

##### Recomendações Finais

- Sempre confirme o modelo e firmware antes de aplicar comandos.

- Em caso de dúvidas, consulte o responsável técnico ou o time de suporte.

- Verifique se o equipamento respondeu ao comando enviado.

#### O equipamento ainda não está comunicando?

Se, após envio de comandos (APN ou SERVER), o equipamento ainda não comunicar, siga os testes abaixo:

##### Testes recomendados

1. Verificar sinal e status de conexão:

- Espere o equipamento entrar em área de cobertura de sinal.

- Envie o comando STATUS
.

- Verifique:

- Tipo de conexão (ex: 4G).

- Se está conectado via rede móvel ou Wi-Fi.

1. Trocar o chip e testar novamente:

- Troque o chip SIM por outro funcional.

- Se o equipamento estiver em bancada, envie o comando RESTORE
.

- Repita o passo a passo de configuração.

1. Atualizar firmware do equipamento:

- Atualize o firmware para uma versão mais recente.

- Se o equipamento foi trocado de BBSA/FOBA para WABA, é essencial que ele esteja em bancada para essa atualização.

1. Limpar configurações salvas via VYSOR:

- Utilize o VYSOR para deletar APNs salvas no equipamento.

- Consulte o artigo “[Como utilizar o VYSOR corretamente]” na wiki para mais detalhes.

##### Encaminhamento para manutenção

> Se, após todos os testes acima, o equipamento continuar sem comunicar, encaminhe para manutenção.

## Equipamento não gera eventos

##### 1. Verificações Iniciais

- Verifique a instalação do equipamento: posição, ligação correta e se está funcionando.

- Faça o apontamento para a plataforma desejada.

- Verifique se o equipamento está comunicando.

##### 2. Ativação do Evento

- Ative o evento específico (consulte a WIKI para comandos conforme modelo e firmware).

- Ative o upload de mídia (se o modelo suportar; veja os comandos na WIKI).

##### 3. Upload e Testes

Se o evento ainda não for disparado:

- Enviar comando de UPLOAD para a plataforma:

| Modelo | Comando de UPLOAD |
| --- | --- |
| JC450 | SERVER,1,othub.jmbrasil.com.br,21122,NA,NA,NA |
| JC400 FW BBSA ou FOBA | UPLOAD,dsmspeed,13.94.231.209/upload |
| JC400 FW WABA | UPLOAD,http://13.94.231.209:21019/upload |
| JC400AD | UPLOAD,http://13.94.231.209:21019/upload |
| JC181 | SERVER,1,othub.jmbrasil.com.br,21122,UTILTY,URL |

##### 4. Evento ainda não gerado?

Caso o evento ainda não apareça, tente o seguinte:

| Ação | Situação indicada |
| --- | --- |
| Reenvie comando de UPLOAD com IP e PORTA corretos | Apontamento incorreto |
| Atualize o firmware do equipamento | Incompatibilidade com a plataforma |
| Migre o equipamento para plataforma Foco na Via | Incompatibilidade com a plataforma atual |
| Encaminhe para manutenção | Problemas persistentes |

##### 5. Eventos DMS

Se o evento for de DMS (ex: velocidade), use os comandos:

| Modelo | Comando para teste de evento DMS |
| --- | --- |
| JC400 FW BBSA ou FOBA | DMS,VIRTUAL_SPEED=666666 |
| JC400 FW WABA | DMS,VIRTUAL_SPEED=60 |
| JC400AD | DMS,VIRTUAL_SPEED=60 |
| JC450 | DMS,V=60 |

Velocidade padrão para gerar evento:

- JC400 e 15KM/h

- JC450 e 30KM/h

## Equipamento não gera playback

##### 1. Verifique o apontamento

- O equipamento está apontado para a Foco na Via?

- Se NÃO:

- Verifique a conectividade e se há cartão SD de no mínimo 16GB inserido.

- Faça os apontamentos corretos para a sua plataforma.

- Se SIM:

- Verifique se o equipamento está dentro do prazo de armazenamento configurado.

##### 2. Verifique a instalação

- O equipamento está instalado corretamente e ligado?

- Se SIM:

- Faça o teste tentando gerar o evento de playback (ex: ignição).

- Se NÃO:

- Verifique a instalação elétrica.

- Valide o funcionamento e a conexão do equipamento.

##### 3. Playback foi registrado?

- Se NÃO:

- O equipamento está em bancada?

- Se SIM:

- Envie o comando RESTORE
.

- Refaça os comandos de apontamento.

- Utilize:

- TECLADO_MINIINFO
(modelo JC450)

- CAMERA_LIST
(modelo JC181)

- Se NÃO:

- Faça os seguintes testes, se possível:

| Teste | Objetivo |
| --- | --- |
| Enviar novo comando deUPLOADcom a URL correta da plataforma | Verificar apontamento correto |
| Atualizar o firmware para versão mais recente | Garantir compatibilidade |
| Conectar o equipamento a uma rede Wi-Fi (com cartão SIM ou banda larga) | Melhorar conectividade |
| Migrar para Foco na Via 2.0 | Verificar problema de compatibilidade |

Se ainda assim falhar:

➤ Encaminhe o equipamento para manutenção.

4. Comandos de UPLOAD (para playback e mídia)

| Modelo | Comando UPLOAD |
| --- | --- |
| JC450 | SERVER,1,othub.jmbrasil.com.br,21122,NA,NA,NA |
| JC400 FW BBSA/FOBA | UPLOAD,666666,dsmpath,13.94.231.209:21019/upload |
| JC400 FW WABA | UPLOAD,http://13.94.231.209:21019/upload |
| JC400AD | UPLOAD,http://13.94.231.209:21019/upload |
| JC181 | SERVER,1,othub.jmbrasil.com.br,21122,URL,TYP,2 |

## Equipamento não gera streaming

##### 1. Equipamento em bancada ou instalado?

- Se em bancada:

➤ Ligue o equipamento.

➤ Insira um cartão SD de no mínimo 16GB.

- Se instalado:

➤ Verifique se o equipamento está ligado.

##### 2. Verifique a plataforma de destino

- Se for Foco na Via 2.0:

➤ Envie comandos de apontamento:

| Modelo | Comando de STREAMING |
| --- | --- |
| JC450 | SERVER,1,othub.jmbrasil.com.br,21122,NA,NA,NA |
| JC400 FW BBSA ou FOBA | !RSERVICE:8000006658,13.94.231.153:9136/live |
| JC400 FW WABA | !RSERVICE:13.94.231.153:9136/live |
| JC400AD | !RSERVICE:13.94.231.153:9136/live |
| JC181 | SERVER,1,othub.jmbrasil.com.br,21122 |

Atenção ao firmware:

- Para modelos JC400 FW BBSA ou FOBA: escolha entre BBSA ou FOBA_BBSA.

- Para JC400 FW WABA: selecione WABA_CINEMA.

- Se for outra plataforma:

➤ Envie os comandos de apontamento específicos dessa plataforma.

➤ Valide os dados cadastrados no painel.

##### 3. O equipamento está comunicando?

- Se NÃO:

➤ Verifique a comunicação e conexão do equipamento.

##### 4. Não é possível visualizar o streaming?

- Conecte o equipamento a uma rede Wi-Fi, se possível.

- Envie o comando !RSERVICE
com URL completa da plataforma (sem alterar IP e PORTA).

- Atualize o firmware para a versão mais recente e refaça as configurações.

##### 5. Encaminhamento para manutenção

> Se o problema persistir mesmo após todas as etapas acima, encaminhe o equipamento para manutenção.

## Exportar Relatórios

### Exportar Relatórios: Descrição

O módulo Exportar Relatórios da plataforma YUV permite visualizar, baixar e gerenciar relatórios gerados a partir dos dados de rastreamento e monitoramento.

Os relatórios podem ser exportados em dois formatos principais:

- PDF – Para visualização formal ou impressão

- Excel – Para análises e cruzamentos em planilhas

### Exportar Relatórios: Tela Principal

A tela principal exibe uma lista com todos os relatórios exportados e os seguintes campos:

| Campo | Descrição |
| --- | --- |
| Nome | Nome do relatório gerado (ex.: Relatório de Posições, Desatualizados) |
| Tipo | Formato do arquivo exportado: PDF ou Excel |
| Status | Estado da exportação (ex.: Concluído, Em processamento) |
| Data de Criação | Quando o relatório foi solicitado |
| Data de Atualização | Quando a geração foi finalizada |
| # (Download) | Botão para baixar o relatório exportado |

Também há um campo de busca rápida, que permite filtrar relatórios pelo nome.

### Exportar Relatórios: Atualização Automática

A tela possui um botão de Atualização Automática, que mantém a lista sincronizada em tempo real, sem a necessidade de atualizar manualmente a página.

### Exportar Relatórios: Observações Importantes

- Os relatórios gerados permanecem disponíveis para download até serem removidos ou expirarem.

- A geração pode demorar alguns minutos, dependendo da quantidade de dados processados.

- O formato do relatório (PDF ou Excel) é determinado de acordo com o tipo selecionado durante a solicitação.

- A filtragem por relatórios recentes agiliza o acesso a arquivos mais relevantes.

## Rastreamento

### Rastreamento: Descrição

O módulo de Rastreamento permite o monitoramento em tempo real de todos os ativos vinculados à operação — como veículos, equipamentos ou dispositivos rastreáveis.

É essencial para a gestão operacional, fornecendo visibilidade imediata da localização, status de funcionamento e comportamento de cada ativo.
Posição: Permite visualizar o histórico detalahdo de localização de um ativo, incluind ignição,velociadae,data/hora e endereço.Essencial para auditoria de trajetos, análise de comportamento e validação de paradas.
Comandos:O módulo Comandos permite a comunicação direta via TCP com os equipamentos da plataforma YUV, enviando instruções e recebendo respostas em tempo real.

### Rastreamento: Visão Geral de Conectividade

No topo da tela, é exibido um painel de status global com o total de dispositivos:

- Online – Dispositivos ativos e enviando dados

- Offline – Dispositivos desconectados ou inativos

Esse painel é fundamental para diagnosticar falhas de comunicação rapidamente e detectar comportamentos fora do esperado.

### Rastreamento: Mapa Interativo

O mapa central exibe a localização atual dos ativos com ícones e cores.

##### Modos de visualização disponíveis:

- Map – Visualização padrão com ruas e regiões

- Satellite – Imagens de satélite reais

- Street View – Visualização em primeira pessoa do local (quando disponível)

Ícones são agrupados ou individuais, dependendo do zoom e densidade de ativos por região.

### Rastreamento: Lista de Ativos

Localizada à esquerda da tela, a lista apresenta todos os ativos conectados com os seguintes dados:

- Nome / Identificador

- Status de conexão (Online ou Offline)

- Status da ignição (Ligada ou Desligada)

- IMEI do dispositivo

- Última comunicação (Heartbeat)

- Última localização com GPS

A lista pode ser rolada e filtrada por nome, placa ou grupo.

### Rastreamento: Informações Detalhadas do Ativo

Ao clicar em qualquer ativo na lista, um painel lateral é exibido com as informações completas:

- Status: Online ou Offline

- Ignition: Ligada / Desligada

- Identificador + IMEI

- Endereço completo baseado em geolocalização

- Coordenadas: Latitude e Longitude

- Rede: 2G / 3G / 4G

- Posições:acompanhamento em tempo real dos ativos.

- Comandos:comunicação direta com os equipamentos.

- Último Heartbeat

- Último GPS

- Link direto para visualização no Google Maps (incluindo Street View)

### Rastreamento: Funcionalidades

- Filtro por nome, cliente ou status

- Atualização automática da posição dos ativos

- Agrupamento de ativos por região geográfica

- Detecção de ativos com falhas ou status fora do normal

- Exibição individual com informações operacionais em tempo real

### Rastreamento: Boas Práticas

- Ativos offline há muito tempo devem ser verificados manualmente

- Ignition ligada fora do horário esperado pode indicar uso não autorizado

- Verificar sempre o campo último heartbeat para garantir que o dispositivo esteja ativo

### Rastreamento: Exemplo

| Identificador | Status | Ignition | Rede | Última Localização | Endereço |
| --- | --- | --- | --- | --- | --- |
| 00001R | Online | Ligada | 4G | 25/04/2025 13:34 | Rua 29 de Julho, Concórdia – SC |

## Relatórios

### Relatório: Posições - Descrição

Permite visualizar o histórico detalhado de localização de um ativo, incluindo ignição, velocidade, data/hora e endereço. Essencial para auditoria de trajetos, análise de comportamento e validação de paradas.

### Relatório: Posições - Filtros

- Ativo: escolha o dispositivo desejado

- Período: selecione o intervalo de datas

- Clique em "Gerar" para visualizar

- Também é possível clicar em "Ver posições" para abrir a rota no mapa interativo

### Relatório: Posições - Indicadores Visuais

| Indicador | Descrição |
| --- | --- |
| Tempo em viagem | Tempo com o veículo em movimento |
| Tempo parado | Ignition ligada, mas velocidade 0 |
| KM percorrido | Distância total registrada no período |

### Relatório: Posições - Gráfico de Velocidade

Gráfico temporal mostrando variações de velocidade — útil para detectar picos, paradas e padrões.

### Relatório: Posições - Tabela de Registros

| Campo | Exemplo |
| --- | --- |
| Identificador | TST-LL-3S |
| Endereço | Av. São João, 2405 |
| Ignição | Ligada / Desligada |
| Velocidade | km/h |
| Latitude / Longitude | Coordenadas exatas |
| Data/Hora | Data e hora do ponto |
| Ícone de mapa | Link para visualização direta |

### Relatório: Posições - Exportação

- Exportar Excel

- Exportar PDF

### Relatório: Posições - Aplicações

- Cruzar com alarmes ou ocorrências

- Identificar padrões de condução

- Provar paradas ou deslocamentos

### Relatório: Posições - Requisitos

- GPS deve estar ativo

- Intervalos maiores processam mais dados

### Relatório: Deslocamento - Descrição

Analisa trajetos realizados por um ativo em um período. Fornece início, fim, distância, eventos e alarmes.

### Relatório: Deslocamento - Filtros

- Ativo

- Período

- Clique em "Gerar"

### Relatório: Deslocamento - Tabela de Dados

| Campo | Descrição |
| --- | --- |
| Identificador | Código do ativo |
| Início | Data/hora de início |
| Local Início | Endereço/Coordenada |
| Fim | Data/hora de término |
| Local Fim | Endereço/Coordenada |
| Evento | Tipo que iniciou/encerrou |
| Duração | Tempo do deslocamento |
| Velocidade Máxima | Pico de velocidade |
| KM Percorrido | Distância total |
| Qtd. de Alarmes | Total de alertas |

### Relatório: Deslocamento - Aplicações

- Verificar tempo real de percurso

- Detectar desvios de rota

- Avaliar condução e riscos

- Investigar ocorrências

### Relatório: Deslocamento - Dicas

- Combine com relatórios de alarmes

- Útil para rotas urbanas com muitas paradas

### Relatório: Deslocamento - Observações

- Requer ignição ativa e variação de posição

- Sem movimentação = relatório vazio

### Relatório: Desatualizados - Descrição

Identifica ativos que deixaram de reportar dados — útil para controle da operação e validação de dispositivos.

### Relatório: Desatualizados - Resumo Gráfico

Distribuição percentual por tempo desde o último envio:

| Categoria | Significado |
| --- | --- |
| Últimas 24h | Dados atualizados |
| > 1 dia | Dados ausentes 24h+ |
| > 7 dias | Desatualização longa |
| > 30 dias | Longa inatividade |
| Nunca posicionaram | Dispositivos nunca reportaram GPS |

### Relatório: Desatualizados - Tabelas Detalhadas

| Campo | Descrição |
| --- | --- |
| Revendedor | Nome do integrador |
| Identificador | Código do ativo |
| IMEI | Número do dispositivo |
| Último GPS | Último dado enviado |
| Último Heartbeat | Última comunicação |

As tabelas são separadas por categorias e são expansíveis.

### Relatório: Desatualizados - Exportação

- PDF

- Excel

### Relatório: Desatualizados - Aplicações

- Diagnóstico de falhas ou chips

- Follow-up de manutenção

- Verificar uso correto dos dispositivos

- Monitorar inatividade por revenda

### Relatório: Desatualizados - Boas Práticas

- Verificar "nunca posicionados" após ativação

- Investigar inatividade > 7 dias

- Cruzar com ocorrências e comandos

### Relatório: Alarmes - Descrição

Apresenta eventos críticos dos sensores — como câmeras, acelerômetros, indicando riscos e condutas suspeitas.

### Relatório: Alarmes - Filtros

- Equipamentos

- Tipo de Alarme (ex: curva brusca, colisão)

- Período

### Relatório: Alarmes - Dados na Tabela

| Campo | Descrição |
| --- | --- |
| Identificador | Nome/código do ativo |
| IMEI | Identificação do dispositivo |
| Tipo de Alarme | Ex: Curva brusca |
| Data | Data/hora do evento |
| # (ações) | Link para vídeo/mapa/imagem |

### Relatório: Alarmes - Visualização

- Painel com vídeos (interno e externo), imagens (se disponíveis) e mapa interativo

### Relatório: Alarmes - Informações Técnicas

- Ativo

- IMEI

- Tipo de Alarme

- Data/Hora

- Coordenadas

### Relatório: Alarmes - Exportação

- PDF

- Excel

### Relatório: Alarmes - Tipos Comuns

- Curva brusca

- Risco de colisão

- Nenhum rosto detectado

- Olhos fechados

- Parada repentina

- Desconexão de câmera

- Excesso de velocidade

### Relatório: Alarmes - Aplicações

- Análise de conduta

- Investigação de acidentes

- Prevenção de risco

- Suporte a ações corretivas

### Relatório: Ocorrências - Descrição

Integra dados de alarmes com tratativas de risco. Ideal para controle, auditoria e resolução de eventos.

### Relatório: Ocorrências - Filtros

- Clientes

- Ativos

- Tipo de Alarme

- Status da Ocorrência (com/sem risco, pendente)

- Período

### Relatório: Ocorrências - Tabela

| Campo | Descrição |
| --- | --- |
| Cliente | Conta vinculada |
| Identificador | Código do ativo |
| Motorista | Nome (se cadastrado) |
| IMEI | Identificador do dispositivo |
| Último Alarme em | Data/hora |
| Alarme | Tipo do evento |
| Situação | Status (risco, pendente) |
| # (ações) | Detalhes, vídeo, mapa |

### Relatório: Ocorrências - Classificação

- Sem risco

- Com risco

- Aguardando tratativa

### Relatório: Ocorrências - Exportações

- PDF

- Excel

### Relatório: Ocorrências - Aplicações

- Gestão por cliente ou frota

- Histórico de eventos com status

- Apoio a compliance e segurança

- Monitoramento de tratativas

### Relatório: Ocorrências - Dica

Combine com módulos de Alarmes, Vídeos e Dashboard para ter um fluxo completo de detecção e resolução.

## Vídeos

### Vídeos: Ao Vivo - Descrição

O módulo Ao Vivo da plataforma YUV permite acompanhar, em tempo real, as câmeras embarcadas em ativos como veículos e equipamentos. Ideal para monitoramento de segurança, auditoria de operação e verificação visual imediata.

### Vídeos: Ao Vivo - Interface de Seleção

No topo do módulo é possível selecionar:

- Cliente – Empresa ou conta gerenciada

- Ativo – Dispositivo com câmera embarcada

Após a seleção, o vídeo é carregado automaticamente e é possível alternar entre as câmeras disponíveis.

### Vídeos: Ao Vivo - Modos de Visualização

#### Visualização Individual

- Exibe o vídeo de um ativo por vez

- Alterna entre câmeras IN (interna) e OUT (externa)

- Pode exibir ambas simultaneamente

#### Visualização Múltipla

- Permite abrir vários ativos ao mesmo tempo

- A tela se adapta (ex: 2x2, 3x3)

- Transmissão sincronizada, mesmo com clientes diferentes

- Experiência próxima de um sistema de CFTV profissional

### Vídeos: Ao Vivo - Detalhes Técnicos da Transmissão

Cada janela de vídeo exibe:

- Data e hora atual

- Coordenadas geográficas

- Velocidade do ativo

- Alternância IN/OUT

- Status Online/Offline

Botão de tela cheia disponível para qualquer câmera.

### Vídeos: Ao Vivo - Requisitos

Para funcionar corretamente:

- Ativo precisa estar Online

- Dispositivo deve suportar vídeo

- Câmeras devem estar ativas e instaladas

- Requer conexão estável com banda suficiente

### Vídeos: Ao Vivo - Recomendações de Uso

- Monitoramento em tempo real de frotas

- Identificação de ocorrências no trajeto

- Verificação visual de entregas ou coletas

- Controle visual em áreas de risco

- Supervisão simultânea de múltiplos veículos

### Vídeos: Playback - Descrição

O módulo Playback permite acessar vídeos gravados pelas câmeras dos ativos. Ideal para auditorias, investigações e validação de eventos passados.

### Vídeos: Playback - Interface

#### 1. Seleção de Equipamento

- Escolha o ativo desejado

- O sistema mostra status Online/Offline

- Modelo e IMEI são exibidos

#### 2. Seleção de Período

- Defina a data desejada

- Gravações disponíveis variam com a memória e configuração do equipamento

#### 3. Requisição

- Após definir equipamento e data, clique em “Requisitar” para carregar os vídeos disponíveis

### Vídeos: Playback - Linha do Tempo e Reprodução

Abaixo do player, é exibida uma linha do tempo interativa dividida por canal:

- Canal IN – Câmera interna (motorista)

- Canal OUT – Câmera externa (frente/traseira)

Os blocos representam trechos gravados. Clique em qualquer um para iniciar a reprodução.

### Vídeos: Playback - Funcionalidades

- Pausar, avançar ou retroceder

- Alternar canais (IN/OUT) ou assistir ambos

- Ver timestamp, velocidade e coordenadas

- Modo tela cheia

- Captura de imagens via sistema operacional

### Vídeos: Playback - Requisitos Técnicos

- Dispositivo precisa ter armazenamento (interno ou SD)

- Deve ter estado ativo durante a gravação

- Requer rede disponível para carregar os trechos

### Vídeos: Playback - Boas Práticas

- Combine com relatórios de alarmes para encontrar eventos rapidamente

- Use canal IN para analisar condutores

- Use canal OUT para visualizar ocorrências externas

### Vídeos: Playback - Observações

- Gravações organizadas cronologicamente

- Blocos maiores indicam gravações mais longas

- Equipamentos podem sobrescrever vídeos antigos conforme a capacidade

### Vídeos: Downloads - Descrição

O módulo Downloads permite acessar vídeos requisitados via Playback, com opções para visualizar online, fazer download ou excluir.

### Vídeos: Downloads - Tabela de Arquivos

| Campo | Descrição |
| --- | --- |
| Nome | Data/hora da gravação (timestamp) |
| Identificador | Nome do ativo |
| Equipamento | IMEI do dispositivo |
| Canal | Câmera (IN, OUT, Canal 1, etc.) |
| Requisitado em | Data/hora da solicitação |
| Status | Processando / Disponível / Expirado |

### Vídeos: Downloads - Ciclo de Status

1. Processando: sistema preparando o arquivo

1. Disponível: pronto para visualização/download

1. Expirado: tempo de acesso expirado — necessário requisitar novamente

> A maioria dos vídeos processa em segundos.

### Vídeos: Downloads - Ações Disponíveis

Menu lateral (ícone de três barras) permite:

- Visualizar online

- Fazer download (.ts)

- Excluir da lista

### Vídeos: Downloads - Pesquisa e Filtros

- Filtro por Status (Processando, Disponível, Expirado)

- Busca por nome, canal, identificador ou IMEI

### Vídeos: Downloads - Observações Técnicas

- Tempo de expiração depende da configuração do servidor (minutos ou horas)

### Vídeos: Downloads - Recomendações

- Baixe vídeos assim que disponíveis

- Não repita solicitações em sequência

- Renomeie arquivos salvos para facilitar identificação

## Visão Geral da Plataforma

### Plataforma: Descrição Geral

A plataforma YUV oferece uma solução completa para o rastreamento, monitoramento de ativos e gestão de frotas.

Todos os módulos foram projetados para serem intuitivos, eficientes e centralizarem informações críticas para tomada de decisão.

### Plataforma: Módulos Principais

| Módulo | Descrição |
| --- | --- |
| Rastreamento | Visualização em tempo real da localização dos ativos com informações de status de conexão, movimento e eventos. |
| BI (Business Intelligence) | Painéis analíticos personalizados para acompanhar indicadores de desempenho, alarmes e métricas operacionais. |
| Dashboard | Resumo das principais informações de ativos, alarmes e status de conectividade de forma visual. |
| Vídeos | Acesso a vídeos gravados de eventos ou requisição manual diretamente das câmeras instaladas nos veículos. |
| Relatórios | Geração de relatórios detalhados sobre posições, deslocamentos, alarmes, desatualizações e mais. |
| Cadastros | Gerenciamento de Ativos, Chips, Clientes, Equipamentos, Motoristas, Grupos de Permissões,Face ID,Checklist Motorista e Configurações de Ocorrências. |
| Comandos | Envio de comandos remotos para equipamentos como atualização de configurações, reboot ou coleta de informações. |
| Exportar Relatórios | Área para download dos relatórios já gerados no sistema, com atualização automática. |

### Plataforma: Funcionalidades

Principais funcionalidades oferecidas pela plataforma YUV:

- Visualização em tempo real de ativos e eventos

- Gestão de alarmes com classificação automática

- Cadastro e gerenciamento de usuários, motoristas e clientes

- Exportação de dados em formatos PDF e Excel

- Envio de comandos remotos para equipamentos

- Controle de permissões para acesso restrito a informações específicas

### Plataforma: Boas Práticas

Recomendações para o uso eficiente da plataforma YUV:

- Manter clientes e ativos atualizados para garantir relatórios precisos

- Utilizar grupos de permissão para controlar acessos de usuários

- Realizar downloads periódicos de relatórios para auditorias internas

- Monitorar alarmes e eventos críticos em tempo real para respostas rápidas
