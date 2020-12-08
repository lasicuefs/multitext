import gcsfs
import os

# print('VARIAVEIS',os.environ)
# print(os.getenv('GOOGLE_CLOUD_PROJECT',None))

if os.getenv('GOOGLE_CLOUD_PROJECT',None) is None:
    # Local development server
    APPENG = False
else:
    # Production
    APPENG = True

pathlivros = 'D:\\angelo-docs\\python\\dash'
mybucket = 'mivesdash.appspot.com'
myproject = 'mivesdash'

listalivros = {'folder': [],
               'titulo': []}


def init_listalivros():
    # 0
    listalivros['folder'].append("ossertoes-euclidesdacunha")
    listalivros['titulo'].append("Os Sertões - Euclides da Cunha")
    # 1
    listalivros['folder'].append("domcasmurro-machadodeassis")
    listalivros['titulo'].append("Dom Casmurro - Machado de Assis")
    # 2
    listalivros['folder'].append("oguarani-josealencar")
    listalivros['titulo'].append("O Guarani - José de Alencar")
    # 3
    listalivros['folder'].append("serafimpontegrande-oswaldodeandrade")
    listalivros['titulo'].append("Serafim Ponte Grande - Oswaldo de Andrade")
    # 4
    listalivros['folder'].append("macunaima-mariodeandrade")
    listalivros['titulo'].append("Macunaima - Mario de Andrade")
    # 5
    listalivros['folder'].append("tristefim-limabarreto")
    listalivros['titulo'].append("Triste Fim de Policarpo Quaresma - Lima Barreto")
    # 6
    listalivros['folder'].append("peruvsbolivia-euclidesdacunha")
    listalivros['titulo'].append("Peru versus Bolívia - Euclides da Cunha")
    # 7
    listalivros['folder'].append("religioesrio-joaodorio")
    listalivros['titulo'].append("As Religiões do Rio - João do Rio")


if not listalivros['folder']: # empty, not initiated
    init_listalivros() # run once when to load data


# def get_arqocorrencias(indicelivro):
#
#     if APPENG:
#         fs = gcsfs.GCSFileSystem(project=myproject, token='cloud')
#         arq_ocorrencias = '{}/livros/{}/ocorrencias.txt'.format(mybucket, listalivros['folder'][indicelivro])
#         arq = fs.open(arq_ocorrencias, 'r', encoding='utf8')
#     else:
#         arq_ocorrencias = pathlivros + '\\livros\\' + listalivros['folder'][indicelivro] + '\\' + 'ocorrencias.txt'
#         arq = open(arq_ocorrencias, 'r', encoding='utf8')
#
#     return arq, arq_ocorrencias


def get_arqfrases(indicelivro):
    if APPENG:
        fs = gcsfs.GCSFileSystem(project=myproject, token='cloud')
        arq_sentencas = '{}/livros/{}/frases.txt'.format(mybucket, listalivros['folder'][indicelivro])
        arq = fs.open(arq_sentencas, 'r',  encoding='utf8')
    else:
        arq_sentencas = pathlivros + '\\livros\\' + listalivros['folder'][indicelivro] + '\\' + 'frases.txt'
        arq = open(arq_sentencas, 'r', encoding='utf8')

    return arq, arq_sentencas


def get_arqescansoes(indicelivro):
    if APPENG:
        fs = gcsfs.GCSFileSystem(project=myproject, token='cloud')
        arq_escansoes = '{}/livros/{}/sentencasprocessadas.xml'.format(mybucket, listalivros['folder'][indicelivro])
        arq = fs.open(arq_escansoes, 'r', encoding='utf8')
    else:
        arq_escansoes = pathlivros + '\\livros\\' + listalivros['folder'][indicelivro] \
                          + '\\' + 'sentencasprocessadas.xml'
        arq = open(arq_escansoes, 'r', encoding='utf8')

    return arq, arq_escansoes
