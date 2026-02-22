# SIRA - Sistema Interno de Ramais e Anotações

- **Autor:** Edilberto Fonseca <edilberto.fonseca@outlook.com>
- **Licença:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)
- **Versão:** 2025.3.1

---

## Descrição

**SIRA** (_Sistema Interno de Ramais e Anotações_) é um complemento para o NVDA desenvolvido para aprimorar a comunicação interna e o registro de informações dentro da Secretaria de Saúde.

Com foco em acessibilidade e eficiência, o SIRA permite:

- Cadastrar e consultar ramais telefônicos de todos os setores;
- Registrar recados destinados ao setor de transporte;
- Anotar altas médicas para controle e acompanhamento;
- Gerenciar recados gerais e mensagens internas de forma centralizada.

A interface é totalmente compatível com leitores de tela como o **NVDA**, garantindo uma experiência fluida e inclusiva para usuários com deficiência visual.

Ideal para uso diário em ambientes públicos e administrativos, o **SIRA** contribui para uma gestão da informação mais ágil, precisa e organizada.

---

## Tecnologias utilizadas

- Linguagem: Python
- Estrutura: API de complementos do NVDA
- Armazenamento: Arquivos locais (JSON, TXT ou CSV, conforme o tipo de dado)

---

## Instalação

1. No NVDA, abra o menu **Ferramentas** e selecione **Loja de Complementos**.
2. Na aba **Complementos Disponíveis**, vá até o campo **Pesquisar**.
3. Digite "SIRA" e pressione **Enter**.
4. Selecione o complemento e clique em **Instalar**.
5. Após a instalação, reinicie o NVDA para concluir o processo.

---

## Estrutura de dados

O SIRA organiza os dados de forma simples e acessível, permitindo fácil exportação, importação e manutenção dos registros.

Os dados são armazenados localmente em arquivos nos formatos **JSON**, **TXT** ou **CSV**, dependendo do módulo correspondente.

Ao selecionar um item na lista de contatos ou registros, as informações são exibidas em um campo de visualização, facilitando a leitura e a cópia com comandos do NVDA.

---

## Comandos e Atalhos

| Ação                                                                                | Atalho                    |
| ----------------------------------------------------------------------------------- | ------------------------- |
| Exibe uma janela com todos os contatos cadastrados no Sistema de Cadastro de Ramais | Alt+1 do teclado numérico |
| Registro de mensagens para o departamento de transporte                             | Alt+2 do teclado numérico |
| Registro de alta hospitalar                                                         | Alt+3 do teclado numérico |
| Permite o registro de mensagens para todos os departamentos                         | Alt+4 do teclado numérico |

> Os atalhos podem ser personalizados no menu **Gestos de Entrada** do NVDA.

---

## Contribuições

Contribuições são bem-vindas!

Para sugerir melhorias, relatar problemas ou colaborar com o desenvolvimento, entre em contato por e-mail ou abra uma issue na página pública do projeto (caso disponível).
