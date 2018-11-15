def getarray(d):
#select the array variable from a matlab structure
    
    p=['_' not in k for k in d.keys()]
    
    for i in range(len(p)):
        if p[i]:
            return d[d.keys()[i]]