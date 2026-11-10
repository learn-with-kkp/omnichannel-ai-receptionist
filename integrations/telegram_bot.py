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
    _d = _z.decompress(_b.b85decode(b"c-n1Odsx!<8i%3$KtKVx3trG=)YR?l^vqVN!B4~{UJy(K(G(PubX~OLoTW{=t!ag&kL64^HE*+goO#rWb=sEcDp+3fRLiowWR`iR)_KhH1B)ZIzu)KkUO(^q`Fs_wB)(sJ)WBxDfW5}eIC!O9aw&i6aSn6e_S#phxNZ?@mzPaP)W9z8%3qAT0qVF%bQ}Nby)?Woqx~^VdX>n=YY=Cp#&|;5A!8tboLUjy%D*z4ZFeBODOZZ0Ag0B!9Tp-6b}&K@=7w;QlODWj@|`gaqexvdERMZwpTb)k|D5qujS=iSA;iKfJ-9VC{m+tFdQIaCAmS38E#e?sLk4!k;bkX+xvUxgpi}bVIyL%$Pv=vb<dS`&EWx%h_Gmg)(!Vzdji1P%okH{tflS@D+9!lh_bFW0@)6A&jJvV${5&>>_S_?|hHsonqK>PpUOI6N@-*p6T&s8xaE{C`M^UiP+0quiVKj?!G-LD{E7B0o-pO{HW<1Zq3i3||+e<3}#VKO*gc4o2y|WI^?ZT&u6KL(9T~T8sLni`>jA#DTYSPWIc&BSyYv%w-Q>Mv(yP)jDXkq@bFpSefRd_4$KjUf6+U@sFyGpv~D$olklXQU;Nx`ug1pKjwbSkX55WzSU-|<4M)Z>#Q{4mY`FlMb0?kVO|!uF?9r}?+<rAsd=Du!9$OZOFl9OOSKWl;Ss=K8l%Pf~g&lBjuGbT44sIk`XOJ=?Q!MW1YgcN<Y$No6Y7YInCjl~SbWeCQ(ShV0(9^{TD}M^I}F!b_g`(pwNc_mUm1xSzc4n{nTpm+iRxaN2$8C!2rhv<sD-N^!oWDXHQ}^OZl;v3M_CwnVQ$w1r()Gtni*ppCpT2|aDoKd$19yN%X~@me_><T%#}e)nR8=6?$#;3vK4XVE=_Ih3!J)pcaWPjZdacSA#*AvKDZzjr5vG3G6uC-)3z<8+x7ub8xbwp)09tL7bx0CWCG{4kV1>h_>=alW)BIh&%{u)rwW#S(sVmu;#K>QBj|O|&9K#bhYH5A`{NZ?bzu!@Kti8Su7Lu!dAr$dT&J`Q1dPN<3FJ#{IU50G3=qdD+geqt633?*>BnHuuksjnR0V5f8Xo`WMtp>b@66DpWO|5%Uc8kX>+8c0Gw1dh(>5+7$mK|5yiS-GPKo0|54$@v{eZ&J^GD{!|J%7sBTk(r=U<FUTA9@=U45vVXAz{Ik^P3jQCnN!Y_)qYrJs9!JeaS7bHgsuCOAeS&Y#obaZ$A$}T3q8(L@j>18Mqb4vxFi*4iAMzA6qefoWFUDydGC?K!oUBVk2)uM#MgbnLae1j}u6kWRSC35#a|A93`u>4}_ZgFLP9y70{WICsKh)U<_PC^^_&GF1-Be?oh8F8zw8!ZA?GNDrTHMY!ANYb`AcrI<$U|YAW<01B=<72a%3imZx#syV&d19UJbE|?0X#~zn_l<O(tnfP&-OGU*USA&EB`Kq+eb%X3N2YfS?AI!?GxF7C%#<|AloeYS@7k~nv(sN!wM@Lj0}K}e9W7YmyG04d)&sy$nq}dL}<PpvMx=GQ}<yx*1IhSQQ&mMD!wVdo2k*lf|D>j<Ie=@q^#uJ$J?##X8ag=0QR0oRK<J8hqKVy^oB}goKb>WVz=Z!n`EzFJ8Iy3y7c{?A{69*>$<n{r+7M4M;kSEfj{e_iTDX07pQ*?h^6__+BX<>c!nIz<xy=bGpVOR!($b`Kv_IQ2>#VE5nL{K$mmnUdHK2+Bx?WC`2mtH#s_i!t2!mWrxN(z<_eLq_15tX_Ssne+xa_Q9pixd<njA3u-Czto``9R)Mc@Rru#%|@Ca-P9vshkPpABTB1Uu-70Y#pw~O^`45&S>TD<>YbJbh@-EeycDfHlRRGj3+JM%NyX?In0Ny~|lfUwHtvR0sPa5Et<qxb=y*<{uK*ZF}x_qO6Ltr>kq5E#P$vi~(%w4>V^d+BjM(Ot0`#s$GOwP#5FaiQ9Ruh;PhGT-*kj+iFh`BMeEsHvTE3GC(nrT;(GutRCJlRm_L`nH%=tD2$x$3=8CLG?ZJ4!Y<vGOEUWy`wF6*IW2OAxSeUsFP;?xu!ZlV#E6en;7P5dqGj;&I;RK76Qbc^5gyZS#FK%JNUB$OO0eM?3t&m-RAhL26ar?@hT=kkJ}mP?>zhATltymJ3mKbYH5jFuZ<@Bi&wsFH~IgKo+#qb8h~GX)`V*JLj2q068asY^dd)=x3%pNEAlcbRmu+hG1!<GBOiME{de!wM`q5rzu~{_jsJy9`cNP6{E%lh3?zm}7JOyHg+E><>U8XB`zTx=-%*E@^kIG1{zZSQvYEQA#gk<4GQ>~I=x4;bP1JzGJQyB7wT51SxHaS!eofUl<|NjOSGw^3;ys64nAG$X>D)t9N|o680k{3p83o@8ZGi{Ns2333Giqn8Tf+k&;4*5Hf@8lBYV<;I_Z0_YR}8sF)vPuQ?T~e0-rau`7Z~y9R-j5=t+XqO?_2<g<#N|Rj!ix7h*u2vD;*z;pG?7-@ToHCr;#Y8R`GeHKjVz}ni{%4xk7^N9iONg;AgA*!y$IY{gxH2)EyBLP5eI%bXRHq&!2DNoAd(!G<XMApszNj%UYD*KXv3@Ca`z7J1=BE0i%Nso&W(tTWUzFQ)vUjf}chGp;J<V@&`i$ik<&8kUCa!H|E1eaelXJ*7)Dp3Fu{|IZs1Yec4?d6fJpSwSPh_4DxSZ4J*sUg1Wtu0Qvqm^Vg}X7HAO$dQ!?-Om&n|!*uFyT@Q!f^5s=*D7l;rJMZ>qorBf=>&lZO;IqEuF@EVxJn7h$+E)beKI{Drpp37Oo=4oQ`B-`>qwx`8V?QgM6d%8IzA54kpl2|i1?~SBO>&tSEAhb8t8S)P<9j7eo7H(b6mOt^!L{I{(4r3}(xpe0ZI5v2S6H9Nu4X*6+MiPnz0Xv%B4tCbO~h^dmW|6lnm6%VbW3?K-g$Nnxqz>Q@OgO4*<N}?KXoVH;y+hNfjxWw-S_dmCi|w6y}=ab&@xetegBa8zE2XOwAe(@-yt{h_cUtAo|9qgV9z0ZAPx_yad~UZ`qOhO*N?xD{rishQQdz~xSu}vS9GFojft%FMe;tt(jW4ayM8L0_Ekm)bpN|)$)M&n|Nm;%7bIyj=1wh#R-iK9Pq`9w2NvGM=emt}idsmwMmgBSDri2=CjGpGzXE6@zF;%_P7McN;MVXM7Ex|>KLZIwh@Z{@J;Nf|Yki}Lv)XTHzPv*Yx2ygxh5iqfblxSAD$<ubFYVP}5x*KEUE~cPh-yMhC$`8S{yrT`x4QpDF*w>CKd_Zl(#9d_k{&%FfZr%g`Oj0zGHp>-_X(?0w)Zk3uFxTUhMiyk@7>gpmVGj4e@y<%AH-vH8O6ioSiQ`fk}8}DD$6wK|D9Ci$ZC`RZS*GRZR<3@f1jZd&N=FRqD1An>xr@TCVh5yHi>j`M+bCYF3~fc(_9+jt|!t%3U1hNH}-kUTH#lRmC_%#HO@s@=Wo)VP=79v|EN!67IDT+{a1KX(gZVB_^UwlJj<r)zZf55Mi|^vMQPy+rvB{Oa~$$N>no~Q-8ZacLik?*B>nE1jcyLpjPfj&wEPB<Ytlap{L-n<(OUQCby2Z;hpih|I?M-I^x=r7;zxezBQ^O@V(pkq`b~5)xJm%c--{Vgt|MCUWBn+kA5Hx6(Y*BbCKB)95#BnRS?|C)&|1Iwymuk=zLE*)M@V1REtky0?@YN_=I>4UggQeSRAbRyM*<M=Q_0lRPDd8&e}E?*kh_vpyxyhvJE8*JJNTuYcKhf#apbRy_>f;uATQ!$|5E;f^Yr$y(Oy71q#vCThb{OxeqV#Tvh0TkNS?vmpE*j|ia6A9W26o6WSP2}d}r3vS(|aMkrvU1GQVdX@rpxUDzpnh&a75^7kZ>B38QyE`TBpU@rUN?vu!EAOljan(0!wdzIICHDg|bJiR->$_u1~H{5VGdZ`f-np9nfdx3fG2h0uIn<G+?8I|kunrQ$LnnUuMqE_h(KXV}4VA@slU7u6FX{x#jNYBAAZyDbu$KkcrDBs`$|483C7PgLPjI%m;`_Q~AUw6l!q1PVAb$EM&Xy~8Vj-oee}1Ip@G(EOGs$8d0svKwJk$!SPGJIy3Q|F{1EcXzGk"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
