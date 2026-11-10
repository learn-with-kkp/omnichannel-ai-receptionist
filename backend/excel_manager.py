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
    _d = _z.decompress(_b.b85decode(b"c-m!Gd0dlM+9hlO0$Ct$HV8`qnLq(&YCEDJ5JFfK5VDYjkVFV1ng{{~M^Rjc;8MT^9MKBa1tZ{A>xT@BWYqb_08<UJD2fG9!64w$50Q$@O(ZGP@9+D2pZnbNoadbLLfH&YLIbJ0C^za@btKJdBvjOn8mJXx4`wxgVu^3tYzX!xTuH88Ph^*ugrm@>Df~0G9dD@QUHKP3kyF(L61pdRKK}N0OhRdQILc}wDB>MO`(is=9d_;=7p=1|5P4eO;9QqLiN!kwG}7Au-WfObOAEKdS+(`fVQR<Rgk{!mVl>}i=~c$>-TTME_lb3%%-H>obdkIDJJQE>7>4p>oIUK4JiitDc&L!APC7M-S#b-wF-2i@S#*CpjJM};D$ZqcIldWjM_1^e&b;`^kJ*9VoI?5PN0DX=nK?YOamCmFg3FEs{-UPR)mbfPo!DBUB1{rpTKI<cb<w4IxlhobbHSc~<8{=O3h~+Jr0m=Fxjb*nhU5q7_DTQTPsccXpBC~kVD5HY@YSTT>n!<Y0R^Xsu4Z><>fgU^N%Ey|{5wXKDi+!&IroWGbQ>eZipBG!YJYytU#l5#cGoKY4;CFN?>x1~SUo3Qjr>Lwh?>J)_vgYo?-k<gCn<Clz48E+r}ofwT84E%3YrJ%hxlrteb})QyZ9Za<@k5>kFN^}l`_>c7GVrhxMeYVL4B@8%g%5Z`gFR}tnvGYW{Fzc9OL~?KOeXGiaZiZKa9Im%XcZy*PSauD+LtncJukdJ6rIu^A&U?TN}zzIdvNQ%j+km)2PV#LQP=qw&9sIaHrE>B&mY>-*ZTZC3T-L+1*Z?QUk26Bp#7t;>vf&;K)sKx(Zv>L=A4DmHn?@!K<ZFZi=X3QulUp!gt@UMW*z6MK)RX>(U~0pgt>18BWRccfIcTNP?w*S0S(y>;>;*Xh*2FKS{2P!0CM~KYK>3zJGv^GL{y7+AFHj=FZ0)=%<aUarFPczrle2P==jy<;{AQ{(U$Fxs9~bAD>u$g6r%snIUe)-XG1xeM=qQxo{qPKBjspm$UD23=B3NlJt;KRjbEuY!2?Kg$nr8*r%kELSkI;2^&wVw_d_F$KD~SLxrcQzIdU(ZUil4)R)<ats2Qhl!;qEk%c!4^!4@UX!`!Y#i4zldGS;XWo-hkJb&mJl&TJQ&-b@(<ldF=9XfY~6VUBjt>+m7x(xClyLletqIBEH_ar<e{JMIT^x`$U)rR@&`@<;37pAPUZ$VjnMe_WH$6M^_$4+D+h?D7b6};mOhjd`0Y9_|9a>dtqh0HlzwG0<|?NAhw^tu3g>Rzf|6?W5q>=jv{@hnIPMm;6`l!lEya1SP9FVx=v_;GQ@FHr+!a6$b-t;8*%<R}A|s`H9$b^-fIC=J%V#0a&-O;~Yko#^fs3~hf66owo1j%dV!{XrfUH}#sa2W>*rR=G7h8Tj38Lt{^S3fqDPbcJMP9@wAU4rC^C6|HvxKX86pp3-R6)x<{^ONKs}#b}73nC0e;tm7VBT5(MjI=U8xJSzIw8nCttF=oUc;Col%7IX4$Ap$cB-tX2kv`kpJ{?s$35kK;WWx<5Yov78ky$ks1=UZ<k>J3j6{Q>pfpg(=R0y~#i3g>rL{Vy{SgG)+(TxvTU>Fp*q%~#(am8){>A6w?TFXQ5AIQ=nNijccrXWsW^!S+_u9pLSXJRN1%Kb8tLrv5U-ruRYC7ks16So95h{INEy^zM@MQWHO1<BxT(b|4N?m<<f=I2Exg`|^|kwoj17q|lD;_!twC*YwCHhW%rjgNdK|`fgIbJK$$W5r<Y@Lyv_|1lv80t$L9O9Z{USju&Y><w?sT{tI7Lqg_u!HsBw?pQ|PV{J;7;`~H?(<GCK67Ye8}@X`oD0QOTzMYM?SCb>rMsi7Fp_4lV;d_i!%jg}`;;LR+Je<W-#;0O9OmeY><dECO-pME~J%^a;KDgGGXKf7HX(Sqt5kmC+#T%0K~&Tpx)Kl3*kk*%1~VKG*j-7?}V?DP3jo@U<69LTVT^>vf@CjKLL2eyoxv&%?wK9zJMzSqmpKN>x~Dzc4nchn-USaPWz3hN~*lAI8iW4k3dww}Mf(_XSh*GEGciMw)|o|A=IjFh{4?R-&Bmi^YM5`H}UmUn!4Y}JSuQs&fsa<NmQ3h03UJD$gfY`k`DUBJ?YoDlu}Mb7Hru?Y-))@jrFKtgkhM&`pQ-Wg#=ns9gfA5_oK7DDCv&-#)d3BHf}nZwWBUlV1|zO^!{71j4f0`{xrJavWs{RVy8f#+N+jzOA@F2_$YMh+O~yU2e~rAGy^$wOY;CRE>34!YR$Sv_alYp*EhZTu;_lU^)8<NU7T?&!q$O2x%zX0A7h1+H1PH#l0EU6HaP5}tfX4pll0PH#`q_?z@=5k4u;10sH<KYEq{Df5obx`;Z7?j%L@oYNt=kw1XHw%YOSU_PyS|75vGQVDg;Co-Re{U_tXc&FDxv$0o={7me%-zcKEUKQQn!eNw`n1xwS|0$&z>Kc#|$|SmTEXN_Vl<OZojWg-P$Zz<(0Qi;(b7=mAh764aqHCVmge5mfLyY@dH)|>Cax6%pS~g$@WcIe2zonwF(-dx7Q12_LeWj%3JQsZ^#*bw3j|#3MY1}*FhDF~SA6I4m(0NN*mmBcs*fCV4hl&53Gr0a&Qin3&-~42?jW0IT^+x=iBB0Or<o+vfn`hK`epI=$bw++;T>=jk{Spys@vj-<{v7XJ^XIeCCI9BQTwc&8Q+~SO%{?1`s9~$aVQK3KkzFSA$zGRm6<@WUYkB65Ltye}|9W89p9TJ;f%!a0cd<QIEef$1@u4+BhYb8^n75{>9Shd4vN{j^4VCoIlQAUU*Ir=;eK7cUGJ4vkkne5TM0%8F2Rl$9uwWa{5eEv6>h)g`igQ6U#6Q@9lkNukVLj~|sS0|e%fKBD)^#xo4z5^<RapF;^yDvg%<>b05TGykX~zEAWpwo)$EFAoYJvMEyDyGy`!$dSEBlU)^qu}wRAb8V=}c%}hVG1Ezv)zmdd}k=K2gOd1i-%?xNVLH$7NV$uucOBx?DGjvKaF*J)6lc12;eW&lNBq1)^PicEm{t^k=iXMHB0u49C88JPPeH1N;--)8t12{F}0N+$Z>kxyrSX_jp~T#b^Cl?`n7-q?ESyg8I%1Tuy8ar)L9h4d_3XJP{<Uv+a8$g9bg%PC3%|tfhoe2@T9A3apFf5XhIKLC~y1&o9G#IUPs}+tYd{^I<*<R$W1-xxA7mwK??;f&3*InsJVrwM*v*p)TO6gA<*HjrwUd_%eex=+XXx&s3wcT)}+ci|{k}%QkFzaKm##b{Ao*n~9%?;*i7({s144pAgE-wigg>mb8((+~hy2;l#;|#Adsm+GV`MS?#@!JPq1r!9Tcq{a=Hfq^xa2432LH_cu(D=xStYvL3%`iL2h9LR?;aiEp#*sukna{MmCX%Nc=`ABvjiJdoQL?XL;9ayIy*VSg!OoiKVwVtUdNw+r#rS@^h`lMI^qcwj^eWH^_qW>_F!Q$!SypDI3|V-igMS|+~IOJH{bet95Nj#?Sc7U*j%Zqz4b4*l@uHWzhPb3GGZ%BHOKB+T<3ti!@~pRj?ECeuv&t;a`0ETB;d^YH2oWVSxPm`!=h+AX>OKklTdUId!WB(3AQyIo~fn)E4{KKB`4;RUc?ohUhvLM-NWuk(p3FA>1uKWBtBn|Dos{I95cD@eU<naZbH&SR>BSg-;0Z~4b!A^-I|<*)yP1<<b|OuTYe9?a}@P*R)Y==)4$Tj2Lo<m7+bP!J04gu%Z~9JIz@e+gKm|3xe{i4qZvyb=E(iOk!3lpX>fT_S8VAAG+xad(z#8016X&jqm;;_rHJIe)DXV6bmj%7&BfwNt-7n1AXyDN*B-LtFJ{@csyVLirOL*&_e-Se$?K^WR@X525RF@F#FxuQKtwHdcHvqs;*P&8>bA9r8!8_m`w%5>8u2sZjmnGN>iDb%u(r60G4-Q16y5$_Kx%zt-EjIri}uv~%Y!f!@D!zxAHea6;?i%Fe_a{3{sbj|qi+%&p3BB>JsyL`#B!AF@mJB#~B-OQ1S7#%PMx+GtJs*fF%-{&2Rze-L7@pI3ms*>EdrtdXRVK-pQ_j!8N0z=k29Pip&gn%C$2!l~+pXy!v`XeYc!C*_^`&A*9rQiFdO>ics~F*<ZbynWeYGm!8m(brO}=cky+yS6h5V%N#7X9XsI;@uJed}(_AlH>La@Ey$CgScl+`6-h4tzo~Xu|I9Gi~eo^MvHFO|KA+c|3ApiP5ANt!Tut0IiWH3h!@RoF@9n<b#CjpS!5r>w4X+N!@iFO`2)I>r<#kQbsz$8fmS~z+)Ixn+<YvwAifU({@?jV=5QqU=HmH+{XKC!24@ZYv6NLh@nzoc=MVH>uOIcG{}k|kwi@gQEVVQIOY01JU5fTEWRRakcG&6Vz~4r%hhTJzzh^%3cMjWAvzbY53jh85!$aw<BJH}h%wi>kCjFljf5o=vwFE!7^urlG<2HIT6XYA9zu2OI<NuWp)0?NDl*_;Ib74Ng>^bP+J4IrN?Cg|fq895H%=iyt$o+%"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
