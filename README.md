# TRY:PASS

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/-Pygame-000000?style=for-the-badge&logo=python&logoColor=white)

TRY:PASS é um jogo de lógica e programação desenvolvido em Python utilizando a biblioteca Pygame. O objetivo é guiar o personagem através de desafios em um mapa top-down, utilizando a montagem de sequências de blocos de comando, como movimentos básicos e estruturas de repetição.

### 🎮 O Conceito

O jogo desafia o pensamento algorítmico do jogador. Ao invés de usar as setas do teclado para mover o herói, deves "programar" o seu percurso:
1. Fase de Codificação: Selecionas e organizas blocos de ação (Andar, Virar, Repetir).
2. Fase de Execução: O personagem percorre o caminho seguindo estritamente as instruções fornecidas, testando a validade da lógica implementada.

### 🏗️ Arquitetura e Engenharia de Software

O projeto foi construído com foco em escalabilidade e manutenção, utilizando padrões de design de software de nível profissional:

#### 1. Padrão MVC (Model-View-Controller)

A separação clara de responsabilidades permite que o jogo seja robusto:
- Model: Gere o estado interno (posição do jogador em pixels, mapa de tiles, fila de comandos e lógica de colisão). É independente da interface gráfica.
- View: Responsável por toda a renderização. Inclui um sistema de painéis modulares e uma Câmera Dinâmica com suavização (Lerp) e limites de mapa (Clamping).
- Controller: Gere o ciclo de vida do jogo, captura eventos de input (Rato/Teclado) e coordena o sistema de Drag and Drop da interface.

#### 2. Padrões de Design Aplicados
- Command Pattern: Cada instrução (Andar, Virar Esquerda, Virar Direita) é um objeto independente. Isto permitiu a criação fácil do bloco Repeat (FOR), que contém uma lista recursiva de outros comandos.
- Game State Machine: Controlo rigoroso entre os estados de edição e execução para evitar comportamentos inesperados.

### 🛠️ Funcionalidades Implementadas
- Câmera Top-Down: Segue o jogador suavemente e respeita os limites do cenário.
- Sistema de Comandos: Suporte para ações básicas e estruturas de repetição aninhadas.
- Interface Modular: Painéis de inventário, ferramentas, mapa e barra de execução.
- Drag and Drop Dinâmico: Reordenação visual de blocos na fila de execução com feedback em tempo real.
- Fundo Transparente: Efeito visual de overlay para menus e inventário.

### 🚀 Como Executar

#### Pré-requisitos
- Python 3.10 ou superior.
- Pygame CE (ou Pygame standard).

#### Instalação

1. Clone o repositório:

```bash
  git clone https://github.com/ItaloKaua288/TRY-PASS-IHM.git
```
2. Instale a biblioteca necessária:
```bash
  pip install -r requirements.txt
```
3. Inicie o jogo:
```bash
  python main.py
```
