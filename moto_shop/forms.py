# forms.py
from django import forms
from datetime import date
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

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


