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
    _d = _z.decompress(_b.b85decode(b"c-l>tc~p~U7RE^fNytLJ0Qo`^2qlO%AmEv51vemkghdIE1+qafED0n+)k0k=;1Y0|h91GPi6{!lCWsDl02Mf$X<1Yj6{t|5YyysHhN;EY;(Q5I=kMpd?|bike)rxt=3`sV#(Tltdp=S1UJj%n=DaEYu<WUbw%5g0t_Y6y+N4QXRxR>U2;}IF%W$-pYSPlyvENjbe5VpUHKG@z7HYg(rH@ho;^ZyJiuS7)r3uqnp~mN_D)nf8Ek-GFH?O62D@1~lOMysIIU)T7Ilp2bc=C%1Jq>yq&g3|wn#GS*I6`k82PHIk1XK{8O|WdWsdwK<w&lcpyn}<U7xud|d<(OKt?kR1lB<?I29{T2Q1J``>ag+v&3BzkUQVM!CE0!i`VDnrC9>x&((!ysMU8oIr-O#=V)>5We~iK}8%#!`=1`(L$j8+zpEL2-US&iM+oXbCHVyotWKmG|i9i5RZXQ@g99~qB`<zZqp`kM}j@*;6M0*>DaQiwdkSLs77tkCuzL)~&;%EN=*xy;FC+)(u&>qKPxJB6*8`3YX;wtY|z3U}P{)23<co)$i8aU(-QB=YKrLR52O_;tP<Lz{@4SE#NM>-(h#dyaZiKB*<)l1OUi(dX$9Gh~Ff)~>2mjwjvPF^O%qJ}$?86Htoz{L^nC)qWD12qatZu&Jn5Y-Xm0eazDg0mte$=Xu66)?Mzx8(WsXAL%ARW&UDwXRB`mqk5IzsCpJ{EVr}oZJw3nOxYXWM~hxciRW_Qo{K=9b1FDUAFla79<cza~l}*n!*Z}I6uB}kp}%vPQ+`dwLy2>MTp+)P#U5|4OQ7T!Fq?HdW96#V|5g-acST_R)D@a)lv}sT#a3Vo=+(4&&OW7o&jiOOtuT-mORIOYeZQ|Al~*B0H2?!*eveaQ$3A{=$7pkxe@D(=aG|x7`9OF;otPps6pl5!EIS_koP*I?86}2xw9E~{`Z4Pc>Hsa@`|(aQbRt)s?%FX^aJThuDEvYU?##ow`4acJMFi#5j*<&h`2Vj>Q6giCta!ZCf57wRh9yn-;k|SUc5_|V-pGCKjL202!H{qCW^_(;*V|>@yfE8Y+<>YW8~*kab8+$mH>`FUA$w<ZL?A~MtGu>gQSi!#Z}u2TUa3rxUL?QydR^46tqUTeiEw_7sJq~*GY`gkH)81fG)BAjalm2{V{_nggv^8vJi`@ze(HCWA|B`O!~nGmYQe=@kZE41|Bo84Ch~-L^hb}U!B^ZM?+6#>HN)%cl@El6hv8ZC>!-34?(Nhz{I{ae@+mYavzIZ(r%SKqO@Q)Nc%+{*ks%H@)(etI%|qQz~9~Oo}gRh!0RoM5~x!?G3}VbISrv8zJ6N3>nEy3ENUICTLt=Rv!#17%hi-6sJIF#?r?fBWexP&q=P$fm63xQdtzBZI4Cvv1hj(R)O~so)@zLSe;(yRZKeGx-njq9+1+T1*G$n}Zm&T_xNx9go-XL{`waCJ=UvRmVQNs$BkX6u?>>~P=+5~>yHifJi?o;?3{$`gX^nbt7=i3sHq~F!Y&{C|@lEW_S$ae#FO~0wYm;_sMBJi5zN0BV+_*u->`J?`VkgXTV&XKkd;S9oYQR6U{XpuR-_9jYVZ~AVyf3b;!2Lr=gy8v;FcRk&q%A<<=rbNrmG{^}GXCrM$`#o*m`_j>@@_5vFL9*%+aqhR!_)hs-t$l6z<TLl{QsZcxFYc%uu^m4{g*bGbeLao%7=H`vghq)%j1Wx&5#A>9OKw5LSxW(?i7A+e;ArR=N)+;%FktqSL^o!H9hJRT&*-K)<JmI<iBF)C>%cvr%k)NOap#OUyZNSUBWBNlTlEY_frhy2eZlcc?T9MP5oum?fO+X-q{PGzG3C=<Sd(Kvl?uk^6so%u$HXhv8-ETN)tiu#Y>?m>p8Wc&F1MVn9sDT8uN%@jGFCYag$b@j`2NjoX>SWyu0Y9hDhMlSNiLs_w^}Dg5xWJNKq~7fM)W8`C}&kEw?qKvms~4TKOYq47V`b%vZ9si+9DbxDM%{RlfKGAsn`dX0yy;{&+TFr?e27G~?m8=KuB=oizC%pyas`bzvi!h=aP5(QyAL2&Vj{UCv!bzBVc$SBv_nhweBiJC6g}PpbWzE&3LYiu2;DmnkBxLqe2`c^$V@BjUmRX9bk6#_xgc*k8SDCLSQ~6DeX%^+R@>>g&zB%+XdHaySp~H#cD~9p)dZmv?89pwa>}mC(o+{Qfc1{&N#|`W=Ycf@+kGI^!WN{J!g=C*2gE(LYmuJ{)(OTf(uV$nZ-A61w>G>Uns6rnEe9Bs_6ADsjfO*>)>18CipYfbgcDQLi)g*D?v}x6**Sh;^IppuPB~a%5<9-9}y&x47mA;dolx_2_M#)OgU1SevlMrzQR0JEYAYJ)elg=Et_bkwG2SaU!oR%`rLdIAPHsnZ52ekANC(@oN=1H+A7^G`7L$U(la+dKF$!bWzH-f9c7qMUGXx-ygEQG2Z64gG<#gpLrMy`~P}~m#oJZ;r;Hpa6QuGzbC3yI>cMeUwB{b-;5buJhuK!!t5I}b|2o=QGsd<h4&N2G{0Z16EtDxX7}QC$!#^kz+=15jq^`FluQcKjeTiFn{<`_9UOkCB;<KE=*{f@1t_DKTWaM)8c_KC;6WdmseU~Z$MEM<Ul=~{{k}h8{u{C5)5`U${dwj?e*|g24W$9IwkE!htUsA@ciPOlOqRlDvTq50(%5F4E{?`C42lo_UAGVn!~X*t%SOSFiZ0ZBixml%JOhmTSwqQz|1T1LkF|#H$!LxF`7kBp^rb)w>4x8$za7qPYyTe`%X{J{stu4fTY>`&NrWZr_@Wc@oYRdN6!1`{7HQ~hL1S_F4Bf>r9DOc9bs70&T1hygD3~YnA5fWc*O1$`4-ZrMWyj?>#6nzz!Qt7w#!eU0uBXBGXX4X?UMus_#`z*tW&RKEUk!u"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
