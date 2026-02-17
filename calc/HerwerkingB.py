class Balans:
    def __init__(self,oprichtingskosten,iva,mva,fva,vorderingenmeerdan1jaar,voorradenbiu,vorderingentenhoogste1jaar,geldbeleggingen,overlopenderekeningenactief,liquidemiddelen,inbreng,hwmw,reserves,overgedragenwv,kapsubs,voorschotvennootennettoactief,voorzieningenrisicoskosten,uitgesteldebelastingen,schuldenopmeer1jaar,schuldentenhoogste1jaar,overlopenderekeningenpassief):
        self.oprichtingskosten = oprichtingskosten
        self.iva = iva
        self.mva = mva
        self.fva = fva
        self.vorderingenmeerdan1jaar = vorderingenmeerdan1jaar
        self.voorradenbiu = voorradenbiu
        self.vorderingentenhoogste1jaar = vorderingentenhoogste1jaar
        self.geldbeleggingen = geldbeleggingen
        self.overlopenderekeningactief = overlopenderekeningenactief
        self.liquidemiddelen = liquidemiddelen
        self.inbreng = inbreng
        self.hwmw = hwmw
        self.reserves = reserves
        self.overgedragenwv = overgedragenwv
        self.kapsubs = kapsubs
        self.voorschotvennootennettoactief = voorschotvennootennettoactief
        self.voorzieningenrisicoskosten = voorzieningenrisicoskosten
        self.uitgesteldebelastingen = uitgesteldebelastingen
        self.schuldenopmeer1jaar = schuldenopmeer1jaar
        self.schuldentenhoogste1jaar = schuldentenhoogste1jaar
        self.overlopenderekeningenpassief = overlopenderekeningenpassief

    def vasteactiva(self):
        va = self.iva + self.mva + self.fva
        return va

    def vlottendeactiva(self):
        vla = self.vorderingenmeerdan1jaar + self.voorradenbiu + self.vorderingentenhoogste1jaar + self.geldbeleggingen + self.liquidemiddelen + self.overlopenderekeningactief
        return vla

    def eigenvermogen(self):
        ev = self.inbreng + self.hwmw + self.overgedragenwv + self.kapsubs + self.voorschotvennootennettoactief
        return ev

    def vreemdvermogen(self):
        vv = self.voorzieningenrisicoskosten + self.uitgesteldebelastingen + self.schuldenopmeer1jaar + self.schuldentenhoogste1jaar + self.overlopenderekeningenpassief
        return vv


class HerwerkteBalans:
    def __init__(self,oprichtingskosten,iva,mva,fva,vorderingenmeerdan1jaar,voorradenbiu,vorderingentenhoogste1jaar,geldbeleggingen,overlopenderekeningenactief,liquidemiddelen,inbreng,hwmw,reserves,overgedragenwv,kapsubs,voorschotvennootennettoactief,voorzieningenrisicoskosten,uitgesteldebelastingen,schuldenopmeer1jaar,schuldentenhoogste1jaar,overlopenderekeningenpassief):
        self.oprichtingskosten = oprichtingskosten
        self.iva = iva
        self.mva = mva
        self.fva = fva
        self.vorderingenmeerdan1jaar = vorderingenmeerdan1jaar
        self.voorradenbiu = voorradenbiu
        self.vorderingentenhoogste1jaar = vorderingentenhoogste1jaar
        self.geldbeleggingen = geldbeleggingen
        self.overlopenderekeningactief = overlopenderekeningenactief
        self.liquidemiddelen = liquidemiddelen
        self.inbreng = inbreng
        self.hwmw = hwmw
        self.reserves = reserves
        self.overgedragenwv = overgedragenwv
        self.kapsubs = kapsubs
        self.voorschotvennootennettoactief = voorschotvennootennettoactief
        self.voorzieningenrisicoskosten = voorzieningenrisicoskosten
        self.uitgesteldebelastingen = uitgesteldebelastingen
        self.schuldenopmeer1jaar = schuldenopmeer1jaar
        self.schuldentenhoogste1jaar = schuldentenhoogste1jaar
        self.overlopenderekeningenpassief = overlopenderekeningenpassief

    def uitgebreidevasteactiva(self):
        uva = self.oprichtingskosten + self.iva + self.mva + self.fva + self.vorderingenmeerdan1jaar
        return uva

    def beperktevlottendeactiva(self):
        bvla = self.voorradenbiu + self.vorderingentenhoogste1jaar + self.geldbeleggingen + self.overlopenderekeningactief + self.liquidemiddelen
        return bvla

    def eigenvermogen(self):
        ev = self.inbreng + self.hwmw + self.reserves + self.overgedragenwv + self.kapsubs + self.voorschotvennootennettoactief
        return ev

    def vreemdvermogenlangetermijn(self):
        vvlt = self.voorzieningenrisicoskosten + self.uitgesteldebelastingen + self.schuldenopmeer1jaar
        return vvlt

    def vreemdvermogenkortetermijn(self):
        vvkt = self.schuldentenhoogste1jaar + self.overlopenderekeningenpassief
        return vvkt