# Dit script bepaalt volgens welk model van jaarrekening de vennootschap moet hanteren.


# ------- Overschrijdingen -------
# Dit zijn dynamische waarden, verander de variabelen hier indien de wetgeving zou wijzigen.
# Groot indien overschrijding:
VOL_PERSONEEL = 50
VOL_OMZET = 11250000
VOL_BALANSTOTAAL = 6000000
# Micro indien niet-overschrijding:
MIC_PERSONEEL = 10
MIC_OMZET = 900000
MIC_BALANSTOTAAL = 450000


class Onderneming:
    def __init__(self,personeel,omzet,balanstotaal):
        self.personeel = personeel
        self.omzet = omzet
        self.balanstotaal = balanstotaal
        self.type = 3 # 1 = VOL, 2 = MIC, 3 = VKT

        vol_counter = 0
        if self.personeel > VOL_PERSONEEL:
            vol_counter += 1
        if self.omzet > VOL_OMZET:
            vol_counter += 1
        if self.balanstotaal > VOL_BALANSTOTAAL:
            vol_counter += 1

        if vol_counter > 1:
            self.type = 1


        mic_counter = 0
        if self.personeel > MIC_PERSONEEL:
            mic_counter += 1
        if self.omzet > MIC_OMZET:
            mic_counter += 1
        if self.balanstotaal > MIC_BALANSTOTAAL:
            mic_counter += 1

        if mic_counter < 2:
            self.type = 2



    def is_VOL(self):
        if self.type == 1:
            return True
        else:
            return False

    def is_MIC(self):
        if self.type == 2:
            return True
        else:
            return False

    def is_VKT(self):
        if self.type == 3:
            return True
        else:
            return False
