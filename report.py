import pyodbc
from fpdf import FPDF

def get_user_data(user_id):
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=10.30.64.44;'
        'DATABASE=teste_rafael;'
        'UID=rafael_teste;'
        'PWD=rafael_teste123!'
    )
    cursor = conn.cursor()

    cursor.execute('EXEC GetRespostasPorUtilizador ?', user_id)
    rows = cursor.fetchall()

    cursor.execute('''
        SELECT u.nome_colaborador, u.numero_colaborador, l.nome_linha
        FROM Utilizadores u
        JOIN TrabalhadorLinha tl ON u.id = tl.id_trabalhador
        JOIN Linhas l ON tl.id_linha = l.id
        WHERE u.id = ?
    ''', user_id)
    user_info = cursor.fetchone()

    conn.close()
    return user_info, rows

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Check List de Avaliação Prática Nível B-C1', 0, 1, 'C')
        self.set_font('Arial', 'B', 10)
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln(1)

    def add_question(self, question, response):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, question, 0, 0, 'L')
        self.cell(-50)
        self.cell(50, 10, str(response), 0, 1, 'R')

    def footer(self):
        self.set_y(-28)
        self.set_font('Arial', 'B', 13)
        self.cell(0, 15, 'DT.18.1.4.2', 0, 1)
        self.image('logo.png', x=130, y=self.get_y() - 12, w=60)

    def add_user_info_table(self, user_info):
        self.set_text_color(0, 0, 0) 
        self.set_font('Arial', 'B', 10)

    
        self.cell(60, 10, 'Nome do Colaborador/a:', 1, 0, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, str(user_info.nome_colaborador), 1, 1, 'C')

        self.set_font('Arial', 'B', 10)
        self.cell(60, 10, 'Número do Colaborador/a:', 1, 0, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, str(user_info.numero_colaborador), 1, 1, 'C')

        self.set_font('Arial', 'B', 10)
        self.cell(60, 10, 'Linha:', 1, 0, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, str(user_info.nome_linha), 1, 1, 'C')

    def add_legend(self):
        self.set_font('Arial', 'I', 10)
        self.ln(5)
        self.multi_cell(0, 0, 'Escala de Avaliação: 1 (Demonstra) / 2 (Demonstra sem dificuldade) / 3 (Demonstra claramente)', 0)

    def add_observations_and_signature(self):
        self.set_y(-80)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, 'Observações:\n______________________________________________________________________________________________\n')
        self.ln(5)
        self.cell(0, 10, 'Data da Avaliação: ____/____/____     Assinatura do Responsável: ________________', 0, 1)

def create_pdf(user_info, responses):
    pdf = PDF()
    pdf.add_page()

    pdf.add_user_info_table(user_info)

    pdf.chapter_body(
        "A Avaliação prática de Nível B-C tem como principal objetivo verificar a transferência dos saberes adquiridos, pela via da formação prática, para os respetivos contextos de trabalho. "
        "Ao avaliar positivamente o/a colaborador/a neste processo, está a assumir que o/a colaborador/a acima identificado/a está capacitado/a para desempenhar de forma autónoma as operações deste processo."
        "Devido à importância deste processo, é fundamental que sejas rigoroso/a no seu preenchimento."
        "\nO/A colaborador/a:"
    )
    
    for row in responses:
        question = row.Pergunta
        response = row.OpcaoID
        pdf.add_question(question, response)
    
    pdf.add_legend()
    pdf.add_observations_and_signature()

    pdf.output('avaliacao_pratica.pdf')

if __name__ == '__main__':
    user_id = 1 
    user_info, responses = get_user_data(user_id)

    create_pdf(user_info, responses)
