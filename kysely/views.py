from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Kysymys, Vaihtoehto


class ListaNäkymä(generic.ListView):
    template_name = "kysely/indeksi.html"
    context_object_name = "kysymykset"

    def get_queryset(self):
        """Return the last five published questions."""
        return Kysymys.objects.order_by("-julkaisupvm")[:2]

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
    