from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.



class Brand(models.Model):
    nume = models.CharField(max_length=120, unique=True)                  # unic (altul decât id)
    tara = models.CharField(max_length=80, null=True, blank=True)         # admite NULL
    activ = models.BooleanField(default=True)                              # default

    class Meta:
        verbose_name_plural = "Brand-uri"
        ordering = ["nume"]

    def __str__(self):
        return self.nume


class Categorie(models.Model):
    nume = models.CharField(max_length=120, unique=True)
    descriere = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=140, unique=True)
    culoare = models.CharField(max_length=7, null=True, blank=True, help_text="Hex color, ex: #FF5722")
    icon_css = models.CharField(max_length=50, null=True, blank=True,    # ex: fa-solid fa-helmet-safety
                                help_text="FontAwesome class, ex: fa-solid fa-helmet-safety")
    class Meta:
        verbose_name_plural = "Categorii"
        ordering = ["nume"]

    def __str__(self):
        return self.nume
    
    def get_absolute_url(self):
        return reverse("categorie_detail", args=[self.slug])


class Produs(models.Model):
    class GenChoices(models.TextChoices):                                  
        UNISEX = "unisex", "Unisex"
        FEMEI  = "femei", "Femei"
        BARBATI= "barbati", "Barbati"

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="produse")
    categorii = models.ManyToManyField("Categorie", related_name="produse", blank=True)
    nume = models.CharField(max_length=160)                
    descriere = models.TextField(null=True, blank=True)
    gen = models.CharField(max_length=10, choices=GenChoices.choices, default=GenChoices.UNISEX)
    pret_baza = models.DecimalField(max_digits=10, decimal_places=2)
    creat_la = models.DateTimeField(auto_now_add=True)                   
    activ = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Produse"
        unique_together = [("brand", "nume")]                            
        ordering = ["-creat_la"]

    def __str__(self):
        return self.nume


class ImagineProdus(models.Model):
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, related_name="imagini")
    url = models.URLField()
    alt_text = models.CharField(max_length=200, null=True, blank=True)
    este_coperta = models.BooleanField(default=False)
    ordine = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Imaginiprodus"
        unique_together = [("produs", "ordine")]                         
        ordering = ["produs", "ordine"]

    def __str__(self):
        return f"Img {self.produs} [{self.ordine}]"


class Furnizor(models.Model):
    nume = models.CharField(max_length=120, unique=True)
    email = models.EmailField(max_length=120, unique=True)
    telefon = models.CharField(max_length=30, null=True, blank=True)
    tara = models.CharField(max_length=80, null=True, blank=True)
    activ = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Furnizori"
        ordering = ["nume"]
    def __str__(self):
        return self.nume


class Discount(models.Model):
    nume = models.CharField(max_length=120, unique=True)
    procent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)   # ex. 15.00 pentru 15%
    suma_fixa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_la = models.DateField(null=True, blank=True)
    end_la = models.DateField(null=True, blank=True)
    activ = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Discounturi"
    
    def __str__(self):
        return self.nume


class VariantaProdus(models.Model):
    class MarimeChoices(models.TextChoices):
        XS = "XS", "Extra Small"
        S  = "S", "Small"
        M  = "M", "Medium"
        L  = "L", "Large"
        XL = "XL", "Extra Large"
        XXL = "XXL", "2X Large"
        XXXL = "XXXL", "3X Large"
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, related_name="variante")
    furnizor = models.ForeignKey(Furnizor, on_delete=models.PROTECT, related_name="variante")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name="variante")
    cod_produs = models.CharField(max_length=50, unique=True)                                 
    marime = models.CharField(
        max_length=5,
        choices=MarimeChoices.choices,
        default=MarimeChoices.M,   
    )
    culoare = models.CharField(max_length=40)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    stoc = models.PositiveIntegerField(default=0)
    greutate = models.PositiveIntegerField(null=True, blank=True)                             
    disponibil_de_la = models.DateField(null=True, blank=True)
    activ = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "VarianteProdus"
        unique_together = [("produs", "marime", "culoare")]                                   
        ordering = ["produs", "cod_produs"]

    def __str__(self):
        return f"{self.produs.nume} - {self.marime}/{self.culoare}"
    
class CustomUser(AbstractUser):

    nume = models.CharField(max_length=100, help_text="Numele complet afișat pe site.")
    telefon = models.CharField(max_length=20, blank=True, help_text="Telefon de contact.")
    tara = models.CharField(max_length=50, blank=True)
    judet = models.CharField(max_length=50, blank=True)
    localitate = models.CharField(max_length=80, blank=True)
    strada = models.CharField(max_length=120, blank=True)
    nr_strada = models.IntegerField( null=True,blank=True)
    cod_postal = models.IntegerField( null=True,blank=True)
    data_nasterii = models.DateField(null=True, blank=True)
    cod = models.CharField(max_length=100, null=True)
    email_confirmat = models.BooleanField(default=False,null=False)
    blocat = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = "Utilizatori"

    def __str__(self):
        return self.username
    
# LAB7 : modele promotii si vizualizare
class Vizualizare(models.Model):
    utilizator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(auto_now_add=True)

class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateField()
    procent = models.DecimalField(max_digits=5, decimal_places=2)
    descriere = models.TextField()
    categorii = models.ManyToManyField(Categorie)

    class Meta:
        verbose_name_plural = "Promotii"
        permissions = (
            ("vizualizeaza_oferta", "Poate vizualiza oferta speciala"),
        )
    def __str__(self):
        return self.nume

