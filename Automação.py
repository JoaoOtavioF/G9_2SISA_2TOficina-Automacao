import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import mysql.connector
from typing import List, Dict


class ConfigBancoDados:
    """Configurações de conexão com MySQL"""
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "3974Jo17@"  # Sua senha do MySQL
        self.database = "2t_oficina"
        self.port = 3306


class ConfigEmail:
    """Configurações de email"""
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_remetente = "2toficinasptech@gmail.com"
        self.senha = "spgdqpqqiwtezvnb"  # Senha de app sem espaços
        self.nome_oficina = "2T Oficina"


class GerenciadorBancoDados:
    """Gerencia conexões e consultas ao banco de dados MySQL"""
    
    def __init__(self, config: ConfigBancoDados):
        self.config = config
    
    def _conectar(self):
        """Cria uma conexão com o banco de dados"""
        return mysql.connector.connect(
            host=self.config.host,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            port=self.config.port
        )
    
    def buscar_agendamentos_proximos(self) -> List[Dict]:
        """
        Busca agendamentos nas próximas 24 horas com status 'Pendente'
        e retorna dados completos do cliente e serviços
        """
        agora = datetime.now()
        limite = agora + timedelta(hours=24)
        
        query = """
        SELECT 
            a.id as id_agendamento,
            a.data as data_agendamento,
            a.hora as hora_agendamento,
            a.veiculo,
            a.descricao,
            a.hora_retirada,
            u.id as id_usuario,
            u.nome,
            u.sobrenome,
            u.email,
            u.telefone,
            sa.status,
            GROUP_CONCAT(s.nome SEPARATOR ', ') as servicos
        FROM agendamento a
        INNER JOIN usuario u ON a.fk_usuario = u.id
        INNER JOIN status_agendamento sa ON a.fk_status_agendamento = sa.id
        LEFT JOIN servico_agendado sag ON sag.fk_agendamento = a.id
        LEFT JOIN servico s ON s.id = sag.fk_servico
        WHERE CONCAT(a.data, ' ', a.hora) BETWEEN %s AND %s
        AND sa.status = 'Pendente'
        GROUP BY 
            a.id, a.data, a.hora, a.veiculo, a.descricao, 
            a.hora_retirada, u.id, u.nome, u.sobrenome, 
            u.email, u.telefone, sa.status
        ORDER BY a.data, a.hora
        """
        
        try:
            conn = self._conectar()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(query, (
                agora.strftime("%Y-%m-%d %H:%M:%S"),
                limite.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return resultados
            
        except mysql.connector.Error as e:
            print(f"Erro ao consultar banco de dados: {e}")
            return []
    
    def adicionar_coluna_lembrete(self):
        """
        Adiciona coluna 'lembrete_enviado' na tabela agendamento se não existir
        Execute este método apenas uma vez para preparar o banco
        """
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            cursor.execute("""
                ALTER TABLE agendamento 
                ADD COLUMN IF NOT EXISTS lembrete_enviado TINYINT DEFAULT 0
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✓ Coluna 'lembrete_enviado' verificada/criada com sucesso")
            
        except mysql.connector.Error as e:
            print(f"Aviso ao adicionar coluna: {e}")
    
    def marcar_lembrete_enviado(self, id_agendamento: int):
        """Marca um agendamento como já tendo recebido lembrete"""
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE agendamento 
                SET lembrete_enviado = 1 
                WHERE id = %s
            """, (id_agendamento,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as e:
            print(f"Erro ao marcar lembrete como enviado: {e}")


class EnviadorEmail:
    """Responsável por enviar emails de lembrete"""
    
    def __init__(self, config: ConfigEmail):
        self.config = config
    
    def criar_mensagem_html(self, agendamento: Dict) -> str:
        """Cria o corpo HTML do email de lembrete personalizado para a oficina"""
        
        # Formatar data e hora
        if isinstance(agendamento['data_agendamento'], str):
            data_obj = datetime.strptime(agendamento['data_agendamento'], "%Y-%m-%d")
        else:
            data_obj = agendamento['data_agendamento']
        
        if isinstance(agendamento['hora_agendamento'], str):
            hora_str = agendamento['hora_agendamento']
        else:
            hora_str = str(agendamento['hora_agendamento'])
        
        data_formatada = data_obj.strftime("%d/%m/%Y")
        dia_semana = data_obj.strftime("%A")
        
        # Traduzir dia da semana
        dias_pt = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        dia_semana_pt = dias_pt.get(dia_semana, dia_semana)
        
        nome_completo = f"{agendamento['nome']} {agendamento['sobrenome']}"
        servicos = agendamento['servicos'] if agendamento['servicos'] else "Não especificado"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            🏍️ {self.config.nome_oficina}
                        </h1>
                        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">
                            Lembrete de Agendamento
                        </p>
                    </div>
                    
                    <div style="background-color: #ffffff; padding: 30px; border: 1px solid #e0e0e0; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; margin-bottom: 20px;">
                            Olá <strong>{nome_completo}</strong>,
                        </p>
                        
                        <p style="font-size: 15px;">
                            Este é um lembrete automático sobre seu agendamento na nossa oficina:
                        </p>
                        
                        <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                                    padding: 25px; border-radius: 8px; margin: 25px 0;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #555;">
                                        📅 Data:
                                    </td>
                                    <td style="padding: 8px 0; color: #333;">
                                        {dia_semana_pt}, {data_formatada}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #555;">
                                        ⏰ Horário:
                                    </td>
                                    <td style="padding: 8px 0; color: #333;">
                                        {hora_str}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #555;">
                                        🏍️ Veículo:
                                    </td>
                                    <td style="padding: 8px 0; color: #333;">
                                        {agendamento['veiculo']}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #555; vertical-align: top;">
                                        🔧 Serviços:
                                    </td>
                                    <td style="padding: 8px 0; color: #333;">
                                        {servicos}
                                    </td>
                                </tr>
        """
        
        if agendamento.get('hora_retirada'):
            html += f"""
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #555;">
                                        🕐 Retirada prevista:
                                    </td>
                                    <td style="padding: 8px 0; color: #333;">
                                        {agendamento['hora_retirada']}
                                    </td>
                                </tr>
            """
        
        html += f"""
                            </table>
                        </div>
                        
                        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; 
                                    padding: 15px; margin: 20px 0; border-radius: 4px;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                <strong>⚠️ Importante:</strong> Por favor, chegue com 10 minutos de antecedência.
                            </p>
                        </div>
                        
                        <p style="font-size: 15px; margin-top: 25px;">
                            <strong>Descrição:</strong><br>
                            {agendamento['descricao']}
                        </p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #f0f0f0;">
                            <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                                Caso precise cancelar ou reagendar, entre em contato:
                            </p>
                            <p style="font-size: 14px; color: #667eea; margin: 5px 0;">
                                📞 Telefone: (11) 98861-9917
                            </p>
                            <p style="font-size: 14px; color: #667eea; margin: 5px 0;">
                                ✉️ Email: {self.config.email_remetente}
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="font-size: 16px; color: #333; margin: 0;">
                                Aguardamos você! 🚀
                            </p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; padding: 15px;">
                        <p style="color: #999; font-size: 12px; margin: 5px 0;">
                            Este é um email automático, por favor não responda.
                        </p>
                        <p style="color: #999; font-size: 12px; margin: 5px 0;">
                            © 2025 {self.config.nome_oficina} - Todos os direitos reservados
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        return html
    
    def enviar_lembrete(self, agendamento: Dict) -> bool:
        """Envia email de lembrete para um agendamento"""
        try:
            mensagem = MIMEMultipart("alternative")
            mensagem["Subject"] = f"🏍️ Lembrete: Agendamento na {self.config.nome_oficina}"
            mensagem["From"] = f"{self.config.nome_oficina} <{self.config.email_remetente}>"
            mensagem["To"] = agendamento['email']
            
            corpo_html = self.criar_mensagem_html(agendamento)
            parte_html = MIMEText(corpo_html, "html", "utf-8")
            mensagem.attach(parte_html)
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_remetente, self.config.senha)
                server.send_message(mensagem)
            
            nome_completo = f"{agendamento['nome']} {agendamento['sobrenome']}"
            print(f"✓ Email enviado para {nome_completo} ({agendamento['email']})")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao enviar email para {agendamento['email']}: {str(e)}")
            return False


class AutomacaoLembretes:
    """Classe principal que orquestra o processo de lembretes"""
    
    def __init__(self):
        self.config_db = ConfigBancoDados()
        self.config_email = ConfigEmail()
        self.db = GerenciadorBancoDados(self.config_db)
        self.enviador = EnviadorEmail(self.config_email)
    
    def preparar_banco(self):
        """Prepara o banco adicionando a coluna de controle se necessário"""
        print("Verificando estrutura do banco de dados...")
        self.db.adicionar_coluna_lembrete()
    
    def executar(self):
        """Executa o processo completo de verificação e envio de lembretes"""
        print("\n" + "="*70)
        print("🏍️  SISTEMA DE LEMBRETES AUTOMÁTICOS - 2T OFICINA")
        print("="*70)
        print(f"⏰ Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*70 + "\n")
        
        print("🔍 Buscando agendamentos nas próximas 24 horas...")
        agendamentos = self.db.buscar_agendamentos_proximos()
        
        if not agendamentos:
            print("✓ Nenhum agendamento pendente encontrado nas próximas 24 horas.\n")
            return
        
        print(f"📋 Encontrados {len(agendamentos)} agendamento(s) para notificar:\n")
        
        enviados = 0
        falhas = 0
        
        for i, agendamento in enumerate(agendamentos, 1):
            nome_completo = f"{agendamento['nome']} {agendamento['sobrenome']}"
            data_hora = f"{agendamento['data_agendamento']} {agendamento['hora_agendamento']}"
            
            print(f"[{i}/{len(agendamentos)}] Processando agendamento #{agendamento['id_agendamento']}")
            print(f"    👤 Cliente: {nome_completo}")
            print(f"    📅 Data/Hora: {data_hora}")
            print(f"    🏍️  Veículo: {agendamento['veiculo']}")
            
            if self.enviador.enviar_lembrete(agendamento):
                self.db.marcar_lembrete_enviado(agendamento['id_agendamento'])
                enviados += 1
            else:
                falhas += 1
            
            print()
        
        print("="*70)
        print(f"✅ PROCESSO FINALIZADO")
        print(f"   • Emails enviados: {enviados}")
        print(f"   • Falhas: {falhas}")
        print(f"   • Total processado: {len(agendamentos)}")
        print("="*70 + "\n")


def main():
    """Função principal"""
    automacao = AutomacaoLembretes()
    
    # Executar apenas uma vez para preparar o banco
    # automacao.preparar_banco()
    
    # Executar o envio de lembretes
    automacao.executar()


if __name__ == "__main__":
    main()
