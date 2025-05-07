from django.db import models

class Concours(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    def __str__(self):
        return self.nom

class Candidat(models.Model):
    NIVEAU_CHOICES = [
        ('BAC', 'Baccalauréat'),
        ('BAC+1', 'Bac+1'),
        ('BAC+2', 'Bac+2'),
        ('BAC+3', 'Bac+3'),
        ('BAC+4', 'Bac+4'),
        ('BAC+5', 'Bac+5'),
    ]
    
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=200)
    date_naissance = models.DateField()
    niveau_etudes = models.CharField(max_length=5, choices=NIVEAU_CHOICES)
    etablissement_origine = models.CharField(max_length=200)
    concours = models.ForeignKey(Concours, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    # Documents
    extrait_naissance = models.FileField(upload_to='documents/extraits/')
    certificat = models.FileField(upload_to='documents/certificats/')
    diplome = models.FileField(upload_to='documents/diplomes/')
    lettre_motivation = models.FileField(upload_to='documents/lettres/')
    photo = models.ImageField(upload_to='documents/photos/')
    
    # Validation de l'inscription
    inscription_validee = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nom} {self.prenoms} - {self.concours}"
    
