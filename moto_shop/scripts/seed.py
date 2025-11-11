from moto_shop.models import Brand, Categorie, Produs, Furnizor, Discount, VariantaProdus, ImagineProdus
from datetime import date

# brands
b1 = Brand(nume="Dainese", tara="Italia")
b1.save()

b2 = Brand(nume="Alpinestars", tara="Italia")
b2.save()

b3 = Brand(nume="Shoei", tara="Japonia")
b3.save()

# categorii
c1 = Categorie(nume="Casti", slug="casti", descriere="Casti integrale si modulare pentru protecție maxima",
               culoare="#222222", icon_css="fa-solid fa-helmet-safety")
c1.save()

c2 = Categorie(nume="Geci moto", slug="geci-moto", descriere="Geci din piele si textile pentru protectie la impact",
               culoare="#0055AA", icon_css="fa-solid fa-vest-patches")
c2.save()

c3 = Categorie(nume="Manusi", slug="manusi", descriere="Manusi de strada si sport cu protectii",
               culoare="#AA0000", icon_css="fa-solid fa-hand-back-fist")
c3.save()

c4 = Categorie(nume="Femei",slug="femei",descriere="Echipamente moto dedicate femeilor",
               culoare="#FF69B4",  icon_css="fa-solid fa-person-dress"
)
c4.save()

c5 = Categorie(nume="Bărbați",slug="barbati",descriere="Echipamente moto pentru bărbați",
               culoare="#1EECFF",  icon_css="fa-solid fa-person"
)
c5.save()

c6 = Categorie(nume="Unisex",slug="unisex",descriere="Echipamente moto potrivite pentru oricine",
               culoare="#00AA55", icon_css="fa-solid fa-helmet-safety"
)
c6.save()


# furnizori
f1 = Furnizor(nume="MotoGear SRL", email="contact@motogear.ro", telefon="0722123456", tara="România")
f1.save()

f2 = Furnizor(nume="RiderStore", email="sales@riderstore.com", telefon="0755123456", tara="Germania")
f2.save()

f3 = Furnizor(nume="TrackLine", email="info@trackline.eu", telefon="0040123456", tara="Olanda")
f3.save()

# discounturi
d1 = Discount(nume="Reducere de toamnă", procent=10, start_la=date(2025,10,1), end_la=date(2025,11,30))
d1.save()

d2 = Discount(nume="Black Friday", procent=25, start_la=date(2025,11,15), end_la=date(2025,11,25))
d2.save()

d3 = Discount(nume="Reducere lichidare", suma_fixa=150, activ=True)
d3.save()

# produse
p1 = Produs(nume="Casca Dainese Sportmodular", brand=b1, pret_baza=2200, gen="unisex")
p1.save()
p1.categorii.add(c1, c6)

p2 = Produs(nume="Casca Shoei NXR2", brand=b3, pret_baza=1950, gen="barbati")
p2.save()
p2.categorii.add(c1, c5)

p3 = Produs(nume="Casca Alpinestars S-M10", brand=b2, pret_baza=2450, gen="unisex")
p3.save()
p3.categorii.add(c1, c6)

p4 = Produs(nume="Geaca Dainese Super Rider", brand=b1, pret_baza=1800, gen="barbati")
p4.save()
p4.categorii.add(c2, c5)

p5 = Produs(nume="Geaca Alpinestars Stella", brand=b2, pret_baza=1650, gen="femei")
p5.save()
p5.categorii.add(c2, c4)

p6 = Produs(nume="Geaca Shoei Touring Pro", brand=b3, pret_baza=1720, gen="unisex")
p6.save()
p6.categorii.add(c2, c6)

p7 = Produs(nume="Manusi Dainese Steel Pro", brand=b1, pret_baza=650, gen="barbati")
p7.save()
p7.categorii.add(c3, c5)

p8 = Produs(nume="Manusi Alpinestars Stella SP", brand=b2, pret_baza=590, gen="femei")
p8.save()
p8.categorii.add(c3, c4)

p9 = Produs(nume="Manusi Shoei AirFlow", brand=b3, pret_baza=520, gen="unisex")
p9.save()
p9.categorii.add(c3, c6)

p10 = Produs(nume="Casca Dainese Urban", brand=b1, pret_baza=1200, gen="unisex")
p10.save()
p10.categorii.add(c1, c6)


# imagini
i1 = ImagineProdus(produs=p1, url="/static/moto_shop/imagini/casca_dainese_sportmodular.jpg",
                   alt_text="Casca Dainese Sportmodular", este_coperta=True, ordine=1)
i1.save()

i2 = ImagineProdus(produs=p2, url="/static/moto_shop/imagini/casca_shoei_nxr2.jpg",
                   alt_text="Casca Shoei NXR2", este_coperta=True, ordine=1)
i2.save()

i3 = ImagineProdus(produs=p3, url="/static/moto_shop/imagini/casca_alpinestars_sm10.jpg",
                   alt_text="Casca Alpinestars S-M10", este_coperta=True, ordine=1)
i3.save()

i4 = ImagineProdus(produs=p4, url="/static/moto_shop/imagini/geaca_dainese_super_rider.jpg",
                   alt_text="Geacă Dainese Super Rider", este_coperta=True, ordine=1)
i4.save()

i5 = ImagineProdus(produs=p5, url="/static/moto_shop/imagini/geaca_alpinestars_stella.jpg",
                   alt_text="Geacă Alpinestars Stella", este_coperta=True, ordine=1)
i5.save()

i6 = ImagineProdus(produs=p6, url="/static/moto_shop/imagini/geaca_shoei_touring_pro.jpg",
                   alt_text="Geacă Shoei Touring Pro", este_coperta=True, ordine=1)
i6.save()

i7 = ImagineProdus(produs=p7, url="/static/moto_shop/imagini/manusi_dainese_steel_pro.jpg",
                   alt_text="Mănuși Dainese Steel Pro", este_coperta=True, ordine=1)
i7.save()

i8 = ImagineProdus(produs=p8, url="/static/moto_shop/imagini/manusi_alpinestars_stella_sp.jpg",
                   alt_text="Mănuși Alpinestars Stella SP", este_coperta=True, ordine=1)
i8.save()

i9 = ImagineProdus(produs=p9, url="/static/moto_shop/imagini/manusi_shoei_airflow.jpg",
                   alt_text="Mănuși Shoei AirFlow", este_coperta=True, ordine=1)
i9.save()

i10 = ImagineProdus(produs=p10, url="/static/moto_shop/imagini/casca_dainese_urban.jpg",
                    alt_text="Casca Dainese Urban", este_coperta=True, ordine=1)
i10.save()

# variante
v1 = VariantaProdus(cod_produs="DAI-SPM-L-BLK", produs=p1, furnizor=f1, discount=d1,
                    marime="L", culoare="Negru", pret=2100, stoc=5)
v1.save()

v2 = VariantaProdus(cod_produs="SHO-NXR2-M-WHT", produs=p2, furnizor=f2, discount=d2,
                    marime="M", culoare="Alb", pret=1750, stoc=7)
v2.save()

v3 = VariantaProdus(cod_produs="ALP-SM10-XL-RED", produs=p3, furnizor=f3, discount=d3,
                    marime="XL", culoare="Roșu", pret=2300, stoc=3)
v3.save()

v4 = VariantaProdus(cod_produs="DAI-SRID-M-BLK", produs=p4, furnizor=f1,
                    marime="M", culoare="Negru", pret=1750, stoc=6)
v4.save()

v5 = VariantaProdus(cod_produs="ALP-STEL-S-PNK", produs=p5, furnizor=f2,
                    marime="S", culoare="Roz", pret=1600, stoc=4)
v5.save()

v6 = VariantaProdus(cod_produs="SHO-TUR-L-GRY", produs=p6, furnizor=f3,
                    marime="L", culoare="Gri", pret=1680, stoc=8)
v6.save()

v7 = VariantaProdus(cod_produs="DAI-STEEL-M-BLK", produs=p7, furnizor=f1,
                    marime="M", culoare="Negru", pret=630, stoc=15)
v7.save()

v8 = VariantaProdus(cod_produs="ALP-STEL-SP-S-BLU", produs=p8, furnizor=f2,
                    marime="S", culoare="Albastru", pret=560, stoc=10)
v8.save()

v9 = VariantaProdus(cod_produs="SHO-AIR-M-BLK", produs=p9, furnizor=f3,
                    marime="M", culoare="Negru", pret=500, stoc=12)
v9.save()

v10 = VariantaProdus(cod_produs="DAI-URB-L-WHT", produs=p10, furnizor=f1,
                     marime="L", culoare="Alb", pret=1150, stoc=9)
v10.save()
