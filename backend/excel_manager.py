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
    _d = _z.decompress(_b.b85decode(b"c-m!Gdpy&7AGelaHn!QtF7B7Y<I>aVc_>LUGjg5%W;0CLjLaMyI&?Vcv>fG<lcG*ia*3?_Nw2lalWw9yp_KE`1tF4$94C2x8(W_9{QZ4>zu(XI{ds@h@Ans%M7J_NL+Z><@i|iNP1SzAiGS0uw>lboKqCLbioUJ8-QC{!d{}ur5h&cd*$`D}8GcId!K9r@PMYkCNn}&HfM%t$5O_Na9hBd>*--nvo7a?O$6yxF<XJPtL5(2N`Bp1$up0%qkUhI1sHBfh+*4*v@1SPCNUH0}o=upPpl@K4zAfKjX=UpD<~^g}{*byaT0jqm#y5vekv?xl)1?&w2*}xlGzIo$|4yKZd2$@RzS$s=C)Pg4f06~^=Dv)?Q^s8ha{c=wJCRMXvM&yy4^TUJmg_F@TQW>S2WI_sj4H9-S8zS=ex%$KoPURom_x)+t*JAl18X_Vid~pEpfZ6V#|_Ph^$!c=gJ`erh)sAW?epwIIvhxAr!Ez!w5H8N`X<GM!*(Mt*K8Yf3&aYe7f9uf%5@(U@ZObp8QRt_GQ4kf{IP9nze{B53io-VM#rW7@7)Lr+~HSZq%`S9B|G_}b7UrRReAPjrpI^H7k+S9--gZj#bLhIJhjPUxSoZQMkLb2+6~y=I0Q|)N6XW#8J1SMYN&%@e<teaoehFqKo>9eQ{5kUq?3+>DC^UCF(`%~v>T~nQ=~@8#^iMel1o(eLl)nsRW_Dsdr%<%jHb2_lfBb5^=~1-W~{@fcx5A*VYvdu1c_b{6|zIirdT)&Y!KASzPGY?5O4aNURG_#1?zi_LEY6$rh@(FJ&ET~kLN@njT>COE@InevQZ`R{ik`f`v`NhujecAb7R&TJs7nk9ZFHWC9ao7SgPuO9EV^XIi~9wK4a_i8Tb5MEa7JK)j2Y^RW~Wr(zF44XRAK9Wp>$q{6Xh)6Iwtk+#YM@a4>C(xiRB(qhO;=v)PZ6er2_p#`%((E}UnVQ3A(RN6u==W^;3Mf;}UC-kh@EX1;~JsV<<P-WN4zAo8|?)$w1&X;BN0@4#SZtjy-b7a#h&R?&_=XCbAlRQMV%Y$N#XJ{ClEzZ*|hy`Og~@#F-FCjEO1&yF$WqI_RVr6-a+l#o%Q-`l^F*QT%RU#_!=wjQeBS6HMd-|uNV^LL&c*H&wz>MuLF3z5jTG`+}wlEF!-I2eu(JG+@MMK7xjK>QM|cukIyvV!=QUh{Yrf7-uCQ3jj{e^QIp`(rvx(!DmR?{A{Ofi5d{E$)x$4DKaC%@;Q1oDyHgIJ4Xz3GC@ifD*?O1hqPCA2QYTZTdFU(NrE)?vH>DoU@EW4>=M*{`SV|-`pmjz|oql(zqUw>p*90u+Q$}0ZM$3Q@FNIcC;qiftEEt%&p&&spqvo_{otFQh1C*Mve=k71$?3vH1NPZYlYTu+$f?zY*AFW6H=a<v<}L+ctvltBy8nN*<g*aJzMrO@+Z-YJT7dmFWZpzHc-`t1NMFkR0-_|G$5cf0X<b+4*eL5`O~z?dT2JvpWEx{pVWV{F<Im+sH+dQ<ae#em%(MP+Fya{@8&{QPt3ki~Ox;`E)bW`K~ZIX_sSo%D&@12%vd`kHWBfQa~w8yLMW0zKfc_>`Ex};)=dcc4kGX)uURpHjL1HY5pKTmHNU^AFv?`-L~p)xHXcRFA-6<(IS0`-3|8BBsinxcU?4P)(QS9tfV>tpD&#L9p>E>YzbJw&NFs7dx&J0CDvhQRQ*@h7cUz{0X<d%Q2!Qm$|H$DMQJ!<?dU4rpSZR+JCQfH)ee%WWl?Lt{oZ*PT4BMVNe}OUkjAaO$7y-Z8{K<cM`~E?Hk2gZ)#x05m$QCg?yvqJ{}YzZ{|V#=nmT79;XAAZ&-ceN@{f7zkY{4}3T($hETJU2s*xSqgh>zeU`&x(<KV#VVqXKsiPg;On7&UAKvTMWbY)TpF_W6?Aq#qDow79F30~I>yL%JxzX)Zs;QV+b(pDSFFdF>>^=As+_d1JqDXw86!mC4D5}F)vhWRvxk8CaWF(7?NN0stFD*`<4t$wqMrN$q`7tY8(8o{?6b!LL^|16~R*(zR{MD14NXYX!&u2sxqo)K-FQtK1QzYe1meKY7a{-JCHC$|*m4H>cI{>QIuFcw#oIxTb28}OzZCU{M`lrO9Af?nHXEVfVSFUH-vJHze5W&^tfc-XzpElA>fH~4=nbN=PB@wx4QroI^$&HJWZi5Kzr`$Z=AeG6J$(mpvmX!uc39!|x-Ulk``(NrBxXiBYnV+0fgIN{9=FJPt_Zo;!Cc5VUc5@2%?8h$Fz2kc;%Kz<rB?-U0Z5bNDIRlK}9J5o{N^&t}Su8}0(#-P^dfAH1rdnXLr3-S-dA1ew2@fW_>h6e`J>q>k`(!{DN47UXZ&gTj_?|B?NyWm%v!H?>7<^7;PwlHJDZIBnjp2Z*_-JM%NemHsO>pUHk5JuGXDf`2HwiRobR~`=XKLI|4X&)2W?v}{M(bRM5{%QQvoi>l{`N%fO6U*M{a35fj6SMv~$$Ta-^R4K_QGMhZ{-@Vh>4ZEX+6UXf<bE$RP`ax6KR9{SV7sfc$s_s=6ByKOL`tZo!7kpzECNHiSIJ+jm%^=Yemf=Ku5NB6zYUYlvs-yatK1h&t*GPSb<QTFUpISOXJ?j|D4WC49?~tnU5!EhGt9T0y|KgE{gHv`JF)Wq(wN~!R#=m6B-dk|g7Hj@pk0>wpiKL%IadRJ9}`jzL@Qn`>dOWqxIdGW*>cj?fHannehS|+CPEf~^QD8CO;^5OrEj5oq&u+KaS!GRy0n_9@%I?IyY>}UOSDN)#mgWaNPRq@(0ei_GQAnsaGHb4bqSN``AonIHiqlon^pJk`E&+8FG(?kj_P0vLtUx!+?QLiv?DS))OaYKJVjghAcmJ%4b*7#YZ*Sm;47E|wcCyJ6J@gwo)3-0p%VInafLO@LCqhKza!Cv60kp7rniXcrV^r@(JCO*E+6wXM4b>3CTYcWP&GeIQs`FD3xVx%c;L>V0DR;LSFd__$4r)OVRZEbm_MR?!tGYxFfOss=mYyJKH(s~_Sj9PHyABU1Y>V0JP<e$Z@M5>&+jt-wlbqt^ul3UAMCy4dfmMORN;4u2^~yc#6O@yy2d}C+8?c>u4B6TMaV~B{)@nL86*IpKa=*kh9EWk*SS9(iz-a32K{?KSws~u8UkNtAeo>(d;a60cJk40rketIEsnR;{ALvWIOV%0siA#koO*s7?5czEo7eBi4c6o@?|pj%@RSKB;&r{pGV`#5Y4R~G?tP*?Hh%3#vv%`H@7A7ZPVnQU{A8_~pC$fGg8eZGD(VeKuISsyzG>7qvzY$~-aQ5)j_W!Z@Bs9;V>vKG>>SoxfmZ2*%D?wUgizPPuCRI?O~L%<4~4u=P_L)f&O0deAD`@3#8c*9>E+F!eyH+U?{<8?MBd0wFJ1r7Z_^kHp)VZCtRuU?eBB4?3%$I01Gmq8Sk3}k3`Ka!-;Vt7=N1p>z0N>=;yBi;9^ZG>0bZ1Na-2<6&9|{U^8Qw0=;ab01O)W&Lwenl7K9wJtdX618<oKFfX?H~v(dc5$3*6$|GWVEBTX$GHRj&JfcoQbDYQ2RN0aW=f|EX227vzgMo7E04dfrt6Xk?oZzv0VDj^1Rw=e3?WRU88iLx=RB=GzYOTSlN{|EI}oRfyPMnuS*#Oc$<K(nqnNlcM5S_EXz+{bVTYHSnpB(1ne$uCuZNnpO#JI{V4pm6VXMnQ>{mfR_5_Xhz5%wH1`)Cc;Jo{q43{v!(x>ehWrwSEqYarqY0^-!<<W}<L&D%c;FW%#N5<&e0hk-%@UN??BDrQs(8HNJ}Y8;B2>pHgM-ArZF?B7?0~p3(RZerOeMUaRAsklSY=e+x}&#!15IOa9TS)c*#1o*dFWEGCqI_Y;6tT@lSlUx^=wQK0mvKFiQE^zM-?ZeG%G2c05i@bPxA27dWg6Q2s1uL0$)jmjTY^IOMCZr4pDI~x2J^eBTv-E%zBkX-2=)re`IQLT@WsZz7Va53}(n4j2->yybEf2|%xB()I5Aipm1?$}^y(q2$s>sK>x!Vgcy;SLFg-@;J4c@Ab`#Cb-!#3UfMb29=Mu;$Ha=39x6B-GVZ&M0@`&<pn}^NUCLb+@PeSs*|9-;pD}`16gOwJ!y=$AoC~sS0;^5#KHpIA3CK8|@3egAzi(<>LW($dKFid347>7P`rOcnHTRK*t0c!Q`xRTMq7CCo%YI{ux=yf8TO9th*Kp>KAi&IUVgZ;Ng7|+C9nEFG@dDMFHB#+o|HP1>GW*fAO_=llGghEYtsU#-d=c*}15f87A3<`?ly1``nl}47&%!`Umam-;#M?J_P;wE$LAP9N8-MghD3meNMUUyRg-(De&qS6Mn0SByp3eOa#6^Y0t5MK;Y+P{#(C1|0w(KYe4MF<iDeTn$AKMCDjc&dvzG_LHvt>CvhxD*<N3~)?_l_7`|;RmXMQp@DDBOEckz2p?!g0tg|d1{Pldq751|%BJk6FT{J}L-&Xy1{ny>}$+^3RSfTQ-b71~h?OAbDYb9me$>$=by#c!P|7$f$$Gg+y)Th}9X7dY-Mjv-lO1_i7QTfkiCvZMHL4Esmf3N{>+?w6!_IP9`X1AnvAOh4U5#7<WaWTJ0c~nNFJMc4Y^o<Z-Xp#5TzkMr$RsNwm|2Mq{)jRQ}7AN1ZsJAh~PyuI3$xr`%`*xs6(+QNRu;QB<f5HjyAifwSe+!S({B+*C!%ylx*5s!W;BTt=F0s-Fj{M5;i>OS8EB`kZ%KyV_QrH|W)@&Q`4C855ux`ifa{Tf{!+&Unbm%1`H1ny(7u|XW%pZyUvt*w#gT&3zehQ%Ddt6X=E5slAdKL8w=>M6>oV4qIWH0Y8IKO;2cE%O-$DziJ=wAK5_8-)LrGA)!^<M?w?>G$3M>|@qpA|lXZ53l#g<yVKF=Fp^0`xcbmZ$NzmhTssLVi9-GqAs8g?#?k{+l#le~-fkH1G1kF+Ny(F3?|$2oVKI)7QL-`{6O+ZiZmK0rfXmMuh)QJ{*Ptw+Xsm`MK1es+EUl;tZvBXI~owT_)*K!sxF50vA5VIs"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
