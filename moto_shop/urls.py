from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("info/", views.info, name="info"), 
    path("exemplu_simplu", views.afis_template2,name="exemplu2"),
    path("log", views.log, name="log"),
    path('despre/', views.despre, name='despre'),
    path('produse/', views.produse_list, name='produse_list'),
    path('cos_virtual/', views.cos_virtual, name='cos_virtual'),
    path("produse/<int:pk>/", views.produs_detail, name="produs_detail"),
    path("categorii/<slug:slug>/", views.categorie_detail, name="categorie_detail"),
    path("contact/", views.contact_view, name="contact"),
    path("produs_creare/", views.produs_creare, name="produs_creare"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.profil_view, name="profil"),
    path("schimba-parola/", views.schimba_parola_view, name="schimba_parola"),
]
