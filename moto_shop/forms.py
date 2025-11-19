# forms.py
from django import forms
from datetime import date
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from .models import Produs, Brand, Categorie
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


ITEMS_PER_PAGE_CHOICES = [(5, '5'), (10, '10'), (25, '25'), (50, '50')]
class ProduseForm(forms.Form):
    nume_contine = forms.CharField(label="Nume conține", required=False, max_length=80)
    descriere_contine = forms.CharField(label="Descriere conține", required=False, max_length=120)

    pret_min = forms.DecimalField(label="Pret minim", required=False, min_value=0, decimal_places=2, max_digits=10)
    pret_max = forms.DecimalField(label="Pret maxim", required=False, min_value=0, decimal_places=2, max_digits=10)

    creat_de_la = forms.DateField(label="Creat de la", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    creat_pana  = forms.DateField(label="Creat până la", required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    gen = forms.ChoiceField(
        label="Gen",
        required=False,
        choices=[("", "(toate)")] + list(Produs.GenChoices.choices)
    )

    ACTIV_CHOICES = (("", "(toate)"), ("1", "Da"), ("0", "Nu"))
    activ = forms.ChoiceField(label="Activ", required=False, choices=ACTIV_CHOICES)


    brand = forms.ModelChoiceField(label="Brand", queryset=Brand.objects.all(), required=False, empty_label="(toate)")
    categorie = forms.ModelChoiceField(label="Categorie", queryset=Categorie.objects.all(), required=False, empty_label="(toate)")

    items_per_page = forms.ChoiceField(
        label="Produse pe pagină",
        choices=ITEMS_PER_PAGE_CHOICES,
        required=False,
        initial=10
    )

    def clean(self):
        cleaned = super().clean()
        pmin, pmax = cleaned.get('pret_min'), cleaned.get('pret_max')
        dfrom, dto = cleaned.get('creat_de_la'), cleaned.get('creat_pana')
        ipp = cleaned.get('items_per_page') or self.fields['items_per_page'].initial

        if pmin is not None and pmax is not None and pmin > pmax:
            self.add_error('pret_max', "Prețul maxim trebuie să fie ≥ prețul minim.")

        if dfrom and dto and dfrom > dto:
            self.add_error('creat_pana', "Data de sfârșit trebuie să fie după (sau egală cu) data de început.")

        try:
            ipp_int = int(ipp)
        except (TypeError, ValueError):
            self.add_error('items_per_page', "Valoare invalida pentru paginare.")
        else:
            if ipp_int not in {v for v, _ in ITEMS_PER_PAGE_CHOICES}:
                self.add_error('items_per_page', "Valoare de paginare neacceptata.")
            else:
                cleaned['items_per_page'] = ipp_int

        return cleaned

    def clean_activ(self):
        val = self.cleaned_data.get('activ')
        if val == "1": return True
        if val == "0": return False
        return None

    def lock_categorie(self, categorie_obj: Categorie):
        self.fields['categorie'].initial = categorie_obj.pk
        self.fields['categorie'].widget = forms.HiddenInput()


def validate_only_letters(value):
    if not value.isalpha():
        raise ValidationError("Acest câmp trebuie să conțină doar litere.")
def validate_varsta(value):
    if (date.today().year - value.year) < 18:
        raise ValidationError("Trebuie să aveți cel puțin 18 ani.")
    elif (date.today().month - value.month) < 0:
        raise ValidationError("Trebuie să aveți cel puțin 18 ani.")
    elif (date.today().month - value.month) == 0 and (date.today().day - value.day) < 0:
        raise ValidationError("Trebuie să aveți cel puțin 18 ani.")
def validate_numar_cuvinte(value):
    count = 0
    in_word = False

    for c in value:
        if c.isalnum():  
            if not in_word:
                count += 1
                in_word = True
        else:
            in_word = False

    if count < 5 or count > 100:
        raise ValidationError("Mesajul trebuie să conțină între 5 și 100 de cuvinte.")
def validate_len_cuvant(value):
    cuvinte = value.strip().split()
    for cuvant in cuvinte:
        if len(cuvant) > 15:
            raise ValidationError("Fiecare cuvânt din mesaj trebuie să aibă maximum 15 de caractere.")
def validate_linkuri(value):
    cuvinte = value.strip().split()
    for cuvant in cuvinte:
        if "http://" in cuvant or "https://" in cuvant:
            raise ValidationError("Mesajul nu trebuie să conțină linkuri.")
def validate_cnp(value):
    if len(value) != 13:
        raise ValidationError("CNP-ul trebuie să conțină exact 13 cifre.")
    if not value.isdigit() or len(value) != 13:
        raise ValidationError("CNP-ul trebuie să conțină exact 13 cifre.")
    if value[0] not in '12':
        raise ValidationError("CNP-ul trebuie să înceapă cu cifrele 1 sau 2.")
    data = value[1:7]
    an = int(data[0:2])
    luna = int(data[2:4])
    zi = int(data[4:6])
    if luna < 1 or luna > 12:
        raise ValidationError("Luna din CNP nu este validă.")
    if zi < 1 or zi > 31:
        raise ValidationError("Ziua din CNP nu este validă.")
    if an > 25:
        an += 1900
    else:
        an += 2000
    try:
        date(an, luna, zi)
    except ValueError:
        raise ValidationError("Data din CNP nu este valida.")
    
def validate_email_temp(value):
    domenii_interzise = ['guerillamail.com', 'yopmail.com']
    domeniu = value.split('@')[-1]
    if domeniu in domenii_interzise:
        raise ValidationError("Adresa de e-mail nu poate fi temporara.")
    
def validate_litere(value):
    if value[0].islower():
        raise ValidationError("Primul caracter trebuie sa fie litera mare.")
    for c in value:
        if not (c.isalpha() or c == '-' or c == ' '):
            raise ValidationError("Acest camp poate contine doar litere, spatii si cratime.")

def validate_litere_cratima(value):
    for i in range(len(value)):
        if value[i] == '-' or value[i] == ' ':
            if i + 1 < len(value):
                if value[i+1].islower():
                    raise ValidationError("Dupa cratima sau spatiu trebuie litera mare.")

TIP_MESAJ_CHOICES = [
    ('neselectat', 'Neselectat'),
    ('reclamatie', 'Reclamatie'),
    ('intrebare', 'Intrebare'),
    ('review', 'Review'),
    ('cerere', 'Cerere'),
    ('programare', 'Programare'),
]

class ContactForm(forms.Form):
    nume = forms.CharField(
        max_length=10,
        label='Nume',
        required=True,
        validators=[validate_litere, validate_litere_cratima]
    )

    prenume = forms.CharField(
        max_length=10,
        label='Prenume',
        required=False,
        validators=[validate_litere, validate_litere_cratima]
    )

    cnp = forms.CharField(
        label='CNP',
        required=False,
        max_length=13,                        
        validators=[validate_cnp]             
    )

    data_nasterii = forms.DateField(
        label='Data nașterii',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_varsta]          
    )

    email = forms.EmailField(
        label='E-mail',
        required=True,
        validators=[validate_email_temp]       
    )

    confirmare_email = forms.EmailField(
        label='Confirmare e-mail',
        required=True,
        validators=[validate_email_temp]       
    )

    tip_mesaj = forms.ChoiceField(
        choices=TIP_MESAJ_CHOICES,
        initial='neselectat',
        label='Tip mesaj',
        required=True,
    )

    subiect = forms.CharField(
        max_length=100,
        label='Subiect',
        required=True,
        validators=[                                   # fără linkuri + format nume propriu
            validate_linkuri,
            validate_litere,
            validate_litere_cratima
        ]
    )

    minim_zile_asteptare = forms.IntegerField(
        label=('Pentru review-uri/cereri minimul de zile de asteptare trebuie setat '
               'de la 4 incolo iar pentru cereri/intrebari de la 2 incolo. Maximul e 30.'),
        required=True,
        min_value=1,
        max_value=30
    )

    mesaj = forms.CharField(
        widget=forms.Textarea,
        label='Mesaj (includeți semnatura la final)',
        required=True,
        validators=[                                   # fără linkuri + 5–100 cuvinte + ≤ 15/car cuvânt
            validate_linkuri,
            validate_numar_cuvinte,
            validate_len_cuvant
        ]
    )

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        confirm = cleaned.get("confirmare_email")
        mesaj = cleaned.get("mesaj") or ""
        nume = cleaned.get("nume") or ""
        tip = cleaned.get("tip_mesaj")
        zile = cleaned.get("minim_zile_asteptare")
        cnp = cleaned.get("cnp") or ""
        data_n = cleaned.get("data_nasterii")

        if email and confirm and email != confirm:
            self.add_error('confirmare_email', "Adresele de e-mail nu corespund.")
        if mesaj.strip().lower().endswith(nume.strip().lower()) is False:
            self.add_error('mesaj', "Mesajul trebuie să se încheie cu semnatura.")
        minime = {"review": 4, "cerere": 4, "intrebare": 2, "programare": 2}
        if tip in minime and minime[tip]:
            if zile < minime[tip]:
                self.add_error('minim_zile_asteptare',
                               f"Pentru {tip} minimul de zile de așteptare este {minime[tip]}.")
        if cnp and data_n:
            an_cnp = int(cnp[1:3])
            luna_cnp = int(cnp[3:5])
            zi_cnp = int(cnp[5:7])
            if cnp[0] in '12':
                if an_cnp >= 0 and an_cnp <= 25:
                    an_cnp += 2000
                else:
                    an_cnp += 1900
            try:
                data_cnp = date(an_cnp, luna_cnp, zi_cnp)
                if data_cnp != data_n:
                    self.add_error('cnp', "Data nașterii nu corespunde cu cea din CNP.")
            except ValueError:
                self.add_error('cnp', "Data din CNP nu este validă.")
        return cleaned

def validate_first_capital(value):
    if not value:
        return
    if not value[0].isalpha() or not value[0].isupper():
        raise ValidationError("Primul caracter trebuie să fie o literă majusculă.")

def validate_no_forbidden_words(value):
    if not value:
        return
    cuvinte_interzise = ["interzis", "banat", "test"]
    text = value.lower()
    for cuv in cuvinte_interzise:
        if cuv in text:
            raise ValidationError("Textul conține cuvinte nepermise.")

def validate_percent(value):
    if value is None:
        return
    if value < 0 or value > 300:
        raise ValidationError("Procentajul trebuie să fie între 0 și 300.")

class ProdusForm(forms.ModelForm):
    pret_cumparare = forms.DecimalField(
        label="Preț de cumparare",
        min_value=0,
        decimal_places=2,
        max_digits=10,
        help_text="Prețul plătit furnizorului.",
        error_messages={
            "required": "Introdu prețul de cumparare.",
            "invalid": "Introduceți un număr valid pentru prețul de cumparare."
        }
    )

    adaos_proc = forms.DecimalField(
        label="Adaos procentual",
        min_value=0,
        decimal_places=2,
        max_digits=5,
        help_text="Procentul de adaos față de prețul de cumparare.",
        validators=[validate_percent],
        error_messages={
            "required": "Introdu procentul de adaos.",
            "invalid": "Introduceți un număr valid pentru procent."
        }
    )

    class Meta:
        model = Produs
        fields = ["nume", "descriere", "brand", "gen"]
        labels = {
            "nume": "Denumire produs",
            "descriere": "Descriere detaliata",
        }
        help_texts = {
            "nume": "Numele produsului, cu literă mare la început.",
        }
        error_messages = {
            "nume": {
                "required": "Numele produsului este obligatoriu.",
                "max_length": "Numele este prea lung."
            },
            "descriere": {
                "required": "Descrierea produsului este obligatorie."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nume"].validators.extend([validate_first_capital, validate_no_forbidden_words])
        self.fields["descriere"].validators.append(validate_no_forbidden_words)

    def clean_pret_cumparare(self):
        value = self.cleaned_data.get("pret_cumparare")
        if value is not None and value == 0:
            raise ValidationError("Pretul de cumpărare nu poate fi zero.")
        return value

    def clean(self):
        cleaned = super().clean()
        pret_c = cleaned.get("pret_cumparare")
        adaos = cleaned.get("adaos_proc")
        if pret_c is not None and adaos is not None:
            pret_final = pret_c * (1 + adaos / 100)
            if pret_final < 50:
                raise ValidationError("Pretul final rezultat trebuie să fie cel putin 50 RON.")
        return cleaned

 
class CustomAuthenticationForm(AuthenticationForm):
    ramane_logat = forms.BooleanField(
        required=False,
        initial=False,
        label='Ramaneti logat'
    )

    def clean(self):        
        cleaned_data = super().clean()
        ramane_logat = self.cleaned_data.get('ramane_logat')
        return cleaned_data
    
class CustomUserCreationForm(UserCreationForm):
    nume = forms.CharField(max_length=100, label="Nume complet")
    telefon = forms.CharField(max_length=20, label="Telefon", required=False)
    tara = forms.CharField(max_length=50, label="Țara", required=False)
    judet = forms.CharField(max_length=50, label="Județ", required=False)
    localitate = forms.CharField(max_length=80, label="Localitate", required=False)
    strada = forms.CharField(max_length=120, label="Stradă", required=False)
    nr_strada = forms.IntegerField(label="Număr", required=False)
    cod_postal = forms.IntegerField(label="Cod poștal", required=False)
    data_nasterii = forms.DateField(
        label="Data nașterii",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "nume",
            "telefon",
            "tara",
            "judet",
            "localitate",
            "strada",
            "nr_strada",
            "cod_postal",
            "data_nasterii",
            "password1",
            "password2",
        )

    def clean_nume(self):
        val = self.cleaned_data.get("nume", "")
        if any(ch.isdigit() for ch in val):
            raise ValidationError("Numele nu poate conține cifre.")
        return val

    def clean_telefon(self):
        val = self.cleaned_data.get("telefon", "")
        if val:
            if not val.isdigit():
                raise ValidationError("Telefonul trebuie să conțină doar cifre.")
            if len(val) < 10:
                raise ValidationError("Telefonul trebuie să aiba cel putin 10 cifre.")
        return val

    def clean_cod_postal(self):
        val = self.cleaned_data.get("cod_postal")
        if val is not None:
            if val < 100000 or val > 999999:
                raise ValidationError("Codul poștal trebuie sa aiba 6 cifre.")
        return val

    def clean_data_nasterii(self):
        val = self.cleaned_data.get("data_nasterii")
        if val and val >= date.today():
            raise ValidationError("Data nașterii trebuie să fie în trecut.")
        return val
