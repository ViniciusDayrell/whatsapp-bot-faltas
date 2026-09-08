"""
Preciso automatizar o envio de mensagens para alunos faltosos
"""
#Descrever os passos manuais e descrever isso em código
import xlrd
from urllib.parse import quote
import webbrowser
from time import sleep
import pandas as pd
from phonenumbers import PhoneNumberFormat, parse as phone_parse, format_number as phone_format
from io import StringIO
from phonenumbers.phonenumberutil import NumberParseException
import pyautogui
import pyscreeze
import os

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

#Ler planilha Faltas Hoje e guardar informacoes sobre nome e telefone
workbook = xlrd.open_workbook('alunos_exemplo.xls')
planilha = workbook.sheet_by_index(0)

headers = planilha.row_values(0)

for linha_idx in range(1, planilha.nrows):
    #nome, telefone_aluno, telefone_responsavel
    linha = planilha.row_values(linha_idx)
    dados = dict(zip(headers, linha))
    
    nome = dados.get('Nome Aluno')
    telefone_aluno = dados.get('Telefone Aluno')
    telefone_responsavel = dados.get('Telefone Responsável')
    
    telefone_contato, mensagem, contato = msg_contato(nome, telefone_aluno, telefone_responsavel)
    
    #Criar um links personalizados do whatsapp e enviar mensagens com base nos dados da planilha
    if contato == 'Aluno':
        print(f"Mensagen enviada ao aluno {nome}")
        link_msg_whatsapp = f'https://web.whatsapp.com/send?phone={telefone_contato}&text={quote(mensagem)}'
    elif contato == 'Responsavel':
        print(f"Mensagem enviada ao responsavel do aluno {nome}")
        link_msg_whatsapp = f'https://web.whatsapp.com/send?phone={telefone_contato}&text={quote(mensagem)}'
    elif telefone_contato is None:
        print(f"Pulando {nome}: telefone inválido ou ausente")
    
    webbrowser.open(link_msg_whatsapp)
    sleep(20)

    # print("Diretório atual:", os.getcwd())
    # print("Arquivo existe?", os.path.exists("seta-wpp.PNG"))
    
    # debug_screenshot = pyautogui.screenshot()
    # debug_screenshot.save("debug_tela_atual.png")
    # print("Screenshot de debug salvo!")

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
        pyautogui.hotkey('ctrl','w')
        sleep(5)
    
    except pyautogui.ImageNotFoundException:
        print(f'Não foi possível enviar mensagem para {nome}')
        with open('erros.csv','a',newline='',encoding='utf-8') as arquivo:
            arquivo.write(f'{nome},{telefone_contato}')