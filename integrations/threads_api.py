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
    _d = _z.decompress(_b.b85decode(b"c-oy<X;_n2w<QLWkbw+jh7ce)AOd>(^(j;l3?U#gWlkU@kujJ61u9i32-JYJidGa5MTRO^2CLQrWe{p@uMpHi6;Q!q4TFG%)TdN!)%zw068wJM-}^b|>|yP-*FG|PJbQIZ$dK#0ttX1NLLgP}_)@lhD$_PU?dw-Gxt0sday4%i4rVc3e(u`~B~3bso7uCoD#=#~UyqRmTAO$x72UwQA7kTFe$pSg_ZwAKyT!nSf|T!Y>UW6X8aaiy5#7%1i?Rmg6|;%9PgasE!Pg&uBsrpJc}|mEO?M}fS2W0n62wg4eS@8J2{v>#!}dsG<qQ<_D<PT)Lf1u<Nie*E!XT{RCr{y5RwdUY>pMSreujlPgimK~qKp!b?tuH8EQJthvu?sBLeZ2Ob<1F<d?N$mQ#6WhM8O5xvIwQ^%tmn~u4HBpu>esyZZ02yIfgS(&AeZCr23yI^J9Yk*(hrVl}yK29!_hkT`&0==0-%BR};&aFhOn^8%#N`%4i|<99H0uB(=Qa`wd`{<Zi46dCx8yxBS@_w8axo->25yk7F^p?#)vW-_CTH;ePooS3gjGS*V5W^g7CAa8Fm9U4BeUl`!UpRlH~orHJ39r1K8sZ9&;oM0wp+-+!!x7cS&)r#-lZ-}ON%NZSX4V00?wL3ICg=Bf_otF?TLM(RjZQ(A=g9gKFSpi0H80C(S0(C#_pzc7<@<D$b!l)8Ws;Qg~@Y^Y?viu9CSa@JXr6IC|@^?d<LjC3|1rT&?T4A^&StCgGH+pmDFIqOd>h|y)gxj*o0`K=f`@#Q>!OU!f%=@hYNI*yc+SoqwG`Aq6fTw!rh-sCC<Y478d!28Dg_t+kcAA1cI3@}t&wdi%|O(i@lw+M!URyna=f`;{KQjzoIgH2H*UhG(F?}K}1xEo@-9>9D=bz9!}*O}TdhO@gy-_G-<WQX*{(L%MiU|`}yH&%sb&t#NsfkVwRzPz6s%kw~A3_9+<F5&y8gjK7C;U6DiO!W(0zX?2aO=zo;+0)s9uc>7Q|8jz@tn0nFmFNfm3Q>o5H0by!4LqK;5?LMF6=luR^!Z~1Pdp6u8Hq<<XPmmaYNyVFlR$Mpl=csQ_0BWjC$1BnSBWbEejCZOE%;>QoaauxSERzyqv%r|cU@9NQ=E^aDnWb&);qSHT#(!_=E9n<@4Ww)f249mbx~e#;&W)7Aq&5trOK^gSGEoU_30{=5-s#8<bOfky4~2DJ1d@HIX|G+iJk3cgAOtRzz?4p>g&$^j@>&aq#jN_|H#^JfD&itjs8}8%vC_w9`Q#}niunz*6<3%)Jhc+2ITMc#`x#)L8<`XezcnWSyaPwXmYQ00?$$LCO<~|T1gYTe=<{27;|Piobxk1-p~8}IzhjZh%U+7iUH|2$!e^Q)O<udo>qJ=^22$2%%4ASDu@XgU(I=GtsTi&^?B?fJ`Hv?(NBBIpD56~MSK@<V@{3eP}ZM;vaVUB`)vf*agV!$LQZFY;v-$eXBWbFo*W;hwrvTxtpa78Dh`BGpV-q4{;!lAN~)g;!Av64<qY#H!m%tQukitlNPX-kdCdO%uT0G0<gdrveS59sRJCPOMDKQ5=)qzf^TR*AWo@v#kGb$;X~)0f(@si**&g5v{Gsg(Zh7`j@!mK1b&j~oI6VWA{78uRQyclwo%MOCKgzCZjr<b)_DH;)#^L-Z1f$1)#B;T(r{3H}<?hekf&)!CNnWx_YrsH#Ck*}*Vu%hFt@5(<Kz(x}%^(jwWf#GvXO*OV4sD}!fmZ5`F!nFQign^-h|StLCut)r_ptNAc_4rG7R`}^dxZg-WB!4nTW-FW*warkY;$5;Yr%s5#V1Nu&-Z6QK@kjV_HYfig79EAmT<y-@~bS&lKSup@**)dZ~aFsyI*)9n~ks;jV7E1_voBm_op>XVSF`+c)pXx1x{HK#wY)DFcLSe@@qs6k7e5KbEtof#q?S`G8v#2ewhNx%`23GX!Qwpci-T9;u)6pi<NqwAD{+&1wpN=Jh<&E#{X7Z9^5su$S?KsUKQVE0iVYCu<BS+@godegHC5D7V#;CqUKUa6}WC=eje6JtTY}ffyajWkXsI7h2{&>`Yqz`!&-4~3}S0R4h$@qb@T6_m+0dpImr_<NJ&3TC3Xq?f_qCz@hj;Qqabs!i~YGUzc$g^g}1XX0h;451f*&$>ESl5UTxW#(lSaC^rJmCE#SX7FBm8IHih(=^Hi_1@Z_8Rb@%l~H;`^8SXh;phC}gV9<VFmp=sr+W4oGXw#JM&2{9h%nviUU5Pc&%7)SXB@7w0t`|v-ao9>JLd)CQsxCYv2tKv5}RK*0<SapvmX@%?BpJSQ(331z^?V17x)wbNrxshg+DG&Ly1z<;go>YB@#xLQnBQNsbFL0m5{9y7Nsz=Q*{gkAzC~$r3gD9eZ?(s+rW-Qw7sb#lu{$9LeCVxSQBYWFj3Fyi~2b7nZ1&Zbv%C9W7dSOJ5!{iGa-(E(#%sSvHwR|@wtK_7g7r>8%8nD6MwdT+4CH?P;4>@=|7!xtIlG7IQpoY8l>!7lq-;bGoFG!`{Jnz5O7{AK5ja~j~$@|+>VXwDzDa`~$zkn9!i=jR(GiH7RILF|{_}<{>DNCzYqK>CdUf|>U3CX_ph&uUQ_qX_3I6wKymf1;*^RouGlJi~dz~!Z%U~OmcL2ZPh*$i?)Y|XgT{2+G+??22r|MIu<b>TdtWyV}O#7LLSpNF$fp5}Ogp5SFoftSuM?Oz~%vcdnZ>o6kbg}2ROe=OJo+PFi}L{|PUI3|!^zeecLoJ-o$^HuAc7UG-p40)_xdftIZw`&P3+r$K&%MJ#E##JA;!FqHGk|xcBf0N*>19`z-X0xkFf3P3aq{20c=g$y)dKe0kH@b@Oa~3W5&`=~6GYj}{Q>@>P&?xGk3r+Zazwv&&|0VkENhPgw)5L3tw2Po1Z$dO|9b}+*`NeDyb<B-^PQ5I?z?Y)I1gy{HJPr<1kwVh{&&%P+h#thmQvZPayYhmmAi!P&?$oa|iQixk=N06#4E(5USy9^IjL@W<dFsOI2K0qOv8?{=Qr!-!Cbbp7&rOONpKjzAq0jy=gRzidZ*eoY--KT``0C}qCXxIK?!ieQT^w2;ddbAT8GW9b?Fz(qdW%`atQ)%;!1rnw%}4DsP}ZUJxBkz+zXqsZ&xjCtG*Opr8Xv%aV9=v<ekJ&>UcKsw;^LSM=Z7%ZvhylAQ2&t(`0$>|E*n`dMa|s4xjJyroeAnH6yqpUYlJoEfvHuX8|fV{CBkm2WE)TNxAXoN!Rc@H-GcwgJdYI@WZCX(lA5dGCjIl!#6LrS!${CSR?991bdT&pYEs+IfS6s@sXRv}pl=<-g52_8l-XQ5<WXpeZja<>OzR69SwH11|1ISI0)AMRY1@(3@Ep)r#1x4m>s!H40>bh{aRiP!?ZJHs*b_Nj?)5Vy`45z}^w@XmcYiV-m7}blfh6~k9T93vU_aPR%L2{^;l{n`dh}3@ecI$weDLnO5<|-SwxMk1*2>!F_3u0QI#DboL8nzgdP0vb6IsakvsNe=uu5blv0sx1_rgO?82YcrY2JT8KLGOwGeAlA-E7_>D^tNk^7=l7L&w+hD%j8O_(YT;O!~`BoLXKiX8Jd);;YSXPw&BYGHY~ZoE}^}%Y>i)+$`uoYo8eKG10^q=0j6>_DFrijhNNG2Xcbx;m<v|9cD$ddu)%&D*v#g_s;8!*c-d3!MQm;Z~5C$-xnZm7a>JvO}*mV8%6O0^zobeUDsv6HSX=tfc=b~$aQ9(S#O%(lCv(<qcO()4(Okxu-B5lXrxc>sbI|7Dfj=vPgf)llnCy;{!c(XB@91K7A@T$?kufe;ERCasU5_9F(c<dtRFca;$syicK>Q~VE)72@(0jgp@UgS^!LRQ5=QS$f9HMb{QSP0A8z$7zT-q5h~ERRC*uQ3N<YEj|5+`*wBp#|W&BIM1I+h=><GD41x(zI8=lJKUk2u{5U!C$vo}E+B}2QhA)4W^&=r4eqJC%DJ>dk@r$J}HXB>V5`_3|amQ1Ko`;+RMgo;UbA>O3EZ}%6&`~E$!9Yml%g}0N1yn@dnp@6<%R>BAVQj@Nyv`@G&J5g>#5AY><-!7!>y{jN5UjHUP@FPjp&#~}tq|5jPz|TSa@SHQNQ`I_3wd=Bu=6W-~3H^-=XO-moBO&9lhWXK8FWMJVH;NG)61cq6pOxUA*$h(Wo~yOX`3bOBc=%qz-I#On?PRphP+9r!@{=LHnoKN!pFf~Lf7&Ar_4$1-jr-H_U}9v2BTpatZvKt@{-r+>^vF@th##L$jJW4eH%et)BdB?s-*1$C2^BA&ufTaB?*>gRc80t(D|1KA|4&qGSyq3?ZR|z<2&NLpH~KzhbdISlk11<(d``bK9%)jaKb*oYgS+e0h@(j@RXE&&e*ZUe189FC%SxbIE9(FcbvUokeEQ$@^Lj!B?ymk*_|=UQ=Wv`JOgwife?aCu>5ZYsfd1OAsMcYn`D{nLhw*;{0WNyxXo!#3Xjbx<5>Xga{D{iy#sd2D{d4l)Vo4#{_adMaT|B7?+M|0<az<JA%CNr}{~zLw`(3-(@INB#@cMUp2dXu-?U@*(!)2(jVT<_m5mnd-D+vHT$OR6S0Di9%)EqUfMSLfU6sSEGjv`k<xHZs{s~O}Y2@_hU-5P2lYe9egv{WCWj_xwmZ?w?zYz{M^%3W9kE&5%Jy3T0OnK6fCZbZ@tbK4Jvndl?K{u^iHe_(!Xw$?`u?hXU*FWn044<3Zq>_>z4j=xAv@Rvae2KWm^d$cmFkuZP%l_|1cCvg7<q&XA*GU`vvK8L?*S8%!v`#<v~@2)$?MBioFmh1%hm3<Afj^k|i_q_fx{a-NPM>t@eoZv}m2`F1H79BVZvB1nl6TZU_Ot=U-_k3qse||}ExR>pi3jWlrdopI#@zjQA;i691TKr0@mqdgA^Y}OHH^YAe{xNj5LO(4@E!k+EZTSBHU%l_R6yG1W0`pBvOXjIXucf!52wA6d0DU~_=KBxJupbvF&dwPAFNCtq=qs|DuCCmIZ1}dlCj3VeYH*26HTA;QE-uzjTNci=dE#x<Pw%~>pWv+W{BWe8$4SztHqoanXS>>fUtPiP>SLq6H_nH^zAR)`Zjrgtv_JWne9IJL|CWESke_(3W&KG^qSwoBMN@(bfc`MkyZIf2-JMViCYSRAxV$)wC~8*uHrn-=>a+hxe`k@8CRggL$v?_iqLmO}e(xrMP8Nn^F;#RqpuZmOkrc<&{%#|`DNPl<54jL=_XBZw!C@f3OXD-yUsDC20s0rK$MZYT!2FO5oBq$O<hVTiKZlF$4*"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
