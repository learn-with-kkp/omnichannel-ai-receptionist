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
    _d = _z.decompress(_b.b85decode(b"c-nPVdtB1z9)>_cK)EQlpP+#`L*}}yo#}GZxP_*W$PZBw@isBAQcpJ5QgflUsjKM{HKw+e<)zGZYR9a|xwF(Z(@l%YwbH`88%t}Q@&Hz!ot@A5`}sWY_xpaI@AJH`a=Dv;-KhK}QJzs{*o1JLTfw&k>-%?6$}*eo;lOJWWFC`xGO|xigYNqj`8sWe#i<iakE;M3W8V~B*{?|Au7tG$*ONSjx=Kg2_w0%d?aPMe-^}`vQ9DE0{mGk|+@R2ha6_O7n%^$rP^P@)mNid)W;uVZI{Jhhe~GA#&|+GJhA?*4o!iLOZjUsn``P+qZ%3aE{<4uA--}F&XJT7`o;+$qO^v`I@1!QV9W^|$g=S1?d5(|lC#K7_VT-Ys)9|9+x|B7b*;`T%y>w&?r6lqEeIoCQtCr;J&;s1nq6B5PH(>JW(ugMQuM6+H8I_fjP~KIS)HK)7Gf_V#qQKsA0S1`&<+eKw&BJh|84ZsixGS#6cm~ia?DiuD*H$ypl!q($4T9deU6_w|bdFGidt9<fLCYFNza(S|3kx>lpojfAr${~HTWIB(os*97mlererc)C*kbs63)XJR^^P1RtSMz-}P@KGkXNv=2r{WCB#E8B53eGzZgOnXe(*symy`*~3Cu8h&QI@O!ms=nE@u4@mC=!10hIh+RJ+m@kPh#DSBCZRb5&t*rU33M4#w#7z33r`YFF74B{7f6s&A4}3nm35lL^ILfB>a?v`l$agk^>%2BhD@FpGZd;Q%{)TV5dSA&qTLy4ap>EO}PREP6d$L(Wbjv+-J%Ylhk0NJ2T!l^o;bU9BOz`Wms5LUD~@Af&R#Dbk+LKMk!9GV3M@3w$On*jP-sY4!DUG>VH56A89?t8DmR0kLA%Q{Mip5_Q@CFXkgec;sR;-u8)UqN980TZjhRi#v-&6DiCsL??5;}GOy=ayo~p?P8I5gQPDg0^FtSbJ~c*KbqI;4F9azs3j3y1Krw54iSL%88eDBsdq8UqJBe<;Cq=dqOcz=1RXbXq$Z<pTZGz?4eBrGex_fVpfCOIDWaqCl4++<`hL;Y$mN6H=CM8H0<y|>+$*cLS?HNr)eY~}K27&7$>>~Mjo{Jpta~J6fL(uN#0CIzq{&W!G*sd|NyRt_i*#QkL-ZkMB1M9Z))#Pf3el!KGQ#D(p5js>-jJL~T`oCl4vVy{34rL@rdJa2umxZ_DGmbQ!ODZRTatgSW3kvmiJ~P6y%rvKtD&KMZF@!rn%vL5NpQ(S}^d78pAOwRy%p&gfnKrVc_iY=SCi1#`{1Lft-&<|)v&|35L70O$^+^34weuddT^}GhHW2$QkniWSv9wl>APm1DJ|jBt87tbzsGpR|zQbomvNsO`FZd+H(+s=5Hr%G)pi4Tajam%3ybT$-_dqz_u{nTqUexvqf1yvpO${-k><c(2>ZF(QEX-_HlgpCZkI8XG5nH3#j_qOB6JnfuuZH6gQvt+9LG>|J>=nlNAM{|OV6B@<wfM5W_5K>NwSL12%Ew-#jWTG_W~N&Lx`lGU4-Hn`h=oxe`bbLLOmo`JR(=D4uurjkgCFe~$*>A3tf?eKM%_;Rul{ZQdBabNyI0eKYs=vr$N5$AqXgajNACNx8Xn-eLlQ|IZIuQ1DTl_Z$|vF>zpdwYI1JB!7}YA&_sMbn#BGsYo=u2i#Gm_Hn%}GQF^i#niSF2{N(C7)xl(=>rvG+b^i{_3Q5>$Ds`Ut@v__ZbV)%QD6q~>f4a}_gpZN)|=Qu~|2IM&4P71GK*|pi-SugQa(JJgokwFOIlocq@z~o=_p=a;~_W8v^TgrJZ<dKyM3%Y+o<+dk%?3rW4AVwo++i?`HwkQSzK3o}7Lb!G#mvWHRJOPQ=r^tw60N=#l&7*>4eSe<sIJ$EhFVkTXVqHC2Q+l*6PBjPka`3mc+%v?ABOg*qGrpc-bGneJ7%l9S$go<j`nGQ8nst5dyAB47cf|!>VKm((DtoD0`PtU|=(gq8uSf`O-rw1R9hzhDjH{o2C8gIWRAPT@GvusI|Es8A=B)3=Izi89Zgh#d<2eN^rfMbL=u^Oy=q;$eoKK*d{mJb}{U{4np*lKE<XlpKJAu%%@wd|Gk>6YSc{Y9Em*%vueXi=5kvi+JNwI;B?J0d)46pY(5=tNOjy{9xJ>nHzpze4g_54KfPM|GcZYPjA`7I$Xw0qv<X~E4Y+x~w2L<;CUG@PK&S)$>sOq>1?$fyQo!Cq_H1gS_q_uYC*Nw!VD^WvLc*vNvy@KACcHTR3<)y*)QK4VbXr|9kR{@8_(?mTBs?JYTs^dN~iv#R<yD|Co4(ntY&rI{duJMU`0|Nc05?4tl>18l#U{YHIM=_Hk>Q?i%(`@jQxD1QS9*XYl!cfC31<FqI7tHUzP<hsy22WF+!A0gx)2B;$Nj+g8_a`?fApfU5f8LlvTZIANDT7cVs$M8<)hmde5G~h+2o6|B%iTdQI9QOk;o1en9`=9$|g(DF$5hQsEueRlf*PVRZ{;9aWyko*&a_CO_!Wc4XK4oK@!_O^j{&A~6|8M_~wzzepZToqRn$3L=z9_$}kqOEQl`!hU8=ik?+dfOD6*8J8D3MojNgUQ&7sRGya&Fn7a2(-j(#BS_*;ar3*qAfVh_&alqCb%ezRG8B(}OLT605!l+`^iO7x_#Vm*tDy!TA+r>;Ge7H?Hu5u?Iv&H+4HH2xyQ0HAODc?FlD=qt^co+_bQj_M`gf*D^wpUB5F5Ljqm=UBM=-?|olxn^^x()}|Zim;QVY+a&HwlH<ScWZL{M?Qpg4Z+gq9BKTkUIEkOf1y=(z3Tm?V=O?d6o91Mwimb7-Qdv=O4(R21N@PrlVcYTpI=j}{^wPgih;f6sRK6`=m-ZtL<6!mgQ^>W2WJ-nd+;i*uVDq2L1<@@ThqJfH`hFeLIFyNB<p=jFK92vc=LO;QTsf_GPaHOGPD8g4^&{`2jhSO3z>D{<c}X8ze$Bqdv&8Dh)Xv4L&OLSHm11|sx>8SwZ{^V?y~9W-u;9)8L;Esc9Kn94?Q$)pEyT{R+ziD%3?d)&xcOU-^S-S|TXX-CUz9NG|KvYDl2<G"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
