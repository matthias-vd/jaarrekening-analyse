def brutoverkoopmarge(recurrentbrutobedrijfsresultaatvoornietkaskosten,verkopen):
    if verkopen == 0:
        return "Verkopen zijn 0!"
    elif verkopen != 0:
        BRUTOVERKOOPMARGE = recurrentbrutobedrijfsresultaatvoornietkaskosten/verkopen
        return BRUTOVERKOOPMARGE

def nettoverkoopmarge(recurrentnettobedrijfsresultaatnanietkaskosten,verkopen):
    if verkopen == 0:
        return "Verkopen zijn 0!"
    elif verkopen != 0:
        NETTOVERKOOPMARGE = recurrentnettobedrijfsresultaatnanietkaskosten/verkopen
        return NETTOVERKOOPMARGE