import requests
import unicodedata
import re
import argparse, sys
import csv
import datetime
import urllib.parse
from bs4 import BeautifulSoup
from bs4 import Comment

parser = argparse.ArgumentParser()
parser.add_argument("--pesquisaLivre", help="Campo de pesquisa livre (valor default '')")
parser.add_argument("--tipoNumero", help="Campo de pesquisa tipo número (valor default 'UNIFICADO')")
parser.add_argument("--numeroDigitoAnoUnificado", help="Campo de pesquisa numero digitado ano unificado (valor default '')")
parser.add_argument("--foroNumeroUnificado", help="Campo de pesquisa foro numero unificado (valor default '')")
parser.add_argument("--nuProcesso", help="Campo de pesquisa numero de processo (valor default '')")
parser.add_argument("--nuProcessoAntigo", help="Campo de pesquisa numero de processo antigo (valor default '')")
parser.add_argument("--classe", help="Campo de pesquisa classe (valor default '')")
parser.add_argument("--assunto", help="Campo de pesquisa assunto (valor default '')")
parser.add_argument("--magistrado", help="Campo de pesquisa magistrado (valor default '')")
parser.add_argument("--dataInicio", help="Campo de pesquisa data início (valor default '' formato: dd/mm/yyyy)")
parser.add_argument("--dataFim", help="Campo de pesquisa data fim (valor default '' formato: dd/mm/yyyy)")
parser.add_argument("--vara", help="Campo de pesquisa vara (valor default '')")
parser.add_argument("--ordenacao", help="Campo de ordenação de data (valor default DESC - valor possível ASC)")


class Process(object) :
    classe = ""
    assunto = ""
    magistrado = ""
    comarca = ""
    foro = ""
    vara = ""
    data = "", 
    text = ""

def transformTextToUrl(text) :
    return urllib.parse.quote_plus(text)

def textFormmater(text, propertyToReplace, replace) :

    result =  re.sub(r'(^[\t]+|[\t])|\n', ' ', text.decode('utf-8'), flags=re.M)
    if replace :
        result = result.replace('{0} '.format(propertyToReplace.strip()), '')

    result = str(result).replace(';', '.').strip()
    return str(result.encode('iso-8859-1', 'ignore').decode('iso-8859-1'))

def normalizeText(text) :
    return urllib.parse.unquote_plus(text)

def createCsv(data) :
    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    with open(f'resultado_pesquisa_{date}.csv', 'w', newline='') as csvfile:
        # wr = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)
        # wr.writerow(data) 
        fieldnames = ['classe', "assunto", "magistrado", "comarca", "foro", "vara", "data de disponibilizacao", "texto"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_ALL, )
        writer.writeheader()
        for item in data:
            writer.writerow({'classe': item.classe, 'assunto': item.assunto, 'magistrado': item.magistrado, 
            'comarca': item.comarca, 'foro': item.foro, 'vara': item.vara, 'data de disponibilizacao': item.data, 'texto': item.text})
            
def buildProccess(proccess) :
    proc = Process()
    cleaner = proccess.decode('utf-8').replace('\n\n      \t\t\t\t\t\t\t\t\t\t\t\n\n', ' ').replace('\t\t\t\t\t\t\t\t\t\t', ' \t\t\t\t\t\t\t\t\t\t ')
    proccess = cleaner.encode('utf-8', 'ignore')

    itemsProcess = proccess.split(b'\t\t\t\t\t\t\t\t\t\t')
    for item in itemsProcess:
        for index in range(len(propertiesArray)):
            if str(propertiesArray[index]) in item.decode('utf-8') :
                if index == 0:
                    proc.classe = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 1:
                    proc.assunto = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 2:
                    proc.magistrado = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 3:
                    proc.comarca = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 4:
                    proc.foro = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 5:
                    proc.vara = textFormmater(item, propertiesArray[index], True)
                    pass
                elif index == 6:
                    date = re.search(r'\d{1,2}\/\d{1,2}\/\d{2,4}', item.decode('utf-8'))
                    proc.data = date.group(0)
                    pass
                elif index == 7:
                    proc.text = textFormmater(item, propertiesArray[index], False)
                    pass
                else:
                    pass    
            else :
                pass
    return proc


def buildSearchUrl():
    baseUrl = "http://esaj.tjsp.jus.br/cjpg/pesquisar.do?conversationId=&"
    url = f'{baseUrl}dadosConsulta.pesquisaLivre={pesquisaLivre}'
    url = f'{url}&tipoNumero={tipoNumero}'
    if numeroDigitoAnoUnificado is "" :
        url = f'{url}&numeroDigitoAnoUnificado='
    else :
        url = f'{url}&numeroDigitoAnoUnificado={numeroDigitoAnoUnificado}'
    
    if foroNumeroUnificado is "" :
        url = f'{url}&foroNumeroUnificado='
    else :
        url = f'{url}&foroNumeroUnificado={foroNumeroUnificado}'

    if nuProcesso is "" :
        url = f'{url}&dadosConsulta.nuProcesso='
    else :
        url = f'{url}&dadosConsulta.nuProcesso={nuProcesso}'

    if nuProcessoAntigo is "" :
        url = f'{url}&dadosConsulta.nuProcessoAntigo='
    else :
        url = f'{url}&dadosConsulta.nuProcessoAntigo={nuProcessoAntigo}'                
    
    if classe is "" :
        url = f'{url}&classeTreeSelection.text='
    else :
        classeUrl = "http://esaj.tjsp.jus.br/cjpg/classeTreeSelect.do?campoId=classe&mostrarBotoesSelecaoRapida=true&conversationId="
        classesHtml = requests.post(classeUrl)
        classeSoup = BeautifulSoup( classesHtml.text, 'html.parser' )
        classesFind = classeSoup.find_all("span", attrs={"class":"node"}, text=classe.replace('+', ' '))
        valor = ""
        for item in classesFind:
            if valor is "" :
                valor = item['value']
            else :
                valor = valor + ',' + item['value']
            

        url = f'{url}&classeTreeSelection.values={transformTextToUrl(valor)}'
        url = f'{url}&classeTreeSelection.text={classe}'

    if assunto is "" :
        url = f'{url}&assuntoTreeSelection.text='
    else :
        assuntoUrl = "http://esaj.tjsp.jus.br/cjpg/assuntoTreeSelect.do?campoId=assunto&mostrarBotoesSelecaoRapida=true&conversationId="
        assuntoHtml = requests.post(assuntoUrl)
        assuntoSoup = BeautifulSoup( assuntoHtml.text, 'html.parser' )
        assuntoFind = assuntoSoup.find_all("span", attrs={"class":"node"}, text=normalizeText(assunto))
        valor = ""
        for item in assuntoFind:
            if valor is "" :
                valor = item['value']
            else :
                valor = valor + ',' + item['value']
        
        url = f'{url}&assuntoTreeSelection.values={transformTextToUrl(valor)}'
        url = f'{url}&assuntoTreeSelection.text={assunto}'

    if magistrado is "" :
        url = f'{url}&agenteSelectedEntitiesList='
    else :
        url = f'{url}&agenteSelectedEntitiesList={magistrado}'

    url = f'{url}&contadoragente=0'
    url = f'{url}&contadorMaioragente=0'
    url = f'{url}&cdAgente='
    url = f'{url}&nmAgente='

    if dataInicio is "" :
        url = f'{url}&dadosConsulta.dtInicio='
    else:
        url = f'{url}&dadosConsulta.dtInicio={dataInicio}'
    
    if dataFim is "" :
        url = f'{url}&dadosConsulta.dtFim='
    else:
        url = f'{url}&dadosConsulta.dtFim={dataFim}'

    if vara is "" :
        url = f'{url}&varasTreeSelection.text='
    else  :
        varaUrl = "http://esaj.tjsp.jus.br/cjpg/varasTreeSelect.do?campoId=varas&mostrarBotoesSelecaoRapida=true&conversationId="
        varaHtml = requests.post(varaUrl)
        varaSoup = BeautifulSoup( varaHtml.text, 'html.parser' )
        varaFind = varaSoup.find_all("span", attrs={"class":"node"}, text=normalizeText(vara))
        valor = ""
        for item in varaFind:
            if valor is "" :
                valor = item['value']
            else :
                valor = valor + ',' + item['value']
        url = f'{url}&varasTreeSelection.values={valor}'

    url = f'{url}&dadosConsulta.ordenacao={ordenacao}'

    return url

args = parser.parse_args()
pesquisaLivre = "" if args.pesquisaLivre is None else transformTextToUrl(args.pesquisaLivre)
tipoNumero = "UNIFICADO" if args.tipoNumero is None else args.tipoNumero
numeroDigitoAnoUnificado = "" if args.numeroDigitoAnoUnificado is None else transformTextToUrl(args.numeroDigitoAnoUnificado)
foroNumeroUnificado = "" if args.foroNumeroUnificado is None else transformTextToUrl(args.foroNumeroUnificado)
nuProcesso = "" if args.nuProcesso is None else transformTextToUrl(args.nuProcesso)
nuProcessoAntigo = "" if args.nuProcessoAntigo is None else transformTextToUrl(args.nuProcessoAntigo)
classe = "" if args.classe is None else transformTextToUrl(args.classe)
assunto = "" if args.assunto is None else transformTextToUrl(args.assunto)
magistrado = "" if args.magistrado is None else transformTextToUrl(args.magistrado)
dataInicio = "" if args.dataInicio is None else transformTextToUrl(args.dataInicio)
dataFim = "" if args.dataFim is None else transformTextToUrl(args.dataFim)
vara = "" if args.vara is None else transformTextToUrl(args.vara)
ordenacao = "DESC" if args.ordenacao is None else args.ordenacao
        
searchUrl = buildSearchUrl()
session = requests.session()
baseRequest = session.post(url=searchUrl)
html = baseRequest.text
soup = BeautifulSoup( html, 'html.parser' )
[s.extract() for s in soup('script')]
numberPagesResult = soup.find_all("td", attrs={"bgcolor": "#EEEEEE"})
propertiesArray = ["Classe:", "Assunto:\n\t", "Magistrado:", "Comarca:", "Foro:", "Vara:", "Data de Disponibilização:", "TRIBUNAL DE JUST"]
numberPages = 0
arrayResult = list()
print(f'Iniciando a leitura')
if len(numberPagesResult) > 0:
    result = re.search(r'de\W*\d*', numberPagesResult[0].text)
    numberPages = int(result.group(0).replace("de ", ""))
    numberPages = 1 if round(numberPages/10) is 0 else round(numberPages/10)
    print(f'Número de páginas: {numberPages}')
    indexPage = 1
    while (indexPage <= numberPages):
        print(f'Lendo página {indexPage} de {numberPages}')
        if indexPage > 1 :
            pageChangeUrl = f"http://esaj.tjsp.jus.br/cjpg/trocarDePagina.do?pagina={indexPage}&conversationId="
            changePageRequest = session.get(pageChangeUrl)
            html = changePageRequest.text
            soup = BeautifulSoup( html, 'html.parser' )
            [s.extract() for s in soup('script')]

        text = soup.get_text().encode('utf-8')

        proccess = re.compile(b'\n\d*\\xc2\\xa0\\-\n').split(text) 
        if len(proccess) > 1 :
            for i in range(len(proccess)):
                if i == 0:
                    pass
                else:
                    proc = buildProccess(proccess[i])
                    arrayResult.append(proc)        

        indexPage = indexPage + 1

    createCsv(arrayResult)
    print('Serviço finalizado')