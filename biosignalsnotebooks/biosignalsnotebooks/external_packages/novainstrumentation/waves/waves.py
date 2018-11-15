from numpy import *
import numpy as np

#testar
#escrever comentários:
    # dizer o que a função faz
    # referir valores negativos faz com que a função segmente de valores anteriores ao evento até valores superiores

# sugestões de melhoria:
    # testar se lowerBound < upperBound
    # aviso de segmentos ignorados quando [(upperBound - lowerBound) == len(i)] == False
    # bloquear o inicio e o fim da funcao

def waves(signal, events, lowerBound, upperBound):
    signal = [signal[(center + lowerBound):(center + upperBound)] for center in events]
    x = np.array(list(filter(lambda i: (upperBound - lowerBound) == len(i), signal)))
    return x