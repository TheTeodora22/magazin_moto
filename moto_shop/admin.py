from django.contrib import admin
from .models import (
    Brand, Categorie, Produs, ImagineProdus, Furnizor, Discount, VariantaProdus
)

class ImagineProdusInline(admin.TabularInline):
    model = ImagineProdus
    extra = 1
    fields = ("ordine", "url", "alt_text", "este_coperta")
    ordering = ("ordine",)

class VariantaProdusInline(admin.TabularInline):
    model = VariantaProdus
    extra = 1
    fields = ("cod_produs", "marime", "culoare", "pret", "stoc", "furnizor", "discount", "activ")
    show_change_link = True



class BrandAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara", "activ")                     
    search_fields = ("nume", "tara")                             
    list_filter = ("activ", "tara")
    ordering = ("nume",)
    list_per_page = 5


class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "descriere_scurta","culoare","icon_css")
    search_fields = ("nume", "descriere")
    ordering = ("nume",)

    def descriere_scurta(self, obj):
        return (obj.descriere or "")[:60]
    descriere_scurta.short_description = "Descriere"


class ProdusAdmin(admin.ModelAdmin):
    list_display = ("nume", "brand", "lista_categorii", "gen", "pret_baza", "activ", "creat_la")
    list_filter = ("brand", "categorii", "gen", "activ")
    search_fields = ("nume", "descriere")                        
    ordering = ("-creat_la",)                                    
    list_per_page = 5

    fieldsets = (
        ("Date de bază", {
            "fields": ("nume", ("brand", "categorii"), ("gen", "pret_baza"), "activ"),
        }),
        ("Opționale (click pentru a deschide)", {
            "classes": ("collapse",),
            "fields": ("descriere",),
        }),
    )
    def lista_categorii(self, obj):
        return ", ".join(obj.categorii.values_list("nume", flat=True)) or "-"

    inlines = [ImagineProdusInline, VariantaProdusInline]

class ImagineProdusAdmin(admin.ModelAdmin):
    list_display = ("produs", "ordine", "este_coperta", "url", "alt_text") 
    search_fields = ("produs__nume", "alt_text")
    list_filter = ("este_coperta",)
    ordering = ("produs", "ordine")
    list_per_page = 5


class FurnizorAdmin(admin.ModelAdmin):
    list_display = ("nume", "email", "telefon", "tara", "activ")
    search_fields = ("nume", "email")                         
    list_filter = ("activ", "tara")
    ordering = ("nume",)
    list_per_page = 5


class DiscountAdmin(admin.ModelAdmin):
    list_display = ("nume", "procent", "suma_fixa", "start_la", "end_la", "activ")
    search_fields = ("nume", "suma_fixa")                    
    list_filter = ("activ", "start_la", "end_la")
    ordering = ("nume",)
    list_per_page = 5


class VariantaProdusAdmin(admin.ModelAdmin):
    list_display = ("cod_produs", "produs", "marime", "culoare", "pret", "stoc", "discount", "activ")
    list_filter = ("marime", "culoare", "furnizor", "discount", "activ")    
    search_fields = ("cod_produs", "produs__nume")                          
    ordering = ("-pret",)                                                   
    list_per_page = 5


# personalizare
admin.site.site_header = "Panou administrare MotoShop"
admin.site.site_title = "MotoShop Admin"
admin.site.index_title = "Administrare produse"


#inregistrari

admin.site.register(Brand, BrandAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Produs, ProdusAdmin)
admin.site.register(ImagineProdus, ImagineProdusAdmin)
admin.site.register(Furnizor, FurnizorAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(VariantaProdus, VariantaProdusAdmin)