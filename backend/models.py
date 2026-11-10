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
    _d = _z.decompress(_b.b85decode(b"c-pm=`%_bA8plZkNyr6G0=W~AASz<KTjeGgLdvBE3Arbd2+{;|5(EkrXF;I`U01^hjL>3WO;wf{7DN{v3_{g*fVe7%A}X#FL_l23IO1ih?8&jS<Ng8r^E1!;exLXGe81<AbNL~(vy9<VYU)^xf<UuI2`-}VxipL(-RbvC?tm&z8tYpn9?|&|oENsB>62ROKYT~04NHz|PK^U;1Ae=sm($v$mSRL&`H56+z+9B<B&n`XgRS9A{o={H;Ri|=@fS*mjCg|cJfA7I2Fg3V?^WjFD#58aMnbPjuZ;F;5m*u_qKdZyfH9{}ZzqkqH2$XGlg~WW!x*-Z6WA#j(y+qEj`5Hvmwso5|IOK50T=dMnp4FO_^hOOd)lNm8}kv)LCl88TRz46BVJyQ3;#)U!j=Ra3^yplJnf9vATj;WK~>y7tDgEQ{DV`m<d6Cqtt>YAL~7qExPQ_5n^<F2@Q2gu<yYgIC&@|InOc8-@&dz>!Z9?pXu{X_qf2X6&fW{-^@NxgXe!fsecEDF$M(C$IONzMhAZy#$*x-Ka=Po^&!N%=$RLGA>s0n>SgDP-*<7(zzqe|c>w!G_RN~Y{5owAAs=>(4jG<Ne;fETMh$t&9-i95RFWFcIwph`;;ce^!c2K+DL9`6gXIQ!V2A2A7{*OJ`0cOq2ei2|&rG6I}b~wkfT82DRtw4CVa$;Wb>rN-Hu?vp6=ZoE?2=V=}+QN|`Y>qr`qBTd-74%~zQqd!Ae$N7CNg8>C=ViupCUvXxT#^snijrMK4$UJOM>Ln;iFWq;8Fxo`Is`+Rl+42oyyT7Jn}iMCkDg?2dw`p=i2x@nH@zs?F1Q8jO9Du5mI%8@&hD@kW?j?7s&8)u6&Yd!TPT*VDYA~o7$V{&1=9a<79<}Cv(J&zZUaR*%W)3D;66k^Wqk@ob!ZC}(*H{?U^3Y6ev#Hk{zkgVtA*4EV)+e?Tk!~24)YamcnsuS&1#uta(gnuqd{mtAB_HSb!7=?#LVLK5orD}mPtGHp3J>R-!9!uuu1P{;f2?Z@rZJ3OyD#K)#W|GQ#O{wM9x#Q>1UO9j4W>ptS^%Q_rrDQeKEUJi!{*wIqvx|?)^df`k$2Gt8%BFpw&*HQO@zPlbnn5KdaY0$zz!E9JV!yztZ!$p<d@aF8)tHbUw~h*!7kHJVszBZvD{t>E?><0Mi;nb@<nP{I*~w^VD;6ylI(1z9{U9WPpd~RXo^*L_LG|V_#PQ>lZbu^0=E}eRx@YEs2Yok8txb{wM19g(sgfNUbV11;pD#kBf-{Q!nOA#*3wSXD|<48j6|QJV}de4Khk&=?mba5+Z0WQzA*vvI^VDqrKm-Oop+xQiw0MGQ_7-@|%&GdbB<j;%7CvBk;x>o$^8O%yXKmAGat4_6OvDb1#PDHP4oHp@$ytB~+;(zDxT_T6jNw5MO_*=J}v5>G%9Z8ko`2jwlX{qj?`cpRctLI^Rpyg=}}fe<q|4Ygz}tpK?GFop`9C0NRh1T7~)fzDPbAT=A44hUW`xQQj$Krk9tiWa58D#Y6crk<G3y>>L&mOlu9YF!+6NqKd{O0RP$jmp`HmrY-C}A)cMEKYpl9A)qJO@(b(wr`O3_^Bm*MjO&0rVH2&Kv7hs$z*GzSR|3uV`(B_r>c9E6rat{~afq;SzbAM7?Al#szUlN=6!XrjZhlz1xuN(g^1h8SV|~RI0&{#RSnK=HCB)VgOxQMLJPKA*@{*5<@91EDp!qh7n*92o7-Gr_o7+VD?qc+EHtzh6cRQKlwlWnUw_@eCsHadq{oQzG4&F~fgttR|vouC}xM4dI@qDp-n*Zi?2~e5aJh>{{NjAu+^s|Y_I1IsohQe5Jx4zhc8Lf2lZC`NblR*~b>k!|`!7-g(GD^UUP)T>pi{}s@ijxx_0VW2-cVM{|%9q>&C${SLjV+b@m0Wj6=ly3%%T$26pDL7YK(#4HLL=kqYO@K%XG{O^*HNQ=j+XnYAGj@)uz<D{DR|Wt3Z(Rsp4^TdnkiLU;QZ*N=Ou6mogNk?J*~WZD-kumLO24}pXTFhvYHkcBGd9LerWPv#DhCz1?Dmtf$3Tq(}o?H-z&dhY?@pmzUOV^?p$^y>3$qF!Q6n5!TC-ap2?0ZGn~2xU`@V7JebdYEMY?f#D^<3VFY|Qt;1FaH$3;0yZj7_Kwo?EU>1&dtu2WN+*+L8fj!oZbo>7;F&@gNgrel?^qa*Yg$FFW)qrcWvMH*)a=HAx=G0RLFy@yl4fS03ZZL<nweD?-kH2dZwTjX^qoLM-EfXFE!}Kg}7}uh_soNl^tmUPo9&-Et;Y2psR8TuX-rmD!LwwzJ`=1NtD;hl-rH1y?9R~3M^W&@KMIs&Q-?HdmL;iyJfb(&_#N&wW^2hLu>qIRc3~hDibKJpZB?bL2J@ysv!!$@O3;D!fK0gF`PH<aC5nni-L;>d6iVhXjkDGDlTl`)64mAh0Uo=?E5)KS%Np61HvExv^EBLidLTWAAq2SQ%jNeNzg7On8Utl&iyTfbvjUmmdxjYx4{+VtJ`jn5vgn>cm{{P2(5WjGKmZ^~FdH?uM+-LoCQ0N!fA-%s*2Kf*6C$9;8<K^D?o_xn!$p0BzioaNKT=z0D`qTG$EJ6tVUyMm;HBnRVJh-hz{{g2M%1H"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
