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
    _d = _z.decompress(_b.b85decode(b"c-nPWdpw)>8kggekfgcD{em#nR8!k}+R|!i@`_6vw}>VYN!^2>7^V(oThN=fA68nmv^LWPy`7FN(!=y}no*~rl&*Rhr&aV4R=S>*^TyDzp1+^Z^ZcIYdwJgHmD=IB+Z%(PL|Q{GREnX5>BN1F`1X-xbV=-JeMs6JRHBecuBVL2DZZaoaoFw?9>G^|{f0e+5|_3%yz~cjoLA<a$)&i(3=_DB)4$9`A59tk4a4rBBnntIje>5d08)K=Cz3So7&!G8{fvTA#;AD?<y@!65!~SozIUT+oo{x<6CqDyy&Cbi#^S7$jQZy!Q8#&SfP&T-RwcstwSe_E&$vpjnzm0f|Ef%D9=8^?Q|+^84s+O^Y(!ASEhvw;5Py$!O#Wz=9;UaBC%Kqk#&_k?1Fn<`;o@KRkq3SCqpNZA`GSL}IN=(v>GxGGV&|bsFD&JS2T_Z^JP~bqG+nE<;rxh&$rzN2J~|f8|M2HK5ZGdtmlj@O*lT$p<${_X-ebL&tyteE(lLa4l!wgNTP8iET3G)RM^U}Jc{WdU3y}o4`l)^N5g5*me4e$*V^>Z;s^?`ayo_=66-m-zvyRIm)ytZo#`-+8pd~R(3;Fj%oK0tJ!>p^UjT#3;`yAr;iim#IrzKGAi?tk$WpAxr`WU?K5uVd436(i*zZf(dfdQ0-Sh=7&k=SJVuqJf%ft0he&M8MS?FkCMIZ71^4iuG{&Bv#>6*UR?1JPg4I)}BIyAn((b^NX<GVfx61ihv@lUQZhJLs6+${1CLpp}vcu_Nk||Ic}J_Q`UIP;h&z@%@n)`_c@}y%41G!z3Y-+XL1YLfX4vri7vOz!|rWu}E6U*3lbgK!>$rx7`Qz{{IRT(%QA&2z0UW{o^gBqJ{dXIPqFQ8+unx5L`LQqk{8?w4esYb5|dVzNDtImDZ^wXH=c6J15Yzr8#QT79H**mCKv<@YQv|@pD3Sk<{7!_xXg7igLg#Y{*I42<y1NkM?PL!z|dJZL*AMRu|JLr}9e*VMu88d%zpWfI&e#!5n+IEyu9IHy*Y6#QrIfQ`-4U`<xhO;)n*|_)+FUf4$`7z(}}O)Rza(Q&n-GR1lxb=06SYvueqx9l}VJ)_VyKWJ7pgHa(!~zSSmoo$bdJZol62bN_pA`NOR_gCE*a6h3dPo1jK~c0sMH?SaGQ_r_DuMIULNqe;g4F@BR~RVhUOqFeUt1%74}$j{TiRug1DqStycExyM+NTvc61z7~jll7u0Xzvh{cr;`5SB&IZaFoCWRqy+AHqo!-v;_t-?8Z5R(HkOy+CHwGvq&itIJ<L=_{7t_+Y5LI%z%sZtm#jN&;|YfKYirTK9zqrjFIXclDJH>e189CVX!LyZ9JD&kuj-;0{7<grzyua2xC4uE^)J%cB4)?_5K#Z8C%egJuca&lHZw278IZ2VFbg8d<|~kQLgAnbn~zH-K~;Lkpe!Kd^dKTe|}du2K^#&hXz`q--Er9{H1!6S1(?{_aM(@f%tnKuH>2vu2J*e0H<n~^kbXMXPM>u^d)10J}KuCK>Yx<xMSdcIgonxIR$uaoyND{*eES?fD2Am3jHL-JLdZb`IVnnLj^j@I+@2tt)M#*!~G(kXAxePx@{poUthl}2f<y?7pU*w`LX`-2@_~_I5TVF*~?{-*W1?fyXElUo8W#4o3@wKT6WhZ5RR;`eT|X6rl-lGXwPsZ_LyDQRXmKv@VemN@B`yXp>6O5d<cvBtt<^%MHzM>KI2|n(%&EBx<c=5CWiH1hfxn|H;6t>Y8a=a+#^TG+)XthI!4;t{@(VFy@iU2ceTDCQ*9QSs>%ZiyU*|VV|=kb>0u;6P;y%08Bomtw6GIHf5RP18#IIht!A0HOustWjcjw+(8~HVdCU3(-?zX`uLb+>nvNxQ#$0`D#yNtB3a~T(2Z%pCptx!mH2lnV&bK@B!Tq&zJ}cl<7oKhM!YNE+c49^W`#idNRvg)i%;J04%)Gx0|AqI#{Yg`jqS&n6&0#u4i1Rz<N8ct#1v5$Y(3?=<yYK<ux65*|)cAJVf%+@wg7doux0sw5NuYrK=rNIXk`<Ic@xPdVZnLZ%7AJJ|KE$~#7gO8s_+rhU*@s-l>c`?j52n?Qgl<`Z&wT!Q#Y+6A|1@77x-5Ql&O)NY?;&kRoe${CL!iFM2ax8E9c|B=>b_wj4=5V`0|6=kX99~n=hK%5qYk}mzEyEv?i-Exfcv*13`wnb5?=mGdqWPbH1*LdOwbP@&ZIRct)O2X2y1)wE_{+j&Pa_<X*9w6v-|#@<u;wfB2>3N7TfBj1pU(vvu8W_eI?S%$pKgLc@Wy9eehN6jd$>CoKFme%(#iB=%=Q0No5~3pYul-f!|+OpDBte8SSY&&0DqmyF`2~s@o8YZDWm|vk>$ml7t?pHzrm4>A{r^yG$X&o0j>r)hvSVZZo(4MlwA}Rq2fo47(B=C6`y~JG3jo7C8BUhlW0Nv;7vBn22N@O&IN@vs-O52@r69K1jd>9PWz$(7l=!s<9dv+90Zo{`Oq>mJ5shM-aJ(%f-8B6D;9>O-^N;m=Q2a`?ux3c%Kt#?s%N?1lW-A)%O`}#?w^dIrF=Na$-w*!xOq^2U)@X!0$`STqI4X@8T2CuRZ(>0ZaX{TVYv%z28^M_&4A?Msg9Q4wLFoP6sAS%(Br)Rm=Tdn}8`u`T98ttCHBU9U*msUYF(icZMq?&%UOE{Dh0#QI}%w#)JAi4nT1eIIl)?{mVVHl8ll3Kk_3MlpHkr-y^sVyVM`=!u)<$`RWu1pJEk{K!55okAD)akn!EP1*g>^Q3&2w{O$xNufqFAeo~3$sGkhMR%PiU>W$I|3}-?_$Xv$lY>dCM6ma`sd<~}<-!bDTI-7Fo9@A<GUl*}ybEz1EHY7%AkP~B(qNZr|&s15b#M=}6e&dYy+2VYSXz)G|4KV7*O@a<l<Ji$Ynq7TS2-AOdS$Rr|7xjB=&!tDypdTb2gf;NGu+jv&;M$#?Nb2-@Q7uqblV+w{+P{v7Ieup}Ay`$)g`m}2L)BLIMv?@rY1&ueZ~HUyQz)he6tDD0+U|`O7sL8lUXX$UZ$#L$_d=WS$6m@!4kv%}EPR>&OAhXYnolRD)tL{>-^Y{rEBzrfMHutB%9^yWvgnJmp;pR;{n-j#;vZ;)Js8YceIRDEDJ0}NEXsHvVO5D%{)G+3?<Y>$1RSr4g}0`DGeweJC#?%&+RTtT<pi&i{46-;Oe9f@s~D0a3tTQdHz67Qw+7W<)CaQtj@8cni~dI{v$bkpbPqj8>;P}Z-IpUQb%i_%WMw`q&VSy&E<sEDXiO@m6~xb?H9hnYC0!A$u+gw}o0sW#;l4p(d&vrLKZEy$3mZ~VDE6~>?8tA#J)TGk>|l(|Vtn*cSAvI416C(D5wtyod7^(Y^7l!N0;NpRzWx6A^kpOY%C1->_3@5v{aF38T*4t~-6Ny^?cs{w|8F9TDtQQqI&xe8{{TbGaRU"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
