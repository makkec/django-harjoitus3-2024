from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils import timezone

from .models import Kysymys, Vaihtoehto


class ListaNäkymä(generic.ListView):
    template_name = "kysely/indeksi.html"
    context_object_name = "kysymykset"

    def get_queryset(self):
        # Otetaan nykyinen ajanhetki muuttujaan "nyt"
        nyt = timezone.now()

        # Aloitetaan hakemalla kaikki kysymykset
        kaikki_kysymykset = Kysymys.objects.all()

        # Suodatetaan (filter) kaikista kysymyksistä ne, joiden
        # julkaisupvm on pienempi tai yhtäsuuri kuin tämänhetkinen aika
        # (muuttujassa "nyt")
        #
        # Huom. lte = Less Than or Equal = pienempi tai yhtäsuuri
        ei_tulevaisuudessa = kaikki_kysymykset.filter(julkaisupvm__lte=nyt)

        # Järjestetään kysymykset julkaisupvm:n mukaan
        #
        # Huom. "-"-merkki edessä kääntää järjestyksen niin, että suuret
        # arvot tulevat ennen pieniä, jolloin uusimmat kysymykset ovat
        # ensimmäisenä
        järjestetyt_kysymykset = ei_tulevaisuudessa.order_by("-julkaisupvm")

        # Palautetaan järjestettyjen kysymysten listan alusta 2 ensimmäistä
        return järjestetyt_kysymykset[:2]
        
class NäytäNäkymä(generic.DetailView):
    model = Kysymys
    template_name = "kysely/näytä.html"


class TuloksetNäkymä(generic.DetailView):
    model = Kysymys
    template_name = "kysely/tulokset.html"


def äänestä(request, kysymys_id):
    kysym = get_object_or_404(Kysymys, pk=kysymys_id)
    try:
        valittu = kysym.vaihtoehto_set.get(pk=request.POST["valittu"])
    except (KeyError, Vaihtoehto.DoesNotExist):
        # Näytä kysymyslomake uudelleen.
        return render(
            request,
            "kysely/näytä.html",
            {
                "kysymys": kysym,
                "virheviesti": "Et valinnut mitään vaihtoehtoa.",
            },
        )
    else:
        valittu.ääniä = valittu.ääniä + 1
        valittu.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        osoite = reverse("kysely:tulokset", args=(kysym.id,))
        return HttpResponseRedirect(osoite)
    