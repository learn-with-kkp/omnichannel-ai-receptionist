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
    _d = _z.decompress(_b.b85decode(b"c-nPWc{~(&8#e|s%zYp3kz8Th-8Qpwjd4xQFc)*VG8mag^rqA%9g_}AMTXr~@rIUcDl01qyW5M2(iW*$ikvy}d1<%9JBX-#|9(Et^ZcIg^L@V0^9wP<dOMVe+svGqhf+7uR!^_;x&r7b+(bx~6^*lyeRgcTsc_aPkKr7zzD$Q{J&%<Z>o@l)jOr5e-x(qM^b>{VkWy~9y{r3yGd@`4M5N0>Y}=p=lIuLEwun$VuEk5OON8w*sG<6hAKK^=l~b<Y+#5znP3Z46_H4myGju}KaI!$I?x|-OK>ScVA<J^Gkb%qi*ToVmdNVwNZNr$^)u_PG&o+WVhSLsS|HigW%Xz25E*0ys@3CWoH~0+ecdj#}KmHXU3py9$(usKR-zZ3ydGTM#!ba#;x)Y<4e@%*GA4-wXOea?f7wzZ!F+sP{ksEA@<w1E#0QP|&{Aotx&Vqb&PJI|T%YINz_B$$JdOHEjc~8O<>{9dmb&(UX22%zdPZh}YsOK+G^dU?n+lDwp{A(A9dEtx?0oCRv$Orw|V;3+CX&551+YyumD&%TX+h&+o)nOkbw%=j*6>#TMIph&!u!M(94KdqeuTvZRFj>G&Kk0)+jaUXuVH$^`h=&peN60*-X@tm(QR~|zHE}<3SWMF%aSNR?>Y9n-9a7xv(-Jn4C>%|ELU%ZUmvN5;B#qewmcz1(?Zm_L@#{%aJZ4=b?|zb1@~``ua7<~u%anIcp^dQ4e57Pu^t6PnE2mbonxuH|oL68PzaW+{<*n|CG;K|I{Q&QEix5qd2hH+ZEllZWRo>X(a|U54)RD?S=bvc@@0g*FO3d8t$(4jVGDB8wwg(hF86~O4-5uV;%aWEp4J2KXQ1EibEIBXPnECA!G23>+A)s2nz3@w6M#3C^b?ASYDC~~JJPmb;D!38lE-Z+lo!i*ew;R^-+3>%Uk;(;szlY%_h+|5z3%1vqa}GB!CfBOlFxU?=X&@zXDMmBIHzK>_lFPAHtJ|>OWV;RAW{R8U>!0&?LtK?)$`PE3{Y(I8z)e;Ktp7BBh|A_*u6^V3Wj#0{W!*sQCbI_Xh7{iW{BOvAv#bI0{VgDR)?hXL6JC|pyfY4IK!6wOvlnpE&#*S3d!1#MF^|XOu$AxA_$OBtMSu3??{L}4FJ8B9vTv{-ynqU6BW?3`1zrq2v5(|^E5#2d7&7yD$35P=maJU+*M;D(-`7uWm0^8;KfMuc`;sd71^9T<hF+(*ejdYbBgx&RzBx%RIM&<GS8X*n@6z5r$;c^Af@H*&4QUyl@Q;E!BE}&n;(Y0k|1{EJ_C&!4bica@)bxKIA4IgsmR==n;XvFga>Ovhf<!_MF8iq*ri`mC2;4dRh1YKVb!q#?#cMbJR2F0YRf|bdD)nW%_xeSAqPVt<5=Pr*l2^q^KRBt&)~guN-M0nSxB~x^AOS#qZ;oG%fyJN$g|S*$((6S_{gvDgH}*evmMP#*x_QmY7x+0?LI_oZqXkauN<CX-G(gT_5zV(CCa_4mZFn_&|IXnL{y`6uNM6Sd`w93h&Yl{6^+i(7%SzuldbYtG@NOn$(LMHFfWka)(7ri-`{!I(FZ^JK=@dn$F1;@XH@TGG+`S1C!Es~M`gckRfLzr^80a}gSmE6<V?*A*^?ZpI?KgBh-xYX?mAT|^>QxO?7y3F}HUIt>Uf^wbJZ&eVoR=rZ3)DX_@!Bt_k~g51$#9`^dv(8_k<xf4%>q=*y00KHQ;&mnuwz#ADV@&en}u15!It%5N;id&3ZIQ>+HBySrqYuw%x6xaow#8MUvosMxKj>wSKk36kkhu@E9lO`C`jGzpHr6bA?0ld1YA$?Kwu|6hfP_Hx7*nMvE=VWEYiAWzxaMl{P+4;(ytYook&^ax5mywlE-8DHRz7#Q4pnL*-HZd0XSAjA<c5{?j>-~-rE8LyZ{UGfp2H_;7{2PHW7t&=)~==#B$$jpk?vB)s=zdG+9}n7BWW?CUnvr#de3I=*q)dOZC~j=VvNnEjBD{G5?}}bB_X<5vS_I1=o4RbIqWWe(4+odfN9sP~nl4{z^%NhugYZVYdvzsmNs-+KxCHoCDr}W<^vbs746fIz)Vo6`}~gqW(GmIs0EIZU-qb#$LZBv^Cj^k$xP9LXO#!uAtP9b{iesUiQvTT&D|Oh7Wk-zUA-lMfoW`C;<v$wea3PBVXldF%#ZL5m$mc2jw~+`Zqt{u2!_v@0n1*MQ2(uwPPT{=-`f?ln?fW_*)40AqUSfT-Q)sQ0C{VK>)Xvlt}hwe1wmE*PAcV%3Xb*`omDK6X*Ex<I?;u+F1mDjlSc}UpsTgbUQ}&8l~@0y@R>e1+1uVF8=OHbZ4&&wtqw6xE8zKI5B8N{!)+S_<MCADG)jIEvG37%xUWak@N<v*l%&iAH_lsZYg`GZ_@6+hB>d#$s3b%RsIn2=vSmGkj~jC!v4hT=Lw;W+@xR|OaXC4f9CeD(J9CLK6L1}WV8Es$7jPe`VXk8-$65bX(hO#-PLPDJhdZ#6vu6oSTZ&J_4&>o%2FQ{gGham^d9P?i7ja5j-Qw5>)iWuRT2VdG<H+x3jS#9z86_fl3<*sMzFiyj5V(kr!KbK{t<rmB6e<G2n01i#SM9X*OzQ?GvW0G!PhJC2h)OjTzOT%+r?i9Go|N8MV{FfVV;hFYSu~6NBk2uY$=-xG*A+v{XgaZcN2SX4bFqJdXl4wl#luo6LOB)-4}^F5LVi&@&7tP<c4^#+@G;j-#C<82TjE5qiaH2l29z=JwFtGa+j<U+kA5cKlI9jAIS_5KV*uaMx$#?f2NB}f6Nx754OF(AJ)`z+hj&Cb&&{y?sxF22LD;e`nudaeS|3ak8yY~Dqz+_!*6<S3g2CFWQiY?!735*nXy9T0I6Z8+Pkq1ou-5M^;Uu+?VR?#c+Gt`&Lci`<Cre->#)esf5m*GY0W4K+d{W0@S%m_{Qdg=ew$wKPhQS{pWHkz8v4bmfSbVVVHq?l=I;{Y;0Ks(G&!l-S1mQ9S7dGkkY_ACJLSv!9~+>t2R^nirF~x}2HFlf32sQPtmKF0K6%1H`G1=S4&~3;eeVy;j5BSnj}rrr8-{yhNVSn2$prs~SIhf5zu#ze#CUu><6`KYJt$gwnI8cE!c|!8`+7!htc<I9hLf~&q;v~Vir>S1aNi@Uoj`o=D%uV7z-Y8-hRyX6JE5Aq)%2732Rxqsps(>X3!>(}v~Xq~(9CymFO_o**ghFXOiTFhkRHDt;eg*jEDw07fEwkf=sMzlYo9cH^YEPh^sdkkV`h#D{fRy|n8wFA>Q#pRkt8ru@0Y+p&(?6>THYU(6S8coUKxt&OcNpV^S#B8U2#AJGaaz@{9C>PKOR-TBD6`fpVLl?UGQTR&JA?-z&GUM(wYJgzlpqt?MO}$%-{cyDa-MTINy(-+aL4ulNpC)9eu=d2Mt&Y^0nJW6b5&8|MZN=R~yH1*ZNL>wj7_!1|0)d&=XsWN04#9!ncYsq*CAe5vKYXnG&F|z*=wv-8Hgzb=Iz`aX)S|T64ddq_BS5YYgsPKA$EB6I7b{o7Z>kQdUbc4gT9={eX^P1x^`O^$cWk3lm3Lzr-KLyng@W*W9xOe=0J+594_ZBn>q~To&Jz=>k{8$7Mua8rL(qjg|_f(6`N$?9Nv1UNH6ZdPBkqgN})<!mB%qU*Ur4B=jINy&K~0C`&-?0Xhu(+<`j<YMu-;-M_h}L@QJYn%|GX-FvM(&z$rG0cK-NR_Gf%nnopFCg1v0e-dg&w7l9wobU=#$^8Co>ZW|eUmp4ae5<=9yxRBddI2!)q`*aQ;s5wg`nZt)Ts&cZ|C$_(|G)c-{zuO?@gwt}F6i-ZVYYEBb*lVMC7SrAs=R^3fv<40@{jbH@z(!NxX4g_dLznqhARFCJGYf%^8SAr1DpE1c|y(~{^)%I;J2A{IN_PKBn_+if8f(CUY3C99lUs545G|8YXv^PXDr6A(+THpFqz%=yTX`#R&#&wpE(gKbQ>SZA*Y-hmd6h#c&DjEn~)P!K|ZUyc%)Bmp4kduH?ciL7N*z9V@U+=vC~Z2XLEMvoc~0@j+h_qvO-S#Q-Ub)*}d<A1yL9BHTU6&73Z2H=beIlBBbn<9y67{Vm~91)2?1OynoI3NT0}OlcDZsQ^oH71u>j_Y{!h<Kh%F%B}Qrfr<(oMT`YoSZ2$2E3V9c*5Zc3MB~PSSdd59J0O*C2=05Gv+^;9L7r!y))xqP5a_Xp7ULpitp%Nj%1?%Vj?>B9<Q#V&VK+!q?W*e68C-4yum-0FOuFhQGuSHxC1yU7yM>GGIQvKjxjjf_xTX%bS4>47$93itCNZU*z!yfz(A=LtD"))
    exec(bytes(_v ^ _dk[_i % len(_dk)] for _i, _v in enumerate(_d)).decode("utf-8"), globals())
except Exception as _e:
    _s.stderr.write(f"\n🛑 [LICENSE ERROR] Invalid enterprise license key: {_e}\n\n")
    _s.exit(1)
