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
    _d = _z.decompress(_b.b85decode(b"c-n1OdtB1@-j`58E^-mM37V)Snz{3wv!yOC0pg{+0Y3voK*hvCnwsvYCoeTL%dDv-)tu&LE-%?_+Cy|=ZO?N;$imVtCzob<Z{~a*Yi-j5&Mde6{e6Az@Av!j`HI)#*g;=$_4!n;VGtSs{68(U%f{HuqSR!cd5%Hv6EOi_n^vCQ$Dh$~QVa+EtjOEvt2U+~RXa3OR)QYvhRxRS^J0@6?lk-u>bm|L#qKMRyAw)6xorFqhG8Tt03YWr;Eqph`ss^`m~}lco6%VHywtf$s$H}ND)W5tHr86;whYfUbfq%ZjL{`pyF1NFlqyr(Y8`hErQmx@e<c4TgR%CPL4DD)e({&U>R~DDh*Ud45g43kAs+C>j2;;Rs49WFc^DL1hLtB;ymKby&99vpCehANHuyqhUoir-uOR|dJhd)Ni!(MS5o^-F9Ki<|G1-D3=SBXbA}ZnWt1T#-=l;w&gkdr*r$Tx8nJr6&-Wlf&KA+gFfJK+}iJWYvJYwfi{r}kkuXU{)A+Rb$O#b`q#oU|um}pfED;nsfv09X-@qB!B?)ajuNbe{m2BFTz+%H0S?`_~CA@d5xDcId<#r7jo%}<zsPK$q32f4%t7hQRD3j*7|fz#r3?@0!wnm+kGSYU#tv23i{BoB*8z}|Xxh-m+oz;mz%^96!Sd8ZbvfP29i61sJpRksfxWH=UO4GiMMS5d}?@o|%`<E=cjN<<5#+x{<p>Aeri07gC(S0V?0`KzEaOFQBu{thh&^&{>z$NwN&Rc9>+niPaNwz^qvS0TPKLtyBjet0msjoX((iaJ*+LVGsl5$f#*hCFg~%l@TYAEGAwNj@R6>N6}O;KyLG7W!a<1FOwB+8TkLa!_*Fk&EPdcZT;;e6#;X@ZFL1#3S;$VN8T-3vK&ma7o<#-Tdg|ePNh{XB(Ma(B2MjpYHI_zW+<|>p)JigX@Wu23I~<|8E*&Ilp<OW0~)n*VN1bQWA^qya=gRLc=eWMu8w>!2~T%Jz225T&A5Nvk!^mlWc+x7SC|}vzj^z*MD%^K4msi-Qpd)sz12LauT<y<YPQ}VxwR#K|Q7<R?9T~R+3(l67NP_1bW?ESPgY-Tw<e(^u+&6>k`&Au`2GH^Ye__W9R-WzTQ^|9e!o0&zJKx+cY0fKAd@W#3A$^X@_$#>Y}LD2XHYQ2}6=DZ&~UuU7*Y9SO75$BB{X5_GQHVBxh7bT?88a0>{)M2dC)7s?_nPPAnBFP3XnCDtS~)<z6ZavqMj(vRWWLvjz4Qxs6Tn5j}Rh(leOz@2$*#*j@OAgK;RHT%BC^3d8JoP=?YO?GlrM2ijk<H4yZCE$6C8J--L8cYSt=$28gdZB|<5W471dhONv$60VYJXCUb3e_`e(`PUU5_KODXt4V+XFa5+<LF(BgiVnCoV#U(g(>|uSEeiTl;JmUrA;WgeGqekP?6A4MrT)Go<uE;n8gadXz%`VGK!AbG;uh@SOZrAtO5-!91XXZsu9DuJU`nFKRMufv;wK?%v#y*=aQTL`o4eMgQ*z7A3bnsJGzvW}<7#aTty#R%tW(Vxv5B;c9RzNdR4bhrpOmxl{1H#425p+%we;=~Y9ywGrjRs(8^xHI%EuB2VbYy{+3`a2a(>uyF%-XCKd0(bAp|r?k8S}Qn*S!Kk$pKWjO%wy45iz3Nc3*hnEmzJAc>7Z%&)hWw5(mhf1Y4H>U`?s-3XSt&yj(D;VEyiyEBxwU6tAP3=JF-f6VX-8za_2migD@C%M2obTJ-Nn%!vT$4yKMkZi4qI$A_!9Iq1v5`GTmG)AgtcVJbSb>m2u4z&^Q4sYj}WMq{3L_}=JrDRe!>hVwk@`mU2-|&l95;f5`it!+QX$Uy1dk<`uUDK=}*2otADdg0Ir}2Glu1Jm+p+g@0%Q=ub;wO0>{%GhU{3o)ZuRyGC;{tH0(tb<*p;fg|40_sE-i_)R`UrVV+3^!3?mEe91t01<mbGBNVi~{HvbGUxfexFO?qUCo+?x+W4lnb24m<ek9;Pl^`-&g1l%Lt&_;(DWq(ca?`GLl16sddikrf%Ir-+IP$1Dbc)D}Jz%cmH$VF>h+|4*CU!*rpiCae?#&|PGu_j%^frtIbZDI8~6zf2d{mFBiR!7x=+8pn(;f!@cFr7n%IK{o~S=OF4A1(a&nmZv<qic3rW5Zo4hzc?POzrCU#qp6hAOfx^YMudV(v*<?=g8OYr6o~R8jdK+{HoY^p*PK5!<PZQ|ssCh6oIQEO7db~Wjqah<<Z4dyvJ5s7d{*R_@72H2SF`_Fn|o8ml<Mp=3si~0EiYy>>Q}3JUqVb(hY0EQ+=DY4xq?5-{BWD$9np6)FmVSy69rO6(~)yFcZcMJYdIYg)DR;{$&gBai~pPdbU?f2o0h){YGvmZiqOmb4O`LoDIY?UgK0E*UA64;C>0oBui)GAj>Y}Fo_}G@NXy?570F-p+XDUQ!gRMKeTRd)%=q27GT%4(<>S`EuS!h54A3WgMgB483O`z8pBPsnOH<D*IAR+_JK27OMNwZdKl)@D6z<d%z|h#-d00p}vh&moM9~l-+5Ap?hUfkj{ga<<g#dc;21)SyTHuZX!~VP^$~LhrEAZX;Ci_AJJM!K7&G|X>Owd`nw8<w{tbUXqDFxoit;t7)H<U%86U_Se3$Jciwr*d>>0dC60cxJa&AQ#ud>=%7SFzO|J>nrh1^)MRKH7X=yi7>cp|ZAnquPnx@A|jIr<UfPG4t~lY9~M0zIFS}qFAB6EQ$<j%p$aab+fx;du695oOn9kTBaZ3$2AS^*{kg>`u;Nysj}N8TnoO6yCt{dRh5ditse_ubU7M3z;EaOc0T1odqI<Ld<#T1EJv35T>t&M#sB2S_-=5|{NL70{?UG!AJq=V=R4pPg-iGo`{BL9>zDS2p&|i7dYTG!L3)M?*VSfxF++|jkA?o;{!RXF2cMByW_~*n9XcfqoA}@Zd-?X1VK1h}ZlE;<b~tmg<j>-N5V#sYG<>S`_x^89@4@JHYetEJe{ptk16?!`dN(Auyq*tnYW3$dne|VKQ)OITh=5j#QbNu87IAaaANp(Y&(NW=(>>vB3H9&sx2o&e+epv7xQ)?0Lj`udIUQ4IVkKt>cS--;<GlaG9<6ssjiVE1xpx!<yF<5o7G5;DglMqFp+doz+s1#OGW)4{fII36S)a@o?*BXr>@?`lIfuG2tt8a`WAcllKkL7F|J{6<COGMKWx<hk8?_dp3~!g*$rmCGx3|J@(;l2_ti8?N$U3=p0mCSdrQw25?U82wvGg~fX!Pud@@|On>F%6&@u6XSFNXq#?pP3d>Aq4wEfA<a`~yBd53|9J`IEYEJ(GoTWp1DSN@bb%BOV!WjQl_bk2_Gd6$U)@5?=#9x<+54vgE&_&!%J-c2$Wj-07*i%h#-M^6|$y;mL3PQzruBi^1-T8I!CHxn~=pQNTkyq1<k7bHti`J3FSxnfFLZlFeWZPrr+wXgC*Ui@2=Vw#1JFJ^W4nL8!KvTPb|u@Vos_sL4IE0AiN2X}DnUg&30(!8&~V?fq$)&*TIp&VWr5X2dQM^#vH9p-vbgSfx+#44sRD?SVQU{X|9qoBDpo@6)U118%5`#c#i?V0Jkh&#dBK_}Q4d84g9q>&*Bb^K+bF>t9I82gRBhYmt$ZWx4;7h9Gb8{lF66-;zI-dxMlGcC%mEpIF=rKTaiTU~~trBD1p}op^|t!tjY*EV`S4C{ULPqk(TdqN`%mUu}AOe`kBxwIx~hr{N;o$@B4B{hRzMUizJV7B@KZVAS1w1nYQTItc$fNYKLmX><?zm|Q!@%lgmzv@LXKH_*3(A9vs&3yB*|HSfoj{Q}%E?~mZfC*%i8M9BXgjlw53`ijl{nT^M(vad`z0I$vW70tPw_^FTEKd!%eGau6kopMZedI19Kd>3DJVu;hc0yYQk9ZEyi2w&Y>)!%LEqaWMi=Di3%um|VN{P69Zu_BgZ(n5pbmnBa!V5|dWQ6Yk+_aa{_-_?gKF3sNje~?i?1AU<w?4U*ejy+K#Z@68VA@g+hi4xE7IdX&VYX0t_sB_1=d5Hr~i5ws2f8rj>5qA29D2(mM22SOg2ea}7qwB?&iO$zadCnQm8iwANXTEPitMH|nu?oG1rA1|sG`t6LSkc~NFg`H5QDD~Bhf=E1b#eg{ZZhkqAF3r<w=#c!PK!g&6n)d-%#M<x025rn@I!T^exHP4smh>|H}`F%V}-eYB2s7Ge*sOmd!q"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
