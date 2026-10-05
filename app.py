"""
Preciso automatizar o envio de mensagens para alunos faltosos
"""
#Descrever os passos manuais e descrever isso em código
import xlrd
from urllib.parse import quote
import webbrowser
from time import sleep
from datetime import datetime, date
from phonenumbers import PhoneNumberFormat, parse as phone_parse, format_number as phone_format
from phonenumbers.phonenumberutil import NumberParseException
import pyautogui
import os
import csv

def normalizar_telefone(valor):
    try:
        if isinstance(valor, float):
            valor = str(int(valor))
        else:
            valor = str(valor)
        numero = phone_parse(valor, 'BR')
        return phone_format(numero, PhoneNumberFormat.E164)
    except NumberParseException:
        print("Numero não cadastrado")
        return None

def msg_contato(nome, telefone_aluno, telefone_responsavel):
    telefone_aluno = normalizar_telefone(telefone_aluno)

    if telefone_aluno:
        mensagem = (
            f'Olá {nome}, tudo bem? '
            'Sentimos sua falta na aula de hoje. Houve algum imprevisto?'
        )
        return telefone_aluno, mensagem, 'Aluno'

    telefone_responsavel = normalizar_telefone(telefone_responsavel)

    if telefone_responsavel:
        mensagem = (
            'Olá! Tudo bem? '
            f'Sentimos falta do {nome} na aula de hoje. Houve algum imprevisto?'
        )
        return telefone_responsavel, mensagem, 'Responsavel'

    return None, None, None

def reset_arquivo(caminho_arquivo):
    timestamp = os.path.getmtime(caminho_arquivo)
    dt_modificacao = datetime.fromtimestamp(timestamp).date()
    dt_hoje = date.today()

    if dt_modificacao < dt_hoje:
        open(caminho_arquivo, "w").close()
        print("Arquivo resetado!")
    else:
        print("O arquivo e de hoje. Nada foi apagado!")

def arq_existente(caminho_arquivo):
    return os.path.exists(caminho_arquivo)

def ja_enviados(nome, coluna_unica):
    return nome in coluna_unica

def enviar_mensagem_whatsapp(link_msg_whatsapp):
    """
    Abre o WhatsApp Web com a mensagem já preenchida, procura o botão de
    enviar na tela e clica nele. Retorna True se conseguiu enviar,
    False se não encontrou o botão (e portanto não enviou de verdade).
    """
    webbrowser.open(link_msg_whatsapp)
    sleep(45)

    try:
        print("Procurando a seta...")

        largura_tela, altura_tela = pyautogui.size()

        # Região aproximada: canto inferior direito da tela
        regiao_busca = (
            int(largura_tela * 0.7),   # começa em 70% da largura
            int(altura_tela * 0.7),    # começa em 70% da altura
            int(largura_tela * 0.3),   # largura da região
            int(altura_tela * 0.3)     # altura da região
        )

        seta = pyautogui.locateCenterOnScreen(
            'seta-wpp.PNG',
            confidence=0.8,
            grayscale=True,
            region=regiao_busca
        )

        sleep(5)
        pyautogui.click(seta)
        print("Seta encontrada!")
        sleep(5)
        pyautogui.hotkey('ctrl', 'w')
        sleep(5)
        return True

    except pyautogui.ImageNotFoundException:
        return False


#Ler planilha Faltas Hoje e guardar informacoes sobre nome e telefone
workbook = xlrd.open_workbook('alunos_exemplo.xls')
planilha = workbook.sheet_by_index(0)

headers = planilha.row_values(0)

caminho_enviados = 'enviados_hoje_alunos.csv'

if arq_existente(caminho_enviados):
    print("Arquivo existente!")
    reset_arquivo(caminho_enviados)
else:
    print("Arquivo nao existente!")
    with open(caminho_enviados, 'w', encoding='utf-8') as create_arquivo:
        pass  # só criar vazio, sem escrever nada

with open(caminho_enviados, 'r', encoding='utf-8') as read_arquivo:
    leitor = csv.reader(read_arquivo)
    coluna_unica = set(linha[0] for linha in leitor if linha)


for linha_idx in range(1, planilha.nrows):
    #nome, telefone_aluno, telefone_responsavel
    linha = planilha.row_values(linha_idx)
    dados = dict(zip(headers, linha))

    nome = dados.get('Nome Aluno')

    if ja_enviados(nome, coluna_unica):
        print(f"Mensagem já enviada ao aluno {nome}")
        continue

    telefone_aluno = dados.get('Telefone Aluno')
    telefone_responsavel = dados.get('Telefone Responsável')

    telefone_contato, mensagem, contato = msg_contato(nome, telefone_aluno, telefone_responsavel)

    # Nem aluno nem responsável têm telefone válido: pula ANTES de tentar montar link ou abrir navegador
    if contato is None:
        print(f"Pulando {nome}: telefone inválido ou ausente")
        continue

    # Chegou aqui, contato é 'Aluno' ou 'Responsavel' — pode montar o link com segurança
    if contato == 'Aluno':
        print(f"Enviando mensagem ao aluno {nome}...")
    elif contato == 'Responsavel':
        print(f"Enviando mensagem ao responsável do aluno {nome}...")

    link_msg_whatsapp = f'https://web.whatsapp.com/send?phone={telefone_contato}&text={quote(mensagem)}'

    enviado_com_sucesso = enviar_mensagem_whatsapp(link_msg_whatsapp)

    if enviado_com_sucesso:
        print(f"Mensagem enviada com sucesso para {nome} ({contato.lower()})")
        with open(caminho_enviados, 'a', newline='', encoding='utf-8') as nomes_enviados:
            nomes_enviados.write(f'{nome}\n')
    else:
        print(f'Não foi possível enviar mensagem para {nome}')
        with open('erros.csv', 'a', newline='', encoding='utf-8') as write_arquivo:
            write_arquivo.write(f'{nome},{telefone_contato}\n')