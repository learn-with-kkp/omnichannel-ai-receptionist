# -*- coding: utf-8 -*-
# ==============================================================================
# 🛡️ PROTECTED BY LEARN-WITH-KKP ENTERPRISE AI GUARD
# Copyright (c) 2026 Kishor Kumar Paroi (Learn-with-KKP). All Rights Reserved.
# Proprietary & Confidential.
# Unauthorized reproduction, decompilation, redistribution, reverse engineering,
# or commercial exploitation is strictly prohibited under international copyright laws.
# ==============================================================================
import os as _o, sys as _s, zlib as _z, base64 as _b, hashlib as _h

_k = _o.getenv("KKP_ENTERPRISE_LICENSE_KEY", "").strip()
if not _k:
    _s.stderr.write(
        "\n"
        "================================================================================\n"
        "🛑 [LICENSE VERIFICATION FAILED] UNAUTHORIZED EXECUTION BLOCKED\n"
        "--------------------------------------------------------------------------------\n"
        "This proprietary codebase is protected under Learn-With-KKP Enterprise Shield.\n"
        "A cryptographically valid KKP_ENTERPRISE_LICENSE_KEY is required to\n"
        "execute, evaluate, or deploy this software.\n\n"
        "Unauthorized copying, reverse engineering, redistribution, or deployment\n"
        "is strictly prohibited under international copyright laws.\n\n"
        "To request an authorized commercial or research license key, contact:\n"
        "📧 contact@kishor.tech | https://kishor.tech\n"
        "================================================================================\n\n"
    )
    _s.exit(1)

try:
    _salt = b"KKP_OMNICHANNEL_AI_SHIELD_2026_ENTERPRISE_KEY"
    _dk = _h.sha256(_k.encode("utf-8") + _salt).digest()
    _d = _z.decompress(_b.b85decode(b"c-oCtc~sM979|8i_WTk;Hb{^}(1=2p(~4CPLI@!hkR>4rAz_tZLJ$=Y9N9`hM@!l%Rz`?a1W^KNDFp^lD0V@hc!+}4iUwpWE;MBX>QR{liU*weWBz{UeeZqu-gn=#OW`m`I*LAfKesU79{^Q4vD={yPvT*k1MRgWS(m*+=o<Ymu0C4G|3|(L5?4tVpM&)nnV!dD+s}um_FB6Uz!Y7WK8_qXQX)o?Dz^)2(6^r`M8}jZ;}Euba~x~^a=u?dVIUH`l5eMpt{Vho17xK)C;BDD7)$o+y>E`Y1)qZtOhltj9GZFpk#$S<i5Rp+>FpdUt3oTb&zW@gIYGE<j1dhxl|Hr*e#(g2?F?y67+o(2E6(#rgD2x?uLyVNmBbSFmd6l&FO*JJa*eWEhsCZ%+5pI=iS@os(Ej>lLP`Ajm#*I5L-!(>Ru>a~Rw4ts7U*co_~y{F9CdX9p=i(9F<V*}IX#PkYLVS^7Vjz02BU!iMraeRcW58+6UInxc6cX+9>S#MM(JZ61B>e;;lSihd8_4Tb<FSwPDL*)L_N4TF_Em}8n*5S_3EJjFz4lWm2+oq15KS)KW0fP+8&sRa5<gu%+E8vqdvwZLg(Yz41Q3ZWl<b^>amq~kDZd`g!wvXG?SQpLhEl$p2V};z{AF@ki68EajJ9xn<(_yy_kJlh0H1~6bJFII|mi>N{vclUP}8QHM~NS%JSlkQYw<D{(moG6C!j9%2Uq0={<J$5L30`K#_Fa4kd4q^706jt^P8S1)6pvHW0d}qlqQT`Y{XO4mn2Th5ifwGa)R{Q-xp_J}|2k)u?KolK5)(y<tq6@g40JA*lWfHX2gN6kI`-jvgj`5`SrtB)Kn17b(e25#2Fle!iB&B0Y5voy9z;4kBpwRLz8^KL3Eu_rkQvZe?P<i}Ijgn@NSJ9alQ1MD?%fZ@{FF#xMN|z!Oi$W>}vg5z~=+@wEf06L&Ca2SOKGVk0!+yMljd3)6(}si*d`E+8>!r)8_`Mkv<r`mb~rzfvJ-a-4h=ZKrm6UTg1r+&+<I;vZMR+p4O&mh9>B6FKIz^Q(K@kIn^Yzh9T~=!2jGD$XM5K@QcgxLkt3Kl30p!tRVFICSi<U$7MYNREndhg}K2l_~hRRLk*}990l!IRlTFL`~Y%xD9QPnl6n6*F`?e-pwmMo?+$i%#HS&vb35h>U5f_b>!b?#LL!U7HzcI$gt~`0R(C-Uj8lSwn5->!@YIJMs@?9NK0T}j=U)+@PEh;0Dvbui7z>~4EtOP<yA9LAE_mDf(!Xd_^1lb*5qYiLBA{Dv#?&B%E7E}32yZLz*GzO+@uAWoBTp^2IIr;tYWqAP2LoLc*(3^z?5&sKS2AAFr}b8P;SD9ScCtr1H9B<IH0EN6FKo(`1-wg_7B<sB4|33*ox?$K8)&o>;FsoHsc#|7B*O|TH@EvyU$T2V_NC(cjFPPf`UK*xibIuC*@VovX}Zd^V_c?h7{*PW&FEIvKn0X-1~x?=^d}c5k0mEVkY8pSU<x)sBqX^Kc0OKKRlKUKN?^E+6K3f4qeJO>5u!V-X9zJ$0px4?(nN<c*%al2sYpaMImPTjxXu+ul|Tv@WUfnCjV%gfpGd96O*>U+WFmaNX&)YK!^!nX#>1hmx9nJPyLBy-Li`bvqiLv^oI!i#u6ViQ0rsjcZI)jGk#G_+g!=*7%Hka?_-qpqzC*f>pRbt@adJfxj)<HmHLw#q~CJ%b9;y#v8^+J?+Z*iJ3V@-|G)a%=+|V~doLOIByFlWTs&l}B(1Z)Chd2|g%*@&fNUn+*(dD!=GPtQT=jlC_m?CDXh<JvWAkr%c+<AK6MG3KQ`)PxvN}m7e*j+-^fPE-1r-@s;CD~y74YQPUW(@6`PZ(ZUP>~J!&_b7q+jbELo&Q0;p}e~4r)w{Xa}awW|<%Qa(wy!8@tT)$yt0RMMqgkvuBqT`k?G9H?e2I`I;4cZrCP-FiA$)%^YIb^%A%<<>}_gCeE+(N~$`g{gItyNTLur)0!d&;w`-^%KVZ1u}#tr@cj;^rTTBv=a%*1j9d&DlvDYQWxH7TC+@_r(8Go!F2@q4bOAt-b+WJ52g~|w%o75@BljhL6aWR%uVx_pB1xQZ<1#+>BP;*I^}Kw44Ssd9n}@NiV!a)UI8Tpk4mv#-<DgD!yC4LL;2+|nm-4B>6=eZvNXHUCbzsq|{5AY-6IPk_N9daO&2e%_nbrphnsF1=a330ugmlH#j5~^Y?W1HHxpRc()%ct7MX6IRj#;Gik=%AD-{NPLKb!XxO$ECq7?8uW)nEA8MCcMd-_j>xC#@cL{|GcFzg&Vb>6_dL?yGmD<Rw?lKvD+r$wDS~&h~Sgx9W>l?H6{7?1r;Av^ZCaAWY&#4T#~Ib^PhK{wMS<%lAjv&$)zN#eF%dM0GRTUZW&^nDit%qCr-%KHPQf`<+e~Us%cdaOsg|f4C<{!fxbAz&3Mu-`4;AerQFm1=#wJ_0p@jK|>;{e^32u3GO@Cz6cMn$^W9U!Dk8su@RRP;ECYRFRtOooNxBmFN8SCV`txM;31=V{~9h>u}t%C;&%#D@_+URn)k3<<edJIv-Ldp^iS^|EaJcMA2WVCb5`X~<*x1@!Tx7~4+yC9@IMQ_JCcP}$G86}As>gwiML_ua3u_rK2C8UQAZVT`AaIt3uBu91S-3tZI=u(?G{?IZD7Rtzw`z7R-X)%MO;rkV&pZf;olVBbw38ht}GW4K|gQzZG{cBxNiQ2eR}ZSY~!}w2cX>9HU4O>uOJj0dTtbOz6UbGc5=rl6FEddlV<JwPs||sKf=<(;(Z5K>oc+)^w4lP;#kV1afzVl%$aYLu9tbg#5u4vdLD}M8(q}MxjvQ&)5y=iCY$cF&8GWlp87DB$jdJe_H>v~(k^lOrkP$E)#V8+Fo#bJ^Wasj%)g`QK3a_rs}q{Rrt^+-yX9~8PpHm%`1ui0b*65{irr_cBy1rs%8J(L`}VYoramw+17Y=`H|<s(Wi@Ge#Gn&r0$DC*eC<lj_np(H3lP~I4n2@bd}X_4KJmlGzafg9iXW4FJJZehwhH>?tT+1ko%7O=<8VUNGKrNANVX6h!41I!N+h?S9Ezb#xV@Rrs&U(hPV{CO9eD-!tNYPwhYmrvz4x=#z6wU^kk5{4ep&5?%qeD228r?6LBkeCT5)**64avDRRbOxOGI_Z>*krjoVAkAL@x^Uv9?_GNhlfr$97>Wv~S9M|6ZQ4Am!7NMH|3hM~%iiK)N*WkKgDMp-#KHKmm;Cj4)30e*hzy5Ci"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
