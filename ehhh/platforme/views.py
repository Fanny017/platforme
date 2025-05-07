from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Concours, Candidat
from .forms import CandidatForm
from .models import Concours
from django.views.decorators.http import require_GET

@require_GET
def concours_detail_api(request, pk):
    try:
        concours = Concours.objects.get(pk=pk)
        data = {
            'nom': concours.nom,
            'categorie': concours.get_categorie_display(),
            'date_debut': concours.date_debut.isoformat(),
            'date_fin': concours.date_fin.isoformat(),
            'description': concours.description
        }
        return JsonResponse(data)
    except Concours.DoesNotExist:
        return JsonResponse({'error': 'Concours non trouvé'}, status=404)

# Page d'accueil
def home(request):
    # Récupération des concours actifs (dont la date de fin est postérieure à aujourd'hui)
    concours_actifs = Concours.objects.filter(date_fin__gte=timezone.now().date()).order_by('date_debut')
    # Récupération des concours populaires (avec le plus d'inscrits)
    concours_populaires = Concours.objects.annotate(num_candidats=Count('candidat')).order_by('-num_candidats')[:3]
    
    context = {
        'concours': concours_actifs,
        'concours_populaires': concours_populaires,
        'total_candidats': Candidat.objects.count(),  # Statistique sur le nombre total de candidats
    }
    return render(request, 'platforme/home.html', context)

# Formulaire d'inscription
def registration_form(request):
    # Vérification si un concours est spécifié dans l'URL
    concours_id = request.GET.get('concours_id')
    initial_data = {}
    
    if concours_id:
        try:
            concours = Concours.objects.get(id=concours_id)
            initial_data = {'concours': concours}
        except Concours.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save(commit=False)
            
            # Vérification que le concours est toujours ouvert
            if candidat.concours.date_fin < timezone.now().date():
                messages.error(request, f"Les inscriptions pour le concours {candidat.concours.nom} sont terminées.")
                return render(request, 'platforme/registration_form.html', {'form': form})
                
            candidat.save()
            
            # Ajout d'un message de succès avec style féminin
            messages.success(request, "Félicitations! Votre inscription a été enregistrée avec succès! ✨")
            return redirect('confirmation', candidat_id=candidat.id)
        else:
            # Message d'erreur si le formulaire n'est pas valide
            messages.error(request, "Des erreurs ont été trouvées dans votre formulaire. Veuillez les corriger.")
    else:
        form = CandidatForm(initial=initial_data)
    
    context = {
        'form': form,
        'concours_list': Concours.objects.filter(date_fin__gte=timezone.now().date()),
    }
    return render(request, 'platforme/registration_form.html', context)

# Page de confirmation
def confirmation(request, candidat_id):
    # Utilisation de get_object_or_404 pour gérer le cas où le candidat n'existe pas
    candidat = get_object_or_404(Candidat, id=candidat_id)
    
    context = {
        'candidat': candidat,
        'date_inscription': candidat.date_inscription.strftime('%d/%m/%Y à %H:%M'),
    }
    return render(request, 'platforme/confirmation.html', context)

# Recherche de candidature existante
def recherche_candidature(request):
    query = request.GET.get('query', '')
    results = []
    
    if query:
        # Recherche parmi les candidats
        results = Candidat.objects.filter(
            nom__icontains=query
        ) | Candidat.objects.filter(
            prenoms__icontains=query
        ) | Candidat.objects.filter(
            email__icontains=query
        )
        
    # Pagination des résultats
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'platforme/recherche.html', context)

# Liste des concours disponibles
def liste_concours(request):
    concours_list = Concours.objects.all().order_by('date_debut')
    
    # Pagination des résultats
    paginator = Paginator(concours_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'platforme/liste_concours.html', context)

# Détails d'un concours
def detail_concours(request, concours_id):
    concours = get_object_or_404(Concours, id=concours_id)
    nb_inscrits = Candidat.objects.filter(concours=concours).count()
    
    context = {
        'concours': concours,
        'nb_inscrits': nb_inscrits,
        'est_ouvert': concours.date_fin >= timezone.now().date(),
    }
    return render(request, 'platforme/detail_concours.html', context)

# Génération du PDF de confirmation (vous aurez besoin d'installer xhtml2pdf)
def telecharger_confirmation(request, candidat_id):
    try:
        from xhtml2pdf import pisa
        import io
        
        candidat = get_object_or_404(Candidat, id=candidat_id)
        
        # Génération du contenu HTML
        template = get_template('platforme/pdf_confirmation.html')
        html = template.render({'candidat': candidat})
        
        # Création du PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"confirmation_inscription_{candidat.nom}_{candidat.prenoms}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        return HttpResponse("Erreur lors de la génération du PDF", status=500)
    except Exception as e:
        return HttpResponse(f"Une erreur est survenue: {str(e)}", status=500)