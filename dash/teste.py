# import os
#
# print(os.environ['PATH'])


import mivesfreqlines as mf
import pandas as pd

mylivros = mf.get_listalivros()
livro = 0
janela = 200
passo = 20
titulo = mylivros['titulo'][livro]

frases,escansoes = mf.load_sentencas(livro, janela)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

print(frases[(frases['sent_ini_freq']>=0)].head(5))
print(frases.dtypes)

print(escansoes.head(5))


# import gcsfs
# mybucket = 'mivesdash.appspot.com'
# myproject = 'mivesdash'
# fs = gcsfs.GCSFileSystem(project=myproject, token='cache')
# fs.ls(mybucket)