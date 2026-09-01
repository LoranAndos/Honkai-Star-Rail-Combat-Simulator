def team_SilverWolf999_Sparxie_YaoGuang_Huohuo():

    s1 = SilverWolf999(0, Role.DPS,   1, eidolon=0)
    s2 = Sparxie(1, Role.SUBDPS, 1, eidolon=0)
    s3 = YaoGuang(2, Role.SUP1, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_SilverWolf999_Sparxie_YaoGuang_Pearl():

    s1 = SilverWolf999(0, Role.DPS,   1, eidolon=0)
    s2 = Sparxie(1, Role.SUBDPS, 1, eidolon=0)
    s3 = YaoGuang(2, Role.SUP1, 1, eidolon=0)
    s4 = Pearl(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

    {"name": "SilverWolf999 e0s1 | Sparxie e0s0 | Yao Guang e0s0 | Huo Huo e0s0",
     "factory": team_SilverWolf999_Sparxie_YaoGuang_Huohuo},
    {"name": "SilverWolf999 e0s1 | Sparxie e0s0 | Yao Guang e0s0 | Pearl e0s0",
     "factory": team_SilverWolf999_Sparxie_YaoGuang_Pearl},