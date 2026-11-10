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
    _d = _z.decompress(_b.b85decode(b"c-pm<{a2Ic8OMnMo{$%K63CM`0`ej)vH-R^qCmkAQivr8AtZrFG7tfI5)5cM?7(6haBji`&dMqQ$pmL4N2MKjFxJe{l@O+eA{2%W213ACnzB*#9Cc5g({twjfc<=(>%PC&{r!Ben_4A^pkHQA*VD2W+6zc@W1?sXm~yL_*7DxxES^J=DoqJ!mCTd}k?f!E1sKa^v_A(tSXD>;UUgv+%y9%BN!m`oDmBz%a!z(;^McnCWj&M*n+o5~aen2^9}k43TLrJ`CpAQp{WAeeZVZtR`%Se}5n5p9Ix~G#QCXPeV-^`QpuEPXB9OUWDITCaaI1p!VLdC}%4uA9E+=GIG^t|8ES%+IechD@2ZQdo4hMh!%j@fkG>3mI<mYXYwkK3$>=U?Md+z$zez^Plk<^$!=5?Af!KN5>VYGKY^WQL8e5y&2dcs&q+lYB#FNpf7zN1W*BJ9kz#i9LMcizEkTEkxS?v&q7yR=Nr9AT9O352hhhJ76MMYAgAtudg!J=Qf9&9_E0zoIMjJ1cV{eFqQRuO(m?CU887&A+tuEw|lM|7hJe$3cZ5I(@j%rebGz-wWqSjFrb*-*nH)lP+X9hw>;+HmrpA3>QttRmYs_$|U<5>1igsW3w)y0X7=}{`CIvn()wpz$QS3=u^kWkK<|I2|l%!1~;qLKFkC4itP78qEA;C;$_&rwgQZoyCQi*(9tX0(JwmVnJ?vVK}5idcmqd<F<G>{3}Z$9&CpL<umx7>rRQwWMN!Fjd*5KL7Spoq*E0PXMqk+wc5)NT{H^N7v%G_2ftn+`y)B~2VyO6Z7hjmL$j$BYo0~7)KTB|$@<2PgN~{z1i|(TOGC|6ZQMorM_FK_EYc9XI6nAtyRHse}F++y;AlcwU92xUHgy?_if~g-z_peiO?t!|B?F5Tx;shqR<=j3<acVCO(f?Hys8{#j-;!ga9+Gl>%#>~zFX-ydB4XSXtPR5S0?fZ%Vs^23)}ojs81d(YCMdO|AsxW1MT%#T`J>tTGUszDZ;Ek1`VPq?{kDXd`{h|aS#C@YS%s0h+#2RIvGes*tumZ(x$qke+s}aND<+}+XdQW9+>vaZ3h|%gnGfgj579R^Uq@`Ma?S%vd#*;#@$aYDBdcGlcg$;<dacE@Bjc}(YTh=VYhFYD(~q1_&>y?`lnFk>;2@8F<a}{+;{lLmOr}|aI$j>FSu4Kq7)aB<sg`ez{vzMOC-NI-4`Y2-P=EU0u0i$Zbt|;IcTjyq*||?BJm1aT9zGU-Mf>Pj&m$(~iXt3>iKe`VwPcZg6!&xHlQ*<|xWBtqP&4n+GJVgLP>nQ&@d}=+Bg4%Ng;>f;$*}?IgV955y?WtlJ;GNwZx?ge%fQ1)P8tMQ#tb*DC$ZytbV5s&8RbtWkMQj*bo_$Avfq?J!B4j3-%9?M>p1C#<l-ZG%?PMD!3`KFo9CosdJO^q&7aTAYH6BPbp0h;X=iKHIIKmqTu&5#JyAg<{=>t^=2}_sn&<ub(`-0Bjy@=~CCD`A8uyY|i*LZ^DP!Lv`O3byMBanwgHl2Vq;n@QuibBVe-LR+a*nWytU6?Vp;`H`7@v;prv%_TEv*w8cO9ZNsN0@-@t!JDpe;VvltTb3>vTgQFJdvV=ws~clS9yNaxQJql_T`+M>&k)_a`dYS+_^g{1yyS?Ms^A*|4t1-f|~Ho6aE(#}CEIG+m8Cl9wxvrUyn{(VP~|1yht{il~;Q1l*T9U_!3F?_Cn(UM#;4KW^SfZ#$@e1WIfYF3PVB$={#a`2I=DS{gE6i-*7Abs*h_<3dP&;)hVaaXW*42rsetO-{r3-)Z`uk?AXJtr+8TL+Oa*#d!DvR=B)dp8W0lb+yH@RXGOk7pH`NCYlGTx7d3!{h6-H8Vg~@RVFuU`q$}cKl%T`-|A=?`o?sCwTVj~1jgsX5*w<`U$gS8U<?u6e;P(s(<cSVti`C@RRQw8D1WpZ8(78<WDZHbDd%B28Vkxje4odTZK#;~qQ1ur$$$AINLsu0k}(gq<$r-a*(>mCNA?3%@iIWiCky|{?9K?{>)Y^X{{S?)rlPgO<|VJHzp!;;E_OiKg!KR6sV6_&cL#kOOQliG8p}F>*T0SCtI&~;)UV)_lJgbGGd`0`$MM$G>(5zoJFZF`9&!ft|I4eHWbkgJco2W~7S@yRMG&t??*D(xcbwFU?#C%y37@;`viRO>{e!r<**fsd!5>V>en<K27tPg@avc+e5Mb2N+}nP%XU7k`cjit$%6FXS|0oZxKi!DtJ9*|mFw{AX"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
