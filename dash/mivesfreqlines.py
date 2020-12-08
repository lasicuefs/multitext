import numpy as np
import pandas as pd
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import arquivos



def load_sentencas(indicelivro, janela):
    frases = _load_frases(indicelivro)
    escansoes = _load_escansoes(indicelivro)
    frases = _complement_frases(frases, escansoes, janela)

    return frases, escansoes

def _load_frases(indicelivro):

    arqs, nome = arquivos.get_arqfrases(indicelivro)
    print('Lendo arquivo ' + nome + ' ...\n')

    # setencasnum = pd.read_csv(arqs, sep=':', header=None, names=['linha', 'sentenca'], verbose=True)

    sentencasnum = pd.DataFrame(line.strip().split(':', maxsplit=1) for line in arqs)
    sentencasnum.columns = ['linha', 'sentenca']
    sentencasnum['linha'] = pd.to_numeric(sentencasnum['linha'], errors='coerce')

    print("quantidade de sentenças na obra:", sentencasnum['linha'].size, "\n")

    sentencasnum['sentenca'] = sentencasnum['sentenca'].str.strip()

    #ocorrencias['metrico?'] = ocorrencias['metro'].apply(lambda x: 0 if x < 0 else 1)
    #ocorrencias = ocorrencias.join(setencasnum.set_index('linha'), on='linha')  # join os dataframes

    # print(ocorrencias.dtypes)
    #print(ocorrencias.loc[(ocorrencias['metrico?'] == 1)].head())

    # conta frequencia, qtd de métricos dentro da janela, numero sentenca inicial e final da janela
    # ocorrencias['freqj'] = ocorrencias['metrico?'].rolling(window=janela).sum()
    # ocorrencias['sent_ini_freq'] = ocorrencias.index - janela + 1
    # ocorrencias['sent_fim_freq'] = ocorrencias.index + 1

    # print(ocorrencias.dtypes)

    # linhasrem=ocorrencias.index[np.arange(len(ocorrencias['freq200']))%20!=0]
    # ocorrencias['freq200'].iloc[linhasrem] = np.NaN #remove valores e deixa somente de 20 em 20

    arqs.close()

    return sentencasnum


def _load_escansoes(indicelivro):

    escansoes = pd.DataFrame(columns=['linha','metro','escansao'])

    arqe, nome = arquivos.get_arqescansoes(indicelivro)

    tree = ET.parse(arqe)
    print('Lendo arquivo ' + nome + ' ...\n')

    raiz = tree.getroot()

    for exportsentenca in raiz:
        nolink = exportsentenca.find("link")
        nosegmento = exportsentenca.find("segmento")

        if (nolink is not None) and (nosegmento is not None):
            sentenca = nosegmento.text.strip()

            num = exportsentenca.find('numeroDaFrase')
            linha = -1
            if (num is not None) and (num.text.isnumeric()):
                linha = int(num.text)

            escansoes = escansoes.append({'linha': linha, 'metro': -1, 'escansao': sentenca}, ignore_index=True)

            #print(linha, ' - ', sentenca)
            estrutura = exportsentenca.find('estruturaDeVesificacao')
            if estrutura is not None:
                listescandidas = []
                for verso in estrutura.iter('exportacao.EstruturaVersificacao'):
                    numsilab = verso.find("numeroDeSilabas")
                    escandida = verso.find("sentecaEscandida")
                    #listescandidas.append("{} :: {}".format(numsilab.text, escandida.text))
                    escansoes = escansoes.append({'linha': linha, 'metro': numsilab.text, 'escansao': escandida.text}, ignore_index=True)
                    #print('> ', numsilab.text, ' - ', escandida.text)

    arqe.close()

    return escansoes

def _complement_frases(frases, escansoes, janela):
    newfrases = frases

    contaesc = escansoes[(escansoes['metro'] != -1)].groupby('linha').count()[['metro']]
    contaesc = contaesc.reset_index()

    newfrases = newfrases.join(contaesc.set_index('linha'), on='linha')  # join os dataframes
    newfrases['metro'] = newfrases['metro'].fillna(0)
    newfrases.rename(columns={'metro': 'countmetro'}, inplace=True)

    newfrases['metrico?'] = newfrases['countmetro'].apply(lambda x: 0 if x == 0 else 1)

    # conta frequencia, qtd de métricos dentro da janela, numero sentenca inicial e final da janela
    newfrases['freqj'] = newfrases['metrico?'].rolling(window=janela).sum()
    newfrases['sent_ini_freq'] = newfrases['linha'] - janela + 1
    newfrases['sent_fim_freq'] = newfrases['linha']

    return newfrases

def get_listalivros():
    return arquivos.listalivros
