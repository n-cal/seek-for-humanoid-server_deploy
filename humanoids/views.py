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

    if len(search_words_list) > 10:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if len(search_words_list) > 0:

        if len(search_words_list) == 1:
            search_word = search_words_list[0]
            humanoids = humanoids.filter(Q(name__icontains=search_word) | Q(surname__icontains=search_word))
        else:
            last_search_word = search_words_list.pop()

            for search_word in search_words_list:
                word_between = ' ' + search_word + ' '
                humanoids = humanoids.annotate(full_name=Concat(V(' '), 'name', V(' '), 'surname', V(' ')))\
                    .filter(full_name__icontains=word_between)

            res_humanoids = []
            for humanoid in humanoids:
                full_name_list = humanoid.full_name_list

                if len(search_words_list) + 1 > len(full_name_list):
                    continue

                for search_word in search_words_list:
                    if search_word in full_name_list:
                        full_name_list.remove(search_word)
                
                for remain_word in full_name_list:
                    if last_search_word in remain_word:
                        res_humanoids.append(humanoid)
                        break

            humanoids = res_humanoids

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