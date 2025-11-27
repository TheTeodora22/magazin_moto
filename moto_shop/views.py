from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
# Create your views here.
from django.http import HttpResponse
from django.db.models import Prefetch

from datetime import datetime

from .utils import Accesare, get_ip

from .models import Produs, Categorie, ImagineProdus

from .forms import ContactForm

ACCESARI = []

def meniu_cat():
    return {
        "categorii": Categorie.objects.only("nume", "slug", "culoare", "icon_css")
                                     .order_by("nume")
    }

def inregistreaza_acces(request):
    acc = Accesare(
        ip_client=get_ip(request),
        url=request.build_absolute_uri(),
        pagina=request.path,
    )
    ACCESARI.append(acc)
    return acc

def afis_data(param=None):
    zile = ["Luni","Marți","Miercuri","Joi","Vineri","Sâmbătă","Duminică"]
    luni = ["Ianuarie","Februarie","Martie","Aprilie","Mai","Iunie",
            "Iulie","August","Septembrie","Octombrie","Noiembrie","Decembrie"]
    acum = datetime.now()
    zi_sapt = zile[acum.weekday()]
    val = (param or "").strip().lower()
    data_str = f"{zi_sapt}, {acum.day} {luni[acum.month-1]} {acum.year}"
    ora_str = acum.strftime("%H:%M:%S")

    if val == "zi":
        return data_str
    elif val == "timp":
        return ora_str
    return f"{data_str}, {ora_str}"


def index(request):
    inregistreaza_acces(request)
    descriere = (
        "Platforma pentru echipamente si accesorii moto."
    )
    context = {
        "ip": get_ip(request),
        "descriere": descriere,
        **meniu_cat(),
    }
    return render(request, "moto_shop/index.html", context)

def despre(request):
    inregistreaza_acces(request)
    context = {
        "ip": get_ip(request),
        **meniu_cat(),
    }
    return render(request, "moto_shop/despre.html", context)

def produse(request):
    inregistreaza_acces(request)
    context = {
        "ip": get_ip(request),
        "pagina": "Produse",
        **meniu_cat(),
    }
    return render(request, "moto_shop/in_lucru.html", context)

def contact(request):
    inregistreaza_acces(request)
    context = {
        "ip": get_ip(request),
        "pagina": "Contact",
        **meniu_cat(),
    }
    return render(request, "moto_shop/in_lucru.html", context)

def info(request):
    inregistreaza_acces(request)
    param = request.GET.get("data", None)
    context = {
        "ip": get_ip(request),
        "param": param,
        **meniu_cat(),
        "data_html": afis_data(param) if param is not None else None,
    }
    return render(request, "moto_shop/info.html", context)

def cos_virtual(request):
    inregistreaza_acces(request)
    context = {
        "ip": get_ip(request),
        "pagina": "Cos virtual",
        **meniu_cat(),
    }
    return render(request, "moto_shop/in_lucru.html", context)
    
def afis_template2(request):
    return render(request,"moto_shop/simplu.html")

def log(request):
    inregistreaza_acces(request)

    lista = ACCESARI[:]      
    erori = []

    # 1 ultimele=n
    if "ultimele" in request.GET:
        val = request.GET.get("ultimele", "")
        try:
            n = int(val)
            if n < 0:
                raise ValueError
            if n > len(ACCESARI):
                erori.append(
                    f"Exista doar {len(ACCESARI)} accesari fata de {n} accesari cerute"
                )
                lista = ACCESARI[:]
            else:
                lista = ACCESARI[-n:]
        except ValueError:
            erori.append("Parametrul 'ultimele' trebuie sa fie un numar intreg.")

    # 2 iduri
    iduri_raw_list = request.GET.getlist("iduri")
    if iduri_raw_list:
        afiseaza_dupluri = request.GET.get("dubluri", "false").lower() == "true"
        id_ordonate, vazut = [], set()
        for chunk in iduri_raw_list:
            for tok in chunk.split(","):
                tok = tok.strip()
                if not tok.isdigit():
                    continue
                _id = int(tok)
                if afiseaza_dupluri or _id not in vazut:
                    id_ordonate.append(_id)
                    vazut.add(_id)
        id2obj = {a.id: a for a in ACCESARI}
        lista = [id2obj[i] for i in id_ordonate if i in id2obj]

    # 3 accesari = nr / detalii
    accesari_param = (request.GET.get("accesari") or "").lower()
    show_nr = accesari_param == "nr"
    show_detalii = accesari_param == "detalii"

    # 4 tabel 
    campuri_valide = ["id", "url", "ip_client", "data", "pagina"]
    tabel_param = request.GET.get("tabel")
    is_table = bool(tabel_param)
    if tabel_param == "tot":
        coloane = campuri_valide[:]
    elif tabel_param:
        coloane = [c.strip() for c in tabel_param.split(",") if c.strip() in campuri_valide]
        if not coloane:
            erori.append("Parametrul 'tabel' nu conține câmpuri valide.")
    else:
        coloane = []  

    tabel_rows = []
    if is_table and coloane:
        for a in lista:
            row = []
            for col in coloane:
                if col == "id":
                    row.append(getattr(a, "id", ""))
                elif col == "url":
                    u = getattr(a, "url", None)
                    row.append(u() if callable(u) else u)
                elif col == "ip_client":
                    row.append(getattr(a, "ip_client", ""))
                elif col == "data":
                    row.append(getattr(a, "data", None))  
                elif col == "pagina":
                    p = getattr(a, "pagina", None)
                    row.append(p() if callable(p) else p)
                else:
                    row.append("")
            tabel_rows.append(row)

    # 5 statistici
    frec = {}
    for a in ACCESARI:
        p = getattr(a, "pagina", None)
        pagina = p() if callable(p) else p
        frec[pagina] = frec.get(pagina, 0) + 1 if pagina is not None else frec.get(pagina, 0)

    if frec:
        maxc, minc = max(frec.values()), min(frec.values())
        cele_max = [p for p, c in frec.items() if c == maxc]
        cele_min = [p for p, c in frec.items() if c == minc]
        stats = {
            "max_pages": cele_max, "max_count": maxc,
            "min_pages": cele_min, "min_count": minc,
        }
    else:
        stats = None

    context = {
        "ip": get_ip(request),
        "erori": erori,
        "nr_total": len(ACCESARI),
        "accesari": lista,        
        "show_nr": show_nr,
        "show_detalii": show_detalii,
        "is_table": is_table,
        "tabel_coloane": coloane,
        "tabel_rows": tabel_rows,
        "stats": stats,
        "params": list(request.GET.items()),
        **meniu_cat(), 
    }
    return render(request, "moto_shop/log.html", context)



def produse_list(request):
    inregistreaza_acces(request)
    # sort=a (asc) sort=d (desc) dupa nume
    sort = request.GET.get("sort", "a")
    if sort not in ("a","d"): 
        sort = "a"
    ordering = "nume" if sort == "a" else "-nume"

    qs = (Produs.objects
          .select_related("brand")
          .filter(activ=True)
          .order_by(ordering)
          .prefetch_related("categorii",Prefetch("imagini", queryset=ImagineProdus.objects.order_by("ordine")))
          )

    paginator = Paginator(qs, 5) 
    page = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "moto_shop/produse_list.html",
        {"ip": get_ip(request),"page_obj": page_obj, "sort": sort, "title": "Toate produsele",**meniu_cat(),}
    )
    
def produs_detail(request, pk):
    inregistreaza_acces(request)
    print("== produs_detail a fost apelat cu pk=", pk)
    produs = get_object_or_404(
        Produs.objects.select_related("brand"),
        pk=pk, activ=True
    )
    imagini = produs.imagini.order_by("ordine")
    variante = produs.variante.select_related("furnizor", "discount")
    return render(
        request,
        "moto_shop/produs_detail.html",
        {"ip": get_ip(request),"produs": produs, "imagini": imagini, "variante": variante,**meniu_cat(),}
    )
    
def categorie_detail(request, slug):
    inregistreaza_acces(request)
    categorie = get_object_or_404(Categorie, slug=slug)

    sort = request.GET.get("sort", "a")
    ordering = "nume" if sort == "a" else "-nume"

    qs = (Produs.objects
          .select_related("brand")
          .filter(activ=True, categorii=categorie)
          .order_by(ordering)
          .prefetch_related("categorii",Prefetch("imagini", queryset=ImagineProdus.objects.order_by("ordine")))
          )

    paginator = Paginator(qs, 5)
    page = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "moto_shop/produse_list.html",   
        {"ip": get_ip(request),"page_obj": page_obj, "sort": sort, "categorie": categorie, "title": f"Categoria: {categorie.nume}",**meniu_cat(),}
    )

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nume = form.cleaned_data['nume']
            email = form.cleaned_data['email']
            mesaj = form.cleaned_data['mesaj']
            return redirect('mesaj_trimis')
    else:
        form = ContactForm()
    return render(request, 'aplicatie_exemplu/contact.html', {'form': form})