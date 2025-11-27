from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
# Create your views here.
from django.http import HttpResponse
from django.db.models import Prefetch
from django.contrib import messages
from django import forms
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .models import CustomUser
from django.core.mail import EmailMessage
from django.core.mail import send_mass_mail
from django.core.mail import mail_admins


import logging
import os
import json
import time

from datetime import datetime, date


from .utils import Accesare, get_ip
from django.contrib.auth.models import Permission


from .models import Produs, Categorie, ImagineProdus, Vizualizare

from .forms import ContactForm, ProduseForm, ProdusForm, CustomAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PromotieForm

from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Promotie, Vizualizare, CustomUser, Categorie

ACCESARI = []

logger = logging.getLogger("django")

def este_admin_site(user):
    return user.is_authenticated and user.groups.filter(name="Administratori_site").exists()

from django.conf import settings

def pagina_403(request, titlu="", mesaj=""):
    n_403 = request.session.get("n_403", 0) + 1
    request.session["n_403"] = n_403
    context = {
        "ip": get_ip(request),
        "titlu": titlu,
        "mesaj_personalizat": mesaj,
        "n_403": n_403,
        "N_MAX_403": settings.N_MAX_403,
        **meniu_cat(),
    }
    return render(request, "moto_shop/403.html", context, status=403)



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

# LAB1 : afisare data
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
    if not este_admin_site(request.user):
        return pagina_403(
            request,
            "Eroare acces log",
            "Nu ai voie să accesezi pagina de log."
        )
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
    if not este_admin_site(request.user):
        return pagina_403(
            request,
            "Eroare acces log",
            "Nu ai voie să accesezi pagina de log."
        )
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
    # LAB7 : DLOG
    logger.debug(f"Produse list requested cu sort={sort} si params={request.GET.dict()}")
    if sort not in ("a","d"): 
        # LAB7 : WLOG
        logger.warning(f"Parametru sort invalid: {sort}, fallback la 'a'")
        sort = "a"
    ordering = "nume" if sort == "a" else "-nume"

    qs = (Produs.objects
          .select_related("brand")
          .order_by(ordering)
          .prefetch_related("categorii",Prefetch("imagini", queryset=ImagineProdus.objects.order_by("ordine")))
          )
    form = ProduseForm(request.GET or None)

    if form.is_valid():
        cd = form.cleaned_data

        if cd.get("nume_contine"):
            qs = qs.filter(nume__icontains=cd["nume_contine"])

        if cd.get("descriere_contine"):
            qs = qs.filter(descriere__icontains=cd["descriere_contine"])

        if cd.get("pret_min") is not None:
            qs = qs.filter(pret_baza__gte=cd["pret_min"])

        if cd.get("pret_max") is not None:
            qs = qs.filter(pret_baza__lte=cd["pret_max"])

        if cd.get("creat_de_la"):
            qs = qs.filter(creat_la__date__gte=cd["creat_de_la"])

        if cd.get("creat_pana"):
            qs = qs.filter(creat_la__date__lte=cd["creat_pana"])

        if cd.get("gen"):
            qs = qs.filter(gen=cd["gen"])

        if cd.get("brand"):
            qs = qs.filter(brand=cd["brand"])

        if cd.get("categorie"):
            qs = qs.filter(categorii=cd["categorie"])

        activ = cd.get("activ")
        if activ == "1":
            qs = qs.filter(activ=True)
        elif activ == "0":
            qs = qs.filter(activ=False)

        per_page = cd.get("items_per_page") or 10
        if "items_per_page" in request.GET:
            messages.info(
                request,
                "Atentie: schimbarea numarului de produse pe pagina poate duce la sarirea unor produse sau reafisarea celor deja vizualizate."
            )
            # LAB7 : WLOG
            logger.warning(
                f"User {request.user.username if request.user.is_authenticated else 'anonim'} "
                f"a modificat items_per_page la {per_page}"
            )
    else:
        per_page = 10


    paginator = Paginator(qs, per_page) 
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
        {"ip": get_ip(request),"page_obj": page_obj, "sort": sort, "title": "Toate produsele","form": form,**meniu_cat(),}
    )
    
def produs_detail(request, pk):
    inregistreaza_acces(request)

    produs = get_object_or_404(
        Produs.objects.select_related("brand"),
        pk=pk, activ=True
    )
    imagini = produs.imagini.order_by("ordine")
    variante = produs.variante.select_related("furnizor", "discount")

    if request.user.is_authenticated:
        n = settings.N_MAX_VIZUALIZARI
        viz_qs = Vizualizare.objects.filter(utilizator=request.user)\
                                    .order_by('-data_vizualizare')


        if viz_qs.count() >= n:
            viz_qs.last().delete()

        Vizualizare.objects.create(
            utilizator=request.user,
            produs=produs
        )

    return render(
        request,
        "moto_shop/produs_detail.html",
        {
            "ip": get_ip(request),
            "produs": produs,
            "imagini": imagini,
            "variante": variante,
            **meniu_cat(),
        }
    )

    
def categorie_detail(request, slug):
    inregistreaza_acces(request)
    categorie = get_object_or_404(Categorie, slug=slug)

    sort = request.GET.get("sort", "a")
    if sort not in ("a", "d"):
        sort = "a"
    ordering = "nume" if sort == "a" else "-nume"

    qs = (Produs.objects
          .select_related("brand")
          .filter(categorii=categorie)
          .order_by(ordering)
          .prefetch_related("categorii", Prefetch("imagini", queryset=ImagineProdus.objects.order_by("ordine")))
          )

    cat_param = request.GET.get("categorie")
    if cat_param is not None and cat_param != str(categorie.pk):
        messages.error(request, "Valoarea categoriei a fost modificată nepermis și a fost resetată.")

    data = request.GET.copy()
    data["categorie"] = str(categorie.pk)

    form = ProduseForm(data or None, initial={"categorie": categorie})
    form.fields["categorie"].widget = forms.HiddenInput()

    if form.is_valid():
        cd = form.cleaned_data

        if cd.get("nume_contine"):
            qs = qs.filter(nume__icontains=cd["nume_contine"])

        if cd.get("descriere_contine"):
            qs = qs.filter(descriere__icontains=cd["descriere_contine"])

        if cd.get("pret_min") is not None:
            qs = qs.filter(pret_baza__gte=cd["pret_min"])

        if cd.get("pret_max") is not None:
            qs = qs.filter(pret_baza__lte=cd["pret_max"])

        if cd.get("creat_de_la"):
            qs = qs.filter(creat_la__date__gte=cd["creat_de_la"])

        if cd.get("creat_pana"):
            qs = qs.filter(creat_la__date__lte=cd["creat_pana"])

        if cd.get("gen"):
            qs = qs.filter(gen=cd["gen"])

        if cd.get("brand"):
            qs = qs.filter(brand=cd["brand"])

        activ = cd.get("activ")
        if activ == "1":
            qs = qs.filter(activ=True)
        elif activ == "0":
            qs = qs.filter(activ=False)

        per_page = cd.get("items_per_page") or 10
        if "items_per_page" in request.GET:
            messages.info(
                request,
                "Atentie: schimbarea numarului de produse pe pagina poate duce la sarirea unor produse sau reafisarea celor deja vizualizate."
            )
    else:
        per_page = 10

    paginator = Paginator(qs, per_page)
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
        {
            "ip": get_ip(request),
            "page_obj": page_obj,
            "sort": sort,
            "categorie": categorie,
            "title": f"Categoria: {categorie.nume}",
            "form": form,
            **meniu_cat(),
        }
    )

def contact_view(request):
    inregistreaza_acces(request)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # LAB7 : DLOG
            logger.debug(f"Contact form valid pentru email={form.cleaned_data.get('email')}")
            data = form.cleaned_data.copy()
            # 1. Data nasterii
            data_n = form.cleaned_data['data_nasterii']
            azi = date.today()
            ani = azi.year - data_n.year - ((azi.month, azi.day) < (data_n.month, data_n.day))
            luni = azi.month - data_n.month - (azi.day < data_n.day)
            data['varsta'] = f"{ani} ani si {luni} luni"
            data.pop('data_nasterii',None)
            # 2. Normalizarea
            msg = data['mesaj']
            msg = msg.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
            msg = " ".join(msg.split())
            msg = msg.strip()
            # 3. Majuscula 
            cap = False
            i = 0
            while i < len(msg):
                if not cap and msg[i:i+3] == "...":
                    cap = True
                    i += 2
                elif not cap and msg[i] in ".!?":
                    cap = True
                elif cap and msg[i].isalpha():
                    msg = msg[:i] + msg[i].upper() + msg[i+1:]
                    cap = False 
                i += 1   
            data['mesaj'] = msg
            # 4. Timp minim
            tip = form.cleaned_data['tip_mesaj']
            minim_zile = form.cleaned_data['minim_zile_asteptare']
            minime = {"review": 4, "cerere": 4, "intrebare": 2, "programare": 2}
            if tip in minime and minime[tip] == minim_zile:
                data['urgent'] = True
            else:
                data['urgent'] = False

            # 5. Salavare json
            data.pop('confirmare_email', None)
            data['client_ip'] = get_ip(request)
            now = datetime.now()
            data['received_at'] = now.isoformat()

            ts = int(time.time())  
            suffix = "_urgent" if data['urgent'] else ""
            filename = f"mesaj_{ts}{suffix}.json"
            filepath = os.path.join("Measaje", filename)

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                subject = "Eroare la salvarea mesajului de contact"
                message = f"Eroare: {e}"
                html_message = (
                    f'<h1 style="color:red;">{subject}</h1>'
                    f'<pre style="background-color:red;">{e}</pre>'
                )
                mail_admins(subject, message, html_message=html_message)
                # LAB7 : ELOG
                logger.error(f"Eroare la salvarea mesajului in {filepath}: {e}", exc_info=True)
                messages.error(request, "A apărut o eroare la salvarea mesajului.")
                return redirect("contact")
            
            return redirect("mesaj_trimis")

    else:
        form = ContactForm()
    return render(request, 'moto_shop/contact.html', {'form': form,"ip": get_ip(request),**meniu_cat(),})

def produs_creare(request):
    inregistreaza_acces(request)

    if not request.user.is_authenticated or not request.user.has_perm("moto_shop.add_produs"):
        n_403 = request.session.get("n_403", 0) + 1
        request.session["n_403"] = n_403
        context = {
            "ip": get_ip(request),
            "titlu": "Eroare adaugare produse",
            "mesaj_personalizat": "Nu ai voie să adaugi produse moto.",
            "n_403": n_403,
            "N_MAX_403": settings.N_MAX_403,
            **meniu_cat(),
        }
        return render(request, "moto_shop/403.html", context, status=403)

    if request.method == "POST":
        form = ProdusForm(request.POST)
        if form.is_valid():
            produs = form.save(commit=False)
            pret_c = form.cleaned_data["pret_cumparare"]
            adaos = form.cleaned_data["adaos_proc"]
            produs.pret_baza = pret_c * (1 + adaos / 100)
            produs.activ = True
            produs.save()
            if "categorii" in form.cleaned_data:
                form.save_m2m()
            messages.success(request, "Produsul a fost creat cu succes.")
            return redirect("produse_list")
    else:
        form = ProdusForm()
    return render(
        request,
        "moto_shop/produs_form.html",
        {"ip": get_ip(request), "form": form, **meniu_cat()},
    )


def register_view(request):
    inregistreaza_acces(request)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # LAB7 : ILOG
            logger.info(f"User nou inregistrat: {user.username} ({user.email})")
            context = {
                "user": user,
                "domain": request.get_host(),
                "protocol": "https" if request.is_secure() else "http",
            }
            html_content = render_to_string("moto_shop/email_confirmare.html", context)
            email = EmailMessage(
                subject="Confirmare adresă e-mail",
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send()
            messages.success(request, "Cont creat cu succes. Verifică e-mailul pentru confirmare.")
            return redirect("login")
        else:
            print("ERORI REGISTER:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, "moto_shop/register.html", {"form": form, **meniu_cat()})




def login_view(request):
    inregistreaza_acces(request)
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # LAB7 : ILOG
            logger.info(f"User {user.username} s-a logat de la IP {get_ip(request)}")
            if form.cleaned_data.get("ramane_logat"):
                request.session.set_expiry(24 * 60 * 60)
            else:
                request.session.set_expiry(0)
            profil_data = {
                "username": user.username,
                "email": user.email,
                "nume": getattr(user, "nume", ""),
                "telefon": getattr(user, "telefon", ""),
                "tara": getattr(user, "tara", ""),
                "judet": getattr(user, "judet", ""),
                "localitate": getattr(user, "localitate", ""),
                "strada": getattr(user, "strada", ""),
                "nr_strada": getattr(user, "nr_strada", ""),
                "cod_postal": getattr(user, "cod_postal", ""),
                "data_nasterii": user.data_nasterii.isoformat() if getattr(user, "data_nasterii", None) else "",
            }
            request.session["profil"] = profil_data
            return redirect("profil")
    else:
        form = CustomAuthenticationForm(request)
    return render(request, "moto_shop/login.html", {"form": form, **meniu_cat()})


def logout_view(request):
    inregistreaza_acces(request)
    if request.user.is_authenticated:
        try:
            perm = Permission.objects.get(codename="vizualizeaza_oferta")
            request.user.user_permissions.remove(perm)
        except Permission.DoesNotExist:
            pass
    logout(request)
    return redirect("login")

@login_required
def profil_view(request):
    inregistreaza_acces(request)
    profil = request.session.get("profil")
    if profil is None:
        u = request.user
        profil = {
            "username": u.username,
            "email": u.email,
            "nume": getattr(u, "nume", ""),
            "telefon": getattr(u, "telefon", ""),
            "tara": getattr(u, "tara", ""),
            "judet": getattr(u, "judet", ""),
            "localitate": getattr(u, "localitate", ""),
            "strada": getattr(u, "strada", ""),
            "nr_strada": getattr(u, "nr_strada", ""),
            "cod_postal": getattr(u, "cod_postal", ""),
            "data_nasterii": getattr(u, "data_nasterii", None),
        }
        request.session["profil"] = profil
    return render(request, "moto_shop/profil.html", {"profil": profil, **meniu_cat()})

@login_required
def schimba_parola_view(request):
    inregistreaza_acces(request)
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parola a fost schimbată cu succes.")
            return redirect("profil")
        else:
            messages.error(request, "Există erori în formular.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "moto_shop/schimba_parola.html", {"form": form, **meniu_cat()})

# LAB7 : view confirmare mail
def confirma_mail(request, cod):
    try:
        user = CustomUser.objects.get(cod=cod)
    except CustomUser.DoesNotExist:
        # LAB7 : ELOG
        logger.error(f"Cod de confirmare invalid sau expirat: {cod}")
        context = {**meniu_cat()}
        return render(request, "moto_shop/confirmare_esec.html", context)
    user.email_confirmat = True
    user.cod = None
    user.save()
    context = {"user": user, **meniu_cat()}
    return render(request, "moto_shop/confirmare_succes.html", context)

# LAB7: trimite promotii
def trimite_promotie(promotie_id):
    promotie = Promotie.objects.get(pk=promotie_id)
    categorii = promotie.categorii.all()

    utilizatori = CustomUser.objects.filter(
        vizualizare__produs__categorii__in=categorii
    ).distinct()

    mesaje = []

    for user in utilizatori:
        categ = Categorie.objects.filter(
            produse__vizualizare__utilizator=user,
            produse__categorii__in=categorii
        ).distinct().first()

        if not categ:
            continue

        if categ.nume.lower().startswith("cască"):
            template = "moto_shop/email_promotii/promotie_categ1.txt"
        else:
            template = "moto_shop/email_promotii/promotie_categ2.txt"

        context = {
            "subiect": promotie.nume,
            "user": user,
            "categorie_nume": categ.nume,
            "procent": promotie.procent,
            "data_expirare": promotie.data_expirare,
            "descriere": promotie.descriere,
        }

        text_mesaj = render_to_string(template, context)

        mesaj = (
            promotie.nume,
            text_mesaj,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        mesaje.append(mesaj)

    if mesaje:
        send_mass_mail(mesaje, fail_silently=False)

def promotii_view(request):
    inregistreaza_acces(request)
    if request.method == "POST":
        form = PromotieForm(request.POST)
        if form.is_valid():
            promotie = form.save()
            subiect = form.cleaned_data["subiect"]
            mesaj_extra = form.cleaned_data["mesaj"]
            k = settings.PROMO_MIN_VIZUALIZARI
            categorii_selectate = form.cleaned_data["categorii"]

            template_map = {
                "SLUG1": "moto_shop/email_promotii/promotie_categ1.txt",
                "SLUG2": "moto_shop/email_promotii/promotie_categ2.txt",
            }

            mesaje = []

            for categorie in categorii_selectate:
                utilizatori = CustomUser.objects.filter(
                    vizualizare__produs__categorii=categorie
                ).annotate(
                    nr_viz=Count(
                        "vizualizare",
                        filter=Q(vizualizare__produs__categorii=categorie)
                    )
                ).filter(nr_viz__gte=k).distinct()

                tmpl_path = template_map.get(categorie.slug)
                if not tmpl_path:
                    continue

                for user in utilizatori:
                    context = {
                        "subiect": subiect,
                        "user": user,
                        "categorie_nume": categorie.nume,
                        "procent": promotie.procent,
                        "data_expirare": promotie.data_expirare,
                        "descriere": promotie.descriere,
                        "mesaj_extra": mesaj_extra,
                    }
                    text_mesaj = render_to_string(tmpl_path, context)
                    msg_tuple = (
                        subiect,
                        text_mesaj,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    mesaje.append(msg_tuple)

            if mesaje:
                send_mass_mail(mesaje, fail_silently=False)

            messages.success(request, "Promoția a fost creată și mailurile au fost trimise.")
            return redirect("promotii")
    else:
        form = PromotieForm()

    return render(
        request,
        "moto_shop/promotii.html",
        {"form": form, **meniu_cat()}
    )

# LAB8 : interzis
def interzis_view(request):
    inregistreaza_acces(request)
    n_403 = request.session.get("n_403", 0) + 1
    request.session["n_403"] = n_403
    context = {
        "ip": get_ip(request),
        "titlu": "",
        "mesaj_personalizat": "Nu aveți permisiunea de a accesa această resursă.",
        "n_403": n_403,
        "N_MAX_403": settings.N_MAX_403,
        **meniu_cat(),
    }
    return render(request, "moto_shop/403.html", context, status=403)
# LAB8 : oferta
def oferta_view(request):
    inregistreaza_acces(request)
    if not request.user.is_authenticated or not request.user.has_perm("moto_shop.vizualizeaza_oferta"):
        return pagina_403(
            request,
            "Eroare afisare oferta",
            "Nu ai voie să vizualizezi oferta."
        )
    context = {"ip": get_ip(request), **meniu_cat()}
    return render(request, "moto_shop/oferta.html", context)


def oferta_claim(request):
    inregistreaza_acces(request)
    if not request.user.is_authenticated:
        return redirect("login")
    perm = Permission.objects.get(codename="vizualizeaza_oferta")
    request.user.user_permissions.add(perm)
    return redirect("oferta")

