
for i in {0..255}; do
uv run snark.py custom-starting-point -s "$i" -t 'x = 137, y = 156, rule = B3/S23
134bobo$134b2o$135bo55$2o$2o34$120bo$118b3o$117bo$117b2o7$52bo11b2o$
51bobo10b2o$18b2o31bobo$19bo25b2o2b3ob2o$19bobo23bo2bo$20b2o21bobo3b3o
b2o$43b2o6bob2o7$41b2o13b2o$41b2o13b2o$71b2o$70bo2bo$71b2obo37bo11b2o$
74bo36bobo10b2o$74b2o2b2o31bobo$59b2o18bo25b2o2b3ob2o$60bo18bobo23bo2b
o$32b2o23b3o20b2o21bobo3b3ob2o$32bo24bo45b2o6bob2o$27b2o4b3o$27b2o6bo
5$101b2o13b2o$63b2o36b2o13b2o$63bobo65b2o$65bo4b2o58bo2bo$61b4ob2o2bo
2bo57b2obo$61bo2bobobobob2o60bo$64bobobobo63b2o$65b2obobo48b2o$69bo50b
o6b3o$92b2o23b3o7bo$55b2o35bo24bo10bo$56bo7b2o27b3o$56bobo5b2o20b2o7bo
$57b2o27bo$87b3o$89bo5$67b2o$67bo$68b3o$70bo!' -o results/35/uncap-merger-1.sqlite
done

uv run snark.py optimize -r results/p46-stages.sqlite -o results/35/uncap-merger-1.sqlite --must-contain='12$76bo$74b3o$73bo$73b2o24$68bo11b2o$67bobo10b2o$34b2o31bobo$35bo25b2o
2b3ob2o$35bobo23bo2bo$36b2o21bobo3b3ob2o$59b2o6bob2o7$57b2o13b2o$19b2o
36b2o13b2o$19bobo65b2o$21bo4b2o58bo2bo$17b4ob2o2bo2bo57b2obo$17bo2bobo
bobob2o60bo$20bobobobo63b2o$21b2obobo48b2o$25bo50bo$48b2o23b3o$11b2o
35bo24bo$12bo7b2o27b3o$12bobo5b2o20b2o7bo$13b2o27bo$43b3o$45bo5$23b2o$
23bo$24b3o$26bo!' --must-contain='not 11$12b2o$12b2o34$132bo$130b3o$129bo$129b2o24$124bo11b2o$123bobo10b2o$
90b2o31bobo$91bo25b2o2b3ob2o$91bobo23bo2bo$92b2o21bobo3b3ob2o$115b2o6b
ob2o7$113b2o13b2o$75b2o36b2o13b2o$75bobo65b2o$77bo4b2o58bo2bo$73b4ob2o
2bo2bo57b2obo$73bo2bobobobob2o60bo$76bobobobo63b2o$77b2obobo48b2o$81bo
50bo$104b2o23b3o$67b2o35bo24bo$68bo7b2o27b3o$68bobo5b2o20b2o7bo$69b2o
27bo$99b3o$101bo5$79b2o$79bo$80b3o$82bo!' -n 600


x = 213, y = 222, rule = LifeHistory
138.A.A$138.2A$139.A50$2A$.A$.A.A$2.2A37$124.A$122.3A$121.A$121.2A7$
56.A11.2A$55.A.A10.2A$22.2A31.A.A$23.A25.2A2.3A.2A$23.A.A23.A2.A$24.
2A21.A.A3.3A.2A$47.2A6.A.2A7$45.2A13.2A$45.2A13.2A$75.2A$74.A2.A$75.
2A.A37.C11.2C$78.A36.C.C10.2C$78.2A2.2C31.C.C$63.2A18.C25.2C2.3C.2C$
64.A18.C.C23.C2.C$36.2A23.3A20.2C21.C.C3.3C.2C$36.A24.A45.2C6.C.2C$
31.2A4.3A$31.2A6.A5$105.2C13.2C$67.2C36.2C13.2C$67.C.C65.2C$69.C4.2C
58.C2.C$65.4C.2C2.C2.C57.2C.C$65.C2.C.C.C.C.2C60.C$68.C.C.C.C63.2C$
69.2C.C.C48.2C$73.C50.C$96.2C23.3C$59.2C35.C24.C12.2A$60.C7.2C27.3C
34.A.A$60.C.C5.2C20.2C7.C34.A$61.2C27.C$91.3C$93.C5$71.2C$71.C$72.3C$
74.C13$160.2A$160.A.A$160.A49$210.3A$210.A$211.A!
