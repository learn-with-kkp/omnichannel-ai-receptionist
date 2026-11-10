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
    _d = _z.decompress(_b.b85decode(b"c-n<mc~p~U_9g~M$O1{op0H{JRKzY?85bagfCv#nzK{(PHVG0yP^e%LTp}(Ew1SFS1(Br^sY@MnSOgjDh@lF|rV@n$f`Uq9MCyz(Up_F}-<flMf8X=o_b$(Uo_oXXiQHv3HnavfE43xQ6xgUc<!=^u%EOp>ii!_{om%TuiHqfR`DqTBo3~qrrccD<r&j95l$1iHrpgIuv5W|hRGblZL|XB+1zZL&u%1(k)J<oI3!^K>=^QmOf$UEI1?Z0x#a5k@@_?s{1QlrAcqXdN;ra+w{3|KeN8x`%@W2(#IkC?RhAUmnZ?M*C;L_%W&Dl0#-PT*#D)^-pT?!=c#D1hDePmg91MJGsPV!$JejZ0~S}^fs7UCjsFI}XltINQeOfUDD<xX~lxs<1CUYT;*tW|W?nkxCd?E=`1Jsd3YDK@+jURb^fmm57?^`*QQj|^IGc7^`icBIc=JH4#TUbuTtt?D0=GIz&R&+HQRS|^d$TGvVMr{me$Q$7UxqzB~(gm!>K-WOd~AxLYZCGxqLYM|W}BRX}8YX*!j_N^zjm2)i$m6gLJ*+Cgk?qNGc|09|K{IfF-gE`>pQ;#lsx*4r@s~)x%YiY}TovAkjt$dVc?#KTr{cpkghR@mO;(Hv4;@tY4L&3dv4{snG)2k@Elj^%^!CIS`koEpGp}$3<0PX%j3~|Ckc^3X;A_IG5M{_n+-pq*Qs6uCjom=eu)JM(DaMK9URhaIrgH)4L`JM{gWW+`<wA0A%xdkshaXO5Qn~X<IIgPbR$wyPGXJnqev}pO)q3=oknRv_WAAL!*QMaHPPGNZ_H7Dgwhwy*nV}<T%Ci#fNN$ppJ834JKYw?Tp?k<s1eKZgcySb3vfPFr&1EWr<FI^SfL)#>Fw)(|72O)xKJ7oyQ5X(E)s=v_%Rk*FWN`O-%V|lBCW;e8ErGR!Mj5xhKsGfMU(Ph>5sb@#%!L3fo?DgNwB2K&6an#2pa9W8MWr|y*S739aUstX1>>wqGT+R1^?^&>(PLvyQV!g1Ds~=Bf78u?WF3KFqDnu=>KaK_*x{Y)-n|2g6Ai5q0;`XK%{9(dADDxJr{ALe5+jYHP-kAV@{HUw20@d~~iMltnat4dNNs3^{D7sfXj-c_2I-@Z3H%|O(FkRPo%p*HazB2P^vP!eHL|>3kMlv}$j|fVjG@eok?-`E8HYzV%5_or5BFQTM*^RfAC{ahJl#DnK560j2Jbm%uHDk9R{D#_pQ6p##5;3(m9hF(l?xG5U?yZwWK3G4YT^k`L#KZQz^|d$~UoD6~oZdq@??0yU87!=ckY>9UT_NmLF&WxA$iBVKy62^o`NQ_=KTK%FX<+{T@2SO5{Ub1h(be81+_r&aY?HF$0|VDVj3s-}YsFphcuxL&fBr=(n#dsMD(YY1aQA5u?1j`>|NbnDU-2nlj1-E0c2bE3@%akxttKUl?a`W$&M1+0-hMd(HxUn1kUGXyr~-%jSM*>lGMUQtpQWF6lfVZ%k!)bxmC|6*R-R5hkx)5~v+bZ|up?<2zpl(6WXB9>FE#kTGps<V9kL(WD+Wv>Le|>W0QXsF;L!ds{F1>%AvMz6zqtcVG1VVP;#M#FNEd>J{+kLGxUV39O&(&2>j_1pDzRF1{R5Ven+DZCv@e|o;zI<-yj&!_=GQ%tN!_QY9~a1bW$7EC_!Kt4q4Ov*bJ~foUsH75#bWo4vJsNtFfyKPZ`Hlxw5teq;<%JTn+E6SPxHG>?uf13(8_1>4&?YC7}HVfKzx?Fh@0l~50g8GUX->(P(1Vdjrczg2km1Y@&B0}I~~KRBzC-U2x>z^b`ZaAXpQ_~Budn?X9I)wVoAt*vj=*WZT_~)RSdQ|JSN1^s#@CNCRnQNoU7jrc-wFSwNUY96whga`aiwm8W_JeJCJNL$)fzEnu~9&O6c8TljiN=H$pGog=HT&F2#rb49%CpzOeii!n=hLOHA|sJN4xb20L%J)YRmq6K~3@XHW%G$BYfq<(;@#{!*)1arX|gKZs8<y>yN6ETKcMAm=%}(wheN;}SxhIU4zW6&bjCD!`6k5^Jo_^Os<Jq(q;@pjp4ZUD&{4sQ;_hJy6ZO-Ha)Wt}Qc__aK)LqZkH$mmmj^1)2g=>-lHxM(6p_F8mHUF~k{LOPKG!2xw)A%22w&MCRq~)ic=0ChWK1{7job`M0AyvkdrJrF)x1KBB6tLIAgIRBV>TY(QTkhIgV<iXcup%cl@eh82{8)Uk1aH#mP17yr5V+jb)f#7U3vN~_*+r)^OE2su!FtL1lHePAb#N#KlWBEJC!;y?6Abp4DCaG$nht;&Ee@c-iDT!TIQn)LSYR#Lv=LYWDm1^>5(*O8(44E=-hQ@>G~<R+efDe-EjZQZ0$%)JNs6KkfkN1a35e72do&#ivMH0iD^fuj<48|+AEz9yG@R}g#3cQOmm&DmeG?^vXTtmj;px3VObMf*39%}XNJU4uU^Ph=K`&*L-9(d;K-Uz{E1>TVevrjPQjK|UDITzoL*brpisEAt@R*wy;Auq6CLXM8cCnn>&eL;pbiKKaVTr<agSW|`K>Zz-8DqkeE7z4(rDIAv@C#HWp8FpF6$IGt{@>Clg|fY6dSsQ+6?YDGo&T>hYb@%o}@n~JNw%%yq{pIY+w7o14>X`nvQApSPLB<_!JV(-o2T9}unQA!uwG4Nk>#S5G8CVrS?p~Vg1@0k=o^?qppVbsI!5=u85yLfItIVcmy$3XQ%af)*!7~qdj_%_Zbi2uhCHlFJ0x%r&^G#_FuHJ0aMnGNB)sCpyTWWs~=jN3I38=RY{8K)-wO8i#jM4SH9zY=?KJ-%xo!B!ov8KH+a*`<XT{6EXWa{g)Lx0BN<B8cB1O46@35#cT?YXz-Ycur9}flV7_*&V<Z4Q)m@Z5bP)<GQF@Lmh3i<@dMXH|6zzi^siMBCfQ0^l%GxZ(MbijZjTl=Cc}I&AXd{2lhVXd0GxS@vk7~=i@C8l>^A_Ab#7LvUKo@1lph8lY6H#gPWH(yrarnsBT<m45%+Ev`GB}(i}G&&pwCh9ZpzWpeP%mCv{V!<DAXvH?=Ftz(1h)UBUfoPr1y(fX^?*tu#lpYFUl2k0rFa^~m&p=%2xU$*<jrpSk(pLM@EGIAXq`SO)65|L^pFN1_7$(JqD4Ua*um;60N<YF^CocMMsZU3`d#-}H*YZ=n6aGjvY>o073d6q*kRoIyWS7MBFAV0_v_36@&A-nY@>!Jx{fiGThnBV7GOtjL`^8`qa*=?C%~d)1JKu+ielc^7bhDKhM*W{#VY%b@x3R3Ag48BdpQssZ&cQ+zO~enh|p`zK!Se^t<#LFD8g4P;YC7mLo?9m|LK>nGt~4E)T(%nCZwMZSB^1O`}-JMkM3-2)%-dzhx;d)U<Qx>*vdQ^$Covg=0tZ96}N0MuU#BbjcM;=W9b-@YGB@US5dc8U9==Lt;R%9&ab?j|iQlx6-q^>q|cq%Bn~0)`!>V0^<nnN2AT?@Z;r$XI?PSRVsFK=VJiNDS6rpCQ&coPSRecgUjU_EvhoJ{8lV8S0;7@D#FF??TT9^_$M=;X?Xo$Uo%JDJcTDV;8k|VbfC;wBO3+^kHQ^@IdK9dem&n#*cakYf<XTx&Gq?YI;1#k2M=kD@nn{hs`}@(0*{mkY8%;6c4J8!T&ua%_lD#DF-^;f_KBg{-AFwE6Y}G=%6KM!P)h|eUKlDcf&S9{A{QXvnaK8oWg0MhH+g%eLcNGlu=`xpU2O4iVwzIst|aB`ULXNto;5C66ZvL3=uZDTzCzBN0Uy?iLN{M>Hj(Y4I%@L@pk7BPX?Uk{l7ElFMFEanI(d^J~GF{CLMkMz3IyQ{6qRHUjp*~t#r0gUq9+s^=lJ$i($T3UX(smqOA_?5g`~)qk{G8#)cD_O&MojVsLq~uQuXWUG{2KngGYzVakv1jrvdjR${->;2+%o+P7m|CgNy+x9Avm_&@m<BIfz!WB=@qCX|8vsY9+d>WjgS7;@y){P{kz^{~CcyS>Yaz3*6{-0R9t#?%6xUWv<H`@DsLYcfsaxLRnWPa<sQ>NC8E-LRl&B369KC$CI6$G-;u#{b><CDvVf7f#dG3p1qfj)k$JrSQx0f@tVISciY%%m(LI@375SKk&U#|K+ezmau^^I*|}skXk!rO3mdbiq}|G6AB$tV4u}juYwh>{dtxugZjhmHs%M~1y=~V-#4RAtksO00L|8)>!ZQGm|uzLAI_xeGMbJ5&)eI1XpmopH{d55UF;4fRF@Gz{!)cHSWT_?%s<qhrP%z`^G}x=@MYLfgndy#A$bJ>2*iao!mDuY1=gSPGx(SA_vJ`nxRPXw9<LkCz!gRxe}@ykvq+IFMAuQTeeR!O#Mh_#X4wE|vbk)_1E28q|LkXm_k`QDWFHV8)Erk^`1PEPFr0pMa0ROCKQ6eu&EWnI+?1sUvCM0UkD`ejb%758SsE442=A%h3EjUED8CpAxZiKF;Wu}BVPG%fcUIWy$|cm?#EPl~z^_Pfzkpo^?nK!5<Q_+w5cSK+djCJo2hrI|BkhVn!#g@92=lj2pXsN;Ztvp=zv$nWE@5a3!z^h!559&l)cBVT?Xt160>WYbG9ve5fASp-_2FyGbZ;`nM*NapX|wViBmSJA`__qhWLxEoOqk=ol{0srpuzhW`Q;Za$&{bqw<_(8{n;AIqSeyhh?gb*d}t#Ay8n1uy%Kvg<@hs(pvmhS^Y6H`;oyDXmvfKj`PC4}uM3Lwo5kO6t9*v{?ve3RP(ia^chgZ8d5-{)-@N_{1GH5d"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
