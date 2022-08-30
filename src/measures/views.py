from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from measures.models import CalculatedMeasure, SupportedMeasure
from measures.serializers import (
    CalculatedMeasureHistorySerializer,
    LatestMeasuresCalculationsRequestSerializer,
    MeasuresCalculationsRequestSerializer,
    SupportedMeasureSerializer,
)
from organizations.models import Repository
from utils.clients import CoreClient


class CalculateMeasuresViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Endpoint que ativa o mecanismo de cálculo das medidas
    """

    serializer_class = MeasuresCalculationsRequestSerializer
    queryset = CalculatedMeasure.objects.all()

    def get_repository(self):
        return get_object_or_404(
            Repository,
            id=self.kwargs['repository_pk'],
            product_id=self.kwargs['product_pk'],
            product__organization_id=self.kwargs['organization_pk'],
        )

    def create(self, request, *args, **kwargs):
        """
        Calculate measures.
        """
        # 1. Valida se os dados foram enviados corretamente
        serializer = MeasuresCalculationsRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 2. Obtenção das medidas suportadas pelo serviço
        measure_keys = [measure['key'] for measure in data['measures']]
        qs = SupportedMeasure.objects.filter(
            key__in=measure_keys
        ).prefetch_related(
            'metrics',
            'metrics__collected_metrics',
        )

        # 3. Criação do dicionário que será enviado para o serviço `core`
        core_params = {'measures': []}

        # 4. Obtenção das métricas necessárias para calcular as medidas
        measure: SupportedMeasure
        for measure in qs:
            metric_params = measure.get_latest_metric_params()

            core_params['measures'].append({
                'key': measure.key,
                'parameters': metric_params,
            })

        # 5. Solicitação do cáculo ao serviço core
        # TODO: Se alguma métrica ter sido recentemente
        # calculada não recalculá-la
        response = CoreClient.calculate_measure(core_params)

        if response.ok is False:
            return Response(response.text, status=response.status_code)

        data = response.json()

        calculated_values = {
            measure['key']: measure['value']
            for measure in data['measures']
        }

        # 6. Salvando no banco de dados as medidas calculadas

        calculated_measures = []

        repository = self.get_repository()

        measure: SupportedMeasure
        for measure in qs:
            value = calculated_values[measure.key]
            calculated_measures.append(
                CalculatedMeasure(
                    measure=measure,
                    value=value,
                    repository=repository,
                )
            )

        CalculatedMeasure.objects.bulk_create(calculated_measures)

        # 7. Retornando o resultado
        serializer = LatestMeasuresCalculationsRequestSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SupportedMeasureModelViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Viewset que retorna todas as medidas suportadas pelo sistema
    """
    queryset = SupportedMeasure.objects.all()
    serializer_class = SupportedMeasureSerializer


class RepositoryMeasuresMixin:
    def get_queryset(self):
        repository = get_object_or_404(
            Repository,
            id=self.kwargs['repository_pk'],
            product_id=self.kwargs['product_pk'],
            product__organization_id=self.kwargs['organization_pk'],
        )
        qs = repository.calculated_measures.all()
        qs = qs.values_list('measure', flat=True).distinct()
        return SupportedMeasure.objects.filter(id__in=qs)


class LatestCalculatedMeasureModelViewSet(
    RepositoryMeasuresMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet para cadastrar as medidas coletadas
    """
    queryset = SupportedMeasure.objects.prefetch_related(
        'calculated_measures',
    )
    serializer_class = LatestMeasuresCalculationsRequestSerializer


class CalculatedMeasureHistoryModelViewSet(
    RepositoryMeasuresMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet para ler o histórico de medidas coletadas
    TODO: Criar uma classe de paginação (
        https://www.django-rest-framework.org/api-guide/pagination/#modifying-the-pagination-style
    )
    """
    queryset = SupportedMeasure.objects.prefetch_related(
        'calculated_measures',
    )
    serializer_class = CalculatedMeasureHistorySerializer
