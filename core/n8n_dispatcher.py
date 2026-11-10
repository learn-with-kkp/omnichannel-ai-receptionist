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
    _d = _z.decompress(_b.b85decode(b"c-n1NdtB0Y7Zyzc0R_Y#0-}Mo4V}8nyQa=*BI0F=#zjF0yk7!!+455@Zxxo+bjwS&a+XOJ$}G3n^^zCfZd1XT+RR#-<u$BnbJKFG-XG?5@BV&1=X=igoacGY5wFKF-7d2Fb6}jkd7*TYdINsH$=xT3z+uW4e__PkBBsQL*uol2Aak@O0cc+58v?cI&5<O$Jayt8NpOQeji<rY!R_(*u)TSrkenM-#u=z?EXKB&a{f6=d;|BXfNH7?sz|nA$n#+Ubn@-+Mx0iW1!&TzN4NnU7AfKDP0s~YNb#KRXM_-5my@6YGB8K;DvmurX3fx9$pDm@I<P&P4_D=G!9b>+{2GnRl{ELlMD+|ePJ_*qP%JO9N?dsM+S3dZ;E@zF^WMNCncdN7MK04$?i2pGEaX*YzsweL=`a(*tKWe?VRg4}7f|9d(Mj5=BW>MHvsFiY<+71gc_IKQs6z6aAh(8SP6y*vFQJ}gY-*wdp%(vAh6~lU2BGc7eZ<X>@-sAN`3}{Hk)Q)hO`wsKlHN2jTYDd%2k51rHo@;dk_j5(TZS<Ka_6m)?u2iGJ1KnZFJ-We#JRU5FRj`Xp@@QQSI$LX>ocW7FH;q(A{ODiw~~*7&PunOg7+0g<GxH&zvPNKNC^@u>SxZ)EIg;OM`R8icjBmF_lwdIMY4%str;4aR7eYMjO>gx=V{A=0Q4+1s!=vLmx$BsxHwN1UlA?7AB3S-4#FHre<tBi0=mbE_`K9B!-P#87MXyfU2X7nXh!J%(l98rDihxdzyB~Af55GN%4iRmpW{t`@tNGuE3kZT5CG_1{hx+46m7N6%ebucgiX3j{k;&if}fMkNe_Bpbl#Zj<{6Li$4TfC@v$l>ubt?OWCp(?R=DsX+PqK;t2!TXi^=WjEWrTfuWE*8y@(3PEYzZktz_Q!@=zo46GzbztByw$b9w5wXSoawHjeN9L8JJ93xapN$C@7b)JfO``?`+C9i$wXH}pR)3QwpF9QrT=qBZ2Nl3G7y=!dcp1@SFYQ1lHeS@;H&GO#~|AJ%&kW{n<l;5VVlhmy!&rkx%!LSMB=70N6xhTO`*hvgq*0=y?4_#dFU5vfga{Fq@rhWZTkyYkW3ds2}mlOFtL#K2^hpe$NFY|U;bz+U4neD3jYU=p6v7eB)+SI`6+%7l_D>0>8w+`;!t-8K>ws+>1J>{z$6+~dh@e_=ZU#L@D__j_{qtnzzdP{{ZO-#;0%%>i$Gw`u=%&-5XufSooTx#?5BQLqQE|M&WR;3%c$c~qnZmc;j5n9rM^{intJlbj_yTu)hiU*Z(34D4R%j{%>Pp-Q)(RYK_P>}_;!lX`3kbQ#CZaLW_|+oNwcO%XS1VN|w@T?_wSHW{+_qzH-y^{0mSDH4F9t<CdX!BtV*CKr?Mg!f~}&P(st;Qrfc^7{X;|A$oZZn_XR9XuY2#MHS()Ijf!?6%b;E9Ob`ZV}j@4{9a7GJyB}2_}FZ^@ymkygj*l`>OchMs9nuJ?BuqFN*Y3YCZ!Qcp8C{r=K4&O4ngCInFjMtXr`F`)YnD68G3AS#A7P5p7le4airV-d$wo@nR8z_}Cra0K2D%#+Ss`KU?q@|5%ioRqAHRDEK-6WjEl?zJMEe>KuM|&3p{}Jy9&gEce&8JXSStgdSQK!|}3f<n^xY?;pwL#fU3Q@iuB!TMhtGR4}1A2MzeWp>)Ci<jeEcj2pNu98b`{N}>G4cz1TIQOR=s8uKKO{}+Wflj)H1{3zCPet6!_>QQTMCFsv?cKd_cbGQ)Y$<023gNwMJB>wCqkuh(bh?If)sCb8OQeMnJkxnh}v+n)n{;tQRxi$uM%8>MZ$AonB@2-LxrcO`8_oq(`6Vca1G66N9Iie@cDo|buGr~PsAATC%IhiUbNl{N(a}SHb{jsF)Rr;kdG#RQftlbqtX39sF&Fr37tL$%b8NndGBbu?}k5kw1^CGX^WvTz({;i@0#j5#5IiM~{x*Tj71qZ@{txll@ldw@mfbX~B%C3z&_3sCz5ZsH2y|GBh!3yR&+fi@-M&mL?h^0KeNy+(SrGKVo+B`pm>2I!_7mT(1@V2ZC>x#=*=I=CfVonCn+pbbV8P~9hk=_=Kn?V0yR2cl>Hz)2T6W!nDQ!gA$B=fXgFv9YD4EQ+=6WmX@%wTm$e;hJfUhEHDnU5hpf}z7C`MV<;f-67d`ya{=1#G8W3C-{>)%wVSjGD(JdK)>@E`j;;>;5kKTa8KIND`_wx$Ybb-A#~1Qtfg%cPMN4SCeW}60N_$-E_?~P2gg&9B-eqoc}7NaM+9|C(GC}<b}Yy$w<hdyv;~J5BeLtb2h<9lTo8Imgwx005`;U5fwRP_K6B623<vE%)ka_WC%@M^(bDbv03&%-oD&W6AZXNYAia2lF0?>_0{Y7w+V6V_~=)w>i3B_4eIw_27j-1_S0Y!Qw;m(VHTcUIY?dcH-RQv{RE2o0+GaZG`+C-;ZF0=AA3S^Xi(p0puhYoL+L0g!+qi)i=<f20za(u2R~zcXDA*h^g8(rT=z@*bzJU`-(}puNNQy9j`PoqY>s3u)GzLr^0Uj2G0mLxK7MCB+Vs0oZ3h0@%Hf|zWd_%=x+wh3hraTILM}<St4(!-yHQ77CbYz$XW`TZ{XUE%gcP>H!22W?b!Tb5FU^7~GgtgW+ap0h^ioL;w(Z56o=1|w`@yE$I-TQSUkm*y85eLp-`5iT#M^J4d1sbJT)@riMXTe%`lnqPGs5z*1T@I+>UEMnn3LBUe6fFf5Jz0D{LQ}>@CkQ*v#@PsD^|W^B=;ZiDhGCh@xa_}#tDbRqeO83W|C~I>LnmQO%CnlTi8BW@PB2Tc~QFlEEhX%nZ$^3z9i}06-CnCjK`zKZ6aFXedi=VL99yqvHdajd$@O_|6bo({TcG#lJYr)d1e^Mun+x|$1nO+a6g<?ii}G`T!HMUUx5mrK&u~nh-}~5Z6B}Nugme>vG&ZuTr&h|#L@oWj3~kp!DaBiq@icwF+3WfPSh5I<7>-&F{Z;l+{-5S6taKvhr6ExxLI$;Bj(jPnfXr{O_N6ceGV~#w=AoyDjnD8%aA|5`Z?zR=VQRlZ$C`4J?hpvX(rZT6YQJ<KR!i%sQFfVo*6~DFO6<ocT=B;)ofQi!U%c^iGYt?3#%=gA9ehgFvM)u$?vT7_*f!YzGni|zg)O$g<nOMeBN^p_NhSK&^FZNkDgy*r1p!Qm*-!2=o6^vtTdz6bl{IHbW!@mBowV-!dBO3K^%RXeLApf<a0cz&nhf7V65uS@1w6`dOra6Xul6a5XRl`HE{4gu-TU~@dCr{v`XCq-bdojSWH-D4+{mYl7%#)!TaZp!f3@59A7Eg#d$Yy_MIP~070$_L74sK<afaWyx$p`u<2{>2>Ot5bT?ylV5wuq{{W$kI8X"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
