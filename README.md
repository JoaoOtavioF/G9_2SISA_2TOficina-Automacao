# 📌 Sistema de Agendamento e Gestão para Oficinas de Moto

## 📖 Sobre o Projeto

Este projeto tem como objetivo otimizar a gestão de uma oficina de motos por meio da digitalização do processo de agendamento de serviços. Com um sistema eficiente e automatizado, buscamos reduzir o tempo de espera dos clientes, melhorar a organização da oficina e aumentar a produtividade da equipe. O sistema se alinha aos Objetivos de Desenvolvimento Sustentável (ODS), especialmente ao **ODS 8**, que promove o crescimento econômico sustentável e o emprego decente.

## 🚀 Funcionalidades Principais

- ✅ Agendamento online de serviços
- ✅ Gestão de clientes e histórico de atendimentos
- ✅ Notificações automáticas para lembretes de serviço
- ✅ Relatórios e indicadores de desempenho (KPIs)

## 📄 Licença

Este projeto está sob a licença **MIT**. Sinta-se livre para usá-lo e modificá-lo conforme necessário.

---

## API de Verificação por Email

Adicionei um endpoint simples para enviar códigos de verificação por email.

- Para instalar dependências:

```powershell
python -m pip install -r requirements.txt
```

- Para executar o servidor (modo API):

```powershell
python Automação.py serve
```

- Exemplo de requisição (PowerShell):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/send-verification \
  -Body (ConvertTo-Json @{ email='destino@exemplo.com'; code='123456'; name='João' }) \
  -ContentType 'application/json'
```

Observações:

- O script utiliza as configurações dentro da classe `ConfigEmail` em `Automação.py`. Para produção, mova as credenciais para variáveis de ambiente ou um arquivo `.env` e não mantenha senhas em código fonte.
- O endpoint espera um JSON com `email` e `code`.

---

Desenvolvido para otimizar a gestão de oficinas de motos e proporcionar um serviço mais eficiente e ágil para os clientes!
# 📌 Sistema de Agendamento e Gestão para Oficinas de Moto

## 📖 Sobre o Projeto

Este projeto tem como objetivo otimizar a gestão de uma oficina de motos por meio da digitalização do processo de agendamento de serviços. Com um sistema eficiente e automatizado, buscamos reduzir o tempo de espera dos clientes, melhorar a organização da oficina e aumentar a produtividade da equipe. O sistema se alinha aos Objetivos de Desenvolvimento Sustentável (ODS), especialmente ao **ODS 8**, que promove o crescimento econômico sustentável e o emprego decente.

## 🚀 Funcionalidades Principais

✅ Agendamento online de serviços
✅ Gestão de clientes e histórico de atendimentos
✅ Notificações automáticas para lembretes de serviço
✅ Relatórios e indicadores de desempenho (KPIs)

## 📄 Licença

Este projeto está sob a licença **MIT**. Sinta-se livre para usá-lo e modificá-lo conforme necessário.

---

🚀 Desenvolvido para otimizar a gestão de oficinas de motos e proporcionar um serviço mais eficiente e ágil para os clientes!
