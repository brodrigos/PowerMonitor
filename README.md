# PowerMonitor Pro - Monitoramento de Energia

Uma aplicação completa para monitorar o consumo de energia do seu computador em tempo real.

## Funcionalidades

- Monitoramento em tempo real de CPU, GPU, RAM e consumo de energia
- Interface gráfica moderna com Tkinter
- Identificação de processos mais intensivos em recursos
- Sistema de alertas para consumo excessivo
- Relatórios detalhados com estatísticas
- Exportação de dados em CSV e Excel

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
python main.py
```

## Estrutura do Projeto

```
PowerMonitor/
├── main.py              # Ponto de entrada principal
├── requirements.txt     # Dependências
├── README.md           # Documentação
├── modules/            # Módulos principais
│   ├── power_monitor.py     # Monitoramento de energia
│   ├── alert_system.py      # Sistema de alertas
│   └── data_exporter.py     # Exportação de dados
├── ui/                 # Interface gráfica
│   └── main.py              # Interface principal
├── data/               # Dados salvos
└── logs/               # Logs da aplicação
```

## Uso

- **Iniciar/Parar**: Botões para controlar o monitoramento
- **Exportar**: Salve dados em CSV para análise posterior
- **Alertas**: Configure limites para notificações
- **Configurações**: Ajuste intervalo de amostragem e outros parâmetros

## Requisitos

- Python 3.8+
- Windows 10/11
- Dependências listadas em requirements.txt

## Licença

Este projeto está sob a licença MIT.
