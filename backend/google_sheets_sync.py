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
    _d = _z.decompress(_b.b85decode(b"c-oCtc~sM979~U=WaCH3PS^s7VQo931sA{&5<tV2g@gox5EdouiUkh{mXKl<urLy}h@e1aajQidu%y^_gitIfiwhK$O#u<@fHGAkiQ)k|=gj>5o%g->?z{KBi%Fte<LimN*{MGHhZq2;%8J$sxiT#_EJ|yw!;9KY<9QAd-~04N@Hk%`+73rmkwecKcFs|@6-2hyuv1ie&R8(9p4A&gU_LAjMc}KpaBGowrsMeqlIAgen$$6hYV$7MJ1?IJ2QSBCiXs~N08tM?;z^JAlQ<Vi@K!z0ygLV+h4zd`AdY-CIjt|cDNN>Dn=ggmIcP?$C=WF~IAOc}2=?yWF8+{}d`gFR)H*ECR$meQ$cD=*%w-_K6H(@Guy+?ExKfwqDSeI#LMBLj=0vv-ggVH|ef90fZM>Qw-Hi#@QgO|n4xT?j_P{9X&PV?$f%~?<A|r`oj=`05X>~MK7E?KDV%|<j&$LD~i*DJ5#^jX;Ab}q1;3kx+KN<JA^~0QOwvtE=qL}A|^+sAS3mXMcV8SC#p<CQQVGmo$7IpZYsHjjJq26cY(^QbE7XkqD?%vnw1M_y~(tVAix_H?ZW(I8i$>?X^+r({+yVi%)Z{KzeJY1crQy5t`wa&8>BcWOuUG{&Jfy+Kp&d?)FplL1Op}EYU+?3`qv+y3{Se|R(Quduhc&0o*)Sq+1*1ynCJ}1HDCbjmNu`7frRCm8e#ERW!jKeY-Hl#kDI77epGzN1IHd)68WZ{-uC4Ni9KeHe->2U!S^wb%51$*;p1g=!lII05-5O(q1k?-+89Yh7q#B*OldtOTTwTZPec#hO%4~t?x_ffeM57byfL+V#ixR(&}M+fkqi!UtUg%5=3d<mf`<mN5{=TJGFil1=_erYsZ?T;;rIXBBr`PW7=$K9w!bUVY?Q<e(>8%)IWTT$|P38H&deW#r~*oSj=Qqg1f;ny);)p79B#Of&>&X2-$mWTP0?@ckBraHtx5*9qduY=@syGY6u#TelI3nZRT_G<_pjDtI<@u!kT<9TO%ejmvq749GT#%A}NTTrA4<#61r&!&A>YZ5-TIunU&Ma!RNhRDRNvqbvQaBiA~`|-VtE<vFFTM$psbNApm;gxC%UumVTPuOW1&2pzTvF}F)GCFjx{rr0s5OsXxbhW_oLcq~M3NVk0r*AcCA@+!oG}U(u1nQYHE(bX@k_A<!ULM5(H%yYTu0{?1<w-dIoKti?&TD(dS;L;GEVMMK^_&T(hi%KY*1O8Oy~oa{s1IbJ<_GR2U9QQW*7z1gRSCH?H={l+{{Nfb5Gtq2Rn!FTx)))l+&Vd9Oj|Tf;5(@G(;aO_t7zP=ANKD5XA+&Z*vfHZKrT%1jzlQ@2cwXN9pA+|ebSAL%dviX+jDbuctOXf2cLh!-3_%aIap!E1Amdj)CZ<L!mmJ8b&1;fI(R9OdqplrIfCIt99x>N57D2o#VkrR^%ulWj+)Y>CMo!>u=?N<G0d|dSH}?eH#$fG9cuVnnigL`D%{Q5xbb^dPaKb=$`t}(z4l%${uB3-fFt6vzA*CvLJHrKq(GHgLp)EE(XoOT_TEj9uIlytFU6PpQ2Y*pgO)!7*|>nK$3hK^=g_oTw7i*uEpfRxtHV)2?a?sX;;cCzyVMJ3vK==46P;dcyYL&sscpxppEsk9q(iXkc>b+8Qn2b4#F04dyiJ3D7VN~9c5QuRtOVZ3`OV3~Kkpwj1Hp_vwHA4}Is#pssCdg>(?3~_f4m0Y#|N-StuBt4hIA03=(dL6vIe8zMn$ItAmSg+-gWez$qejQ`z9wr{0=-sTfb($@?#7XFc%Mfx$Wdk7NR)yMYVv@3v&#z)@$YtN+3S+2Rjh>Mos>*`3#seqTw}(qlBcOjU)QB@oN6VOsZ^XZ#4TeM4D0gTF2`sE;hgf-ozcWp=$N<zP{=`Flls4oiET&NcOZfR75{WH1$9IwQ%RA=gurOzSD7-5|<0FOv4t9VriSft)fQ~Q)-@!j<p{p3!3~t=;IweeoH}vd+iv9PBZ;Ea~pVP!K&s=Vo^%t>+I!sO?{Au%lW}~rjz)GQ)@>ZSObI@Zxi+Ylo@F2e_!AI1&LWnc*A2HO}d>d^w7JE?or<l`8}#JaT?981V5PPLQB&g)|qjom=qD2P%pThXl9t3%YfTIbPK+QnV8Rlby>B%)h9>^iQW{y?|gfs?5HQob{gByd3fJ_r>}SQW5n1*Vk1i>fzz&@V48+hk@+w6I!6+qZPArabby~wF<4td6T3Tu5b#Br4#;4_g?2=@XFQACo}zfH8`MJx3!|94i9O~7<D9sUid)8a`Ts5=84YZ@j4u~sK^pz&54nV2LOrg{fEDaN|JFFEn{WVa9Qa{=)D`iOidn#G5g*TS{rHXFEiuxwqHMofKfCw56v)R9kn&Q?o|&<F>@4Z-;PZlxI6J?>FQFcS=gy2agZm>^g4VE_Z+L*rQi6_-SX%M_2Ja?aRrTNbC1S;&W-O(36vsucj@@Csg;jW*2?tHt3(oiqFT|kRQX60C@_!+Og}4}A3b>tN=OZm;_#Ir+pVT6mwSkZmuD(wQRqhUi-h?akjNZV%B+#cT`C)QRlfNtw1ibLT9XG!}l7T2ltf|9zNeQkW_%ACD&;y=F2Uns87OX7V>9u1fLZxsQje=CLJH!O0ymvdCG*9NX8MTjQ0YyoZ(-^h>W8e~F1*5_yb$S15?<W_?vpPQt0R8A#mg~l*@N!3QP{)@HoWYPIuN8D>gbOWBYn%eSekH_GO~5VDeQ{7)N3Sp3_#HlN;N|`x$pPuB@N*5W1bW6LYJXC<WG4KPZRu@er10-{VS_sINS=Ic{LoYukekqQ4M$btQ-~77ANYN7cHW27_<$$e{GVCgeUeG)fUUrXcx~nU(E~3iG-YV}ig#`P5*~^;W$X0=xPMOLFGjw>iaK#>|EBJ*!iMdzhCf#7`xc~vgo!rL|H7})48x+hnzsbCe{xj&n+5!^1kEhW*$+q0I%5|7{-ST+j)Q@orw%b-rt|BAucMAXk|1tc*H7VvN@N(_M(?ty!X^mua83Tn75=7Vj~VC2Zvq2@KgjGRxBgKvseQv}&YJ#ueNlQdWPUA7ji2T|S8=_1^b$oL<~i&K5oX}_VKQ}%zJmJT2_mxj6}7+M(hKu-JoV@8y=&dNrvLl@0<1yZ+WTu6?1ulr|4t+}JO30N2byrjEYXi#vJC86H6QJM&JXoNzu3Z4K)NP1{!@Kl@G^L^djG${mTzW4{?GcnYA`3yQv_%I^Sic1PP)<8=o7nbrM@n%tUs3tfTuPDzroyGkl^!D&&(Rr`q>Wn&9H9+2D1YpKdboxOuJaD+Hab8!bP7!2`TvVGA4HGc>1zFoc_YE9A7wUA|3OU@I|d{+N$}h-;tg&8Pmb^g}c|+*skdq+>mwo-H#&|-F8MAx}MCguu5IKzoKfNArQmidqXTO6uuRo@-k19i##A-ti&hGT)8fm<7TeD@2mFzou`TB(zNl%L~bWrjJ_}*`rf}X^*JLpyk?{RM-<%^{+QM*>aZ1g<&}HEOvljS*R~&fML`r<6>0A;Ia;I7@^qMQVVQ6nX?)Xrf3n<PGRxJXkzLM*vI}1==O22rhg7_8@)n$>gr|$F*DVRUoy<&E@f%YVb8%MRT!~EPyHmf%i;DjMHE8{Nyjbhs`QLt4^Mt)`0GU8b_d6$2x&*D#=K)gbUd1Ro{U;!WMc3dPhYl{h`GG%AV$5Y?#W`@$07|WI&HrVC-K;E#Epf(C&_th_k&sGLCtoANe-TCmY=t%W4({d|%1<&4Ktp8K6Z(z$T_owgvc~|kK)XL1h`$~*3oiUx$m6_zxBnxc%B0%2?Cefd?2c%k`Hz<QXE5PGt%S&LsPDhHJ?B4Hs{A?"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
