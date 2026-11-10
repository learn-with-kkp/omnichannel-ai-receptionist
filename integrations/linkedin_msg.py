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
    _d = _z.decompress(_b.b85decode(b"c-n1Ndt4HR7M4&!5qZd4P{eGZL%Zv?t6fdyCE^3+p&%qGK9kg}?6EeriL9-3%@)>jIyYmfWNW|aLUYcxmSP%O_So$DN=@1v)%DT+l^49~vfJP1ch33F`M&c=B%|0HnuUXz#7tFx8pz)49is>TtBylG=TSUvBkFWk(7o)wLA9{(yz<YZ5WEl4u^L$S@D6B)Qnvt#?L;eMm640P2SV^1b$>V(@cV{1E$p@lDC~&SO%dhYSPClu+$iZw1&a<>vFW5SFToG6!BLA{pj#lxdhklR5~L6BRk||`Cqof-W5L2!i=7HPk~B4H!@LFa$15OBf{J7WuSgRKac$fvZV&Hm*?>~zx0+l;g9T(%PSP#Gjd!tv>i#f9p=m={8>**H;aHyAIff7Eb}qn>?Y`fBQ{nD&tSAg7ntdzGT3-_C;~f19;hrA%0)o=#8^&?kKVqvt3v)vKk%6s-8O%WVv0d7E8~6?9oCGhhnRDk5lv!Cyf#4pmXKC5j=hDze6cf+T^g%p0&>H_vp_pj+Jj@Ph@``y57&5ak>U7<_4EYeP+)i~qDSWDMVje9D#}I$_LO)YpEZ>1H&Tp;vml&`ad^_7SaW^wDBI7)mE~@q8f5)D@mxMjCS943YRVAZfl-xx^Zzd}2mnC~P_6hsfhe^b;y_zw&qiS=$l^>}w4k9|$1eS|>)=QeX7wf2!4v(pNp`Z($A@<+WD8FAw5*hn5kO0$q$wkMp*>@qAJ^o$4Rc^rh23q4+(Zqlck4ISeM={!<L#EA=rd@4gu8BXvB`km3VL}n@?P!&TV$JXNP+7SgA0+A`yeT3B^};Sbf@SCf1Mntai8jDELdAUIp<PIb?*M0rx6+>%JY{T7ZE8&qdb@XBe$`u(JyFsgkLj<suc`0n<4g$rQE+Ar@Ygvdv?FlpAx_ePEXWFmwQ=qo5J#V~@GE`b%V-Ao>U_4G<GtUv>43>I^q`&J@to1bpp;83he9N^S(g5;!58o6V9^)fDY{6*rgLh&g%^N^**IwV4&As=ep|Mal>*gA-%&U_bhRhHx$PI&dsP7oSGj@T@-_GW`OffLWP+0O+@%F11{nGyK`ylv=25%brd+sskA4P@8^q_tq;VhHR^?)&)z>J?{8U=-f4ci@Jx1OQ_hwP;FQI<Rab;E(@52xt`bwUF21lsa^1V|F2-y|BLgWW)3?Ds!<(8eXM*zkG7&Qo^IXSj-zjo0+S1s}hWLx>kB83@>qnr>!8~8QoyQ9k3X)C{QOaH9#F)cJJK8rs7^cCtc#^DU;4}0|E(eOcV9)Z2guc0)G0Qf$esYNa6W8;*T3m-uz)3Nvl&T(1*?~^8E<}&^|A89A+iv`<Qqx%j)Ft=6Em+2}pR7WA~$KK>Wfg8uETaM&@IRignknse;_;%}j0qSd$Bjanbf~@}5{x?h@Vhx`Am=x|Pq4$8J!zoP!#BNC+*XJ@~dh^@nNg>BXV9c`qILG?gP(bZQX)|c>-XTbtU+W7r-3Z$&_g^=MyH<#CRey#Ik$oSEU5US>Z@fb6;;s``Z4!rdsS})de^8)b0=s9^vG)$H=EpwYwAvpN4O;`eIrav;BC+8CA+E=DACu}l=b{EJ+n4I^nag9W_ICxJ@YLs)`Ks|`XfcK#HpCV0`r<3x()@bankD^7@$q+uSWEk}8GX8Z8Q-e^btNFGq$1LyzfD0e;a{~^7n10Q4~K$WXZ_I+*<%xF#Nu4dqJ83g%xZsL!dIzHC0690`yH{n8(AQrxIMS2Do9|IoQw_O)duq$kU#%l{*E>ES@V}9wV8xa6=s)&!ffT;co*XESw*ZfVa(6%IdE_your~pFWSU?z$Ck~U(JsidP-$>?9or)B){<U1VQfl@Gehp=4o{l0#Lt(pOyT)zGNYwyg~-#On5Uc{<WW8?r(TmMI;DhE{MGQn*J>1zmbInOs{9@iFeIOm@?1D^+@C-Ucsc|7DJczM@0kxZuZaAIt&bF*mlx7U-e(X&-~AH22_>XrX`2p!jqkpoObT@WCZ=g(om?Y&V$(oK79`Oy8KrE8W%z_&|pr3Uys#4u#sPN$#EsXbm2EsFhFC!V~q4-8py1C9ez8Xwf*n#7%6%+z8nIW&Zd9ic=J(q{3ofG77+|1e;<=<*CZeCa%7&q55^E@e8p#xs>@_aasJdif^m!eT7AqZ9Y0QNG}*+eLMgIf%l$T{;8~UT5<vEk(^$=*-*n{olGKI=aM3Z#etC_5UE0$9N{|=`JKelFL1+DGf9I%9McD^F%1&rT8^&{p9r?O(8@SPh66I&Fmk#iu0#&(VMBz*It=5mzM_c9>@bL{P1~t2lX_i%L4_fZm^jRVDDoP=yz`n()X$et>&oDp;lNWlCecFmY=j;LkSuM*G1QUu9e>;GejlA4HVr7c%nGJl{Hdzqp)+`#J;rRy5U;Aq%f0s*IEEQ*#_Z4CVS57$k5+9NIEq;S_%%%AuC3eaf>2};p(woU7ma$&|0@tJjt?F;WHNF#{hx4+%B>FTv!MG>s1l`xT?qI3+f-&Un^ByHvw!Sm$AF&_7{Ya#y0qJT@xRdu>faE;;r@9DC$^OUnFlL8sK|~JY)=Gcj@Y!vw%j_#_<}(N1Ann=@vFZmwoY^M5h#VU65v|!jxcg~%o=U^C%y*Vl4;~oa2`}>;U!$J{LD}(8ByrM<anz;T<iqGl`DzB8_{<?soRsu3zgdiCw;t_g$%)hpFWy`65BuMJ%e35|;KU1%A#*aO1Y*tqBR&-q2+@V#;agt6Di*}`0cx55YiZ|RpdD5I*&_eHHAeS&h?7(w?TrvM?ZuwK^gK$(7VoU+B?*jg?4oaDFTOLd$Lo-B^?y07^`RE;Zk++aSN@}_1QO%@sxSx9WDx%{@}$;Bx>`S4Nog0}O(yXT#WJAlgg2{&{q#`=Qk7ObE)45%+ad7;EQ<PQ5KgI@2?R{~VNY$DGpx=pEJM5zrnCGn#E|L=dpr270$l?f98p5P+kN)y?eK1A3ZLfIj=GoW<j`fkuaf~5{au+S$E#D@YU3n7Ci-AJaf?>{!H#NV-1zYTaXa&b<vw;nR`~IUX`?OohxK7;cqDQ%*xhV<dn8ZV<)NJy3V#ACa6YgGWOWjWUs=He#h=fPJkL8hs)SziY@2ansznsZHg2o5OBu&5E42v$Om1eFxs_U<nAQ5_-rPp{Ko&`0s9@WRW_@{D*_!>yq`K8}253NFrG{+}|1%5v1l=>|;i$@OoUz9rk&)?CWP@eCEdSv>83;O?!d=z(Jc4<{S&3O^_l>*-l)o~6nHL<b|AXcKx=Kpy#itiisNV|iD4ZNR=PCaM56Kv;"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
