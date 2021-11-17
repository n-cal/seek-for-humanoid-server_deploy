from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .pagination import HumanoidsPaginator
from django.db.models import Q
from humanoids.models import Humanoid
from humanoids.serializers import HumanoidListSerializer, HumanoidDetailSerializer
from django.db.models import Value as V
from django.db.models.functions import Concat 

@api_view(['GET'])
@csrf_exempt
def all_humanoids(request):

    humanoids = Humanoid.objects.all()

    country = request.query_params.get('country', None)

    if country is not None:
        humanoids = humanoids.filter(country__iexact=country)

    search_words_list = request.query_params.get('search', '').lower().split()

    if len(search_words_list) > 100:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if len(search_words_list) > 0:
        humanoids = filter_matching_names(humanoids, search_words_list)


    paginator = HumanoidsPaginator()
    paginated_queryset = paginator.paginate_queryset(humanoids, request)
    serializer = HumanoidListSerializer(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def humanoid_detail(request, id):
    try:
        humanoid = Humanoid.objects.get(id=id)
        serializer = HumanoidDetailSerializer(humanoid, many=False)

        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def all_countries(request):
    countries = Humanoid.objects.distinct('country').values_list('country', flat=True)
    return Response(countries)


def filter_matching_names(humanoids, search_words_list):
    # if client input has only one word, search for humanoids that
    # contain that word in name or surname field
    if len(search_words_list) == 1:
        search_word = search_words_list[0]
        return humanoids.filter(Q(name__icontains=search_word) | Q(surname__icontains=search_word))

    # if client input has more than one word...
    else:
        # ...save the last word for later ...
        last_search_word = search_words_list.pop()

        # ...filter humanoids by exact match for previous words...
        for search_word in search_words_list:
            word_between = ' ' + search_word + ' '
            humanoids = humanoids.annotate(full_name=Concat(V(' '), 'name', V(' '), 'surname', V(' ')))\
                .filter(full_name__icontains=word_between)
        
        # ...then filter humanoids that match each word only one time 
        # (for example input ['Mario', 'Mar'] -> disacard 'Mario Rossi') ...
        res_humanoids = []
        for humanoid in humanoids:
            full_name_list = humanoid.full_name_list

            if len(search_words_list) + 1 > len(full_name_list):
                continue

            for search_word in search_words_list:
                if search_word in full_name_list:
                    full_name_list.remove(search_word)
            
            # ...and contain (not exact match) the last word saved earlier.
            for remain_word in full_name_list:
                if last_search_word in remain_word:
                    res_humanoids.append(humanoid)
                    break

        return res_humanoids