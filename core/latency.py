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
    _d = _z.decompress(_b.b85decode(b"c-mEzc}$ac7{}?jI@;2=r3X-;l%h~h<7NcqEN#JR3oW#~J>(FyFZu!#1xE;n%mQ-`mVu$hajXH+atIhPpux^~q!tlS1Vj`R0V$KzX25ij72I6*_czb?_j$h0^Zb(B2^>a$!blp9dAc4M=rR)wHd;<DDqOX^OCNDbcdb2g={8rApXZa~@2sVwZQgmXd%jT3e<SIDnimjJN}tT+K<s+KQ-~zeS4$DDhHzmg{=q7oxG3r~kY!KgIq_l9ZTx44T@mNcgSJkFEkcu}cKR^725On*@2ZfevBP$B?<w~WPH3oOTOthJ<Py@<^kJMfzWog)QBTZErdzG!-%9+DGcS+;;Wa_pC|3<CNVS>mZyiL+00lG5vTxtBRM1}E6^%yBe-&l&(yzdT(#)<B37`YAGlJZD`7cvY6n%espy-K*w1=~_$O!-b*!7PI>G#PBkQ2Qw9!~KRohsX7@3S0)F>N0+LPRa^)V+lG`?wq_!>vd3$e+qm)=JHMo|1{ZD&ry2nWW}F`GC<OQwn2SlAnKzjyd%UlDqwP&$yeGs=E+TncZfvaZv_EkZ9CanJ%3idv7GunKbX^wozYbcN4zenUJov%A*8Xzsq<4xiY^Skx?isbYUY_U*#z&J>Ic|W4^~7MZ><Dq{j!qsQMbdt*v28oGC(OfHAdMeKQHHF;|!!V%^Ta<_`YHPk%DwiK+5yp9O$N4o5@`?iJBUA;>#j#zT`nL=ugx?y7856}&L&D;`3gU@>--I6qE7^3RnaEh$T$QQi3AMTOlW)cl^p9G2%L)3BrRhX;s=h95u_<@J%Ie$v=#p`;0F{a7R(bI2wIT6gisbJ4ugpO7fWcb@DPj(LAD%KRJi#H8C41&fn%ChIS5Xpa6Nl3T1kLN>7`RtjVTs0B>|P;Q?l$l{DT*ZG5%<@M}P#EO5Ek=xzOkZ9>mb57aA4ta_0F{W*19ic0W#yB-9LQNc1voEG5XYoQ2pp<(M0;s+6@nR`vX3_&Hp79bl5>+|~qs(qKxifE5GvdSIKKbj0Qn8M!;o>g4spfo_pZ)rlt=U>^9x2?dfB(2YA)=v{gFvf;g`HpCpMg<>^u>!syUhM1Z)~sgOCc_{wCqIaeq(^_YOLzwPDw}Bg=PMx4s+L?2O&cAopv@ZR*g;S#J^f8L=Dh7<|u+;ng<HTskdD-^Xt3!Vkj#Cu`Q?x1LUSWcFWwq(oqoyJGIK5LUF>%dOlyY<Rk5otIYMf-JAM`zgd5n54z~fBC$Z*ZsD&M^K*yLmAUO}a;MAxykD1Z2M(_xnWBw+&G|4S=b-jE;4|N3Iw_*OUH}$<*0r>SWk<m%Rw0BF*YUb^BI`~m4{(_B1}`87rV9i*+G~w1>$ZI!6^>X({TLd9o&2AFb$Zj1RPdXl59n{(N2-Ge5$8|xY~&S@8~O}P)uyz)l}BlTbZ6MAKXH5~C~PRPVmca+lCRp0%@)RK{Z=%)lJ!nOA)EZ>d{nh8E7{amRt0im0ru2}EUZ!3dPg5N!={&DzF+K_S~-{UYO8RaQ_&h6r}bHww{=nSeM2}K^%<_w`f6Dy&fp#OfjIRhd((fL<StUe4stX(Po|P18ZP6ZfB6rgYiNIHu;OxCIFW``9~>%@QuHTz_6}|4|0U+dbfKU!rFj_y&I-3vVRUCqU7FLr%8^L4XqcK;LpQ8hZsfNypJa~%bhmzS9b~~QFW+ZtqxO>Z2M-vtG1`>t8dsK*c$DPNZHs;3PGp@vxgP-3o&uBI;{`FMD)-V{5%AA^_#^pFJoA0vESA$EO%`LT4EzACU*npj#44mdtdhh*I!;vCAmhr_9s(0a)%3OGR%X+@FKgI2k8m*MQ-1o9Xfk3VBkBfz;*FS4O+TyI1B^MG0KJ*5A{|V?=(UK?{TH~@9PgV=NFG8WL;eQhn2oL"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
